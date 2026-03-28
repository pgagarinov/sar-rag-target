"""Document chunking with deterministic chunk IDs."""

from dataclasses import dataclass, field
from pathlib import Path

from rag.config import CHUNK_SIZE, CORPUS_DIR


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


def chunk_document(doc_path: Path) -> list[Chunk]:
    """Split a document into fixed-size character chunks.

    Chunk IDs are deterministic: {doc_stem}-{chunk_index} where index is 0-based.
    """
    text = doc_path.read_text(encoding="utf-8")
    doc_stem = doc_path.stem
    chunks = []

    for i in range(0, len(text), CHUNK_SIZE):
        chunk_text = text[i : i + CHUNK_SIZE]
        chunk_id = f"{doc_stem}-{i // CHUNK_SIZE}"
        chunks.append(
            Chunk(
                id=chunk_id,
                text=chunk_text,
                metadata={
                    "doc_name": doc_stem,
                    "chunk_index": i // CHUNK_SIZE,
                },
            )
        )

    return chunks


def chunk_corpus(corpus_dir: Path | None = None) -> list[Chunk]:
    """Chunk all markdown files in the corpus directory."""
    if corpus_dir is None:
        corpus_dir = Path(CORPUS_DIR)

    all_chunks = []
    for doc_path in sorted(corpus_dir.glob("*.md")):
        all_chunks.extend(chunk_document(doc_path))

    return all_chunks
