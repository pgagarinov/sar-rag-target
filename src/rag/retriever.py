"""Hybrid BM25+vector retrieval via ChromaDB with RRF fusion."""

import math
import string
from dataclasses import dataclass, field

import chromadb

from rag.config import TOP_K

# BM25 hyperparameters
_BM25_K1 = 0.5
_BM25_B = 0.75

# RRF constant
_RRF_K = 10

# BM25 weight in RRF fusion (vector weight is 1x)
_BM25_WEIGHT = 3


@dataclass
class RetrievalResult:
    chunk_id: str
    text: str
    score: float
    metadata: dict = field(default_factory=dict)


def _tokenize(text: str) -> list[str]:
    """Lowercase and split on whitespace/punctuation."""
    text = text.lower()
    text = text.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))
    return [t for t in text.split() if t]


def _compute_bm25_scores(
    query_tokens: list[str],
    corpus_texts: list[str],
) -> list[float]:
    """Compute BM25 scores for each document in corpus_texts against query_tokens.

    Uses k1=_BM25_K1, b=_BM25_B. IDF computed over the given corpus.
    """
    tokenized_corpus = [_tokenize(doc) for doc in corpus_texts]
    n_docs = len(tokenized_corpus)

    if n_docs == 0:
        return []

    # Average document length
    avg_dl = sum(len(doc) for doc in tokenized_corpus) / n_docs

    # Document frequency for each query term
    df: dict[str, int] = {}
    for term in query_tokens:
        df[term] = sum(1 for doc in tokenized_corpus if term in doc)

    scores: list[float] = []
    for doc_tokens in tokenized_corpus:
        doc_len = len(doc_tokens)
        tf_map: dict[str, int] = {}
        for token in doc_tokens:
            tf_map[token] = tf_map.get(token, 0) + 1

        score = 0.0
        for term in query_tokens:
            tf = tf_map.get(term, 0)
            if tf == 0:
                continue
            idf = math.log((n_docs - df.get(term, 0) + 0.5) / (df.get(term, 0) + 0.5) + 1.0)
            numerator = tf * (_BM25_K1 + 1)
            denominator = tf + _BM25_K1 * (1 - _BM25_B + _BM25_B * doc_len / avg_dl)
            score += idf * (numerator / denominator)
        scores.append(score)

    return scores


def retrieve(
    collection: chromadb.Collection,
    query: str,
    k: int = TOP_K,
) -> list[RetrievalResult]:
    """Hybrid BM25+vector retriever with RRF fusion.

    Steps:
    1. Over-fetch k*4 candidates from ChromaDB (vector search).
    2. Score all candidates with BM25.
    3. Combine ranks via reciprocal rank fusion (BM25 weighted 3x).
    4. Return top-k by fused score.
    """
    fetch_n = min(k * 4, collection.count())
    if fetch_n == 0:
        return []

    raw = collection.query(
        query_texts=[query],
        n_results=fetch_n,
        include=["documents", "distances", "metadatas"],
    )

    if not raw["ids"] or not raw["ids"][0]:
        return []

    ids = raw["ids"][0]
    docs = raw["documents"][0]
    distances = raw["distances"][0]
    metadatas = raw["metadatas"][0] if raw["metadatas"] else [{}] * len(ids)

    # --- BM25 scoring over candidates ---
    query_tokens = _tokenize(query)
    bm25_scores = _compute_bm25_scores(query_tokens, docs)

    # --- Vector rank (already sorted by ChromaDB, rank 0 = best) ---
    # BM25 rank: sort descending by BM25 score
    bm25_order = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
    bm25_rank_of: dict[int, int] = {idx: rank for rank, idx in enumerate(bm25_order)}

    # --- RRF fusion ---
    rrf_scores: list[float] = []
    for i in range(len(ids)):
        vec_rank = i  # ChromaDB already returns in distance order
        bm25_rank = bm25_rank_of[i]
        rrf = 1.0 / (_RRF_K + vec_rank) + _BM25_WEIGHT / (_RRF_K + bm25_rank)
        rrf_scores.append(rrf)

    # Sort by fusion score descending
    fused_order = sorted(range(len(ids)), key=lambda i: rrf_scores[i], reverse=True)

    # Build results
    results: list[RetrievalResult] = []
    for i in fused_order[:k]:
        meta = metadatas[i] if metadatas else {}
        results.append(
            RetrievalResult(
                chunk_id=ids[i],
                text=docs[i],
                score=rrf_scores[i],
                metadata=meta,
            )
        )

    return results
