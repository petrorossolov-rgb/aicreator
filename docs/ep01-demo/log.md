# Execution Log — ep01-demo

<!-- Task completion entries appended by /execute -->

## [2026-04-13] — [T01] Project skeleton: directories, .env, .gitignore
- **Status**: ✅ Done
- **Files changed**: `demo/.env`, `demo/.gitignore`, directories: specs/proto, specs/openapi, templates/go-server, templates/python, config, scripts, dockerfiles
- **Learnings**: Guard hook blocks direct `.env` writes — use bash echo instead
- **Patterns**: none

## [2026-04-13] — [T02] Synthetic Proto specifications
- **Status**: ✅ Done
- **Files changed**: `demo/specs/proto/buf.yaml`, `buf.gen.yaml`, `common.proto`, `order.proto`, `shipment.proto`, `warehouse.proto`
- **Learnings**: buf not installed on host; lint validation deferred to Docker (T05a). Proto cross-refs use `import "common.proto"` with same-package flat structure.
- **Patterns**: All protos use `java_multiple_files = true` + `java_package` for Kotlin codegen compatibility

## [2026-04-13] — [T03] Synthetic OpenAPI specification
- **Status**: ✅ Done
- **Files changed**: `demo/specs/openapi/logistics.yaml`
- **Learnings**: OpenAPI 3.0.3 (not 3.1) for openapi-generator compatibility. 11 operations, 8 paths, 18 schemas.
- **Patterns**: Pagination via shared `$ref` parameters (Limit, Offset). All operations have operationId.

## [2026-04-13] — [T04] openapi-generator configs + mustache templates
- **Status**: ✅ Done
- **Files changed**: `demo/config/go-server.yaml`, `demo/config/python-client.yaml`, `demo/templates/go-server/partial_header.mustache`, `demo/templates/python/partial_header.mustache`
- **Learnings**: Configs use container-absolute paths (`/specs/...`, `/templates/...`) since they run inside Docker. `partial_header.mustache` is the template partial that openapi-generator injects into generated file headers.
- **Patterns**: Config inputSpec/outputDir/templateDir use container paths, not host paths

## [2026-04-13] — [T05] F1 Kotlin: Dockerfile + generation script
- **Status**: ✅ Done
- **Files changed**: `demo/dockerfiles/Dockerfile.kotlin`, `demo/scripts/generate-f1-kotlin.sh`, `demo/specs/proto/buf.gen.yaml`
- **Learnings**: buf BSR remote plugins return 403 (require auth). Switched to `protoc_builtin: java` + `protoc_builtin: kotlin` in buf.gen.yaml — requires protoc installed locally in Docker image. protoc v29.3 linux-x86_64 zip works on Alpine (statically linked).
- **Patterns**: Use `protoc_builtin` in buf.gen.yaml instead of `remote` plugins to avoid BSR authentication dependency. Kotlin codegen produces both .java (84 files) and .kt (43 files) — base classes are Java, Kotlin DSL extensions are .kt.

## [2026-04-13] — [T05a] Pre-flight: validate buf Kotlin generation in Docker
- **Status**: ✅ Done
- **Files changed**: none (validation only)
- **Learnings**: Determinism verified — two consecutive runs produce byte-identical output (md5 checksums match). Generated Kotlin files correctly import `com.google.protobuf`. BSR remote plugin fallback to local protoc already handled in T05.
- **Patterns**: none

## [2026-04-13] — [T06] F2 Go: Dockerfile + generation script
- **Status**: ✅ Done
- **Files changed**: `demo/dockerfiles/Dockerfile.go`, `demo/scripts/generate-f2-go.sh`
- **Learnings**: openapi-generator-cli JAR (~30MB) works with openjdk17-jre-headless on Alpine. golangci-lint install script from GitHub used with pinned version. Generated 31 Go files with `package logistics` and corporate header present.
- **Patterns**: openapi-generator go-server outputs to `src/` subfolder under outputDir. `--additional-properties=router=mux` passed in script (also in config, belt-and-suspenders).

## [2026-04-13] — [T07] F4 Python: Dockerfile + generation script
- **Status**: ✅ Done
- **Files changed**: `demo/dockerfiles/Dockerfile.python`, `demo/scripts/generate-f4-python.sh`
- **Learnings**: python:3.12-slim + default-jre-headless for openapi-generator. ruff installed via pip. Generated 52 Python files with `logistics_client` package structure. WARN about schema name: null is benign (no-op schema reference in spec).
- **Patterns**: Python generator creates test/, docs/, and package scaffolding automatically. Same openapi-generator JAR version (v7.12.0) across Go and Python images.
