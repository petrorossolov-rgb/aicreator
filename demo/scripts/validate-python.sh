#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="/generated/python"

echo "=== Python: syntax validation ==="
echo "Target: ${OUTPUT_DIR}"

# Compile all Python files (syntax check)
python3 -m compileall -q "${OUTPUT_DIR}"

echo "=== Python validation passed ==="
