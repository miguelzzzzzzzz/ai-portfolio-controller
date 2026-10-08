# Portfolio decisions

Portfolio-level architecture decision records. Project-specific ADRs live in
each project's `docs/adr/`.

## ADR-001: Run the portfolio from a persistent Linux box with a scoped token

Status: Accepted (2026-10-09)

Reason: The portfolio account's credential (a fine-grained personal access token
with Administration, Contents, Workflows, Actions, Pull requests, and Issues
permissions) is available only on the box, so all work happens in local
checkouts under `/workspace/portfolio/`. Pushes use HTTPS with the token
supplied at runtime by a credential helper; it is never written to
`.git/config`, files, or logs. SSH to github.com times out from the box, so
SSH is not used.

Alternatives considered: cloud agents per run (no access to the credential);
SSH deploy keys (blocked by network, and per-repo keys cannot create repos).

Consequences: every project's quality gate runs on the box *and* in GitHub
Actions. The scripts only ever touch repositories listed in `portfolio.yaml`;
the account's unrelated pre-existing repositories are out of scope.

## ADR-002: Zero paid API spend by default; local CPU models; LLMs behind provider interfaces

Status: Accepted (2026-10-09)

Reason: No paid LLM key is available and the user has not authorized spending
(`policies.paid_api_budget_usd: 0`). Projects use small open models on CPU
(ONNX via fastembed or similar) and put any LLM behind an OpenAI-compatible
provider interface with an offline fallback, so systems, tests, and evals run
for free and reproducibly.

Alternatives considered: hosted LLM/embedding APIs (cost, non-reproducible
offline); PyTorch-based local models (multi-GB dependency, slow CI).

Consequences: some evaluations (LLM-judged faithfulness, generation quality)
are scaffolded and reported as "not run" until a provider is approved. When an
API key is approved, the budget is set here and in `portfolio.yaml`.

## ADR-003: No local Docker; container builds are validated in GitHub Actions

Status: Accepted (2026-10-09)

Reason: Docker is not installed on the box. Dockerfiles are written alongside
the service code and built (and smoke-tested) in CI. Project docs state this
explicitly rather than implying local validation.

## ADR-004: Controller state is a validated JSON file plus scripts, not a database

Status: Accepted (2026-10-09)

Reason: State is small (around ten projects, a log entry per run) and must be
human-reviewable in git history. `state.json` is validated on every load and
save and written atomically; `portfolio.yaml` holds intent (catalog and
policies), `state.json` holds facts (what happened). Decision logic
(`controller/cycle.py`) is a pure function of the two, so it is unit-tested.

Alternatives considered: SQLite (opaque in diffs); GitHub Issues/Projects as
state (network-dependent, harder to test).

## ADR-005: First project is production-rag-engine with an in-process vector index

Status: Accepted (2026-10-09)

Reason: RAG covers the most requested skills (embeddings, vector search,
hybrid retrieval, reranking, evaluation, APIs). For its vector store, an
in-process exact NumPy index behind a `VectorStore` protocol gives zero
infrastructure and exactly reproducible evals at the target scale (up to about
100k chunks); Qdrant or pgvector adapters can be added behind the same
protocol. Retrieval is evaluated on SciFact (BEIR; claims CC BY 4.0, abstracts
ODC-By 1.0). See the project's ADR-0001 through ADR-0005.

## ADR-006: Align project catalog with the owner's brief

Status: Accepted (2026-10-09). Supersedes the catalog written at bootstrap.

Reason: At bootstrap the controller wrote its own ten-project catalog
(`llm-eval-harness`, `agent-tool-runtime`, `document-intelligence`,
`embedding-finetuning-lab`, `llm-gateway`, `multimodal-search`,
`ml-training-pipeline`, `llm-distillation`, `structured-output-benchmark`).
That catalog did not match the ordered queue in the owner's brief (section 5),
which is authoritative. Because `create_project.py` only accepts ids that are
in `portfolio.yaml`, and `next_queued_project` follows its order, the wrong
catalog would have started the wrong projects.

Decision: Replace the catalog with the brief's queue, in this order:

1. production-rag-engine
2. agentic-research-platform
3. llm-evaluation-lab
4. multimodal-document-intelligence
5. mlops-fraud-detection
6. llm-finetuning-lab
7. ai-observability-platform
8. semantic-search-engine
9. voice-ai-agent
10. ai-inference-benchmark

Project 01 keeps its milestones and status. Project 02's milestones come from
the planner's PLAN.md (staged in `/workspace/p02-agentic-research-platform/`).
The scope of the old `agent-tool-runtime` entry (typed tool registry,
JSON-schema tool calls, malformed-call repair, retries and budgets, traces) is
absorbed into project 02. Projects 03-10 carry the objectives and
capabilities from brief section 5. The planner turns them into milestones
before each project starts.

Scope boundaries:

- Project 02 owns agent-trajectory graders. `llm-evaluation-lab` owns the
  general prompt/LLM-output regression framework, including LLM-judge
  agreement.
- Project 02 owns JSONL run traces. `ai-observability-platform` owns
  OpenTelemetry, cost accounting, and dashboards.
- Project 02 handles schema validation and repair only for tool calls.
  Measuring structured-output reliability across techniques belongs to
  `llm-evaluation-lab`.

Consequences: `portfolio.yaml`, `PROJECT_QUEUE.md` (including its overlap
check), and the controller tests now use the brief's ids. Project 02's
repository is not created, and its docs are not committed, until project 01
is complete.

## ADR-007: Cross-project reuse through pinned releases behind consumer-side interfaces

Status: Accepted (2026-10-09)

Reason: Later projects can build on earlier ones. `agentic-research-platform`
needs a corpus search tool, and `production-rag-engine` already provides a
tested retriever whose chunks carry exact character offsets. Reusing that
retriever avoids re-implementing retrieval and shows realistic cross-repo
composition. The risk is coupling schedules and APIs across repos.

Alternatives considered: copy code between repos (drift, duplicated
maintenance); a shared "common" library repo (premature, and not a portfolio
project itself); publish to PyPI (unnecessary for portfolio use and adds
release overhead); re-implement minimal retrieval in each project
(duplicated skill, weaker component).

Consequences: A consuming project depends on a tagged release of a completed
portfolio project through a git URL pinned to both tag and commit SHA (hatch
`allow-direct-references = true`). It defines its own small protocol (for
example `SearchBackend`) and one adapter module, so upstream API changes stay
inside the adapter. Default unit tests use an in-repo fake behind the same
protocol, so they don't depend on the upstream package's heavier code paths.
Reuse is chosen only when the reused component is not the skill the
consuming project demonstrates.

## ADR-008: Local LLM inference through OpenAI-compatible servers; CI never calls a model

Status: Accepted (2026-10-09)

Reason: ADR-002 covers local ONNX embedding and reranking models but not
generative LLM serving, and several queued projects need an LLM. The box is
CPU-only (8 cores, 15 GB RAM, of which about 3 GB was free on 2026-10-09).
At that time neither Ollama nor llama.cpp was installed, and no paid key
existed.

Alternatives considered: in-process inference through `transformers`/PyTorch
(multi-GB dependency, slow on CPU); in-process `llama-cpp-python` bindings
(ties the app to one runtime); hosted APIs (not approved, ADR-002); running a
model inside GitHub Actions (slow, flaky, and results would depend on runner
hardware).

Consequences: Projects talk to LLMs only through an OpenAI-compatible HTTP
interface. Locally that means Ollama or a llama.cpp server (`llama-server`
or `llama-cpp-python[server]`) running small, openly licensed instruct
models. The default family is Qwen3 1.7B/4B (Apache-2.0). The secondary
choice is Llama 3.2 3B (Llama 3.2 Community License; record its terms).
Every report records the model tag, digest, quantization, server version,
sampling parameters, seed, and hardware. CI uses only scripted or replayed
(recorded) providers, so it stays free and deterministic. Live local-model
results are produced on the box, committed with their cassettes, and labelled
separately from CI results. Installing a runtime and pulling models (roughly
1.5-3 GB per model) is a one-time box setup step and may require freeing
memory. Larger (7B+) models are not planned on this box.

## ADR-009: Programmatic graders by default; LLM-as-judge only with measured agreement

Status: Accepted (2026-10-09)

Reason: Without a strong judge model, using a small local model as an
LLM judge would produce numbers nobody can verify. The
`never_fabricate_metrics` policy requires every number to be traceable and
reproducible.

Alternatives considered: a small local model as judge (low reliability that
is never measured); a hosted judge (paid, not approved); human grading (not
reproducible in CI and does not scale).

Consequences: Evaluation suites are designed around answers that programs can
grade:

- normalized exact match and F1
- numeric tolerance and set equality
- abstention
- citation span verification against source text
- tool-set comparison

These graders are unit-tested, including an oracle run that must score 100%.
Qualities that need judgement (fluency, free-form faithfulness) are reported
as "not measured", never estimated. An LLM judge may be added later, but only
in a project that also measures judge-human agreement (`llm-evaluation-lab`).
