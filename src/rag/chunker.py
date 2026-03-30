"""Document chunking with deterministic chunk IDs."""

from collections.abc import Iterator
from dataclasses import dataclass, field

from rag.config import CHUNK_SIZE


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)


def chunk_text(text: str, doc_id: str) -> list[Chunk]:
    """Split text into fixed-size character chunks with deterministic IDs."""
    chunks = []
    for i in range(0, len(text), CHUNK_SIZE):
        chunk_text = text[i : i + CHUNK_SIZE]
        chunk_id = f"{doc_id}-{i // CHUNK_SIZE}"
        chunks.append(
            Chunk(
                id=chunk_id,
                text=chunk_text,
                metadata={
                    "doc_name": doc_id,
                    "chunk_index": i // CHUNK_SIZE,
                },
            )
        )
    return chunks


def iter_chunks() -> Iterator[Chunk]:
    """Yield chunks from all QASPER papers without materializing everything."""
    from rag.corpus import iter_papers, paper_to_text
    for paper in iter_papers():
        text = paper_to_text(paper)
        yield from chunk_text(text, paper.id)
