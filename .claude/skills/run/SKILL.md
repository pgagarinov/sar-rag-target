---
name: run
description: "Build or load cached USearch index from QASPER, run eval pipeline, report metrics"
user_invocable: true
---

# /run — Evaluate the RAG System

Build or load a cached USearch index, run evaluation against all 2,814 questions in eval_set.json, and report metrics.

## Steps

```bash
rm -f ${RAG_REPORT_PATH:-/tmp/rag-eval-report.json}
PYTHONPATH=src python -m rag.pipeline
```

## Caching

The index is cached in `$RAG_INDEX_CACHE_DIR` (default `/tmp/rag-index-cache`). Cache invalidation is output-based: chunk IDs are hashed to detect changes.

- **Cache HIT** (~12s): only retriever/reranker/evaluator code changed → load cached index, run queries
- **Cache MISS** (~80s): chunker/corpus/embeddings/config changed → full rebuild, save cache
- **Force rebuild**: set `RAG_FORCE_REBUILD=1`

## Metrics

The pipeline computes mean metrics across ALL golden labels in eval_set.json:

- **NDCG@5** (primary): mean(normalized discounted cumulative gain) across all questions
- **Recall@5** (secondary): mean(relevant_in_top5 / total_gold) across all questions
- **MRR**: mean(1/rank_of_first_hit) across all questions
- **Precision@5**: mean(relevant_in_top5 / 5) across all questions

## Important

- This is the ONLY entry point for evaluation
- Uses USearch (HNSW, f16) for vector indexing
- Uses MLX embeddings on Apple Silicon (falls back to sentence-transformers)
- Corpus streamed from HuggingFace `allenai/qasper`

