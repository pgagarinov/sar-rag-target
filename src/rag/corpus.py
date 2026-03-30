"""QASPER corpus loader via HuggingFace datasets library."""

from dataclasses import dataclass


@dataclass
class Paper:
    id: str
    title: str
    abstract: str
    sections: list[tuple[str, list[str]]]  # (section_name, [paragraphs])


def load_papers() -> list[Paper]:
    """Load all QASPER papers from HuggingFace (cached automatically)."""
    from datasets import load_dataset
    ds = load_dataset("allenai/qasper", split="train+validation")
    papers = []
    for row in ds:
        sections = list(zip(
            row["full_text"]["section_name"],
            row["full_text"]["paragraphs"],
        ))
        papers.append(Paper(
            id=row["id"],
            title=row["title"],
            abstract=row["abstract"],
            sections=sections,
        ))
    return papers


def paper_to_text(paper: Paper) -> str:
    """Convert a paper to markdown-like text with section headings."""
    parts = [f"# {paper.title}\n\n{paper.abstract}"]
    for section_name, paragraphs in paper.sections:
        if section_name:
            parts.append(f"\n## {section_name}\n")
        for para in paragraphs:
            if para.strip():
                parts.append(para.strip())
    return "\n\n".join(parts)
