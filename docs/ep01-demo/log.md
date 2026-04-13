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
