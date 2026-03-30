"""ChromaDB index management."""

import shutil
from pathlib import Path

import chromadb

from rag.chunker import Chunk
from rag.config import CHROMA_PATH, COLLECTION_NAME
from rag.embeddings import get_embedding_function


def build_index(chunks: list[Chunk]) -> chromadb.Collection:
    """Build a ChromaDB collection from chunks."""
    chroma_path = Path(CHROMA_PATH)
    if chroma_path.exists():
        shutil.rmtree(chroma_path)

    ef = get_embedding_function()
    client = chromadb.PersistentClient(path=str(chroma_path))

    try:
        client.delete_collection(COLLECTION_NAME)
    except ValueError:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        embedding_function=ef,
    )

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
    ef = get_embedding_function()
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    return client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
