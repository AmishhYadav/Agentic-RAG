"""
Semantic Cache for Agentic RAG
===============================
Caches query-answer pairs indexed by their embedding vector.
On a new query, computes cosine similarity against cached queries.
If above threshold (default 0.96), returns the cached answer instantly
without invoking the full agent pipeline.
"""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

CACHE_DB_PATH = Path(__file__).parent.parent / "data" / "cache.db"
DEFAULT_THRESHOLD = 0.96


class SemanticCache:
    def __init__(
        self, db_path: Path = CACHE_DB_PATH, threshold: float = DEFAULT_THRESHOLD
    ):
        self.threshold = threshold
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS query_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                query_vector BLOB NOT NULL,
                answer TEXT NOT NULL,
                sources TEXT,
                verification TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()
        conn.close()

    def lookup(self, query_vector: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Check if a similar query exists in cache.
        Returns cached response if similarity > threshold, else None.
        """
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute(
            "SELECT query, query_vector, answer, sources, verification FROM query_cache"
        ).fetchall()
        conn.close()

        if not rows:
            return None

        best_score = -1.0
        best_row = None

        for row in rows:
            cached_vec = np.frombuffer(row[1], dtype=np.float32)
            score = self._cosine_similarity(query_vector, cached_vec)
            if score > best_score:
                best_score = score
                best_row = row

        if best_score >= self.threshold and best_row:
            return {
                "cached": True,
                "similarity": round(float(best_score), 4),
                "query": best_row[0],
                "answer": best_row[2],
                "sources": json.loads(best_row[3]) if best_row[3] else [],
                "verification": json.loads(best_row[4]) if best_row[4] else None,
            }

        return None

    def store(
        self,
        query: str,
        query_vector: np.ndarray,
        answer: str,
        sources: list = None,
        verification: dict = None,
    ):
        """Store a query-answer pair in the cache."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO query_cache (query, query_vector, answer, sources, verification) VALUES (?, ?, ?, ?, ?)",
            (
                query,
                query_vector.astype(np.float32).tobytes(),
                answer,
                json.dumps(sources or []),
                json.dumps(verification or {}),
            ),
        )
        conn.commit()
        conn.close()

    def clear(self):
        """Clear all cached entries."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("DELETE FROM query_cache")
        conn.commit()
        conn.close()

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        if a.shape != b.shape:
            return 0.0
        dot = np.dot(a, b)
        norm = np.linalg.norm(a) * np.linalg.norm(b)
        return float(dot / norm) if norm > 0 else 0.0
