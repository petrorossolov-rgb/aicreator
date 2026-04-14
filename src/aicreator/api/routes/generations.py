"""GET /api/v1/generations/{id} — retrieve generation metadata."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from aicreator.api.dependencies import get_db
from aicreator.api.schemas import GenerationResponse
from aicreator.db.repository import get_generation

router = APIRouter()


@router.get("/generations/{generation_id}", response_model=GenerationResponse)
async def get_generation_by_id(
    generation_id: UUID,
    db: Session = Depends(get_db),
) -> GenerationResponse:
    """Return generation record by ID."""
    gen = get_generation(db, generation_id)
    if gen is None:
        raise HTTPException(status_code=404, detail=f"Generation {generation_id} not found")
    return GenerationResponse(
        id=gen.id,
        function=gen.function,
        language=gen.language,
        spec_type=gen.spec_type,
        status=gen.status,
        input_hash=gen.input_hash,
        created_at=gen.created_at,
        completed_at=gen.completed_at,
        duration_ms=gen.duration_ms,
        error=gen.error,
    )
