# CI scripts

This directory contains the scripts for the CI pipeline.

CI builds are triggered by `pr.yaml`, `build.yaml` and `test.yaml` files in the `.github/workflows` directory. And these scripts are used from those workflows to build and test the code.

cuOpt is packaged in following ways:

## PIP package

### Build

The scripts for building the PIP packages are named as `build_wheel_<package_name>.sh`. For example, `build_wheel_cuopt.sh` is used to build the PIP package for cuOpt.

Please refer to existing scripts for more details and how you can add a new script for a new package.

### Test

The scripts for testing the PIP packages are named as `test_wheel_<package_name>.sh`. For example, `test_wheel_cuopt.sh` is used to test the PIP package for cuOpt.

Please refer to existing scripts for more details and how you can add a new script for a new package.

## Conda Package

### Build

For Conda package,

- all cpp libraries are built under one script called `build_cpp.sh`.
- all python bindings are built under one script called `build_python.sh`.

So if there are new cpp libraries or python bindings, you need to add them to the respective scripts.


### Test

Similarly, for Conda package,

- all cpp libraries are tested under one script called `test_cpp.sh`.
- all python bindings are tested under one script called `test_python.sh`.


## Wheel Validation

The `validate_wheel.sh` script is used to validate built wheel packages before publishing. It performs two checks:

1. **pydistcheck**: Validates the wheel package structure and enforces size limits (PyPI has a 1GiB hard limit, but we aim to keep packages smaller).
2. **twine check**: Ensures the wheel passes PyPI's upload validation requirements.

## Docker

The `docker/` folder contains everything needed to build and test the cuOpt container image:

- `Dockerfile`: The main Dockerfile for building the cuOpt container image.
- `context/`: Contains files and data for the buildx context (e.g., entrypoint scripts).
- `test_image.sh`: Script to test the built container image.
- `create_multiarch_manifest.sh`: Script for creating multi-architecture manifests.

Refer to `docker/README.md` for instructions on testing container images.

## Other Scripts

There are other scripts in this directory which are used to build and test the code and are also used in the workflows as utilities.
