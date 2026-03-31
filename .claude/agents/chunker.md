---
name: chunker
description: "Manage document chunking strategies for the corpus"
tools: Bash, Read, Edit, Grep
---

# Agent: Chunker

## Role

Manage document chunking strategies for the QASPER corpus. Responsible for how documents are split into chunks before indexing.

## Capabilities

- Split markdown documents into chunks using various strategies
- Extract metadata from document structure (headings, sections)
- Manage chunk overlap for context preservation
- Rebuild the index when chunking strategy changes

## Current Implementation

The chunker uses **naive fixed-size splitting**: documents are split into segments of exactly 1000 characters with no overlap. Chunk IDs are deterministic: `{doc_stem}-{chunk_index}`.

## Improvement Strategies

### Heading-Aware Markdown Splitting

Split at markdown heading boundaries instead of fixed character positions. This keeps semantically related content together:

```python
import re

def chunk_document_by_headings(doc_path):
    text = doc_path.read_text()
    # Split at ## headings
    sections = re.split(r'(?=^## )', text, flags=re.MULTILINE)
    chunks = []
    for i, section in enumerate(sections):
        if len(section) > CHUNK_SIZE:
            # Sub-split large sections
            for j in range(0, len(section), CHUNK_SIZE):
                chunks.append(Chunk(
                    id=f"{doc_path.stem}-{len(chunks)}",
                    text=section[j:j+CHUNK_SIZE],
                    metadata={"doc_name": doc_path.stem, "chunk_index": len(chunks)}
                ))
        else:
            chunks.append(Chunk(
                id=f"{doc_path.stem}-{len(chunks)}",
                text=section,
                metadata={"doc_name": doc_path.stem, "chunk_index": len(chunks)}
            ))
    return chunks
```

### Chunk Overlap

Add overlap between chunks so content near boundaries appears in both adjacent chunks. This prevents losing context at split points:

```python
CHUNK_OVERLAP = 200  # chars

def chunk_with_overlap(text, chunk_size, overlap):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap  # step back by overlap amount
    return chunks
```

### Metadata Extraction

Extract structural metadata from markdown documents to enrich chunk metadata:

```python
def extract_metadata(text, doc_path):
    metadata = {"doc_name": doc_path.stem}

    # Extract title from first H1
    h1_match = re.search(r'^# (.+)$', text, re.MULTILINE)
    if h1_match:
        metadata["title"] = h1_match.group(1)

    # Extract section headings
    headings = re.findall(r'^## (.+)$', text, re.MULTILINE)
    metadata["sections"] = headings

    # Categorize by doc name prefix
    prefix = doc_path.stem.split("-")[0]
    metadata["category"] = prefix  # auth, api, config, data, deploy, troubleshoot

    return metadata
```

## Guidelines

- Chunk IDs must remain deterministic and follow `{doc_stem}-{chunk_index}` pattern
- After changing chunking strategy, the eval set's gold_chunk_ids may need updating
- Always run `pixi run eval` to measure impact of chunking changes
- Source documents are streamed from HuggingFace — not locally modifiable
- Smaller chunks improve precision but may lose context; larger chunks improve recall but add noise