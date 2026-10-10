# Daily log


## 2026-10-10 — CitationNeeded M4 evaluation harness

- Milestone M4 done: `rag_engine.eval` (metrics, SciFact BEIR loader + MD5/zip-slip checks, structured-doc set, runner), `rag-engine evaluate`, `scripts/eval_table.py`.
- Committed hashing smoke reports under `evals/results/` (structured + SciFact); notes mark them as harness checks, not quality claims. SciFact data stays gitignored.
- Tests: 462 passed + 9 slow deselected; coverage ~95% (soft bar was ~96%; new eval modules). CI green: https://github.com/miguelzzzzzzzz/CitationNeeded/actions/runs/38012671154 (sha 96b3c33).
- Cline DeepSeek (`cline-pass/deepseek-v4.1-flash`) primary coder/reviewer; Kim applied API fixes (runner imports, Document.create, HybridRetriever.method, qrels remap) after review findings.
- Next: M5 answer generation.


Generated from `state.json` by `scripts/update_state.py render-log`. Do not edit by hand.

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
