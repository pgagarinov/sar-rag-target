"""Evaluation framework for retrieval quality."""

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import chromadb

from rag.config import EVAL_SET_PATH, REPORT_PATH, TOP_K
from rag.reranker import rerank
from rag.retriever import retrieve


@dataclass
class EvalQuestion:
    id: str
    question: str
    gold_chunk_ids: list[str]
    gold_answer: str
    difficulty: str
    type: str


@dataclass
class QuestionResult:
    id: str
    precision: float
    recall: float
    rr: float  # reciprocal rank
    ndcg: float
    retrieved: list[str]
    gold: list[str]


@dataclass
class EvalReport:
    precision_at_5: float
    recall_at_5: float
    mrr: float
    ndcg_at_5: float
    total_questions: int
    questions_with_hits: int
    per_question: list[QuestionResult]
    status: str


def load_eval_set(eval_set_path: Path | None = None) -> list[EvalQuestion]:
    """Load evaluation questions from JSON."""
    if eval_set_path is None:
        eval_set_path = Path(EVAL_SET_PATH)

    with open(eval_set_path, encoding="utf-8") as f:
        data = json.load(f)

    return [
        EvalQuestion(
            id=q["id"],
            question=q["question"],
            gold_chunk_ids=q["gold_chunk_ids"],
            gold_answer=q["gold_answer"],
            difficulty=q["difficulty"],
            type=q["type"],
        )
        for q in data
    ]


def _precision_at_k(retrieved: list[str], gold: set[str], k: int) -> float:
    """Precision@k: fraction of top-k results that are relevant."""
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for r in top_k if r in gold)
    return hits / len(top_k)


def _recall_at_k(retrieved: list[str], gold: set[str], k: int) -> float:
    """Recall@k: fraction of gold items found in top-k."""
    if not gold:
        return 1.0
    top_k = retrieved[:k]
    hits = sum(1 for r in top_k if r in gold)
    return hits / len(gold)


def _reciprocal_rank(retrieved: list[str], gold: set[str]) -> float:
    """Reciprocal rank: 1/position of first relevant result."""
    for i, r in enumerate(retrieved):
        if r in gold:
            return 1.0 / (i + 1)
    return 0.0


def _ndcg_at_k(retrieved: list[str], gold: set[str], k: int) -> float:
    """NDCG@k: normalized discounted cumulative gain."""
    top_k = retrieved[:k]

    # DCG: sum of (relevance / log2(position + 1))
    # Binary relevance: 1 if in gold, 0 otherwise
    dcg = 0.0
    for i, r in enumerate(top_k):
        if r in gold:
            dcg += 1.0 / math.log2(i + 2)  # +2 because position is 1-indexed

    # Ideal DCG: all gold items ranked first
    ideal_k = min(len(gold), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_k))

    if idcg == 0:
        return 0.0
    return dcg / idcg


def evaluate_question(
    collection: chromadb.Collection,
    question: EvalQuestion,
    k: int = TOP_K,
) -> QuestionResult:
    """Evaluate a single question."""
    results = retrieve(collection, question.question, k=k)
    results = rerank(results, question.question)

    retrieved_ids = [r.chunk_id for r in results]
    gold_set = set(question.gold_chunk_ids)

    precision = _precision_at_k(retrieved_ids, gold_set, k)
    recall = _recall_at_k(retrieved_ids, gold_set, k)
    rr = _reciprocal_rank(retrieved_ids, gold_set)
    ndcg = _ndcg_at_k(retrieved_ids, gold_set, k)

    return QuestionResult(
        id=question.id,
        precision=round(precision, 4),
        recall=round(recall, 4),
        rr=round(rr, 4),
        ndcg=round(ndcg, 4),
        retrieved=retrieved_ids,
        gold=question.gold_chunk_ids,
    )


def evaluate(
    collection: chromadb.Collection,
    eval_set_path: Path | None = None,
    k: int = TOP_K,
) -> EvalReport:
    """Evaluate all questions and compute aggregate metrics."""
    questions = load_eval_set(eval_set_path)
    question_results = []
    hits = 0

    for q in questions:
        result = evaluate_question(collection, q, k=k)
        question_results.append(result)
        if result.recall > 0:
            hits += 1

    n = len(question_results)
    if n == 0:
        return EvalReport(
            precision_at_5=0.0,
            recall_at_5=0.0,
            mrr=0.0,
            ndcg_at_5=0.0,
            total_questions=0,
            questions_with_hits=0,
            per_question=[],
            status="no_questions",
        )

    mean_precision = round(sum(r.precision for r in question_results) / n, 4)
    mean_recall = round(sum(r.recall for r in question_results) / n, 4)
    mrr = round(sum(r.rr for r in question_results) / n, 4)
    mean_ndcg = round(sum(r.ndcg for r in question_results) / n, 4)

    # Check if all questions have perfect precision and recall
    all_perfect = all(
        r.precision == 1.0 and r.recall == 1.0 for r in question_results
    )
    status = "all_clear" if all_perfect else "has_failures"

    return EvalReport(
        precision_at_5=mean_precision,
        recall_at_5=mean_recall,
        mrr=mrr,
        ndcg_at_5=mean_ndcg,
        total_questions=n,
        questions_with_hits=hits,
        per_question=question_results,
        status=status,
    )


def write_report(report: EvalReport, report_path: Path | None = None) -> None:
    """Write evaluation report to JSON file."""
    if report_path is None:
        report_path = Path(REPORT_PATH)

    report_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "precision_at_5": report.precision_at_5,
        "recall_at_5": report.recall_at_5,
        "mrr": report.mrr,
        "ndcg_at_5": report.ndcg_at_5,
        "total_questions": report.total_questions,
        "questions_with_hits": report.questions_with_hits,
        "per_question": [
            {
                "id": r.id,
                "precision": r.precision,
                "recall": r.recall,
                "rr": r.rr,
                "retrieved": r.retrieved,
                "gold": r.gold,
            }
            for r in report.per_question
        ],
        "status": report.status,
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Report written to {report_path}")
