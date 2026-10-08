# Project queue

Source of truth for ordering is `portfolio.yaml`; status comes from
`state.json`. The planner revisits scope before each project starts.

| # | Project | Status | Demonstrates |
| --- | --- | --- | --- |
| 1 | [production-rag-engine](https://github.com/miguelzzzzzzzz/production-rag-engine) | in progress | RAG, chunking, embeddings, hybrid BM25 + vector search, reranking, retrieval evals, FastAPI, Docker |
| 2 | llm-eval-harness | queued | LLM evaluation, prompt versioning, LLM-judge agreement, CI regression gates |
| 3 | agent-tool-runtime | queued | agents, typed tool registry, tool calling, malformed-call repair, tracing |
| 4 | document-intelligence | queued | document AI, OCR + vision models, structured extraction, field-level evals |
| 5 | embedding-finetuning-lab | queued | fine-tuning embeddings/rerankers, hard negatives, measured gains vs baseline |
| 6 | llm-gateway | queued | observability, caching, rate limiting, cost/latency optimization |
| 7 | multimodal-search | queued | CLIP-style image-text retrieval, ANN vs exact benchmarks |
| 8 | ml-training-pipeline | queued | classical/deep ML, experiment tracking, model registry, drift monitoring |
| 9 | llm-distillation | queued | distilling LLM labels into small models, quality vs cost trade-off |
| 10 | structured-output-benchmark | queued | JSON mode vs function calling vs constrained decoding reliability |

## Overlap check

- 1 and 7 both do retrieval: 1 is text RAG with hybrid lexical/dense retrieval and
  answer generation; 7 is cross-modal embedding search with ANN indexing trade-offs.
- 2 and 10 both evaluate LLM outputs: 2 is a general regression framework; 10 is
  a focused benchmark of output-constraint techniques. 10 may become a case study
  built *with* 2 if that proves cleaner (decide at planning time).
- 5 and 9 both fine-tune: 5 targets retrieval models, 9 targets classification
  via distillation from an LLM teacher.
