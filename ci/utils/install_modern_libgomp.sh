#!/bin/bash
# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# Fetch a modern GNU libgomp from conda-forge and leave it, verified, at
# <dest_dir>/libgomp.so.1.0.0 (with a libgomp.so.1 symlink alongside it).
#
# The Rocky Linux 8 wheel build image's own libgomp (and the SCL gcc-toolset compiler's, which
# doesn't ship a private copy at all) predates the OpenMP 5.0 detached-task runtime
# (omp_fulfill_event) the fast MPS parser needs, with no newer one available from the image's
# configured repos. conda-forge's build is confirmed to have it -- fetched directly over HTTPS
# (a .conda file is just a zip archive; no conda/mamba CLI needed) rather than pulled in via a
# package manager, since neither is installed on this image.
#
# See https://github.com/NVIDIA/cuopt/issues/1219

set -euo pipefail

dest_dir="${1:?Usage: install_modern_libgomp.sh <dest_dir>}"
mkdir -p "${dest_dir}"

case "$(arch)" in
    x86_64)
        subdir="linux-64"
        build="he0feb66_4"
        ;;
    aarch64)
        subdir="linux-aarch64"
        build="h8acb6b2_4"
        ;;
    *)
        echo "Unsupported architecture for modern libgomp fetch: $(arch)" >&2
        exit 1
        ;;
esac

# Pinned for build reproducibility -- bump deliberately, not by tracking "latest".
version="16.2.0"
pkg="libgomp-${version}-${build}.conda"
url="https://conda.anaconda.org/conda-forge/${subdir}/${pkg}"

workdir="$(mktemp -d)"
trap 'rm -rf "${workdir}"' EXIT

echo "Fetching ${url}"
curl -fsSL -o "${workdir}/${pkg}" "${url}"

python3 -m pip install --quiet zstandard

python3 - "${workdir}/${pkg}" "${workdir}/extracted" <<'PYEOF'
import io
import sys
import tarfile
import zipfile

import zstandard

pkg_path, out_dir = sys.argv[1], sys.argv[2]
zf = zipfile.ZipFile(pkg_path)
pkg_name = next(n for n in zf.namelist() if n.startswith("pkg-"))
raw = zf.read(pkg_name)
tar_bytes = zstandard.ZstdDecompressor().decompress(raw, max_output_size=200 * 1024 * 1024)
tarfile.open(fileobj=io.BytesIO(tar_bytes)).extractall(out_dir)
PYEOF

libgomp_so="$(find "${workdir}/extracted" -name 'libgomp.so.1.0.0' | head -1)"
if [[ ! -f "${libgomp_so}" ]]; then
    echo "Could not find libgomp.so.1.0.0 in ${pkg}" >&2
    exit 1
fi

# The whole point of fetching from conda-forge instead of using Rocky Linux 8's own libgomp:
# verify it actually supports what we need rather than trusting the download.
if ! nm -D "${libgomp_so}" 2>/dev/null | grep -qE ' T omp_fulfill_event(@|$)'; then
    echo "Fetched libgomp does not export omp_fulfill_event -- wrong package or bad extraction" >&2
    exit 1
fi

cp "${libgomp_so}" "${dest_dir}/libgomp.so.1.0.0"
ln -sf libgomp.so.1.0.0 "${dest_dir}/libgomp.so.1"

echo "Modern libgomp ready at ${dest_dir}/libgomp.so.1.0.0"
