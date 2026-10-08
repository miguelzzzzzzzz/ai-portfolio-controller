#!/usr/bin/env python3
"""Run the automated completion-gate review on a project checkout.

Examples:
  python scripts/review_project.py ../production-rag-engine
  python scripts/review_project.py ../production-rag-engine --run-checks \
      --record production-rag-engine

Exit code: 0 if no CRITICAL/MAJOR findings, 1 otherwise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import _bootstrap  # noqa: F401

from controller.review import passes, review_repository
from controller.state import (
    PORTFOLIO_PATH,
    STATE_PATH,
    StateError,
    get_project,
    load_portfolio,
    load_state,
    now_iso,
    save_state,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Automated completion-gate review")
    parser.add_argument("repo", type=Path)
    parser.add_argument("--run-checks", action="store_true", help="run quality commands")
    parser.add_argument("--no-eval-required", action="store_true")
    parser.add_argument("--record", metavar="PROJECT_ID", help="store results in state.json")
    parser.add_argument("--state", type=Path, default=STATE_PATH)
    parser.add_argument("--portfolio", type=Path, default=PORTFOLIO_PATH)
    args = parser.parse_args(argv)

    portfolio = load_portfolio(args.portfolio)
    commands = portfolio.get("quality", {}).get("commands", []) if args.run_checks else None
    try:
        findings = review_repository(
            args.repo, requires_eval=not args.no_eval_required, quality_commands=commands
        )
    except RuntimeError as exc:  # not a git repository, git unavailable, ...
        print(f"error: {exc}", file=sys.stderr)
        return 2
    ok = passes(findings)
    print(f"# Review: {args.repo.resolve().name}\n")
    print(f"Result: {'PASS' if ok else 'FAIL'} ({len(findings)} finding(s))\n")
    for finding in findings:
        print(f"- **{finding.severity}** [{finding.check}] {finding.message}")

    if args.record:
        try:
            state = load_state(args.state)
            get_project(state, args.record)["review"] = {
                "last_run": now_iso(),
                "passed": ok,
                "findings": [f.to_dict() for f in findings],
            }
            save_state(state, args.state)
        except StateError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
