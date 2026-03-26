"""
Quick preview utility for cleaned RAG knowledge base.
Prints:
- first 300 chars of one cleaned OWASP file
- first 3 rows of cleaned CWE CSV
- first 2 records of cleaned NVD JSON
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
PROC_DIR = BASE_DIR / "knowledge_base" / "processed"


def preview_owasp() -> str:
    owasp_dir = PROC_DIR / "owasp"
    files = sorted(owasp_dir.glob("*.md"))
    if not files:
        return "No cleaned OWASP files."
    text = files[0].read_text(encoding="utf-8", errors="ignore")
    return text[:300] + ("..." if len(text) > 300 else "")


def preview_cwe() -> str:
    cwe_path = PROC_DIR / "cwe" / "cwe_clean.csv"
    if not cwe_path.exists():
        return "No cleaned CWE CSV."
    with cwe_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = []
        for idx, row in enumerate(reader):
            rows.append(row)
            if idx >= 2:
                break
    return json.dumps(rows, indent=2, ensure_ascii=False)


def preview_nvd() -> str:
    nvd_path = PROC_DIR / "nvd" / "recent_clean.json"
    if not nvd_path.exists():
        return "No cleaned NVD JSON."
    data = json.loads(nvd_path.read_text(encoding="utf-8", errors="ignore"))
    return json.dumps(data[:2], indent=2, ensure_ascii=False) if isinstance(data, list) else "Invalid NVD format."


def main() -> None:
    print("OWASP sample (first 300 chars):")
    print(preview_owasp())
    print("\nCWE sample (first 3 rows):")
    print(preview_cwe())
    print("\nNVD sample (first 2 records):")
    print(preview_nvd())


if __name__ == "__main__":
    main()
