#!/usr/bin/env bash
#
# Builds an importable Liferay fragment collection ZIP from the source in src/.
# No dependencies beyond a POSIX shell and "zip".
#
# Usage: ./build.sh
# Output: dist/accessible-components.zip
#
set -euo pipefail

cd "$(dirname "$0")"

collection="accessible-components"
out="dist/${collection}.zip"

mkdir -p dist
rm -f "${out}"

(cd src && zip -r -q "../${out}" "${collection}" -x '*.DS_Store')

echo "Built ${out}"
