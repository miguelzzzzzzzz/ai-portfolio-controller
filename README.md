# ai-portfolio-controller

[![CI](https://github.com/miguelzzzzzzzz/ai-portfolio-controller/actions/workflows/ci.yml/badge.svg)](https://github.com/miguelzzzzzzzz/ai-portfolio-controller/actions/workflows/ci.yml)

Control plane for an AI engineering portfolio built by an orchestrator agent
and specialized sub-agents. It holds the project catalog, the
machine-readable state of every project, decision records, reusable role
prompts, and the scripts that decide what the next daily cycle should do and
whether a project passes its completion gate.

The goal is a small number of technically strong repositories, not commit
volume: every cycle must produce a real engineering improvement, and every
published metric must come from an executed, committed evaluation.

## Layout

| Path | Purpose |
| --- | --- |
| `portfolio.yaml` | Owner, policies (budget, commit style, scope), quality commands, ordered project catalog |
| `state.json` | Facts: active project, milestone status, last CI result, review findings, daily log |
| `LOG.md` | Daily summaries rendered from `state.json` |
| `PROJECT_QUEUE.md` | Human-readable queue and overlap check between projects |
| `DECISIONS.md` | Portfolio-level ADRs |
| `prompts/` | Role instructions: orchestrator, planner, engineer, test engineer, evaluator, DevOps, documentation, reviewer |
| `templates/` | Document skeletons copied into new projects |
| `controller/` | Library: state validation and atomic writes, cycle decisions, review gate |
| `scripts/` | CLIs over the library (below) |

## Daily cycle

```
python scripts/run_daily_cycle.py            # decide: prints action, project, milestone, prompts
#   start_next_project      -> planner writes PROJECT_SPEC/PLAN; create_project.py registers it
#   implement_milestone     -> engineer/test/eval/devops/docs roles do one coherent unit
#   run_review              -> review_project.py + reviewer prompt record findings
#   resolve_review_blockers -> fix CRITICAL/MAJOR findings
#   finalize_project        -> run_daily_cycle.py --apply marks it complete
python scripts/update_state.py milestone <project> <M#> done
python scripts/update_state.py ci <project> --conclusion success --url <run-url>
python scripts/update_state.py log --project ... --milestone ... --work ... --tests ... \
    --evaluation ... --commit ... --next ...
```

`controller/cycle.py` implements the decision table from the brief
(no active project -> start next; open milestones -> implement the in-progress
or first open one; all done -> review; CRITICAL/MAJOR findings -> fix;
passing review -> finalize; then the next project). It is a pure function
of `state.json` and `portfolio.yaml` and is unit-tested for each branch.

The cycle is triggered once a day by the orchestrator agent's scheduler,
which runs on the same box as the checkouts (see `DECISIONS.md` ADR-001).
The scripts never perform engineering work themselves; they keep state
honest and tell the orchestrator which role prompts to use.

## Review gate

`python scripts/review_project.py <checkout> --run-checks --record <project>`
checks required files (README, spec, plan, changelog, license, `.env.example`,
Dockerfile, ...), tracked `.env` files and token-like strings, tests and CI
presence, committed evaluation reports, README sections, conventional commit
subjects, and runs the quality commands from `portfolio.yaml`. Findings use
CRITICAL / MAJOR / MINOR; a project passes only with no CRITICAL or MAJOR
findings. The judgement part of the review follows `prompts/reviewer.md`.

## Development

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check . && mypy && pytest
```
