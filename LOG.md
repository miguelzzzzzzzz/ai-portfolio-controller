# Daily log

Generated from `state.json` by `scripts/update_state.py render-log`. Do not edit by hand.

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

Remaining blockers: Daily scheduler not yet configured (needs the orchestrator's automation; cron on the box cannot drive the agent)

Next recommended task: M2: fastembed adapter (bge-small-en-v1.5, slow tests), BM25 index with hand-computed score tests, Retriever, index/search CLI
