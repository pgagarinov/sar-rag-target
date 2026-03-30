"""Tests for index caching — all use temp dirs and tiny indexes."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
from usearch.index import Index

from rag.cache import (
    _clear_cache,
    _compute_cache_key,
    _load_cache,
    _save_cache,
)
from rag.indexer import VectorIndex


def _make_tiny_index(n: int = 5, ndim: int = 8) -> tuple[Index, list[str]]:
    """Create a small USearch index with n random vectors."""
    index = Index(ndim=ndim, metric="cos", dtype="f16")
    vecs = np.random.randn(n, ndim).astype(np.float16)
    keys = np.arange(n, dtype=np.uint64)
    index.add(keys, vecs)
    chunk_ids = [f"doc-{i}" for i in range(n)]
    return index, chunk_ids


def test_save_and_load_round_trip():
    """Save a VectorIndex, load it back, verify chunk_ids and count match."""
    cache_dir = Path(tempfile.mkdtemp())
    index, chunk_ids = _make_tiny_index(10)
    cache_key = "test-key-abc123"

    _save_cache(index, cache_dir, cache_key, chunk_ids)

    result = _load_cache(cache_dir, cache_key)
    assert result is not None, "Cache load returned None"
    loaded_index, loaded_ids = result
    assert len(loaded_index) == 10
    assert loaded_ids == chunk_ids


def test_key_mismatch_returns_none():
    """Cache with different key returns None."""
    cache_dir = Path(tempfile.mkdtemp())
    index, chunk_ids = _make_tiny_index()

    _save_cache(index, cache_dir, "key-A", chunk_ids)

    result = _load_cache(cache_dir, "key-B")
    assert result is None


def test_missing_manifest_returns_none():
    """Empty cache dir returns None."""
    cache_dir = Path(tempfile.mkdtemp())
    result = _load_cache(cache_dir, "any-key")
    assert result is None


def test_missing_index_file_returns_none():
    """Cache with manifest but no index.usearch returns None."""
    cache_dir = Path(tempfile.mkdtemp())
    index, chunk_ids = _make_tiny_index()
    _save_cache(index, cache_dir, "key", chunk_ids)

    # Delete the index file
    (cache_dir / "index.usearch").unlink()

    result = _load_cache(cache_dir, "key")
    assert result is None


def test_missing_chunk_ids_file_returns_none():
    """Cache with manifest but no chunk_ids.json returns None."""
    cache_dir = Path(tempfile.mkdtemp())
    index, chunk_ids = _make_tiny_index()
    _save_cache(index, cache_dir, "key", chunk_ids)

    (cache_dir / "chunk_ids.json").unlink()

    result = _load_cache(cache_dir, "key")
    assert result is None


def test_corrupted_manifest_returns_none():
    """Garbage manifest returns None."""
    cache_dir = Path(tempfile.mkdtemp())
    index, chunk_ids = _make_tiny_index()
    _save_cache(index, cache_dir, "key", chunk_ids)

    (cache_dir / "manifest.json").write_text("not json{{{")

    result = _load_cache(cache_dir, "key")
    assert result is None


def test_size_mismatch_returns_none():
    """Manifest says 5 chunks but chunk_ids has 3 → returns None."""
    cache_dir = Path(tempfile.mkdtemp())
    index, chunk_ids = _make_tiny_index(5)
    _save_cache(index, cache_dir, "key", chunk_ids)

    # Overwrite chunk_ids with fewer entries
    with open(cache_dir / "chunk_ids.json", "w") as f:
        json.dump(["a", "b", "c"], f)

    result = _load_cache(cache_dir, "key")
    assert result is None


def test_clear_cache_removes_dir():
    """_clear_cache removes the directory."""
    cache_dir = Path(tempfile.mkdtemp())
    index, chunk_ids = _make_tiny_index()
    _save_cache(index, cache_dir, "key", chunk_ids)
    assert cache_dir.exists()

    _clear_cache(cache_dir)
    assert not cache_dir.exists()


def test_clear_cache_nonexistent_dir():
    """_clear_cache on nonexistent dir doesn't raise."""
    _clear_cache(Path("/tmp/nonexistent-rag-cache-test-12345"))


def test_compute_cache_key_deterministic():
    """Same chunks → same key across two calls."""

    def fake_iter():
        return iter(["doc-0", "doc-1", "doc-2"])

    with patch("rag.chunker.iter_chunk_ids", side_effect=[fake_iter(), fake_iter()]):
        key1 = _compute_cache_key()
        key2 = _compute_cache_key()

    assert key1 == key2
    assert len(key1) == 64  # SHA-256 hex


def test_compute_cache_key_changes_with_different_chunks():
    """Different chunk IDs → different key."""

    def ids_a():
        return iter(["doc-0", "doc-1"])

    def ids_b():
        return iter(["doc-0", "doc-1", "doc-2"])

    with patch("rag.chunker.iter_chunk_ids", side_effect=[ids_a(), ids_b()]):
        key1 = _compute_cache_key()
        key2 = _compute_cache_key()

    assert key1 != key2
