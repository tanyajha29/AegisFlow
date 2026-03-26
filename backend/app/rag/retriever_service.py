"""
Semantic retrieval against pgvector-stored knowledge chunks.
"""

from __future__ import annotations

import json
from typing import List, Dict, Any, Optional

from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings

settings = get_settings()

MODEL_NAME = "all-MiniLM-L6-v2"
EMB_DIM = 384
model = SentenceTransformer(MODEL_NAME)


def _vector_literal(values: List[float]) -> str:
    return "[" + ",".join(f"{v:.6f}" for v in values) + "]"


def build_filters(vulnerability_type: Optional[str], language: Optional[str], framework: Optional[str]) -> str:
    filters = []
    if vulnerability_type:
        filters.append("metadata->>'vulnerability_type' = :vuln_type")
    if language:
        filters.append("metadata->>'language' = :language")
    if framework:
        filters.append("metadata->>'framework' = :framework")
    if filters:
        return "WHERE " + " AND ".join(filters)
    return ""


def search_chunks(
    db: Session,
    query: str,
    vulnerability_type: Optional[str] = None,
    language: Optional[str] = None,
    framework: Optional[str] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    if not query:
        return []
    query_vec = model.encode([query], convert_to_numpy=False, normalize_embeddings=False)[0]
    vec_literal = _vector_literal(list(map(float, query_vec)))

    filter_clause = build_filters(vulnerability_type, language, framework)
    sql = f"""
        SELECT chunk_id, source, title, content, metadata,
               1 - (embedding <=> (:vec)::vector) AS similarity
        FROM kb_chunks
        {filter_clause}
        ORDER BY embedding <=> (:vec)::vector
        LIMIT :top_k
    """
    params = {
        "vec": vec_literal,
        "top_k": top_k,
        "vuln_type": vulnerability_type,
        "language": language,
        "framework": framework,
    }
    results = db.execute(text(sql), params).mappings().all()
    payload = []
    for row in results:
        metadata = row["metadata"]
        if isinstance(metadata, str):
            try:
                metadata = json.loads(metadata)
            except Exception:
                metadata = {}
        payload.append(
            {
                "chunk_id": row["chunk_id"],
                "source": row["source"],
                "title": row["title"],
                "content": row["content"],
                "metadata": metadata or {},
                "similarity": float(row["similarity"]),
            }
        )
    return payload
