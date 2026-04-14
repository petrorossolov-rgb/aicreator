"""Repository functions for Generation model."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from aicreator.db.models import Generation, GenerationStatus


def create_generation(
    db: Session,
    *,
    spec_type: str,
    language: str,
    function: str,
    input_hash: str,
) -> Generation:
    """Create a new generation record."""
    gen = Generation(
        spec_type=spec_type,
        language=language,
        function=function,
        input_hash=input_hash,
        status=GenerationStatus.PENDING.value,
    )
    db.add(gen)
    db.commit()
    db.refresh(gen)
    return gen


def get_generation(db: Session, generation_id: UUID) -> Generation | None:
    """Get generation by ID. Returns None if not found."""
    return db.get(Generation, generation_id)


def update_generation_status(
    db: Session,
    generation_id: UUID,
    status: GenerationStatus,
    *,
    error: str | None = None,
    duration_ms: int | None = None,
) -> Generation | None:
    """Update generation status. Sets completed_at for terminal states."""
    gen = db.get(Generation, generation_id)
    if gen is None:
        return None
    gen.status = status.value
    if status in (GenerationStatus.COMPLETED, GenerationStatus.FAILED):
        gen.completed_at = datetime.now(UTC)
    if error is not None:
        gen.error = error
    if duration_ms is not None:
        gen.duration_ms = duration_ms
    db.commit()
    db.refresh(gen)
    return gen
