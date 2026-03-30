"""Index caching with two-pass early exit.

Infrastructure file — never edited by the researcher.

Pass 1 (cheap, ~1.5s): stream chunk IDs only, compute SHA-256 hash.
  If hash matches cached manifest → load index from disk, skip embedding.
Pass 2 (expensive, ~72s): stream full chunks, embed, build index, save cache.

The cache key is output-based: it captures the actual chunk IDs produced,
not the source code that produced them. Refactoring chunker.py without
changing its output does NOT invalidate the cache.

The embedding model name is included in the key so that switching models
forces a rebuild even if chunks are identical.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from rag.paths import FORCE_REBUILD, INDEX_CACHE_DIR

_MANIFEST_FILE = "manifest.json"
_INDEX_FILE = "index.usearch"
_CHUNK_IDS_FILE = "chunk_ids.json"

# Embedding model name — included in cache key.
# If the researcher changes the model, this must be updated.
_EMBEDDING_MODEL = "mlx-community/all-MiniLM-L6-v2-4bit"


def _compute_cache_key() -> str:
    """Stream chunk IDs and hash them with the embedding model name.

    ~1.5s — runs the chunker but not the embedder.
    """
    from rag.chunker import iter_chunk_ids

    h = hashlib.sha256()
    h.update(_EMBEDDING_MODEL.encode())
    for chunk_id in iter_chunk_ids():
        h.update(chunk_id.encode())
    return h.hexdigest()


def _load_cache(cache_dir: Path, expected_key: str) -> tuple | None:
    """Load cached index if manifest key matches and files are intact.

    Returns (usearch.Index, list[str]) or None on any failure.
    """
    from usearch.index import Index

    manifest_path = cache_dir / _MANIFEST_FILE
    if not manifest_path.exists():
        print("  Cache: no manifest found")
        return None

    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"  Cache: manifest unreadable ({e})")
        return None

    if manifest.get("cache_key") != expected_key:
        print("  Cache: key mismatch (chunks or model changed)")
        return None

    index_path = cache_dir / _INDEX_FILE
    chunk_ids_path = cache_dir / _CHUNK_IDS_FILE

    if not index_path.exists() or not chunk_ids_path.exists():
        print("  Cache: missing index or chunk_ids file")
        return None

    try:
        index = Index.restore(str(index_path))
        with open(chunk_ids_path, encoding="utf-8") as f:
            chunk_ids = json.load(f)
    except Exception as e:
        print(f"  Cache: failed to load ({e})")
        return None

    if len(index) != len(chunk_ids):
        print(f"  Cache: size mismatch (index={len(index)}, chunk_ids={len(chunk_ids)})")
        return None

    return index, chunk_ids


def _save_cache(
    index: object, cache_dir: Path, cache_key: str, chunk_ids: list[str],
) -> None:
    """Persist USearch index + chunk_ids + manifest to cache_dir."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    index.save(str(cache_dir / _INDEX_FILE))
    with open(cache_dir / _CHUNK_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunk_ids, f)
    with open(cache_dir / _MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump({"cache_key": cache_key, "num_chunks": len(chunk_ids)}, f)


def _clear_cache(cache_dir: Path) -> None:
    """Remove cache directory. Never raises."""
    try:
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
    except OSError:
        pass


def load_or_build(build_fn: object) -> object:
    """Load index from cache if valid, otherwise call build_fn and cache the result.

    Two-pass early exit:
      Pass 1: compute cache key from chunk IDs (~1.5s)
      If HIT:  load from disk, return immediately
      If MISS: call build_fn() (~72s), save cache, return
    """
    from rag.indexer import VectorIndex

    cache_dir = Path(INDEX_CACHE_DIR)

    if FORCE_REBUILD:
        print("  Cache: RAG_FORCE_REBUILD=1, rebuilding")
        _clear_cache(cache_dir)
        vi = build_fn()
        try:
            _save_cache(vi._index, cache_dir, "forced", vi.chunk_ids)
        except OSError as e:
            print(f"  Cache: failed to save ({e})")
        return vi

    # Pass 1: compute cache key (cheap — chunk IDs only)
    try:
        cache_key = _compute_cache_key()
    except Exception as e:
        print(f"  Cache: cannot compute key ({e}), rebuilding")
        return build_fn()

    # Try loading from cache
    result = _load_cache(cache_dir, cache_key)
    if result is not None:
        index, chunk_ids = result
        print(f"  Cache HIT: loaded {len(chunk_ids)} vectors from {cache_dir}")
        return VectorIndex(_index=index, chunk_ids=chunk_ids)

    # Pass 2: full rebuild
    print("  Cache MISS: rebuilding index")
    vi = build_fn()

    try:
        _clear_cache(cache_dir)
        _save_cache(vi._index, cache_dir, cache_key, vi.chunk_ids)
        print(f"  Cache: saved {vi.count()} vectors to {cache_dir}")
    except OSError as e:
        print(f"  Cache: failed to save ({e})")

    return vi
