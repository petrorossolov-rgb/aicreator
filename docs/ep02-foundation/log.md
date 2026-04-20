# Execution Log — ep02-foundation

<!-- Task completion entries appended by /execute -->

## [2026-04-14] — [T01] Python project skeleton with uv
- **Status**: ✅ Done
- **Files changed**: pyproject.toml, .python-version, .pre-commit-config.yaml, .gitignore, src/aicreator/__init__.py, src/aicreator/{api,cli,core,db,generators}/__init__.py, tests/{__init__,conftest}.py, tests/{unit,integration}/__init__.py
- **Learnings**: uv 0.10.7 on Windows works well with src layout + hatchling. Exit code 5 from pytest is expected when 0 tests collected.
- **Patterns**: pre-commit hooks with ruff + mypy require `additional_dependencies` for pydantic in mypy hook.

## [2026-04-14] — [T02] FastAPI app + health endpoint + logging
- **Status**: ✅ Done
- **Files changed**: src/aicreator/core/config.py, src/aicreator/core/logging.py, src/aicreator/api/app.py, src/aicreator/api/middleware.py, src/aicreator/api/routes/health.py, tests/unit/test_health.py, .pre-commit-config.yaml
- **Learnings**: pre-commit mirrors-mypy needs ALL project deps in `additional_dependencies` (fastapi, sqlalchemy, etc.) since it runs in isolated env. `dictConfig` replaces pytest caplog handlers — test log filters directly via unit test on filter class.
- **Patterns**: Request ID via `contextvars.ContextVar` + `logging.Filter` — set in middleware, read anywhere in the async call stack.

## [2026-04-14] — [T03] SQLAlchemy models + DB engine
- **Status**: ✅ Done
- **Files changed**: src/aicreator/db/models.py, src/aicreator/db/engine.py, src/aicreator/db/repository.py, tests/unit/test_models.py
- **Learnings**: SQLAlchemy `Uuid` column type expects `uuid.UUID` objects, not strings — `db.get(Model, uuid_obj)` not `db.get(Model, str(uuid))`. Use `StrEnum` instead of `(str, Enum)` for Python 3.12+. `datetime.UTC` alias preferred over `timezone.utc`.
- **Patterns**: In-memory SQLite for unit tests with `Base.metadata.create_all(engine)` in fixture. Repository functions accept `Session` as first arg for testability.

## [2026-04-14] — [T04] Test fixtures (proto + openapi specs)
- **Status**: ✅ Done
- **Files changed**: tests/fixtures/proto/{buf.yaml,buf.gen.go.yaml,common.proto,order.proto,shipment.proto,warehouse.proto}, tests/fixtures/openapi/logistics.yaml, tests/fixtures/invalid/proto/{broken.proto,buf.yaml}, tests/fixtures/invalid/openapi/logistics.yaml, tests/conftest.py
- **Learnings**: Invalid spec fixtures from demo/specs-invalid/ already had buf.yaml alongside broken.proto. Conftest fixtures use `pathlib.Path(__file__).parent / "fixtures"` for reliable resolution.
- **Patterns**: Test fixtures live in `tests/fixtures/` with subdirs mirroring spec types. conftest.py exposes fixture functions for path resolution.

## [2026-04-14] — [T05] Core abstractions (BaseGenerator, GeneratorConfig, GenerationResult)
- **Status**: ✅ Done
- **Files changed**: src/aicreator/core/generator.py, tests/unit/test_generator.py, tests/conftest.py
- **Learnings**: Pydantic BaseModel with `Path` fields works well for GenerationResult — JSON serialization handled automatically. StubGenerator with `should_fail_validation` flag enables both positive and negative test scenarios.
- **Patterns**: ABC with `@abstractmethod` for validate/generate. Pydantic models (not dataclasses) for result types — enables API serialization. StubGenerator in conftest.py shared across test modules.

## [2026-04-14] — [T06] Orchestrator with Registry pattern
- **Status**: ✅ Done
- **Files changed**: src/aicreator/core/orchestrator.py, tests/unit/test_orchestrator.py
- **Learnings**: Class-level `_registry` dict requires `reset_registry()` classmethod for test isolation. PostProcessor injected via Protocol + constructor DI — no concrete PostProcessor needed until T09.
- **Patterns**: `@Orchestrator.register(spec_type, language, function)` decorator for generator registration. `PostProcessorProtocol` for DI — _NoOpPostProcessor as default. `autouse` fixture with `reset_registry()` prevents cross-test pollution.

## [2026-04-14] — [T07] BufGoGenerator (F1: Proto → Go)
- **Status**: ✅ Done
- **Files changed**: src/aicreator/generators/buf.py, tests/unit/test_buf_generator.py
- **Learnings**: buf.gen*.yaml glob picks up template files like buf.gen.go.yaml from spec dir. `--output` flag overrides `out:` in buf.gen.yaml for flexible output paths.
- **Patterns**: Generators follow pattern: validate(spec_path) checks dir/files exist, generate() wraps subprocess.run with timeout + capture_output. `time.monotonic()` for reliable duration measurement.

## [2026-04-14] — [T08] OpenAPI generators (F2: Go server + F4: Go client)
- **Status**: ✅ Done
- **Files changed**: src/aicreator/generators/openapi_base.py, src/aicreator/generators/openapi_server.py, src/aicreator/generators/openapi_client.py, src/aicreator/templates/go-server/partial_header.mustache, tests/unit/test_openapi_generators.py, pyproject.toml, .pre-commit-config.yaml
- **Learnings**: OpenAPI generators share identical validate + generate logic — extracted to OpenAPIBaseGenerator. Invalid OpenAPI fixture has `openapi` key (just missing `paths`), so "missing openapi key" test needs separate fixture. pyyaml needs types-pyyaml in pre-commit additional_dependencies.
- **Patterns**: Base class + `generator_name` class var for OpenAPI generators — minimal subclass per generator type. `_build_command()` method constructs CLI args from config.

## [2026-04-14] — [T09] PostProcessor chain
- **Status**: ✅ Done
- **Files changed**: src/aicreator/core/postprocessor.py, tests/unit/test_postprocessor.py
- **Learnings**: PostProcessor.run() satisfies PostProcessorProtocol from orchestrator.py (same signature: `run(output_dir, language)`). Severity enum with StrEnum keeps DB-friendly string values.
- **Patterns**: Step ABC + severity enum for chain control flow: FATAL raises PostProcessError, WARNING logs and continues. `go_postprocessor()` factory creates standard 4-step Go chain. MagicMock(spec=PostProcessStep) verifies third step not called after fatal failure.

## [2026-04-14] — [T10] Alembic migrations + Docker Compose
- **Status**: ✅ Done
- **Files changed**: alembic.ini, alembic/env.py, alembic/versions/2089e8373d0d_initial_generations_table.py, docker/Dockerfile.dev, docker/docker-compose.yml, docker/entrypoint.sh, .env.example
- **Learnings**: Guard hook blocks Write tool for .env files — use bash redirect. Alembic autogenerate with SQLite produces correct schema but `postgresql_ops` index params are preserved (PostgreSQL-specific, ignored on SQLite).
- **Patterns**: alembic env.py overrides `sqlalchemy.url` from `settings.database_url` at runtime. Entrypoint runs `alembic upgrade head` before uvicorn start. `uv sync --no-dev --frozen` in Dockerfile for reproducible prod-like builds.

## [2026-04-14] — [T11] POST /api/v1/generate endpoint
- **Status**: ✅ Done
- **Files changed**: src/aicreator/api/schemas.py, src/aicreator/api/dependencies.py, src/aicreator/api/routes/generate.py, src/aicreator/api/app.py, src/aicreator/db/models.py, tests/integration/test_api_generate.py, pyproject.toml
- **Learnings**: `python-multipart` required for FastAPI `UploadFile`/`Form`. In-memory SQLite for TestClient needs `StaticPool` + `check_same_thread=False` due to ASGI threading. Model `Mapped[str]` for `Uuid` column breaks mypy — must use `Mapped[uuid.UUID]`.
- **Patterns**: Multipart form: `files[]` as `list[UploadFile]` + `metadata` as `Form(str)` parsed to Pydantic model. DI override via `app.dependency_overrides[get_db]` for test isolation. Input hash: SHA-256 over sorted (filename, content) pairs.

## [2026-04-14] — [T12] GET /api/v1/generations/{id} endpoint
- **Status**: ✅ Done
- **Files changed**: src/aicreator/api/routes/generations.py, src/aicreator/api/app.py, tests/unit/test_generations_endpoint.py
- **Learnings**: FastAPI path param with `UUID` type auto-validates format and returns 422 for invalid UUIDs. No additional validation code needed.
- **Patterns**: Simple CRUD read endpoint: repository.get → None check → 404 or Pydantic response model.

## [2026-04-14] — [T13] CLI: generate + status + health commands
- **Status**: ✅ Done
- **Files changed**: src/aicreator/cli/app.py, src/aicreator/cli/output.py, src/aicreator/cli/commands/{generate,status,health}.py, tests/unit/test_cli.py, .pre-commit-config.yaml
- **Learnings**: Typer CliRunner works well with MagicMock for httpx.Client context manager. Pre-commit mypy needs httpx+rich in additional_dependencies.
- **Patterns**: FUNCTION_SPEC_MAP dict maps f1→proto, f2/f4→openapi. Rich `console.status()` for spinner. Typer `Exit(code=1)` for error exits.

## [2026-04-14] — [T14] Multi-stage production Dockerfile
- **Status**: ✅ Done
- **Files changed**: docker/Dockerfile, docker/entrypoint.prod.sh, docker/docker-compose.yml
- **Learnings**: python:3.12-slim (Debian Trixie) has JRE 21, not 17. openapi-generator 7.12.0 works fine with JRE 21. Image size 1.34GB with all tools.
- **Patterns**: Three-stage Docker build: Stage 1 (golang:1.23-alpine) → Go tools. Stage 2 (alpine) → buf + protoc binaries. Stage 3 (python:3.12-slim) → runtime with COPY --from stages 1+2. Production profile: `docker compose --profile prod up`.

## [2026-04-14] — [T15] E2E tests
- **Status**: ✅ Done
- **Files changed**: tests/e2e/{__init__,conftest}.py, tests/e2e/test_generate_proto_go.py, tests/e2e/test_generate_openapi_go.py, tests/e2e/test_error_handling.py, pyproject.toml
- **Learnings**: `addopts = "-m 'not e2e'"` in pyproject.toml excludes e2e from default test run. Generator fixture for yield in conftest needs `# type: ignore[no-untyped-def]` for mypy strict (return type is Generator).
- **Patterns**: Session-scoped `docker_compose_up` fixture manages lifecycle: `up -d --build` → health poll → `down -v`. E2E tests use httpx directly for API and subprocess for CLI.

## [2026-04-20] — INCIDENT: uv.lock missing on fresh clone (MacBook demo)
- **Symptom**: `docker compose --profile prod build` на MacBook падал на шаге `COPY pyproject.toml uv.lock ./` с ошибкой `"/uv.lock": not found` (оба сервиса: `api` via Dockerfile.dev и `api-prod` via Dockerfile).
- **Root cause**: `uv.lock` был внесён в `.gitignore` (строка 17) с самого начала проекта, поэтому никогда не коммитился. На dev-машине (Windows) файл существовал локально, поэтому Docker build работал. На чистом клоне файла не было → `uv sync --frozen` невозможен.
- **Fix** (commit 93defac): удалена строка `uv.lock` из `.gitignore`, закоммичен текущий lock-файл (59 resolved packages, `uv lock --check` прошёл).
- **Prevention**:
  - Lock-файлы (`uv.lock`, `package-lock.json`, `poetry.lock`, `go.sum`) — ВСЕГДА коммитим. Это требование и официальной uv-документации, и конституционного принципа «Determinism First». Рекомендация на будущее: при старте нового Python-проекта с uv сразу `git add uv.lock`.
  - Для эпика ep02-foundation: T15 E2E-тесты не поймали эту регрессию потому что они запускаются из dev-окружения, где `uv.lock` уже существует локально. Следовало бы добавить smoke-тест «сборка из чистого клона» (простой CI job: `git clone` в temp dir → `docker compose build`).
- **Docs debt**: в `docs/ep02-foundation/demo/macbook-setup.md` troubleshooting-секция не содержит этого случая — добавить при следующем /sync-docs.
- **Time to resolve**: 1 фаза (диагноз уже был предвнесён пользователем).
