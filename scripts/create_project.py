#!/usr/bin/env python3
"""Start the next (or a named) portfolio project.

Registers the project in state.json as the active project, optionally copies
the document templates into a local directory, and optionally creates the
public GitHub repository (token read from PORTFOLIO_GITHUB_TOKEN; never printed).

Examples:
  python scripts/create_project.py --dry-run
  python scripts/create_project.py agentic-research-platform --scaffold ../agentic-research-platform
  python scripts/create_project.py --scaffold ../next --create-repo
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import _bootstrap  # noqa: F401

from controller.cycle import next_queued_project
from controller.projects import (
    create_github_repo,
    portfolio_entry,
    register_project,
    scaffold_project,
)
from controller.state import (
    PORTFOLIO_PATH,
    STATE_PATH,
    StateError,
    load_portfolio,
    load_state,
    save_state,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Start a portfolio project")
    parser.add_argument("project", nargs="?", help="project id (default: next queued)")
    parser.add_argument("--state", type=Path, default=STATE_PATH)
    parser.add_argument("--portfolio", type=Path, default=PORTFOLIO_PATH)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--scaffold", type=Path, help="directory to copy templates into")
    parser.add_argument("--create-repo", action="store_true", help="create the GitHub repo")
    parser.add_argument(
        "--force", action="store_true", help="allow starting while another is active"
    )
    parser.add_argument("--dry-run", action="store_true", help="show what would happen")
    args = parser.parse_args(argv)

    try:
        state = load_state(args.state)
        portfolio = load_portfolio(args.portfolio)
        project_id = args.project or next_queued_project(state, portfolio)
        if project_id is None:
            print("no queued projects remain")
            return 0
        entry = portfolio_entry(portfolio, project_id)
        if args.dry_run:
            print(json.dumps({"would_start": project_id, "title": entry.get("title")}, indent=2))
            return 0
        register_project(state, portfolio, project_id, args.date, force=args.force)
        if args.create_repo:
            url = create_github_repo(project_id, entry.get("summary", "")[:350])
            state["projects"][project_id]["repo"] = url
        written = scaffold_project(args.scaffold, entry) if args.scaffold else []
        save_state(state, args.state)
    except StateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "started": project_id,
                "repo": state["projects"][project_id]["repo"],
                "scaffolded": [str(p) for p in written],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
