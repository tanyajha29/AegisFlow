"""
Preview chunked knowledge-base outputs.
Prints:
- total OWASP chunks + first 2
- total CWE chunks + first 2
- total NVD chunks + first 2
"""

from __future__ import annotations

import json
from pathlib import Path

CHUNK_DIR = Path(__file__).parent / "knowledge_base" / "chunks"


def load(path: Path):
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return []


def preview(name: str, data):
    print(f"{name} chunks: {len(data)}")
    for i, item in enumerate(data[:2]):
        print(f"  [{i}] {json.dumps(item, ensure_ascii=False)[:500]}")


def main():
    owasp = load(CHUNK_DIR / "owasp_chunks.json")
    cwe = load(CHUNK_DIR / "cwe_chunks.json")
    nvd = load(CHUNK_DIR / "nvd_chunks.json")

    preview("OWASP", owasp)
    preview("CWE", cwe)
    preview("NVD", nvd)


if __name__ == "__main__":
    main()
