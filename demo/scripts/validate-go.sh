#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="/generated/go"

echo "=== Go: build validation ==="
echo "Target: ${OUTPUT_DIR}"

cd "${OUTPUT_DIR}"

# Initialize go module if not present
if [ ! -f "go.mod" ]; then
  go mod init logistics
fi

# Fetch dependencies
go mod tidy

# Build all packages
go build ./...

echo "=== Go validation passed ==="
