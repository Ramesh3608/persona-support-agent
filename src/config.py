# src/config.py
# ─────────────────────────────────────────────
# Central configuration and tunable thresholds
# ─────────────────────────────────────────────

import os
from dotenv import load_dotenv

load_dotenv()

# ── API ──────────────────────────────────────
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")

# ── Models ───────────────────────────────────
LLM_MODEL: str = "gemini-2.5-flash"
EMBEDDING_MODEL: str = "gemini-embedding-001"

# ── Vector DB ────────────────────────────────
CHROMA_DB_DIR: str = "./chroma_db"
COLLECTION_NAME: str = "support_kb"

# ── RAG Pipeline ─────────────────────────────
CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 50
TOP_K_RESULTS: int = 3

# ── Escalation Thresholds ────────────────────
CONFIDENCE_THRESHOLD: float = 0.45   # cosine similarity below this → escalate
MAX_FRUSTRATED_TURNS: int = 3         # consecutive frustrated turns → escalate

# ── Sensitive topic keywords (triggers escalation regardless of confidence) ──
SENSITIVE_KEYWORDS: list[str] = [
    "billing", "refund", "charge", "invoice", "legal", "lawsuit",
    "account deletion", "fraud", "dispute", "payment", "unauthorized charge",
    "cancel subscription", "lawyer", "sue",
]

# ── Data directory ───────────────────────────
DATA_DIR: str = "./data"
