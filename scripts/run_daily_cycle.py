#!/usr/bin/env python3
"""Decide (and optionally apply) the next action of the daily cycle (section 27).

Prints a JSON decision: action, project, milestone, reason, and the role prompts
the orchestrator should load. With --apply, performs the state-only transitions
(start_next_project, finalize_project). Engineering work itself is done by the
orchestrator and its sub-agents following the prompts.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import _bootstrap  # noqa: F401

from controller.cycle import decide_next_action, finalize_project
from controller.projects import register_project
from controller.state import (
    PORTFOLIO_PATH,
    STATE_PATH,
    StateError,
    load_portfolio,
    load_state,
    save_state,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--state", type=Path, default=STATE_PATH)
    parser.add_argument("--portfolio", type=Path, default=PORTFOLIO_PATH)
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--apply", action="store_true", help="apply state-only transitions")
    args = parser.parse_args(argv)

    try:
        state = load_state(args.state)
        portfolio = load_portfolio(args.portfolio)
        decision = decide_next_action(state, portfolio)
        applied = False
        if args.apply and decision.project:
            if decision.action == "start_next_project":
                register_project(state, portfolio, decision.project, args.date)
                applied = True
            elif decision.action == "finalize_project":
                finalize_project(state, decision.project, args.date)
                applied = True
            if applied:
                save_state(state, args.state)
    except (StateError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({**decision.to_dict(), "applied": applied}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
