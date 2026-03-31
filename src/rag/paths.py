"""Path configuration with environment variable overrides.

Infrastructure file — never edited by the researcher.
"""

import os

REPORT_PATH = os.environ.get("SAR_RAG_REPORT_PATH", "/tmp/rag-eval-report.json")
INDEX_CACHE_DIR = os.environ.get("SAR_RAG_INDEX_CACHE_DIR", "/tmp/rag-index-cache")
FORCE_REBUILD = os.environ.get("SAR_RAG_FORCE_REBUILD", "").strip() == "1"
