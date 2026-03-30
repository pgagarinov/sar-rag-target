"""Path configuration with environment variable overrides.

Infrastructure file — never edited by the researcher.
"""

import os

CHROMA_PATH = os.environ.get("CHROMA_PERSIST_DIR", "/tmp/qasper-chroma")
REPORT_PATH = os.environ.get("RAG_REPORT_PATH", "/tmp/rag-eval-report.json")
