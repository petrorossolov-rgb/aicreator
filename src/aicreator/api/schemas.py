"""API request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    """Metadata for a generation request (parsed from multipart form JSON)."""

    function: str
    language: str
    spec_type: str


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str


class GenerationResponse(BaseModel):
    """Generation record returned by GET /api/v1/generations/{id}."""

    id: UUID
    function: str
    language: str
    spec_type: str
    status: str
    input_hash: str
    created_at: datetime
    completed_at: datetime | None = None
    duration_ms: int | None = None
    error: str | None = None
