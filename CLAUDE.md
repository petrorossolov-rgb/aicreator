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

1. **Determinism First**: Identical input must produce identical output, every run. No randomness in deterministic generation functions.
2. **Docker-Isolated Execution**: All tools run inside containers. Host machine needs only Docker — nothing else installed.
3. **Fail Fast, Fail Loud**: Any step failure (generation, formatting, compilation) stops the pipeline immediately with a clear error message. No silent failures.
4. **Swap Without Change**: Replacing input specifications must not require editing any script, config, or Dockerfile. Volume mount is the only mechanism.
5. **Pinned Versions**: All Docker images and tool versions use explicit tags (e.g., `golang:1.23-alpine`, not `latest`). Reproducibility over convenience.
6. **Zero Runtime Dependencies**: No databases, no API servers, no message queues. Pure generation pipeline — every added component is a potential demo failure point.
7. **Minimal Customization**: Template overrides limited to corporate header, package naming, and basic error handling patterns. Demo scope — show it's possible, not build a template library.
8. **OSS 700+ Stars Gate**: All external dependencies must have 700+ GitHub stars and active maintenance (per ADR-005).

## Epics

| ID | Name | Status |
|----|------|--------|
| ep01-demo | Demo: deterministic code generation (F1, F2, F4) | 🔄 Active |
