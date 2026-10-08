"""Daily-cycle decision logic (brief section 27).

``decide_next_action`` is a pure function of state + portfolio so it can be
tested exhaustively. It never performs engineering work itself; it tells the
orchestrator *what* to do next and which role prompts to load.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

ROLE_PROMPTS = {
    "start_next_project": ["prompts/orchestrator.md", "prompts/planner.md"],
    "implement_milestone": [
        "prompts/orchestrator.md",
        "prompts/engineer.md",
        "prompts/test_engineer.md",
        "prompts/evaluator.md",
        "prompts/devops.md",
        "prompts/documentation.md",
    ],
    "run_review": ["prompts/orchestrator.md", "prompts/reviewer.md"],
    "resolve_review_blockers": [
        "prompts/orchestrator.md",
        "prompts/engineer.md",
        "prompts/test_engineer.md",
    ],
    "finalize_project": ["prompts/orchestrator.md", "prompts/documentation.md"],
    "unblock_project": ["prompts/orchestrator.md"],
    "portfolio_complete": [],
    "investigate_state": ["prompts/orchestrator.md"],
}


@dataclass
class Action:
    action: str
    project: str | None = None
    milestone: str | None = None
    reason: str = ""
    prompts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _action(name: str, **kwargs: Any) -> Action:
    return Action(action=name, prompts=list(ROLE_PROMPTS[name]), **kwargs)


def next_queued_project(state: dict[str, Any], portfolio: dict[str, Any]) -> str | None:
    """First project in portfolio order that has not been started or completed."""
    for entry in sorted(portfolio["projects"], key=lambda p: p.get("order", 0)):
        status = state["projects"].get(entry["id"], {}).get("status", "queued")
        if status == "queued":
            return str(entry["id"])
    return None


def _blocking_findings(project: dict[str, Any]) -> list[dict[str, Any]]:
    findings = project.get("review", {}).get("findings", [])
    return [f for f in findings if f["severity"] in ("CRITICAL", "MAJOR") and not f.get("resolved")]


def decide_next_action(state: dict[str, Any], portfolio: dict[str, Any]) -> Action:
    active_id = state.get("active_project")
    if active_id is None:
        nxt = next_queued_project(state, portfolio)
        if nxt is None:
            return _action("portfolio_complete", reason="no queued projects remain")
        return _action("start_next_project", project=nxt, reason="no active project")

    project = state["projects"][active_id]
    status = project["status"]
    if status == "blocked":
        return _action(
            "unblock_project",
            project=active_id,
            reason="; ".join(project.get("blockers", [])) or "project marked blocked",
        )
    if status == "complete":
        return _action(
            "investigate_state",
            project=active_id,
            reason="active project is already complete; clear active_project",
        )

    milestones = project.get("milestones", [])
    open_milestones = [m for m in milestones if m["status"] != "done"]
    if open_milestones:
        current = next((m for m in open_milestones if m["status"] == "in_progress"), None)
        target = current or open_milestones[0]
        if target["status"] == "blocked":
            return _action(
                "unblock_project",
                project=active_id,
                milestone=target["id"],
                reason=f"milestone {target['id']} is blocked",
            )
        return _action(
            "implement_milestone",
            project=active_id,
            milestone=target["id"],
            reason=f"{len(open_milestones)} milestone(s) not done",
        )

    review = project.get("review", {})
    if not review.get("last_run"):
        return _action("run_review", project=active_id, reason="all milestones done, not reviewed")
    blockers = _blocking_findings(project)
    if blockers:
        return _action(
            "resolve_review_blockers",
            project=active_id,
            reason=f"{len(blockers)} unresolved CRITICAL/MAJOR finding(s)",
        )
    if review.get("passed"):
        return _action("finalize_project", project=active_id, reason="review passed")
    return _action(
        "run_review", project=active_id, reason="findings resolved; re-run review to confirm"
    )


def finalize_project(state: dict[str, Any], project_id: str, date: str) -> None:
    """Mark a reviewed project complete and clear the active slot."""
    project = state["projects"][project_id]
    if any(m["status"] != "done" for m in project.get("milestones", [])):
        raise ValueError(f"{project_id}: cannot finalize with open milestones")
    if not project.get("review", {}).get("passed") or _blocking_findings(project):
        raise ValueError(f"{project_id}: cannot finalize without a passing review")
    project["status"] = "complete"
    project["completed"] = date
    if state.get("active_project") == project_id:
        state["active_project"] = None
