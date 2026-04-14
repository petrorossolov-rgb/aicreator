"""FastAPI dependency providers."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from aicreator.core.orchestrator import Orchestrator
from aicreator.db.engine import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide a database session, closing it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_orchestrator() -> Orchestrator:
    """Provide an Orchestrator instance."""
    return Orchestrator()
