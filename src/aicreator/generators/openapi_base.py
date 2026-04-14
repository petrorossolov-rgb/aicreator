"""Shared validation logic for OpenAPI generators."""

from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path

import yaml

from aicreator.core.generator import BaseGenerator, GenerationResult, GeneratorConfig, ValidationResult

logger = logging.getLogger(__name__)


class OpenAPIBaseGenerator(BaseGenerator):
    """Base class for OpenAPI generators with shared validation and subprocess logic."""

    generator_name: str = ""  # override in subclasses: "go-server" or "go"

    def _resolve_spec_file(self, spec_path: Path) -> Path | None:
        """Resolve spec_path to a single .yaml/.yml file.

        If spec_path is a file, return it directly.
        If spec_path is a directory, find the first .yaml/.yml file inside.
        """
        if spec_path.is_file():
            return spec_path
        if spec_path.is_dir():
            for ext in ("*.yaml", "*.yml"):
                files = sorted(spec_path.glob(ext))
                if files:
                    return files[0]
        return None

    def validate(self, spec_path: Path) -> ValidationResult:
        errors: list[str] = []

        resolved = self._resolve_spec_file(spec_path)
        if resolved is None:
            errors.append(f"No .yaml/.yml spec file found in: {spec_path}")
            return ValidationResult(valid=False, errors=errors)

        if resolved.suffix not in (".yaml", ".yml"):
            errors.append(f"Spec file must be .yaml or .yml, got: {resolved.suffix}")
            return ValidationResult(valid=False, errors=errors)

        try:
            with open(resolved) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            errors.append(f"Invalid YAML: {exc}")
            return ValidationResult(valid=False, errors=errors)

        if not isinstance(data, dict) or "openapi" not in data:
            errors.append("YAML does not contain 'openapi' key - not a valid OpenAPI spec")

        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def _build_command(self, spec_path: Path, output_dir: Path, config: GeneratorConfig) -> list[str]:
        jar = config.tool_path or "openapi-generator-cli.jar"
        cmd = [
            "java",
            "-jar",
            jar,
            "generate",
            "-i",
            str(spec_path),
            "-g",
            self.generator_name,
            "-o",
            str(output_dir),
        ]
        if config.template_dir and config.template_dir.is_dir():
            cmd.extend(["-t", str(config.template_dir)])
        for key, value in config.additional_properties.items():
            cmd.extend(["--additional-properties", f"{key}={value}"])
        return cmd

    def generate(self, spec_path: Path, output_dir: Path, config: GeneratorConfig) -> GenerationResult:
        output_dir.mkdir(parents=True, exist_ok=True)

        resolved = self._resolve_spec_file(spec_path)
        if resolved is None:
            return GenerationResult(
                output_dir=output_dir,
                files_generated=0,
                duration_ms=0,
                success=False,
                error=f"No .yaml/.yml spec file found in: {spec_path}",
            )

        cmd = self._build_command(resolved, output_dir, config)
        start = time.monotonic()

        try:
            result = subprocess.run(
                cmd,
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
                error=f"openapi-generator timed out after {config.timeout}s",
            )

        duration_ms = int((time.monotonic() - start) * 1000)

        if result.returncode != 0:
            logger.error("openapi-generator failed: %s", result.stderr)
            return GenerationResult(
                output_dir=output_dir,
                files_generated=0,
                duration_ms=duration_ms,
                success=False,
                error=result.stderr.strip(),
            )

        generated_files = list(output_dir.rglob("*.go"))
        logger.info("openapi-generator produced %d Go files in %dms", len(generated_files), duration_ms)

        return GenerationResult(
            output_dir=output_dir,
            files_generated=len(generated_files),
            duration_ms=duration_ms,
            success=True,
        )
