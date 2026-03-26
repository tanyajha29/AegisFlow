"""
Chunk cleaned knowledge-base data into JSON lists for downstream embeddings.

Inputs (cleaned):
  knowledge_base/processed/owasp/*.md
  knowledge_base/processed/cwe/cwe_clean.csv
  knowledge_base/processed/nvd/recent_clean.json

Outputs:
  knowledge_base/chunks/owasp_chunks.json
  knowledge_base/chunks/cwe_chunks.json
  knowledge_base/chunks/nvd_chunks.json
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).parent
PROC_DIR = BASE_DIR / "knowledge_base" / "processed"
CHUNK_DIR = BASE_DIR / "knowledge_base" / "chunks"


def ensure_dirs() -> None:
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 90) -> List[str]:
    if not text:
        return []
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end].strip())
        if end == n:
            break
        start = max(0, end - overlap)
    return [c for c in chunks if c]


def chunk_owasp() -> List[Dict[str, Any]]:
    owasp_dir = PROC_DIR / "owasp"
    if not owasp_dir.exists():
        print("OWASP processed dir missing; skipping OWASP chunks.")
        return []
    all_chunks: List[Dict[str, Any]] = []
    for md_path in sorted(owasp_dir.glob("*.md")):
        try:
            text = md_path.read_text(encoding="utf-8", errors="ignore")
            base_title = md_path.stem
            chunks = chunk_text(text, chunk_size=600, overlap=90)
            for idx, content in enumerate(chunks):
                all_chunks.append(
                    {
                        "chunk_id": f"owasp-{base_title}-{idx}",
                        "source": "owasp",
                        "title": base_title,
                        "content": content,
                        "metadata": {"category": md_path.name},
                    }
                )
        except Exception as exc:  # pragma: no cover
            print(f"  ! Skipping OWASP file {md_path.name}: {exc}")
    print(f"OWASP chunks: {len(all_chunks)}")
    return all_chunks


def chunk_cwe() -> List[Dict[str, Any]]:
    cwe_path = PROC_DIR / "cwe" / "cwe_clean.csv"
    if not cwe_path.exists():
        print("CWE cleaned CSV missing; skipping CWE chunks.")
        return []
    chunks: List[Dict[str, Any]] = []
    with cwe_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            cwe_id = row.get("CWE-ID") or row.get("ID") or f"row-{idx}"
            name = row.get("Name", "").strip()
            parts = [
                f"CWE-ID: {cwe_id}",
                f"Name: {name}",
                f"Description: {row.get('Description', '')}",
                f"Extended: {row.get('Extended Description', '')}",
                f"Related: {row.get('Related Weaknesses', '')}",
            ]
            content = "\n".join([p for p in parts if p.strip()])
            chunks.append(
                {
                    "chunk_id": f"cwe-{cwe_id}",
                    "source": "cwe",
                    "title": f"CWE-{cwe_id} {name}".strip(),
                    "content": content.strip(),
                    "metadata": {"cwe_id": cwe_id, "name": name},
                }
            )
    print(f"CWE chunks: {len(chunks)}")
    return chunks


def chunk_nvd() -> List[Dict[str, Any]]:
    nvd_path = PROC_DIR / "nvd" / "recent_clean.json"
    if not nvd_path.exists():
        print("NVD cleaned JSON missing; skipping NVD chunks.")
        return []
    chunks: List[Dict[str, Any]] = []
    try:
        data = json.loads(nvd_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:  # pragma: no cover
        print(f"  ! Unable to parse NVD cleaned JSON: {exc}")
        return []

    if not isinstance(data, list):
        print("NVD cleaned JSON is not a list; skipping.")
        return []

    for idx, rec in enumerate(data):
        try:
            cve_id = rec.get("cve_id") or f"cve-{idx}"
            parts = [
                f"CVE: {cve_id}",
                f"Severity: {rec.get('severity', '')}",
                f"CVSS: {rec.get('cvss_score', '')}",
                f"Weaknesses: {', '.join(rec.get('weaknesses', []) or [])}",
                f"References: {', '.join(rec.get('references', []) or [])}",
                f"Description: {rec.get('description', '')}",
            ]
            content = "\n".join([p for p in parts if p.strip()])
            chunks.append(
                {
                    "chunk_id": f"nvd-{cve_id}",
                    "source": "nvd",
                    "title": cve_id,
                    "content": content.strip(),
                    "metadata": {
                        "cve_id": cve_id,
                        "severity": rec.get("severity"),
                        "cvss_score": rec.get("cvss_score"),
                        "weaknesses": rec.get("weaknesses") or [],
                    },
                }
            )
        except Exception as exc:  # pragma: no cover
            print(f"  ! Skipping one NVD record: {exc}")
    print(f"NVD chunks: {len(chunks)}")
    return chunks


def write_json(path: Path, data: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    owasp_chunks = chunk_owasp()
    cwe_chunks = chunk_cwe()
    nvd_chunks = chunk_nvd()

    write_json(CHUNK_DIR / "owasp_chunks.json", owasp_chunks)
    write_json(CHUNK_DIR / "cwe_chunks.json", cwe_chunks)
    write_json(CHUNK_DIR / "nvd_chunks.json", nvd_chunks)

    print("\nChunking complete.")
    print(f"  OWASP chunks: {len(owasp_chunks)} -> {CHUNK_DIR / 'owasp_chunks.json'}")
    print(f"  CWE   chunks: {len(cwe_chunks)} -> {CHUNK_DIR / 'cwe_chunks.json'}")
    print(f"  NVD   chunks: {len(nvd_chunks)} -> {CHUNK_DIR / 'nvd_chunks.json'}")


if __name__ == "__main__":
    main()
