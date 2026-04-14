"""FastAPI application factory."""

from fastapi import FastAPI

from aicreator import __version__
from aicreator.api.middleware import RequestIdMiddleware
from aicreator.api.routes.health import router as health_router
from aicreator.core.config import settings
from aicreator.core.logging import setup_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    setup_logging(level=settings.log_level, fmt=settings.log_format)

    application = FastAPI(
        title="AICreator",
        version=__version__,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    application.add_middleware(RequestIdMiddleware)
    application.include_router(health_router, prefix="/api/v1")

    return application


app = create_app()
