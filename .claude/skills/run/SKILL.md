---
name: run
description: "Build USearch index from QASPER, run eval pipeline, report metrics"
user_invocable: true
---

# /run — Evaluate the RAG System

Stream QASPER papers from HuggingFace, chunk them, build a fresh USearch index with MLX embeddings, run evaluation against all 2,814 questions in eval_set.json, and report metrics.

## Steps

```bash
rm -f ${RAG_REPORT_PATH:-/tmp/rag-eval-report.json}
PYTHONPATH=src python -m rag.pipeline
```

## Metrics

The pipeline computes mean metrics across ALL golden labels in eval_set.json:

- **Precision@5**: mean(relevant_in_top5 / 5) across all questions
- **Recall@5**: mean(relevant_in_top5 / total_gold) across all questions
- **MRR**: mean(1/rank_of_first_hit) across all questions
- **NDCG@5**: mean(normalized discounted cumulative gain) across all questions
- **Hits**: count of questions with at least one relevant result in top-5

Each question has gold_chunk_ids from QASPER annotator evidence paragraphs. A retrieved chunk is "relevant" if its ID matches any gold_chunk_id.

## Output

Report written to `${RAG_REPORT_PATH:-/tmp/rag-eval-report.json}` with per-question breakdown.

## Important

- This is the ONLY entry point for evaluation
- Uses USearch (HNSW, f16) for vector indexing — NOT ChromaDB
- Uses MLX embeddings on Apple Silicon (falls back to sentence-transformers on other platforms)
- Corpus streamed from HuggingFace `allenai/qasper` (no local corpus/docs/ directory)
- Index is ephemeral (rebuilt every run, not persisted)

