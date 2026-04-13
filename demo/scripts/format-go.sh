#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="/generated/go"

echo "=== Go: gofmt + golangci-lint format ==="
echo "Target: ${OUTPUT_DIR}"

# Check that generated files exist
FILE_COUNT=$(find "${OUTPUT_DIR}" -name "*.go" | wc -l)
if [ "${FILE_COUNT}" -eq 0 ]; then
  echo "ERROR: No .go files found in ${OUTPUT_DIR}" >&2
  exit 1
fi

# Run gofmt (format in-place)
find "${OUTPUT_DIR}" -name "*.go" -exec gofmt -w {} +

# Initialize go module and download deps (needed for golangci-lint)
cd "${OUTPUT_DIR}"
if [ ! -f "go.mod" ]; then
  go mod init logistics
fi
go mod tidy
go mod download

# Run golangci-lint with --fix (minimal linters for generated code)
golangci-lint run --fix --disable-all --enable=gofmt,govet ./... || true

echo "=== Go format complete (${FILE_COUNT} .go files) ==="
