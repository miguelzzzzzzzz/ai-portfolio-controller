"""End-to-end tests of the CLI scripts against temporary state files."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import create_project
import pytest
import run_daily_cycle
import update_state

PID = "production-rag-engine"


def test_full_cli_flow(
    state_path: Path,
    portfolio_path: Path,
    tmp_path: Path,
    capsys,  # type: ignore[no-untyped-def]
) -> None:
    common = ["--state", str(state_path), "--portfolio", str(portfolio_path)]

    assert run_daily_cycle.main(common) == 0
    decision = json.loads(capsys.readouterr().out)
    assert decision["action"] == "start_next_project" and decision["applied"] is False

    scaffold = tmp_path / "proj"
    assert create_project.main([*common, "--date", "2026-10-09", "--scaffold", str(scaffold)]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["started"] == PID
    assert (scaffold / "PROJECT_SPEC.md").read_text().startswith(f"# PROJECT_SPEC: {PID}")

    # a second start is refused while the first is active
    assert create_project.main([*common, "agentic-research-platform"]) == 1
    assert "still active" in capsys.readouterr().err

    log_file = tmp_path / "LOG.md"
    st = ["--state", str(state_path)]
    assert update_state.main([*st, "milestone", PID, "M1", "done", "--date", "2026-10-09"]) == 0
    assert (
        update_state.main(
            [*st, "ci", PID, "--conclusion", "success", "--url", "https://example.com/run/1"]
        )
        == 0
    )
    assert update_state.main(
        [
            *st, "log", "--date", "2026-10-09", "--project", PID, "--milestone", "M1",
            "--work", "loaders", "--work", "chunkers", "--tests", "98 passed",
            "--evaluation", "not run", "--commit", "abc1234 feat: x", "--next", "M2",
            "--log-file", str(log_file),
        ]
    ) == 0  # fmt: skip
    assert "- chunkers" in log_file.read_text()

    capsys.readouterr()
    assert update_state.main([*st, "show"]) == 0
    shown = json.loads(capsys.readouterr().out)
    assert shown["projects"][PID]["milestones"]["M1"] == "done"
    assert shown["projects"][PID]["last_ci"] == "success"
    assert shown["log_entries"] == 1

    assert run_daily_cycle.main(common) == 0
    decision = json.loads(capsys.readouterr().out)
    assert (decision["action"], decision["milestone"]) == ("implement_milestone", "M2")


def test_errors_are_reported_not_raised(state_path: Path, capsys) -> None:  # type: ignore[no-untyped-def]
    assert update_state.main(["--state", str(state_path), "milestone", "ghost", "M1", "done"]) == 1
    assert "unknown project" in capsys.readouterr().err


@pytest.mark.parametrize(
    "script", ["update_state.py", "create_project.py", "run_daily_cycle.py", "review_project.py"]
)
def test_scripts_run_as_standalone_programs(script: str, tmp_path: Path) -> None:
    """Scripts must work via `python scripts/x.py` from any cwd, without installation."""
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, str(root / "scripts" / script), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 0, result.stderr
    assert "usage:" in result.stdout
