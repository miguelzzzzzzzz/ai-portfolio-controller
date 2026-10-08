# Project queue

The queue follows the owner's brief (section 5); see `DECISIONS.md` ADR-006.
Ordering is encoded in `portfolio.yaml`; status comes from `state.json`. The
planner refines each project's scope before it starts.

| # | Project | Status | Demonstrates |
| --- | --- | --- | --- |
| 01 | [production-rag-engine](https://github.com/miguelzzzzzzzz/production-rag-engine) | in progress | RAG, chunking, embeddings, hybrid BM25 + vector search, reranking, retrieval evals, FastAPI, Docker |
| 02 | agentic-research-platform | queued (docs staged) | agents, planning, typed tool registry and routing, multi-step tool use, budgets/retries/timeouts, guardrails, cited answers, tracing, trajectory evals with fault injection |
| 03 | llm-evaluation-lab | queued | reusable LLM eval framework: JSONL datasets, multiple models/prompts, deterministic and model-based evaluators, structured-output validation, hallucination checks, latency/token/cost measurement, experiment comparison, regression detection, HTML/Markdown reports |
| 04 | multimodal-document-intelligence | queued | structured extraction from invoices, receipts, contracts, forms, and financial statements: classification, OCR/vision, validation, confidence scoring, JSON output, pydantic schemas, malformed-document handling, extraction-accuracy evals, API |
| 05 | mlops-fraud-detection | queued | feature engineering, baseline vs XGBoost/LightGBM, experiment tracking, model versioning, inference API, Docker, CI, monitoring and drift detection; precision/recall/F1/PR-AUC/ROC-AUC and latency |
| 06 | llm-finetuning-lab | queued | base vs prompt engineering vs RAG vs LoRA/QLoRA vs RAG plus fine-tuning; documented data, training config, hardware, and memory; only executed runs reported |
| 07 | ai-observability-platform | queued | reusable tracing for LLM/agent apps (model, prompt version, tokens, latency, errors, retries, tool calls, cost, eval results), OpenTelemetry, structured logs, metrics, dashboards, experiment comparison |
| 08 | semantic-search-engine | queued | embeddings, HNSW/ANN, lexical/vector/hybrid baselines, query expansion, reranking, filtering; benchmarks of retrieval quality, indexing time, query latency, and memory |
| 09 | voice-ai-agent | queued | audio to STT to agent/tool calling to TTS; streaming, interruption handling, session state, error recovery, end-to-end latency |
| 10 | ai-inference-benchmark | queued | local/hosted inference benchmarks across quantization, batching, model size, and concurrency; TTFT, tokens/sec, memory, throughput, latency; only executed results |

Project 02's PROJECT_SPEC, PLAN, ADRs, TODO, and CHANGELOG are staged on the
box in `/workspace/p02-agentic-research-platform/`. Its repository is created
only after 01 completes.

## Overlap check

- 01 and 08 both retrieve text. 01 is a RAG pipeline that ends in cited
  answers, using exact search. 08 benchmarks the search layer itself: HNSW/ANN
  vs exact search, query expansion, indexing time, and memory. 08's planner
  must show capabilities 01 does not already cover.
- 01 and 02 both touch retrieval. 02 uses 01's retriever as a pinned
  dependency behind a `SearchBackend` interface (ADR-007) and measures
  orchestration, not retrieval.
- 02 and 03 both evaluate. 02's graders are specific to agent trajectories
  (tool selection, calls, citations, failure taxonomy). 03 is the general
  prompt/LLM regression framework, including judge agreement (ADR-009).
- 02 and 07 both trace. 02 writes versioned JSONL traces for its own runs.
  07 is the cross-application observability platform (OpenTelemetry, cost,
  dashboards).
- 02 and 09 are both agents. 09's distinct skills are the speech pipeline and
  real-time latency, not tool-loop design.
- 03 and 10 both benchmark. 03 measures output quality, hallucination, cost,
  and regressions of LLM apps. 10 measures inference performance (TTFT,
  tokens/sec, throughput, memory) across quantization, batching, and
  concurrency.
- 03 and 07 both record latency, tokens, and cost. 03 does offline experiments
  on datasets. 07 instruments running applications.
- 06 and 01 both involve RAG. 06 uses RAG only as one adaptation strategy to
  compare against fine-tuning.
- 05 and 06 both train models. 05 is classical ML (gradient boosting) with
  MLOps around it. 06 adapts LLMs.
