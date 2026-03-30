"""End-to-end RAG pipeline: chunk, index, evaluate."""

import chromadb

from rag.chunker import chunk_corpus
from rag.config import CHROMA_PATH
from rag.evaluator import EvalReport, evaluate, write_report
from rag.indexer import build_index


def setup() -> chromadb.Collection:
    """Chunk the corpus and build the ChromaDB index."""
    print("Loading QASPER papers from HuggingFace...")
    chunks = chunk_corpus()
    print(f"  {len(chunks)} chunks from {len(set(c.metadata['doc_name'] for c in chunks))} papers")

    print("Building ChromaDB index (MLX embeddings)...")
    collection = build_index(chunks)
    print(f"  Collection '{collection.name}' with {collection.count()} vectors")

    return collection


def run_eval() -> EvalReport:
    """Run the full evaluation pipeline."""
    collection = setup()

    print("\nRunning evaluation...")
    report = evaluate(collection)
    write_report(report)

    print(f"\nResults:")
    print(f"  Precision@5: {report.precision_at_5:.4f}")
    print(f"  Recall@5:    {report.recall_at_5:.4f}")
    print(f"  MRR:         {report.mrr:.4f}")
    print(f"  NDCG@5:      {report.ndcg_at_5:.4f}")
    print(f"  Hits:        {report.questions_with_hits}/{report.total_questions}")
    print(f"  Status:      {report.status}")

    return report


if __name__ == "__main__":
    run_eval()
