# AICreator Demo — Deterministic Code Generation Pipeline

Docker-based pipeline that generates, formats, and validates code from Proto and OpenAPI specifications.

## Prerequisites

- **Docker** (with Docker Compose v2)
- No other tools required — everything runs inside containers

## Quick Start

```bash
cd demo
docker compose up --build
```

This runs 9 services in dependency order:

| Wave | Services | Description |
|------|----------|-------------|
| 1 | `f1-kotlin`, `f2-go`, `f4-python` | Code generation (parallel) |
| 2 | `format-kotlin`, `format-go`, `format-python` | Formatting & linting |
| 3 | `validate-kotlin`, `validate-go`, `validate-python` | Compilation & syntax checks |

Output appears in `generated/`:
- `generated/kotlin/` — Kotlin + Java classes from Proto specs (buf + protoc)
- `generated/go/` — Go server stubs from OpenAPI spec (openapi-generator, go-server)
- `generated/python/` — Python client from OpenAPI spec (openapi-generator, python)

## Functions

| Function | Input | Generator | Output |
|----------|-------|-----------|--------|
| F1 Kotlin | Proto specs (`specs/proto/`) | buf + protoc | Kotlin/Java data classes, gRPC stubs |
| F2 Go | OpenAPI spec (`specs/openapi/`) | openapi-generator (go-server) | Go HTTP server with mux router |
| F4 Python | OpenAPI spec (`specs/openapi/`) | openapi-generator (python) | Python API client library |

## Volume Swap — Using Your Own Specs

Replace input specifications without editing any file:

```bash
SPECS_DIR=./your-specs docker compose up --build
```

The specs directory must contain:
```
your-specs/
├── proto/           # buf.yaml, buf.gen.yaml, *.proto files
│   ├── buf.yaml
│   ├── buf.gen.yaml
│   └── *.proto
└── openapi/
    └── logistics.yaml   # OpenAPI 3.0.3 spec
```

An alternative spec set (`specs-alt/`) is included for testing:
```bash
SPECS_DIR=./specs-alt docker compose up --build
```

## Running Individual Pipelines

```bash
# Kotlin only (generate + format + validate)
docker compose up f1-kotlin format-kotlin validate-kotlin

# Go only
docker compose up f2-go format-go validate-go

# Python only
docker compose up f4-python format-python validate-python
```

## Convenience Script

```bash
./scripts/run-all.sh                    # Default specs
./scripts/run-all.sh ./specs-alt        # Alternative specs
```

## Project Structure

```
demo/
├── docker-compose.yml          # Pipeline orchestration (9 services)
├── dockerfiles/
│   ├── Dockerfile.kotlin       # JDK 21 + buf + protoc + ktlint + kotlinc
│   ├── Dockerfile.go           # Go 1.23 + openapi-generator + golangci-lint
│   └── Dockerfile.python       # Python 3.12 + openapi-generator + ruff
├── scripts/
│   ├── generate-f1-kotlin.sh   # Proto → Kotlin/Java
│   ├── generate-f2-go.sh       # OpenAPI → Go server
│   ├── generate-f4-python.sh   # OpenAPI → Python client
│   ├── format-kotlin.sh        # ktlint -F
│   ├── format-go.sh            # gofmt + golangci-lint --fix
│   ├── format-python.sh        # ruff format + ruff check --fix
│   ├── validate-kotlin.sh      # javac + kotlinc compilation
│   ├── validate-go.sh          # go build ./...
│   ├── validate-python.sh      # python3 -m compileall
│   └── run-all.sh              # Convenience wrapper
├── specs/                      # Default synthetic specifications
│   ├── proto/                  # Logistics proto (Order, Shipment, Warehouse)
│   └── openapi/                # Logistics REST API (OpenAPI 3.0.3)
├── specs-alt/                  # Alternative specs for volume swap testing
├── specs-invalid/              # Invalid specs for fail-fast testing
├── config/                     # openapi-generator config files
├── templates/                  # Mustache template overrides (corporate header)
└── generated/                  # Output directory (gitignored)
```

## Expected Output

With default specs (`./specs`):

| Language | Files | Key classes/packages |
|----------|-------|---------------------|
| Kotlin | ~43 .kt + ~84 .java | `com.logistics.v1` — Order, Shipment, Warehouse |
| Go | ~31 .go | `package logistics` — server stubs with mux router |
| Python | ~52 .py | `logistics_client` — API client with models |

## Error Handling

The pipeline follows **Fail Fast, Fail Loud** — any error stops the pipeline immediately:

```bash
# Test with invalid specs
SPECS_DIR=./specs-invalid docker compose up f1-kotlin
# → exits non-zero: "broken.proto:7:3: syntax error: expecting ';'"

SPECS_DIR=./specs-invalid docker compose up f2-go
# → exits non-zero: "attribute paths is missing"
```

## Pinned Versions

All tool versions are explicit (no `latest` tags):

| Tool | Version | Image |
|------|---------|-------|
| JDK | 21 (Eclipse Temurin Alpine) | Dockerfile.kotlin |
| buf | 1.50.0 | Dockerfile.kotlin |
| protoc | 29.3 | Dockerfile.kotlin |
| ktlint | 1.5.0 | Dockerfile.kotlin |
| kotlinc | 2.1.10 | Dockerfile.kotlin |
| Go | 1.23 Alpine | Dockerfile.go |
| openapi-generator | 7.12.0 | Dockerfile.go, Dockerfile.python |
| golangci-lint | 1.63.4 | Dockerfile.go |
| Python | 3.12 slim | Dockerfile.python |
| ruff | 0.9.10 | Dockerfile.python |
