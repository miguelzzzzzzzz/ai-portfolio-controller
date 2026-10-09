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

Status: Accepted (2026-10-09). Zero-spend part superseded for Cline DeepSeek only by ADR-016.

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

Status: Accepted (2026-10-09). Amended by ADR-016: Cline DeepSeek v4.1 is the default LLM and local models are the fallback.

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

## ADR-010: Offline evaluation (llm-evaluation-lab) vs live observability (ai-observability-platform); the run report is the contract

Status: Accepted (2026-10-09)

Reason: Both catalog entries mention latency, tokens, cost, eval results, and
experiment comparison (`portfolio.yaml` projects 03 and 07). Without a firm
boundary, the two projects would show the same skill twice.

Decision:
- `llm-evaluation-lab` (03) owns offline, batch evaluation of fixed, versioned
  datasets. That covers per-run quality metrics, statistically tested
  comparisons, regression gates, and benchmark-time latency/token/compute-cost
  measurements. Its artifacts are run directories and a versioned
  `report.json` schema.
- `ai-observability-platform` (07) owns instrumentation of running
  applications: OpenTelemetry spans, structured logs, metrics, dashboards,
  alerting, and per-request cost tracking of live traffic.
- 07 may ingest 03's `report.json` to show eval results next to production
  telemetry. That schema is the only integration point, and neither project
  imports the other's code.
- Inference-performance sweeps (TTFT, throughput, quantization, batching,
  concurrency) belong to `ai-inference-benchmark` (10). 03 reports latency at
  one documented concurrency setting.

Alternatives considered: merge cost/latency tracking into one shared library
used by 03, 07, and 10 (premature, and it couples three schedules); let 03
emit OpenTelemetry (duplicates 07 and adds infrastructure to an offline
tool).

Consequences: 03 has no OTel, dashboards, or live hooks. 07 has no dataset
runner or statistical gate. 07's planner should design against the published
`report.json` schema version. `PROJECT_QUEUE.md`'s overlap check already
states "03 does offline experiments on datasets; 07 instruments running
applications". This ADR makes that line binding.

## ADR-011: Cost reporting without paid APIs: measured local compute cost; dollar figures only as labelled estimates

Status: Accepted (2026-10-09). Zero-spend part superseded for Cline DeepSeek only by ADR-016; costs reported by Cline are real spend, not estimates.

Reason: `paid_api_budget_usd` is 0, and `never_fabricate_metrics` is set.
Several projects (03, 07, 10) report cost, and a dollar figure that looks like
real spend would be a fabricated metric.

Decision: Cost has two parts.
1. **Measured local compute cost**: wall time, CPU-seconds, peak RSS of the
   model-server process, tokens, and tokens/sec, each recorded with a hardware
   fingerprint.
2. **Optional dollar estimates**: token counts x prices from a versioned,
   dated price table that cites its source URL and retrieval date. These are
   always labelled "estimate" (`estimate: true` in JSON) and carry a
   tokenizer caveat, because local and hosted tokenizers differ.

Dollar estimates are never summed into anything called spend or cost
incurred. Real spend can only appear after a paid budget is approved under
ADR-002, and then it comes from provider billing/usage data.

Alternatives considered: omit dollar figures entirely (less useful for
comparing against hosted options); estimate energy cost from TDP (too
speculative to report).

Consequences: Reports stay honest and still answer "what would this workload
cost at published prices?". Each project that reports cost includes a test
that enforces the labelling. Price tables go stale, which is why they are
dated files rather than constants.

## ADR-012: llm-evaluation-lab is a standalone library; earlier projects may adopt it only after its release

Status: Accepted (2026-10-09)

Reason: 03 is designed to be reusable, and 01 (answer-generation evals) and
02 (agent evals) could use its graders, statistics, and gate. But 01 and 02
are built before 03 exists, and ADR-007 allows reuse only through pinned
releases of completed projects.

Decision:
- 03 depends on neither 01 nor 02.
- 01 and 02 do not depend on 03 during their build.
- 03 publishes a stable Python API (graders, stats, compare/gate, report
  schema) and a reusable CI workflow example.
- After 03's v0.1.0, adopting it in 01 or 02 (for example, gating 02's
  trajectory metrics with `evallab gate`) is an optional follow-up. Each
  adoption is recorded as its own ADR in the consuming repo and pinned per
  ADR-007.
- 03 duplicates a small OpenAI-compatible client and response cache instead
  of importing 02's (project ADR-0003). Extracting a shared provider package
  is reconsidered only if a third project needs the same code.

Alternatives considered: 03 imports 02's provider/replay layer (couples an
eval framework to an agent package for about 200 lines of client code);
retrofit 01/02 onto 03 before 03 is released (violates ADR-007 and reorders
the queue).

Consequences: No schedule coupling. 02's and 03's provider code is
duplicated, which is acknowledged. 02 keeps its own trajectory graders, and
03 demonstrates reuse through its plugin API and examples instead.

Owner decision (2026-10-09): Copying about 200 lines of OpenAI-compatible
client and response-cache code from 02 into 03 is accepted. It is a
deliberate duplication, consistent with ADR-007, which allows reuse only
through pinned releases and prefers a small copy over coupling an eval
framework to an agent package. 02's code does not exist yet (02's repository
`RabbitHole` has not been created), so the source commit can't be recorded
now. When the copy is made, the copied module's header and 03's project
ADR-0003 must cite the `RabbitHole` commit SHA and file path it came from.

## ADR-013: Committing small public benchmark subsets when the license permits redistribution

Status: Accepted (2026-10-09)

Reason: 01 and 02 download their evaluation data with checksums and never
commit it. 03's CI gate must replay and re-grade committed runs offline and
deterministically, so it needs the exact examples. Its subsets are small (a
few hundred examples per dataset), and their licenses allow redistribution
with attribution (verified below).

Decision:
- A project may commit a small benchmark subset when the license explicitly
  permits redistribution.
- Each committed dataset lives in its own directory with the upstream
  `LICENSE`/attribution, the source revision, and the sampling script and
  seed. The README lists dataset licenses separately from the code license.
- Share-alike terms (CC BY-SA) apply to those files only.
- Data whose license does not clearly permit redistribution is downloaded by
  script with a checksum, as before.
- Full datasets are never committed.

Alternatives considered: always download in CI with a cache (network
dependence in the gate, and cache eviction breaks reproducibility); commit
only example IDs (CI would still need the data).

Consequences: 03's CI is fully offline. Licensing is visible per directory,
and the review gate's licensing checks apply. 01's and 02's existing choices
are unchanged.

Owner decision (2026-10-09): Accepted for 03's GSM8K (MIT) and SQuAD 2.0
(CC BY-SA 4.0, share-alike) subsets, on these conditions:

- Each subset lives in its own data folder (for example `data/gsm8k/` and
  `data/squad_v2/`) with its own `LICENSE` file and attribution, separate
  from the repository's code license.
- The share-alike terms apply only to the SQuAD 2.0 folder.
- Each subset stays small (a few hundred examples, never the full dataset).

Licenses verified on 2026-10-09:

- **GSM8K**: MIT License, Copyright (c) 2021 OpenAI (`LICENSE` in
  github.com/openai/grade-school-math; the Hugging Face card `openai/gsm8k`
  also says MIT). MIT permits redistribution as long as the copyright and
  permission notice are included, so the subset directory carries that
  `LICENSE` text.
- **SQuAD 2.0**: CC BY-SA 4.0 (stated on rajpurkar.github.io/SQuAD-explorer;
  the Hugging Face card `rajpurkar/squad_v2` also says cc-by-sa-4.0; the
  passages come from Wikipedia, which is also CC BY-SA). Redistribution is
  permitted with attribution, a license link, an indication of changes (the
  subset was sampled), and the same license for the redistributed subset. The
  subset directory carries the attribution, a CC BY-SA 4.0 notice, and the
  sampling script and seed.

## ADR-014: Witty repository names, plain descriptions, stable catalog ids

Status: Accepted (2026-10-09)

Reason: The owner chose memorable PascalCase repository names (for example
`CitationNeeded`, `RabbitHole`, `HNSWFromScratch`) to make the portfolio
stand out. A clever name alone doesn't tell a reviewer what a repository
does, so every scannable surface also has to say it plainly.

Decision:
- Each catalog entry in `portfolio.yaml` has three names:
  - `id`: stable and descriptive (for example `production-rag-engine`). It is
    the key in `state.json`, in script arguments, and in the tests.
  - `repo`: the GitHub repository name.
  - `title`: the display title, which may contain characters GitHub
    repository names can't (`LoRA & Order` -> `LoraAndOrder`).
- Repository names are validated when the catalog is loaded (unique,
  case-insensitively, and GitHub-legal).
- Each repository's GitHub description and README subtitle state plainly what
  the project is (for example "A production-style hybrid RAG service that
  answers with citations to exact source spans").
- Python distribution, import, and CLI names stay descriptive and are not
  renamed to match the repository. Renaming a package is risky and adds
  nothing.
- `production-rag-engine` was renamed to `CitationNeeded` on 2026-10-09.
  GitHub redirects the old URL. The local checkout stays at
  `/workspace/portfolio/production-rag-engine`.

Alternatives considered: switch catalog ids to the slugs (churns
`state.json`, the logs, and the tests, and ties internal keys to branding
that may change again); descriptive repository names (the owner preferred the
witty ones).

Consequences: `create_project.py --create-repo` creates repositories under
their slugs. Links in the controller use the slugs. Historical log entries
keep the id they were written with.

## ADR-015: Hardware-honest scope for projects 06, 08, and 10

Status: Accepted (2026-10-09)

Reason: The box is CPU-only (8 cores, 15 GB RAM), no GPU or paid API is
available (ADR-002), and `never_fabricate_metrics` is set. As written, the
brief's entries for 06, 08, and 10 either assume GPU-scale work or overlap
with project 01. Each scope below keeps the brief's objective while making
every published number something the box (or an approved free resource) can
actually produce.

Decision:
- **06 llm-finetuning-lab (LoRA & Order):** LoRA fine-tuning of a tiny open
  model (about 0.5B parameters) on one narrow, well-defined task, trained on
  the box's CPU. It is compared against the base model, prompt engineering,
  RAG, and RAG plus LoRA on the same evaluation set. QLoRA (which needs a
  CUDA GPU for bitsandbytes 4-bit) runs only on free Colab or Kaggle GPU
  sessions, and only if the owner approves. Those runs are labelled with the
  platform, GPU type, and date, and are reported separately from CPU results.
  Without approval, QLoRA is documented as "not run".
- **08 semantic-search-engine (HNSW From Scratch):** the project centres on an
  HNSW index implemented from scratch. It is benchmarked against exact search
  and the established libraries hnswlib and FAISS on recall@k, query latency,
  index build time, and memory, with sweeps over M, efConstruction, and
  efSearch, on real embeddings. Hybrid search and query expansion are removed
  because project 01 already covers hybrid lexical/dense retrieval.
- **10 ai-inference-benchmark (Quant Leap):** benchmarks llama.cpp on CPU
  across quantization levels, batching, and concurrency, on hardware
  documented in every report (CPU model, cores, RAM, OS, build flags). It
  measures time to first token, tokens/sec, memory, throughput, and total
  latency. It publishes no GPU results, and hosted APIs are benchmarked only
  if a budget is approved.

Alternatives considered: keep the GPU-oriented scope and mark most results
"not run" (a hollow project); rent GPUs (spend not approved); keep hybrid
search in 08 (duplicates 01's strongest feature).

Consequences: `portfolio.yaml` and `PROJECT_QUEUE.md` entries for 06, 08, and
10 reflect these scopes. Each planner writes its milestones within them.
Results are smaller in scale but fully reproducible on documented hardware,
and each README states its hardware limits explicitly.

## ADR-016: Cline DeepSeek v4.1 is the default LLM; local models are the free fallback

Status: Accepted (2026-10-09). Amends ADR-008; supersedes the zero-spend parts of ADR-002 and ADR-011 for Cline DeepSeek only. Amended 2026-10-09 (see "Amendment: Cline Pass billing" below): the model id is `cline-pass/deepseek-v4.1-flash`.

Reason: On 2026-10-09 the owner authorized Cline DeepSeek v4.1, on a free or
paid Cline Pass, as the default LLM for every project, with unlimited usage
(no spend cap). The CPU-only box can serve only small local models, which are
too weak for the agent, answer-generation, and evaluation work that projects
01, 02, 03, and 07 need. A hosted model that is cheap per call removes that
ceiling while the provider interface from ADR-002 and ADR-008 keeps projects
portable.

Decision:
- **Default provider:** model `deepseek/deepseek-v4.1-flash` via
  `https://api.cline.bot/api/v1/chat/completions` (OpenAI-style chat
  completions). The key is read from the `CLINE_API_KEY` environment variable
  and is never logged, printed, or committed.
- **Fallback:** small local models (about 1.7B parameters or smaller) behind
  an OpenAI-compatible server, as in ADR-008, for offline work or when Cline is
  unavailable. Reports name the provider that produced each result.
- **CI:** recorded (cassette) replies only. CI never calls Cline or any other
  model, so it stays free and deterministic.
- **Spend:** no budget limit. The owner authorized unlimited Cline usage on
  2026-10-09. Every other paid API stays at zero (`paid_api_budget_usd: 0`).
- **Cost logging:** every call, from every project, appends one record (time
  in Asia/Manila, project, model, prompt/completion/reasoning tokens, the
  reported `usage.cost`, latency, outcome) to a single shared spend log on the
  box, `/workspace/portfolio/.cline/calls.jsonl`. It sits outside every
  repository and is never committed. Daily totals are summed per calendar day
  in Asia/Manila (midnight to midnight). When a response does not report its
  cost, the record stores `cost: null` and a warning is logged for that call;
  the call is still counted.
- **Runaway guard (not a budget):** before each call, the client checks the
  shared log and stops if the most recent calls are consecutive failures
  (default: 3). Each call retries at most twice with backoff, and a loop that
  keeps retrying the same failing request is stopped rather than continued.
- **API quirks observed on 2026-10-09:** the OpenAI-style payload is wrapped as
  `{"data": {...}}`, so clients unwrap `data` before reading `choices` and
  `usage`. The model spends hidden reasoning tokens before answering, so
  requests set `max_tokens` to 1000 or more; a two-word reply used 26
  reasoning tokens out of 28 completion tokens. Responses report `usage.cost`
  in US dollars. One review request (about 6 KB prompt, `max_tokens` 4000)
  failed with HTTP 500 `empty response content`, so clients treat that error
  as retryable and log it.
- **Unverified through Cline:** tool calls, streaming, `response_format`
  (JSON mode or schemas), and reasoning-effort controls. They are checked in
  project 01's M5 (structured answers) and M6 (service) with recorded tests
  before any project relies on them; until then, clients use plain chat
  completions and parse and validate output themselves.

Alternatives considered: stay local-only (ADR-008 as written; quality ceiling
too low for agent and generation work); other hosted APIs (not authorized);
hard daily or per-run spend caps (proposed, then dropped by the owner in
favour of visible per-call cost logging).

Consequences: `portfolio.yaml` records the default and fallback providers,
the spend log location, and the runaway guard. Evaluation reports that use
Cline state the model id, date, and the summed reported cost from the spend
log; those dollar figures are real spend, unlike the labelled estimates of
ADR-011. Results stay reproducible in CI through recorded replies, and live
results are labelled as such. If Cline changes pricing, model ids, or its
response format, the provider adapter and this ADR are updated together.

### Amendment (2026-10-09): Cline Pass billing

Reason: the first calls used the model id `deepseek/deepseek-v4.1-flash`.
Cline bills that id against prepaid credits, not against the owner's Cline
Pass. The credit balance ran out (HTTP 402 `insufficient_credits`, balance
about $0.007) during the second cycle on 2026-10-09.

Decision:
- **Model id:** every project uses `cline-pass/deepseek-v4.1-flash`, which is
  billed to the owner's Cline Pass. The plain `deepseek/deepseek-v4.1-flash`
  id must not be used, and credits are never bought by the agents.
- **HTTP 402** from Cline means a request was billed in credits mode (wrong
  model id) or the credit balance is empty. It is a configuration error: the
  client stops and reports it instead of retrying.
- **Pass limits:** the Pass has rolling five-hour, weekly, and monthly usage
  limits. `GET https://api.cline.bot/api/v1/users/me/plan/usage-limits`
  (same bearer key) returns `percentUsed` and `resetsAt` for each. Every cycle
  that uses Cline records the readings at its start and end. If a limit is
  reached, coding with Cline stops and the cycle reports the blocker; the
  agent does not replace Cline by writing large amounts of code itself.
- **Cost labelling:** on Pass-billed calls, the `usage.cost` field is a
  reference price, not money spent. The spend log stores it in `cost` next to
  `billing: cline-pass` and `cost_kind: reference`, and reports label it
  "reference cost". Real spend is only reported for credit-billed calls.
- **Observed behaviour (2026-10-09):** long hidden reasoning can consume the
  whole `max_tokens` budget. The API then returns `finish_reason: length`
  with little or no content, or HTTP 500 `empty response content`. Clients
  use `max_tokens` of 16,000-24,000 for code and keep prompts to one file or
  one focused task. Prompts that asked for large, many-part outputs failed
  this way and succeeded once split.
