"""Core abstractions for code generators."""

from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, Field


class GeneratorConfig(BaseModel):
    """Configuration for a code generator."""

    tool_path: str = "/opt/openapi-generator/openapi-generator-cli.jar"
    template_dir: Path | None = None
    additional_properties: dict[str, str] = Field(default_factory=dict)
    timeout: int = 120
    module_name: str = "generated"


class ValidationResult(BaseModel):
    """Result of spec validation."""

    valid: bool
    errors: list[str] = Field(default_factory=list)


class GenerationResult(BaseModel):
    """Result of code generation."""

    output_dir: Path
    files_generated: int
    duration_ms: int
    success: bool
    error: str | None = None


class BaseGenerator(ABC):
    """Abstract base class for all code generators."""

    @abstractmethod
    def validate(self, spec_path: Path) -> ValidationResult:
        """Validate the specification before generation."""

    @abstractmethod
    def generate(self, spec_path: Path, output_dir: Path, config: GeneratorConfig) -> GenerationResult:
        """Generate code from the specification."""
