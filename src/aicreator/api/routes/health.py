"""Health check endpoint."""

from typing import Any

from fastapi import APIRouter

from aicreator import __version__

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, Any]:
    """Return service health status."""
    return {"status": "ok", "version": __version__}
