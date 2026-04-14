"""Orchestrator with Registry pattern for routing to generators."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Protocol

from aicreator.core.generator import BaseGenerator, GenerationResult, GeneratorConfig, ValidationResult

logger = logging.getLogger(__name__)


class PostProcessorProtocol(Protocol):
    """Protocol for post-processor dependency injection."""

    def run(self, output_dir: Path, language: str) -> None: ...


class _NoOpPostProcessor:
    """Default post-processor that does nothing."""

    def run(self, output_dir: Path, language: str) -> None:
        pass


class UnsupportedCombinationError(Exception):
    """Raised when no generator is registered for the given (spec_type, language, function) tuple."""

    def __init__(self, key: tuple[str, str, str]) -> None:
        self.key = key
        super().__init__(f"No generator registered for {key}")


class ValidationError(Exception):
    """Raised when spec validation fails."""

    def __init__(self, result: ValidationResult) -> None:
        self.result = result
        super().__init__(f"Validation failed: {', '.join(result.errors)}")


class Orchestrator:
    """Routes generation requests to registered generators."""

    _registry: dict[tuple[str, str, str], type[BaseGenerator]] = {}

    def __init__(
        self,
        config: GeneratorConfig | None = None,
        postprocessor: PostProcessorProtocol | None = None,
    ) -> None:
        self.config = config or GeneratorConfig()
        self.postprocessor = postprocessor or _NoOpPostProcessor()

    @classmethod
    def register(cls, spec_type: str, language: str, function: str) -> Any:
        """Decorator to register a generator class for a (spec_type, language, function) tuple."""

        def decorator(generator_cls: type[BaseGenerator]) -> type[BaseGenerator]:
            key = (spec_type, language, function)
            cls._registry[key] = generator_cls
            logger.info("Registered generator %s for %s", generator_cls.__name__, key)
            return generator_cls

        return decorator

    @classmethod
    def reset_registry(cls) -> None:
        """Clear all registrations. Used in tests."""
        cls._registry.clear()

    def run(
        self,
        spec_type: str,
        language: str,
        function: str,
        spec_path: Path,
        output_dir: Path,
    ) -> GenerationResult:
        """Route to the correct generator: validate → generate → post-process."""
        key = (spec_type, language, function)
        generator_cls = self._registry.get(key)
        if generator_cls is None:
            raise UnsupportedCombinationError(key)

        generator = generator_cls()

        validation = generator.validate(spec_path)
        if not validation.valid:
            raise ValidationError(validation)

        result = generator.generate(spec_path, output_dir, self.config)

        if result.success:
            self.postprocessor.run(output_dir, language)

        return result
