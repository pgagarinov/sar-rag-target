---
name: run
description: "Clean ChromaDB, run eval pipeline, report metrics"
user_invocable: true
---

# /run — Evaluate the RAG System

Clean the ChromaDB index, chunk the QASPER corpus, build a fresh index, run evaluation against all questions in eval_set.json, and report metrics.

## Steps

```bash
rm -rf ${CHROMA_PERSIST_DIR:-/tmp/qasper-chroma}
rm -f ${RAG_REPORT_PATH:-/tmp/rag-eval-report.json}
PYTHONPATH=src python -m rag.pipeline
```

## Output

The pipeline prints:
- Number of chunks and papers indexed
- Precision@5, Recall@5, MRR, NDCG@5
- Questions with hits / total questions
- Status: all_clear or has_failures

It also writes a JSON report to `${RAG_REPORT_PATH:-/tmp/rag-eval-report.json}`.

## Important

- This is the ONLY entry point for evaluation
- Always cleans ChromaDB before rebuilding (ensures fresh index)
- Uses MLX embeddings on Apple Silicon (falls back to ONNX on other platforms)
- Corpus loaded from HuggingFace `allenai/qasper` (cached automatically)
