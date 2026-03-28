# Skill: /search — RAG Retrieval over FluxAPI Documentation

## Purpose

Answer user questions about FluxAPI by retrieving relevant documentation chunks from a vector database and synthesizing an answer.

## Workflow

1. **Parse the query**: Extract the user's question and identify key concepts.
2. **Retrieve**: Dispatch the retriever agent to find the top-k most relevant chunks from the ChromaDB index.
3. **Rerank** (optional): If initial results seem noisy or the query is ambiguous, dispatch the reranker agent to improve result ordering.
4. **Re-index** (if needed): If the corpus has changed or the index is stale, dispatch the chunker agent to rebuild the index before retrieving.
5. **Synthesize**: Combine retrieved chunks into a coherent answer, citing source documents.

## Agents

- **retriever** — Runs vector similarity search against the ChromaDB collection. Returns top-k chunks with scores.
- **reranker** — Improves result ordering using relevance scoring, filtering, or diversity strategies.
- **chunker** — Manages document chunking and index rebuilding when corpus or chunking strategy changes.

## Evaluation

Run `pixi run eval` to measure retrieval quality. The eval pipeline:
- Chunks all docs in `corpus/docs/`
- Builds a ChromaDB index
- Evaluates 20 questions against gold-standard chunk IDs
- Reports precision@5, recall@5, MRR, NDCG@5
- Writes detailed results to `/tmp/rag-eval-report.json`

The primary metric is **recall@5** (higher is better). The goal is to maximize the fraction of gold chunks found in the top 5 results.

## Key Files

- `src/rag/pipeline.py` — End-to-end pipeline orchestration
- `src/rag/retriever.py` — Vector search implementation
- `src/rag/reranker.py` — Result reranking (currently passthrough)
- `src/rag/chunker.py` — Document chunking
- `src/rag/indexer.py` — ChromaDB index management
- `src/rag/evaluator.py` — Evaluation framework
- `corpus/docs/` — FluxAPI documentation (DO NOT MODIFY)
- `corpus/eval_set.json` — Gold standard eval questions (DO NOT MODIFY)

## Constraints

- Never modify files in `corpus/docs/` or `corpus/eval_set.json`
- Always run `pixi run eval` after changes to verify improvement
- Keep changes minimal and focused on one technique at a time
- The chunk ID scheme is `{doc_stem}-{chunk_index}` with 1000-char fixed-size chunks
