"""Document chunking with deterministic chunk IDs."""

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


def chunk_corpus() -> list[Chunk]:
    """Chunk all QASPER papers from HuggingFace dataset."""
    from rag.corpus import load_papers, paper_to_text
    papers = load_papers()
    all_chunks = []
    for paper in papers:
        text = paper_to_text(paper)
        all_chunks.extend(chunk_text(text, paper.id))
    return all_chunks
