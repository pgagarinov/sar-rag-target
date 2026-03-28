"""Tests for the evaluator metrics."""

import json
import tempfile
from pathlib import Path

from rag.evaluator import (
    EvalQuestion,
    QuestionResult,
    _ndcg_at_k,
    _precision_at_k,
    _recall_at_k,
    _reciprocal_rank,
    write_report,
    EvalReport,
)


def test_precision_perfect():
    """Perfect retrieval should give precision 1.0."""
    retrieved = ["a", "b", "c"]
    gold = {"a", "b", "c"}
    assert _precision_at_k(retrieved, gold, k=3) == 1.0


def test_precision_partial():
    """One relevant out of five retrieved gives precision 0.2."""
    retrieved = ["a", "x", "y", "z", "w"]
    gold = {"a"}
    assert _precision_at_k(retrieved, gold, k=5) == 0.2


def test_precision_none():
    """No relevant results gives precision 0.0."""
    retrieved = ["x", "y", "z"]
    gold = {"a", "b"}
    assert _precision_at_k(retrieved, gold, k=3) == 0.0


def test_recall_perfect():
    """Finding all gold items gives recall 1.0."""
    retrieved = ["a", "b", "c", "x", "y"]
    gold = {"a", "b", "c"}
    assert _recall_at_k(retrieved, gold, k=5) == 1.0


def test_recall_partial():
    """Finding one of two gold items gives recall 0.5."""
    retrieved = ["a", "x", "y", "z", "w"]
    gold = {"a", "b"}
    assert _recall_at_k(retrieved, gold, k=5) == 0.5


def test_recall_none():
    """Finding no gold items gives recall 0.0."""
    retrieved = ["x", "y", "z"]
    gold = {"a", "b"}
    assert _recall_at_k(retrieved, gold, k=3) == 0.0


def test_reciprocal_rank_first():
    """Relevant result at position 1 gives RR 1.0."""
    retrieved = ["a", "x", "y"]
    gold = {"a"}
    assert _reciprocal_rank(retrieved, gold) == 1.0


def test_reciprocal_rank_third():
    """Relevant result at position 3 gives RR 1/3."""
    retrieved = ["x", "y", "a"]
    gold = {"a"}
    assert abs(_reciprocal_rank(retrieved, gold) - 1 / 3) < 1e-9


def test_reciprocal_rank_none():
    """No relevant result gives RR 0.0."""
    retrieved = ["x", "y", "z"]
    gold = {"a"}
    assert _reciprocal_rank(retrieved, gold) == 0.0


def test_ndcg_perfect():
    """All gold items ranked first gives NDCG 1.0."""
    retrieved = ["a", "b", "x", "y", "z"]
    gold = {"a", "b"}
    assert abs(_ndcg_at_k(retrieved, gold, k=5) - 1.0) < 1e-9


def test_ndcg_imperfect():
    """Gold items not at top positions gives NDCG < 1.0."""
    retrieved = ["x", "a", "y", "b", "z"]
    gold = {"a", "b"}
    ndcg = _ndcg_at_k(retrieved, gold, k=5)
    assert 0.0 < ndcg < 1.0


def test_ndcg_none():
    """No gold items gives NDCG 0.0."""
    retrieved = ["x", "y", "z"]
    gold = {"a"}
    assert _ndcg_at_k(retrieved, gold, k=3) == 0.0


def test_perfect_retrieval_report():
    """A perfect retrieval should produce precision=1.0 and recall=1.0."""
    results = [
        QuestionResult(
            id="q-001",
            precision=1.0,
            recall=1.0,
            rr=1.0,
            ndcg=1.0,
            retrieved=["a"],
            gold=["a"],
        )
    ]
    report = EvalReport(
        precision_at_5=1.0,
        recall_at_5=1.0,
        mrr=1.0,
        ndcg_at_5=1.0,
        total_questions=1,
        questions_with_hits=1,
        per_question=results,
        status="all_clear",
    )
    assert report.status == "all_clear"
    assert report.precision_at_5 == 1.0
    assert report.recall_at_5 == 1.0


def test_report_json_valid():
    """Report should be written as valid JSON."""
    results = [
        QuestionResult(
            id="q-001",
            precision=0.2,
            recall=1.0,
            rr=0.5,
            ndcg=0.6,
            retrieved=["a", "b", "c", "d", "e"],
            gold=["a"],
        ),
        QuestionResult(
            id="q-002",
            precision=0.0,
            recall=0.0,
            rr=0.0,
            ndcg=0.0,
            retrieved=["x", "y"],
            gold=["z"],
        ),
    ]
    report = EvalReport(
        precision_at_5=0.1,
        recall_at_5=0.5,
        mrr=0.25,
        ndcg_at_5=0.3,
        total_questions=2,
        questions_with_hits=1,
        per_question=results,
        status="has_failures",
    )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        tmp_path = Path(f.name)

    try:
        write_report(report, report_path=tmp_path)

        # Read it back and verify valid JSON
        with open(tmp_path) as f:
            data = json.load(f)

        assert data["precision_at_5"] == 0.1
        assert data["recall_at_5"] == 0.5
        assert data["mrr"] == 0.25
        assert data["status"] == "has_failures"
        assert len(data["per_question"]) == 2
        assert data["per_question"][0]["id"] == "q-001"
    finally:
        tmp_path.unlink()


def test_has_failures_status():
    """Report with imperfect results should have 'has_failures' status."""
    results = [
        QuestionResult(
            id="q-001",
            precision=0.2,
            recall=1.0,
            rr=1.0,
            ndcg=1.0,
            retrieved=["a", "b", "c", "d", "e"],
            gold=["a"],
        ),
    ]
    report = EvalReport(
        precision_at_5=0.2,
        recall_at_5=1.0,
        mrr=1.0,
        ndcg_at_5=1.0,
        total_questions=1,
        questions_with_hits=1,
        per_question=results,
        status="has_failures",
    )
    assert report.status == "has_failures"
