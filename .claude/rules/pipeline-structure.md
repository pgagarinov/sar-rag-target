# Rule: Pipeline Structure

## Immutable Files

Never modify the following files — they define the evaluation ground truth:

- `corpus/eval_set.json` — 2,814 QASPER questions with gold_chunk_ids from annotator evidence
- `src/rag/paths.py` — Infrastructure file for env var overrides (never edited by researcher)
- `src/rag/embeddings.py` — MLX/fallback embedding function (infrastructure)

## Evaluation Protocol

`/run` computes mean metrics across ALL 2,814 golden labels. Every question counts equally. A metric improvement must come from better retrieval, not from skipping hard questions.

## Verification Required

Always run `/run` (or `pixi run -e dev eval`) after making changes to any pipeline component. Verify that the primary metric (recall@5) has improved or at least not regressed.

## Change Discipline

- Keep changes minimal and focused on one technique at a time
- Document what you changed and why in commit messages
- If a change degrades metrics, revert it before trying something else
- Compare before/after eval reports to understand the impact

## Module Boundaries

- `chunker.py` — Only document splitting logic. No retrieval or evaluation.
- `corpus.py` — Only QASPER dataset loading. Streams papers, no materialization.
- `indexer.py` — Only USearch index management. No chunking or retrieval logic.
- `retriever.py` — Only vector search queries. No index building or evaluation.
- `reranker.py` — Only result reordering. No retrieval or index access.
- `evaluator.py` — Only metric computation and reporting. No index modification.
- `pipeline.py` — Orchestration only. Delegates to other modules.

## Configuration

All tunable parameters live in `config.py`. Do not hardcode values in other modules.

