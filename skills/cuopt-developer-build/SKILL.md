---
name: cuopt-developer-build
version: "26.04.00"
description: Build, test, and submit cuOpt changes. Use when building from source, running tests, checking style, or preparing a PR.
---

# cuOpt Developer — Build & Test

Build the project, run tests, check style, and prepare commits.

---

## Project Architecture

```
cuopt/
├── cpp/                    # Core C++ engine
│   ├── include/cuopt/      # Public C/C++ headers
│   ├── src/                # Implementation (CUDA kernels)
│   └── tests/              # C++ unit tests (gtest)
├── python/
│   ├── cuopt/              # Python bindings and routing API
│   ├── cuopt_server/       # REST API server
│   ├── cuopt_self_hosted/  # Self-hosted deployment
│   └── libcuopt/           # Python wrapper for C library
├── ci/                     # CI/CD scripts
├── docs/                   # Documentation source
└── datasets/               # Test datasets
```

## Supported APIs

| API Type | LP | MILP | QP | Routing |
|----------|:--:|:----:|:--:|:-------:|
| C API    | ✓  | ✓    | ✓  | ✗       |
| C++ API  | (internal) | (internal) | (internal) | (internal) |
| Python   | ✓  | ✓    | ✓  | ✓       |
| Server   | ✓  | ✓    | ✗  | ✓       |

---

## Build

### Build Everything

```bash
./build.sh
```

### Build Specific Components

```bash
./build.sh libcuopt    # C++ library
./build.sh cuopt       # Python package
./build.sh cuopt_server # Server
./build.sh docs        # Documentation
```

---

## Run Tests

```bash
# C++ tests
ctest --test-dir cpp/build

# Python tests
pytest -v python/cuopt/cuopt/tests

# Server tests
pytest -v python/cuopt_server/tests
```

---

## Before You Commit

### Run Style Checks

```bash
./ci/check_style.sh
# or
pre-commit run --all-files --show-diff-on-failure
```

### Sign Your Commits (DCO Required)

```bash
git commit -s -m "Your message"
```

---

## Key Files Reference

| Purpose | Location |
|---------|----------|
| Main build script | `build.sh` |
| Dependencies | `dependencies.yaml` |
| C++ formatting | `.clang-format` |
| Conda environments | `conda/environments/` |
| Test data | `datasets/` |
| CI scripts | `ci/` |

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Cython changes not reflected | Rerun: `./build.sh cuopt` |
| Missing `nvcc` | Set `$CUDACXX` or add CUDA to `$PATH` |
| CUDA out of memory | Reduce problem size |
| Slow debug library loading | Device symbols cause delay |

## Canonical Documentation

- **Contributing/build/test**: `CONTRIBUTING.md`
- **CI scripts**: `ci/README.md`
- **Release scripts**: `ci/release/README.md`
- **Docs build**: `docs/cuopt/README.md`
