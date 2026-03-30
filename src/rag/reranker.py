"""Result reranking (baseline: passthrough)."""

from rag.retriever import RetrievalResult


def rerank(
    results: list[RetrievalResult],
    query: str,
) -> list[RetrievalResult]:
    """Rerank retrieval results. Baseline: passthrough."""
    return results
