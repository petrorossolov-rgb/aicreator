#!/bin/bash
set -e

echo "Running database migrations..."
uv run alembic upgrade head

echo "Starting API server..."
exec uv run uvicorn aicreator.api.app:app \
    --host "${AICREATOR_API_HOST:-0.0.0.0}" \
    --port "${AICREATOR_API_PORT:-8000}" \
    --workers "${AICREATOR_WORKERS:-2}"
