"""OpenAPIServerGenerator — OpenAPI → Go server code (F2)."""

from __future__ import annotations

from aicreator.core.orchestrator import Orchestrator
from aicreator.generators.openapi_base import OpenAPIBaseGenerator


@Orchestrator.register("openapi", "go", "f2")
class OpenAPIServerGenerator(OpenAPIBaseGenerator):
    """Generates Go server stubs from OpenAPI spec using go-server generator."""

    generator_name = "go-server"
