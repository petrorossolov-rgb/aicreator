"""POST /api/v1/generate — run code generation from uploaded specs."""

import hashlib
import io
import logging
import shutil
import tempfile
import time
import zipfile
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from aicreator.api.dependencies import get_db, get_orchestrator
from aicreator.api.schemas import GenerateRequest
from aicreator.core.orchestrator import Orchestrator, UnsupportedCombinationError, ValidationError
from aicreator.db.models import GenerationStatus
from aicreator.db.repository import create_generation, update_generation_status

logger = logging.getLogger(__name__)

router = APIRouter()


def _compute_input_hash(files: list[UploadFile]) -> str:
    """SHA-256 hash of sorted (filename, contents) pairs."""
    h = hashlib.sha256()
    pairs: list[tuple[str, bytes]] = []
    for f in files:
        content = f.file.read()
        pairs.append((f.filename or "", content))
        f.file.seek(0)
    for name, content in sorted(pairs, key=lambda p: p[0]):
        h.update(name.encode())
        h.update(content)
    return h.hexdigest()


def _save_uploaded_files(files: list[UploadFile], dest: Path) -> None:
    """Write uploaded files into *dest* directory."""
    dest.mkdir(parents=True, exist_ok=True)
    for f in files:
        target = dest / (f.filename or "unnamed")
        target.write_bytes(f.file.read())
        f.file.seek(0)


def _zip_directory(directory: Path) -> bytes:
    """Create an in-memory ZIP archive from *directory* contents."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, file_path.relative_to(directory))
    buf.seek(0)
    return buf.read()


@router.post("/generate")
async def generate(
    files: list[UploadFile],
    metadata: str = Form(...),
    db: Session = Depends(get_db),
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> StreamingResponse:
    """Accept spec files + metadata, run generation, return ZIP."""
    # Validate metadata JSON
    try:
        request = GenerateRequest.model_validate_json(metadata)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid metadata: {exc}") from exc

    if not files:
        raise HTTPException(status_code=422, detail="No files uploaded")

    input_hash = _compute_input_hash(files)

    gen = create_generation(
        db,
        spec_type=request.spec_type,
        language=request.language,
        function=request.function,
        input_hash=input_hash,
    )

    spec_dir = Path(tempfile.mkdtemp(prefix="aicreator_specs_"))
    output_dir = Path(tempfile.mkdtemp(prefix="aicreator_output_"))

    try:
        _save_uploaded_files(files, spec_dir)

        update_generation_status(db, gen.id, GenerationStatus.RUNNING)

        t0 = time.monotonic()
        try:
            orchestrator.run(
                spec_type=request.spec_type,
                language=request.language,
                function=request.function,
                spec_path=spec_dir,
                output_dir=output_dir,
            )
        except UnsupportedCombinationError as exc:
            duration_ms = int((time.monotonic() - t0) * 1000)
            update_generation_status(db, gen.id, GenerationStatus.FAILED, error=str(exc), duration_ms=duration_ms)
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except ValidationError as exc:
            duration_ms = int((time.monotonic() - t0) * 1000)
            update_generation_status(db, gen.id, GenerationStatus.FAILED, error=str(exc), duration_ms=duration_ms)
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except Exception as exc:
            duration_ms = int((time.monotonic() - t0) * 1000)
            update_generation_status(db, gen.id, GenerationStatus.FAILED, error=str(exc), duration_ms=duration_ms)
            logger.exception("Generation failed for %s", gen.id)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        duration_ms = int((time.monotonic() - t0) * 1000)
        update_generation_status(db, gen.id, GenerationStatus.COMPLETED, duration_ms=duration_ms)

        zip_bytes = _zip_directory(output_dir)

        return StreamingResponse(
            io.BytesIO(zip_bytes),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=generation-{gen.id}.zip",
                "X-Generation-ID": str(gen.id),
            },
        )
    finally:
        shutil.rmtree(spec_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)
