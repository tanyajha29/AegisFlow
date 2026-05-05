"""
Semantic retrieval against pgvector-stored knowledge chunks.

Model loading strategy:
- SentenceTransformer is loaded once per worker process into a module singleton.
- The same model instance is reused by /rag/search, /rag/explain, and /rag/fix.
- HF_HOME and SENTENCE_TRANSFORMERS_HOME are pinned to a stable cache path.
- Timing is logged for model load, warmup, encode, and retrieval.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from threading import Lock, local
import time
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

EMB_DIM = 384
MODEL_NAME = "all-MiniLM-L6-v2"


def _prepare_cache_dirs() -> tuple[str, str]:
    preferred_hf = Path(settings.hf_home)
    preferred_st = Path(settings.sentence_transformers_home)
    fallback_hf = Path.home() / ".cache" / "huggingface"
    fallback_st = fallback_hf / "sentence_transformers"

    for hf_dir, st_dir in (
        (preferred_hf, preferred_st),
        (fallback_hf, fallback_st),
    ):
        try:
            hf_dir.mkdir(parents=True, exist_ok=True)
            st_dir.mkdir(parents=True, exist_ok=True)
            return str(hf_dir), str(st_dir)
        except PermissionError as exc:
            logger.warning(
                "Embedding cache path is not writable, falling back. hf_home=%s sentence_transformers_home=%s error=%s",
                hf_dir,
                st_dir,
                exc,
            )
        except OSError as exc:
            logger.warning(
                "Embedding cache path setup failed, falling back. hf_home=%s sentence_transformers_home=%s error=%s",
                hf_dir,
                st_dir,
                exc,
            )

    raise RuntimeError("Unable to initialize a writable embedding cache directory")


CACHE_DIR, SENTENCE_TRANSFORMERS_CACHE_DIR = _prepare_cache_dirs()
os.environ["HF_HOME"] = CACHE_DIR
os.environ["SENTENCE_TRANSFORMERS_HOME"] = SENTENCE_TRANSFORMERS_CACHE_DIR

# Singleton model instance. It is created exactly once for each app worker.
_model = None
_model_load_error: Optional[str] = None
_model_lock = Lock()
_request_metrics = local()


def _load_model_once() -> None:
    """
    Load SentenceTransformer into the module-level singleton.
    Called during module import, never inside request handlers.
    """
    global _model, _model_load_error
    if _model is not None:
        return

    with _model_lock:
        if _model is not None:
            return

        t0 = time.perf_counter()
        logger.info(
            "Loading embedding model... model=%s cache_dir=%s",
            MODEL_NAME,
            SENTENCE_TRANSFORMERS_CACHE_DIR,
        )
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            _model = SentenceTransformer(
                MODEL_NAME,
                cache_folder=SENTENCE_TRANSFORMERS_CACHE_DIR,
            )
            logger.info(
                "Embedding model loaded. model=%s dim=%d elapsed=%.2fs",
                MODEL_NAME,
                EMB_DIM,
                time.perf_counter() - t0,
            )
        except Exception as exc:
            _model_load_error = str(exc)
            logger.error(
                "SentenceTransformer load failed (vector retrieval unavailable): %s",
                exc,
            )


_load_model_once()


def _get_model():
    """Return the cached model instance. Never re-loads."""
    if _model is None and _model_load_error:
        logger.warning("SentenceTransformer unavailable: %s", _model_load_error)
    return _model


def warmup_embeddings() -> bool:
    """Ensure the model is fully initialized before the first live request."""
    model = _get_model()
    if model is None:
        return False

    t0 = time.perf_counter()
    try:
        model.encode(["warmup"], convert_to_numpy=True, normalize_embeddings=True)
        logger.info("Embedding warmup complete. elapsed=%.3fs", time.perf_counter() - t0)
        return True
    except Exception as exc:
        logger.warning("Embedding warmup failed (non-fatal): %s", exc)
        return False


def _vector_literal(values: List[float]) -> str:
    """Produce a pgvector-compatible literal string: [0.1,0.2,...]"""
    return "[" + ",".join(f"{v:.6f}" for v in values) + "]"


def _encode_query(query: str) -> Optional[List[float]]:
    """Encode a query string to a float vector. Returns None on failure."""
    model = _get_model()
    if model is None:
        return None

    t0 = time.perf_counter()
    try:
        vec = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
        elapsed = time.perf_counter() - t0
        _request_metrics.encoding_time = elapsed
        logger.info("encoding_time=%.3fs query_len=%d", elapsed, len(query))
        return [float(v) for v in vec]
    except Exception as exc:
        _request_metrics.encoding_time = time.perf_counter() - t0
        logger.error("Embedding encode failed (%.3fs): %s", time.perf_counter() - t0, exc)
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
    t0 = time.perf_counter()
    _request_metrics.encoding_time = 0.0
    _request_metrics.retrieval_time = 0.0
    if not query:
        logger.warning("search_chunks called with empty query")
        return []

    query_vec = _encode_query(query)

    if query_vec is not None:
        results = _vector_search(db, query_vec, vulnerability_type, language, framework, top_k)
    else:
        logger.warning("Embedding unavailable; falling back to metadata keyword search")
        results = _keyword_search(db, query, vulnerability_type, language, framework, top_k)

    _request_metrics.retrieval_time = time.perf_counter() - t0
    rag_debug = getattr(settings, "rag_debug", False)
    if rag_debug:
        logger.debug(
            "search_chunks: query=%r vuln_type=%r lang=%r fw=%r top_k=%d -> %d results",
            query[:80], vulnerability_type, language, framework, top_k, len(results),
        )
        for i, r in enumerate(results[:3]):
            logger.debug(
                "  [%d] source=%s title=%s sim=%.4f",
                i + 1,
                r.get("source"),
                r.get("title"),
                r.get("similarity", 0),
            )
    else:
        logger.info(
            "retrieval_time=%.3fs chunks=%d query=%r vuln_type=%r",
            _request_metrics.retrieval_time, len(results), query[:60], vulnerability_type,
        )

    return results


def get_last_retrieval_timings() -> tuple[float, float]:
    return (
        float(getattr(_request_metrics, "encoding_time", 0.0)),
        float(getattr(_request_metrics, "retrieval_time", 0.0)),
    )


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

    # Build WHERE clause and embed the vector literal directly to avoid
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
