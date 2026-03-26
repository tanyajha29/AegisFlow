# Requires: pip install sentence-transformers
"""
Generate embeddings for chunked knowledge base and save combined output.

Inputs:
  knowledge_base/chunks/owasp_chunks.json
  knowledge_base/chunks/cwe_chunks.json
  knowledge_base/chunks/nvd_chunks.json

Outputs:
  knowledge_base/embeddings/all_embeddings.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).parent
CHUNK_DIR = BASE_DIR / "knowledge_base" / "chunks"
EMB_DIR = BASE_DIR / "knowledge_base" / "embeddings"
MODEL_NAME = "all-MiniLM-L6-v2"


def ensure_dirs() -> None:
    EMB_DIR.mkdir(parents=True, exist_ok=True)


def load_chunks() -> List[Dict[str, Any]]:
    combined: List[Dict[str, Any]] = []
    for name in ["owasp_chunks.json", "cwe_chunks.json", "nvd_chunks.json"]:
        path = CHUNK_DIR / name
        if not path.exists():
            print(f"  ! Missing chunk file: {path}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            if isinstance(data, list):
                combined.extend(data)
            else:
                print(f"  ! {name} is not a list; skipping.")
        except Exception as exc:  # pragma: no cover
            print(f"  ! Failed to load {name}: {exc}")
    print(f"Total chunks loaded: {len(combined)}")
    return combined


def embed_chunks(chunks: List[Dict[str, Any]], batch_size: int = 64) -> List[Dict[str, Any]]:
    if not chunks:
        return []
    model = SentenceTransformer(MODEL_NAME)
    contents = [c.get("content", "") for c in chunks]
    embeddings: List[List[float]] = []

    print(f"Generating embeddings with {MODEL_NAME} ...")
    for start in range(0, len(contents), batch_size):
        end = min(start + batch_size, len(contents))
        batch = contents[start:end]
        embs = model.encode(batch, show_progress_bar=False, convert_to_numpy=False, normalize_embeddings=False)
        embeddings.extend([list(map(float, e)) for e in embs])
        print(f"  processed {end}/{len(contents)}")

    embedded_records: List[Dict[str, Any]] = []
    for idx, chunk in enumerate(chunks):
        try:
            embedded_records.append(
                {
                    "chunk_id": chunk.get("chunk_id"),
                    "source": chunk.get("source"),
                    "title": chunk.get("title"),
                    "content": chunk.get("content"),
                    "metadata": chunk.get("metadata", {}),
                    "embedding": embeddings[idx],
                }
            )
        except Exception as exc:  # pragma: no cover
            print(f"  ! Failed to attach embedding for chunk {chunk.get('chunk_id')}: {exc}")
    return embedded_records


def main() -> None:
    ensure_dirs()
    chunks = load_chunks()
    embedded = embed_chunks(chunks)
    out_path = EMB_DIR / "all_embeddings.json"
    out_path.write_text(json.dumps(embedded, ensure_ascii=False), encoding="utf-8")
    print(f"Embedded records: {len(embedded)} -> {out_path}")


if __name__ == "__main__":
    main()
