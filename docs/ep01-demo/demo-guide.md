# Demo Guide: AICreator ep01-demo

Инструкция по настройке и проведению живого демо для CTO.

---

## 1. Что это

AICreator ep01-demo — демонстрация детерминистической кодогенерации из спецификаций (Proto, OpenAPI) в три языка: **Kotlin**, **Go**, **Python**.

Ключевые свойства:
- **Одна команда** (`docker compose up`) генерирует ~300 файлов компилируемого кода
- **Детерминизм** — идентичный вход всегда даёт идентичный выход (побайтово)
- **Docker-изоляция** — на хосте нужен только Docker Desktop и Git, никаких SDK
- **Fail Fast** — ошибка в спецификации мгновенно останавливает pipeline
- **Swap Without Change** — замена входных спек не требует изменения ни одного скрипта

---

## 2. Архитектура pipeline

### Общая схема

```
Входные спеки (Proto + OpenAPI)
        │
        ▼
┌─── Волна 1: Генерация (параллельно) ───┐
│  F1: Proto → Kotlin (buf + protoc)      │
│  F2: OpenAPI → Go (openapi-generator)   │
│  F4: OpenAPI → Python (openapi-generator)│
└─────────────────────────────────────────┘
        │
        ▼
┌─── Волна 2: Форматирование (параллельно) ─┐
│  Kotlin: ktlint                            │
│  Go: gofmt + golangci-lint                 │
│  Python: ruff                              │
└────────────────────────────────────────────┘
        │
        ▼
┌─── Волна 3: Валидация (параллельно) ──────┐
│  Kotlin: javac + kotlinc (компиляция)      │
│  Go: go build (компиляция)                 │
│  Python: compileall (синтаксис)            │
└────────────────────────────────────────────┘
        │
        ▼
    generated/
    ├── kotlin/  (~128 файлов: .java + .kt)
    ├── go/      (~39 файлов: .go)
    └── python/  (~140 файлов: .py)
```

### 9 Docker-сервисов

Pipeline оркестрирован через Docker Compose с `depends_on: service_completed_successfully`:

| Волна | Сервис | Инструмент | Dockerfile |
|-------|--------|------------|------------|
| 1 | `f1-kotlin` | buf 1.50.0 + protoc 29.3 | Dockerfile.kotlin (JDK 21) |
| 1 | `f2-go` | openapi-generator 7.12.0 | Dockerfile.go (Go 1.23) |
| 1 | `f4-python` | openapi-generator 7.12.0 | Dockerfile.python (Python 3.12) |
| 2 | `format-kotlin` | ktlint 1.5.0 | Dockerfile.kotlin |
| 2 | `format-go` | gofmt + golangci-lint 1.63.4 | Dockerfile.go |
| 2 | `format-python` | ruff 0.9.10 | Dockerfile.python |
| 3 | `validate-kotlin` | javac + kotlinc 2.1.10 | Dockerfile.kotlin |
| 3 | `validate-go` | go build | Dockerfile.go |
| 3 | `validate-python` | python3 compileall | Dockerfile.python |

Все версии инструментов **зафиксированы** (pinned) — ни одного тега `:latest`.

### Входные спецификации (домен: логистика)

**Proto** (пакет `logistics.v1`):
- `Order` — заказ (customer_id, items, status, адрес доставки)
- `Shipment` — отправка (маршрут, трекинг, статус)
- `Warehouse` — склад (адрес, координаты, inventory)
- `Common` — общие типы (Address, Coordinates)
- 3 gRPC-сервиса с CRUD-операциями (15 RPC-методов)

**OpenAPI 3.0.3** (Logistics API):
- 11 REST-эндпоинтов (Orders, Shipments, Warehouses)
- ~20 схем (модели данных, запросы, ответы, ошибки)

---

## 3. Подготовка рабочего Mac

### Требования

- **Docker Desktop** для macOS (запущен, иконка в меню-баре)
- **Git**
- **Терминал** (Terminal.app или iTerm2)
- Интернет (для скачивания Docker images при первой сборке)

### Шаг 1: Клонировать репозиторий

```bash
git clone https://github.com/petrorossolov-rgb/aicreator.git
cd aicreator/demo
```

### Шаг 2: Предварительная сборка (сделать заранее!)

Первая сборка скачивает base images и инструменты (~2 ГБ). Это занимает 5-10 минут.

```bash
docker compose build
```

### Шаг 3: Проверочный запуск

```bash
docker compose up
```

Убедись, что все 9 сервисов завершились с exit code 0. После этого демо готово к показу.

> **Важно:** Прогони полный цикл **до встречи с CTO**. На демо сборка не нужна — образы уже закешированы.

---

## 4. Сценарий демо

### Перед началом

```bash
cd AICreator/demo
rm -rf generated/*    # чистый старт
```

Открой терминал на полный экран, увеличь шрифт (Cmd+).

---

### Акт 1: Happy Path — "Одна команда → 300 файлов кода"

**Команда:**
```bash
docker compose up
```

**Что происходит в терминале** (комментируй по ходу):

1. **Волна 1** — запускаются `f1-kotlin`, `f2-go`, `f4-python` параллельно:
   > "Сейчас три контейнера одновременно генерируют код из наших спек. Kotlin из Proto через buf, Go и Python из OpenAPI через openapi-generator."

2. **Волна 2** — форматирование, после завершения генерации:
   > "Код сгенерирован, теперь форматируется: ktlint для Kotlin, gofmt для Go, ruff для Python. Всё автоматически."

3. **Волна 3** — валидация, после завершения форматирования:
   > "Финальный шаг — компиляция. Kotlin и Go компилируются, Python проходит syntax check. Если что-то не скомпилируется — pipeline упадёт."

4. **Все 9 сервисов завершились с exit 0:**
   > "Готово. Давай посмотрим, что получилось."

**Показать результат:**

```bash
# Общая картина
find generated -type f | wc -l

# Структура по языкам
find generated/kotlin -name "*.kt" | wc -l
find generated/go -name "*.go" | wc -l
find generated/python -name "*.py" | wc -l
```

**Показать примеры файлов:**

```bash
# Kotlin — protobuf DSL для создания объекта Order
head -20 generated/kotlin/com/logistics/v1/OrderKt.kt

# Go — REST контроллер с corporate header
head -20 generated/go/src/api_orders.go

# Python — API-клиент с типизацией (pydantic)
head -15 generated/python/logistics_client/api/orders_api.py
```

**Ключевое сообщение:**
> "Из двух файлов спецификаций — Proto и OpenAPI — мы получили 300+ файлов компилируемого, отформатированного кода на трёх языках. Одной командой, в Docker, без установки SDK на хост."

---

### Акт 2: Volume Swap — "Другие спеки, ноль изменений"

**Контекст для CTO:**
> "А что если нужно сгенерировать код для другого домена? Другие сущности, другой пакет. Покажу."

**Команда:**
```bash
rm -rf generated/*
SPECS_DIR=./specs-alt docker compose up
```

**Что показать:**

```bash
# Было: logistics.v1.Order, Shipment, Warehouse
# Стало: catalog.v1.Product
find generated/kotlin -name "*.kt" | head -5
head -20 generated/kotlin/com/catalog/v1/ProductKt.kt
```

**Ключевое сообщение:**
> "Мы подменили входные спецификации через переменную окружения `SPECS_DIR`. Ни один скрипт, Dockerfile или конфиг не менялся. Это принцип Swap Without Change — volume mount как единственный механизм замены."

---

### Акт 3: Fail Fast — "Битая спека → мгновенная остановка"

**Контекст для CTO:**
> "Что будет, если кто-то сломает спецификацию? Pipeline должен упасть быстро и громко."

**Команда:**
```bash
rm -rf generated/*
SPECS_DIR=./specs-invalid docker compose up
```

**Что произойдёт:**
- `f1-kotlin` упадёт с ошибкой: `broken.proto:7:3: Expected ";"`
- `f2-go` и `f4-python` упадут: `attribute paths is missing`
- Форматирование и валидация **не запустятся** (`depends_on: service_completed_successfully`)

**Что показать:**

```bash
# Показать битый proto-файл
cat specs-invalid/proto/broken.proto
```

> "Видишь — пропущена точка с запятой на 6-й строке. Pipeline остановился на первой волне с чётким сообщением. Не потратил время на форматирование или компиляцию. Это принцип Fail Fast, Fail Loud."

---

### После трёх актов: обзор кода

Вернись к результатам Акта 1 (или запусти заново с `docker compose up`).

Открой в редакторе (VS Code, если есть) три файла:

| Файл | Что показать |
|------|-------------|
| `generated/kotlin/com/logistics/v1/OrderKt.kt` | Kotlin DSL: type-safe builder для protobuf-объекта `Order` |
| `generated/go/src/api_orders.go` | Go REST controller: header "Copyright X5 Group", interface-based architecture, Gorilla mux router |
| `generated/python/logistics_client/api/orders_api.py` | Python API client: pydantic-валидация, полная типизация, ready-to-use HTTP-клиент |

> "Это не болванки. Каждый файл проходит форматирование по стандартам языка и компиляцию. Corporate header добавляется через mustache-шаблон — единственная кастомизация."

---

## 5. Быстрая справка по командам

| Действие | Команда |
|----------|---------|
| Полный pipeline | `docker compose up` |
| С пересборкой образов | `docker compose up --build` |
| Другие спеки | `SPECS_DIR=./specs-alt docker compose up` |
| Тест на ошибки | `SPECS_DIR=./specs-invalid docker compose up` |
| Только Kotlin | `docker compose up f1-kotlin format-kotlin validate-kotlin` |
| Очистка результатов | `rm -rf generated/*` |
| Остановка контейнеров | `docker compose down` |

---

## 6. Troubleshooting

| Проблема | Решение |
|----------|---------|
| `Cannot connect to the Docker daemon` | Запусти Docker Desktop, дождись иконки в меню-баре |
| Первый запуск очень долгий | Нормально — скачиваются base images (~2 ГБ). Повторные запуски быстрые |
| Сервис завис | `docker compose down && docker compose up` |
| `permission denied` на скриптах | `chmod +x scripts/*.sh` |
| Ошибки сети при сборке | Проверь интернет-соединение, Docker использует GitHub и Maven Central |
| `no space left on device` | `docker system prune -a` (удалит все неиспользуемые образы) |
