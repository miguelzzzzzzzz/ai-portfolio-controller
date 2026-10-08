"""Load, validate, mutate, and save ``state.json`` and ``portfolio.yaml``.

The state file is the single source of truth for what the orchestrator does
next. All writes go through :func:`save_state`, which validates first and
writes atomically so an interrupted run cannot leave a half-written file.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / "state.json"
PORTFOLIO_PATH = ROOT / "portfolio.yaml"

PROJECT_STATUSES = ("queued", "in_progress", "in_review", "blocked", "complete")
MILESTONE_STATUSES = ("planned", "in_progress", "done", "blocked")
SEVERITIES = ("CRITICAL", "MAJOR", "MINOR")
SCHEMA_VERSION = 1


class StateError(ValueError):
    """Raised when state.json or portfolio.yaml is inconsistent."""


def now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def load_portfolio(path: Path = PORTFOLIO_PATH) -> dict[str, Any]:
    data: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("projects"), list):
        raise StateError("portfolio.yaml must be a mapping with a 'projects' list")
    ids = [p.get("id") for p in data["projects"]]
    if len(ids) != len(set(ids)) or not all(isinstance(i, str) and i for i in ids):
        raise StateError("portfolio.yaml project ids must be unique non-empty strings")
    return data


def load_state(path: Path = STATE_PATH) -> dict[str, Any]:
    state = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        raise StateError("state.json must contain a JSON object")
    validate_state(state)
    return state


def validate_state(state: dict[str, Any]) -> None:
    if state.get("schema_version") != SCHEMA_VERSION:
        raise StateError(f"unsupported schema_version {state.get('schema_version')!r}")
    projects = state.get("projects")
    if not isinstance(projects, dict):
        raise StateError("'projects' must be a mapping")
    active = state.get("active_project")
    if active is not None and active not in projects:
        raise StateError(f"active_project {active!r} is not in projects")
    for pid, project in projects.items():
        status = project.get("status")
        if status not in PROJECT_STATUSES:
            raise StateError(f"{pid}: invalid status {status!r}")
        seen: set[str] = set()
        for milestone in project.get("milestones", []):
            if milestone.get("status") not in MILESTONE_STATUSES:
                raise StateError(f"{pid}/{milestone.get('id')}: invalid milestone status")
            if milestone["id"] in seen:
                raise StateError(f"{pid}: duplicate milestone id {milestone['id']}")
            seen.add(milestone["id"])
        for finding in project.get("review", {}).get("findings", []):
            if finding.get("severity") not in SEVERITIES:
                raise StateError(f"{pid}: invalid review severity {finding.get('severity')!r}")
    in_progress = [
        pid for pid, p in projects.items() if p["status"] in ("in_progress", "in_review")
    ]
    if len(in_progress) > 1:
        raise StateError(f"more than one active project: {in_progress}")
    if not isinstance(state.get("daily_log"), list):
        raise StateError("'daily_log' must be a list")


def save_state(state: dict[str, Any], path: Path = STATE_PATH) -> None:
    validate_state(state)
    state["updated_at"] = now_iso()
    payload = json.dumps(state, indent=2, ensure_ascii=False) + "\n"
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".state-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def get_project(state: dict[str, Any], project_id: str) -> dict[str, Any]:
    try:
        project: dict[str, Any] = state["projects"][project_id]
    except KeyError as exc:
        raise StateError(f"unknown project {project_id!r}") from exc
    return project


def set_milestone_status(
    state: dict[str, Any], project_id: str, milestone_id: str, status: str, date: str | None = None
) -> None:
    if status not in MILESTONE_STATUSES:
        raise StateError(f"invalid milestone status {status!r}")
    project = get_project(state, project_id)
    for milestone in project["milestones"]:
        if milestone["id"] == milestone_id:
            milestone["status"] = status
            milestone["completed"] = (date or now_iso()[:10]) if status == "done" else None
            return
    raise StateError(f"{project_id}: unknown milestone {milestone_id!r}")


@dataclass(frozen=True)
class DailySummary:
    """Section 29 daily summary. Every field must come from an actual run."""

    date: str
    project: str
    milestone: str
    work_completed: list[str]
    tests: str
    evaluation: str
    commits: list[str]
    blockers: list[str]
    next_task: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "project": self.project,
            "milestone": self.milestone,
            "work_completed": self.work_completed,
            "tests": self.tests,
            "evaluation": self.evaluation,
            "commits": self.commits,
            "remaining_blockers": self.blockers,
            "next_recommended_task": self.next_task,
        }


def append_daily_summary(state: dict[str, Any], summary: DailySummary) -> None:
    if summary.project not in state["projects"]:
        raise StateError(f"unknown project {summary.project!r}")
    if not summary.work_completed:
        raise StateError("a daily summary needs at least one completed work item")
    state["daily_log"].append(summary.to_dict())


def render_log_markdown(state: dict[str, Any]) -> str:
    """Render the daily log (newest first) as Markdown for LOG.md."""
    lines = [
        "# Daily log",
        "",
        "Generated from `state.json` by `scripts/update_state.py render-log`. Do not edit by hand.",
        "",
    ]
    for entry in reversed(state["daily_log"]):
        lines += [
            f"## {entry['date']} - {entry['project']} - {entry['milestone']}",
            "",
            "Work completed:",
            *[f"- {item}" for item in entry["work_completed"]],
            "",
            f"Tests: {entry['tests']}",
            "",
            f"Evaluation: {entry['evaluation']}",
            "",
            "Commits:",
            *[f"- {c}" for c in entry["commits"]],
            "",
            "Remaining blockers: " + ("; ".join(entry["remaining_blockers"]) or "none"),
            "",
            f"Next recommended task: {entry['next_recommended_task']}",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"
