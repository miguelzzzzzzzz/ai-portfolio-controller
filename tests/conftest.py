from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture
def portfolio_path(tmp_path: Path) -> Path:
    target = tmp_path / "portfolio.yaml"
    shutil.copy(ROOT / "portfolio.yaml", target)
    return target


@pytest.fixture
def empty_state() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "updated_at": None,
        "active_project": None,
        "projects": {},
        "daily_log": [],
    }


@pytest.fixture
def state_path(tmp_path: Path, empty_state: dict[str, Any]) -> Path:
    path = tmp_path / "state.json"
    path.write_text(json.dumps(empty_state))
    return path


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        env={
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@example.com",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@example.com",
            "PATH": "/usr/bin:/bin:/usr/local/bin",
        },
    )
