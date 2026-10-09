from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from controller.projects import register_project
from controller.state import (
    DailySummary,
    StateError,
    append_daily_summary,
    load_portfolio,
    load_state,
    render_log_markdown,
    save_state,
    set_milestone_status,
    validate_state,
)

ROOT = Path(__file__).resolve().parent.parent


def test_repository_state_and_portfolio_are_valid() -> None:
    validate_state(json.loads((ROOT / "state.json").read_text()))
    portfolio = load_portfolio(ROOT / "portfolio.yaml")
    assert 8 <= len(portfolio["projects"]) <= 10


BRIEF_QUEUE = [
    "production-rag-engine",
    "agentic-research-platform",
    "llm-evaluation-lab",
    "multimodal-document-intelligence",
    "mlops-fraud-detection",
    "llm-finetuning-lab",
    "ai-observability-platform",
    "semantic-search-engine",
    "voice-ai-agent",
    "ai-inference-benchmark",
]


def test_catalog_matches_the_briefs_ordered_queue() -> None:
    """Guards ADR-006: ids and order come from the owner's brief, section 5."""
    projects = load_portfolio(ROOT / "portfolio.yaml")["projects"]
    ordered = sorted(projects, key=lambda p: p["order"])
    assert [p["id"] for p in ordered] == BRIEF_QUEUE
    assert [p["order"] for p in ordered] == list(range(1, 11))


EXPECTED_REPOS = {
    "production-rag-engine": ("CitationNeeded", "Citation Needed"),
    "agentic-research-platform": ("RabbitHole", "Rabbit Hole"),
    "llm-evaluation-lab": ("TrustIssues", "Trust Issues"),
    "multimodal-document-intelligence": ("PaperTrail", "Paper Trail"),
    "mlops-fraud-detection": ("SusTransactions", "Sus Transactions"),
    "llm-finetuning-lab": ("LoraAndOrder", "LoRA & Order"),
    "ai-observability-platform": ("WhoSpentMyTokens", "Who Spent My Tokens"),
    "semantic-search-engine": ("HNSWFromScratch", "HNSW From Scratch"),
    "voice-ai-agent": ("InterruptMe", "Interrupt Me"),
    "ai-inference-benchmark": ("QuantLeap", "Quant Leap"),
}


def test_catalog_repo_slugs_and_titles() -> None:
    """Guards ADR-014: owner-chosen repository names and display titles."""
    projects = load_portfolio(ROOT / "portfolio.yaml")["projects"]
    assert {p["id"]: (p["repo"], p["title"]) for p in projects} == EXPECTED_REPOS


def test_llm_policy_follows_adr_016() -> None:
    """Cline Pass DeepSeek is the default, CI never calls a model, no spend cap, key only by env."""
    portfolio = load_portfolio(ROOT / "portfolio.yaml")
    llm = portfolio["llm"]
    assert llm["default"]["model"] == "cline-pass/deepseek-v4.1-flash"
    assert llm["default"]["billing"] == "cline-pass"
    assert llm["default"]["cost_field_meaning"] == "reference_price"
    assert llm["runaway_guard"]["stop_on_pass_limit"] is True
    assert llm["default"]["api_key_env"] == "CLINE_API_KEY"
    assert llm["default"]["min_max_tokens"] >= 1000
    assert llm["default"]["spend_cap_usd"] is None
    assert llm["ci"] == "recorded_replies_only"
    assert portfolio["policies"]["paid_api_budget_usd"] == 0
    spend_log = Path(llm["cost_logging"]["spend_log"])
    assert ROOT not in spend_log.parents  # the shared spend log is never inside a repo


@pytest.mark.parametrize(
    ("repos", "message"),
    [
        (["Same", "same"], "unique"),
        (["Lora & Order", "Ok"], "invalid GitHub repository names"),
        (["has space", "Ok"], "invalid GitHub repository names"),
    ],
)
def test_invalid_repo_slugs_are_rejected(tmp_path: Path, repos: list[str], message: str) -> None:
    catalog = {"projects": [{"id": f"p{i}", "repo": r} for i, r in enumerate(repos)]}
    path = tmp_path / "portfolio.yaml"
    path.write_text(yaml.safe_dump(catalog))
    with pytest.raises(StateError, match=message):
        load_portfolio(path)


def test_project_02_uses_the_planners_milestones(
    empty_state: dict[str, Any], portfolio_path: Path
) -> None:
    project = register_project(
        empty_state, load_portfolio(portfolio_path), "agentic-research-platform", "2026-10-09"
    )
    titles = [m["title"] for m in project["milestones"]]
    assert len(titles) == 7
    assert titles[0] == "Scaffold, tool contracts, registry, calculator, trace schema"
    assert titles[-1] == "Container, CI image smoke eval, docs, v0.1.0 release"


def test_register_project_uses_portfolio_milestones(
    empty_state: dict[str, Any], portfolio_path: Path
) -> None:
    portfolio = load_portfolio(portfolio_path)
    project = register_project(empty_state, portfolio, "production-rag-engine", "2026-10-09")
    assert empty_state["active_project"] == "production-rag-engine"
    assert project["repo"] == "https://github.com/miguelzzzzzzzz/CitationNeeded"
    assert project["title"] == "Citation Needed"
    assert [m["id"] for m in project["milestones"]] == [f"M{i}" for i in range(1, 8)]
    validate_state(empty_state)


def test_register_refuses_second_active_project(
    empty_state: dict[str, Any], portfolio_path: Path
) -> None:
    portfolio = load_portfolio(portfolio_path)
    register_project(empty_state, portfolio, "production-rag-engine", "2026-10-09")
    with pytest.raises(StateError, match="still active"):
        register_project(empty_state, portfolio, "agentic-research-platform", "2026-10-09")


def test_project_without_milestones_gets_defaults(
    empty_state: dict[str, Any], portfolio_path: Path
) -> None:
    portfolio = load_portfolio(portfolio_path)
    project = register_project(
        empty_state, portfolio, "multimodal-document-intelligence", "2026-10-09"
    )
    assert [m["id"] for m in project["milestones"]] == ["M1", "M2", "M3", "M4", "M5"]


def test_project_03_uses_the_planners_eight_milestones(
    empty_state: dict[str, Any], portfolio_path: Path
) -> None:
    project = register_project(
        empty_state, load_portfolio(portfolio_path), "llm-evaluation-lab", "2026-10-09"
    )
    assert [m["id"] for m in project["milestones"]] == [f"M{i}" for i in range(1, 9)]
    assert project["milestones"][-1]["title"].startswith("Container, CI gate workflow")


def test_milestone_status_and_completion_date(
    empty_state: dict[str, Any], portfolio_path: Path
) -> None:
    register_project(
        empty_state, load_portfolio(portfolio_path), "production-rag-engine", "2026-10-09"
    )
    set_milestone_status(empty_state, "production-rag-engine", "M1", "done", "2026-10-09")
    m1 = empty_state["projects"]["production-rag-engine"]["milestones"][0]
    assert (m1["status"], m1["completed"]) == ("done", "2026-10-09")
    with pytest.raises(StateError, match="unknown milestone"):
        set_milestone_status(empty_state, "production-rag-engine", "M99", "done")
    with pytest.raises(StateError, match="invalid milestone status"):
        set_milestone_status(empty_state, "production-rag-engine", "M1", "finished")


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda s: s.update(schema_version=2), "schema_version"),
        (lambda s: s.update(active_project="ghost"), "not in projects"),
        (lambda s: s["projects"]["p"].update(status="weird"), "invalid status"),
        (lambda s: s["projects"].update(q={"status": "in_progress"}), "more than one active"),
        (lambda s: s.update(daily_log={}), "daily_log"),
    ],
)
def test_invalid_states_are_rejected(
    empty_state: dict[str, Any], mutate: Any, message: str
) -> None:
    empty_state["projects"]["p"] = {"status": "in_progress", "milestones": []}
    empty_state["active_project"] = "p"
    validate_state(empty_state)
    mutate(empty_state)
    with pytest.raises(StateError, match=message):
        validate_state(empty_state)


def test_save_is_validated_and_atomic(tmp_path: Path, empty_state: dict[str, Any]) -> None:
    path = tmp_path / "state.json"
    save_state(empty_state, path)
    assert load_state(path)["updated_at"] is not None
    empty_state["active_project"] = "ghost"
    with pytest.raises(StateError):
        save_state(empty_state, path)
    assert load_state(path)["active_project"] is None  # previous file untouched
    assert not list(tmp_path.glob(".state-*"))


def test_daily_summary_round_trip_and_rendering(
    empty_state: dict[str, Any], portfolio_path: Path
) -> None:
    register_project(
        empty_state, load_portfolio(portfolio_path), "production-rag-engine", "2026-10-09"
    )
    summary = DailySummary(
        date="2026-10-09",
        project="production-rag-engine",
        milestone="M1",
        work_completed=["implemented loaders"],
        tests="10 passed",
        evaluation="not run",
        commits=["abc1234 feat: x"],
        blockers=[],
        next_task="M2",
    )
    append_daily_summary(empty_state, summary)
    rendered = render_log_markdown(empty_state)
    assert "## 2026-10-09 - production-rag-engine - M1" in rendered
    assert "Remaining blockers: none" in rendered
    with pytest.raises(StateError, match="at least one"):
        append_daily_summary(
            empty_state,
            DailySummary("2026-10-09", "production-rag-engine", "M1", [], "", "", [], [], ""),
        )
