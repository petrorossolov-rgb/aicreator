#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="/generated/kotlin"

echo "=== Kotlin: ktlint format ==="
echo "Target: ${OUTPUT_DIR}"

# Check that generated files exist
FILE_COUNT=$(find "${OUTPUT_DIR}" -name "*.kt" | wc -l)
if [ "${FILE_COUNT}" -eq 0 ]; then
  echo "ERROR: No .kt files found in ${OUTPUT_DIR}" >&2
  exit 1
fi

# Disable function-naming rule — protobuf Kotlin DSL uses non-standard names
cat > "${OUTPUT_DIR}/.editorconfig" <<'EDITORCONFIG'
root = true

[*.kt]
ktlint_standard_function-naming = disabled
EDITORCONFIG

# Run ktlint in format mode (fix in-place)
ktlint -F "${OUTPUT_DIR}/**/*.kt"

echo "=== Kotlin format complete (${FILE_COUNT} .kt files) ==="
