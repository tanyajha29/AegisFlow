"""
Semantic retrieval against pgvector-stored knowledge chunks.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

EMB_DIM = 384
_model = None  # lazy-loaded to avoid crashing on import if package missing


def _get_model():
    """Lazy-load SentenceTransformer so import errors don't break the whole app."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer loaded (all-MiniLM-L6-v2, dim=%d)", EMB_DIM)
        except Exception as exc:
            logger.error(
                "Failed to load SentenceTransformer: %s. "
                "Vector retrieval will be unavailable. Install sentence-transformers.",
                exc,
            )
    return _model


def _vector_literal(values: List[float]) -> str:
    """Produce a pgvector-compatible literal string: [0.1,0.2,...]"""
    return "[" + ",".join(f"{v:.6f}" for v in values) + "]"


def _encode_query(query: str) -> Optional[List[float]]:
    """Encode a query string to a float vector. Returns None on failure."""
    model = _get_model()
    if model is None:
        return None
    try:
        vec = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
        return [float(v) for v in vec]
    except Exception as exc:
        logger.error("Embedding encode failed: %s", exc)
        return None


def search_chunks(
    db: Session,
    query: str,
    vulnerability_type: Optional[str] = None,
    language: Optional[str] = None,
    framework: Optional[str] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k KB chunks from pgvector using cosine similarity.
    Falls back to metadata-only keyword search if embedding is unavailable.
    Returns an empty list (never raises) so callers always get a safe result.
    """
    if not query:
        logger.warning("search_chunks called with empty query")
        return []

    query_vec = _encode_query(query)

    if query_vec is not None:
        results = _vector_search(db, query_vec, vulnerability_type, language, framework, top_k)
    else:
        logger.warning("Embedding unavailable; falling back to metadata keyword search")
        results = _keyword_search(db, query, vulnerability_type, language, framework, top_k)

    rag_debug = getattr(settings, "rag_debug", False)
    if rag_debug:
        logger.debug(
            "search_chunks: query=%r vuln_type=%r lang=%r fw=%r top_k=%d → %d results",
            query[:80], vulnerability_type, language, framework, top_k, len(results),
        )
        for i, r in enumerate(results[:3]):
            logger.debug("  [%d] source=%s title=%s sim=%.4f", i + 1, r.get("source"), r.get("title"), r.get("similarity", 0))
    else:
        logger.info(
            "RAG retrieval: %d chunks returned for query=%r (vuln_type=%r)",
            len(results), query[:60], vulnerability_type,
        )

    return results


def _vector_search(
    db: Session,
    query_vec: List[float],
    vulnerability_type: Optional[str],
    language: Optional[str],
    framework: Optional[str],
    top_k: int,
) -> List[Dict[str, Any]]:
    """pgvector cosine similarity search with optional metadata filters."""
    vec_literal = _vector_literal(query_vec)

    # Build WHERE clause — embed the vector literal directly to avoid
    # SQLAlchemy/psycopg2 issues with casting named params to vector type.
    filter_parts: List[str] = []
    params: Dict[str, Any] = {"top_k": top_k}

    if vulnerability_type:
        filter_parts.append("metadata->>'vulnerability_type' ILIKE :vuln_type")
        params["vuln_type"] = vulnerability_type
    if language:
        filter_parts.append("metadata->>'language' ILIKE :language")
        params["language"] = language
    if framework:
        filter_parts.append("metadata->>'framework' ILIKE :framework")
        params["framework"] = framework

    where_clause = ("WHERE " + " AND ".join(filter_parts)) if filter_parts else ""

    sql = f"""
        SELECT chunk_id, source, title, content, metadata,
               1 - (embedding <=> '{vec_literal}'::vector) AS similarity
        FROM kb_chunks
        {where_clause}
        ORDER BY embedding <=> '{vec_literal}'::vector
        LIMIT :top_k
    """

    try:
        rows = db.execute(text(sql), params).mappings().all()
    except Exception as exc:
        logger.error("pgvector query failed: %s", exc)
        # Retry without metadata filters in case the table/column is missing
        if filter_parts:
            logger.warning("Retrying vector search without metadata filters")
            return _vector_search(db, query_vec, None, None, None, top_k)
        return []

    return _rows_to_dicts(rows)


def _keyword_search(
    db: Session,
    query: str,
    vulnerability_type: Optional[str],
    language: Optional[str],
    framework: Optional[str],
    top_k: int,
) -> List[Dict[str, Any]]:
    """Fallback full-text ILIKE search when embeddings are unavailable."""
    params: Dict[str, Any] = {"query": f"%{query}%", "top_k": top_k}
    filter_parts = ["(content ILIKE :query OR title ILIKE :query)"]

    if vulnerability_type:
        filter_parts.append("metadata->>'vulnerability_type' ILIKE :vuln_type")
        params["vuln_type"] = vulnerability_type
    if language:
        filter_parts.append("metadata->>'language' ILIKE :language")
        params["language"] = language

    where_clause = "WHERE " + " AND ".join(filter_parts)
    sql = f"""
        SELECT chunk_id, source, title, content, metadata, 0.5 AS similarity
        FROM kb_chunks
        {where_clause}
        LIMIT :top_k
    """
    try:
        rows = db.execute(text(sql), params).mappings().all()
        return _rows_to_dicts(rows)
    except Exception as exc:
        logger.error("Keyword fallback search failed: %s", exc)
        return []


def _rows_to_dicts(rows) -> List[Dict[str, Any]]:
    payload = []
    for row in rows:
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
