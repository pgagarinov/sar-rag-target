"""Path configuration via environment variables.

Infrastructure file — never edited by the researcher.
All paths MUST be set explicitly via env vars. No defaults.
"""

import os


def _require_env(name: str) -> str:
    """Read a required env var. Fail loudly if missing."""
    val = os.environ.get(name, "")
    if not val:
        raise RuntimeError(f"{name} env var is not set. Set it in .env or pass via supervisor.")
    return val


REPORT_PATH = _require_env("SAR_RAG_REPORT_PATH")
INDEX_CACHE_DIR = _require_env("SAR_RAG_INDEX_CACHE_DIR")
FORCE_REBUILD = os.environ.get("SAR_RAG_FORCE_REBUILD", "").strip() == "1"
