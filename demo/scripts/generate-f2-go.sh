#!/usr/bin/env bash
set -euo pipefail

SPECS_DIR="${SPECS_DIR:-/specs}"
OUTPUT_DIR="/generated/go"
CONFIG="/config/go-server.yaml"
TEMPLATES="/templates/go-server"

echo "=== F2 Go: openapi-generator generate ==="
echo "Spec: ${SPECS_DIR}/openapi/logistics.yaml"
echo "Config: ${CONFIG}"
echo "Output: ${OUTPUT_DIR}"

# Ensure output directory exists and is clean
mkdir -p "${OUTPUT_DIR}"
rm -rf "${OUTPUT_DIR:?}"/*

# Run openapi-generator
java -jar /opt/openapi-generator/openapi-generator-cli.jar generate \
  -i "${SPECS_DIR}/openapi/logistics.yaml" \
  -g go-server \
  -c "${CONFIG}" \
  -t "${TEMPLATES}" \
  -o "${OUTPUT_DIR}" \
  --additional-properties=router=mux

# Verify output
FILE_COUNT=$(find "${OUTPUT_DIR}" -name "*.go" | wc -l)
echo "=== Generated ${FILE_COUNT} Go file(s) in ${OUTPUT_DIR} ==="

if [ "${FILE_COUNT}" -eq 0 ]; then
  echo "ERROR: No Go files generated" >&2
  exit 1
fi
