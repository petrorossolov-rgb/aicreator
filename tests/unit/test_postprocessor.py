"""Tests for PostProcessor chain."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from aicreator.core.postprocessor import (
    GoBuildStep,
    GofmtStep,
    GolangciLintStep,
    GoModInitStep,
    PostProcessError,
    PostProcessor,
    PostProcessStep,
    Severity,
    StepResult,
    go_postprocessor,
)


class PassStep(PostProcessStep):
    name = "pass-step"
    severity = Severity.FATAL

    def execute(self, output_dir: Path) -> StepResult:
        return StepResult(step_name=self.name, success=True)


class FailFatalStep(PostProcessStep):
    name = "fail-fatal"
    severity = Severity.FATAL

    def execute(self, output_dir: Path) -> StepResult:
        return StepResult(step_name=self.name, success=False, error="fatal failure")


class FailWarningStep(PostProcessStep):
    name = "fail-warning"
    severity = Severity.WARNING

    def execute(self, output_dir: Path) -> StepResult:
        return StepResult(step_name=self.name, success=False, error="lint warning")


class TestPostProcessor:
    def test_all_steps_pass(self, tmp_path: Path) -> None:
        chain = PostProcessor(steps=[PassStep(), PassStep()])
        result = chain.run(tmp_path)
        assert result.success is True
        assert len(result.steps) == 2
        assert all(s.success for s in result.steps)

    def test_fatal_step_stops_chain(self, tmp_path: Path) -> None:
        third = MagicMock(spec=PostProcessStep)
        third.name = "third"
        third.severity = Severity.FATAL

        chain = PostProcessor(steps=[PassStep(), FailFatalStep(), third])

        with pytest.raises(PostProcessError, match="fail-fatal"):
            chain.run(tmp_path)

        third.execute.assert_not_called()

    def test_warning_step_continues(self, tmp_path: Path) -> None:
        chain = PostProcessor(steps=[PassStep(), FailWarningStep(), PassStep()])
        result = chain.run(tmp_path)
        assert result.success is True
        assert len(result.steps) == 3
        assert result.steps[1].success is False
        assert result.steps[2].success is True

    def test_empty_chain(self, tmp_path: Path) -> None:
        chain = PostProcessor(steps=[])
        result = chain.run(tmp_path)
        assert result.success is True
        assert result.steps == []


class TestGoModInitStep:
    def test_runs_init_tidy_download(self, tmp_path: Path) -> None:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""

        with patch("aicreator.core.postprocessor.subprocess.run", return_value=mock_proc) as mock_run:
            step = GoModInitStep(module_name="test-mod")
            result = step.execute(tmp_path)

        assert result.success is True
        # 3 calls: mod init, mod tidy, mod download
        assert mock_run.call_count == 3
        first_call = mock_run.call_args_list[0][0][0]
        assert first_call == ["go", "mod", "init", "test-mod"]

    def test_skips_init_if_go_mod_exists(self, tmp_path: Path) -> None:
        (tmp_path / "go.mod").write_text("module test\n")
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""

        with patch("aicreator.core.postprocessor.subprocess.run", return_value=mock_proc) as mock_run:
            step = GoModInitStep()
            result = step.execute(tmp_path)

        assert result.success is True
        # Only 2 calls: mod tidy, mod download (no init)
        assert mock_run.call_count == 2

    def test_timeout_handled(self, tmp_path: Path) -> None:
        with patch(
            "aicreator.core.postprocessor.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="go", timeout=60),
        ):
            step = GoModInitStep()
            result = step.execute(tmp_path)

        assert result.success is False
        assert "timed out" in (result.error or "")


class TestGofmtStep:
    def test_success(self, tmp_path: Path) -> None:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stderr = ""

        with patch("aicreator.core.postprocessor.subprocess.run", return_value=mock_proc):
            step = GofmtStep()
            result = step.execute(tmp_path)

        assert result.success is True


class TestGolangciLintStep:
    def test_warning_on_failure(self, tmp_path: Path) -> None:
        step = GolangciLintStep()
        assert step.severity == Severity.WARNING


class TestGoBuildStep:
    def test_failure_returns_stderr(self, tmp_path: Path) -> None:
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = "cannot find package"

        with patch("aicreator.core.postprocessor.subprocess.run", return_value=mock_proc):
            step = GoBuildStep()
            result = step.execute(tmp_path)

        assert result.success is False
        assert "cannot find package" in (result.error or "")

    def test_step_timeout(self, tmp_path: Path) -> None:
        with patch(
            "aicreator.core.postprocessor.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="go", timeout=120),
        ):
            step = GoBuildStep()
            result = step.execute(tmp_path)

        assert result.success is False
        assert "timed out" in (result.error or "")


class TestGoChain:
    def test_go_mod_init_runs_first(self) -> None:
        pp = go_postprocessor()
        assert len(pp.steps) == 4
        assert isinstance(pp.steps[0], GoModInitStep)
        assert isinstance(pp.steps[1], GofmtStep)
        assert isinstance(pp.steps[2], GolangciLintStep)
        assert isinstance(pp.steps[3], GoBuildStep)
