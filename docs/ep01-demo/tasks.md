# Tasks: ep01-demo

## Dependency Map

```
[T01] ← none                         # Skeleton: dirs, .env, .gitignore
[T02] ← none                         # Proto specs (order, shipment, warehouse)
[T03] ← none                         # OpenAPI spec (logistics.yaml)
[T04] ← none                         # openapi-generator configs + mustache templates
[T05] ← T01, T02                     # Dockerfile.kotlin + generate script + test
[T05a] ← T05                         # Pre-flight: validate buf Kotlin generation in Docker
[T06] ← T01, T03, T04                # Dockerfile.go + generate script + test
[T07] ← T01, T03, T04                # Dockerfile.python + generate script + test
[T08] ← T05a                         # Kotlin format + validate scripts + test
[T09] ← T06                          # Go format + validate scripts + test
[T10] ← T07                          # Python format + validate scripts + test
[T11] ← T08, T09, T10                # docker-compose.yml + full pipeline test
[T11a] ← T11                         # Negative test: pipeline on invalid input
[T12] ← T11a                         # run-all.sh + README.md + volume swap test
```

---

## Task List

### [T01] Project skeleton: directories, .env, .gitignore
- **Phase**: 1 — Skeleton & Specifications
- **Type**: setup
- **Depends on**: none
- **Input**: AICreator repo root
- **Output**: `demo/` directory with `.env`, `.gitignore`, empty subdirectories
- **Acceptance criteria**:
  - [ ] `demo/.env` exists with `SPECS_DIR=./specs`
  - [ ] `demo/.gitignore` ignores `generated/` directory
  - [ ] Directories exist: `demo/specs/proto/`, `demo/specs/openapi/`, `demo/templates/go-server/`, `demo/templates/python/`, `demo/config/`, `demo/scripts/`, `demo/dockerfiles/`
- **Tests required**: none (pure file creation)
- **Constitution check**: Docker-Isolated Execution (structure supports container volume mounts)
- **Implementation notes**: `.gitignore` should include `generated/`, `*.jar`, `.env.local`. `.env` uses `SPECS_DIR` variable referenced by docker-compose later.

---

### [T02] Synthetic Proto specifications
- **Phase**: 1 — Skeleton & Specifications
- **Type**: data
- **Depends on**: none
- **Input**: Data model from plan (Order, Shipment, Warehouse entities)
- **Output**: `demo/specs/proto/` — buf.yaml, buf.gen.yaml, common.proto, order.proto, shipment.proto, warehouse.proto
- **Acceptance criteria**:
  - [ ] `buf.yaml` defines module `logistics/v1` with lint and breaking change detection
  - [ ] `buf.gen.yaml` configures `buf.build/protocolbuffers/java` + `buf.build/protocolbuffers/kotlin` plugins with output to `generated/kotlin`
  - [ ] `common.proto` defines Address message and imports google/protobuf/timestamp.proto
  - [ ] `order.proto` defines Order, OrderItem, OrderStatus enum, OrderService with CRUD RPCs
  - [ ] `shipment.proto` defines Shipment, ShipmentItem, Location, ShipmentStatus enum, ShipmentService
  - [ ] `warehouse.proto` defines Warehouse, InventoryItem, WarehouseService
  - [ ] All protos use `syntax = "proto3"` and `package logistics.v1`
  - [ ] Cross-references work (Order uses Address from common.proto)
- **Tests required**:
  - [ ] `buf lint` passes (run manually or via Docker if buf available)
- **Constitution check**: Determinism First (proto specs are the deterministic input)
- **Implementation notes**: Use `google.protobuf.Timestamp` for time fields. Keep services simple: Create, Get, List, Update, Delete. Filter/request messages as separate types (not inlined).

---

### [T03] Synthetic OpenAPI specification
- **Phase**: 1 — Skeleton & Specifications
- **Type**: data
- **Depends on**: none
- **Input**: Data model from plan (same entities as proto, REST API)
- **Output**: `demo/specs/openapi/logistics.yaml`
- **Acceptance criteria**:
  - [ ] Valid OpenAPI 3.0.3 spec (not 3.1 — openapi-generator compatibility)
  - [ ] Paths: `/orders` (POST, GET), `/orders/{orderId}` (GET, PUT, DELETE)
  - [ ] Paths: `/shipments` (GET), `/shipments/{shipmentId}` (GET), `/shipments/{shipmentId}/track` (GET)
  - [ ] Paths: `/warehouses` (GET), `/warehouses/{warehouseId}` (GET), `/warehouses/{warehouseId}/inventory/{sku}` (PATCH)
  - [ ] Schemas: Order, OrderItem, Shipment, ShipmentItem, Warehouse, InventoryItem, Address, Location
  - [ ] All operations have operationId (required for clean codegen)
  - [ ] Pagination on list endpoints (limit/offset query params)
  - [ ] Enum types for OrderStatus, ShipmentStatus
- **Tests required**:
  - [ ] Spec validates against OpenAPI 3.0.3 schema (openapi-generator-cli validate)
- **Constitution check**: Determinism First (OpenAPI spec is deterministic input), Minimal Customization (spec is realistic but not over-engineered)
- **Implementation notes**: Use OpenAPI 3.0.3 (not 3.1) for maximum openapi-generator compatibility. Include `info.contact`, `servers` section. Use `$ref` for schema reuse.

---

### [T04] openapi-generator configs and mustache templates
- **Phase**: 1 + 4 — Specifications + Template Customization
- **Type**: setup
- **Depends on**: none
- **Input**: Plan tech stack (go-server, python generators)
- **Output**: `demo/config/go-server.yaml`, `demo/config/python-client.yaml`, `demo/templates/go-server/partial_header.mustache`, `demo/templates/python/partial_header.mustache`
- **Acceptance criteria**:
  - [ ] `go-server.yaml` sets: packageName=logistics, generateInterfaces=true, sourceFolder=src
  - [ ] `python-client.yaml` sets: packageName=logistics_client, packageVersion=1.0.0, projectName=logistics-client
  - [ ] Go mustache template adds corporate header comment to generated files
  - [ ] Python mustache template adds corporate header comment to generated files
  - [ ] Header contains placeholder: `Copyright (c) 2026 X5 Group. Generated by AICreator.`
- **Tests required**: none (validated during T06, T07 generation)
- **Constitution check**: Minimal Customization (only header + package naming), Swap Without Change (configs reference $SPECS_DIR paths)
- **Implementation notes**: Extract default `partial_header.mustache` from openapi-generator for each generator to understand the template structure, then override. Config files use YAML format compatible with openapi-generator `-c` flag. Corporate header is a placeholder — swap to real text before demo.

---

### [T05] F1 Kotlin: Dockerfile + generation script + test
- **Phase**: 2 — Dockerfiles & Generation Scripts
- **Type**: feature
- **Depends on**: T01, T02
- **Input**: Proto specs in `demo/specs/proto/`, skeleton in `demo/`
- **Output**: `demo/dockerfiles/Dockerfile.kotlin`, `demo/scripts/generate-f1-kotlin.sh`
- **Acceptance criteria**:
  - [ ] Dockerfile.kotlin based on `eclipse-temurin:21-jdk-alpine` with pinned version
  - [ ] buf installed as binary (pinned version, e.g., v1.50.0)
  - [ ] ktlint JAR downloaded (pinned version, e.g., 1.5.0)
  - [ ] protobuf-kotlin runtime JAR available for compilation validation
  - [ ] `generate-f1-kotlin.sh` runs `buf generate` with specs from `$SPECS_DIR/proto`
  - [ ] Script has `set -euo pipefail` (fail fast)
  - [ ] Script outputs to `/generated/kotlin/`
  - [ ] `docker build -f dockerfiles/Dockerfile.kotlin -t demo-kotlin .` succeeds
  - [ ] `docker run` with volume mounts produces Kotlin files in `generated/kotlin/`
  - [ ] Generated files contain Kotlin data classes for Order, Shipment, Warehouse
- **Tests required**:
  - [ ] Build image → exit code 0
  - [ ] Run generation → Kotlin .kt files exist in output dir
  - [ ] Generated files are non-empty and contain `class Order`
- **Constitution check**: Docker-Isolated Execution, Pinned Versions, Fail Fast, Determinism First
- **Implementation notes**: buf remote plugins (buf.build/protocolbuffers/kotlin) require network on first run. Consider caching plugin in Dockerfile layer. Script must reference `$SPECS_DIR` env var — NOT hardcoded path. All scripts must be `chmod +x`.

---

### [T05a] Pre-flight: validate buf Kotlin generation in Docker
- **Phase**: 2 — Dockerfiles & Generation Scripts
- **Type**: test
- **Depends on**: T05
- **Input**: Dockerfile.kotlin built, proto specs in `demo/specs/proto/`
- **Output**: Confirmed working generation; if remote plugins fail → updated Dockerfile with local plugin binary
- **Acceptance criteria**:
  - [ ] `docker run demo-kotlin /scripts/generate-f1-kotlin.sh` produces Kotlin files
  - [ ] If buf remote plugins fail (network issue): Dockerfile updated to install `protoc-gen-kotlin` binary locally
  - [ ] Generated Kotlin files import `com.google.protobuf` correctly
  - [ ] Generation completes in under 60 seconds
- **Tests required**:
  - [ ] Run generation twice — output is byte-identical (determinism)
  - [ ] Disconnect network simulation: verify error message is clear if plugins unavailable
- **Constitution check**: Determinism First (identical output), Docker-Isolated Execution, Fail Fast (clear error on plugin failure)
- **Implementation notes**: If remote plugins fail, fallback plan: install `protoc` + `protoc-gen-kotlin` binary directly in Dockerfile instead of using buf BSR. This trades buf's managed plugin convenience for offline reliability. Master plan notes "все зависимости предзагружены во внутренние реестры".

---

### [T06] F2 Go: Dockerfile + generation script + test
- **Phase**: 2 — Dockerfiles & Generation Scripts
- **Type**: feature
- **Depends on**: T01, T03, T04
- **Input**: OpenAPI spec, go-server config, mustache templates
- **Output**: `demo/dockerfiles/Dockerfile.go`, `demo/scripts/generate-f2-go.sh`
- **Acceptance criteria**:
  - [ ] Dockerfile.go based on `golang:1.23-alpine` with pinned version
  - [ ] JRE installed (for openapi-generator-cli JAR)
  - [ ] openapi-generator-cli JAR downloaded (pinned v7.12.0)
  - [ ] golangci-lint installed (pinned v1.63.x)
  - [ ] `generate-f2-go.sh` runs openapi-generator with `-g go-server -c /config/go-server.yaml -t /templates/go-server`
  - [ ] Script has `set -euo pipefail`
  - [ ] Script reads spec from `$SPECS_DIR/openapi/logistics.yaml`
  - [ ] Script outputs to `/generated/go/`
  - [ ] `docker build` succeeds, `docker run` produces Go files
  - [ ] Generated Go files have correct package name from config
- **Tests required**:
  - [ ] Build image → exit code 0
  - [ ] Run generation → .go files exist in output dir
  - [ ] Generated files contain `package logistics` (or configured package name)
  - [ ] Corporate header present in generated files
- **Constitution check**: Docker-Isolated Execution, Pinned Versions, Fail Fast, Swap Without Change
- **Implementation notes**: openapi-generator-cli is a fat JAR (~30MB). Download via curl in Dockerfile. JRE: `apk add openjdk17-jre-headless` in Alpine. The `-t` flag points to `/templates/go-server/` (volume-mounted). Go generator may need `--additional-properties=router=mux` for clean net/http output.

---

### [T07] F4 Python: Dockerfile + generation script + test
- **Phase**: 2 — Dockerfiles & Generation Scripts
- **Type**: feature
- **Depends on**: T01, T03, T04
- **Input**: OpenAPI spec, python-client config, mustache templates
- **Output**: `demo/dockerfiles/Dockerfile.python`, `demo/scripts/generate-f4-python.sh`
- **Acceptance criteria**:
  - [ ] Dockerfile.python based on `python:3.12-slim` with pinned version
  - [ ] JRE installed (for openapi-generator-cli JAR)
  - [ ] openapi-generator-cli JAR downloaded (pinned v7.12.0)
  - [ ] ruff installed via pip (pinned version)
  - [ ] `generate-f4-python.sh` runs openapi-generator with `-g python -c /config/python-client.yaml -t /templates/python`
  - [ ] Script has `set -euo pipefail`
  - [ ] Script reads spec from `$SPECS_DIR/openapi/logistics.yaml`
  - [ ] Script outputs to `/generated/python/`
  - [ ] `docker build` succeeds, `docker run` produces Python files
  - [ ] Generated Python files have correct package name `logistics_client`
- **Tests required**:
  - [ ] Build image → exit code 0
  - [ ] Run generation → .py files exist in output dir
  - [ ] Generated files contain `logistics_client` package structure
  - [ ] Corporate header present in generated files
- **Constitution check**: Docker-Isolated Execution, Pinned Versions, Fail Fast, Swap Without Change
- **Implementation notes**: Python slim image + JRE: `apt-get install -y default-jre-headless`. ruff: `pip install ruff==0.9.x`. Same openapi-generator JAR as Go image (consider shared base or just duplicate — demo simplicity > DRY).

---

### [T08] Kotlin post-processing: format + validate scripts + test
- **Phase**: 3 — Post-processing
- **Type**: feature
- **Depends on**: T05
- **Input**: Generated Kotlin files in `generated/kotlin/`, Dockerfile.kotlin with ktlint + kotlinc
- **Output**: `demo/scripts/format-kotlin.sh`, `demo/scripts/validate-kotlin.sh`
- **Acceptance criteria**:
  - [ ] `format-kotlin.sh` runs `ktlint -F` on `/generated/kotlin/`
  - [ ] `validate-kotlin.sh` runs `kotlinc` compilation check with protobuf-kotlin runtime on classpath
  - [ ] Both scripts have `set -euo pipefail`
  - [ ] Format script fixes style issues in-place
  - [ ] Validate script exits 0 if compilation succeeds, non-zero otherwise
  - [ ] Running format → validate sequentially on generated Kotlin succeeds
- **Tests required**:
  - [ ] After generation + format: ktlint reports no issues
  - [ ] After generation + format + validate: kotlinc exits 0
- **Constitution check**: Fail Fast (non-zero exit on failure), Determinism First (format is idempotent)
- **Implementation notes**: kotlinc needs protobuf-kotlin-lite JAR on classpath (`-cp /path/to/protobuf-kotlin-lite.jar`). ktlint may need `.editorconfig` or `--code-style=kotlin_official` flag. Validate script should compile to a temp dir and clean up.

---

### [T09] Go post-processing: format + validate scripts + test
- **Phase**: 3 — Post-processing
- **Type**: feature
- **Depends on**: T06
- **Input**: Generated Go files in `generated/go/`, Dockerfile.go with gofmt + golangci-lint
- **Output**: `demo/scripts/format-go.sh`, `demo/scripts/validate-go.sh`
- **Acceptance criteria**:
  - [ ] `format-go.sh` runs `gofmt -w` + `golangci-lint run --fix` on `/generated/go/`
  - [ ] `validate-go.sh` runs `go mod tidy && go build ./...` in `/generated/go/`
  - [ ] Both scripts have `set -euo pipefail`
  - [ ] Format fixes formatting + lint issues in-place
  - [ ] Validate exits 0 if build succeeds
  - [ ] Running format → validate sequentially succeeds
- **Tests required**:
  - [ ] After generation + format: `gofmt -l` returns no files (all formatted)
  - [ ] After generation + format + validate: `go build` exits 0
- **Constitution check**: Fail Fast, Determinism First
- **Implementation notes**: Generated go-server code needs a `go.mod`. The validate script should do `go mod init` if go.mod doesn't exist, then `go mod tidy` to fetch dependencies. golangci-lint config: disable noisy linters for generated code (or use `--disable-all --enable=gofmt,govet,errcheck`).

---

### [T10] Python post-processing: format + validate scripts + test
- **Phase**: 3 — Post-processing
- **Type**: feature
- **Depends on**: T07
- **Input**: Generated Python files in `generated/python/`, Dockerfile.python with ruff
- **Output**: `demo/scripts/format-python.sh`, `demo/scripts/validate-python.sh`
- **Acceptance criteria**:
  - [ ] `format-python.sh` runs `ruff format` + `ruff check --fix` on `/generated/python/`
  - [ ] `validate-python.sh` runs `python3 -m compileall` on `/generated/python/`
  - [ ] Both scripts have `set -euo pipefail`
  - [ ] Format fixes style issues in-place
  - [ ] Validate exits 0 if syntax check passes
  - [ ] Running format → validate sequentially succeeds
- **Tests required**:
  - [ ] After generation + format: `ruff check` exits 0 (no remaining issues)
  - [ ] After generation + format + validate: `compileall` exits 0
- **Constitution check**: Fail Fast, Determinism First
- **Implementation notes**: ruff config may need `[tool.ruff] line-length = 120` (generated code can have long lines). `compileall` checks syntax only — sufficient for demo. Consider `ruff check --select=E,W,F` to focus on errors, not style nitpicks on generated code.

---

### [T11] Docker Compose: full pipeline integration
- **Phase**: 5 — Docker Compose Integration
- **Type**: feature
- **Depends on**: T08, T09, T10
- **Input**: All Dockerfiles, all scripts, all specs and configs
- **Output**: `demo/docker-compose.yml`
- **Acceptance criteria**:
  - [ ] 9 services defined: f1-kotlin, f2-go, f4-python, format-kotlin, format-go, format-python, validate-kotlin, validate-go, validate-python
  - [ ] Generation services have no dependencies (run in parallel)
  - [ ] Format services depend on their generation service (`condition: service_completed_successfully`)
  - [ ] Validate services depend on their format service
  - [ ] Volume mounts: `${SPECS_DIR:-./specs}:/specs:ro`, `./generated:/generated`, `./scripts:/scripts:ro`, `./templates:/templates:ro`, `./config:/config:ro`
  - [ ] `docker compose build` succeeds
  - [ ] `docker compose up` — all 9 services exit 0
  - [ ] `generated/kotlin/`, `generated/go/`, `generated/python/` contain expected files after run
- **Tests required**:
  - [ ] Full pipeline: `docker compose up --build` exits 0
  - [ ] All 3 output directories are non-empty
  - [ ] Repeat run produces identical output (determinism)
- **Constitution check**: All principles — this is the integration point
- **Implementation notes**: Use `docker compose` v2 syntax (no `version:` key). Each service uses `build: context: . dockerfile: dockerfiles/Dockerfile.{lang}`. Scripts mounted as `/scripts/`. Use `entrypoint: ["/bin/bash"]` with `command: ["/scripts/generate-f1-kotlin.sh"]`.

---

### [T11a] Negative test: pipeline behavior on invalid input
- **Phase**: 5 — Docker Compose Integration
- **Type**: test
- **Depends on**: T11
- **Input**: Working docker-compose pipeline, deliberately invalid specs
- **Output**: Verified "Fail Fast" behavior; minimal `demo/specs-invalid/` test fixtures
- **Acceptance criteria**:
  - [ ] Create `demo/specs-invalid/proto/` with a malformed .proto file (syntax error)
  - [ ] Create `demo/specs-invalid/openapi/` with a malformed OpenAPI spec (missing required fields)
  - [ ] `SPECS_DIR=./specs-invalid docker compose up f1-kotlin` → exits non-zero with clear error message
  - [ ] `SPECS_DIR=./specs-invalid docker compose up f2-go f4-python` → exits non-zero with clear error
  - [ ] Error messages contain actionable information (file name, line number or field name)
  - [ ] `generated/` directory is empty or contains no partial output after failure
- **Tests required**:
  - [ ] Invalid proto → f1-kotlin fails, error mentions syntax issue
  - [ ] Invalid OpenAPI → f2-go and f4-python fail, error mentions validation issue
  - [ ] Valid specs still work after invalid run (no state pollution)
- **Constitution check**: Fail Fast, Fail Loud (clear errors, non-zero exit, no partial output)
- **Implementation notes**: Create minimal invalid fixtures — one broken proto (missing semicolon), one broken OpenAPI (missing `paths` key). After negative test, re-run with valid specs to confirm pipeline recovers cleanly. `specs-invalid/` should be committed to repo as test fixtures.

---

### [T12] README, run-all.sh, volume swap test
- **Phase**: 5 — Docker Compose Integration
- **Type**: docs
- **Depends on**: T11a
- **Input**: Working docker-compose pipeline
- **Output**: `demo/README.md`, `demo/scripts/run-all.sh`
- **Acceptance criteria**:
  - [ ] README covers: prerequisites (Docker), quick start (`docker compose up --build`), volume swap instructions, project structure overview, what each function generates
  - [ ] `run-all.sh` runs all 3 pipelines sequentially as alternative to docker compose
  - [ ] Volume swap tested: create minimal alt spec, run with `SPECS_DIR=./specs-alt`
  - [ ] README includes example output / expected results
- **Tests required**:
  - [ ] `SPECS_DIR=./specs-alt docker compose up` works with alternative specs
- **Constitution check**: Swap Without Change (volume swap works), Docker-Isolated Execution (README states Docker-only requirement)
- **Implementation notes**: `run-all.sh` is a convenience — calls docker compose up or individual docker run commands. Create a minimal `specs-alt/` with one proto + one openapi for swap testing (can be a subset). README in English.

---

## Execution Order

```
── Wave 1 (no dependencies) ────────────────────────────
   T01: Project skeleton               🟡 Important
   T02: Proto specifications            🔴 Critical path
   T03: OpenAPI specification           🔴 Critical path
   T04: Configs + mustache templates    🟡 Important

── Wave 2 (after Wave 1) ──────────────────────────────
   T05: F1 Kotlin Dockerfile + gen     🔴 Critical path  ← T01, T02
   T06: F2 Go Dockerfile + gen         🔴 Critical path  ← T01, T03, T04
   T07: F4 Python Dockerfile + gen     🟡 Important      ← T01, T03, T04

── Wave 2.5 (after T05) ──────────────────────────────
   T05a: Pre-flight buf Kotlin check   🔴 Critical path  ← T05

── Wave 3 (after Wave 2/2.5) ─────────────────────────
   T08: Kotlin format + validate       🔴 Critical path  ← T05a
   T09: Go format + validate           🔴 Critical path  ← T06
   T10: Python format + validate       🟡 Important      ← T07

── Wave 4 (after Wave 3) ──────────────────────────────
   T11: Docker Compose integration     🔴 Critical path  ← T08, T09, T10

── Wave 4.5 (after T11) ──────────────────────────────
   T11a: Negative test (invalid input) 🟡 Important      ← T11

── Wave 5 (after Wave 4.5) ────────────────────────────
   T12: README + run-all + swap test   🟢 Flexible       ← T11a
```

---

## Critical Path

```
T02 → T05 → T05a → T08 → T11 → T11a → T12
```

Longest chain: 7 tasks. Alternative parallel chain: `T03 → T06 → T09 → T11` (shorter, merges at T11).

Any delay in specs (T02, T03), Dockerfiles (T05, T06), or post-processing (T08, T09) delays the entire project.

---

## Progress Tracker

### Wave 1
- [x] T01: Project skeleton: directories, .env, .gitignore
- [x] T02: Synthetic Proto specifications
- [x] T03: Synthetic OpenAPI specification
- [x] T04: openapi-generator configs + mustache templates

### Wave 2
- [x] T05: F1 Kotlin: Dockerfile + generation script + test
- [x] T05a: Pre-flight: validate buf Kotlin generation in Docker
- [x] T06: F2 Go: Dockerfile + generation script + test
- [x] T07: F4 Python: Dockerfile + generation script + test

### Wave 3
- [x] T08: Kotlin post-processing: format + validate scripts + test
- [x] T09: Go post-processing: format + validate scripts + test
- [x] T10: Python post-processing: format + validate scripts + test

### Wave 4
- [x] T11: Docker Compose: full pipeline integration
- [x] T11a: Negative test: pipeline on invalid input

### Wave 5
- [x] T12: README, run-all.sh, volume swap test

---

## First Task Brief (T01)

**Goal**: Create the `demo/` directory skeleton with config files.

**Files to create**:

1. `demo/.env`:
```
SPECS_DIR=./specs
```

2. `demo/.gitignore`:
```
generated/
*.jar
.env.local
```

3. Empty directories (create with .gitkeep or will be populated by subsequent tasks):
```
demo/specs/proto/
demo/specs/openapi/
demo/templates/go-server/
demo/templates/python/
demo/config/
demo/scripts/
demo/dockerfiles/
```

**Commands to run**:
```bash
cd "d:/Proj/X5 Proj/AICreator"
mkdir -p demo/specs/proto demo/specs/openapi demo/templates/go-server demo/templates/python demo/config demo/scripts demo/dockerfiles
# Then create .env and .gitignore via Write tool
```

**Verification**:
```bash
ls -la demo/
cat demo/.env          # Should show SPECS_DIR=./specs
cat demo/.gitignore    # Should show generated/ and *.jar
ls demo/specs/proto    # Directory exists
ls demo/dockerfiles    # Directory exists
```

**Expected result**: `demo/` directory tree exists, `.env` and `.gitignore` are in place. Ready for T02/T03/T04 to populate specs and configs.
