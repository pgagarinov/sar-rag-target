"""Tests for the document chunker."""

from rag.chunker import Chunk, chunk_text
from rag.config import CHUNK_SIZE


def test_chunk_count():
    """Test that chunking a known string produces expected number of chunks."""
    content = "A" * 2500  # 2500 chars -> 3 chunks at 1000 chars each
    chunks = chunk_text(content, "test-doc")
    assert len(chunks) == 3, f"Expected 3 chunks, got {len(chunks)}"
    assert len(chunks[0].text) == CHUNK_SIZE
    assert len(chunks[1].text) == CHUNK_SIZE
    assert len(chunks[2].text) == 500


def test_chunk_ids_follow_pattern():
    """Test that chunk IDs follow the {doc_id}-{N} pattern."""
    content = "Hello world. " * 200  # ~2600 chars
    chunks = chunk_text(content, "my-document")

    for i, chunk in enumerate(chunks):
        expected_id = f"my-document-{i}"
        assert chunk.id == expected_id, (
            f"Expected chunk ID '{expected_id}', got '{chunk.id}'"
        )
        assert chunk.metadata["doc_name"] == "my-document"
        assert chunk.metadata["chunk_index"] == i


def test_single_chunk_document():
    """Test that a short text produces a single chunk."""
    content = "Short document."
    chunks = chunk_text(content, "short")
    assert len(chunks) == 1
    assert chunks[0].text == content
    assert chunks[0].metadata["chunk_index"] == 0


def test_chunk_ids_unique():
    """Test that chunking produces unique IDs within a document."""
    content = "X" * 5000
    chunks = chunk_text(content, "doc")
    seen_ids = set()
    for chunk in chunks:
        assert chunk.id not in seen_ids, f"Duplicate chunk ID: {chunk.id}"
        seen_ids.add(chunk.id)
        assert "-" in chunk.id
        assert len(chunk.text) > 0
        assert len(chunk.text) <= CHUNK_SIZE


def test_exact_boundary_document():
    """Test a text whose length is exactly CHUNK_SIZE."""
    content = "X" * CHUNK_SIZE  # exactly 1000 chars
    chunks = chunk_text(content, "exact")
    assert len(chunks) == 1
    assert len(chunks[0].text) == CHUNK_SIZE
