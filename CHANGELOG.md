# Changelog

## [Unreleased]

### Added
- Portfolio catalog (`portfolio.yaml`) with policies, quality commands, and ten planned projects.
- Validated, atomically written `state.json`; daily summaries rendered to `LOG.md`.
- Daily-cycle decision logic, project registration/scaffolding, and an automated review gate.
- Scripts: `create_project.py`, `run_daily_cycle.py`, `review_project.py`, `update_state.py`.
- Role prompts for orchestrator, planner, engineer, test engineer, evaluator, DevOps, documentation, reviewer.
- Portfolio ADRs 001-005 and CI (ruff, mypy, pytest, state validation).
