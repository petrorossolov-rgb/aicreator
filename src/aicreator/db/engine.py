"""Database engine and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from aicreator.core.config import settings


def create_engine(url: str | None = None) -> Engine:
    """Create SQLAlchemy engine."""
    return sa_create_engine(url or settings.database_url)


engine = create_engine()
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
