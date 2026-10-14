#!/usr/bin/env bash
#
# Builds an importable Liferay fragment collection ZIP from the source in src/.
# No dependencies beyond a POSIX shell and "zip".
#
# Usage: ./build.sh
# Output: dist/accessible-fragments.zip
#
set -euo pipefail

cd "$(dirname "$0")"

# The folder name is the collection key in Liferay. It stays accessible-components
# so importing a new version overwrites the collection instead of duplicating it.
collection="accessible-components"
out="dist/accessible-fragments.zip"

mkdir -p dist
rm -f "${out}"

(cd src && zip -r -q "../${out}" "${collection}" -x '*.DS_Store')

echo "Built ${out}"
