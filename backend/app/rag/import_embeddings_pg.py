"""
Import precomputed embeddings into PostgreSQL (pgvector).

Usage:
  python backend/app/rag/import_embeddings_pg.py

Environment (optional):
  RAG_EMBEDDINGS_FILE   path to all_embeddings.json (default: knowledge_base/embeddings/all_embeddings.json)
  DATABASE_URL          Postgres connection string (fallback to config settings)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import text

# Allow running as a script from repo root
import sys
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.config import get_settings  # type: ignore
from app.database import engine  # type: ignore

settings = get_settings()

BASE_DIR = Path(__file__).parent
DEFAULT_EMB_PATH = BASE_DIR / "knowledge_base" / "embeddings" / "all_embeddings.json"
EMB_DIM = 384


def load_embeddings(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Embeddings file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    if not isinstance(data, list):
        raise ValueError("Embeddings file must contain a list.")
    return data


def ensure_table(conn) -> None:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.execute(
        text(
            f"""
            CREATE TABLE IF NOT EXISTS kb_chunks (
              chunk_id TEXT PRIMARY KEY,
              source TEXT,
              title TEXT,
              content TEXT,
              metadata JSONB,
              embedding vector({EMB_DIM}),
              created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
    )


def vector_literal(values: List[float]) -> str:
    return "[" + ",".join(f"{v:.6f}" for v in values) + "]"


def import_embeddings(records: List[Dict[str, Any]]) -> None:
    if not records:
        print("No embeddings to import.")
        return
    with engine.begin() as conn:
        ensure_table(conn)
        inserted = 0
        batch_size = 500
        for start in range(0, len(records), batch_size):
            batch = records[start : start + batch_size]
            payload = [
                {
                    "chunk_id": r.get("chunk_id"),
                    "source": r.get("source"),
                    "title": r.get("title"),
                    "content": r.get("content"),
                    "metadata": json.dumps(r.get("metadata", {})),
                    "embedding": vector_literal(r.get("embedding") or []),
                }
                for r in batch
                if r.get("embedding")
            ]
            if not payload:
                continue
            conn.execute(
                text(
                    """
                    INSERT INTO kb_chunks (chunk_id, source, title, content, metadata, embedding)
                    VALUES (:chunk_id, :source, :title, :content, :metadata, (:embedding)::vector)
                    ON CONFLICT (chunk_id) DO UPDATE
                    SET source = EXCLUDED.source,
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding
                    """
                ),
                payload,
            )
            inserted += len(payload)
            print(f"  inserted {inserted}/{len(records)}")
        print(f"Import complete. Total rows upserted: {inserted}")


def main() -> None:
    emb_path = Path(os.getenv("RAG_EMBEDDINGS_FILE", DEFAULT_EMB_PATH))
    print(f"Loading embeddings from: {emb_path}")
    records = load_embeddings(emb_path)
    import_embeddings(records)


if __name__ == "__main__":
    main()
