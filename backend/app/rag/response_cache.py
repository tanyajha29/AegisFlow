from __future__ import annotations

import json
import logging
import os
from collections import OrderedDict
from threading import Lock
from time import time
from typing import Any, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class _InMemoryTTLCache:
    def __init__(self, max_entries: int, ttl_seconds: int) -> None:
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._lock = Lock()
        self._store: OrderedDict[str, tuple[float, dict[str, Any]]] = OrderedDict()

    def get(self, key: str) -> Optional[dict[str, Any]]:
        now = time()
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at <= now:
                self._store.pop(key, None)
                return None
            self._store.move_to_end(key)
            return value

    def set(self, key: str, value: dict[str, Any]) -> None:
        expires_at = time() + self.ttl_seconds
        with self._lock:
            self._store[key] = (expires_at, value)
            self._store.move_to_end(key)
            while len(self._store) > self.max_entries:
                self._store.popitem(last=False)


class RagResponseCache:
    def __init__(self) -> None:
        self.ttl_seconds = max(1, settings.rag_response_cache_ttl_seconds)
        self.max_entries = max(16, settings.rag_response_cache_max_entries)
        self._memory = _InMemoryTTLCache(self.max_entries, self.ttl_seconds)
        self._redis = self._init_redis()

    def _init_redis(self):
        redis_url = settings.rag_cache_redis_url or os.getenv("REDIS_URL")
        if not redis_url:
            logger.info("[RAG cache] Using in-memory cache")
            return None

        try:
            import redis  # type: ignore

            client = redis.Redis.from_url(redis_url, decode_responses=True)
            client.ping()
            logger.info("[RAG cache] Using Redis cache")
            return client
        except Exception as exc:
            logger.warning("[RAG cache] Redis unavailable, falling back to in-memory cache: %s", exc)
            return None

    def get(self, key: str) -> Optional[dict[str, Any]]:
        if self._redis is not None:
            try:
                payload = self._redis.get(key)
                if payload:
                    value = json.loads(payload)
                    if isinstance(value, dict):
                        return value
            except Exception as exc:
                logger.warning("[RAG cache] Redis get failed, falling back to memory: %s", exc)
        return self._memory.get(key)

    def set(self, key: str, value: dict[str, Any]) -> None:
        if self._redis is not None:
            try:
                self._redis.setex(key, self.ttl_seconds, json.dumps(value))
                return
            except Exception as exc:
                logger.warning("[RAG cache] Redis set failed, falling back to memory: %s", exc)
        self._memory.set(key, value)


_cache = RagResponseCache()


def get_rag_response_cache() -> RagResponseCache:
    return _cache
