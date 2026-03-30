#!/usr/bin/env python3
"""Generate eval_set.json from QASPER dataset.

Reads QASPER papers from HuggingFace, chunks them, maps evidence paragraphs
to chunk IDs, and writes corpus/eval_set.json.
"""
import json
import sys
from pathlib import Path

# Add src to path so we can import rag modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag.corpus import load_papers, paper_to_text
from rag.chunker import chunk_text


def find_chunk_for_evidence(evidence_text: str, chunks: list) -> str | None:
    """Find which chunk contains the evidence paragraph."""
    evidence_text = evidence_text.strip()
    if not evidence_text:
        return None
    for chunk in chunks:
        if evidence_text in chunk.text:
            return chunk.id
    # Fuzzy: try first 100 chars
    prefix = evidence_text[:100]
    for chunk in chunks:
        if prefix in chunk.text:
            return chunk.id
    return None


def classify_difficulty(answers: list[dict]) -> str:
    """Classify question difficulty from answer types."""
    for ans in answers:
        if ans.get("unanswerable"):
            return "hard"
    has_extractive = any(ans.get("extractive_spans") for ans in answers)
    if has_extractive:
        return "easy"
    return "medium"


def classify_type(question: str) -> str:
    """Classify question type from text."""
    q = question.lower()
    if q.startswith("how") or "method" in q or "approach" in q:
        return "how-to"
    if "compar" in q or "differ" in q or "versus" in q or " vs " in q:
        return "comparison"
    if "why" in q or "reason" in q or "cause" in q:
        return "reasoning"
    return "factual"


def main():
    print("Loading QASPER papers...")
    papers = load_papers()
    print(f"  {len(papers)} papers loaded")

    eval_questions = []
    skipped_unanswerable = 0
    skipped_no_evidence = 0

    # Load raw dataset with qas field
    from datasets import load_dataset
    ds = load_dataset("allenai/qasper", split="train+validation")

    for row in ds:
        paper_id = row["id"]
        text_parts = [f"# {row['title']}\n\n{row['abstract']}"]
        for section_name, paragraphs in zip(
            row["full_text"]["section_name"],
            row["full_text"]["paragraphs"],
        ):
            if section_name:
                text_parts.append(f"\n## {section_name}\n")
            for para in paragraphs:
                if para.strip():
                    text_parts.append(para.strip())
        text = "\n\n".join(text_parts)
        chunks = chunk_text(text, paper_id)

        for q_idx, question in enumerate(row["qas"]["question"]):
            q_id = row["qas"]["question_id"][q_idx]
            # answers[q_idx] is a dict with 'answer' (list of annotator dicts)
            answers_entry = row["qas"]["answers"][q_idx]
            answers_list = answers_entry["answer"]

            # Collect gold chunk IDs from all annotator answers
            gold_chunk_ids = set()
            gold_answer = ""
            is_unanswerable = True

            for ans in answers_list:
                if ans.get("unanswerable"):
                    continue
                is_unanswerable = False

                if not gold_answer and ans.get("free_form_answer"):
                    gold_answer = ans["free_form_answer"]

                for evidence_para in (ans.get("evidence") or []):
                    chunk_id = find_chunk_for_evidence(evidence_para, chunks)
                    if chunk_id:
                        gold_chunk_ids.add(chunk_id)

            if is_unanswerable:
                skipped_unanswerable += 1
                continue

            if not gold_chunk_ids:
                skipped_no_evidence += 1
                continue

            eval_questions.append({
                "id": q_id,
                "question": question,
                "gold_chunk_ids": sorted(gold_chunk_ids),
                "gold_answer": gold_answer or "",
                "difficulty": classify_difficulty(answers_list),
                "type": classify_type(question),
            })

    print(f"  {len(eval_questions)} questions with gold chunk IDs")
    print(f"  {skipped_unanswerable} skipped (unanswerable)")
    print(f"  {skipped_no_evidence} skipped (no evidence mapped to chunks)")

    output_path = Path(__file__).parent.parent / "corpus" / "eval_set.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(eval_questions, f, indent=2, ensure_ascii=False)
    print(f"  Written to {output_path}")


if __name__ == "__main__":
    main()
