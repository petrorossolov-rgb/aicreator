# ep02-foundation — Pre-Development Research

> **Epic**: ep02-foundation — Фундамент платформы AICreator
> **Статус**: Research complete
> **Дата**: 2026-04-14

---

## 1. Понимание задачи

### Суть проекта

AICreator — корпоративная платформа кодогенерации для логистической платформы крупной ритейл-компании. Платформа принимает спецификации (Proto, OpenAPI, AsyncAPI) и генерирует готовый к компиляции код на целевых языках с корпоративными стандартами.

### Решаемая проблема

Команды разработки тратят значительное время на бойлерплейт: дата-модели из protobuf, REST-эндпоинты/клиенты, скелеты сервисов. ep02-foundation строит серверную платформу, заменяющую shell-скрипты демо (ep01) на production-ready CLI + API архитектуру.

### Целевая аудитория (первый цикл)

- Go-команда симуляционного моделирования (пилотные пользователи)
- 1 разработчик платформы с Claude Code workflow

### Функциональные требования ep02-foundation

1. **CLI** (typer): команда `generate` с выбором функции (F1/F2/F4), спецификации, языка, output-директории
2. **API** (FastAPI): POST /api/v1/generate (приём файлов), GET /api/v1/generations/{id} (статус/результат)
3. **Orchestrator**: маршрутизация (spec_type, language, function) → конкретный генератор
4. **Generators**: subprocess-вызовы buf, openapi-generator (паттерны из демо)
5. **Post-processor**: format → lint → validate цепочка (gofmt, golangci-lint, go build)
6. **DB**: PostgreSQL — история генераций с input_hash для детерминизма
7. **Docker**: контейнеризированный деплой через Docker Compose

### Scope ограничения

- Только Go в первом цикле (multi-language by design)
- Только F1 (Proto → Go) и F2 (OpenAPI → Go server) и F4 (OpenAPI → Go client)
- Без SSO, Web UI, Celery, Redis
- Без AI-генерации (F3 — Фаза 3 по master-plan)
- Синхронный subprocess для MVP

---

## 2. Анализ рынка и существующих решений

### Существующие инструменты кодогенерации

| Инструмент | Подход | Сильные стороны | Слабые стороны |
|---|---|---|---|
| **buf** (13k+ ⭐) | Proto → код, managed plugins | Современный toolchain, BSR, lint | Только protobuf, нет REST |
| **openapi-generator** (23k+ ⭐) | OpenAPI → 50+ языков | Широкое покрытие, кастомные шаблоны | JRE-зависимость, объёмный output |
| **gRPC Gateway** (18k+ ⭐) | Proto → REST proxy | Единый источник истины | Тесная связь proto↔REST |
| **Swagger Codegen** (17k+ ⭐) | OpenAPI → код | Зрелый, SmartBear backing | Медленнее openapi-generator |
| **Speakeasy** | OpenAPI → SDK | Качественный output, type-safe | Коммерческий, cloud-only |
| **Buf Schema Registry** | Управление proto-схемами | Версионирование, breaking change detection | SaaS, не работает в изоляции |

### Что отсутствует на рынке

1. **Единая платформа** для Proto + OpenAPI + AsyncAPI с оркестрацией
2. **Корпоративная кастомизация** (шаблоны, стандарты, header injection) из коробки
3. **Детерминированная pipeline** с post-processing (format → lint → validate)
4. **On-premise** решение для сетевой изоляции
5. **Аудит** генераций с историей и input hashing

### Выводы из демо (ep01-demo)

18 паттернов задокументированы в `progress.md`. Ключевые для ep02:

| # | Паттерн | Влияние на ep02 |
|---|---------|-----------------|
| 1 | Container paths in configs | Генераторы ожидают абсолютные пути внутри контейнера |
| 5 | buf local plugins (`protoc_builtin`) | BSR требует auth — использовать локальные плагины |
| 7 | openapi-generator shared JAR | Версия 7.12.0 синхронизирована между генераторами |
| 8 | Go enum collision | Enum values в OpenAPI должны быть type-prefixed |
| 10 | ruff generated code | `--unsafe-fixes --ignore=E501,E721` для generated code |
| 12 | Docker Compose one-shot chaining | `service_completed_successfully` для зависимостей |
| 13 | Volume swap specs | Альтернативные спеки должны включать buf.yaml + buf.gen.yaml |

### Pinned tool versions из демо (reference)

| Tool | Version | Image |
|------|---------|-------|
| Go | 1.23 | golang:1.23-alpine |
| buf | 1.50.0 | binary from GitHub |
| openapi-generator | 7.12.0 | JAR from Maven Central |
| golangci-lint | 1.63.4 | binary from GitHub |
| protoc | 29.3 | binary from GitHub |
| JRE | 17 | openjdk17-jre-headless |
| Python | 3.12 | python:3.12-slim |
| ruff | 0.9.10 | pip install |

---

## 3. Рекомендация по технологическому стеку

### Язык и фреймворк

| Компонент | Выбор | Почему | Trade-off | Альтернатива |
|---|---|---|---|---|
| **Язык** | Python 3.12 | AI SDK, FastAPI, быстрое прототипирование | Не самый быстрый runtime | Go (быстрее, но медленнее разработка) |
| **API** | FastAPI 0.115+ (80k+ ⭐) | Async-ready, auto-docs, Pydantic v2 | Нужен uvicorn | Flask (проще, но нет async) |
| **CLI** | typer 0.15+ (16k+ ⭐) | Авто-help, type hints, Rich integration | Привязка к Click | argparse (stdlib, но verbose) |
| **ORM** | SQLAlchemy 2.0 (10k+ ⭐) | Зрелый, sync+async, миграции через Alembic | Тяжеловесный для MVP | SQLModel (проще, но менее гибкий) |
| **Миграции** | Alembic 1.14+ (3k+ ⭐) | Стандарт для SQLAlchemy, autogenerate | Кривая обучения | Вручную (не масштабируется) |
| **Валидация** | Pydantic 2.10+ (21k+ ⭐) | Нативная интеграция с FastAPI | — | attrs (менее удобен с FastAPI) |
| **HTTP-клиент** | httpx 0.28+ (13k+ ⭐) | Sync+async, requests-compatible | — | requests (нет async) |
| **Console UI** | Rich 13+ (50k+ ⭐) | Прогресс-бары, цветной вывод, таблицы | — | click.echo (примитивно) |

### Dev-инструменты

| Компонент | Выбор | Почему | Trade-off | Альтернатива |
|---|---|---|---|---|
| **Package mgr** | uv (30k+ ⭐) | 10-100x быстрее pip, lockfile, PEP 621, private index | Молодой проект | poetry (медленнее, свой формат) |
| **Linter** | ruff 0.8+ (35k+ ⭐) | Всё-в-одном: lint+format, Rust-скорость | Молодой | flake8+black (два инструмента) |
| **Type checker** | mypy 1.13+ (19k+ ⭐) | Зрелый, широко поддержан | Медленный | pyright (быстрее, Node-зависимость) |
| **Tests** | pytest 8+ (12k+ ⭐) | Стандарт, плагины, fixtures | — | unittest (stdlib, verbose) |
| **Pre-commit** | pre-commit (13k+ ⭐) | Авто-запуск ruff, mypy перед коммитом | — | Вручную |

### Решение: uv vs poetry vs pip-tools

**Выбор: uv**

| Критерий | uv | poetry | pip-tools |
|---|---|---|---|
| Скорость | 10-100x быстрее pip | Медленный resolution | Средняя |
| Lockfile | `uv.lock` (кросс-платформенный) | `poetry.lock` | `requirements.txt` |
| pyproject.toml | PEP 621 нативно | Собственный формат | Input only |
| Private index | `UV_INDEX_URL`, конфиг | `[[tool.poetry.source]]` | `--index-url` |
| Offline | `--no-index --find-links` | Частичная | `--no-index` |
| GitHub stars | 30k+ | 31k+ | 8k+ |
| Корп. изоляция | ✅ `UV_INDEX_URL` на внутренний PyPI | ✅ Сложнее конфиг | ✅ Просто |

uv выигрывает по скорости и удобству. Lockfile детерминированный. Private index через env var — идеально для корпоративной сети.

### Все зависимости проходят OSS 700+ Stars Gate (ADR-005) ✅

---

## 4. Архитектура

### Высокоуровневая архитектура

```
┌─────────────┐     HTTP/multipart      ┌──────────────────────────────────┐
│   CLI       │ ──────────────────────►  │         FastAPI Server           │
│   (typer)   │                          │                                  │
│             │  ◄─────────────────────  │  POST /api/v1/generate           │
│   httpx     │     ZIP / JSON           │  GET  /api/v1/generations/{id}   │
└─────────────┘                          │  GET  /api/v1/health             │
                                         └──────────┬───────────────────────┘
                                                    │
                                         ┌──────────▼───────────────────────┐
                                         │       Orchestrator               │
                                         │  Registry: (spec, lang, fn)      │
                                         │         → Generator              │
                                         └──────────┬───────────────────────┘
                                                    │
                                    ┌───────────────┼───────────────────┐
                                    ▼               ▼                   ▼
                             ┌────────────┐  ┌────────────┐     ┌────────────┐
                             │ BufGenerator│  │OpenAPIServer│    │OpenAPIClient│
                             │ (F1: Proto) │  │(F2: REST)  │    │(F4: Client)│
                             │ subprocess  │  │ subprocess  │    │ subprocess  │
                             └──────┬──────┘  └──────┬──────┘    └──────┬─────┘
                                    └───────────┬────┘                  │
                                                ▼                      ▼
                                    ┌───────────────────────────────────────┐
                                    │         Post-Processor                 │
                                    │   format (gofmt) → lint (golangci)    │
                                    │   → validate (go build)               │
                                    └───────────────┬───────────────────────┘
                                                    │
                                    ┌───────────────▼───────────────────────┐
                                    │         PostgreSQL                     │
                                    │   generations, generation_files        │
                                    └───────────────────────────────────────┘
```

### Структура проекта

```
src/aicreator/
├── __init__.py
├── cli/                        # CLI layer (typer)
│   ├── __init__.py
│   ├── app.py                  # typer.Typer() — точка входа CLI
│   ├── commands/
│   │   ├── generate.py         # aicreator generate --function f1 --spec path
│   │   ├── status.py           # aicreator status <generation_id>
│   │   └── config.py           # aicreator config show/set
│   └── output.py               # Rich-форматирование вывода
├── api/                        # API layer (FastAPI)
│   ├── __init__.py
│   ├── app.py                  # FastAPI() — точка входа API
│   ├── routes/
│   │   ├── generate.py         # POST /api/v1/generate
│   │   ├── generations.py      # GET /api/v1/generations/{id}
│   │   └── health.py           # GET /api/v1/health
│   ├── schemas.py              # Pydantic request/response models
│   ├── dependencies.py         # FastAPI Depends (db session, etc.)
│   └── middleware.py           # Request ID, logging
├── core/                       # Business logic (shared CLI ↔ API)
│   ├── __init__.py
│   ├── orchestrator.py         # Registry + routing logic
│   ├── generator.py            # BaseGenerator ABC
│   ├── postprocessor.py        # PostProcessor chain
│   └── config.py               # pydantic-settings: Settings class
├── generators/                 # Concrete generator implementations
│   ├── __init__.py
│   ├── buf.py                  # F1: Proto → Go (buf generate)
│   ├── openapi_server.py       # F2: OpenAPI → Go server
│   └── openapi_client.py       # F4: OpenAPI → Go client
├── db/                         # Database layer
│   ├── __init__.py
│   ├── engine.py               # create_engine, SessionLocal
│   ├── models.py               # SQLAlchemy ORM models
│   └── repository.py           # CRUD operations
└── templates/                  # Generation templates (mustache overrides)
    └── go-server/
        └── partial_header.mustache

tests/
├── conftest.py                 # Shared fixtures
├── unit/
│   ├── test_orchestrator.py
│   ├── test_postprocessor.py
│   └── test_schemas.py
├── integration/
│   ├── test_api_generate.py
│   └── test_generators.py
└── fixtures/
    ├── proto/                  # From demo/specs/proto/
    └── openapi/                # From demo/specs/openapi/

alembic/
├── alembic.ini
├── env.py
└── versions/

docker/
├── Dockerfile                  # Multi-stage: Python + Go toolchain + JRE + buf
├── Dockerfile.dev              # Development with hot reload
└── docker-compose.yml          # API + PostgreSQL

pyproject.toml                  # uv, dependencies, ruff, mypy config
```

### Поток данных

1. **CLI** → читает файлы спецификаций → отправляет multipart POST на API
2. **API** → сохраняет файлы во temp dir → создаёт запись в DB (status=PENDING)
3. **Orchestrator** → по (spec_type, language, function) находит Generator в Registry
4. **Generator** → subprocess.run(buf/openapi-generator) → собирает output из temp dir
5. **PostProcessor** → gofmt → golangci-lint → go build (цепочка, fail fast)
6. **API** → обновляет DB (status=COMPLETED, файлы) → возвращает ZIP или JSON
7. **CLI** → сохраняет файлы в --output директорию → Rich-вывод результата

### Ключевые архитектурные решения

#### File upload: multipart/form-data

```python
@router.post("/api/v1/generate")
async def generate(
    files: list[UploadFile] = File(...),
    metadata: str = Form(...),  # JSON: {"function": "f1", "language": "go", "spec_type": "proto"}
):
```

- Стриминг файлов на диск (не в память)
- Метаданные как JSON в form field
- Base64 отвергнут: +33% к размеру, нет стриминга

#### Response: ZIP для файлов, JSON для статуса

- `POST /api/v1/generate` → `StreamingResponse(ZIP)` с `Content-Disposition: attachment`
- `GET /api/v1/generations/{id}` → JSON с метаданными + ссылка на download
- Отдельный `GET /api/v1/generations/{id}/download` → ZIP

#### SQLAlchemy: sync для MVP

- FastAPI запускает sync-эндпоинты в thread pool — достаточно для единиц запросов/минуту
- Async добавляет сложность без выигрыша при малой нагрузке
- Миграция на async позже: замена `create_engine` → `create_async_engine`

#### Docker: multi-stage build

```dockerfile
# Stage 1: Go toolchain
FROM golang:1.23-alpine AS go-tools
RUN go install golang.org/dl/go1.23@latest
# Install golangci-lint

# Stage 2: buf
FROM alpine AS buf
RUN wget buf v1.50.0

# Stage 3: Runtime
FROM python:3.12-slim
COPY --from=go-tools /usr/local/go /usr/local/go
COPY --from=buf /usr/local/bin/buf /usr/local/bin/buf
RUN apt-get install openjdk-17-jre-headless
# Install openapi-generator JAR
# Install Python app
```

Оценка размера: ~1.5-2 GB (Go toolchain ~500MB, JRE ~200MB, Python ~150MB, tools ~200MB). Приемлемо для on-premise.

---

## 5. Схема базы данных

### generations

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Уникальный идентификатор |
| spec_type | VARCHAR(20) | proto / openapi / asyncapi |
| language | VARCHAR(20) | go (позже: kotlin, python) |
| function | VARCHAR(10) | f1 / f2 / f4 |
| status | VARCHAR(20) | pending / running / completed / failed |
| input_hash | VARCHAR(64) | SHA-256 входных файлов (для детерминизма) |
| created_at | TIMESTAMP | Время создания |
| completed_at | TIMESTAMP | Время завершения |
| duration_ms | INTEGER | Длительность генерации |
| error | TEXT | Сообщение об ошибке (если failed) |
| output_path | VARCHAR(500) | Путь к ZIP-архиву результата |

### generation_files

| Column | Type | Description |
|--------|------|-------------|
| id | UUID (PK) | Уникальный идентификатор |
| generation_id | UUID (FK) | Ссылка на generations |
| path | VARCHAR(500) | Относительный путь файла |
| content_hash | VARCHAR(64) | SHA-256 содержимого |
| size_bytes | INTEGER | Размер файла |

### Индексы

- `generations(input_hash)` — быстрый поиск дубликатов (детерминизм)
- `generations(created_at DESC)` — список последних генераций
- `generation_files(generation_id)` — файлы конкретной генерации

---

## 6. Orchestrator — паттерн Strategy + Registry

```python
# core/generator.py
class BaseGenerator(ABC):
    @abstractmethod
    def validate(self, spec_path: Path) -> ValidationResult: ...

    @abstractmethod
    def generate(self, spec_path: Path, output_dir: Path, config: GeneratorConfig) -> GenerationResult: ...

# core/orchestrator.py
class Orchestrator:
    _registry: dict[tuple[str, str, str], type[BaseGenerator]] = {}

    @classmethod
    def register(cls, spec_type: str, language: str, function: str):
        def decorator(generator_cls):
            cls._registry[(spec_type, language, function)] = generator_cls
            return generator_cls
        return decorator

    def run(self, spec_type, language, function, spec_path, output_dir) -> GenerationResult:
        key = (spec_type, language, function)
        generator_cls = self._registry.get(key)
        if not generator_cls:
            raise UnsupportedCombinationError(key)
        generator = generator_cls()
        generator.validate(spec_path)
        result = generator.generate(spec_path, output_dir, self.config)
        return self.postprocessor.run(result, language)

# generators/buf.py
@Orchestrator.register("proto", "go", "f1")
class BufGoGenerator(BaseGenerator):
    def generate(self, spec_path, output_dir, config):
        subprocess.run(["buf", "generate", ...], check=True)
```

### Post-Processor цепочка

```python
class PostProcessor:
    steps: list[PostProcessStep]  # format, lint, validate

    def run(self, result, language):
        for step in self.steps:
            step_result = step.execute(result.output_dir)
            if step_result.failed and step.severity == "fatal":
                raise PostProcessError(step_result)
            # warning steps: log and continue
```

Go-цепочка (из демо):
1. `gofmt -w` — fatal
2. `golangci-lint run --fix` — warning (best-effort, `|| true` в демо)
3. `go build ./...` — fatal

---

## 7. Стратегия тестирования

### Уровни тестирования

| Уровень | Что тестируем | Инструменты | Coverage target |
|---------|---------------|-------------|-----------------|
| **Unit** | Orchestrator routing, PostProcessor chain, Pydantic schemas, config loading | pytest, unittest.mock | 80%+ |
| **Integration** | API endpoint → Orchestrator → StubGenerator → response | pytest + TestClient (FastAPI) | Ключевые paths |
| **E2E** | CLI → API → Orchestrator → Real Generator → файлы | pytest + subprocess | Happy path + errors |

### Unit-тесты

- **Orchestrator**: правильный routing по (spec_type, language, function), ошибка на неизвестную комбинацию
- **PostProcessor**: цепочка шагов, fatal vs warning, пропуск шагов при ошибке
- **Schemas**: Pydantic validation — валидные/невалидные inputs
- **Subprocess**: mock subprocess.run для генераторов (returncode, stdout, stderr)

### Integration-тесты

```python
# test_api_generate.py
def test_generate_proto_go_f1(client, tmp_path):
    with open("tests/fixtures/proto/order.proto", "rb") as f:
        response = client.post("/api/v1/generate",
            files=[("files", ("order.proto", f))],
            data={"metadata": '{"function":"f1","language":"go","spec_type":"proto"}'}
        )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
```

### Fixtures

- Спецификации из `demo/specs/` — копируются в `tests/fixtures/`
- Невалидные спецификации из `demo/specs-invalid/` — для тестов ошибок

### CI pipeline

```
pre-commit: ruff check + ruff format --check + mypy
PR:         pytest tests/unit/ + pytest tests/integration/
Nightly:    pytest tests/ (full E2E с Docker)
```

---

## 8. Риски, допущения и оценка сложности

### Оценка сложности

| Параметр | Оценка | Комментарий |
|----------|--------|-------------|
| **Техническая сложность** | Medium | Знакомые инструменты, но subprocess orchestration + Docker multi-stage |
| **Time to MVP** | Medium | ~4-6 недель (1 разработчик + Claude Code) |
| **Maintenance burden** | Low-Medium | Python + Docker, стандартный стек |

### Ключевые риски

| Риск | Вероятность | Влияние | Митигация |
|------|-------------|---------|-----------|
| Docker image >3GB | Средняя | Медленный pull, CI | Multi-stage build, alpine bases |
| Subprocess flakiness | Низкая | Нестабильная генерация | Timeout, retry, temp dir isolation |
| Tool version conflicts | Низкая | Build failures | Pinned versions, single Dockerfile |
| uv breaking changes | Низкая | Build failures | Pin uv version, lockfile |

### Допущения

| Допущение | Что ломается если неверно |
|-----------|---------------------------|
| Нагрузка: единицы запросов/минуту | Sync SQLAlchemy не справится → нужен async |
| Один сервер для пилота | Docker Compose достаточно → не нужен K8s |
| Go toolchain + JRE + Python в одном образе | Если >3GB → split на sidecar containers |
| Внутренний PyPI доступен | uv не сможет установить зависимости → vendoring |
| buf и openapi-generator версии стабильны | Breaking changes → pin + тесты |

---

## 9. Обновлённая Конституция (9 принципов)

Текущие 8 принципов из CLAUDE.md адаптированы для продукта (демо → платформа):

### Сохранённые без изменений

> **1. Determinism First**: Identical input must produce identical output, every run. No randomness in deterministic generation functions.
> *Rationale*: Основа доверия к платформе. Input hash в DB подтверждает детерминизм.

> **2. Fail Fast, Fail Loud**: Any step failure (generation, formatting, compilation) stops the pipeline immediately with a clear error message. No silent failures.
> *Rationale*: Быстрая обратная связь критична для developer experience.

> **3. Pinned Versions**: All Docker images and tool versions use explicit tags (e.g., `golang:1.23-alpine`, not `latest`). Reproducibility over convenience.
> *Rationale*: Без pinned versions детерминизм невозможен.

> **4. OSS 700+ Stars Gate**: All external dependencies must have 700+ GitHub stars and active maintenance (per ADR-005).
> *Rationale*: Enterprise-надёжность, снижение риска abandoned dependencies.

### Адаптированные

> **5. Containerized Platform** (было: Docker-Isolated Execution): Platform and all generation tools run inside containers. Host machine needs only Docker.
> *Rationale*: Расширение от "всё в контейнерах" к "платформа — это контейнер". API, генераторы, инструменты — всё containerized.

> **6. Specification Agnostic** (было: Swap Without Change): Adding new specifications must not require code changes to the platform core. Registry pattern routes to the right generator.
> *Rationale*: Переход от volume mount к API — спецификации приходят через HTTP, а не через mount.

> **7. Minimal Infrastructure** (было: Zero Runtime Dependencies): Platform requires only PostgreSQL as external dependency. No message queues, caches, or auxiliary services for MVP.
> *Rationale*: Каждый компонент инфраструктуры — потенциальная точка отказа на пилоте.

> **8. Template-Driven Generation** (было: Minimal Customization): Code generation uses customizable templates for corporate standards (headers, naming, patterns). Templates live in the platform repository.
> *Rationale*: Переход от демо-scope к продукту — шаблоны становятся первоклассным элементом.

### Новый

> **9. Go First, Multi-Language by Design**: First release targets Go only. Architecture supports multiple languages through Strategy + Registry pattern without core changes.
> *Rationale*: Фокус на одном языке для быстрого пилота. Архитектура не блокирует добавление Kotlin, Python позже.

---

## 10. Рекомендуемые следующие шаги

### MVP scope (ep02-foundation)

**Wave 1: Skeleton + DB** (T01-T04)
- Структура Python-проекта с uv
- pyproject.toml с зависимостями
- FastAPI app skeleton + health endpoint
- PostgreSQL schema + Alembic migrations (сразу в skeleton)
- Docker Compose (api + postgres)

**Wave 2: Core** (T05-T08)
- Orchestrator с Registry pattern
- BaseGenerator + BufGoGenerator (F1)
- OpenAPIServerGenerator (F2) + OpenAPIClientGenerator (F4)
- PostProcessor chain (gofmt → golangci-lint → go build)

**Wave 3: API endpoints** (T09-T11)
- POST /api/v1/generate (multipart upload + DB запись)
- GET /api/v1/generations/{id} + download
- CLI skeleton с typer (generate, status)

**Wave 4: Integration + Docker** (T12-T14)
- CLI generate command → API
- E2E тесты
- Multi-stage Dockerfile

### Закрытые вопросы (решения от 2026-04-14)

1. **Database**: ✅ PostgreSQL сразу (не SQLite) — production-ready с первого дня
2. **Конфигурация генераторов**: ✅ Dataclasses (Pydantic) — type-safe, YAML только для tool-specific config (buf.gen.yaml, go-server.yaml)
3. **Версии инструментов**: ✅ Сохранить демо-версии (buf 1.50.0, openapi-generator 7.12.0, Go 1.23) — обновление отдельным тикетом
4. **DB timing**: ✅ PostgreSQL с Wave 1 (skeleton) — все endpoints пишут историю с первого дня
