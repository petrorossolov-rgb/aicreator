# AICreator ep02-foundation: Результаты

## Что реализовано

AICreator -- платформа детерминистичной генерации кода. ep02-foundation поставляет production-ready CLI и API для генерации Go-кода из Proto и OpenAPI спецификаций.

### Функции генерации

| Функция | Вход | Выход | Инструмент | Кол-во файлов |
|---------|------|-------|------------|---------------|
| **F1** | `.proto` файлы | Go structs + gRPC stubs | buf 1.50.0 + protoc 29.3 | ~7 |
| **F2** | OpenAPI 3.x `.yaml` | Go server stubs | openapi-generator 7.12.0 | ~38 |
| **F4** | OpenAPI 3.x `.yaml` | Go client library | openapi-generator 7.12.0 | ~59 |

### Ключевые свойства

- **Детерминизм**: идентичный вход всегда даёт идентичный выход (проверяется через `input_hash` в БД)
- **Контейнеризация**: на хост-машине нужен только Docker -- никакого Go, Java или Python
- **Fail Fast**: любой сбой генерации/форматирования/компиляции немедленно останавливает процесс с понятным сообщением
- **Спецификация-агностик**: добавление нового типа спецификации требует только новый класс генератора + запись в реестре

---

## Архитектура

```
CLI (typer)                         API (FastAPI)
    |                                    |
    +--- HTTP POST /api/v1/generate -----+
                                         |
                                    Orchestrator
                                    (паттерн Registry)
                                         |
                    +--------------------+--------------------+
                    |                    |                    |
              BufGoGenerator    OpenAPIServerGen    OpenAPIClientGen
              (proto,go,f1)     (openapi,go,f2)    (openapi,go,f4)
                    |                    |                    |
               buf generate     java -jar openapi-  java -jar openapi-
                                generator-cli.jar   generator-cli.jar
                                -g go-server        -g go
                                         |
                                    PostProcessor
                                    (gofmt + golangci-lint + go build)
                                         |
                                    ZIP-ответ
                                    + запись в БД (input_hash, status, duration)
```

### Поток обработки запроса

1. Пользователь вызывает `aicreator generate -f f1 -s ./specs -o ./output -l go`
2. CLI читает файлы спецификаций, загружает в API как multipart form
3. API сохраняет файлы во временную директорию, вычисляет SHA-256 `input_hash`
4. Orchestrator ищет ключ `(spec_type, language, function)` в реестре
5. Найденный генератор выполняет: validate -> generate -> post-process
6. Результат: ZIP-архив возвращается в CLI, извлекается в output-директорию
7. Запись о генерации сохраняется в PostgreSQL (id, status, hash, duration)

---

## Карта кода

```
src/aicreator/
|-- __init__.py                          # Версия пакета
|-- api/
|   |-- app.py                           # Фабрика FastAPI-приложения
|   |-- dependencies.py                  # DI: get_db, get_orchestrator
|   |-- middleware.py                     # Request ID middleware
|   |-- schemas.py                       # Pydantic-модели (GenerateRequest)
|   |-- routes/
|       |-- generate.py                  # POST /api/v1/generate
|       |-- generations.py               # GET /api/v1/generations/{id}
|       |-- health.py                    # GET /api/v1/health
|
|-- cli/
|   |-- app.py                           # Typer-приложение, регистрация команд
|   |-- output.py                        # Форматирование вывода (Rich)
|   |-- commands/
|       |-- generate.py                  # Команда `aicreator generate`
|       |-- health.py                    # Команда `aicreator health`
|       |-- status.py                    # Команда `aicreator status`
|
|-- core/
|   |-- config.py                        # Настройки (Pydantic-settings)
|   |-- generator.py                     # BaseGenerator, GeneratorConfig, модели результатов
|   |-- logging.py                       # Структурированное JSON-логирование
|   |-- orchestrator.py                  # Маршрутизация по паттерну Registry
|   |-- postprocessor.py                 # Цепочка: gofmt + golangci-lint + go build
|
|-- db/
|   |-- engine.py                        # SQLAlchemy engine + SessionLocal
|   |-- models.py                        # ORM-модель Generation
|   |-- repository.py                    # CRUD-операции
|
|-- generators/
    |-- __init__.py                      # Авто-импорт для срабатывания @register
    |-- buf.py                           # F1: Proto -> Go (buf CLI)
    |-- openapi_base.py                  # Общая валидация + subprocess для OpenAPI
    |-- openapi_server.py                # F2: OpenAPI -> Go Server
    |-- openapi_client.py                # F4: OpenAPI -> Go Client
```

### Инфраструктура

```
docker/
|-- Dockerfile                           # Production multi-stage (Python + Go + Java + инструменты)
|-- Dockerfile.dev                       # Dev (только Python, hot-reload)
|-- docker-compose.yml                   # PostgreSQL + API сервисы
|-- entrypoint.sh                        # Dev entrypoint (миграции + uvicorn)
|-- entrypoint.prod.sh                   # Prod entrypoint (миграции + uvicorn workers)

alembic/
|-- versions/
    |-- 2089e8373d0d_initial_generations_table.py   # Миграция БД

tests/
|-- fixtures/
|   |-- proto/                           # Примеры .proto спецификаций (логистический домен)
|   |-- openapi/                         # Пример OpenAPI спецификации (logistics.yaml)
|-- e2e/                                 # End-to-end тесты
|-- unit/                                # Unit-тесты
```

---

## Принципы конституции в коде

| # | Принцип | Реализация |
|---|---------|-----------|
| 1 | Детерминизм | `input_hash` (SHA-256) вычисляется при загрузке, хранится в БД |
| 2 | Контейнеризация | Multi-stage Dockerfile: Go 1.23 + Python 3.12 + JRE 21 + buf + protoc |
| 3 | Fail Fast | Цепочка PostProcessor: gofmt -> golangci-lint -> go build; любой сбой = ошибка |
| 4 | Спецификация-агностик | Декоратор `@Orchestrator.register(spec_type, language, function)` |
| 5 | Фиксированные версии | Все Docker-образы + инструменты с явными тегами (buf 1.50.0, protoc 29.3 и т.д.) |
| 6 | Минимальная инфраструктура | Только PostgreSQL, без Redis/RabbitMQ/Celery |
| 7 | Шаблонная генерация | buf.gen.yaml / openapi-generator шаблоны в директории спецификаций |
| 8 | OSS 700+ звёзд | FastAPI (80k), typer (16k), SQLAlchemy (10k), buf (13k), openapi-generator (23k) |
| 9 | Go First, Multi-Language | Registry поддерживает любой кортеж `(spec_type, language, function)` |

---

## Следующие шаги

1. **F3: AI-генерация (PUML -> Go-сервисы)** -- интеграция litellm + on-prem LLM (Qwen 3 235B) для генерации Go-сервисов из PlantUML-диаграмм. ADR-003 и ADR-004 уже приняты.

2. **Multi-language** -- расширить Registry генераторами для Kotlin и Python. Архитектура уже поддерживает это через Strategy-паттерн.

3. **CI/CD интеграция** -- создать плагины для GitHub Actions / GitLab CI, вызывающие API напрямую из пайплайнов.

---

## Для команды симуляции

### Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone <repo-url>
cd AICreator

# 2. Запустить платформу (нужен только Docker!)
docker compose -f docker/docker-compose.yml --profile prod up -d --build

# 3. Дождаться готовности сервисов
docker compose -f docker/docker-compose.yml --profile prod logs -f api-prod
# Ждите строку: "Application startup complete"

# 4. Установить CLI на хост-машину
pip install -e .
# или через uv:
uv pip install -e .

# 5. Проверить работоспособность
aicreator health
# OK API healthy -- version 0.1.0
```

### Команды CLI

#### Генерация кода

```bash
# F1: Proto -> Go structs + gRPC
aicreator generate -f f1 -s /path/to/proto/specs -o ./output/f1 -l go

# F2: OpenAPI -> Go server stubs
aicreator generate -f f2 -s /path/to/openapi/specs -o ./output/f2 -l go

# F4: OpenAPI -> Go client library
aicreator generate -f f4 -s /path/to/openapi/specs -o ./output/f4 -l go
```

**Параметры:**
- `-f, --function` -- функция генерации: `f1`, `f2` или `f4`
- `-s, --spec` -- путь к файлу или директории со спецификациями
- `-o, --output` -- директория для сгенерированного кода
- `-l, --language` -- целевой язык (по умолчанию: `go`)
- `--api-url` -- базовый URL API (по умолчанию: `http://localhost:8000`)

#### Статус генерации

```bash
aicreator status <generation-id>
```

Отображает: функцию, язык, тип спецификации, статус, input hash, длительность.

#### Проверка здоровья

```bash
aicreator health
```

### Подключение своих спецификаций

Флаг `--spec` (`-s`) принимает как **файл**, так и **директорию**:

**Для Proto спецификаций (F1):**
```
your-specs/
|-- buf.yaml              # Обязательно: конфиг модуля buf (version: v2)
|-- buf.gen.go.yaml       # Обязательно: шаблон генерации
|-- service.proto         # Ваши .proto файлы
|-- models.proto
```

Пример `buf.gen.go.yaml`:
```yaml
version: v2
plugins:
  - local: protoc-gen-go
    out: /generated/go
    opt: paths=source_relative
  - local: protoc-gen-go-grpc
    out: /generated/go
    opt: paths=source_relative
```

Proto-файлы должны содержать `option go_package`:
```protobuf
syntax = "proto3";
package your.package.v1;
option go_package = "your/package/v1";
```

**Для OpenAPI спецификаций (F2, F4):**
```
your-specs/
|-- api.yaml              # OpenAPI 3.x спецификация
```

Спецификация должна быть валидным OpenAPI 3.x YAML-файлом с ключом `openapi`.

### API-эндпоинты

Для интеграции в скрипты и CI-пайплайны:

```bash
# Генерация кода
curl -X POST http://localhost:8000/api/v1/generate \
  -F "files=@logistics.yaml" \
  -F 'metadata={"function":"f2","language":"go","spec_type":"openapi"}' \
  -o output.zip

# Статус генерации
curl http://localhost:8000/api/v1/generations/<id>

# Проверка здоровья
curl http://localhost:8000/api/v1/health
```
