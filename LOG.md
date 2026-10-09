# Daily log

Generated from `state.json` by `scripts/update_state.py render-log`. Do not edit by hand.

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
