"""USearch vector index with streaming build."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

import numpy as np
from usearch.index import Index

from rag.chunker import Chunk
from rag.embeddings import get_embedding_function


@dataclass
class VectorIndex:
    """In-memory vector index backed by USearch.

    Stores only vectors (f16) and chunk ID strings.
    Texts and metadata are NOT kept — the evaluator only needs chunk IDs.
    """
    _index: Index
    chunk_ids: list[str] = field(default_factory=list)

    def count(self) -> int:
        return len(self._index)

    def search(self, query_vector: np.ndarray, k: int) -> list[tuple[int, float]]:
        """Return list of (position, distance) for top-k nearest neighbors."""
        matches = self._index.search(query_vector, k)
        return list(zip(matches.keys.tolist(), matches.distances.tolist()))


def build_index(chunks: Iterator[Chunk], batch_size: int = 256) -> VectorIndex:
    """Build a USearch index by streaming chunks through the embedding function.

    Memory profile per batch: batch_size texts + their f16 embeddings.
    Only chunk ID strings are accumulated (a few hundred KB for 30K chunks).
    """
    ef = get_embedding_function()

    index: Index | None = None
    chunk_ids: list[str] = []

    batch_texts: list[str] = []
    batch_ids: list[str] = []

    def flush() -> None:
        nonlocal index
        if not batch_texts:
            return

        embeddings = np.array(ef(batch_texts), dtype=np.float16)

        if index is None:
            ndim = embeddings.shape[1]
            index = Index(ndim=ndim, metric="cos", dtype="f16")

        keys = np.arange(len(chunk_ids), len(chunk_ids) + len(batch_ids), dtype=np.uint64)
        index.add(keys, embeddings)

        chunk_ids.extend(batch_ids)
        batch_texts.clear()
        batch_ids.clear()

    for chunk in chunks:
        batch_texts.append(chunk.text)
        batch_ids.append(chunk.id)
        if len(batch_texts) >= batch_size:
            flush()

    flush()

    if index is None:
        index = Index(ndim=384, metric="cos", dtype="f16")

    return VectorIndex(_index=index, chunk_ids=chunk_ids)
