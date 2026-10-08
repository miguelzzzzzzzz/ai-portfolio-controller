"""Start projects: register them in state and optionally scaffold files / a GitHub repo."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from controller.state import StateError

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"

DEFAULT_MILESTONES = [
    ("M1", "Infrastructure and first core capability"),
    ("M2", "Core functionality complete"),
    ("M3", "Evaluation harness and measured results"),
    ("M4", "API, Docker, CI hardening"),
    ("M5", "Documentation and release"),
]


def portfolio_entry(portfolio: dict[str, Any], project_id: str) -> dict[str, Any]:
    for entry in portfolio["projects"]:
        if entry["id"] == project_id:
            return dict(entry)
    raise StateError(f"{project_id!r} is not in portfolio.yaml")


def repo_slug(entry: dict[str, Any]) -> str:
    """GitHub repository name for a catalog entry (falls back to the id)."""
    return str(entry.get("repo") or entry["id"])


def register_project(
    state: dict[str, Any],
    portfolio: dict[str, Any],
    project_id: str,
    date: str,
    *,
    force: bool = False,
) -> dict[str, Any]:
    """Add the project to state as in_progress and make it the active project."""
    entry = portfolio_entry(portfolio, project_id)
    active = state.get("active_project")
    if active is not None and active != project_id and not force:
        raise StateError(f"project {active!r} is still active; finish it or pass force")
    existing = state["projects"].get(project_id)
    if existing is not None and existing["status"] not in ("queued",):
        raise StateError(f"{project_id!r} already has status {existing['status']!r}")
    milestones = entry.get("milestones") or [
        {"id": mid, "title": title} for mid, title in DEFAULT_MILESTONES
    ]
    owner = portfolio.get("owner", "")
    slug = repo_slug(entry)
    project: dict[str, Any] = {
        "status": "in_progress",
        "title": entry.get("title", project_id),
        "repo": f"https://github.com/{owner}/{slug}" if owner else None,
        "started": date,
        "completed": None,
        "milestones": [
            {"id": m["id"], "title": m["title"], "status": "planned", "completed": None}
            for m in milestones
        ],
        "review": {"last_run": None, "passed": False, "findings": []},
        "last_ci": None,
        "blockers": [],
    }
    state["projects"][project_id] = project
    state["active_project"] = project_id
    return project


def scaffold_project(directory: Path, entry: dict[str, Any]) -> list[Path]:
    """Copy document templates into a new project directory (never overwrites)."""
    directory.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    values = {
        "{{PROJECT_ID}}": entry["id"],
        "{{TITLE}}": entry.get("title", entry["id"]),
        "{{SUMMARY}}": entry.get("summary", ""),
    }
    for template in sorted(TEMPLATES.glob("*.md")):
        target = directory / template.name
        if target.exists():
            continue
        text = template.read_text(encoding="utf-8")
        for key, value in values.items():
            text = text.replace(key, value)
        target.write_text(text, encoding="utf-8")
        written.append(target)
    return written


def create_github_repo(
    name: str, description: str, token_env: str = "PORTFOLIO_GITHUB_TOKEN"
) -> str:
    """Create a public repo for the authenticated user; return its HTML URL.

    The token is read from the environment at call time and never logged.
    """
    token = os.environ.get(token_env)
    if not token:
        raise StateError(f"environment variable {token_env} is not set")
    body = json.dumps({"name": name, "description": description, "private": False}).encode()
    request = urllib.request.Request(
        "https://api.github.com/user/repos",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return str(json.load(response)["html_url"])
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise StateError(f"GitHub repo creation failed ({exc.code}): {detail}") from exc
