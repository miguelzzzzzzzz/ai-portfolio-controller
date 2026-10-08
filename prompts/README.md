# Role prompts

Reusable instructions for the sub-agents the orchestrator delegates to. Each
prompt is self-contained: hand a sub-agent the role prompt plus the task
context block below, and it should be able to work without the rest of the
conversation.

| File | Role | Typical trigger (from `run_daily_cycle.py`) |
| --- | --- | --- |
| `orchestrator.md` | Main orchestrator, daily cycle | every run |
| `planner.md` | Portfolio planner | `start_next_project` |
| `engineer.md` | Senior AI engineer | `implement_milestone`, `resolve_review_blockers` |
| `test_engineer.md` | Test engineer | `implement_milestone`, `resolve_review_blockers` |
| `evaluator.md` | ML / evaluation engineer | milestones with eval work |
| `devops.md` | DevOps engineer | CI, Docker, release milestones |
| `documentation.md` | Documentation engineer | end of milestone, `finalize_project` |
| `reviewer.md` | Independent reviewer | `run_review` |

## Task context block (fill in per delegation)

```
Project: <id>            Repo: <url>          Local checkout: <path>
Milestone: <id - title>  Acceptance criteria: <from PLAN.md>
Relevant files: <paths>  Constraints: <budget, credentials, platform limits>
Definition of done: <tests/evals/docs that must exist, CI green>
```
