"""ChromaDB index management."""

import shutil
from pathlib import Path

import chromadb

from rag.chunker import Chunk
from rag.config import CHROMA_PATH, COLLECTION_NAME


def build_index(chunks: list[Chunk]) -> chromadb.Collection:
    """Build a ChromaDB collection from chunks.

    Uses the default ONNX all-MiniLM-L6-v2 embedding function.
    Removes any existing collection first to ensure a clean build.
    """
    chroma_path = Path(CHROMA_PATH)
    if chroma_path.exists():
        shutil.rmtree(chroma_path)

    client = chromadb.PersistentClient(path=str(chroma_path))

    # Delete collection if it exists (shouldn't after rmtree, but be safe)
    try:
        client.delete_collection(COLLECTION_NAME)
    except ValueError:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    # Add chunks in batches to avoid memory issues
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        collection.add(
            ids=[c.id for c in batch],
            documents=[c.text for c in batch],
            metadatas=[
                {
                    "doc_name": c.metadata["doc_name"],
                    "chunk_index": c.metadata["chunk_index"],
                    "chunk_id": c.id,
                }
                for c in batch
            ],
        )

    return collection


def load_index() -> chromadb.Collection:
    """Load an existing ChromaDB collection."""
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_collection(name=COLLECTION_NAME)
