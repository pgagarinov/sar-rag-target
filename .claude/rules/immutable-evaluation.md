# Immutable Evaluation

## HARD RULE

**NEVER modify these files — they are the measurement apparatus:**

- `src/rag/evaluator.py` — metric computation (precision, recall, MRR, NDCG)
- `corpus/eval_set.json` — 2,814 golden labels from QASPER annotators

These define what "good retrieval" means. Modifying them does not improve retrieval — it corrupts the measurement. Any metric gain from changing the evaluator is fake.

## What This Means

- Do not change how precision, recall, MRR, or NDCG are computed
- Do not change how gold_chunk_ids are loaded or matched
- Do not filter, skip, or reweight questions
- Do not relax matching criteria (e.g., substring instead of exact ID match)
- Do not add post-processing between retrieve() and the metric calculation

## If You Need Additional Metrics

Create a new file (e.g., `extended_metrics.py`). Import from `evaluator.py` — never modify it. The existing metrics must remain unchanged as the ground truth for the supervisor.

## Why

The supervisor uses MRR from the evaluator to decide keep/discard. If the evaluator changes, the supervisor loses its reference frame. All historical comparisons become invalid. The research loop breaks.

