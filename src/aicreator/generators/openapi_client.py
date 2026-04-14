"""OpenAPIClientGenerator — OpenAPI → Go client code (F4)."""

from __future__ import annotations

from aicreator.core.orchestrator import Orchestrator
from aicreator.generators.openapi_base import OpenAPIBaseGenerator


@Orchestrator.register("openapi", "go", "f4")
class OpenAPIClientGenerator(OpenAPIBaseGenerator):
    """Generates Go client SDK from OpenAPI spec using go generator."""

    generator_name = "go"
