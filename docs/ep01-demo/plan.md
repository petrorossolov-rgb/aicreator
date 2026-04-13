# Plan: ep01-demo

## Step 1: Project Definition

- **Project name**: AICreator Demo
- **One-line description**: Docker-based demo of deterministic code generation — Proto→Kotlin, OpenAPI→Go server, OpenAPI→Python client — with post-processing and compilation validation
- **MVP scope**:
  - 3 generation functions (F1, F2, F4) running via `docker compose up`
  - Synthetic logistics-domain specs (Order, Shipment, Warehouse)
  - Post-processing: formatting + linting per language
  - Compilation validation per language
  - Volume swap for real specs via `SPECS_DIR` env var
  - Minimal mustache template customization (corporate header, package naming)
- **Out of scope (for now)**:
  - F3 (PUML→service) — requires AI, not deterministic
  - CLI framework (typer) — demo uses shell scripts
  - API server (FastAPI) — no server needed
  - Web UI — pure terminal demo
  - CI/CD integration — local execution only
  - F5 (AsyncAPI→event handlers) — deferred

---

## Step 2: Constitution (Immutable Principles)

See CLAUDE.md `## Constitution` section (updated separately).

Principles:
1. **Determinism First** — identical input → identical output, every time
2. **Docker-Isolated Execution** — host needs only Docker, nothing else
3. **Fail Fast, Fail Loud** — any step failure stops pipeline with clear error
4. **Swap Without Change** — replacing specs requires zero script/config edits
5. **Pinned Versions** — all Docker images use explicit version tags
6. **Zero Runtime Dependencies** — no DB, no API server, no message queues
7. **Minimal Customization** — template overrides only for header, package naming, basic error handling

---

## Step 3: Tech Stack

| Layer | Technology | Version | Reasoning |
|-------|-----------|---------|-----------|
| Orchestration | Docker Compose | v2 (compose spec) | Multi-container pipeline with dependency ordering |
| Proto→Kotlin | buf | v1.50+ (pinned in Dockerfile) | Managed plugins from BSR, clean YAML config, ADR-002 |
| Kotlin compiler | kotlinc (JDK) | Temurin 21 | LTS JDK, compilation validation |
| Kotlin formatter | ktlint | 1.5+ (JAR) | Official Kotlin linter, ADR-005 (16k+ stars) |
| OpenAPI codegen | openapi-generator-cli | v7.12.0 (pinned) | 60+ generators, mustache templates, ADR-005 (23k+ stars) |
| Go toolchain | Go | 1.23 | Current stable, includes gofmt |
| Go linter | golangci-lint | v1.63 | Meta-linter, includes gofmt, ADR-005 |
| Python runtime | Python | 3.12 | Current stable |
| Python formatter+linter | ruff | 0.9+ | 30x faster than black, formatter+linter in one, 35k+ stars |
| Shell scripts | bash | 5+ | Available in all Alpine/Debian containers |

### Version pinning strategy

Docker images pinned to minor version (e.g. `golang:1.23-alpine`, not `latest`). Tools installed in Dockerfiles pinned to exact version via URL/checksum where possible.

---

## Step 3.1: Development Tooling (MCP Servers)

No additional MCP servers needed. GitHub and Context7 already configured globally — sufficient for this epic. The project is shell scripts + Docker configs, no framework-specific tooling required.

---

## Step 4: Project Structure

```
demo/                               # Demo root (subdirectory of AICreator repo)
├── docker-compose.yml              # Pipeline orchestration: generate → format → validate
├── .env                            # SPECS_DIR=./specs (overridable)
├── .gitignore                      # Ignore generated/
├── README.md                       # Demo instructions: build, run, swap specs
│
├── specs/                          # Synthetic logistics-domain specs
│   ├── proto/
│   │   ├── buf.yaml                # buf module definition
│   │   ├── buf.gen.yaml            # Kotlin generation config
│   │   ├── common.proto            # Shared types: Address, Timestamp wrappers
│   │   ├── order.proto             # Order, OrderItem, OrderStatus
│   │   ├── shipment.proto          # Shipment, ShipmentItem, Location, ShipmentStatus
│   │   └── warehouse.proto         # Warehouse, InventoryItem
│   └── openapi/
│       └── logistics.yaml          # OpenAPI 3.0.3 spec: Orders, Shipments, Warehouses
│
├── templates/                      # Mustache template overrides for openapi-generator
│   ├── go-server/                  # Go: corporate header, package naming
│   │   └── partial_header.mustache
│   └── python/                     # Python: corporate header
│       └── partial_header.mustache
│
├── config/                         # openapi-generator configuration files
│   ├── go-server.yaml              # Generator: go-server, packageName, etc.
│   └── python-client.yaml          # Generator: python, packageName, packageVersion
│
├── scripts/                        # Shell scripts (entrypoints for Docker containers)
│   ├── generate-f1-kotlin.sh       # buf generate → /generated/kotlin/
│   ├── generate-f2-go.sh           # openapi-generator → /generated/go/
│   ├── generate-f4-python.sh       # openapi-generator → /generated/python/
│   ├── format-kotlin.sh            # ktlint -F
│   ├── format-go.sh                # gofmt -w + golangci-lint --fix
│   ├── format-python.sh            # ruff format + ruff check --fix
│   ├── validate-kotlin.sh          # kotlinc compile check
│   ├── validate-go.sh              # go build ./...
│   ├── validate-python.sh          # python3 -m compileall
│   └── run-all.sh                  # Local master script (alternative to docker compose)
│
├── dockerfiles/                    # One Dockerfile per function
│   ├── Dockerfile.kotlin           # Temurin 21 + buf + ktlint + kotlinc
│   ├── Dockerfile.go               # Go 1.23 + JRE + openapi-generator-cli + golangci-lint
│   └── Dockerfile.python           # Python 3.12 + JRE + openapi-generator-cli + ruff
│
└── generated/                      # Output directory (gitignored, created at runtime)
    ├── kotlin/
    ├── go/
    └── python/
```

### Directory purposes

| Directory | Purpose |
|-----------|---------|
| `specs/` | Input specifications — synthetic by default, swappable via volume |
| `templates/` | Minimal mustache overrides for openapi-generator |
| `config/` | openapi-generator YAML configs (package naming, additional properties) |
| `scripts/` | Shell scripts — entrypoints for Docker containers |
| `dockerfiles/` | One Dockerfile per language/function |
| `generated/` | Output — gitignored, created by pipeline |

---

## Step 5: Data Model

Нет persistent data model — проект генерирует код из спецификаций. Модели определены в спецификациях:

### Proto entities (F1 input)

| Entity | Key Fields | Relationships |
|--------|-----------|---------------|
| **Order** | order_id, customer_id, status, total_amount, created_at | has many OrderItem, has one Address |
| **OrderItem** | sku, quantity, unit_price, warehouse_preference | belongs to Order |
| **Shipment** | shipment_id, order_id, carrier, tracking_number, status | belongs to Order, has many ShipmentItem, has one Location |
| **ShipmentItem** | sku, quantity | belongs to Shipment |
| **Warehouse** | warehouse_id, name, capacity_utilization | has one Address, has many InventoryItem |
| **InventoryItem** | sku, quantity_on_hand, quantity_reserved, reorder_point | belongs to Warehouse |
| **Address** | line1, line2, city, state, postal_code, country | shared type |
| **Location** | latitude, longitude, address, timestamp | embedded in Shipment |

### OpenAPI entities (F2, F4 input)

Same entities as proto, exposed via REST:
- `POST/GET /orders`, `GET/PUT/DELETE /orders/{id}`
- `GET /shipments`, `GET /shipments/{id}`, `GET /shipments/{id}/track`
- `GET /warehouses`, `GET /warehouses/{id}`, `PATCH /warehouses/{id}/inventory/{sku}`

---

## Step 6: Implementation Phases

### Phase 1: Skeleton & Specifications
> **Deliverable**: repo structure + realistic synthetic specs, validated manually

- [ ] Create `demo/` directory structure, `.env`, `.gitignore`
- [ ] Write `demo/specs/proto/buf.yaml` — module name `logistics/v1`
- [ ] Write `demo/specs/proto/buf.gen.yaml` — Kotlin generation via protocolbuffers/kotlin plugin
- [ ] Write `demo/specs/proto/common.proto` — Address, shared enums
- [ ] Write `demo/specs/proto/order.proto` — Order, OrderItem, OrderStatus, OrderService
- [ ] Write `demo/specs/proto/shipment.proto` — Shipment, ShipmentItem, Location, ShipmentStatus, ShipmentService
- [ ] Write `demo/specs/proto/warehouse.proto` — Warehouse, InventoryItem, WarehouseService
- [ ] Write `demo/specs/openapi/logistics.yaml` — full OpenAPI 3.0.3 spec
- [ ] Write `demo/config/go-server.yaml` — openapi-generator config
- [ ] Write `demo/config/python-client.yaml` — openapi-generator config

### Phase 2: Dockerfiles & Generation Scripts
> **Deliverable**: each function generates code from specs (manual docker build + run)

- [ ] Write `demo/dockerfiles/Dockerfile.kotlin` — Temurin 21 + buf binary + ktlint JAR + protobuf-kotlin runtime
- [ ] Write `demo/scripts/generate-f1-kotlin.sh` — buf generate
- [ ] Test F1: `docker build + run` → Kotlin files appear in generated/kotlin/
- [ ] Write `demo/dockerfiles/Dockerfile.go` — Go 1.23 + JRE + openapi-generator-cli JAR + golangci-lint
- [ ] Write `demo/scripts/generate-f2-go.sh` — openapi-generator generate
- [ ] Test F2: `docker build + run` → Go files appear in generated/go/
- [ ] Write `demo/dockerfiles/Dockerfile.python` — Python 3.12 + JRE + openapi-generator-cli JAR + ruff
- [ ] Write `demo/scripts/generate-f4-python.sh` — openapi-generator generate
- [ ] Test F4: `docker build + run` → Python files appear in generated/python/

### Phase 3: Post-processing (Format + Validate)
> **Deliverable**: generated code is formatted and compiles without errors

- [ ] Write `demo/scripts/format-kotlin.sh` — ktlint -F
- [ ] Write `demo/scripts/format-go.sh` — gofmt -w + golangci-lint run --fix
- [ ] Write `demo/scripts/format-python.sh` — ruff format + ruff check --fix
- [ ] Write `demo/scripts/validate-kotlin.sh` — kotlinc compile check (with protobuf-kotlin-lite classpath)
- [ ] Write `demo/scripts/validate-go.sh` — go mod init + go mod tidy + go build ./...
- [ ] Write `demo/scripts/validate-python.sh` — python3 -m compileall
- [ ] Test each format + validate script independently

### Phase 4: Template Customization
> **Deliverable**: generated code contains corporate headers and correct package names

- [ ] Extract default mustache templates from openapi-generator for go-server
- [ ] Create `demo/templates/go-server/partial_header.mustache` — corporate header
- [ ] Extract default mustache templates from openapi-generator for python
- [ ] Create `demo/templates/python/partial_header.mustache` — corporate header
- [ ] Verify corporate header appears in generated Go and Python files

### Phase 5: Docker Compose Integration
> **Deliverable**: `docker compose up` runs full pipeline end-to-end

- [ ] Write `demo/docker-compose.yml` — 9 services (3 generate + 3 format + 3 validate) with depends_on
- [ ] Test full pipeline: `docker compose up --build`
- [ ] Test volume swap: `SPECS_DIR=./specs-alt docker compose up`
- [ ] Write `demo/scripts/run-all.sh` — alternative local execution script
- [ ] Write `demo/README.md` — setup, usage, volume swap instructions

---

## Step 7: Interface Design

No API or UI — the interface is the CLI:

### Primary interface: Docker Compose

```bash
# Full pipeline (default synthetic specs)
cd demo && docker compose up --build

# With real specs (volume swap)
SPECS_DIR=/path/to/real/specs docker compose up --build

# Single function only
docker compose up --build f1-kotlin format-kotlin validate-kotlin
```

### Docker Compose services

| Service | Image | Command | Depends On |
|---------|-------|---------|------------|
| `f1-kotlin` | `demo-kotlin` | `/scripts/generate-f1-kotlin.sh` | — |
| `f2-go` | `demo-go` | `/scripts/generate-f2-go.sh` | — |
| `f4-python` | `demo-python` | `/scripts/generate-f4-python.sh` | — |
| `format-kotlin` | `demo-kotlin` | `/scripts/format-kotlin.sh` | f1-kotlin |
| `format-go` | `demo-go` | `/scripts/format-go.sh` | f2-go |
| `format-python` | `demo-python` | `/scripts/format-python.sh` | f4-python |
| `validate-kotlin` | `demo-kotlin` | `/scripts/validate-kotlin.sh` | format-kotlin |
| `validate-go` | `demo-go` | `/scripts/validate-go.sh` | format-go |
| `validate-python` | `demo-python` | `/scripts/validate-python.sh` | format-python |

### Output structure

```
generated/
├── kotlin/
│   └── logistics/v1/           # Package from proto package
│       ├── OrderKt.kt
│       ├── ShipmentKt.kt
│       └── WarehouseKt.kt
├── go/
│   ├── go.mod
│   ├── main.go
│   └── api/
│       ├── api_order.go
│       ├── api_shipment.go
│       ├── api_warehouse.go
│       └── model_*.go
└── python/
    ├── setup.py
    ├── logistics_client/
    │   ├── __init__.py
    │   ├── api/
    │   │   ├── order_api.py
    │   │   ├── shipment_api.py
    │   │   └── warehouse_api.py
    │   └── models/
    │       ├── order.py
    │       ├── shipment.py
    │       └── warehouse.py
    └── test/
```

---

## Step 9: Open Questions

Нет открытых вопросов — все ключевые решения приняты в фазе research:
- ✅ Kotlin: data classes (protobuf-kotlin)
- ✅ Go: go-server (net/http)
- ✅ Docker: отдельные images
- ✅ Repo: директория demo/ в AICreator
- ✅ Python: ruff

---

## Verification Plan

1. `cd demo && docker compose build` — все 3 images собираются без ошибок
2. `docker compose up` — все 9 сервисов завершаются с exit code 0
3. `ls generated/kotlin/` — Kotlin data classes присутствуют
4. `ls generated/go/` — Go server stubs с корректным package
5. `ls generated/python/` — Python client library
6. `grep -r "Copyright" generated/go/ generated/python/` — corporate header
7. Повторный запуск с теми же specs — идентичный output (determinism check)
8. `SPECS_DIR=./specs-alt docker compose up` — volume swap работает
