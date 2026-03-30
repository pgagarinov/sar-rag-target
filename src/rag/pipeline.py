"""End-to-end RAG pipeline: chunk, index, evaluate."""

from rag.cache import load_or_build
from rag.chunker import iter_chunks
from rag.evaluator import EvalReport, evaluate, write_report
from rag.indexer import VectorIndex, build_index


def setup() -> VectorIndex:
    """Load cached index or build from scratch (two-pass early exit)."""
    print("Preparing USearch index...")
    index = load_or_build(lambda: build_index(iter_chunks()))
    print(f"  {index.count()} vectors ready")
    return index


def run_eval() -> EvalReport:
    """Run the full evaluation pipeline."""
    index = setup()

    print("\nRunning evaluation...")
    report = evaluate(index)
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
