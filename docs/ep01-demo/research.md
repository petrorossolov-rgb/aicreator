# Research Report: ep01-demo

> Demo repository for AICreator — deterministic code generation functions F1, F2, F4

**Date:** 2026-04-13
**Epic:** ep01-demo

---

## 1. Understanding the Problem

### What we're building

Demo-репозиторий, демонстрирующий три детерминистические функции кодогенерации AICreator:

| Function | Input | Output | Tool |
|----------|-------|--------|------|
| **F1** | Protobuf specs | Kotlin data classes + gRPC stubs | buf + protobuf-kotlin |
| **F2** | OpenAPI spec | Go REST server endpoints | openapi-generator (go-server) |
| **F4** | OpenAPI spec | Python client library | openapi-generator (python) |

### Core problem

CTO-презентация AICreator нуждается в работающей демонстрации: «запускаем один скрипт — получаем отформатированный, скомпилированный код из спецификаций». Демо должно убедить стейкхолдеров, что детерминистическая генерация работает надёжно и предсказуемо.

### Target audience

- CTO и технические руководители — на презентации
- Разработчики пилотных команд (Java/Kotlin + Go) — для оценки качества генерации
- Архитекторы — для оценки подхода к интеграции

### Key functional requirements

1. **Docker-изоляция**: каждая функция генерации запускается в Docker-контейнере
2. **Post-processing**: форматирование (ktlint, gofmt, black) + линтинг (golangci-lint, ruff) после генерации
3. **Compilation validation**: сгенерированный код должен компилироваться без ошибок
4. **Synthetic specs**: логистический домен (Order, Shipment, Warehouse) — реалистичные спецификации
5. **Volume swap**: замена синтетических спецификаций на реальные через Docker volume mount
6. **Template customization**: корпоративный заголовок, именование пакетов, паттерны обработки ошибок
7. **Minimal footprint**: чистые shell-скрипты, без CLI-фреймворка, без API-сервера, без БД

---

## 2. Market & Existing Solutions Analysis

### Existing approaches

| Tool/Repo | Approach | Strengths | Weaknesses |
|-----------|----------|-----------|------------|
| **buf** (bufbuild/buf) | Managed proto generation with BSR plugins | Remote plugin ecosystem, lint + breaking change detection, clean config | Kotlin generation через Java plugin + Connect RPC; no standalone Kotlin data classes plugin |
| **openapi-generator** | Mustache-template code generation from OpenAPI | 60+ language targets, mature ecosystem, template customization | Generated code quality varies by generator; Go server stubs need manual refinement |
| **namely/docker-protoc** | All-in-one Docker container for protoc | Simple single-container approach | Stale (not updated regularly), no buf integration |
| **grpc-ecosystem/grpc-gateway** | Proto→REST gateway | Production-proven REST gateway from proto | Go-only, not a general code generation solution |
| **Swagger Codegen** | OpenAPI code generation (predecessor) | Well-known | Superseded by openapi-generator, fewer active contributions |

### Gaps we fill

- **Unified pipeline**: ни один из существующих инструментов не объединяет proto→Kotlin + OpenAPI→Go + OpenAPI→Python в единый запуск
- **Post-processing as first class**: существующие демо обычно не включают форматирование и линтинг как часть pipeline
- **Compilation validation**: автоматическая проверка компиляции сгенерированного кода — редкость в демо-репозиториях
- **Volume swap pattern**: документированный подход к замене спецификаций для демо → production

### Lessons from existing implementations

- **Makefile + Docker Compose** — наиболее распространённый паттерн оркестрации (PatrickKoss/grpc-gateway-example)
- **Separate proto/ и openapi/ директории** — стандартная структура ввода
- **`buf.gen.yaml`** — конфигурация предпочтительнее CLI-флагов для воспроизводимости
- **`--additional-properties`** — основной механизм кастомизации openapi-generator

---

## 3. Technology Stack Recommendation

### Core generation tools

| What | Why | Trade-off | Alternative |
|------|-----|-----------|-------------|
| **Docker Compose** | Оркестрация multi-container pipeline; `depends_on: condition: service_completed_successfully` для последовательности | Overhead Docker на каждый шаг vs скорость | Makefile с Docker run (проще, но нет dependency management) |
| **bufbuild/buf:latest** | Managed plugins из BSR, lint + format для proto, clean YAML config | Remote plugins требуют сеть (или кэш) | protoc напрямую (больше ручной конфигурации) |
| **openapitools/openapi-generator-cli:v7.20.0** | 60+ generators, mustache templates, active development | Generated Go code — не идеальный (потребует gofmt/golangci-lint) | swagger-codegen (устарел) |

### Post-processing tools

| What | Why | Trade-off | Alternative |
|------|-----|-----------|-------------|
| **ktlint** (pinterest/ktlint) | Official Kotlin linter/formatter, Android Kotlin Style Guide | Нет official Docker image — нужен custom image или JAR | detekt (больше правил, сложнее конфигурация) |
| **gofmt** (встроен в Go) | Стандартный Go formatter, zero config | Только форматирование, не lint | — |
| **golangci-lint** (golangci/golangci-lint:v1.61) | Meta-linter: включает gofmt + 100+ linters | Тяжёлый image (~200MB) | staticcheck (легче, меньше правил) |
| **black** | Deterministic Python formatter | Одно мнение, нет конфигурации | autopep8 (более гибкий) |
| **ruff** (astral-sh/ruff) | 30x быстрее black, linter + formatter в одном | Относительно молодой проект | black + flake8 (проверенная комбинация, но два инструмента) |

### Compilation validation

| What | Why | Trade-off |
|------|-----|-----------|
| **kotlinc** (JetBrains) | Kotlin compiler для проверки сгенерированных классов | Требует JDK в контейнере (~400MB) |
| **go build ./...** | Стандартная Go компиляция | Требует go.mod init + dependency download |
| **python3 -m py_compile** / **ruff check** | Syntax check без выполнения | Не проверяет import resolution полностью |

### Decision: ruff вместо black + flake8

Для Python используем **ruff** как единый инструмент (formatter + linter):
- Быстрее в 30x
- Совместим с Black на 99.9%
- Один инструмент вместо двух
- ADR-005 (700+ stars): ruff имеет 35k+ stars

---

## 4. Architecture Overview

### High-level structure

```
ep01-demo/
├── docker-compose.yml          # Orchestration: generate → format → validate
├── .env                        # SPECS_DIR=./specs (default: synthetic)
│
├── specs/                      # Synthetic specs (in repo, default)
│   ├── proto/
│   │   ├── buf.yaml            # buf module config
│   │   ├── buf.gen.yaml        # generation config
│   │   ├── order.proto
│   │   ├── shipment.proto
│   │   └── warehouse.proto
│   └── openapi/
│       └── logistics.yaml      # OpenAPI 3.1 spec
│
├── templates/                  # Custom mustache templates
│   ├── go-server/              # Corporate header, package naming
│   └── python/                 # Corporate header, error handling
│
├── config/                     # openapi-generator configs
│   ├── go-server.yaml
│   └── python-client.yaml
│
├── scripts/                    # Generation + validation scripts
│   ├── generate-f1-kotlin.sh   # F1: Proto→Kotlin via buf
│   ├── generate-f2-go.sh       # F2: OpenAPI→Go via openapi-generator
│   ├── generate-f4-python.sh   # F4: OpenAPI→Python via openapi-generator
│   ├── format.sh               # Post-processing: ktlint, gofmt, ruff
│   ├── validate.sh             # Compilation check
│   └── run-all.sh              # Master script: generate → format → validate
│
├── generated/                  # Output (gitignored)
│   ├── kotlin/
│   ├── go/
│   └── python/
│
└── Dockerfiles/                # Custom images where needed
    ├── Dockerfile.kotlin       # buf + kotlinc + ktlint
    ├── Dockerfile.go           # openapi-generator-cli + go + golangci-lint
    └── Dockerfile.python       # openapi-generator-cli + python3 + ruff
```

### Data flow

```
[specs/proto/*.proto] ──buf generate──→ [generated/kotlin/] ──ktlint──→ [kotlinc compile check]
                                                                              ↓
[specs/openapi/logistics.yaml] ──openapi-generator (go-server)──→ [generated/go/] ──gofmt + golangci-lint──→ [go build check]
                                                                              ↓
[specs/openapi/logistics.yaml] ──openapi-generator (python)──→ [generated/python/] ──ruff format + check──→ [py_compile check]
```

### Docker Compose services

```yaml
services:
  # Stage 1: Generation (parallel)
  f1-kotlin:     # buf generate → generated/kotlin/
  f2-go:         # openapi-generator go-server → generated/go/
  f4-python:     # openapi-generator python → generated/python/

  # Stage 2: Format (depends on Stage 1)
  format-kotlin: # ktlint -F → generated/kotlin/
  format-go:     # gofmt + golangci-lint --fix → generated/go/
  format-python: # ruff format + ruff check --fix → generated/python/

  # Stage 3: Validate (depends on Stage 2)
  validate-kotlin: # kotlinc compile check
  validate-go:     # go build ./...
  validate-python: # python3 -m py_compile + ruff check
```

### Volume swap pattern

```bash
# Default: synthetic specs
docker compose up

# Real specs: override SPECS_DIR
SPECS_DIR=./real-specs docker compose up

# Or via docker-compose.override.yml (not in repo)
```

Переменная `SPECS_DIR` в `.env` позволяет заменить директорию спецификаций без изменения скриптов.

### Integration points

- **Нет внешних зависимостей runtime**: всё работает offline в Docker
- **buf BSR plugins**: remote plugins (buf.build/protocolbuffers/java, buf.build/connectrpc/kotlin) — нужен интернет при первом запуске или pre-cached images
- **openapi-generator**: всё включено в Docker image

---

## 4.1. Prior Operational Context

`progress.md` не существует — проект на стадии планирования, кода ещё нет. Пропускаем.

---

## 5. Risks, Assumptions & Complexity Assessment

### Complexity ratings

| Dimension | Rating | Comment |
|-----------|--------|---------|
| **Technical complexity** | Low-Medium | Все инструменты зрелые и документированные; основная сложность — корректная конфигурация buf для Kotlin и mustache templates |
| **Time to MVP** | Low | 2-3 дня для работающего демо (shell-скрипты + Docker Compose) |
| **Maintenance burden** | Low | Скрипты простые, зависимости — pinned Docker images |

### Key risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **buf Kotlin generation** — remote plugins могут не генерировать «чистые» Kotlin data classes, а только Java + Connect стабы | Medium | High | Протестировать buf.build/protocolbuffers/java с opt target_language=kotlin; fallback: protoc-gen-kotlin напрямую |
| **openapi-generator Go quality** — go-server generator может генерировать code с warnings | Medium | Low | golangci-lint --fix + gofmt в post-processing |
| **Docker image sizes** — Kotlin (JDK) + Go + Python images суммарно 2-3 GB | Low | Medium | Multi-stage builds; Alpine-based images; или один толстый image для всех |
| **buf BSR network dependency** — remote plugins требуют интернет | Medium | Medium | Pre-pull images; или local plugin binaries в Dockerfile |
| **Compilation validation false positives** — сгенерированный код может не компилироваться из-за missing dependencies (gRPC runtime, etc.) | Medium | High | Include minimal go.mod / build.gradle.kts with required dependencies в generated/ |

### Assumptions

| Assumption | What breaks if wrong |
|------------|---------------------|
| Docker Desktop установлен и работает на демо-машине | Демо не запустится; fallback: local install tools |
| Интернет доступен для pull Docker images и buf BSR plugins | Нужен pre-pull и cache; или offline-ready images |
| Синтетические спецификации достаточно реалистичны для демо | Аудитория не впечатлится; нужен review от доменных экспертов |
| Реальные спецификации (для volume swap) имеют тот же формат proto3 и OpenAPI 3.x | Скрипты могут потребовать адаптации |
| Демо запускается на машине с 8+ GB RAM | Docker Compose с 3+ containers + compilation может OOM |

---

## 6. Foundational Principles (Constitution Draft)

> **Determinism First**: Every generation run with the same input must produce byte-identical output.
> *Rationale*: Demo must prove predictability — key selling point vs AI-generation for stakeholders.

> **Docker-Isolated Execution**: All tools run inside containers; host needs only Docker.
> *Rationale*: Eliminates "works on my machine" — demo must run on any machine with Docker.

> **Fail Fast, Fail Loud**: Any step failure (generation, formatting, compilation) stops the pipeline with clear error message.
> *Rationale*: Silent failures undermine trust; demo must be transparent about what works and what doesn't.

> **Swap Without Change**: Replacing specs must not require editing any script or configuration.
> *Rationale*: Volume swap pattern proves the system is spec-agnostic, not hardcoded to synthetic data.

> **Minimal Customization**: Template overrides limited to corporate header, package naming, basic error handling.
> *Rationale*: Demo scope — show customization is possible, not build a full template library.

> **Pinned Versions**: All Docker images use specific version tags, never `latest` in production config.
> *Rationale*: Reproducibility; demo must work the same in 3 months as today.

> **Zero Runtime Dependencies**: No databases, no API servers, no message queues — pure generation pipeline.
> *Rationale*: Simplicity for demo; every added component is a potential failure point during live presentation.

---

## 7. Recommended Next Steps

### MVP scope (demo-ready)

**Wave 1 — Skeleton (0.5 day)**
- Repo structure, docker-compose.yml, .env, .gitignore
- Synthetic proto specs (Order, Shipment, Warehouse)
- Synthetic OpenAPI spec (logistics REST API)

**Wave 2 — Generation scripts (1 day)**
- F1: `generate-f1-kotlin.sh` + buf.gen.yaml + Dockerfile.kotlin
- F2: `generate-f2-go.sh` + go-server config + Dockerfile.go
- F4: `generate-f4-python.sh` + python config + Dockerfile.python
- Master script `run-all.sh`

**Wave 3 — Post-processing & validation (0.5 day)**
- `format.sh`: ktlint, gofmt/golangci-lint, ruff
- `validate.sh`: kotlinc, go build, py_compile
- Integration into docker-compose pipeline

**Wave 4 — Customization & polish (0.5 day)**
- Mustache templates: corporate header, package naming
- Volume swap documentation and testing
- README with demo instructions

### Open questions for user

1. **Kotlin generation target**: чистые data classes (protobuf-kotlin) или Connect RPC stubs (с gRPC service interfaces)? Data classes проще для демо.

2. **OpenAPI Go generator**: `go-server` (net/http) или `go-gin-server` (Gin framework)? go-server более универсальный.

3. **Single Docker image vs multiple**: один толстый image со всеми инструментами (проще, один build) или отдельные images per function (чище изоляция, параллельный запуск)?

4. **Corporate header content**: какой текст в заголовке? Placeholder типа `Copyright (c) 2026 X5 Group` или реальный?

5. **Репозиторий**: отдельный repo или директория в текущем AICreator repo?
