"""Path configuration via environment variables.

Infrastructure file — never edited by the researcher.
All paths MUST be set explicitly via env vars. No defaults.
"""

import os

REPORT_PATH = os.environ["SAR_RAG_REPORT_PATH"]
INDEX_CACHE_DIR = os.environ["SAR_RAG_INDEX_CACHE_DIR"]
FORCE_REBUILD = os.environ.get("SAR_RAG_FORCE_REBUILD", "").strip() == "1"
