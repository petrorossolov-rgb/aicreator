"""BufGoGenerator — Proto → Go code generation via buf CLI."""

from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path

from aicreator.core.generator import BaseGenerator, GenerationResult, GeneratorConfig, ValidationResult
from aicreator.core.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


@Orchestrator.register("proto", "go", "f1")
class BufGoGenerator(BaseGenerator):
    """Generates Go code from .proto files using buf."""

    def validate(self, spec_path: Path) -> ValidationResult:
        errors: list[str] = []

        if not spec_path.is_dir():
            errors.append(f"spec_path is not a directory: {spec_path}")
            return ValidationResult(valid=False, errors=errors)

        if not (spec_path / "buf.yaml").is_file():
            errors.append("buf.yaml not found in spec directory")

        proto_files = list(spec_path.glob("*.proto"))
        if not proto_files:
            errors.append("No .proto files found in spec directory")

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def generate(self, spec_path: Path, output_dir: Path, config: GeneratorConfig) -> GenerationResult:
        output_dir.mkdir(parents=True, exist_ok=True)

        buf_gen_files = list(spec_path.glob("buf.gen*.yaml"))
        if not buf_gen_files:
            return GenerationResult(
                output_dir=output_dir,
                files_generated=0,
                duration_ms=0,
                success=False,
                error="No buf.gen*.yaml template found in spec directory",
            )

        template_path = buf_gen_files[0]

        start = time.monotonic()
        try:
            result = subprocess.run(
                ["buf", "generate", "--template", str(template_path), "--output", str(output_dir)],
                cwd=str(spec_path),
                capture_output=True,
                text=True,
                timeout=config.timeout,
            )
        except subprocess.TimeoutExpired:
            duration_ms = int((time.monotonic() - start) * 1000)
            return GenerationResult(
                output_dir=output_dir,
                files_generated=0,
                duration_ms=duration_ms,
                success=False,
                error=f"buf generate timed out after {config.timeout}s",
            )

        duration_ms = int((time.monotonic() - start) * 1000)

        if result.returncode != 0:
            logger.error("buf generate failed: %s", result.stderr)
            return GenerationResult(
                output_dir=output_dir,
                files_generated=0,
                duration_ms=duration_ms,
                success=False,
                error=result.stderr.strip(),
            )

        generated_files = list(output_dir.rglob("*.go"))
        logger.info("buf generated %d Go files in %dms", len(generated_files), duration_ms)

        return GenerationResult(
            output_dir=output_dir,
            files_generated=len(generated_files),
            duration_ms=duration_ms,
            success=True,
        )
