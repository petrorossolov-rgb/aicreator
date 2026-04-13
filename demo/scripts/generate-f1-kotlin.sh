#!/usr/bin/env bash
set -euo pipefail

SPECS_DIR="${SPECS_DIR:-/specs}"
OUTPUT_DIR="/generated/kotlin"

echo "=== F1 Kotlin: buf generate ==="
echo "Specs: ${SPECS_DIR}/proto"
echo "Output: ${OUTPUT_DIR}"

# Ensure output directory exists and is clean
mkdir -p "${OUTPUT_DIR}"
rm -rf "${OUTPUT_DIR:?}"/*

# Run buf generate from proto specs directory
cd "${SPECS_DIR}/proto"
buf generate

# Verify output
FILE_COUNT=$(find "${OUTPUT_DIR}" -name "*.java" -o -name "*.kt" | wc -l)
echo "=== Generated ${FILE_COUNT} file(s) in ${OUTPUT_DIR} ==="

if [ "${FILE_COUNT}" -eq 0 ]; then
  echo "ERROR: No files generated" >&2
  exit 1
fi
