# RAG Search System

A RAG (Retrieval-Augmented Generation) agentic system for searching FluxAPI documentation. Uses ChromaDB for vector search with a Python evaluation pipeline.

## Overview

This system indexes FluxAPI documentation into chunks, stores them in a ChromaDB vector database, and retrieves relevant chunks for user queries. An evaluation framework measures retrieval quality against a gold-standard eval set.

## Components

- **Corpus**: 10 FluxAPI documentation files covering auth, API design, configuration, data, deployment, and troubleshooting
- **Pipeline**: Python modules for chunking, indexing, retrieval, reranking, and evaluation
- **Eval Set**: 20 graded questions testing factual, how-to, comparison, and troubleshooting retrieval
- **Agents**: Claude Code agents for retrieval, reranking, and chunking improvements

## Quick Start

```bash
# Install dependencies
pixi install

# Run the evaluation pipeline
pixi run eval

# Run tests
pixi run test
```

## The /search Skill

The `/search` skill orchestrates retrieval agents to answer user queries against the FluxAPI corpus:

1. **Retriever agent** runs vector similarity search via ChromaDB
2. **Reranker agent** (optional) improves result ordering
3. **Chunker agent** handles re-indexing when corpus or chunking strategy changes

## Corpus

The `corpus/docs/` directory contains 10 markdown files documenting the fictional FluxAPI cloud platform. Topics include authentication, API design, configuration management, data services, deployment, and troubleshooting.

The `corpus/eval_set.json` file contains 20 evaluation questions with gold-standard chunk IDs and answers, spanning easy factual lookups to hard multi-hop queries.

## Architecture

```
src/rag/
  config.py      — Constants (chunk size, paths, collection name)
  chunker.py     — Fixed-size character chunking with deterministic IDs
  indexer.py     — ChromaDB index build/load
  retriever.py   — Vector similarity search
  reranker.py    — Result reranking (passthrough baseline)
  evaluator.py   — Precision/recall/MRR/NDCG evaluation
  pipeline.py    — End-to-end setup and eval orchestration
```
