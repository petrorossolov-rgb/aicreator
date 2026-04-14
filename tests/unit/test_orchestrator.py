"""Tests for Orchestrator with Registry pattern."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from aicreator.core.orchestrator import Orchestrator, UnsupportedCombinationError, ValidationError
from tests.conftest import StubGenerator


@pytest.fixture(autouse=True)
def _clean_registry() -> None:  # noqa: PT004
    """Reset registry before each test to avoid cross-test pollution."""
    Orchestrator.reset_registry()


def test_register_and_route(tmp_path: Path) -> None:
    Orchestrator.register("proto", "go", "f1")(StubGenerator)

    orch = Orchestrator()
    spec_path = tmp_path / "specs"
    spec_path.mkdir()
    output_dir = tmp_path / "output"

    result = orch.run("proto", "go", "f1", spec_path, output_dir)
    assert result.success is True
    assert result.files_generated == 1


def test_unsupported_combination_raises(tmp_path: Path) -> None:
    orch = Orchestrator()
    with pytest.raises(UnsupportedCombinationError, match="No generator registered"):
        orch.run("asyncapi", "rust", "f99", tmp_path, tmp_path / "out")


def test_validation_failure_stops_generation(tmp_path: Path) -> None:
    class FailingGenerator(StubGenerator):
        def __init__(self) -> None:
            super().__init__(should_fail_validation=True)

    Orchestrator.register("proto", "go", "f1")(FailingGenerator)

    orch = Orchestrator()
    output_dir = tmp_path / "output"

    with pytest.raises(ValidationError, match="stub validation failure"):
        orch.run("proto", "go", "f1", tmp_path, output_dir)

    # generate should not have been called — no output dir
    assert not output_dir.exists()


def test_multiple_registrations(tmp_path: Path) -> None:
    class GenA(StubGenerator):
        pass

    class GenB(StubGenerator):
        pass

    class GenC(StubGenerator):
        pass

    Orchestrator.register("proto", "go", "f1")(GenA)
    Orchestrator.register("openapi", "go", "f2")(GenB)
    Orchestrator.register("openapi", "go", "f4")(GenC)

    orch = Orchestrator()
    spec_path = tmp_path / "specs"
    spec_path.mkdir()

    for st, lang, fn in [("proto", "go", "f1"), ("openapi", "go", "f2"), ("openapi", "go", "f4")]:
        result = orch.run(st, lang, fn, spec_path, tmp_path / f"out-{fn}")
        assert result.success is True


def test_postprocessor_called_on_success(tmp_path: Path) -> None:
    Orchestrator.register("proto", "go", "f1")(StubGenerator)

    mock_pp = MagicMock()
    orch = Orchestrator(postprocessor=mock_pp)
    spec_path = tmp_path / "specs"
    spec_path.mkdir()

    orch.run("proto", "go", "f1", spec_path, tmp_path / "output")
    mock_pp.run.assert_called_once_with(tmp_path / "output", "go")
