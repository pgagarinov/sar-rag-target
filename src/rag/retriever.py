"""Vector retrieval via USearch index."""

from dataclasses import dataclass, field

import numpy as np

from rag.config import TOP_K
from rag.embeddings import get_embedding_function
from rag.indexer import VectorIndex


@dataclass
class RetrievalResult:
    chunk_id: str
    score: float
    metadata: dict = field(default_factory=dict)


# Module-level cache so we don't reload the model per query.
_ef = None


def _get_ef():
    global _ef
    if _ef is None:
        _ef = get_embedding_function()
    return _ef


def retrieve(
    index: VectorIndex,
    query: str,
    k: int = TOP_K,
) -> list[RetrievalResult]:
    """Retrieve top-k chunks by cosine similarity."""
    ef = _get_ef()
    query_vec = np.array(ef([query]), dtype=np.float16)[0]

    matches = index.search(query_vec, k)

    results: list[RetrievalResult] = []
    for pos, distance in matches:
        results.append(
            RetrievalResult(
                chunk_id=index.chunk_ids[pos],
                score=1.0 - distance,
            )
        )

    return results
