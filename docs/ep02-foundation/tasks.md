# ep02-foundation — Task List

> **Epic**: ep02-foundation
> **Plan**: [plan.md](plan.md)
> **Date**: 2026-04-14
> **Total tasks**: 15 (4 waves)

---

## Dependency Graph

```
── Wave 1 (no dependencies) ──────────────────────────
   T01: Python project skeleton (uv + pyproject.toml)

── Wave 2 (after T01) ────────────────────────────────
   T02: FastAPI app + health endpoint        ← T01
   T03: SQLAlchemy models + DB engine        ← T01
   T04: Test fixtures (proto + openapi)      ← T01
   T05: Core abstractions (BaseGenerator)    ← T01

── Wave 3 (after Wave 2) ─────────────────────────────
   T06: Orchestrator + Registry              ← T05
   T07: BufGoGenerator (F1)                  ← T05, T04
   T08: OpenAPI generators (F2 + F4)         ← T05, T04
   T09: PostProcessor chain                  ← T05
   T10: Alembic + Docker Compose             ← T02, T03

── Wave 4 (after Wave 3) ─────────────────────────────
   T11: POST /api/v1/generate                ← T06, T07, T08, T09, T10
   T12: GET /api/v1/generations/{id}         ← T10
   T13: CLI generate + status                ← T11, T12
   T14: Multi-stage production Dockerfile    ← T10
   T15: E2E tests                            ← T13, T14
```

---

## Critical Path

```
T01 → T05 → T06 → T11 → T13 → T15
      T05 → T07 ↗
      T05 → T09 ↗
T01 → T02 → T10 → T11
T01 → T03 → T10 ↗
```

**Longest chain**: T01 → T05 → T06+T07+T09 → T11 → T13 → T15 (6 steps)

---

## Task Details

### [T01] Python project skeleton with uv
- **Phase**: 1 — Skeleton + DB
- **Type**: setup
- **Depends on**: none
- **Priority**: 🔴 Critical path
- **Input**: empty project (only `demo/`, `docs/`, `CLAUDE.md` exist)
- **Output**:
  - `pyproject.toml` — PEP 621, uv config, ruff/mypy/pytest sections
  - `src/aicreator/__init__.py` — package with `__version__`
  - `src/aicreator/core/__init__.py`, `api/__init__.py`, `cli/__init__.py`, `generators/__init__.py`, `db/__init__.py`
  - `tests/__init__.py`, `tests/conftest.py`
  - `uv.lock` — generated lockfile
  - `.python-version` — 3.12
  - `.gitignore` — updated with Python patterns
  - `.pre-commit-config.yaml` — ruff + mypy hooks
- **Acceptance criteria**:
  - [ ] `uv sync` installs all dependencies without errors
  - [ ] `uv run ruff check src/` passes with no warnings
  - [ ] `uv run mypy src/` passes with no errors
  - [ ] `uv run pytest` runs (0 tests collected, no errors)
  - [ ] Package structure follows src layout (`src/aicreator/`)
  - [ ] `.gitignore` contains Python patterns (`.venv/`, `__pycache__/`, `*.egg-info/`, `.mypy_cache/`, `.ruff_cache/`, `.env`, `dist/`)
  - [ ] `uv run pre-commit install` succeeds, hooks configured
- **Tests required**: none (setup task — pytest scaffold only)
- **Constitution check**: P5 (Pinned Versions) — all dependency versions pinned in pyproject.toml; P8 (OSS 700+ Stars) — all deps verified
- **Implementation notes**:
  - Dependencies: `fastapi>=0.115`, `uvicorn[standard]`, `sqlalchemy>=2.0`, `alembic>=1.14`, `typer>=0.15`, `httpx>=0.28`, `rich>=13`, `pydantic-settings>=2.7`, `psycopg2-binary` (or `psycopg[binary]`)
  - Dev deps: `pytest>=8`, `ruff>=0.8`, `mypy>=1.13`, `pytest-cov`, `httpx` (for TestClient), `pre-commit`
  - `pyproject.toml` sections: `[tool.ruff]` (target-version = "py312", line-length = 120), `[tool.mypy]` (strict = true), `[tool.pytest.ini_options]`
  - Update existing `.gitignore` — append Python patterns to existing demo patterns (do NOT overwrite)
  - `.pre-commit-config.yaml`: ruff (lint + format), mypy hooks
  - Use `uv init --lib` or manual creation

---

### [T02] FastAPI app skeleton + health endpoint + logging
- **Phase**: 1 — Skeleton + DB
- **Type**: api
- **Depends on**: T01
- **Priority**: 🔴 Critical path
- **Input**: project skeleton from T01
- **Output**:
  - `src/aicreator/api/app.py` — FastAPI app factory
  - `src/aicreator/api/routes/health.py` — `GET /api/v1/health`
  - `src/aicreator/api/routes/__init__.py`
  - `src/aicreator/api/middleware.py` — request ID middleware (X-Request-ID header + log context)
  - `src/aicreator/core/config.py` — pydantic-settings `Settings` class
  - `src/aicreator/core/logging.py` — structured logging configuration
  - `tests/unit/test_health.py`
- **Acceptance criteria**:
  - [ ] `uv run uvicorn aicreator.api.app:app` starts without errors
  - [ ] `GET /api/v1/health` returns `{"status": "ok", "version": "0.1.0"}`
  - [ ] Every response includes `X-Request-ID` header (UUID)
  - [ ] `GET /docs` shows OpenAPI documentation (auto-generated)
  - [ ] Settings loaded from env vars with `AICREATOR_` prefix
  - [ ] Structured logging configured: JSON format in production (`LOG_FORMAT=json`), human-readable in dev (default)
  - [ ] Request ID injected into log context — every log line within a request includes `request_id`
  - [ ] `LOG_LEVEL` setting controls logging verbosity
  - [ ] Unit tests pass
- **Tests required**:
  - [ ] `test_health_returns_ok` — status 200, correct JSON shape
  - [ ] `test_request_id_header` — response has X-Request-ID
  - [ ] `test_openapi_schema_accessible` — `/openapi.json` returns valid schema
  - [ ] `test_logging_includes_request_id` — verify request_id appears in log output during request
- **Constitution check**: P3 (Fail Fast) — app fails to start on invalid config
- **Implementation notes**:
  - Use `FastAPI(title="AICreator", version=__version__)` with router prefix `/api/v1`
  - `Settings` via `pydantic_settings.BaseSettings` with `model_config = SettingsConfigDict(env_prefix="AICREATOR_")`
  - Fields: `database_url: str`, `log_level: str = "INFO"`, `log_format: str = "text"`, `api_host: str = "0.0.0.0"`, `api_port: int = 8000`
  - Logging setup in `core/logging.py`: `logging.config.dictConfig()` with two formatters — JSON (`{"timestamp", "level", "message", "request_id"}`) and text (`%(asctime)s %(levelname)s [%(request_id)s] %(message)s`)
  - Request ID context: use `contextvars.ContextVar` set in middleware, read by log filter
  - TestClient from `fastapi.testclient`

---

### [T03] SQLAlchemy models + DB engine
- **Phase**: 1 — Skeleton + DB
- **Type**: data
- **Depends on**: T01
- **Priority**: 🔴 Critical path
- **Input**: project skeleton, Settings class from T02 (can stub if T02 not done yet)
- **Output**:
  - `src/aicreator/db/engine.py` — `create_engine`, `SessionLocal`, `get_db` dependency
  - `src/aicreator/db/models.py` — `Generation` ORM model
  - `src/aicreator/db/repository.py` — `create_generation`, `get_generation`, `update_generation_status`
  - `tests/unit/test_models.py`
- **Acceptance criteria**:
  - [ ] `Generation` model matches plan schema (id, spec_type, language, function, status, input_hash, created_at, completed_at, duration_ms, error)
  - [ ] `id` is UUID with server-side default
  - [ ] `created_at` has server-side default `now()`
  - [ ] `input_hash` has index
  - [ ] `created_at` has DESC index
  - [ ] Repository functions work with in-memory SQLite for tests
  - [ ] Unit tests pass
- **Tests required**:
  - [ ] `test_create_generation` — creates record, returns UUID
  - [ ] `test_get_generation_not_found` — returns None for unknown ID
  - [ ] `test_update_status` — transitions pending → running → completed
  - [ ] `test_input_hash_indexed` — verify index exists on model metadata
- **Constitution check**: P1 (Determinism) — input_hash stored for determinism audit; P6 (Minimal Infrastructure) — PostgreSQL only
- **Implementation notes**:
  - Use `mapped_column` style (SQLAlchemy 2.0 declarative)
  - `Base = DeclarativeBase()` in models.py
  - For tests: `create_engine("sqlite:///:memory:")` — no PostgreSQL needed for unit tests
  - UUID: `sqlalchemy.Uuid` type, `default=uuid4`
  - Status as string enum (not SQL ENUM — simpler migrations)

---

### [T04] Test fixtures (proto + openapi specs)
- **Phase**: 1 — Skeleton + DB
- **Type**: test
- **Depends on**: T01
- **Priority**: 🟡 Important
- **Input**: demo specs at `demo/specs/proto/`, `demo/specs/openapi/`, `demo/specs-invalid/`
- **Output**:
  - `tests/fixtures/proto/` — `buf.yaml`, `buf.gen.go.yaml`, `common.proto`, `order.proto`, `shipment.proto`, `warehouse.proto`
  - `tests/fixtures/openapi/logistics.yaml`
  - `tests/fixtures/invalid/proto/broken.proto`
  - `tests/fixtures/invalid/openapi/no-paths.yaml`
- **Acceptance criteria**:
  - [ ] Proto specs copied from `demo/specs/proto/` (4 files + buf.yaml)
  - [ ] New `buf.gen.go.yaml` created for Go output (protoc-gen-go, not Kotlin)
  - [ ] OpenAPI spec copied from `demo/specs/openapi/logistics.yaml`
  - [ ] Invalid fixtures copied from `demo/specs-invalid/`
  - [ ] `conftest.py` has fixture functions: `proto_specs_dir`, `openapi_spec_path`, `invalid_proto_dir`, `invalid_openapi_path`
- **Tests required**: none (these ARE test fixtures)
- **Constitution check**: P1 (Determinism) — same specs = same test results
- **Implementation notes**:
  - Demo `buf.gen.yaml` generates Kotlin (`protoc_builtin: java` + `protoc_builtin: kotlin`). For ep02 we need Go: create `buf.gen.go.yaml` with `plugin: go` and `plugin: go-grpc` (NOT `protoc_builtin` — Go plugins are separate binaries, not built into protoc)
  - `buf.gen.go.yaml` content:
    ```yaml
    version: v2
    plugins:
      - plugin: go
        out: /generated/go
        opt: paths=source_relative
      - plugin: go-grpc
        out: /generated/go
        opt: paths=source_relative
    ```
  - Docker image must have `protoc-gen-go` and `protoc-gen-go-grpc` binaries in PATH
  - conftest fixtures should use `pathlib.Path(__file__).parent / "fixtures"` for reliable paths

---

### [T05] Core abstractions: BaseGenerator, GeneratorConfig, GenerationResult
- **Phase**: 2 — Core Logic
- **Type**: feature
- **Depends on**: T01
- **Priority**: 🔴 Critical path
- **Input**: project skeleton
- **Output**:
  - `src/aicreator/core/generator.py` — `BaseGenerator` ABC, `GeneratorConfig`, `GenerationResult`, `ValidationResult`
  - `tests/unit/test_generator.py`
- **Acceptance criteria**:
  - [ ] `BaseGenerator` is ABC with `validate(spec_path) -> ValidationResult` and `generate(spec_path, output_dir, config) -> GenerationResult`
  - [ ] `GeneratorConfig` is a dataclass/Pydantic model with fields for tool paths, template dirs, additional properties
  - [ ] `GenerationResult` contains: `output_dir`, `files_generated` (count), `duration_ms`, `success` (bool), `error` (optional)
  - [ ] `ValidationResult` contains: `valid` (bool), `errors` (list of strings)
  - [ ] A concrete `StubGenerator` exists in tests for testing orchestrator/API without real subprocess
  - [ ] Unit tests pass
- **Tests required**:
  - [ ] `test_base_generator_is_abstract` — cannot instantiate directly
  - [ ] `test_stub_generator_implements_interface` — StubGenerator passes validation + generates
  - [ ] `test_generation_result_fields` — all fields accessible
- **Constitution check**: P9 (Go First, Multi-Language by Design) — BaseGenerator is language-agnostic
- **Implementation notes**:
  - ABC from `abc` module, `@abstractmethod` for `validate` and `generate`
  - `GenerationResult` as Pydantic `BaseModel` (not dataclass) — for JSON serialization in API
  - StubGenerator in `tests/conftest.py` or `tests/helpers/` — returns canned files from fixtures

---

### [T06] Orchestrator with Registry pattern
- **Phase**: 2 — Core Logic
- **Type**: feature
- **Depends on**: T05
- **Priority**: 🔴 Critical path
- **Input**: BaseGenerator ABC
- **Output**:
  - `src/aicreator/core/orchestrator.py` — `Orchestrator` class with `@register` decorator and `run()` method
  - `tests/unit/test_orchestrator.py`
- **Acceptance criteria**:
  - [ ] `@Orchestrator.register(spec_type, language, function)` decorator registers generator class
  - [ ] `orchestrator.run(spec_type, language, function, spec_path, output_dir)` routes to correct generator
  - [ ] `UnsupportedCombinationError` raised for unregistered (spec_type, language, function) tuples
  - [ ] Registry is a class-level dict `dict[tuple[str, str, str], type[BaseGenerator]]`
  - [ ] `run()` calls `generator.validate()` then `generator.generate()` then `postprocessor.run()`
  - [ ] Unit tests pass (using StubGenerator from T05)
- **Tests required**:
  - [ ] `test_register_and_route` — register StubGenerator, verify routing
  - [ ] `test_unsupported_combination_raises` — unknown (spec, lang, fn) raises UnsupportedCombinationError
  - [ ] `test_validation_failure_stops_generation` — if validate returns invalid, generate is not called
  - [ ] `test_multiple_registrations` — register 3 generators, each routes correctly
- **Constitution check**: P4 (Specification Agnostic) — registry pattern allows adding generators without core changes
- **Implementation notes**:
  - See research.md §6 for code sketch
  - PostProcessor is injected via constructor (dependency injection), not hardcoded
  - For unit tests, mock PostProcessor with pass-through

---

### [T07] BufGoGenerator (F1: Proto → Go)
- **Phase**: 2 — Core Logic
- **Type**: feature
- **Depends on**: T05, T04
- **Priority**: 🔴 Critical path
- **Input**: BaseGenerator ABC, test fixtures (proto specs)
- **Output**:
  - `src/aicreator/generators/buf.py` — `BufGoGenerator` registered as `("proto", "go", "f1")`
  - `tests/unit/test_buf_generator.py`
- **Acceptance criteria**:
  - [ ] `BufGoGenerator` extends `BaseGenerator`
  - [ ] Registered via `@Orchestrator.register("proto", "go", "f1")`
  - [ ] `validate()` checks: spec_path exists, contains `.proto` files, `buf.yaml` present
  - [ ] `generate()` runs `subprocess.run(["buf", "generate", ...])` with correct args
  - [ ] Subprocess timeout configurable (default 120s)
  - [ ] `generate()` returns `GenerationResult` with file count from output dir
  - [ ] On subprocess failure: captures stderr, returns result with `success=False`
  - [ ] Unit tests pass (subprocess mocked)
- **Tests required**:
  - [ ] `test_validate_valid_proto_dir` — returns valid for fixture dir
  - [ ] `test_validate_missing_buf_yaml` — returns invalid
  - [ ] `test_validate_empty_dir` — returns invalid (no .proto files)
  - [ ] `test_generate_calls_subprocess` — mock subprocess.run, verify args
  - [ ] `test_generate_failure_captures_stderr` — mock returncode=1, verify error in result
- **Constitution check**: P1 (Determinism) — same proto input → same Go output; P3 (Fail Fast) — subprocess failure immediately surfaces
- **Implementation notes**:
  - Port logic from `demo/scripts/generate-f1-kotlin.sh` but for Go
  - Demo uses `buf generate` from `${SPECS_DIR}/proto` dir — same pattern
  - Need `buf.gen.go.yaml` with `plugin: go` + `plugin: go-grpc` (NOT `protoc_builtin` — Go protobuf plugins are separate binaries). See T04 for exact YAML.
  - `subprocess.run(["buf", "generate", "--template", buf_gen_path], cwd=spec_path, capture_output=True, timeout=config.timeout)`
  - Docker image must have `protoc-gen-go` and `protoc-gen-go-grpc` in PATH (installed via `go install` in T14)

---

### [T08] OpenAPI generators (F2: Go server + F4: Go client)
- **Phase**: 2 — Core Logic
- **Type**: feature
- **Depends on**: T05, T04
- **Priority**: 🔴 Critical path
- **Input**: BaseGenerator ABC, test fixtures (openapi spec)
- **Output**:
  - `src/aicreator/generators/openapi_server.py` — `OpenAPIServerGenerator` registered as `("openapi", "go", "f2")`
  - `src/aicreator/generators/openapi_client.py` — `OpenAPIClientGenerator` registered as `("openapi", "go", "f4")`
  - `src/aicreator/templates/go-server/partial_header.mustache` — copied from demo
  - `tests/unit/test_openapi_generators.py`
- **Acceptance criteria**:
  - [ ] Both generators extend `BaseGenerator`
  - [ ] Registered with correct `(spec_type, language, function)` tuples
  - [ ] `validate()` checks: file exists, `.yaml`/`.yml` extension, valid YAML with `openapi` key
  - [ ] `generate()` runs `java -jar openapi-generator-cli.jar generate` with correct args
  - [ ] F2 uses generator name `go-server`, F4 uses `go` (client)
  - [ ] Config file path and template dir configurable via `GeneratorConfig`
  - [ ] On subprocess failure: captures stderr, returns result with `success=False`
  - [ ] Unit tests pass (subprocess mocked)
- **Tests required**:
  - [ ] `test_validate_valid_openapi_spec` — returns valid
  - [ ] `test_validate_not_yaml` — returns invalid
  - [ ] `test_validate_missing_openapi_key` — returns invalid (valid YAML but not OpenAPI)
  - [ ] `test_server_generate_calls_subprocess` — verify `go-server` generator name in args
  - [ ] `test_client_generate_calls_subprocess` — verify `go` generator name in args
  - [ ] `test_generate_includes_template_dir` — F2 passes `--template-dir` for mustache overrides
- **Constitution check**: P5 (Pinned Versions) — openapi-generator 7.12.0 pinned; P7 (Template-Driven) — mustache templates for corporate header
- **Implementation notes**:
  - Port from `demo/scripts/generate-f2-go.sh` and `demo/config/go-server.yaml`
  - F2 command: `java -jar /opt/openapi-generator/openapi-generator-cli.jar generate -i {spec} -g go-server -c {config} -t {templates} -o {output} --additional-properties=router=mux`
  - F4 command: similar but `-g go` (client generator), no template override needed for MVP
  - Mustache template `partial_header.mustache` from `demo/templates/go-server/`

---

### [T09] PostProcessor chain
- **Phase**: 2 — Core Logic
- **Type**: feature
- **Depends on**: T05
- **Priority**: 🔴 Critical path
- **Input**: BaseGenerator abstractions (GenerationResult)
- **Output**:
  - `src/aicreator/core/postprocessor.py` — `PostProcessor`, `PostProcessStep`, `StepResult`
  - `tests/unit/test_postprocessor.py`
- **Acceptance criteria**:
  - [ ] `PostProcessor` accepts a list of `PostProcessStep` and executes them in order
  - [ ] Each step has `severity`: `fatal` (stops chain) or `warning` (log and continue)
  - [ ] `PostProcessStep` is ABC with `execute(output_dir: Path) -> StepResult`
  - [ ] Go chain defined with 4 steps: `GoModInitStep` (fatal) → `GofmtStep` (fatal) → `GolangciLintStep` (warning) → `GoBuildStep` (fatal)
  - [ ] `GoModInitStep` runs `go mod init` + `go mod tidy` + `go mod download` — initializes Go module before other steps
  - [ ] Each step wraps `subprocess.run` with timeout
  - [ ] Fatal step failure raises `PostProcessError` with step name + stderr
  - [ ] Warning step failure logs but continues chain
  - [ ] Unit tests pass (subprocess mocked)
- **Tests required**:
  - [ ] `test_all_steps_pass` — chain completes, returns success
  - [ ] `test_fatal_step_stops_chain` — second step fails (fatal), third step not called
  - [ ] `test_warning_step_continues` — lint step fails (warning), build step still runs
  - [ ] `test_empty_chain` — no steps, returns success immediately
  - [ ] `test_step_timeout` — subprocess.TimeoutExpired handled gracefully
  - [ ] `test_go_mod_init_runs_first` — GoModInitStep is first in Go chain, called before gofmt
- **Constitution check**: P3 (Fail Fast, Fail Loud) — fatal steps stop immediately with clear error
- **Implementation notes**:
  - See research.md §6 for code sketch
  - Go chain (4 steps, order matters):
    1. `GoModInitStep` (fatal): `go mod init {module_name}` (if no go.mod) → `go mod tidy` → `go mod download`. Module name configurable via GeneratorConfig (default: "generated"). This step is critical — golangci-lint and go build require a valid module with dependencies downloaded.
    2. `GofmtStep` (fatal): `gofmt -w {output_dir}`
    3. `GolangciLintStep` (warning): `golangci-lint run --fix --disable-all --enable=gofmt,govet ./...` (best-effort, `|| true` in demo)
    4. `GoBuildStep` (fatal): `go build ./...`
  - From demo: `format-go.sh` does `go mod init` + `go mod tidy` + `go mod download` before golangci-lint. Separating into GoModInitStep makes it explicit and testable.
  - PostProcessor is stateless — receives output_dir, runs steps, returns aggregate result

---

### [T10] Alembic migrations + Docker Compose
- **Phase**: 1 — Skeleton + DB (infrastructure)
- **Type**: deploy
- **Depends on**: T02, T03
- **Priority**: 🔴 Critical path
- **Input**: FastAPI app, SQLAlchemy models, Settings
- **Output**:
  - `alembic.ini` — Alembic config
  - `alembic/env.py` — migration environment with model imports
  - `alembic/versions/001_initial.py` — initial migration (generations table)
  - `docker/Dockerfile.dev` — Python 3.12-slim, uv install, uvicorn with --reload
  - `docker/docker-compose.yml` — api + postgres services
  - `.env.example` — template for required env vars
- **Acceptance criteria**:
  - [ ] `docker compose up` starts API and PostgreSQL
  - [ ] PostgreSQL is accessible on port 5432 (default)
  - [ ] API is accessible on port 8000
  - [ ] `GET http://localhost:8000/api/v1/health` returns 200
  - [ ] Alembic migration creates `generations` table with correct schema
  - [ ] `docker compose up` runs migrations automatically on startup (entrypoint script)
  - [ ] `docker compose down -v` cleanly removes containers and volumes
  - [ ] `.env.example` documents all required variables
- **Tests required**: none (infrastructure — verified via docker compose up)
- **Constitution check**: P2 (Containerized Platform) — everything in containers; P5 (Pinned Versions) — image tags pinned; P6 (Minimal Infrastructure) — only PostgreSQL
- **Implementation notes**:
  - Dockerfile.dev: `FROM python:3.12-slim`, install uv, `uv sync`, `CMD uvicorn aicreator.api.app:app --host 0.0.0.0 --reload`
  - docker-compose.yml: `postgres:16-alpine` with volume, api service with `depends_on` postgres healthy
  - Entrypoint script: `alembic upgrade head && uvicorn ...`
  - DATABASE_URL: `postgresql://aicreator:aicreator@postgres:5432/aicreator`
  - Healthcheck for postgres: `pg_isready`

---

### [T11] POST /api/v1/generate endpoint
- **Phase**: 3 — API Endpoints
- **Type**: api
- **Depends on**: T06, T07, T08, T09, T10
- **Priority**: 🔴 Critical path
- **Input**: Orchestrator, all generators, PostProcessor, DB, Docker Compose running
- **Output**:
  - `src/aicreator/api/routes/generate.py` — POST endpoint
  - `src/aicreator/api/schemas.py` — `GenerateRequest`, `ErrorResponse`
  - `src/aicreator/api/dependencies.py` — `get_db`, `get_orchestrator`
  - `tests/integration/test_api_generate.py`
- **Acceptance criteria**:
  - [ ] `POST /api/v1/generate` accepts multipart: `files[]` (UploadFile) + `metadata` (Form, JSON string)
  - [ ] Metadata validated as `GenerateRequest` (function, language, spec_type)
  - [ ] Files saved to temp dir, input_hash computed (SHA-256 of sorted file contents)
  - [ ] Generation record created in DB (status=pending → running → completed/failed)
  - [ ] Orchestrator invoked: validate → generate → postprocess
  - [ ] On success: response is `StreamingResponse` with `application/zip` content type
  - [ ] On failure: response is 422 (validation) or 500 (generation) with `ErrorResponse` JSON
  - [ ] Temp dir cleaned up after response (success or failure)
  - [ ] Integration tests pass (using StubGenerator — no real subprocess)
- **Tests required**:
  - [ ] `test_generate_valid_request` — multipart upload, expect 200 + ZIP content-type
  - [ ] `test_generate_invalid_metadata` — missing function field, expect 422
  - [ ] `test_generate_no_files` — no files uploaded, expect 422
  - [ ] `test_generate_unsupported_combination` — invalid (spec_type, language, function), expect 400
  - [ ] `test_generate_creates_db_record` — check DB has new generation record after request
  - [ ] `test_generate_failure_returns_error` — StubGenerator raises, expect 500 + ErrorResponse
- **Constitution check**: P1 (Determinism) — input_hash computed and stored; P3 (Fail Fast) — generation errors return immediately
- **Implementation notes**:
  - Use `tempfile.mkdtemp()` for spec files and output — cleanup in `finally` block
  - Input hash: `hashlib.sha256()` over sorted filenames + contents
  - ZIP creation: `zipfile.ZipFile` over output_dir files, stream via `StreamingResponse`
  - For integration tests: override `get_orchestrator` dependency to inject StubGenerator-based orchestrator

---

### [T12] GET /api/v1/generations/{id} endpoint
- **Phase**: 3 — API Endpoints
- **Type**: api
- **Depends on**: T10
- **Priority**: 🟡 Important
- **Input**: DB models, repository
- **Output**:
  - `src/aicreator/api/routes/generations.py` — GET endpoint
  - `src/aicreator/api/schemas.py` — `GenerationResponse` (add to existing)
  - `tests/unit/test_generations_endpoint.py`
- **Acceptance criteria**:
  - [ ] `GET /api/v1/generations/{id}` returns generation metadata as JSON
  - [ ] Response matches `GenerationResponse` schema (id, function, language, spec_type, status, input_hash, created_at, completed_at, duration_ms, error)
  - [ ] 404 with `ErrorResponse` for unknown generation ID
  - [ ] Invalid UUID format returns 422
  - [ ] Tests pass
- **Tests required**:
  - [ ] `test_get_existing_generation` — create in DB, fetch via API, verify all fields
  - [ ] `test_get_nonexistent_generation` — random UUID, expect 404
  - [ ] `test_get_invalid_uuid` — "not-a-uuid", expect 422
- **Constitution check**: none specific
- **Implementation notes**:
  - Simple CRUD read — `repository.get_generation(id)`, convert to Pydantic, return
  - Reuse `get_db` dependency from T11

---

### [T13] CLI: generate + status commands
- **Phase**: 4 — CLI + Integration
- **Type**: feature
- **Depends on**: T11, T12
- **Priority**: 🔴 Critical path
- **Input**: running API with generate and generations endpoints
- **Output**:
  - `src/aicreator/cli/app.py` — typer.Typer() with generate, status, health commands
  - `src/aicreator/cli/commands/generate.py` — `aicreator generate` command
  - `src/aicreator/cli/commands/status.py` — `aicreator status` command
  - `src/aicreator/cli/output.py` — Rich formatting helpers
  - `tests/unit/test_cli.py`
- **Acceptance criteria**:
  - [ ] `aicreator generate --function f1 --spec ./specs/proto/ --output ./out` sends multipart POST to API, saves ZIP to --output
  - [ ] `aicreator generate --function f2 --spec ./specs/openapi/logistics.yaml --output ./out` works for OpenAPI
  - [ ] `aicreator status <uuid>` sends GET to API, displays Rich-formatted table
  - [ ] `aicreator health` sends GET to health endpoint, displays status
  - [ ] `--api-url` option (default: `http://localhost:8000`) configurable
  - [ ] Rich progress spinner during generation
  - [ ] Error output: clear message + exit code 1 on failure
  - [ ] `--help` auto-generated for all commands
  - [ ] Unit tests pass (httpx mocked)
- **Tests required**:
  - [ ] `test_generate_sends_correct_request` — mock httpx, verify multipart body
  - [ ] `test_generate_saves_zip_to_output` — mock response with ZIP, verify files written
  - [ ] `test_generate_api_error` — mock 500 response, verify error message + exit code
  - [ ] `test_status_displays_metadata` — mock response, verify Rich table output
  - [ ] `test_health_ok` — mock 200, verify output
- **Constitution check**: P3 (Fail Fast) — CLI exits with code 1 on any API error
- **Implementation notes**:
  - typer entry point in `pyproject.toml`: `[project.scripts] aicreator = "aicreator.cli.app:app"`
  - `generate` collects files from --spec path (glob `*.proto` or single YAML), builds multipart request
  - httpx for HTTP calls: `httpx.Client(base_url=api_url)`
  - ZIP response: stream to temp file, extract to --output dir
  - Rich: `Console()`, `Table()`, `Progress()` for output formatting
  - Mock httpx via `pytest` fixtures + `unittest.mock.patch`

---

### [T14] Multi-stage production Dockerfile
- **Phase**: 4 — CLI + Integration
- **Type**: deploy
- **Depends on**: T10
- **Priority**: 🟡 Important
- **Input**: working Docker Compose dev setup, generator subprocess commands
- **Output**:
  - `docker/Dockerfile` — multi-stage production image
  - Updated `docker/docker-compose.yml` — production profile using Dockerfile
- **Acceptance criteria**:
  - [ ] Multi-stage build: Go tools stage, buf stage, runtime stage
  - [ ] Runtime image contains: Python 3.12, Go 1.23, buf 1.50.0, protoc 29.3, openapi-generator 7.12.0, JRE 17, golangci-lint 1.63.4, protoc-gen-go, protoc-gen-go-grpc
  - [ ] `docker build -f docker/Dockerfile .` succeeds
  - [ ] Image size < 3GB (target ~1.5-2GB)
  - [ ] All tool versions match pinned versions from plan
  - [ ] `docker compose --profile prod up` starts production API
  - [ ] Health endpoint accessible from production container
- **Tests required**: none (infrastructure — verified by docker build + health check)
- **Constitution check**: P2 (Containerized Platform); P5 (Pinned Versions) — all tool versions explicit
- **Implementation notes**:
  - See research.md §4 for multi-stage Dockerfile sketch
  - Stage 1: `golang:1.23-alpine` — install protoc-gen-go, protoc-gen-go-grpc, golangci-lint
  - Stage 2: `alpine` — download buf, protoc binaries
  - Stage 3: `python:3.12-slim` — COPY from stage 1+2, install JRE, openapi-generator JAR, install Python app via uv
  - Entrypoint: `alembic upgrade head && uvicorn aicreator.api.app:app --host 0.0.0.0 --workers 2`
  - protoc-gen-go: `go install google.golang.org/protobuf/cmd/protoc-gen-go@latest` + `go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest`

---

### [T15] E2E tests
- **Phase**: 4 — CLI + Integration
- **Type**: test
- **Depends on**: T13, T14
- **Priority**: 🟢 Flexible
- **Input**: full platform running in Docker (production image)
- **Output**:
  - `tests/e2e/test_generate_proto_go.py` — F1 end-to-end
  - `tests/e2e/test_generate_openapi_go.py` — F2, F4 end-to-end
  - `tests/e2e/test_error_handling.py` — invalid inputs
  - `tests/e2e/conftest.py` — Docker Compose fixtures
- **Acceptance criteria**:
  - [ ] F1 E2E: upload proto specs → receive ZIP → extract → contains `.go` files with protobuf types
  - [ ] F2 E2E: upload OpenAPI spec → receive ZIP → extract → contains Go server with mux router
  - [ ] F4 E2E: upload OpenAPI spec → receive ZIP → extract → contains Go client
  - [ ] Error E2E: upload broken proto → receive 500 with error message mentioning parse error
  - [ ] Error E2E: unsupported combination (e.g., spec_type=asyncapi) → receive 400
  - [ ] CLI E2E: `aicreator generate --function f1 --spec {fixtures} --output {tmp}` produces files
  - [ ] Status E2E: after generation, `aicreator status {id}` shows completed
  - [ ] All generated Go code compiles (`go build ./...` in output dir)
- **Tests required**: all of the above (this IS the test task)
- **Constitution check**: P1 (Determinism) — verify same input produces same output hash; P3 (Fail Fast) — verify error messages are actionable
- **Implementation notes**:
  - Tests run against production Docker Compose (`docker compose --profile prod up`)
  - Use `httpx` directly (not CLI) for API tests — faster, easier assertions
  - CLI tests via `subprocess.run(["uv", "run", "aicreator", ...])` — test real CLI behavior
  - Fixtures from `tests/fixtures/` (T04)
  - Mark as `@pytest.mark.e2e` — separate from unit/integration in CI
  - Determinism check: run same generation twice, compare input_hash in both DB records

---

## Execution Order

```
── Wave 1 ────────────────────────────────────────────
   🔴 T01: Python project skeleton (uv + pyproject.toml)

── Wave 2 (parallel after T01) ───────────────────────
   🔴 T02: FastAPI app + health endpoint
   🔴 T03: SQLAlchemy models + DB engine
   🟡 T04: Test fixtures (proto + openapi)
   🔴 T05: Core abstractions (BaseGenerator)

── Wave 3 (parallel after Wave 2) ────────────────────
   🔴 T06: Orchestrator + Registry              ← T05
   🔴 T07: BufGoGenerator (F1)                  ← T05, T04
   🔴 T08: OpenAPI generators (F2 + F4)         ← T05, T04
   🔴 T09: PostProcessor chain                  ← T05
   🔴 T10: Alembic + Docker Compose             ← T02, T03

── Wave 4 (after Wave 3) ─────────────────────────────
   🔴 T11: POST /api/v1/generate                ← T06-T10
   🟡 T12: GET /api/v1/generations/{id}         ← T10
   🔴 T13: CLI generate + status                ← T11, T12
   🟡 T14: Multi-stage production Dockerfile    ← T10
   🟢 T15: E2E tests                            ← T13, T14
```

---

## Progress Tracker

### Wave 1
- [x] T01: Python project skeleton (uv + pyproject.toml)

### Wave 2
- [x] T02: FastAPI app + health endpoint
- [x] T03: SQLAlchemy models + DB engine
- [x] T04: Test fixtures (proto + openapi)
- [x] T05: Core abstractions (BaseGenerator)

### Wave 3
- [x] T06: Orchestrator + Registry
- [x] T07: BufGoGenerator (F1)
- [x] T08: OpenAPI generators (F2 + F4)
- [x] T09: PostProcessor chain
- [x] T10: Alembic + Docker Compose

### Wave 4
- [x] T11: POST /api/v1/generate
- [x] T12: GET /api/v1/generations/{id}
- [x] T13: CLI generate + status
- [x] T14: Multi-stage production Dockerfile
- [x] T15: E2E tests

---

## First Task Brief (T01)

**Goal**: Create Python project skeleton with uv package manager.

### Files to create/update

```
pyproject.toml                    # PEP 621 project config
.python-version                   # Python 3.12
.gitignore                        # UPDATE: append Python patterns
.pre-commit-config.yaml           # ruff + mypy hooks
src/aicreator/__init__.py         # __version__ = "0.1.0"
src/aicreator/api/__init__.py
src/aicreator/cli/__init__.py
src/aicreator/core/__init__.py
src/aicreator/generators/__init__.py
src/aicreator/db/__init__.py
tests/__init__.py
tests/conftest.py                 # Empty for now
tests/unit/__init__.py
tests/integration/__init__.py
```

### pyproject.toml content

```toml
[project]
name = "aicreator"
version = "0.1.0"
description = "Platform for deterministic code generation from specifications"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.34",
    "sqlalchemy>=2.0",
    "alembic>=1.14",
    "typer>=0.15",
    "httpx>=0.28",
    "rich>=13",
    "pydantic-settings>=2.7",
    "psycopg2-binary>=2.9",
]

[project.scripts]
aicreator = "aicreator.cli.app:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/aicreator"]

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-cov>=6",
    "ruff>=0.8",
    "mypy>=1.13",
]

[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]

[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

### Commands to run

```bash
cd /d/Proj/X5\ Proj/AICreator
uv sync
uv run ruff check src/
uv run mypy src/
uv run pytest
```

### Expected result

- `uv sync` creates `.venv/` and `uv.lock`
- `ruff check` — no warnings
- `mypy` — no errors
- `pytest` — 0 tests collected, exit code 5 (no tests) or 0

### Verification

```bash
# Verify package is importable
uv run python -c "from aicreator import __version__; print(__version__)"
# Should print: 0.1.0
```
