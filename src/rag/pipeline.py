"""End-to-end RAG pipeline: chunk, index, evaluate."""

from pathlib import Path

import chromadb

from rag.chunker import chunk_corpus
from rag.config import CHROMA_PATH, CORPUS_DIR
from rag.evaluator import EvalReport, evaluate, write_report
from rag.indexer import build_index, load_index


def setup(corpus_dir: Path | None = None) -> chromadb.Collection:
    """Chunk the corpus and build the ChromaDB index.

    Returns the collection for querying.
    """
    if corpus_dir is None:
        corpus_dir = Path(CORPUS_DIR)

    print(f"Chunking corpus from {corpus_dir}...")
    chunks = chunk_corpus(corpus_dir)
    print(f"  {len(chunks)} chunks from {len(set(c.metadata['doc_name'] for c in chunks))} documents")

    print("Building ChromaDB index...")
    collection = build_index(chunks)
    print(f"  Collection '{collection.name}' with {collection.count()} vectors")

    return collection


def run_eval(corpus_dir: Path | None = None) -> EvalReport:
    """Run the full evaluation pipeline.

    Chunks corpus, builds index, evaluates, writes report.
    """
    collection = setup(corpus_dir)

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
