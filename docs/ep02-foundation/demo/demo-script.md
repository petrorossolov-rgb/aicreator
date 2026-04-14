# AICreator: Сценарий живого демо

> Общая длительность: ~20 минут
> Аудитория: CTO + команда симуляции
> Необходимо: MacBook с Docker Desktop, склонированный репозиторий, реальные спеки в отдельной папке

---

## 1. Вступление (1 мин)

**Что говорить:**

> Мы реализовали платформу детерминистичной генерации кода AICreator.
> Сегодня покажу три вещи:
> 1. Генерация Go-кода из Proto и OpenAPI спецификаций через CLI
> 2. Детерминизм -- повторный запуск даёт идентичный результат
> 3. Работа на реальных спецификациях вашей команды
>
> На хост-машине нужен только Docker. Ни Go, ни Java, ни Python устанавливать не нужно.

---

## 2. Развёртывание (2 мин)

```bash
# Показать, что на машине нет Go/Java
which go    # command not found
which java  # command not found

# Запустить платформу
cd AICreator
docker compose -f docker/docker-compose.yml --profile prod up -d --build

# Дождаться готовности (показать логи)
docker compose -f docker/docker-compose.yml --profile prod logs -f api-prod
# Ждём "Application startup complete", затем Ctrl+C
```

**Что подчеркнуть:**
- Одна команда поднимает всё: PostgreSQL, API с Go-тулчейном, buf, protoc, openapi-generator
- Принцип конституции #2: "Контейнеризация -- хосту нужен только Docker"

```bash
# Проверить здоровье
aicreator health
# OK API healthy -- version 0.1.0
```

---

## 3. F1: Proto -> Go (3 мин)

```bash
# Генерация Go-кода из .proto файлов
aicreator generate -f f1 \
  -s tests/fixtures/proto \
  -o ./demo-output/f1 \
  -l go

# Показать результат
ls -la demo-output/f1/
# 7 Go-файлов: structs, gRPC stubs

# Открыть один файл -- показать качество кода
cat demo-output/f1/logistics/v1/order.pb.go | head -30
```

**Что подчеркнуть:**
- `buf 1.50.0` + `protoc 29.3` -- production-grade инструменты
- Сгенерированный код готов к компиляции
- Generation ID выдаётся для трекинга

---

## 4. F2: OpenAPI -> Go Server (3 мин)

```bash
# Генерация серверных стабов
aicreator generate -f f2 \
  -s tests/fixtures/openapi \
  -o ./demo-output/f2 \
  -l go

# Показать структуру
find demo-output/f2 -name "*.go" | head -15
# ~38 Go-файлов: роутеры, хендлеры, модели

# Открыть API-роутер
cat demo-output/f2/go/routers.go | head -30
```

**Что подчеркнуть:**
- Из одного YAML-файла -- полный серверный стаб
- openapi-generator 7.12.0 -- стандарт индустрии (23k+ звёзд на GitHub)
- Команде остаётся только заполнить бизнес-логику

---

## 5. F4: OpenAPI -> Go Client (3 мин)

```bash
# Генерация клиентской библиотеки
aicreator generate -f f4 \
  -s tests/fixtures/openapi \
  -o ./demo-output/f4 \
  -l go

# Показать структуру
find demo-output/f4 -name "*.go" | head -15
# ~59 Go-файлов: клиент, модели, конфигурация

# Открыть клиентский код
cat demo-output/f4/api_default.go | head -30
```

**Что подчеркнуть:**
- Клиент и сервер генерируются из одной и той же спецификации
- Гарантия совместимости контрактов

---

## 6. Детерминизм (2 мин)

```bash
# Запустить F1 повторно
aicreator generate -f f1 \
  -s tests/fixtures/proto \
  -o ./demo-output/f1-check \
  -l go

# Сравнить с первым запуском
diff -r demo-output/f1 demo-output/f1-check
# Пустой вывод = файлы идентичны

# Проверить input_hash в БД
aicreator status <первый-generation-id>
aicreator status <второй-generation-id>
# input_hash совпадает!
```

**Что подчеркнуть:**
- Принцип конституции #1: "Идентичный вход = идентичный выход"
- `input_hash` (SHA-256) хранится в PostgreSQL для верификации
- Это критично для CI/CD: повторный билд не должен менять артефакты

---

## 7. API (2 мин)

```bash
# Тот же функционал через REST API
curl -X POST http://localhost:8000/api/v1/generate \
  -F "files=@tests/fixtures/openapi/logistics.yaml" \
  -F 'metadata={"function":"f2","language":"go","spec_type":"openapi"}' \
  -o /tmp/api-output.zip

# Распаковать и сравнить
unzip -o /tmp/api-output.zip -d /tmp/api-output/
diff -r demo-output/f2 /tmp/api-output/
# Идентичный результат
```

**Что подчеркнуть:**
- CLI и API -- один и тот же backend
- API можно вызывать из скриптов, CI/CD, других сервисов
- Multipart upload: файлы + JSON-метаданные

---

## 8. Реальные спецификации (2 мин)

```bash
# Подставить реальные спеки
aicreator generate -f f2 \
  -s /path/to/real-specs \
  -o ./demo-output/real \
  -l go

# Показать результат
find demo-output/real -name "*.go" | wc -l
```

**Что подчеркнуть:**
- Флаг `--spec` принимает любую директорию
- Реальные спеки не коммитятся в репозиторий (NDA)
- Платформа работает с любыми валидными Proto/OpenAPI спецификациями

---

## 9. Q&A

### Возможные вопросы CTO и ответы

**Q: Как добавить новый язык, например Kotlin?**
> A: Создать новый класс генератора с декоратором `@Orchestrator.register("openapi", "kotlin", "f2")`.
> Архитектура поддерживает это из коробки -- паттерн Strategy + Registry.

**Q: Как гарантируется качество сгенерированного кода?**
> A: PostProcessor запускает цепочку: `gofmt` (форматирование) -> `golangci-lint` (линтинг) -> `go build` (компиляция).
> Если любой шаг падает -- генерация считается неуспешной.

**Q: Что будет, если спецификация невалидна?**
> A: Fail Fast. Валидация до генерации: проверяется наличие обязательных файлов, корректность YAML, наличие ключа `openapi`.
> Понятное сообщение об ошибке.

**Q: Как это интегрировать в CI/CD?**
> A: REST API. `curl -X POST /api/v1/generate` в любом пайплайне. Следующий эпик -- готовый плагин для GitHub Actions.

**Q: Какие ресурсы нужны для запуска?**
> A: Docker Desktop. PostgreSQL запускается в контейнере. Вся генерация внутри контейнера.
> Минимальные требования: 4 GB RAM, 10 GB диск.

---

## Завершение

```bash
# Остановить платформу
docker compose -f docker/docker-compose.yml --profile prod down
```

> Сегодня показали: CLI для трёх функций генерации, детерминизм, работу с реальными спеками.
> Следующие шаги: F3 (AI-генерация из PlantUML), multi-language поддержка, CI/CD-плагин.
