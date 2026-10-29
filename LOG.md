# Daily log

Generated from `state.json` by `scripts/update_state.py render-log`. Do not edit by hand.

## 2026-10-29 - production-rag-engine - M7 done: v1.0.0 released (project complete)

Work completed:
- Chad's re-check of the final-review fixes at 977f091 (2026-10-28) passed with no CRITICAL or MAJOR findings; recorded in REVIEW.md and in state review (final review 1 MAJOR + 2 MINOR added as resolved, review passed)
- Release commit b8015f3: version 1.0.0 in pyproject.toml and rag_engine.__version__ plus tests/test_version.py (matches pyproject); CHANGELOG [Unreleased] -> [1.0.0] - 2026-10-29 with an empty [Unreleased] and compare links; README status v1.0.0 and a note that latency was measured on a VM shared with other bots and can vary with load; PLAN/TODO mark M7 done
- uv.lock is gitignored and untracked in CitationNeeded, so uv lock (no upgrade) changed only the local file and nothing was committed for it
- Annotated tag v1.0.0 on b8015f3 pushed after CI was green; CI triggers only on main pushes and PRs, so the tag ran no workflow. No GitHub release object created
- git diff 977f091 v1.0.0 --stat: 8 files changed, 45 insertions(+), 20 deletions(-) (CHANGELOG.md, PLAN.md, README.md, REVIEW.md, TODO.md, pyproject.toml, src/rag_engine/__init__.py, tests/test_version.py)
- Controller: M7 done, project finalized (status complete, completed 2026-10-29, active_project cleared); run_daily_cycle.py now decides start_next_project agentic-research-platform (RabbitHole), not applied today. No Cline or other model calls

Tests: CitationNeeded: 798 passed + 9 slow deselected, branch coverage 96.99%, 798 passed with fastembed blocked; ruff lint/format and strict mypy clean; CI green at b8015f3 (runs/40797474922: py3.11, py3.13, docker build + docker run smoke + compose smoke)

Evaluation: No new eval runs; no published numbers changed

Commits:
- b8015f3 chore(release): v1.0.0

Remaining blockers: none

Next recommended task: Bogart moves RabbitHole's CitationNeeded pin to @v1.0.0; then start RabbitHole (agentic-research-platform) local-first via run_daily_cycle.py --apply

## 2026-10-28 - production-rag-engine - M7 release prep: Chad's final review at 900575f resolved (1 MAJOR, 2 MINOR); v1.0.0 notes drafted, not tagged (M7 in progress pending Chad's re-check)

Work completed:
- scripts/eval_table.py --report <file>: one report's nDCG@10, MRR@10, Recall/Hit@{1,5,10} per mode, p50/p95 retrieval latency per mode (n/a when missing) and the report's hardware record verbatim; 8 tests incl. a run on the committed report
- README (MAJOR 1): SciFact quality table gains @1/@5 columns (both fastembed reports hold identical metrics); new per-mode latency table from scifact_test_fastembed_20261012T013527Z.json (99f28f6): p95 dense 40.1 ms, lexical 7.7 ms, hybrid 61.4 ms, hybrid+rerank 1751.6 ms; hardware as recorded (platform Linux-6.12.94+-x86_64-with-glibc2.41, processor empty, python 3.13.5, cpu_count 8; no CPU model, not a CI runner); 'per-stage latency' -> 'latency per mode'
- PROJECT_SPEC 8 p95 < 100 ms target (no rerank): met on the recorded machine (hybrid p95 61.4 ms); wording changed from 'on a CI-class CPU' to the machine the report records, since CI runs no models. Spec 7 (MINOR) now describes the code-graded M5 answer run as run and what one latency timing covers (end to end per mode; no per-stage or index build timings)
- README Known limitations (MINOR): heading stripping in extractive answers scans each chunk alone, so a chunk starting inside a fenced code block drops # comment lines and can quote a real heading after the closing fence (verified on the box); also one eval dataset, 30-claim answer eval, exact linear dense search, unauthenticated read-only service
- REVIEW.md: new section for Chad's final review at 900575f with resolutions and commit links; CHANGELOG: v1.0.0 release notes drafted under Unreleased, not tagged. No Cline or other model calls; code written and self-reviewed by Grok Bot

Tests: CitationNeeded: 797 passed + 9 slow deselected, branch coverage 96.99%, 797 passed with fastembed blocked; ruff lint/format and strict mypy clean; CI green at ff1619c (runs/40612949541) and 977f091 (runs/40613127011: py3.11, py3.13, docker build + docker run smoke + compose smoke)

Evaluation: No new eval runs; README latency and @1/@5 numbers are rendered from the committed 2026-10-12 fastembed report by scripts/eval_table.py --report

Commits:
- aa1427b feat(eval): render @1/@5 metrics, per-mode latency and hardware for one report
- ff1619c docs: add per-mode latency, @1/@5 metrics and known limitations
- 9b57c04 docs(review): record Chad's final review at 900575f and its resolutions
- 977f091 docs(changelog): draft v1.0.0 release notes (not tagged)

Remaining blockers: none

Next recommended task: Chad re-checks the fixes at 977f091 (latency table vs eval_table.py --report output, spec 8 rewording, known limitations, CHANGELOG draft) and signs off in REVIEW.md; then finalize CHANGELOG as [1.0.0], bump the README status, tag v1.0.0 and release; then RabbitHole starts local-first

## 2026-10-27 - production-rag-engine - M7 hardening part 3: extractive heading fix and base image digest pin (M7 code items done; in progress pending release notes and final review)

Work completed:
- Extractive answers no longer quote Markdown heading lines: for markdown/html chunks (HTML headings are normalized to ATX), ATX heading lines found by the loader's fence-aware scanner are sentence boundaries and dropped; reproduced first with a hashing index of evals/structured/docs (the answer started '# Comparison Sorting Algorithms ## Quicksort ...'), now 'Quicksort partitions around a pivot and recurses on both sides.'
- Sentence spans are computed directly (no str.find re-search); plain-text, PDF and format-less chunks unchanged; documented limitation: a chunk that starts inside a fenced code block can misread # lines; 7 new tests (exact offsets, HTML, heading-only chunk abstains, heading as boundary, fenced # comments kept, text format kept, repeated sentences)
- scripts/smoke_lib.sh fails if an /answer answer or quote contains a heading line (runs in both the docker run and compose smoke tests); dry-run against a local uvicorn first
- Dockerfile: both stages build FROM a PYTHON_IMAGE arg pinned to the python:3.13-slim multi-arch index digest sha256:d3449c04... (resolved 2026-10-27 via docker buildx imagetools inspect); the CI build log shows the pinned digest being pulled; README/CHANGELOG/TODO updated
- Controller: removed the uv.lock committed by mistake in 74234b2 and ignored it (CI uses pip). No Cline calls; code written and self-reviewed by Grok Bot

Tests: CitationNeeded: 789 passed + 9 slow deselected, branch coverage 96.99%, 789 passed with fastembed blocked; ruff lint/format and strict mypy clean; CI green at ae654b0 (runs/40430680328) and 900575f (runs/40430863608): py3.11, py3.13, docker build + docker run smoke + compose smoke; controller CI green at 0edf72c (runs/40431042361)

Evaluation: No new eval runs; no published numbers changed (the extractive generator is not in any committed report)

Commits:
- ae654b0 fix(answering): keep Markdown heading lines out of extractive quotes
- 900575f build(docker): pin the python:3.13-slim base image by digest
- 0edf72c chore: remove uv.lock committed by mistake in 74234b2 (controller)

Remaining blockers: none

Next recommended task: M7 code items are done: Chad's final review of CitationNeeded at 900575f (REVIEW.md), then v1.0.0 release notes and the v1.0.0 tag after the review passes

## 2026-10-26 - production-rag-engine - M7 hardening part 2: compose smoke test in CI (M7 in progress)

Work completed:
- scripts/compose_smoke.sh, run in the CI docker job on the image it just built: docker compose run --rm index builds a hashing-embedder index of evals/structured/docs first (no model downloads; /health and the HEALTHCHECK are 503 until an index is served), then docker compose up -d --wait api must turn healthy
- The compose test also checks the 127.0.0.1:8000 binding (compose port), the read-only root filesystem and the read-only /data/index mount (docker inspect), and ends with docker compose down -v with no containers left; verified in the CI log of runs/40251943970
- HTTP checks (health, search per mode, extractive answer, 422/400, X-Request-ID, JSON request log without query text) moved into scripts/smoke_lib.sh and shared by docker_smoke.sh and compose_smoke.sh; the shared checks were dry-run against a local uvicorn first; shellcheck clean; compose.yaml takes the image from RAG_IMAGE (default citation-needed:local)
- README now says compose is tested in CI (hashing index only; the fastembed default of the index service is not exercised in CI). Box still has no Docker daemon access; added a user-local docker compose v2.29.7 plugin for config checks only. No Cline calls; code written and self-reviewed by Grok Bot

Tests: CitationNeeded: 782 passed + 9 slow deselected, branch coverage 96.97%, 782 passed with fastembed blocked; ruff lint/format and strict mypy clean; CI green at 17c3561 (runs/40251943970: py3.11, py3.13, docker build + docker run smoke + compose smoke) and bbbaaa8 (runs/40252065878)

Evaluation: No new eval runs; no published numbers changed

Commits:
- 17c3561 ci(docker): smoke-test compose.yaml with a prebuilt index and up --wait
- bbbaaa8 docs(docker): describe the compose smoke test in CI and tick it off

Remaining blockers: none

Next recommended task: M7 part 2 (rest): pin the python:3.13-slim base image by digest; strip Markdown heading lines from extractive answer sentences; then v1.0.0 release notes and Chad's final REVIEW.md

## 2026-10-25 - production-rag-engine - M7 hardening part 1: locked model loads, opt-in warm-up, request logging, localhost compose (M7 in progress)

Work completed:
- FastEmbedEmbedder and CrossEncoderReranker serialize their lazy first model load (double-checked lock); a threaded test with a slow fake fastembed constructs exactly one model and fails when the lock is removed
- Opt-in RAG_WARMUP=off|embedder|all: RagService.warm_up embeds one probe query (and scores one reranker pair) in the app lifespan before the first request; failures are logged and the model loads on first use
- One JSON request log line on rag_engine.api.requests (request id, method, path, status, duration_ms, retrieve_ms, generate_ms; no query text; /health at DEBUG), X-Request-ID header, RAG_LOG_LEVEL; fixed: the service's INFO lines were dropped under uvicorn (no handler), now a stderr handler is added when nothing else logs
- compose.yaml publishes the API on 127.0.0.1:8000 only; README/Dockerfile state there is no authentication; image runs uvicorn --no-access-log; docker_smoke.sh now checks the warm-up line, X-Request-ID and the JSON request line (and that query text is not logged)
- Box has no Docker daemon access this run; the new smoke-test checks were dry-run against a local uvicorn with the same flags and then passed in CI. No Cline calls; code written and self-reviewed by Grok Bot

Tests: CitationNeeded: 782 passed + 9 slow deselected (slow: 9 passed locally with real fastembed), branch coverage 96.97%, 782 passed with fastembed blocked; ruff lint/format and strict mypy clean; CI green at 85485cd (runs/40149125281: py3.11, py3.13, docker build + smoke)

Evaluation: No new eval runs; no published numbers changed

Commits:
- 85485cd feat(api): lock first model loads, add opt-in warm-up and request logs

Remaining blockers: none

Next recommended task: M7 part 2: pin the python:3.13-slim base image by digest, CI job running docker compose up -d --wait on a tiny prebuilt index with scripts/docker_smoke.sh against the stack then docker compose down (only then call compose tested), strip heading-only lines from extractive answers; then v1.0.0 and Chad's final REVIEW.md

## 2026-10-20 - production-rag-engine - M6 FastAPI service, Dockerfile, docker build in CI (done)

Work completed:
- rag_engine.api: GET /health, POST /search, POST /answer over one prebuilt index served read-only from RAG_INDEX_DIR (ADR-0007); /health 200 only while an index is served, 503 with the reason otherwise; a corrupt index aborts startup
- Request schemas reject unknown fields and enforce the CLI's option rules; error contract 422 (schema) / 400 (unservable, e.g. openai generator without RAG_LLM_*) / 503 (no index, missing fastembed) / 502 (generator failed); ValueError during retrieval stays 500; validation errors do not echo input (NaN/Infinity made the default error body invalid JSON)
- RagService is framework-free with injectable reranker/generator factories; rerank uses only RAG_RERANK_MODEL; tests run real hashing-index retrieval with fake rerankers/generators (no model, no network); /search hits checked against rag-engine search --json per mode
- Shared compose_retriever and select_generator now back both the CLI and the service (removed duplicated wiring in cli.py)
- Dockerfile (multi-stage python:3.13-slim, uid 10001, HEALTHCHECK), .dockerignore, compose.yaml (index tool service + read-only api), CI docker job: image build, compose config check, scripts/docker_smoke.sh (hashing index built in the container, served read-only, every endpoint, 503 + failing HEALTHCHECK without an index)
- Local box checks: docker smoke passed; a fastembed index built and served in the container with a read-only root fs (model cache volume) answered dense and hybrid+rerank searches; uvicorn exits (code 3) on a corrupt index. compose.yaml not run end to end (no compose plugin on the box; CI validates config only)
- POST /ingest dropped from M6 (ADR-0007): indexing stays a batch job. No Cline calls (Pass lapsed); code written and self-reviewed by Grok Bot

Tests: CitationNeeded: 759 passed + 9 slow deselected, branch coverage 96.74%, 759 passed with fastembed blocked, also passed on py3.11 locally; ruff lint/format and strict mypy clean; CI green at 9c76f7e (runs/39352567974: py3.11, py3.13, docker build + smoke)

Evaluation: No new eval runs; no published numbers changed

Commits:
- a5ff323 refactor(cli): share retriever composition and generator selection
- 5ed7b5b feat(api): add FastAPI service with /health, /search and /answer
- c434742 build(docker): add service image, compose file and CI smoke test
- 9c76f7e docs(api): document the HTTP service and Docker image; mark M6 done

Remaining blockers: none

Next recommended task: Chad reviews M6 (b3160e0..9c76f7e); then M7 hardening (startup warm-up, request logging, extractive heading strip), v1.0.0 and Chad's final REVIEW.md

## 2026-10-18 - production-rag-engine - M5 answer-eval review MINORs (pre-M6)

Work completed:
- Reviewed and finished the uncommitted Oct 14 Cline drafts for Chad's four M5 MINORs: MIN_QUOTE_CHARS=20 (trimmed) in the span grader with boundary tests; rag_engine.eval.intervals.wilson_interval + scripts/answer_eval_table.py (rates recomputed from per-item grades, checked against report metrics); README calls correct abstention 8/10 a lower bound and says recall counts only the 17 eligible claims; every rate shows raw count + 95% Wilson CI
- Applied the Oct 14 Cline-written tests/test_intervals.py (41 tests); own glue: ruff format, README/grading-string wording, CHANGELOG, TODO
- Offline replay of the committed answer cache under the 20-char rule (30 cache hits, 0 API calls): every per-item grade and metric identical to the 2026-10-13 report; shortest quote 75 chars
- M6 drafts from Oct 14 (api schemas/service, Dockerfile, compose, CI job) trial-applied in a scratch worktree: incomplete (no app.py routes, no fastapi dependency, no tests, mypy errors); kept out of git

Tests: CitationNeeded at b3160e0 (local): 699 passed + 9 slow deselected, branch coverage 96.36%, 699 passed with fastembed blocked; ruff lint/format and strict mypy clean; CI not run (not pushed)

Evaluation: Answer eval replay 2026-10-18 (unchanged vs 2026-10-13): parsed 30/30 [0.89,1.00]; span validity 29/30 [0.83,0.99]; citation recall 12/17 [0.47,0.87]; precision 18/29 [0.44,0.77]; false abstention 4/17 [0.10,0.47]; correct abstention 8/10 [0.49,0.94] (95% Wilson)

Commits:
- b3160e0 fix(eval): enforce 20-char quote minimum and add Wilson intervals to answer eval (local, unpushed)

Remaining blockers: Cline Pass inactive (HTTP 402 subscription has not been paid / 403 ENTITLEMENT_ERROR) since the 2026-10-17 reset; no Cline review of b3160e0; M6 not started

Next recommended task: Restore the Cline Pass (owner), Cline-review and push b3160e0, then M6 FastAPI service (POST /search, /answer, GET /health), Dockerfile, docker build in CI; Chad re-check of the MINOR fixes

## 2026-10-13 - production-rag-engine - Eval honesty pack close-out + M5 answer eval (pre-M6)

Work completed:
- Committed sidecar-bearing SciFact fastembed re-run at 99f28f6 (git_dirty false, aggregates identical to 2026-10-10 report, sidecar means = aggregates) plus paired bootstrap CI summary (B=10000, seed 0); README keeps hybrid vs dense 'about the same' (nDCG@10 diff -0.0015, 95% CI [-0.0273, +0.0239]); dense and hybrid beat lexical (CIs exclude 0); rerank vs hybrid spans 0
- M5 answer eval slice: rag_engine.eval.answers (seeded subset, raw-reply parsing, code-only grades), answer_cache (request-keyed JSONL cache, record/replay generator), answer_runner (gold-removal no_relevant items, exactly k contexts), scripts/answer_eval.py; OpenAI client unwraps Cline {data:...} envelope
- Recorded 30-claim SciFact answer eval with cline-pass/deepseek-v4.1-flash at c55a2bb; cache committed; offline replay matched every record
- Cline helper: guard now per-day; max_tokens logged; cline_review.py switched to the Pass model id; review HTTP 500s traced to reasoning exhausting max_tokens (reviews now use 24-32k)

Tests: CitationNeeded: 654 passed + 9 slow deselected, branch coverage 96%, 654 passed with fastembed blocked; CI green at 3c9435a, c55a2bb, 67eecad

Evaluation: SciFact bootstrap CIs (seed 0, B=10000): hybrid-dense nDCG@10 -0.0015 [-0.0273, +0.0239]; hybrid+rerank-hybrid -0.0233 [-0.0531, +0.0057]; dense-lexical +0.0458 [+0.0085, +0.0829]; hybrid-lexical +0.0442 [+0.0201, +0.0686]. Answer eval (30 claims, cline-pass/deepseek-v4.1-flash, 2026-10-13, code-graded): span validity 29/30, citation recall 0.71 (17 eligible), precision 18/29, false abstention 4/17, correct abstention 8/10

Commits:
- 3c9435a docs(eval): commit SciFact sidecar re-run and paired bootstrap CIs
- c55a2bb feat(eval): add code-graded M5 answer eval with replayable reply cache
- 67eecad docs(eval): record first M5 answer eval on SciFact with cached replies

Remaining blockers: none

Next recommended task: M6 FastAPI service (POST /search, /answer, GET /health), Dockerfile, docker build in CI; ask Chad to review answer-eval design and numbers

## 2026-10-12 - production-rag-engine - Pre-M6 eval honesty pack (README table + per-query sidecar + bootstrap CI)

Work completed:
- README SciFact quality table from committed report scifact_test_fastembed_20261010T184148Z.json (Chad-matched aggregates); hybrid vs dense described as about the same on nDCG@10
- Eval runner now returns per-query scores; write_report emits sibling *.per_query.json (schema 1)
- rag_engine.eval.bootstrap.paired_bootstrap_ci + scripts/bootstrap_ci.py with unit tests (no network)
- Did not start M6; did not re-run SciFact (committed report predates sidecar — bootstrap CI not claimed in README yet)

Tests: CitationNeeded: 571 passed + 9 slow deselected, branch coverage 96%, 571 passed with fastembed blocked; CI green at 99f28f6

Evaluation: README table cites existing fastembed report only. Sidecar-bearing SciFact re-run deferred; paired bootstrap CI ready for next clean eval.

Commits:
- ea2a3bc feat(eval): emit per-query sidecar and paired bootstrap CI
- 99f28f6 docs(eval): add SciFact fastembed quality table to README

Remaining blockers: Cline pre-push review returned HTTP 500 empty (2 calls); gates passed locally and CI green

Next recommended task: M6 FastAPI service, Dockerfile, image build in CI

## 2026-10-11 - production-rag-engine - M5

Work completed:
- Committed SciFact fastembed report (pending Chad README review)
- Implemented M5 answering: extractive default + OpenAI-compatible client + rag-engine answer CLI

Tests: 553 passed (9 slow deselected), coverage 96%, ruff+mypy clean; CI green

Evaluation: SciFact fastembed report committed; README quality table still blocked pending Chad

Commits:
- 31f9af2 docs(eval): add SciFact fastembed benchmark report
- 3ced24c feat(answer): add M5 extractive and OpenAI-compatible generators

Remaining blockers: Cline M5 pre-push review returned HTTP 500 empty (2 calls); gates passed locally; ask Chad to review SciFact numbers before README claims

Next recommended task: M6 FastAPI service + Dockerfile

## 2026-10-10 - production-rag-engine - Chad's M4 review of 96b3c33 resolved (1 MAJOR, 4 MINOR) - extra on-request work, Cline Pass as primary coder and reviewer

Work completed:
- MAJOR (9f236ba): every eval mode starts at the same chunk depth (EvalConfig.depth, default 50, >= top_k) and doubles until top_k unique documents or exhaustion/max_depth; per-mode initial/max/used depth and queries_short_of_k recorded; evaluate --depth/--max-depth; test with one document owning all top chunks
- MINORs (all in 9f236ba): untimed warm-up per mode with a fixed non-evaluated query; git_dirty recorded beside git_sha; queries with no relevant grade skipped and counted (n_queries_skipped_no_relevant, n_queries_unlabelled); structured set flagged smoke_only (chosen over section-level scoring); report schema_version 2
- Coverage had fallen to 95.55% at 96b3c33; e718f74 adds error-path tests (structured qrels validation, reranker/import mapping, git_dirty, evaluate scifact branch) -> 96.39%
- 34dd3e5: REVIEW.md M4 section, CHANGELOG/TODO/README/evals README; hashing smoke reports regenerated at e718f74 (schema 2, git_dirty false), replacing schema-1 reports
- A real fastembed SciFact run was started, then stopped per owner instruction before finishing; no quality numbers produced or committed
- Controller: normalized the hand-written M4 daily_log entry to the standard schema (render-log failed on it)
- Cline usage: 10 calls / 17 attempts (7 ok, 3 failed with HTTP 500 empty response content on larger test prompts; split prompts succeeded); reference cost USD 0.0570 (Cline Pass reference price, not money spent); Pass usage start -> end: five-hour 0% -> 1%, weekly 0% -> 0%, monthly 74% -> 74%

Tests: CitationNeeded: 484 passed + 9 slow deselected, branch coverage 96.39%, 484 passed with fastembed blocked, 9 slow passed locally; CI green at e718f74 (runs/38014468789, covers 9f236ba pushed with it) and 34dd3e5 (runs/38016069545)

Evaluation: Hashing smoke reports only (harness checks, not quality claims). No fastembed SciFact numbers.

Commits:
- 9f236ba fix(eval): compare modes at equal retrieval depth
- e718f74 test(eval): cover loader, runner and CLI error paths
- 34dd3e5 docs(eval): record Chad's M4 review and regenerate smoke reports

Remaining blockers: none

Next recommended task: Real fastembed SciFact run (dense, lexical, hybrid, hybrid+rerank) for review before any README claim; then M5 answer generation

## 2026-10-10 - production-rag-engine - M4 evaluation harness (done)

Work completed:
- M4 evaluation harness: metrics, SciFact loader, structured-doc set, runner, evaluate CLI, hashing smoke reports committed; CI green at 96b3c33.
- rag_engine.eval: metrics, SciFact BEIR loader with MD5/zip-slip checks, structured-doc set, runner; rag-engine evaluate; scripts/eval_table.py
- Hashing smoke reports under evals/results/ are harness checks, not quality claims; SciFact data stays gitignored
- Cline (cline-pass/deepseek-v4.1-flash) primary coder/reviewer; API fixes applied after review findings

Tests: 462 passed + 9 slow deselected; coverage ~95% (below the 96% bar; restored in e718f74). CI green at 96b3c33: https://github.com/miguelzzzzzzzz/CitationNeeded/actions/runs/38012671154

Evaluation: Hashing smoke reports only; no quality claims.

Commits:
- 96b3c33 feat(eval): add M4 evaluation harness for SciFact and structured docs

Remaining blockers: none

Next recommended task: M5 answer generation

## 2026-10-09 - production-rag-engine - v0.1.0 released (M1-M3 interface release); interface review passed

Work completed:
- Chad re-checked CitationNeeded at cdd892e and signed off for the v0.1.0 interface: both MAJORs and all MINORs closed; citation hash verification, stable corpus-scoped ids and per-stage rerank ranks confirmed. Final review gate remains after M7
- Release commit bf0c83b: CHANGELOG Unreleased moved to [0.1.0] - 2026-10-09 (pre-1.0 interface release, breaking changes listed, no eval numbers), sign-off appended to REVIEW.md, README recommends always passing --corpus-id (Chad's non-blocking advice) and uses it in examples, PLAN M7 reworded; pyproject and __version__ were already 0.1.0
- Annotated tag v0.1.0 on bf0c83b pushed; GitHub release v0.1.0 created with the CHANGELOG section as notes: https://github.com/miguelzzzzzzzz/CitationNeeded/releases/tag/v0.1.0
- No Cline calls this step (release bookkeeping only)

Tests: CitationNeeded: 380 passed + 9 slow deselected, branch coverage 96.49%, 380 passed with fastembed blocked, 9 slow passed locally; CI green at bf0c83b (runs/37915651843); ai-portfolio-controller: 37 passed

Evaluation: Not run. Retrieval quality is measured in M4 on SciFact; no quality numbers claimed.

Commits:
- bf0c83b chore(release): v0.1.0

Remaining blockers: none

Next recommended task: M4 evaluation harness on SciFact (download + checksum, Recall@K/MRR/nDCG, JSON reports)

## 2026-10-09 - production-rag-engine - Chad's review of 84bce05 resolved (0 CRITICAL, 2 MAJOR, MINOR + OPTIONAL items) - extra on-request cycle, Cline Pass as primary coder and reviewer

Work completed:
- MAJOR 2 (a18aca9): doc_id = sha256('<corpus_id>:<relative posix path>')[:16]; corpus_id validated (no ':'), configurable via --corpus-id / RAG_CORPUS_ID / IngestionConfig, default = slugified root dir name; sources must be normalized relative paths; tests pin make_doc_id('handbook','guide/intro.md') = 120aa960849299ee, stability across roots, no cross-corpus collision; Chunk validates end_char > start_char
- MAJOR 1 (1cf8b71): normalized documents persisted (ingest writes <stem>.documents.jsonl, index dirs hold documents.jsonl); verify_chunks checks doc exists, source/content_hash match, chunk.text == doc.text[start:end] on ingest, index build and load; index format 2, format 1 rejected with rebuild message; provenance adds content_hash and page_end; README offset wording fixed; ADR-0006
- MINOR/OPTIONAL: RetrievedChunk.ranks keyed by stage name, rerank no longer overwrites inner stage (raises on key clash), NaN/inf fusion weights rejected (b36d286); search --json versioned with schema_version 1 (8bf4367, breaking); end-to-end offset-invariant tests across md/html/txt, CRLF, front matter, ligatures, control chars, all chunkers, save/load, RRF, weighted, rerank, nested rerank (eeca981); REVIEW.md, CHANGELOG, TODO, README (cdd892e). Also closes the nested-rerank key-collision finding left open in the previous cycle
- Cline per-fix reviews found and fixed: front-matter shadowing of provenance metadata, unnormalized source paths, destructive failed save_index on duplicate documents, ingest writing chunks before verifying, lexical half unverified on save, non-strict JSON (allow_nan=False)
- New gate applied before every push: fast tests with fastembed imports blocked (338, 368, 380 passed at the three code pushes; same counts as the unblocked run); CI waited green between pushes
- Cline usage: 26 calls / 44 attempts (18 ok, 2 truncated, 6 failed after retries with HTTP 500 empty response content on larger test/review prompts; split prompts succeeded); reference cost USD 0.1406 (Cline Pass reference price, not money spent); Pass usage start -> end: five-hour 2% -> 4%, weekly 1% -> 2%, monthly 74% -> 74%

Tests: CitationNeeded: 380 passed + 9 slow deselected, branch coverage 96.49% (bar 96%), same 380 pass with fastembed blocked, 9 slow real-model tests pass locally; CI green at a18aca9, 1cf8b71, eeca981, cdd892e (py3.11, py3.13)

Evaluation: Not run. Retrieval quality is measured in M4 on SciFact; no quality numbers claimed.

Commits:
- a18aca9 fix(ingestion): scope document ids by corpus id
- 1cf8b71 fix(index): persist normalized documents and verify citations
- b36d286 fix(retrieval): record per-stage ranks apart from scores
- 8bf4367 feat(cli): version the search --json payload
- eeca981 test: check citation offsets end to end across loaders and stages
- cdd892e docs: record Chad's review at 84bce05 and its resolutions

Remaining blockers: none

Next recommended task: M4 evaluation harness on SciFact (download + checksum, Recall@K/MRR/nDCG, JSON reports); v0.1.0 not tagged (held per owner)

## 2026-10-09 - production-rag-engine - M2 review fixes and M3 hybrid fusion + reranking (done) - extra on-request cycle, Cline Pass as primary coder and reviewer

Work completed:
- Extra on-request cycle (Oct 9). Cline (cline-pass/deepseek-v4.1-flash) reviewed the M2 diff: 13 findings; 11 accepted and fixed by Cline (index manifest validation, chunk-id alignment, embedder spec check on save, no-fastembed lexical search, CLI ImportError handling, ignored-option warning), 2 rejected (BM25 parameters already persisted; retrieve() cannot raise the cited ValueError)
- M3 written by Cline: RRF and weighted min-max score fusion with hand-computed tests, HybridRetriever with filter pass-through, cross-encoder reranker (Xenova/ms-marco-MiniLM-L-6-v2 via fastembed, slow real-model tests), search --mode hybrid/--fusion/--weight/--rrf-k/--candidates/--rerank
- Cline reviewed the M3 diff (fusion and rerank reviews truncated by hidden reasoning; cli review complete); 8 findings accepted and fixed by Cline; 3 rejected (single-hit lists normalizing to 1.0 is documented design; reranking already returns k hits; components are typed floats); 1 low rerank finding (components key collision for nested reranking) left open
- CI was red on 05090b0 and 167a6e5: a test exposed an unguarded ImportError when fastembed is absent (local env has it); fixed in 84bce05 and reproduced locally by blocking the fastembed import
- Amended ADR-016: Pass model id, HTTP 402 meaning, Pass limits checked per cycle, Pass cost is a reference price; portfolio.yaml llm section and test updated
- Cline usage: 25 calls / 35 attempts (20 ok, 2 truncated, 3 failed after 3 attempts with HTTP 500 empty response content); reference cost USD 0.1915 (Cline Pass, not money spent); Pass usage before -> after: five-hour 0% -> 2%, weekly 0% -> 1%, monthly 73% -> 74%

Tests: CitationNeeded: 287 passed + 9 slow deselected, branch coverage 96%, CI green at 84bce05 (py3.11, py3.13); 9 slow real-model tests passed locally; ai-portfolio-controller: 37 passed

Evaluation: Not run. Retrieval quality of dense vs lexical vs hybrid vs reranked is measured in M4 on SciFact; no quality numbers claimed.

Commits:
- 75ed832 fix(retrieval): validate index manifests and chunk alignment on save and load
- 05090b0 fix(cli): report missing fastembed cleanly and warn on ignored chunking options
- 5512fb0 feat(retrieval): add RRF and weighted score fusion with a hybrid retriever
- b88991f feat(retrieval): add cross-encoder reranking stage
- 0237813 feat(cli): add hybrid fusion and reranking options to search
- c486564 fix(retrieval): validate fusion inputs and hybrid configuration up front
- 167a6e5 fix(cli): reject inert or degenerate fusion and candidate options
- 84bce05 fix(cli): guard embedder setup when fastembed is not installed
- cd02101 docs(adr): bill Cline calls to the Pass and label Pass costs as reference prices

Remaining blockers: none

Next recommended task: Chad's interface review (due after M3); then M4 evaluation harness on SciFact (download + checksum, Recall@K/MRR/nDCG, JSON reports)

## 2026-10-09 - production-rag-engine - M2 retrieval primitives (done) - extra on-request cycle, Cline as primary coder

Work completed:
- Extra cycle on request (Oct 9) to validate Cline DeepSeek as primary coder and reviewer; box-only helper /workspace/portfolio/cline.py with retries, runaway guard, per-call cost log
- Cline wrote retriever.py (Retriever protocol, Dense/Lexical retrievers, RetrievedChunk with provenance), index_store.py (embedder specs, save/load index directory), cli.py index/search commands, and their unit tests (test_retriever.py, test_index_store.py)
- Grok Bot wrote package exports, CLI end-to-end tests (Cline credits ran out), two fixes (zero-vector dense queries; CLI chunk overrides dropped RAG_EMBEDDING_*), and docs
- Cline usage: 9 calls (5 ok, 2 truncated at max_tokens by hidden reasoning, 1 connection dropped after ~270 s, 1 HTTP 402 insufficient credits); reported cost USD 0.1338; Cline review of the full diff not done

Tests: CitationNeeded: 193 passed + 6 slow deselected, branch coverage 95%, CI green (py3.11, py3.13); 6 slow real-model tests passed locally; ai-portfolio-controller: 37 passed

Evaluation: Not run. Retrieval benchmark is planned for M4 on SciFact.

Commits:
- d3b4138 feat(retrieval): add dense and lexical retrievers with index persistence
- 3e42e6b fix(retrieval): return no hits for zero-vector dense queries
- 838f3a4 feat(cli): add index and search commands

Remaining blockers: Cline credits exhausted (HTTP 402, balance about USD 0.007); Cline coding and review paused until the owner tops up

Next recommended task: Top up Cline credits; have Cline review the M2 diff (a5a37ec..838f3a4); then M3 hybrid fusion (RRF/weighted) and cross-encoder reranking

## 2026-10-09 - production-rag-engine - M2 retrieval primitives (in progress): fastembed adapter and BM25 index

Work completed:
- Added FastEmbedEmbedder for BAAI/bge-small-en-v1.5 (optional extra, bounded batches, zero rows for empty texts, L2 normalization, output validation) with real-model tests marked slow
- Added BM25Index (inverted index, document-level upsert/delete, filters before top-k, save/load) with scores checked against hand-computed values
- Added ADR-016: Cline DeepSeek v4.1 is the default LLM, local models <=1.7B the fallback, recorded replies in CI, per-call cost logged to a shared box-only spend log, runaway guard, no spend cap (owner, 2026-10-09)
- Cline usage today: 3 calls (1 ok, 1 HTTP 500, 1 interrupted); reported cost USD 0.0000444; second-opinion review of the embedder not obtained

Tests: CitationNeeded: 139 passed + 3 slow deselected, branch coverage 95%, CI green (py3.11, py3.13); 3 slow real-model tests passed locally; ai-portfolio-controller: 37 passed

Evaluation: Not run. Retrieval benchmark is planned for M4 on SciFact.

Commits:
- 107db3b feat(retrieval): add fastembed adapter for bge-small-en-v1.5 with batching
- a5a37ec feat(retrieval): add BM25 index with hand-computed score tests
- 2dde1ba docs(adr): make Cline DeepSeek v4.1 the default LLM (ADR-016)

Remaining blockers: none

Next recommended task: M2: Retriever returning scored chunks with provenance; rag-engine index/search CLI

## 2026-10-09 - production-rag-engine - M1 ingestion and chunking (done); M2 retrieval primitives (started)

Work completed:
- Bootstrapped ai-portfolio-controller (catalog, validated state, cycle decisions, review gate, role prompts, ADRs)
- Created production-rag-engine with PROJECT_SPEC, PLAN, ADRs 0001-0005, CI on Python 3.11 and 3.13
- Implemented text/Markdown/HTML/PDF loaders with metadata extraction and per-file error isolation
- Implemented fixed, recursive, and structure-aware chunkers with exact character offsets
- Added rag-engine ingest CLI and chunking comparison script
- Added Embedder protocol, HashingEmbedder, and exact InMemoryVectorStore with filters and persistence

Tests: production-rag-engine: 114 passed in CI (py3.11 and py3.13), branch coverage 96%; ai-portfolio-controller: 29 passed

Evaluation: Not run. No retrieval benchmark yet (planned for M4 on SciFact).

Commits:
- 60f05cf chore: scaffold package, validated settings, and CI pipeline
- da3a247 docs: add project spec, milestone plan, and architecture decision records
- 7932df0 feat(ingestion): add document model and format-aware loaders
- c268f04 feat(chunking): add fixed, recursive, and structure-aware chunkers
- f415a97 feat(cli): add ingest command and chunking strategy comparison
- fb38d06 feat(retrieval): add embedder protocol and exact in-memory vector index

Remaining blockers: none

Next recommended task: M2: fastembed adapter (bge-small-en-v1.5, slow tests), BM25 index with hand-computed score tests, Retriever, index/search CLI
