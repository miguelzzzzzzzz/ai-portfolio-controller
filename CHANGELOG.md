# Changelog

## [Unreleased]

### Added
- ADR-016: Cline DeepSeek v4.1 (`deepseek/deepseek-v4.1-flash`) is the default LLM for all projects, with small local models as the free fallback, recorded replies in CI, per-call cost logging to a shared box-only spend log, a runaway-loop guard, and no spend cap (owner authorization, 2026-10-09). `portfolio.yaml` gains an `llm` section; ADR-002, ADR-008, and ADR-011 point to it.
- Per-project `repo` slug and display `title` in `portfolio.yaml`, validated on load and used for repository URLs and creation (ADR-014).
- Project 03 milestones and portfolio ADRs 010-013.

### Fixed
- Project catalog now matches the ordered queue in the owner's brief (ADR-006). It replaces the catalog drafted at bootstrap. Project 02 milestones come from the planner's PLAN.md.

### Changed
- Narrowed projects 06, 08, and 10 to hardware-honest scopes (ADR-015): CPU LoRA on a ~0.5B model, an HNSW index built from scratch and benchmarked against hnswlib and FAISS, and CPU llama.cpp inference benchmarks.
- Recorded the daily schedule (a Grok Bot routine at 08:55 Asia/Manila) and cleared the scheduler blocker.
- Added portfolio ADRs 006-009: catalog alignment, cross-project reuse through pinned releases, local LLMs through OpenAI-compatible servers, and programmatic graders by default.

### Added
- Portfolio catalog (`portfolio.yaml`) with policies, quality commands, and the ordered project queue.
- Validated, atomically written `state.json`; daily summaries rendered to `LOG.md`.
- Daily-cycle decision logic, project registration/scaffolding, and an automated review gate.
- Scripts: `create_project.py`, `run_daily_cycle.py`, `review_project.py`, `update_state.py`.
- Role prompts for orchestrator, planner, engineer, test engineer, evaluator, DevOps, documentation, reviewer.
- Portfolio ADRs 001-005 and CI (ruff, mypy, pytest, state validation).
