"""Result reranking (baseline: passthrough).

This module provides a placeholder reranker that returns results unchanged.
Future improvements could include:
- BM25-based reranking
- Cross-encoder reranking
- LLM-based relevance scoring
- MMR (Maximal Marginal Relevance) for diversity
"""

from rag.retriever import RetrievalResult


def rerank(
    results: list[RetrievalResult],
    query: str,
) -> list[RetrievalResult]:
    """Rerank retrieval results.

    Baseline implementation: passthrough (returns input unchanged).
    """
    return results
