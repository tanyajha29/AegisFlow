from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import ValidationError

from .schemas import KBEntry

logger = logging.getLogger(__name__)

DEFAULT_KB_PATH = Path(__file__).parent / "kb"


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_kb(kb_path: str | None = None) -> List[KBEntry]:
    """
    Load knowledge base entries from JSON files.
    Keeps the surface small and deterministic for Phase 1.
    """
    base_path = Path(kb_path or os.getenv("RAG_KB_PATH") or DEFAULT_KB_PATH)
    if not base_path.exists():
        logger.warning("RAG KB path does not exist: %s", base_path)
        return []

    entries: List[KBEntry] = []
    for file in base_path.glob("*.json"):
        try:
            data = _read_json(file)
            entry = KBEntry.model_validate(data)
            entries.append(entry)
        except (ValidationError, json.JSONDecodeError) as exc:
            logger.warning("Skipping invalid KB file %s: %s", file.name, exc)
    logger.info("Loaded %s KB entries from %s", len(entries), base_path)
    return entries
