"""Tests for the document chunker."""

from pathlib import Path

from rag.chunker import Chunk, chunk_corpus, chunk_document
from rag.config import CHUNK_SIZE


def test_chunk_count():
    """Test that chunking a known string produces expected number of chunks."""
    # Create a temporary file with known content
    import tempfile

    content = "A" * 2500  # 2500 chars -> 3 chunks at 1000 chars each
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", prefix="test-doc-", delete=False
    ) as f:
        f.write(content)
        tmp_path = Path(f.name)

    try:
        chunks = chunk_document(tmp_path)
        assert len(chunks) == 3, f"Expected 3 chunks, got {len(chunks)}"
        assert len(chunks[0].text) == CHUNK_SIZE
        assert len(chunks[1].text) == CHUNK_SIZE
        assert len(chunks[2].text) == 500
    finally:
        tmp_path.unlink()


def test_chunk_ids_follow_pattern():
    """Test that chunk IDs follow the {stem}-{N} pattern."""
    import tempfile

    content = "Hello world. " * 200  # ~2600 chars
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", prefix="my-document-", delete=False
    ) as f:
        f.write(content)
        tmp_path = Path(f.name)

    try:
        chunks = chunk_document(tmp_path)
        stem = tmp_path.stem

        for i, chunk in enumerate(chunks):
            expected_id = f"{stem}-{i}"
            assert chunk.id == expected_id, (
                f"Expected chunk ID '{expected_id}', got '{chunk.id}'"
            )
            assert chunk.metadata["doc_name"] == stem
            assert chunk.metadata["chunk_index"] == i
    finally:
        tmp_path.unlink()


def test_single_chunk_document():
    """Test that a short document produces a single chunk."""
    import tempfile

    content = "Short document."
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", prefix="short-", delete=False
    ) as f:
        f.write(content)
        tmp_path = Path(f.name)

    try:
        chunks = chunk_document(tmp_path)
        assert len(chunks) == 1
        assert chunks[0].text == content
        assert chunks[0].metadata["chunk_index"] == 0
    finally:
        tmp_path.unlink()


def test_corpus_chunks_without_errors():
    """Test that all corpus docs can be chunked without errors."""
    corpus_dir = Path("corpus/docs")
    if not corpus_dir.exists():
        # Try relative to project root
        corpus_dir = Path(__file__).parent.parent / "corpus" / "docs"

    assert corpus_dir.exists(), f"Corpus directory not found at {corpus_dir}"

    chunks = chunk_corpus(corpus_dir)
    assert len(chunks) > 0, "Expected at least one chunk"

    # Verify all chunks have valid IDs
    seen_ids = set()
    for chunk in chunks:
        assert chunk.id not in seen_ids, f"Duplicate chunk ID: {chunk.id}"
        seen_ids.add(chunk.id)
        assert "-" in chunk.id, f"Chunk ID missing separator: {chunk.id}"
        assert len(chunk.text) > 0, f"Empty chunk text for {chunk.id}"
        assert len(chunk.text) <= CHUNK_SIZE, (
            f"Chunk {chunk.id} exceeds max size: {len(chunk.text)} > {CHUNK_SIZE}"
        )


def test_exact_boundary_document():
    """Test a document whose length is exactly CHUNK_SIZE."""
    import tempfile

    content = "X" * CHUNK_SIZE  # exactly 1000 chars
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", prefix="exact-", delete=False
    ) as f:
        f.write(content)
        tmp_path = Path(f.name)

    try:
        chunks = chunk_document(tmp_path)
        assert len(chunks) == 1
        assert len(chunks[0].text) == CHUNK_SIZE
    finally:
        tmp_path.unlink()
