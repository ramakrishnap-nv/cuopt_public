#!/bin/bash

# SPDX-FileCopyrightText: Copyright (c) 2025-2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

# Add cuopt_cli path to PATH variable
if command -v pyenv &> /dev/null; then
    PATH="$(pyenv root)/versions/$(pyenv version-name)/bin:$PATH"
    export PATH
fi

# Test the CLI

# Add a test for the help command
cuopt_cli --help | grep "Usage: cuopt_cli" > /dev/null || (echo "Expected usage information not found" && exit 1)

# Add a test with a simple linear programming problem

# Run solver and check for optimal status - fail if not found

cuopt_cli "${RAPIDS_DATASET_ROOT_DIR}"/linear_programming/good-mps-1.mps | grep -q "Status: " || (echo "Expected solution not found" && exit 1)

cuopt_cli "${RAPIDS_DATASET_ROOT_DIR}"/linear_programming/good-mps-1.lp | grep -q "Status: " || (echo "Expected solution not found for .lp" && exit 1)

cuopt_cli "${RAPIDS_DATASET_ROOT_DIR}"/linear_programming/good-mps-1.lp.gz | grep -q "Status: " || (echo "Expected solution not found for .lp.gz" && exit 1)

cuopt_cli "${RAPIDS_DATASET_ROOT_DIR}"/linear_programming/good-mps-1.lp.bz2 | grep -q "Status: " || (echo "Expected solution not found for .lp.bz2" && exit 1)

# Add a for mixed integer programming test with options

cuopt_cli "${RAPIDS_DATASET_ROOT_DIR}"/mip/sample.mps --mip-absolute-gap 0.01 --time-limit 10 | grep -q "Best objective" || (echo "Expected solution objective not found" && exit 1)

# The console-script wrappers must exec the binary, not spawn it. A spawning
# wrapper leaves a Python parent that waits on the solver but forwards no
# signals, so terminating the console script's pid kills only the wrapper and
# leaves the binary running -- for cuopt_grpc_server that means orphaned GPU
# workers still holding the listen port, with none of the shutdown path run.
# execv is stubbed here so the check costs no GPU and starts no process.

python - <<'PY' || (echo "Wrapper exec check failed" && exit 1)
import os
import sys

from libcuopt import _cli_wrapper, _grpc_server_wrapper

for module, binary in (
    (_cli_wrapper, "cuopt_cli"),
    (_grpc_server_wrapper, "cuopt_grpc_server"),
):
    calls = []
    real_execv, real_argv = os.execv, sys.argv
    os.execv = lambda path, args: calls.append((path, args))
    sys.argv = [binary, "--help"]
    try:
        module.main()
    except SystemExit as exc:
        # A spawning wrapper ends in sys.exit(returncode) once the child is
        # done. Left uncaught that would end this check with the child's own
        # status and read as a pass, so it is the failure being tested for.
        raise AssertionError(
            f"{binary} wrapper returned (SystemExit {exc.code}) instead of "
            "exec'ing the binary"
        ) from None
    finally:
        os.execv, sys.argv = real_execv, real_argv

    assert calls, f"{binary} wrapper did not execv the binary"
    path, args = calls[0]
    assert path.endswith(os.path.join("bin", binary)), path
    assert args[0] == path, args
    assert args[1:] == ["--help"], args

print("Wrapper exec check passed")
PY
