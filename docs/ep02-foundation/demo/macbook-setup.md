# Развёртывание AICreator на MacBook (Apple Silicon)

Пошаговая инструкция для переноса проекта на MacBook M-серии и подготовки к демо.

---

## Предварительные требования

| Компонент | Минимальная версия | Проверка |
|-----------|-------------------|----------|
| Docker Desktop для Mac | 4.x (Apple Silicon native) | `docker --version` |
| Git | 2.x | `git --version` |
| Python 3.12+ | 3.12 | `python3 --version` |
| pip или uv | любая | `pip --version` / `uv --version` |

> **Важно:** Docker Desktop должен быть в режиме Apple Silicon (не Rosetta).
> Проверка: Docker Desktop -> Settings -> General -> "Use Virtualization framework" = включено.

---

## Шаг 1: Клонирование репозитория

```bash
git clone <repo-url>
cd AICreator
```

---

## Шаг 2: Сборка Docker-образа

```bash
docker compose -f docker/docker-compose.yml --profile prod build
```

Это займёт 3-5 минут при первой сборке. Docker BuildKit автоматически определит архитектуру ARM64 и скачает правильные бинарники `buf` и `protoc`.

**Что происходит при сборке:**
- Stage 1: компиляция Go-инструментов (protoc-gen-go, golangci-lint)
- Stage 2: скачивание buf (aarch64) и protoc (aarch_64)
- Stage 3: сборка runtime-образа (Python 3.12 + Go 1.23 + JRE 21 + все инструменты)

---

## Шаг 3: Запуск платформы

```bash
docker compose -f docker/docker-compose.yml --profile prod up -d
```

Проверка готовности:
```bash
# Дождаться готовности PostgreSQL + API
docker compose -f docker/docker-compose.yml --profile prod logs -f api-prod
# Ждите строку: "Application startup complete"
# Затем Ctrl+C
```

Быстрая проверка:
```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok","version":"0.1.0"}
```

---

## Шаг 4: Установка CLI

Глобальная установка через uv (без необходимости создавать venv вручную):

```bash
uv tool install --editable .
```

Это поставит `aicreator` как изолированный uv-tool — команда будет доступна из любой директории.

> **Если предпочитаете классический venv:**
> ```bash
> uv venv && source .venv/bin/activate
> uv pip install -e .
> ```
> `uv pip install` (в отличие от `uv sync`) **не создаёт venv автоматически** — без активного окружения упадёт с `No virtual environment found`.

Проверка:
```bash
aicreator --version
# aicreator 0.1.0

aicreator health
# OK API healthy -- version 0.1.0
```

---

## Шаг 5: Подготовка реальных спецификаций

Создайте директорию для реальных спеков (НЕ внутри репозитория):

```bash
mkdir -p ~/demo-specs/proto
mkdir -p ~/demo-specs/openapi
```

**Для Proto спецификаций (F1):**

Скопируйте в `~/demo-specs/proto/`:
- Ваши `.proto` файлы
- `buf.yaml` -- конфиг модуля buf
- `buf.gen.go.yaml` -- шаблон генерации

Каждый `.proto` файл должен содержать:
```protobuf
option go_package = "your/package/name";
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

**Для OpenAPI спецификаций (F2, F4):**

Скопируйте в `~/demo-specs/openapi/`:
- Ваш `.yaml` файл с OpenAPI 3.x спецификацией

---

## Шаг 6: Тестовая генерация

```bash
# На синтетических спеках (из репозитория)
aicreator generate -f f1 -s tests/fixtures/proto -o /tmp/test-f1 -l go
aicreator generate -f f2 -s tests/fixtures/openapi -o /tmp/test-f2 -l go
aicreator generate -f f4 -s tests/fixtures/openapi -o /tmp/test-f4 -l go

# На реальных спеках
aicreator generate -f f1 -s ~/demo-specs/proto -o /tmp/real-f1 -l go
aicreator generate -f f2 -s ~/demo-specs/openapi -o /tmp/real-f2 -l go
```

---

## Чеклист за 5 минут до демо

- [ ] Docker Desktop запущен
- [ ] `docker compose ... up -d` выполнен, контейнеры Running
- [ ] `aicreator health` отвечает "OK"
- [ ] Тестовая генерация F1 на синтетических спеках прошла
- [ ] Тестовая генерация F2 на синтетических спеках прошла
- [ ] Тестовая генерация F4 на синтетических спеках прошла
- [ ] Реальные спеки скопированы в `~/demo-specs/`
- [ ] Тестовая генерация на реальных спеках прошла
- [ ] Очистить предыдущие demo-output: `rm -rf demo-output/`
- [ ] Терминал развёрнут на полный экран, шрифт увеличен (Cmd+Plus)

---

## Troubleshooting

### Порт 8000 занят
```bash
# Найти процесс
lsof -i :8000
# Убить или сменить порт:
# В docker-compose.yml изменить "8000:8000" на "8001:8000"
# И использовать --api-url http://localhost:8001
```

### Docker не может собрать образ
```bash
# Проверить, что Docker Desktop использует Apple Silicon (не Rosetta)
docker info | grep Architecture
# Должно быть: aarch64

# Если amd64 -- перейти в Docker Desktop -> Settings -> General
# Выключить "Use Rosetta for x86_64/amd64 emulation on Apple Silicon"
```

### `uv.lock: not found` при сборке
Симптом: на шаге 2 `docker compose ... build` падает с
`failed to compute cache key: "/uv.lock": not found`.

Причина: репозиторий клонировался **до коммита 93defac (2026-04-20)**, когда `uv.lock` был в `.gitignore` и не пушился.

Решение:
```bash
git pull origin master
# uv.lock теперь в репозитории, сборка пройдёт
```

### `aicreator` команда не найдена
```bash
# Проверить, что pip установил в PATH
which aicreator
# Если пусто -- переустановить:
pip install -e . --force-reinstall

# Или запускать через uv:
uv run aicreator health
```

### Ошибка подключения к API
```bash
# Проверить, что контейнеры работают
docker compose -f docker/docker-compose.yml --profile prod ps
# api-prod должен быть в статусе "Up"

# Проверить логи
docker compose -f docker/docker-compose.yml --profile prod logs api-prod --tail 20
```

### Генерация зависает
```bash
# Openapi-generator требует JVM warmup (~2-3 секунды)
# Таймаут по умолчанию: 120 секунд
# Если спеки очень большие -- первый запуск может быть медленным
```

---

## Остановка после демо

```bash
docker compose -f docker/docker-compose.yml --profile prod down

# Полная очистка (включая данные PostgreSQL):
docker compose -f docker/docker-compose.yml --profile prod down -v
```
