# Requires: pip install sentence-transformers
"""
Preview embeddings:
- print total records
- show first 2 with chunk_id, source, embedding dim, and first 10 values
"""

from __future__ import annotations

import json
from pathlib import Path

EMB_PATH = Path(__file__).parent / "knowledge_base" / "embeddings" / "all_embeddings.json"


def main():
    if not EMB_PATH.exists():
        print("Embeddings file not found:", EMB_PATH)
        return
    try:
        data = json.loads(EMB_PATH.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:
        print("Failed to load embeddings:", exc)
        return

    print(f"Total embedded records: {len(data)}")
    for i, rec in enumerate(data[:2]):
        emb = rec.get("embedding") or []
        dim = len(emb)
        preview = emb[:10]
        print(f"[{i}] chunk_id={rec.get('chunk_id')} source={rec.get('source')} dim={dim} first10={preview}")


if __name__ == "__main__":
    main()
