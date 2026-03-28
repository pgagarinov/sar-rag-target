# Agent: Reranker

## Role

Improve the ordering of retrieval results to push the most relevant chunks to the top.

## Capabilities

- Apply reranking strategies to retrieval results
- Filter results below a similarity threshold
- Score results using LLM-based relevance judgments
- Apply MMR (Maximal Marginal Relevance) for result diversity

## Current Implementation

The reranker is currently a **passthrough** — it returns results unchanged. This is the baseline for comparison.

## Improvement Strategies

### Similarity Threshold Filtering

Remove results below a minimum similarity score to reduce noise:

```python
def rerank(results, query):
    threshold = 0.3
    return [r for r in results if r.score >= threshold]
```

### BM25 Hybrid Scoring

Combine vector similarity with BM25 keyword relevance:

```python
from rank_bm25 import BM25Okapi

def rerank(results, query):
    corpus = [r.text.split() for r in results]
    bm25 = BM25Okapi(corpus)
    bm25_scores = bm25.get_scores(query.split())

    for i, r in enumerate(results):
        r.score = 0.7 * r.score + 0.3 * (bm25_scores[i] / max(bm25_scores))

    return sorted(results, key=lambda r: r.score, reverse=True)
```

### LLM-Based Relevance Scoring

Use a language model to judge whether each chunk answers the query:

```python
def rerank(results, query):
    for r in results:
        # Score relevance 0-1 using LLM
        r.score = llm_relevance_score(query, r.text)
    return sorted(results, key=lambda r: r.score, reverse=True)
```

### MMR for Diversity

Maximal Marginal Relevance balances relevance with diversity to avoid returning redundant chunks:

```python
def rerank(results, query, lambda_param=0.5):
    selected = []
    remaining = list(results)
    while remaining and len(selected) < k:
        best = max(remaining, key=lambda r:
            lambda_param * relevance(r) - (1 - lambda_param) * max_similarity(r, selected))
        selected.append(best)
        remaining.remove(best)
    return selected
```

## Guidelines

- Always benchmark against the passthrough baseline
- Run `pixi run eval` before and after changes
- Focus on recall@5 as the primary metric — reranking mainly helps precision
- Keep the reranker fast — it runs on every query
