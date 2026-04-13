#!/usr/bin/env bash
set -euo pipefail

# Run all 3 code generation pipelines sequentially via Docker Compose.
# Usage: ./scripts/run-all.sh [SPECS_DIR]
# Default SPECS_DIR: ./specs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEMO_DIR="$(dirname "${SCRIPT_DIR}")"

cd "${DEMO_DIR}"

export SPECS_DIR="${1:-${SPECS_DIR:-./specs}}"

echo "============================================"
echo " AICreator Demo — Full Pipeline"
echo " Specs: ${SPECS_DIR}"
echo "============================================"
echo ""

# Clean previous output
rm -rf generated/*

# Build all images
echo ">>> Building Docker images..."
docker compose build --quiet

# Run full pipeline (dependencies handled by docker compose)
echo ">>> Running generation + format + validation..."
docker compose up

# Summary
echo ""
echo "============================================"
echo " Pipeline Complete"
echo "============================================"
echo " Kotlin files: $(find generated/kotlin -name '*.kt' 2>/dev/null | wc -l)"
echo " Go files:     $(find generated/go -name '*.go' 2>/dev/null | wc -l)"
echo " Python files: $(find generated/python -name '*.py' 2>/dev/null | wc -l)"
echo "============================================"
