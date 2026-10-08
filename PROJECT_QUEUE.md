# Project queue

The queue follows the owner's brief (section 5); see `DECISIONS.md` ADR-006.
Ordering is encoded in `portfolio.yaml`; status comes from `state.json`. The
planner refines each project's scope before it starts.

| # | Project | Status | Demonstrates |
| --- | --- | --- | --- |
| 01 | [production-rag-engine](https://github.com/miguelzzzzzzzz/production-rag-engine) | in progress | RAG, chunking, embeddings, hybrid BM25 + vector search, reranking, retrieval evals, FastAPI, Docker |
| 02 | agentic-research-platform | queued (docs staged) | agents, planning, typed tool registry and routing, multi-step tool use, budgets/retries/timeouts, guardrails, cited answers, tracing, trajectory evals with fault injection |
| 03 | llm-evaluation-lab | queued | LLM evaluation, prompt versioning, programmatic graders, judge agreement, CI regression gates |
| 04 | multimodal-document-intelligence | queued | document AI, OCR, vision-language models, structured extraction, field-level evals |
| 05 | mlops-fraud-detection | queued | machine learning on imbalanced data, experiment tracking, model registry, serving, monitoring |
| 06 | llm-finetuning-lab | queued | parameter-efficient fine-tuning of small open models, evaluation against the base model |
| 07 | ai-observability-platform | queued | tracing, token/cost accounting, latency metrics, dashboards, alerting |
| 08 | semantic-search-engine | queued | vector databases, ANN indexing, semantic search, reranking, relevance/latency benchmarks |
| 09 | voice-ai-agent | queued | speech recognition and synthesis, tool-calling agent, end-to-end latency |
| 10 | ai-inference-benchmark | queued | latency, throughput, quality, and cost benchmarks across models, runtimes, and APIs |

Project 02's PROJECT_SPEC, PLAN, ADRs, TODO, and CHANGELOG are staged on the
box in `/workspace/p02-agentic-research-platform/`. Its repository is created
only after 01 completes.

## Overlap check

- 01 and 08 both retrieve text. 01 is a RAG pipeline that ends in cited
  answers, evaluated on retrieval quality. 08 is a search service built on a
  vector database, with ANN indexing trade-offs and serving latency at larger
  scale. 08's planner must show capabilities 01 does not already cover.
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
- 03 and 10 both benchmark. 03 measures output quality and regressions. 10
  measures inference performance and cost across runtimes and providers.
- 05 and 06 both train models. 05 is classical ML with MLOps around it. 06
  fine-tunes LLMs.
