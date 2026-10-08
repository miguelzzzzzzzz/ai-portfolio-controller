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
