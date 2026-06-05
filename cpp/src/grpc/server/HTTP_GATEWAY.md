# HTTP/OpenAPI 3.0 Gateway for the cuOpt gRPC Server

Work-in-progress. This document captures the full design so the implementation
can be resumed from any point.

---

## Goal

Add an HTTP/REST listener to `cuopt_grpc_server` that exposes the same
LP/MIP solve workflow as the gRPC interface. Both listeners share the
existing job queue and worker infrastructure — no solver code changes.

```
Client (gRPC)  ──►  port 50051  ──►  grpc::Service  (existing)
Client (HTTP)  ──►  port 8000   ──►  httplib thread  (new)
                                          │
                              submit_job_async() / check_job_status()
                              cancel_job() / job_tracker
                                   (shared, existing)
```

---

## Design Decisions (already settled)

| Concern | Decision | Rationale |
|---------|----------|-----------|
| HTTP library | `cpp-httplib` (header-only) | Integrates with existing OpenSSL dep; no new CMake targets |
| Serialization | Protobuf JSON (`MessageToJsonString` / `JsonStringToMessage`) | `json_util.h` already in libprotobuf; mirrors proto schema; human-readable |
| Large array compression | `Content-Encoding: gzip` on result endpoint | httplib built-in; transparent to all HTTP clients |
| TLS | `httplib::SSLServer` reusing `ServerConfig.tls_cert_path/key` | No new CLI surface |
| Default port | 8000; `--http-port 0` disables | Doesn't conflict with gRPC default (50051) |
| OpenAPI spec | Auto-generated from `field_registry.yaml` by `generate_conversions.py` | Single source of truth; zero drift |

---

## Endpoints

| Method | Path | Status |
|--------|------|--------|
| `POST` | `/jobs` | Not implemented |
| `GET` | `/jobs/{id}/status` | Not implemented |
| `GET` | `/jobs/{id}/result` | Not implemented |
| `DELETE` | `/jobs/{id}` | Not implemented |
| `GET` | `/health` | Not implemented |
| `GET` | `/openapi.yaml` | Not implemented |

---

## Files to Create / Modify

### New files
- `cpp/src/grpc/server/grpc_http_server.hpp` — HTTP thread + all route handlers
- `cpp/src/grpc/codegen/generated/openapi.yaml` — auto-generated (do not edit by hand)

### Modified files

#### `cpp/src/grpc/server/grpc_server_types.hpp`
Add `http_port` to `ServerConfig`:
```cpp
int http_port = 8000;   // 0 = disabled
```

#### `cpp/src/grpc/server/grpc_server_main.cpp`
1. New CLI argument:
```cpp
program.add_argument("--http-port")
  .help("HTTP/REST port (0 = disabled, default 8000)")
  .default_value(8000)
  .scan<'i', int>();
```

2. Read it:
```cpp
config.http_port = program.get<int>("--http-port");
```

3. Launch thread before `server->Wait()`:
```cpp
#include "grpc_http_server.hpp"

std::thread http_thread;
if (config.http_port > 0) {
  http_thread = std::thread(run_http_server, config.http_port);
  SERVER_LOG_INFO("[HTTP] REST gateway on port %d", config.http_port);
}

server->Wait();  // existing

if (http_thread.joinable()) http_thread.join();
```

#### `cpp/src/grpc/codegen/generate_conversions.py`
Add `generate_openapi_spec(registry)` function and one `write_file()` call at
the end of `main()`. See the **OpenAPI codegen** section below.

#### `dependencies.yaml`
```yaml
- cpp-httplib>=0.14   # header-only HTTP/HTTPS server (gRPC HTTP gateway)
```

---

## grpc_http_server.hpp — skeleton

```cpp
#pragma once
#ifdef CUOPT_ENABLE_GRPC

#include "grpc_server_types.hpp"
#include <httplib.h>
#include <google/protobuf/util/json_util.h>
#include "cuopt_remote_service.grpc.pb.h"

inline void add_cors_headers(httplib::Response& res)
{
  res.set_header("Access-Control-Allow-Origin",  "*");
  res.set_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
  res.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization");
}

inline void json_error(httplib::Response& res, int status, const std::string& msg)
{
  res.status = status;
  res.set_content("{\"error\":\"" + msg + "\"}", "application/json");
}

inline void run_http_server(int port)
{
  using namespace google::protobuf::util;

  // TLS vs plain
  std::unique_ptr<httplib::Server>    plain_svr;
  std::unique_ptr<httplib::SSLServer> ssl_svr;
  httplib::Server* svr = nullptr;

  if (config.enable_tls && !config.tls_cert_path.empty()) {
    ssl_svr = std::make_unique<httplib::SSLServer>(
      config.tls_cert_path.c_str(), config.tls_key_path.c_str());
    svr = ssl_svr.get();
  } else {
    plain_svr = std::make_unique<httplib::Server>();
    svr = plain_svr.get();
  }

  // Serve generated OpenAPI spec
  const std::string openapi_spec = read_file_to_string(
    std::string(CUOPT_INSTALL_PREFIX) + "/share/cuopt/openapi.yaml");

  // GET /openapi.yaml
  svr->Get("/openapi.yaml", [&openapi_spec](const httplib::Request&, httplib::Response& res) {
    add_cors_headers(res);
    res.set_content(openapi_spec, "application/yaml");
  });

  // GET /health
  svr->Get("/health", [](const httplib::Request&, httplib::Response& res) {
    add_cors_headers(res);
    res.set_content("{\"status\":\"ok\"}", "application/json");
  });

  // POST /jobs
  svr->Post("/jobs", [](const httplib::Request& req, httplib::Response& res) {
    add_cors_headers(res);
    cuopt::remote::SubmitJobRequest proto_req;
    JsonParseOptions parse_opts;
    parse_opts.ignore_unknown_fields = true;
    auto st = JsonStringToMessage(req.body, &proto_req, parse_opts);
    if (!st.ok())
      return json_error(res, 400, "Invalid JSON: " + std::string(st.message()));

    uint32_t category = proto_req.has_mip_request()
                        ? cuopt::remote::MIP : cuopt::remote::LP;
    std::string bin;
    proto_req.SerializeToString(&bin);
    std::vector<uint8_t> data(bin.begin(), bin.end());

    auto [ok, job_id] = submit_job_async(std::move(data), category);
    if (!ok) return json_error(res, 503, job_id);

    res.status = 202;
    res.set_content("{\"job_id\":\"" + job_id + "\"}", "application/json");
  });

  // GET /jobs/:id/status
  svr->Get(R"(/jobs/([^/]+)/status)",
    [](const httplib::Request& req, httplib::Response& res) {
      add_cors_headers(res);
      std::string job_id = req.matches[1];
      std::string msg;
      auto st = check_job_status(job_id, msg);
      static const char* names[] = {
        "QUEUED","PROCESSING","COMPLETED","FAILED","NOT_FOUND","CANCELLED"};
      res.set_content(
        "{\"status\":\"" + std::string(names[static_cast<int>(st)]) +
        "\",\"message\":\"" + msg + "\"}",
        "application/json");
  });

  // GET /jobs/:id/result  — TODO: wire up result assembly (see note below)
  svr->Get(R"(/jobs/([^/]+)/result)",
    [](const httplib::Request& req, httplib::Response& res) {
      add_cors_headers(res);
      // TODO: extract result assembly from grpc_service_impl.cpp GetResult handler
      // into a shared helper, then call it here and serialize with MessageToJsonString.
      json_error(res, 501, "not implemented");
  });

  // DELETE /jobs/:id
  svr->Delete(R"(/jobs/([^/]+))",
    [](const httplib::Request& req, httplib::Response& res) {
      add_cors_headers(res);
      JobStatus st_out;
      std::string msg;
      cancel_job(req.matches[1], st_out, msg);
      res.set_content("{\"cancelled\":true}", "application/json");
  });

  SERVER_LOG_INFO("[HTTP] Listening on port %d", port);
  svr->listen("0.0.0.0", port);
}

#endif  // CUOPT_ENABLE_GRPC
```

---

## The One Hard Piece: Result Retrieval

`GET /jobs/{id}/result` needs the assembled result proto bytes from
`job_tracker`. Today that logic lives inside `GetResult` in
`grpc_service_impl.cpp` and is not factored out.

**Required refactor before implementing the result endpoint:**

1. Open `cpp/src/grpc/server/grpc_service_impl.cpp`
2. Find the `GetResult` RPC handler
3. Extract the result-assembly logic (job_tracker lookup → raw bytes → proto
   parse → serialize) into a free function, e.g.:
   ```cpp
   // grpc_server_types.hpp or a new grpc_result_helper.hpp
   bool get_result_bytes(const std::string& job_id,
                         std::vector<uint8_t>& out_bytes,
                         std::string& error_msg);
   ```
4. Call it from both the gRPC handler and the HTTP handler

This is the only piece that touches existing solver code.

---

## OpenAPI Codegen Addition

Add to `cpp/src/grpc/codegen/generate_conversions.py`, before `if __name__`:

```python
def _field_to_openapi_type(ftype):
    mapping = {
        "double":  {"type": "number",  "format": "double"},
        "float":   {"type": "number",  "format": "float"},
        "int32":   {"type": "integer", "format": "int32"},
        "int64":   {"type": "integer", "format": "int64"},
        "uint32":  {"type": "integer", "format": "int64"},
        "uint64":  {"type": "integer", "format": "int64"},
        "bool":    {"type": "boolean"},
        "string":  {"type": "string"},
        "bytes":   {"type": "string",  "format": "byte"},
    }
    return mapping.get(ftype, {"type": "string"})


def generate_openapi_spec(registry):
    import yaml as _yaml

    def _props_from_section(section_key):
        props = {}
        obj = registry.get(section_key, {})
        for f in obj.get("scalars", []):
            field = parse_field(f)
            props[field["name"]] = _field_to_openapi_type(field["type"])
        for f in obj.get("arrays", []):
            field = parse_field(f)
            props[field["name"]] = {
                "type": "array",
                "items": _field_to_openapi_type(
                    field["type"].replace("repeated ", "")
                ),
            }
        return props

    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "cuOpt Remote Solve REST API",
            "version": "26.08",
            "description": (
                "HTTP/JSON gateway to the cuOpt gRPC solver. "
                "All bodies use protobuf JSON mapping "
                "(google::protobuf::util::JsonPrintOptions, snake_case). "
                "Byte array fields are base64-encoded."
            ),
        },
        "paths": {
            "/jobs": {"post": {
                "summary": "Submit an LP or MIP solve job",
                "operationId": "submitJob",
                "requestBody": {"required": True, "content": {"application/json": {
                    "schema": {"$ref": "#/components/schemas/SubmitJobRequest"}}}},
                "responses": {
                    "202": {"description": "Accepted",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/SubmitJobResponse"}}}},
                    "400": {"description": "Bad request / invalid JSON"},
                    "503": {"description": "Queue full"},
                },
            }},
            "/jobs/{job_id}/status": {"get": {
                "summary": "Poll job status",
                "operationId": "checkStatus",
                "parameters": [{"in": "path", "name": "job_id",
                                "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"content": {"application/json": {"schema": {
                    "$ref": "#/components/schemas/StatusResponse"}}}}},
            }},
            "/jobs/{job_id}/result": {"get": {
                "summary": "Retrieve completed job result",
                "operationId": "getResult",
                "parameters": [{"in": "path", "name": "job_id",
                                "required": True, "schema": {"type": "string"}}],
                "responses": {
                    "200": {"description": "Solution",
                            "content": {"application/json": {"schema": {
                                "$ref": "#/components/schemas/ResultResponse"}}}},
                    "404": {"description": "Job not found"},
                    "425": {"description": "Result not yet ready"},
                },
            }},
            "/jobs/{job_id}": {"delete": {
                "summary": "Cancel a job",
                "operationId": "cancelJob",
                "parameters": [{"in": "path", "name": "job_id",
                                "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"description": "Cancelled"}},
            }},
            "/health": {"get": {
                "summary": "Liveness probe",
                "operationId": "health",
                "responses": {"200": {"description": "OK"}},
            }},
            "/openapi.yaml": {"get": {
                "summary": "This OpenAPI spec",
                "operationId": "getSpec",
                "responses": {"200": {"description": "OpenAPI 3.0 YAML"}},
            }},
        },
        "components": {"schemas": {
            "OptimizationProblem": {
                "type": "object",
                "properties": _props_from_section("optimization_problem"),
            },
            "SubmitJobRequest": {
                "type": "object",
                "properties": {
                    "lp_request":  {"$ref": "#/components/schemas/SolveLPRequest"},
                    "mip_request": {"$ref": "#/components/schemas/SolveMIPRequest"},
                },
            },
            "SolveLPRequest": {
                "type": "object",
                "properties": {
                    "problem":  {"$ref": "#/components/schemas/OptimizationProblem"},
                    "settings": {"type": "object",
                                 "description": "PDLPSolverSettings (protobuf JSON)"},
                },
            },
            "SolveMIPRequest": {
                "type": "object",
                "properties": {
                    "problem":  {"$ref": "#/components/schemas/OptimizationProblem"},
                    "settings": {"type": "object",
                                 "description": "MIPSolverSettings (protobuf JSON)"},
                },
            },
            "SubmitJobResponse": {
                "type": "object",
                "properties": {
                    "job_id":  {"type": "string"},
                    "message": {"type": "string"},
                },
            },
            "StatusResponse": {
                "type": "object",
                "properties": {
                    "status":  {"type": "string",
                                "enum": ["QUEUED", "PROCESSING", "COMPLETED",
                                         "FAILED", "NOT_FOUND", "CANCELLED"]},
                    "message": {"type": "string"},
                },
            },
            "ResultResponse": {
                "type": "object",
                "description": "LP or MIP solution in protobuf JSON format",
                "properties": {
                    **_props_from_section("lp_solution"),
                    **_props_from_section("mip_solution"),
                },
            },
        }},
    }
    return _yaml.dump(spec, sort_keys=False, allow_unicode=True)
```

Add inside `main()`, after the last existing `write_file()` call:
```python
write_file(
    os.path.join(outdir, "openapi.yaml"),
    generate_openapi_spec(registry),
)
```

---

## Known Gaps / Maintenance Notes

1. **Chunked upload has no HTTP equivalent** — `POST /jobs` only handles
   problems that fit in a single message. Return HTTP 413 with a clear message
   for problems that exceed `config.max_message_bytes`. Large problems must
   use the gRPC chunked path directly.

2. **Result path is a stub** — `GET /jobs/{id}/result` returns 501 until the
   result-assembly helper is extracted from `grpc_service_impl.cpp`.

3. **Proto JSON field names** — set `preserve_proto_field_names = true` in
   `JsonPrintOptions` so output uses `snake_case` matching the proto definition,
   not camelCase.

4. **Cert hot-reload** — `httplib::SSLServer` reads certs once at startup,
   same as gRPC. Both listeners require a server restart on cert rotation.

---

## Next Steps (in order)

- [ ] Add `cpp-httplib` to `dependencies.yaml` and run `pre-commit run --all-files`
- [ ] Add `_field_to_openapi_type` + `generate_openapi_spec` to `generate_conversions.py`
- [ ] Run codegen, verify `generated/openapi.yaml` looks correct
- [ ] Add `int http_port` to `ServerConfig` in `grpc_server_types.hpp`
- [ ] Add `--http-port` arg + thread launch to `grpc_server_main.cpp`
- [ ] Create `grpc_http_server.hpp` with all routes except result
- [ ] Extract result assembly from `GetResult` in `grpc_service_impl.cpp` into shared helper
- [ ] Wire result helper into `GET /jobs/{id}/result`
- [ ] Add CMake: link `protobuf::libprotobuf-util`, install `openapi.yaml` to `share/cuopt/`
- [ ] Add server tests in `python/cuopt_server/tests/` or `cpp/tests/`
