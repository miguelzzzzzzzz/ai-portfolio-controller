#!/usr/bin/env python3
"""Inspect and update state.json.

Examples:
  python scripts/update_state.py show
  python scripts/update_state.py milestone production-rag-engine M1 done
  python scripts/update_state.py project-status production-rag-engine blocked \
      --blocker "needs API key"
  python scripts/update_state.py ci production-rag-engine --conclusion success --url https://...
  python scripts/update_state.py log --project production-rag-engine --milestone M1 \
      --work "implemented loaders" --tests "98 passed" --evaluation "not run" \
      --commit "abc1234 feat: ..." --next "M2 vector index"
  python scripts/update_state.py render-log
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

import _bootstrap  # noqa: F401

from controller.state import (
    MILESTONE_STATUSES,
    PROJECT_STATUSES,
    ROOT,
    STATE_PATH,
    DailySummary,
    StateError,
    append_daily_summary,
    get_project,
    load_state,
    now_iso,
    render_log_markdown,
    save_state,
    set_milestone_status,
)

LOG_PATH = ROOT / "LOG.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect and update state.json")
    parser.add_argument("--state", type=Path, default=STATE_PATH)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("show", help="print a summary of the current state")

    milestone = sub.add_parser("milestone", help="set a milestone status")
    milestone.add_argument("project")
    milestone.add_argument("milestone")
    milestone.add_argument("status", choices=MILESTONE_STATUSES)
    milestone.add_argument("--date", default=None)

    status = sub.add_parser("project-status", help="set a project status")
    status.add_argument("project")
    status.add_argument("status", choices=PROJECT_STATUSES)
    status.add_argument("--blocker", action="append", default=[])

    ci = sub.add_parser("ci", help="record the latest CI result for a project")
    ci.add_argument("project")
    ci.add_argument("--conclusion", required=True)
    ci.add_argument("--url", required=True)
    ci.add_argument("--sha", default=None)

    log = sub.add_parser("log", help="append a daily summary (section 29)")
    log.add_argument("--date", default=date.today().isoformat())
    log.add_argument("--project", required=True)
    log.add_argument("--milestone", required=True)
    log.add_argument("--work", action="append", required=True)
    log.add_argument("--tests", required=True)
    log.add_argument("--evaluation", required=True)
    log.add_argument("--commit", action="append", default=[])
    log.add_argument("--blocker", action="append", default=[])
    log.add_argument("--next", dest="next_task", required=True)
    log.add_argument("--log-file", type=Path, default=LOG_PATH)

    render = sub.add_parser("render-log", help="regenerate LOG.md from state.json")
    render.add_argument("--log-file", type=Path, default=LOG_PATH)
    return parser


def show(state: dict[str, object]) -> str:
    return json.dumps(
        {
            "active_project": state["active_project"],
            "projects": {
                pid: {
                    "status": p["status"],
                    "milestones": {m["id"]: m["status"] for m in p.get("milestones", [])},
                    "last_ci": (p.get("last_ci") or {}).get("conclusion"),
                }
                for pid, p in state["projects"].items()  # type: ignore[attr-defined]
            },
            "log_entries": len(state["daily_log"]),  # type: ignore[arg-type]
        },
        indent=2,
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        state = load_state(args.state)
        if args.command == "show":
            print(show(state))
            return 0
        if args.command == "milestone":
            set_milestone_status(state, args.project, args.milestone, args.status, args.date)
        elif args.command == "project-status":
            project = get_project(state, args.project)
            project["status"] = args.status
            project["blockers"] = args.blocker if args.status == "blocked" else []
        elif args.command == "ci":
            get_project(state, args.project)["last_ci"] = {
                "conclusion": args.conclusion,
                "url": args.url,
                "sha": args.sha,
                "recorded_at": now_iso(),
            }
        elif args.command == "log":
            append_daily_summary(
                state,
                DailySummary(
                    date=args.date,
                    project=args.project,
                    milestone=args.milestone,
                    work_completed=args.work,
                    tests=args.tests,
                    evaluation=args.evaluation,
                    commits=args.commit,
                    blockers=args.blocker,
                    next_task=args.next_task,
                ),
            )
        if args.command in ("log", "render-log"):
            args.log_file.write_text(render_log_markdown(state), encoding="utf-8")
        if args.command != "render-log":
            save_state(state, args.state)
    except StateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
