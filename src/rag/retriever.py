"""Vector similarity retrieval via ChromaDB."""

from dataclasses import dataclass, field

import chromadb

from rag.config import TOP_K


@dataclass
class RetrievalResult:
    chunk_id: str
    text: str
    score: float
    metadata: dict = field(default_factory=dict)


def retrieve(
    collection: chromadb.Collection,
    query: str,
    k: int = TOP_K,
) -> list[RetrievalResult]:
    """Retrieve top-k chunks by cosine similarity.

    ChromaDB returns distances (lower is more similar for cosine).
    We convert to similarity scores: score = 1 - distance.
    """
    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents", "distances", "metadatas"],
    )

    retrieval_results = []
    if results["ids"] and results["ids"][0]:
        for i, chunk_id in enumerate(results["ids"][0]):
            distance = results["distances"][0][i]
            score = 1.0 - distance  # cosine distance -> similarity
            retrieval_results.append(
                RetrievalResult(
                    chunk_id=chunk_id,
                    text=results["documents"][0][i],
                    score=score,
                    metadata=results["metadatas"][0][i] if results["metadatas"] else {},
                )
            )

    return retrieval_results
