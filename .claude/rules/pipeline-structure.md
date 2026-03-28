# Rule: Pipeline Structure

## Immutable Files

Never modify the following files — they define the evaluation ground truth:

- `corpus/docs/*.md` — Source documentation files
- `corpus/eval_set.json` — Gold-standard evaluation questions and answers

## Verification Required

Always run `pixi run eval` after making changes to any pipeline component. Verify that the primary metric (recall@5) has improved or at least not regressed.

## Change Discipline

- Keep changes minimal and focused on one technique at a time
- Document what you changed and why in commit messages
- If a change degrades metrics, revert it before trying something else
- Compare before/after eval reports to understand the impact

## Module Boundaries

- `chunker.py` — Only document splitting logic. No retrieval or evaluation.
- `indexer.py` — Only ChromaDB index management. No chunking or retrieval logic.
- `retriever.py` — Only vector search queries. No index building or evaluation.
- `reranker.py` — Only result reordering. No retrieval or index access.
- `evaluator.py` — Only metric computation and reporting. No index modification.
- `pipeline.py` — Orchestration only. Delegates to other modules.

## Configuration

All tunable parameters live in `config.py`. Do not hardcode values in other modules.
