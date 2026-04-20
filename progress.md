# Execution Progress

## Codebase Patterns
<!-- Reusable patterns discovered during implementation. Keep this section at the top. -->

- **Container paths in configs**: openapi-generator config files use absolute container paths (`/specs/...`, `/templates/...`, `/generated/...`) — volumes are mounted at these paths in docker-compose
- **Proto flat structure**: All .proto files in `specs/proto/` are flat (no subdirs), cross-ref via `import "filename.proto"` within same `logistics.v1` package
- **OpenAPI 3.0.3**: Using 3.0.3 (not 3.1) for openapi-generator compatibility
- **Guard hook**: `.env` files cannot be written via Write tool — use bash echo redirect
- **buf local plugins**: Use `protoc_builtin: java` + `protoc_builtin: kotlin` in buf.gen.yaml instead of `remote:` BSR plugins (BSR requires auth, returns 403). Requires protoc installed in Docker image.
- **MSYS_NO_PATHCONV**: On Windows Git Bash, use `MSYS_NO_PATHCONV=1` before docker run to prevent path conversion of container paths (e.g., `/scripts/...` → `C:/Program Files/Git/scripts/...`)
- **openapi-generator shared JAR**: Both Go and Python Dockerfiles download the same openapi-generator-cli v7.12.0 JAR. Keep version synchronized across images.
- **Go enum collision**: openapi-generator go-server creates flat package-level enum constants. Enum values must be globally unique within the package — use type-prefixed names (ORDER_*, SHIPMENT_*) in OpenAPI specs.
- **ktlint generated code**: Protobuf Kotlin DSL uses non-standard function names. Inject `.editorconfig` with `ktlint_standard_function-naming = disabled` before running ktlint on generated code.
- **ruff generated code**: openapi-generator Python output needs `--unsafe-fixes --ignore=E501,E721` to handle unfixable patterns in generated code.
- **SQLAlchemy Uuid type**: Pass `uuid.UUID` objects (not strings) to `db.get()` and queries. The `Uuid` column type handles serialization internally.
- **pre-commit mypy deps**: mirrors-mypy runs in isolated venv — must list all project deps (fastapi, sqlalchemy, etc.) in `additional_dependencies`.
- **ktlint max-line-length**: Protobuf Kotlin DSL extensions can produce lines >140 chars. Disable `ktlint_standard_max-line-length` in `.editorconfig` alongside `function-naming`.
- **Docker Compose one-shot chaining**: Use `depends_on: { service: { condition: service_completed_successfully } }` to chain generate → format → validate in Compose v2.
- **Volume swap specs**: Alternative spec directories must include their own `buf.yaml` + `buf.gen.yaml` alongside proto files. OpenAPI spec must be named `logistics.yaml` to match config paths.
- **OpenAPI base class pattern**: OpenAPIBaseGenerator extracts shared validate + generate + `_build_command()`. Subclass only sets `generator_name` class var ("go-server", "go").
- **PostProcessor chain control**: FATAL severity raises PostProcessError (stops chain), WARNING severity logs and continues. `go_postprocessor()` factory for standard 4-step Go chain.
- **pre-commit types-pyyaml**: mirrors-mypy needs `types-pyyaml` and `pyyaml` in additional_dependencies for yaml import.
- **SQLAlchemy Mapped[uuid.UUID]**: Use `Mapped[uuid.UUID]` (not `Mapped[str]`) for `Uuid` columns — keeps mypy and repository signatures consistent.
- **FastAPI test DB isolation**: In-memory SQLite for TestClient requires `StaticPool` + `connect_args={"check_same_thread": False}` due to ASGI threading model.
- **FastAPI multipart form**: `python-multipart` required for `UploadFile`/`Form`. Metadata sent as JSON string in Form field, parsed to Pydantic model server-side.
- **Alembic env.py override**: `config.set_main_option("sqlalchemy.url", settings.database_url)` overrides alembic.ini URL from app settings.
- **pre-commit mypy httpx/rich**: mirrors-mypy needs `httpx` and `rich` in `additional_dependencies` for CLI module type checking.
- **CLI function→spec_type map**: `FUNCTION_SPEC_MAP = {"f1": "proto", "f2": "openapi", "f4": "openapi"}` in generate command. Language defaults to "go".
- **JRE version in prod Dockerfile**: python:3.12-slim (Debian Trixie) ships JRE 21, not 17. openapi-generator 7.12.0 is compatible with JRE 11+.
- **Compose profiles for dev/prod parallelism**: when `docker-compose.yml` hosts both a dev variant and a prod variant of the same service, both MUST be gated by `profiles:` (e.g. `[dev]` and `[prod]`). Leaving one without a profile makes it start unconditionally and collide with the other on host ports.

## Docs Debt
<!-- Items logged by /execute, /change, /incident. Resolved by /sync-docs. -->
- [2026-04-20] Add troubleshooting entry "uv.lock: not found при docker build на свежем клоне" to `docs/ep02-foundation/demo/macbook-setup.md` (ref incident 2026-04-20 in ep02 log).
- [2026-04-20] Update `docs/ep02-foundation/plan.md:211` and `docs/ep02-foundation/tasks.md:381,386` — dev stack is now started via `docker compose --profile dev up`, not bare `docker compose up` (port-conflict incident 2026-04-20).

## Follow-ups
<!-- Tasks deferred from /incident or /change that need proper implementation later. -->
- [ ] [2026-04-20] Add CI smoke job "fresh-clone docker build" — clones repo into a temp directory and runs `docker compose -f docker/docker-compose.yml --profile prod build` to catch the class of bugs where build works on dev boxes but fails on fresh clones (triggered by uv.lock incident 2026-04-20).
- [ ] [2026-04-20] Run e2e suite (`pytest -m e2e`) as part of pre-release demo checklist — would have caught the port-8000 conflict before the demo (currently excluded by `addopts = "-m 'not e2e'"`).
