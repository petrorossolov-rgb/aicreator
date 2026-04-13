# Demo Guide: AICreator ep01-demo

Инструкция по настройке и проведению живого демо для CTO.

---

## 1. Что это

AICreator ep01-demo — демонстрация детерминистической кодогенерации из спецификаций (Proto, OpenAPI) в три языка: **Kotlin**, **Go**, **Python**.

Ключевые свойства:
- **Одна команда** (`docker compose up`) генерирует ~307 файлов компилируемого кода
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
    ├── kotlin/  (~127 файлов: .java + .kt)
    ├── go/      (~31 файлов: .go)
    └── python/  (~52 файлов: .py)
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

Все спецификации лежат в `demo/specs/`:

```
specs/
├── proto/                          ← Protobuf (для F1: Kotlin)
│   ├── buf.yaml                    ← конфиг модуля buf
│   ├── buf.gen.yaml                ← конфиг генерации (плагины, выходная папка)
│   ├── common.proto                ← общие типы: Address, Coordinates
│   ├── order.proto                 ← заказы: Order, OrderItem, OrderService
│   ├── shipment.proto              ← отправки: Shipment, ShipmentItem, ShipmentService
│   └── warehouse.proto             ← склады: Warehouse, InventoryItem, WarehouseService
└── openapi/                        ← OpenAPI (для F2: Go и F4: Python)
    └── logistics.yaml              ← REST API: 11 эндпоинтов, 18 схем
```

#### Proto-файлы (вход для F1: Kotlin)

**`buf.yaml`** — конфиг модуля. Говорит buf, что текущая директория — модуль `buf.build/logistics/v1`. Включает стандартные правила линтинга и проверки обратной совместимости.

**`buf.gen.yaml`** — конфиг генерации. Описывает что генерировать и куда:
- плагин `protoc_builtin: java` → Java-классы (базовые protobuf-классы) в `/generated/kotlin`
- плагин `protoc_builtin: kotlin` → Kotlin DSL-обёртки (type-safe builders) в `/generated/kotlin`

Оба плагина кладут результат в одну папку, потому что Kotlin DSL зависит от Java-классов.

**`common.proto`** — общие типы, пакет `logistics.v1`:
- **Address** — физический адрес: street, city, region, postal_code, country
- **Coordinates** — гео-координаты: latitude, longitude

Импортируется в остальные три proto-файла.

**`order.proto`** — заказы, пакет `logistics.v1`:
- **OrderStatus** (enum) — 7 состояний: UNSPECIFIED → CREATED → CONFIRMED → PICKING → SHIPPED → DELIVERED / CANCELLED
- **Order** — заказ: order_id, customer_id, shipping_address (Address), items (repeated OrderItem), status, created_at, updated_at
- **OrderItem** — строка заказа: sku, name, quantity, price_cents
- **OrderService** — 5 RPC: CreateOrder, GetOrder, ListOrders, UpdateOrder, DeleteOrder

**`shipment.proto`** — отправки, пакет `logistics.v1` (самый сложный, 95 строк):
- **ShipmentStatus** (enum) — 6 состояний: UNSPECIFIED → PENDING → IN_TRANSIT → OUT_FOR_DELIVERY → DELIVERED / RETURNED
- **Location** — точка трекинга: name, address (Address), coordinates (Coordinates), timestamp
- **Shipment** — отправка: shipment_id, order_id, warehouse_id, origin, destination, items, status, tracking_history (repeated Location)
- **ShipmentItem** — строка отправки: sku, quantity, weight_kg
- **ShipmentService** — 5 RPC: CreateShipment, GetShipment, ListShipments, UpdateShipment, DeleteShipment

**`warehouse.proto`** — склады, пакет `logistics.v1`:
- **Warehouse** — склад: warehouse_id, name, address (Address), coordinates (Coordinates), inventory (repeated InventoryItem)
- **InventoryItem** — позиция на складе: sku, name, quantity_on_hand, quantity_reserved, reorder_point
- **WarehouseService** — 5 RPC: CreateWarehouse, GetWarehouse, ListWarehouse, UpdateWarehouse, DeleteWarehouse

**Итого Proto:** 4 доменных файла, 3 gRPC-сервиса, 15 RPC-методов, 8 message-типов, 2 enum.

#### OpenAPI-файл (вход для F2: Go и F4: Python)

**`logistics.yaml`** — OpenAPI 3.0.3, 536 строк. Описывает REST API для того же домена.

**Эндпоинты (11 штук):**

| Метод | Путь | Операция | Тег |
|-------|------|----------|-----|
| POST | `/orders` | createOrder | Orders |
| GET | `/orders` | listOrders | Orders |
| GET | `/orders/{orderId}` | getOrder | Orders |
| PUT | `/orders/{orderId}` | updateOrder | Orders |
| DELETE | `/orders/{orderId}` | deleteOrder | Orders |
| GET | `/shipments` | listShipments | Shipments |
| GET | `/shipments/{shipmentId}` | getShipment | Shipments |
| GET | `/shipments/{shipmentId}/track` | trackShipment | Shipments |
| GET | `/warehouses` | listWarehouses | Warehouses |
| GET | `/warehouses/{warehouseId}` | getWarehouse | Warehouses |
| PATCH | `/warehouses/{warehouseId}/inventory/{sku}` | updateInventory | Warehouses |

**Схемы (18 штук):**
- Модели: Address, Location, Order, OrderItem, OrderStatus, Shipment, ShipmentItem, ShipmentStatus, Warehouse, InventoryItem, TrackingHistory
- Списки: OrderList, ShipmentList, WarehouseList
- Запросы: CreateOrderRequest, UpdateOrderRequest, UpdateInventoryRequest
- Ошибки: Error (code + message)
- Параметры: Limit (1-100, default 20), Offset (min 0) — переиспользуемые для пагинации

#### Как Proto и OpenAPI связаны

Они описывают **один и тот же домен** (логистика) с двух сторон:
- **Proto** → gRPC-контракты → генерирует **Kotlin** (модели + сервисные интерфейсы)
- **OpenAPI** → REST-контракты → генерирует **Go** (сервер с handlers) и **Python** (клиентскую библиотеку)

Сущности совпадают (Order, Shipment, Warehouse, Address), но форматы разные (proto3 vs OpenAPI 3.0.3), потому что это разные протоколы.

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

### Подготовка к тестовому прогону

```bash
cd aicreator/demo
```

Убедись, что Docker Desktop запущен:
```bash
docker info > /dev/null 2>&1 && echo "Docker OK" || echo "Docker НЕ запущен!"
```
Ожидаемый результат: `Docker OK`

---

### Акт 1: Happy Path — "Одна команда → 300 файлов кода"

#### Шаг 1.1: Очистка предыдущих результатов

```bash
rm -rf generated/*
```

Проверь, что директория пуста:
```bash
ls generated/
```
Ожидаемый результат: пустой вывод (ничего не выводится).

#### Шаг 1.2: Запуск pipeline

```bash
docker compose up
```

#### Шаг 1.3: Что ты увидишь в терминале (по порядку)

**Волна 1 — Генерация** (три сервиса стартуют одновременно):

Логи перемешаны, но ищи эти маркеры:

```
f1-kotlin-1   | === F1 Kotlin: buf generate ===
f1-kotlin-1   | Specs: /specs/proto
f1-kotlin-1   | Output: /generated/kotlin
```
```
f2-go-1       | === F2 Go: openapi-generator generate ===
f2-go-1       | Spec: /specs/openapi/logistics.yaml
```
```
f4-python-1   | === F4 Python: openapi-generator generate ===
f4-python-1   | Spec: /specs/openapi/logistics.yaml
```

Генерация занимает 10-30 секунд. openapi-generator выводит много технических строк — это нормально. Финальные маркеры успеха волны 1:

```
f1-kotlin-1   | === Generated 127 file(s) in /generated/kotlin ===
f1-kotlin-1 exited with code 0
f2-go-1       | === Generated 31 Go file(s) in /generated/go ===
f2-go-1 exited with code 0
f4-python-1   | === Generated 52 Python file(s) in /generated/python ===
f4-python-1 exited with code 0
```

> Числа файлов могут незначительно отличаться. Главное — `exited with code 0` у всех трёх.

**Волна 2 — Форматирование** (стартует автоматически после волны 1):

```
format-kotlin-1  | === Kotlin: ktlint format ===
format-kotlin-1  | === Kotlin format complete (43 .kt files) ===
format-kotlin-1 exited with code 0

format-go-1      | === Go: gofmt + golangci-lint format ===
format-go-1      | === Go format complete (31 .go files) ===
format-go-1 exited with code 0

format-python-1  | === Python: ruff format + check ===
format-python-1  | 49 files reformatted, 3 files left unchanged
format-python-1  | Found 173 errors (173 fixed, 0 remaining).
format-python-1  | === Python format complete (52 .py files) ===
format-python-1 exited with code 0
```

> ktlint и ruff могут вывести информационные строки о найденных и исправленных проблемах — это нормально, они авто-фиксятся.

**Волна 3 — Валидация** (стартует автоматически после волны 2):

```
validate-kotlin-1  | === Kotlin: compilation validation ===
validate-kotlin-1  | Compiling Java sources...
validate-kotlin-1  | Compiling Kotlin sources...
validate-kotlin-1  | === Kotlin validation passed ===
validate-kotlin-1 exited with code 0

validate-go-1      | === Go: build validation ===
validate-go-1      | === Go validation passed ===
validate-go-1 exited with code 0

validate-python-1  | === Python: syntax validation ===
validate-python-1  | === Python validation passed ===
validate-python-1 exited with code 0
```

> kotlinc — самый медленный шаг (~20-40 сек). Может вывести предупреждения (w:) — они фильтруются. Главное — `validation passed` и `exited with code 0`.

**Финальная строка Docker Compose:**

Когда все 9 сервисов завершатся, ты увидишь итоговый блок вида:
```
 ✔ Container demo-f1-kotlin-1        Exited
 ✔ Container demo-f2-go-1            Exited
 ✔ Container demo-f4-python-1        Exited
 ✔ Container demo-format-kotlin-1    Exited
 ✔ Container demo-format-go-1        Exited
 ✔ Container demo-format-python-1    Exited
 ✔ Container demo-validate-kotlin-1  Exited
 ✔ Container demo-validate-go-1      Exited
 ✔ Container demo-validate-python-1  Exited
```

> Если хотя бы один сервис показал `exited with code 1` — что-то пошло не так. Смотри секцию Troubleshooting.

#### Шаг 1.4: Проверка результатов

Подсчёт сгенерированных файлов:
```bash
find generated -type f | wc -l
```
Ожидаемый результат: **307** файлов.

Разбивка по языкам:
```bash
echo "Kotlin .kt:   $(find generated/kotlin -name '*.kt' | wc -l)"
echo "Kotlin .java:  $(find generated/kotlin -name '*.java' | wc -l)"
echo "Go .go:        $(find generated/go -name '*.go' | wc -l)"
echo "Python .py:    $(find generated/python -name '*.py' | wc -l)"
```
Ожидаемый результат:
```
Kotlin .kt:   43
Kotlin .java:  84
Go .go:        31
Python .py:    52
```

#### Шаг 1.5: Просмотр сгенерированного кода

**Kotlin** — protobuf DSL builder для объекта Order:
```bash
head -20 generated/kotlin/com/logistics/v1/OrderKt.kt
```
Ожидаемый вывод — Kotlin DSL с type-safe builder:
```kotlin
// Generated by the protocol buffer compiler. DO NOT EDIT!
// NO CHECKED-IN PROTOBUF GENCODE
// source: order.proto

// Generated files should ignore deprecation warnings
@file:Suppress("DEPRECATION")

package com.logistics.v1

@kotlin.jvm.JvmName("-initializeorder")
public inline fun order(block: com.logistics.v1.OrderKt.Dsl.() -> kotlin.Unit): ...
```

**Go** — REST controller с корпоративным header:
```bash
head -20 generated/go/src/api_orders.go
```
Ожидаемый вывод — Go handler с header "Copyright X5 Group":
```go
// Copyright (c) 2026 X5 Group. Generated by AICreator.
// DO NOT EDIT — this file was auto-generated from OpenAPI specification.

package logistics

import (
	"encoding/json"
	"net/http"
	"strings"

	"github.com/gorilla/mux"
)

// OrdersAPIController binds http requests to an api service...
type OrdersAPIController struct {
```

**Python** — API-клиент с pydantic-типизацией:
```bash
head -15 generated/python/logistics_client/api/orders_api.py
```
Ожидаемый вывод — Python client с импортами pydantic:
```python
# coding: utf-8

# Copyright (c) 2026 X5 Group. Generated by AICreator.
# DO NOT EDIT — this file was auto-generated from OpenAPI specification.

from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from logistics_client.models.create_order_request import CreateOrderRequest
from logistics_client.models.order import Order
```

> **На что обратить внимание:** corporate header `Copyright (c) 2026 X5 Group. Generated by AICreator.` присутствует в Go и Python файлах — он добавляется через mustache-шаблон. Kotlin-файлы генерируются через protobuf, там стандартный protobuf header.

---

### Акт 2: Volume Swap — "Другие спеки, ноль изменений"

#### Шаг 2.1: Очистка и запуск с альтернативными спеками

```bash
rm -rf generated/*
SPECS_DIR=./specs-alt docker compose up
```

#### Шаг 2.2: Ожидаемый вывод в терминале

Те же 3 волны, но с другими данными. Ключевые отличия в логах:

```
f1-kotlin-1   | === F1 Kotlin: buf generate ===
f1-kotlin-1   | Specs: /specs/proto
```

Финальные маркеры — числа будут **меньше**, потому что specs-alt содержит минимальный набор (один Product вместо трёх сущностей):

```
f1-kotlin-1   | === Generated ... file(s) in /generated/kotlin ===
f1-kotlin-1 exited with code 0
```

Все 9 сервисов должны завершиться с `exited with code 0`.

#### Шаг 2.3: Проверка — другой домен, другой пакет

```bash
# Посмотри какие .kt файлы сгенерировались
find generated/kotlin -name "*.kt"
```
Ожидаемый результат — файлы в пакете `catalog.v1` (было `logistics.v1`):
```
generated/kotlin/com/catalog/v1/ProductKt.kt
generated/kotlin/com/catalog/v1/CatalogKt.proto.kt
generated/kotlin/com/catalog/v1/GetProductRequestKt.kt
generated/kotlin/com/catalog/v1/ListProductsRequestKt.kt
generated/kotlin/com/catalog/v1/ListProductsResponseKt.kt
```

Посмотри содержимое — это уже Product, не Order:
```bash
head -20 generated/kotlin/com/catalog/v1/ProductKt.kt
```
Ожидаемый вывод:
```kotlin
// Generated by the protocol buffer compiler. DO NOT EDIT!
...
package com.catalog.v1

@kotlin.jvm.JvmName("-initializeproduct")
public inline fun product(block: com.catalog.v1.ProductKt.Dsl.() -> kotlin.Unit): ...
```

> **Ключевой момент:** ни один файл в `scripts/`, `dockerfiles/`, `config/`, `templates/` не менялся. Единственное отличие — переменная окружения `SPECS_DIR=./specs-alt`.

---

### Акт 3: Fail Fast — "Битая спека → мгновенная остановка"

#### Шаг 3.1: Посмотри на битую спеку перед запуском

```bash
cat specs-invalid/proto/broken.proto
```
Ожидаемый вывод:
```proto
syntax = "proto3";
package logistics.v1;

// Deliberate syntax error: missing semicolon on field
message BrokenOrder {
  string id = 1
  string name = 2;
}
```
> Обрати внимание: на строке 6 после `string id = 1` **нет точки с запятой**.

#### Шаг 3.2: Запуск с невалидными спеками

```bash
rm -rf generated/*
SPECS_DIR=./specs-invalid docker compose up
```

#### Шаг 3.3: Ожидаемый вывод — pipeline падает

**f1-kotlin** упадёт с ошибкой protoc:
```
f1-kotlin-1   | === F1 Kotlin: buf generate ===
f1-kotlin-1   | Specs: /specs/proto
f1-kotlin-1   | broken.proto:7:3:syntax error: expecting ';'
f1-kotlin-1 exited with code 100
```

**f2-go** и **f4-python** упадут с ошибкой openapi-generator:
```
f2-go-1       | === F2 Go: openapi-generator generate ===
f2-go-1       | ... attribute paths is missing
f2-go-1 exited with code 1

f4-python-1   | === F4 Python: openapi-generator generate ===
f4-python-1   | ... attribute paths is missing
f4-python-1 exited with code 1
```

**Волны 2 и 3 НЕ запустятся.** Docker Compose выведет ошибки зависимостей:
```
dependency failed to start: container demo-f1-kotlin-1 exited (100)
dependency failed to start: container demo-f2-go-1 exited (1)
```

Итоговый статус — 6 из 9 сервисов не запустились:
```
 ✔ Container demo-f1-kotlin-1        Exited (100)    ← ОШИБКА
 ✔ Container demo-f2-go-1            Exited (1)      ← ОШИБКА
 ✔ Container demo-f4-python-1        Exited (1)      ← ОШИБКА
 ✗ Container demo-format-kotlin-1    не запустился (зависимость упала)
 ✗ Container demo-format-go-1        не запустился
 ✗ Container demo-format-python-1    не запустился
 ✗ Container demo-validate-kotlin-1  не запустился
 ✗ Container demo-validate-go-1      не запустился
 ✗ Container demo-validate-python-1  не запустился
```

> **Ключевой момент:** pipeline остановился мгновенно на первой волне. Ошибки понятные: `broken.proto:7:3:syntax error: expecting ';'` — файл, строка, столбец. Время не потрачено на форматирование или компиляцию.

Проверь, что в `generated/` ничего полезного не появилось:
```bash
find generated -type f | wc -l
```
Ожидаемый результат: `0` (или минимальное число — папки могли создаться, но файлов нет).

---

### После трёх актов: обзор кода

Чтобы показать CTO сгенерированный код после Акта 3, нужно вернуть результаты Акта 1:

```bash
rm -rf generated/*
docker compose up
```

Дождись `exited with code 0` у всех 9 сервисов (см. Шаг 1.3).

Открой в редакторе (VS Code, если есть) три файла и обрати внимание на:

| Файл | Где открыть | На что смотреть |
|------|-------------|-----------------|
| `generated/kotlin/com/logistics/v1/OrderKt.kt` | Строки 1-17 | Kotlin DSL: функция `order { ... }` — type-safe builder для protobuf-объекта. Вызов `order { orderId = "123"; status = ORDER_STATUS_CREATED }` создаёт объект |
| `generated/go/src/api_orders.go` | Строки 1-2, 14-18 | Первые 2 строки — corporate header `Copyright X5 Group`. Далее — `OrdersAPIController` struct с interface-based architecture (`OrdersAPIServicer`) и Gorilla mux router |
| `generated/python/logistics_client/api/orders_api.py` | Строки 1-4, 6-14 | Corporate header + pydantic-импорты (`validate_call`, `Field`, `StrictStr`). Полностью типизированный HTTP-клиент, готовый к использованию |

> **На что обратить внимание CTO:** это не болванки. Corporate header добавляется через mustache-шаблон (единственная кастомизация). Каждый файл прошёл форматирование и компиляцию.

---

### Очистка между прогонами

Перед повторным прохождением демо (например, после тестового прогона — перед показом CTO):

```bash
# 1. Остановить все контейнеры (если что-то зависло)
docker compose down

# 2. Удалить все сгенерированные файлы
rm -rf generated/*

# 3. (Опционально) Убедиться, что образы уже собраны — чтобы на демо не ждать
docker compose build --quiet
```

После этих команд ты в исходном состоянии — можно запускать `docker compose up` с чистого листа.

> **Важно:** НЕ нужно делать `docker compose build` перед каждым запуском. Образы кешируются. Пересборка нужна только если менялись Dockerfile или скрипты. Для демо достаточно `rm -rf generated/*` + `docker compose up`.

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
