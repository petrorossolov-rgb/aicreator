#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="/generated/python"

echo "=== Python: ruff format + check ==="
echo "Target: ${OUTPUT_DIR}"

# Check that generated files exist
FILE_COUNT=$(find "${OUTPUT_DIR}" -name "*.py" | wc -l)
if [ "${FILE_COUNT}" -eq 0 ]; then
  echo "ERROR: No .py files found in ${OUTPUT_DIR}" >&2
  exit 1
fi

# Run ruff format (fix in-place, generous line length for generated code)
ruff format --line-length 120 "${OUTPUT_DIR}"

# Run ruff check with auto-fix (--unsafe-fixes is safe for generated code)
# Ignore E501 (line too long) — ruff format handles line length; remaining cases are unfixable generated code
ruff check --fix --unsafe-fixes --select=E,W,F --ignore=E501,E721 --line-length 120 "${OUTPUT_DIR}"

echo "=== Python format complete (${FILE_COUNT} .py files) ==="
