# RAG Search System

A RAG (Retrieval-Augmented Generation) system for searching QASPER scientific papers. Uses USearch (HNSW, f16) for vector search with MLX embeddings on Apple Silicon.

## Overview

This system streams 1,169 QASPER papers from HuggingFace, chunks them, embeds with MLX, and indexes into a USearch vector index. An evaluation framework measures retrieval quality against 2,814 gold-standard questions with paragraph-level evidence labels.

## Components

- **Corpus**: 1,169 QASPER scientific NLP papers from HuggingFace `allenai/qasper` (streamed, not stored locally)
- **Pipeline**: Python modules for chunking, indexing, retrieval, reranking, and evaluation
- **Eval Set**: 2,814 questions with gold chunk IDs mapped from QASPER annotator evidence paragraphs
- **Agents**: Claude Code agents for retrieval, reranking, and chunking improvements

## Quick Start

```bash
# Install dependencies
pixi install -e dev

# Run the evaluation pipeline
pixi run -e dev eval

# Run tests
pixi run -e dev test
```

## The /run Skill

The `/run` skill is the ONLY entry point for evaluation:

1. Builds or loads a cached USearch index (two-pass early exit: cache HIT ~12s, cache MISS ~80s)
2. Runs all 2,814 queries against the index
3. Reports MRR (primary), Recall@5, Precision@5, NDCG@5

## Corpus

Papers are streamed from HuggingFace `allenai/qasper` (train + validation splits). No local `corpus/docs/` directory — the HF dataset is cached at `~/.cache/huggingface/`.

The `corpus/eval_set.json` file contains 2,814 evaluation questions with gold-standard chunk IDs and answers.

## Architecture

```
src/rag/
  config.py      — Constants (chunk size, top-k)
  paths.py       — Environment variable overrides (RAG_INDEX_CACHE_DIR, RAG_REPORT_PATH)
  corpus.py      — QASPER dataset streaming from HuggingFace
  chunker.py     — Fixed-size character chunking with deterministic IDs
  embeddings.py  — MLX embedding function (Apple Silicon GPU, sentence-transformers fallback)
  indexer.py     — USearch HNSW index build (streaming, f16)
  cache.py       — Index caching with two-pass early exit (output-based invalidation)
  retriever.py   — Vector similarity search
  reranker.py    — Result reranking (passthrough baseline)
  evaluator.py   — MRR/Precision/Recall/NDCG evaluation
  pipeline.py    — End-to-end setup and eval orchestration
```
