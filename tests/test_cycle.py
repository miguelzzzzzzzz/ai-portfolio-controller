from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from controller.cycle import decide_next_action, finalize_project, next_queued_project
from controller.projects import register_project
from controller.state import load_portfolio, set_milestone_status

PID = "production-rag-engine"


@pytest.fixture
def portfolio(portfolio_path: Path) -> dict[str, Any]:
    return load_portfolio(portfolio_path)


@pytest.fixture
def active_state(empty_state: dict[str, Any], portfolio: dict[str, Any]) -> dict[str, Any]:
    register_project(empty_state, portfolio, PID, "2026-10-09")
    return empty_state


def _finish_milestones(state: dict[str, Any]) -> None:
    for m in state["projects"][PID]["milestones"]:
        set_milestone_status(state, PID, m["id"], "done", "2026-10-09")


def test_no_active_project_starts_first_queued(
    empty_state: dict[str, Any], portfolio: dict[str, Any]
) -> None:
    action = decide_next_action(empty_state, portfolio)
    assert (action.action, action.project) == ("start_next_project", PID)
    assert "prompts/planner.md" in action.prompts


def test_open_milestone_is_implemented_in_order(
    active_state: dict[str, Any], portfolio: dict[str, Any]
) -> None:
    action = decide_next_action(active_state, portfolio)
    assert (action.action, action.milestone) == ("implement_milestone", "M1")
    set_milestone_status(active_state, PID, "M1", "done")
    set_milestone_status(active_state, PID, "M3", "in_progress")
    # an in-progress milestone takes priority over earlier planned ones
    assert decide_next_action(active_state, portfolio).milestone == "M3"


def test_blocked_milestone_or_project_requests_unblocking(
    active_state: dict[str, Any], portfolio: dict[str, Any]
) -> None:
    set_milestone_status(active_state, PID, "M1", "blocked")
    assert decide_next_action(active_state, portfolio).action == "unblock_project"
    active_state["projects"][PID]["status"] = "blocked"
    active_state["projects"][PID]["blockers"] = ["needs API key"]
    action = decide_next_action(active_state, portfolio)
    assert action.action == "unblock_project" and action.reason == "needs API key"


def test_review_lifecycle_to_completion(
    active_state: dict[str, Any], portfolio: dict[str, Any]
) -> None:
    _finish_milestones(active_state)
    assert decide_next_action(active_state, portfolio).action == "run_review"

    review = active_state["projects"][PID]["review"]
    review.update(
        last_run="2026-10-20T00:00:00+00:00",
        passed=False,
        findings=[
            {"severity": "MAJOR", "check": "x", "message": "no Dockerfile", "resolved": False},
            {"severity": "MINOR", "check": "y", "message": "nit", "resolved": False},
        ],
    )
    assert decide_next_action(active_state, portfolio).action == "resolve_review_blockers"

    review["findings"][0]["resolved"] = True
    assert decide_next_action(active_state, portfolio).action == "run_review"

    review.update(passed=True, findings=[])
    assert decide_next_action(active_state, portfolio).action == "finalize_project"
    finalize_project(active_state, PID, "2026-10-21")
    assert active_state["active_project"] is None
    assert active_state["projects"][PID]["status"] == "complete"

    action = decide_next_action(active_state, portfolio)
    assert (action.action, action.project) == ("start_next_project", "llm-eval-harness")


def test_finalize_refuses_without_passing_review(
    active_state: dict[str, Any], portfolio: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="open milestones"):
        finalize_project(active_state, PID, "2026-10-21")
    _finish_milestones(active_state)
    with pytest.raises(ValueError, match="passing review"):
        finalize_project(active_state, PID, "2026-10-21")


def test_portfolio_complete_when_nothing_is_queued(
    empty_state: dict[str, Any], portfolio: dict[str, Any]
) -> None:
    for entry in portfolio["projects"]:
        empty_state["projects"][entry["id"]] = {"status": "complete", "milestones": []}
    assert next_queued_project(empty_state, portfolio) is None
    assert decide_next_action(empty_state, portfolio).action == "portfolio_complete"
