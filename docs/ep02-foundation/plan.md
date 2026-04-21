# ep02-foundation — Implementation Plan

> **Epic**: ep02-foundation
> **Status**: Planning
> **Date**: 2026-04-14
> **Based on**: [research.md](research.md), CTO decisions (2026-04-14)

---

## Step 1: Project Definition

- **Project name**: AICreator Platform
- **One-line description**: Production-ready CLI + API platform for deterministic code generation from Proto/OpenAPI specifications, targeting Go as the first language.
- **MVP scope**:
  - FastAPI server with generation endpoints (POST generate with streaming ZIP, GET status)
  - CLI client (typer) — `aicreator generate`, `aicreator status`
  - Orchestrator with Strategy + Registry pattern routing to generators
  - Three generators: F1 (Proto → Go via buf), F2 (OpenAPI → Go server), F4 (OpenAPI → Go client)
  - Post-processing chain: gofmt → golangci-lint → go build
  - PostgreSQL for generation history with input_hash for determinism verification
  - Docker Compose deployment (api + postgres)
- **Out of scope (for now)**:
  - AI-generation (F3) — deferred to Phase 3
  - Web UI — CLI only for MVP
  - Kotlin, Python targets — Go only (multi-language by design)
  - SSO, Celery, Redis — no auxiliary services
  - AsyncAPI generators — OpenAPI and Proto only
  - Kubernetes deployment — Docker Compose sufficient for pilot

---

## Step 2: Constitution (Project Principles)

Existing 8 principles in CLAUDE.md evolved for the platform phase. Changes:

| # | Principle | Change | Rationale |
|---|-----------|--------|-----------|
| 2 | Docker-Isolated Execution → **Containerized Platform** | Evolved | Platform itself is a container, not just tools |
| 4 | Swap Without Change → **Specification Agnostic** | Evolved | Specs arrive via HTTP API, not volume mounts |
| 6 | Zero Runtime Dependencies → **Minimal Infrastructure** | Evolved | PostgreSQL added as the only external dependency |
| 7 | Minimal Customization → **Template-Driven Generation** | Evolved | Templates become first-class citizens |
| NEW | **Go First, Multi-Language by Design** | Added | Focus pilot on Go, architecture doesn't block others |

Principles 1 (Determinism First), 3 (Fail Fast, Fail Loud), 5 (Pinned Versions), 8 (OSS 700+ Stars Gate) remain unchanged.

Full updated constitution in Step 8.

---

## Step 3: Tech Stack (Final Decision)

| Layer | Technology | Version | Reasoning |
|-------|-----------|---------|-----------|
| Language | Python | 3.12 | AI SDK compatibility, FastAPI ecosystem, rapid development |
| API Framework | FastAPI | 0.115+ | Async-ready, auto-docs, Pydantic v2 native |
| CLI | typer | 0.15+ | Auto-help from type hints, Rich integration (16k+ ⭐) |
| ORM | SQLAlchemy | 2.0+ | Sync for MVP (thread pool), mature migrations via Alembic (10k+ ⭐) |
| Migrations | Alembic | 1.14+ | Autogenerate from models, standard for SQLAlchemy |
| Validation | Pydantic | 2.10+ | Native FastAPI integration, Settings management |
| HTTP Client | httpx | 0.28+ | Sync+async, used by CLI to call API (13k+ ⭐) |
| Console UI | Rich | 13+ | Progress bars, tables, colored output (50k+ ⭐) |
| Database | PostgreSQL | 16 | Production-ready from day one (CTO decision) |
| Package Manager | uv | latest | 10-100x faster than pip, deterministic lockfile, PEP 621 |
| Linter/Formatter | ruff | 0.8+ | All-in-one lint+format, Rust speed (35k+ ⭐) |
| Type Checker | mypy | 1.13+ | Mature, widely supported (19k+ ⭐) |
| Tests | pytest | 8+ | Standard, fixtures, plugins (12k+ ⭐) |
| Pre-commit | pre-commit | latest | Auto-run ruff, mypy before commit (13k+ ⭐) |

### Generation tools (inside Docker)

| Tool | Version | Source |
|------|---------|--------|
| Go | 1.23 | golang:1.23-alpine |
| buf | 1.50.0 | GitHub binary |
| protoc | 29.3 | GitHub binary |
| openapi-generator | 7.12.0 | Maven Central JAR |
| golangci-lint | 1.63.4 | GitHub binary |
| JRE | 17 | openjdk17-jre-headless |

All versions pinned from ep01-demo. Updates tracked as separate tickets.

### Step 3.1: Development Tooling (MCP Servers)

No additional MCP servers needed. GitHub and Context7 already configured globally. PostgreSQL managed via Docker Compose, not MCP.

---

## Step 4: Project Structure

```
src/aicreator/
├── __init__.py              # Package init, version
├── cli/                     # CLI layer (typer)
│   ├── __init__.py
│   ├── app.py               # typer.Typer() entry point
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── generate.py      # aicreator generate --function f1 --spec path
│   │   └── status.py        # aicreator status <generation_id>
│   └── output.py            # Rich formatting helpers
├── api/                     # API layer (FastAPI)
│   ├── __init__.py
│   ├── app.py               # FastAPI() entry point
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── generate.py      # POST /api/v1/generate
│   │   ├── generations.py   # GET /api/v1/generations/{id}
│   │   └── health.py        # GET /api/v1/health
│   ├── schemas.py           # Pydantic request/response models
│   ├── dependencies.py      # FastAPI Depends (db session, etc.)
│   └── middleware.py        # Request ID, logging
├── core/                    # Business logic (shared CLI <-> API)
│   ├── __init__.py
│   ├── orchestrator.py      # Registry + routing logic
│   ├── generator.py         # BaseGenerator ABC
│   ├── postprocessor.py     # PostProcessor chain
│   └── config.py            # pydantic-settings: Settings class
├── generators/              # Concrete generator implementations
│   ├── __init__.py
│   ├── buf.py               # F1: Proto -> Go (buf generate)
│   ├── openapi_server.py    # F2: OpenAPI -> Go server
│   └── openapi_client.py    # F4: OpenAPI -> Go client
├── db/                      # Database layer
│   ├── __init__.py
│   ├── engine.py            # create_engine, SessionLocal
│   ├── models.py            # SQLAlchemy ORM models
│   └── repository.py        # CRUD operations
└── templates/               # Generation templates (mustache overrides)
    └── go-server/
        └── partial_header.mustache

tests/
├── conftest.py              # Shared fixtures (db, client, tmp dirs)
├── unit/
│   ├── test_orchestrator.py
│   ├── test_postprocessor.py
│   └── test_schemas.py
├── integration/
│   ├── test_api_generate.py
│   └── test_generators.py
└── fixtures/
    ├── proto/               # Copied from demo/specs/proto/
    └── openapi/             # Copied from demo/specs/openapi/

alembic/
├── alembic.ini
├── env.py
└── versions/

docker/
├── Dockerfile               # Multi-stage: Python + Go toolchain + JRE + buf
├── Dockerfile.dev            # Development with hot reload (uvicorn --reload)
└── docker-compose.yml        # api + postgres services

pyproject.toml                # uv, dependencies, ruff, mypy config
```

### Directory purposes

| Directory | Purpose |
|-----------|---------|
| `src/aicreator/` | Main application package (src layout for proper packaging) |
| `src/aicreator/cli/` | CLI entry point and commands (typer) |
| `src/aicreator/api/` | FastAPI server, routes, schemas |
| `src/aicreator/core/` | Shared business logic: orchestrator, generators ABC, config |
| `src/aicreator/generators/` | Concrete generator implementations (subprocess wrappers) |
| `src/aicreator/db/` | SQLAlchemy models, engine, repository |
| `src/aicreator/templates/` | Mustache template overrides for openapi-generator |
| `tests/` | pytest tests (unit, integration, fixtures) |
| `alembic/` | Database migration scripts |
| `docker/` | Dockerfiles and compose configuration |

---

## Step 5: Data Model

### Entity: `Generation`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, default gen | Unique identifier |
| spec_type | VARCHAR(20) | NOT NULL | proto / openapi |
| language | VARCHAR(20) | NOT NULL | go (future: kotlin, python) |
| function | VARCHAR(10) | NOT NULL | f1 / f2 / f4 |
| status | VARCHAR(20) | NOT NULL, default PENDING | pending / running / completed / failed |
| input_hash | VARCHAR(64) | NOT NULL, indexed | SHA-256 of input files (determinism check) |
| created_at | TIMESTAMP | NOT NULL, default now | Creation time |
| completed_at | TIMESTAMP | nullable | Completion time |
| duration_ms | INTEGER | nullable | Generation duration |
| error | TEXT | nullable | Error message if failed |

**Indexes**: `input_hash` (duplicate detection), `created_at DESC` (recent list)

> **Decision**: Output files are NOT stored. ZIP is streamed directly to client during generation.
> Deterministic generation means re-running with the same input produces identical output — no need to persist results.
> `GenerationFile` entity removed — DB tracks only metadata for audit/history.

---

## Step 6: Implementation Phases

### Phase 1: Skeleton + DB (Wave 1) — T01-T04

Foundation: project structure, dependencies, database, health check.

- [ ] **T01** — Python project skeleton with uv: `pyproject.toml`, src layout, dev dependencies (ruff, mypy, pytest)
- [ ] **T02** — FastAPI app skeleton: `app.py`, health endpoint (`GET /api/v1/health`), request ID middleware
- [ ] **T03** — Database setup: SQLAlchemy models (`Generation`), engine, session management
- [ ] **T04** — Alembic migrations + Docker Compose (api + postgres): initial migration, `docker-compose.yml`, `Dockerfile.dev`

**Deliverable**: `docker compose -f docker/docker-compose.yml --profile dev up` starts API + PostgreSQL, `GET /api/v1/health` returns `{"status": "ok"}`, database tables created.

### Phase 2: Core Logic (Wave 2) — T05-T08

Business logic: orchestrator, generators, post-processing.

- [ ] **T05** — Core abstractions: `BaseGenerator` ABC, `GeneratorConfig` dataclass, `GenerationResult` model
- [ ] **T06** — Orchestrator with Registry pattern: route `(spec_type, language, function)` → generator, `UnsupportedCombinationError`
- [ ] **T07** — Generators: `BufGoGenerator` (F1), `OpenAPIServerGenerator` (F2), `OpenAPIClientGenerator` (F4) — subprocess wrappers ported from demo scripts
- [ ] **T08** — PostProcessor chain: `gofmt` → `golangci-lint` → `go build`, fatal vs warning severity, fail-fast

**Deliverable**: Orchestrator can route requests and invoke generators via subprocess. Post-processor validates output. Unit tests pass.

### Phase 3: API Endpoints (Wave 3) — T09-T11

HTTP layer: file upload, generation status, schemas.

- [ ] **T09** — `POST /api/v1/generate`: multipart file upload, metadata parsing, DB record creation, orchestrator invocation, streaming ZIP response
- [ ] **T10** — `GET /api/v1/generations/{id}`: generation metadata (status, input_hash, timing, error)
- [ ] **T11** — Pydantic schemas: request validation, response models, error responses with structured error format

**Deliverable**: Full API functional — upload spec → get ZIP streamed back, check metadata of past generations.

### Phase 4: CLI + Integration (Wave 4) — T12-T15

CLI client, end-to-end integration, production Docker image.

- [ ] **T12** — CLI skeleton: typer app, `generate` command (--function, --spec, --output, --language), httpx calls to API
- [ ] **T13** — CLI `status` command: query generation by ID, Rich-formatted output (table, progress)
- [ ] **T14** — Multi-stage production Dockerfile: Go toolchain + JRE + buf + Python app in one image
- [ ] **T15** — E2E tests: CLI → API → Generator → files on disk. Happy path + error cases (invalid spec, unsupported combination)

**Deliverable**: `aicreator generate --function f1 --spec order.proto --output ./out` produces Go code. `aicreator status <id>` shows generation result. `docker compose -f docker/docker-compose.yml --profile dev up` runs the full platform.

---

## Step 7: API / Interface Design

### API Endpoints

| Method | Path | Purpose | Request | Response |
|--------|------|---------|---------|----------|
| POST | `/api/v1/generate` | Generate code from spec | multipart: `files[]` + `metadata` (JSON form field) | 200: StreamingResponse (ZIP) |
| GET | `/api/v1/generations/{id}` | Get generation metadata | — | 200: GenerationResponse (JSON) |
| GET | `/api/v1/health` | Health check | — | 200: `{"status": "ok", "version": "..."}` |

> **Decision**: No `/download` endpoint. ZIP is streamed directly in POST response.
> Re-generation is deterministic — same input always produces same output.

### Request/Response Schemas

```python
# POST /api/v1/generate — metadata form field
class GenerateRequest(BaseModel):
    function: Literal["f1", "f2", "f4"]
    language: Literal["go"] = "go"
    spec_type: Literal["proto", "openapi"]

# GET /api/v1/generations/{id} — metadata only, no file list
class GenerationResponse(BaseModel):
    id: UUID
    function: str
    language: str
    spec_type: str
    status: Literal["pending", "running", "completed", "failed"]
    input_hash: str
    created_at: datetime
    completed_at: datetime | None
    duration_ms: int | None
    error: str | None

# Error response (all 4xx/5xx)
class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
```

### CLI Commands

```bash
# Generate code
aicreator generate --function f1 --spec ./specs/proto/ --output ./out --language go

# Check generation status
aicreator status <generation-id>

# Health check
aicreator health
```

---

## Step 8: CLAUDE.md Updates

### Constitution changes

9 principles (8 existing evolved + 1 new). See Step 2 for change summary.

### Epics table

Add `ep02-foundation` row with 🔄 Active status.

### New sections

- Commands section updated with platform commands (`uv run`, `docker compose`, `aicreator` CLI)
- Project structure updated to reflect src layout

---

## Step 9: Closed Decisions

All open questions resolved (2026-04-14):

| # | Вопрос | Решение | Обоснование |
|---|--------|---------|-------------|
| 1 | **Хранение output** | Streaming only | ZIP стримится клиенту напрямую, в DB только метаданные. Детерминизм гарантирует: тот же input → тот же output. Нет нужды хранить результат. |
| 2 | **Аутентификация** | Без auth на MVP | Внутренняя сеть, 1 команда-пользователь, Docker на сервере без внешнего доступа. Auth отложен до ep04-security. |
| 3 | **Конкурентность** | uvicorn --workers 2 | Sync subprocess, 2 воркера = макс 2 параллельных генерации. Без semaphore, без очереди. Достаточно для пилота. |
| 4 | **Тестовые fixtures** | Копия в tests/fixtures/ | Независимые fixtures, без symlinks. Копируем proto/ и openapi/ из demo/specs/. Тесты не зависят от demo/. |
