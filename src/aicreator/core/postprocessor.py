"""PostProcessor chain — sequential post-processing steps for generated code."""

from __future__ import annotations

import logging
import subprocess
from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Severity(StrEnum):
    FATAL = "fatal"
    WARNING = "warning"


class StepResult(BaseModel):
    """Result of a single post-processing step."""

    step_name: str
    success: bool
    error: str | None = None


class PostProcessResult(BaseModel):
    """Aggregate result of the full post-processing chain."""

    success: bool
    steps: list[StepResult] = Field(default_factory=list)


class PostProcessError(Exception):
    """Raised when a fatal post-processing step fails."""

    def __init__(self, step_name: str, stderr: str) -> None:
        self.step_name = step_name
        self.stderr = stderr
        super().__init__(f"Post-processing step '{step_name}' failed: {stderr}")


class PostProcessStep(ABC):
    """Abstract base for a single post-processing step."""

    name: str = "unnamed"
    severity: Severity = Severity.FATAL
    timeout: int = 120

    @abstractmethod
    def execute(self, output_dir: Path) -> StepResult:
        """Run this step against the generated output directory."""


class PostProcessor:
    """Executes a chain of PostProcessSteps in order."""

    def __init__(self, steps: list[PostProcessStep] | None = None) -> None:
        self.steps = steps or []

    def run(self, output_dir: Path, language: str = "") -> PostProcessResult:
        results: list[StepResult] = []

        for step in self.steps:
            result = step.execute(output_dir)
            results.append(result)

            if not result.success:
                if step.severity == Severity.FATAL:
                    logger.error("Fatal step '%s' failed: %s", step.name, result.error)
                    raise PostProcessError(step.name, result.error or "unknown error")
                logger.warning("Warning step '%s' failed: %s", step.name, result.error)

        return PostProcessResult(success=True, steps=results)


# ---------- Go-specific steps ----------


class GoModInitStep(PostProcessStep):
    """Initialize Go module: go mod init + go mod tidy + go mod download."""

    name = "go-mod-init"
    severity = Severity.FATAL

    def __init__(self, module_name: str = "generated", timeout: int = 120) -> None:
        self.module_name = module_name
        self.timeout = timeout

    def execute(self, output_dir: Path) -> StepResult:
        go_mod = output_dir / "go.mod"
        commands: list[list[str]] = []

        if not go_mod.is_file():
            commands.append(["go", "mod", "init", self.module_name])

        commands.extend(
            [
                ["go", "mod", "tidy"],
                ["go", "mod", "download"],
            ]
        )

        for cmd in commands:
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(output_dir),
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
            except subprocess.TimeoutExpired:
                return StepResult(step_name=self.name, success=False, error=f"'{' '.join(cmd)}' timed out")

            if proc.returncode != 0:
                return StepResult(step_name=self.name, success=False, error=proc.stderr.strip())

        return StepResult(step_name=self.name, success=True)


class GofmtStep(PostProcessStep):
    """Format Go code with gofmt."""

    name = "gofmt"
    severity = Severity.FATAL

    def __init__(self, timeout: int = 120) -> None:
        self.timeout = timeout

    def execute(self, output_dir: Path) -> StepResult:
        try:
            proc = subprocess.run(
                ["gofmt", "-w", str(output_dir)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            return StepResult(step_name=self.name, success=False, error="gofmt timed out")

        if proc.returncode != 0:
            return StepResult(step_name=self.name, success=False, error=proc.stderr.strip())

        return StepResult(step_name=self.name, success=True)


class GolangciLintStep(PostProcessStep):
    """Run golangci-lint (best-effort, warning severity)."""

    name = "golangci-lint"
    severity = Severity.WARNING

    def __init__(self, timeout: int = 120) -> None:
        self.timeout = timeout

    def execute(self, output_dir: Path) -> StepResult:
        try:
            proc = subprocess.run(
                ["golangci-lint", "run", "--fix", "--disable-all", "--enable=gofmt,govet", "./..."],
                cwd=str(output_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            return StepResult(step_name=self.name, success=False, error="golangci-lint timed out")

        if proc.returncode != 0:
            return StepResult(step_name=self.name, success=False, error=proc.stderr.strip())

        return StepResult(step_name=self.name, success=True)


class GoBuildStep(PostProcessStep):
    """Compile Go code to verify it builds."""

    name = "go-build"
    severity = Severity.FATAL

    def __init__(self, timeout: int = 120) -> None:
        self.timeout = timeout

    def execute(self, output_dir: Path) -> StepResult:
        try:
            proc = subprocess.run(
                ["go", "build", "./..."],
                cwd=str(output_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            return StepResult(step_name=self.name, success=False, error="go build timed out")

        if proc.returncode != 0:
            return StepResult(step_name=self.name, success=False, error=proc.stderr.strip())

        return StepResult(step_name=self.name, success=True)


def go_postprocessor(module_name: str = "generated", timeout: int = 120) -> PostProcessor:
    """Create a PostProcessor configured with the standard Go chain."""
    return PostProcessor(
        steps=[
            GoModInitStep(module_name=module_name, timeout=timeout),
            GofmtStep(timeout=timeout),
            GolangciLintStep(timeout=timeout),
            GoBuildStep(timeout=timeout),
        ]
    )
