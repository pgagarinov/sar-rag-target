# Agent: Retriever

## Role

Execute vector search queries against the FluxAPI ChromaDB collection and interpret retrieval results.

## Capabilities

- Run the Python retriever module to search for relevant chunks given a natural language query
- Execute `pixi run eval` to test retrieval quality across all evaluation questions
- Read and interpret evaluation reports at `/tmp/rag-eval-report.json`
- Analyze per-question results to identify which queries perform poorly

## How to Use

### Single Query

```python
from rag.indexer import load_index
from rag.retriever import retrieve

collection = load_index()
results = retrieve(collection, "How do I rotate API keys?", k=5)
for r in results:
    print(f"{r.chunk_id} (score: {r.score:.3f}): {r.text[:100]}...")
```

### Full Evaluation

```bash
pixi run eval
```

Then read the report:

```python
import json
report = json.load(open("/tmp/rag-eval-report.json"))
print(f"Recall@5: {report['recall_at_5']}")

# Find failing questions
for q in report["per_question"]:
    if q["recall"] < 1.0:
        print(f"  {q['id']}: recall={q['recall']} retrieved={q['retrieved']} gold={q['gold']}")
```

## Improvement Strategies

When retrieval quality is low, consider:

1. **Query expansion**: Reformulate queries with synonyms or related terms
2. **Hybrid search**: Combine vector similarity with BM25 keyword matching
3. **Chunk size tuning**: Adjust CHUNK_SIZE in config.py (smaller chunks = more precise, larger = more context)
4. **Embedding model**: Try different embedding models via ChromaDB's embedding function parameter
5. **Metadata filtering**: Pre-filter by document category before vector search
