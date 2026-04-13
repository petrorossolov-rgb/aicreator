#!/usr/bin/env bash
set -euo pipefail

SPECS_DIR="${SPECS_DIR:-/specs}"
OUTPUT_DIR="/generated/python"
CONFIG="/config/python-client.yaml"
TEMPLATES="/templates/python"

echo "=== F4 Python: openapi-generator generate ==="
echo "Spec: ${SPECS_DIR}/openapi/logistics.yaml"
echo "Config: ${CONFIG}"
echo "Output: ${OUTPUT_DIR}"

# Ensure output directory exists and is clean
mkdir -p "${OUTPUT_DIR}"
rm -rf "${OUTPUT_DIR:?}"/*

# Run openapi-generator
java -jar /opt/openapi-generator/openapi-generator-cli.jar generate \
  -i "${SPECS_DIR}/openapi/logistics.yaml" \
  -g python \
  -c "${CONFIG}" \
  -t "${TEMPLATES}" \
  -o "${OUTPUT_DIR}"

# Verify output
FILE_COUNT=$(find "${OUTPUT_DIR}" -name "*.py" | wc -l)
echo "=== Generated ${FILE_COUNT} Python file(s) in ${OUTPUT_DIR} ==="

if [ "${FILE_COUNT}" -eq 0 ]; then
  echo "ERROR: No Python files generated" >&2
  exit 1
fi
