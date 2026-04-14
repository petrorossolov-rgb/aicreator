# AICreator

Platform for automated code generation from specifications (Proto, OpenAPI, AsyncAPI, PUML).

## Tech Stack

- **Orchestration**: Docker Compose v2
- **Proto generation**: buf (managed plugins from BSR)
- **OpenAPI generation**: openapi-generator-cli
- **Languages**: Kotlin, Go, Python
- **AI layer** (future): litellm → on-prem LLMs (Qwen 3 235B, GLM 4.7)

## Project Structure

```
docs/                    # Architecture docs, ADRs, epic artifacts
  architecture/adr/      # Architectural Decision Records
  {epicId}/              # Per-epic: research.md, plan.md, tasks.md, log.md
demo/                    # ep01-demo: Docker-based code generation demo
presentations/           # Slidev presentation materials
```

## Commands

```bash
# Demo (ep01-demo)
cd demo && docker compose up --build          # Full pipeline
SPECS_DIR=./real-specs docker compose up       # With real specs (volume swap)
docker compose up f1-kotlin format-kotlin      # Single function
```

## Constitution (Immutable Principles)

1. **Determinism First**: Identical input must produce identical output, every run. No randomness in deterministic generation functions. Input hash in DB confirms determinism.
2. **Containerized Platform**: Platform and all generation tools run inside containers. Host machine needs only Docker — nothing else installed.
3. **Fail Fast, Fail Loud**: Any step failure (generation, formatting, compilation) stops the pipeline immediately with a clear error message. No silent failures.
4. **Specification Agnostic**: Adding new specifications must not require code changes to the platform core. Registry pattern routes to the right generator.
5. **Pinned Versions**: All Docker images and tool versions use explicit tags (e.g., `golang:1.23-alpine`, not `latest`). Reproducibility over convenience.
6. **Minimal Infrastructure**: Platform requires only PostgreSQL as external dependency. No message queues, caches, or auxiliary services for MVP.
7. **Template-Driven Generation**: Code generation uses customizable templates for corporate standards (headers, naming, patterns). Templates live in the platform repository.
8. **OSS 700+ Stars Gate**: All external dependencies must have 700+ GitHub stars and active maintenance (per ADR-005).
9. **Go First, Multi-Language by Design**: First release targets Go only. Architecture supports multiple languages through Strategy + Registry pattern without core changes.

## Epics

| ID | Name | Status |
|----|------|--------|
| ep01-demo | Demo: deterministic code generation (F1, F2, F4) | ✅ Done |
| ep02-foundation | Platform foundation: CLI + API + generators (Go) | ✅ Done |
