"""
Utility script to clean raw RAG knowledge-base sources and write cleaned copies
into processed/ subfolders (owasp, cwe, nvd).

Sources (relative to this file):
  knowledge_base/owasp/*.md
  knowledge_base/cwe/cwe.csv
  knowledge_base/nvd/recent.json

Outputs:
  knowledge_base/processed/owasp/*.md
  knowledge_base/processed/cwe/cwe_clean.csv
  knowledge_base/processed/nvd/recent_clean.json
"""

from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "knowledge_base"
PROCESSED_DIR = RAW_DIR / "processed"


# ---------- Helpers ----------
def ensure_dirs() -> None:
    (PROCESSED_DIR / "owasp").mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "cwe").mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "nvd").mkdir(parents=True, exist_ok=True)


def strip_markdown(text: str) -> str:
    """Remove links, code fences, markdown symbols; normalize whitespace."""
    if not text:
        return ""
    # remove code fences
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # remove inline backticks
    text = text.replace("`", "")
    # links [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    # strip markdown symbols # * _ > -
    text = re.sub(r"[#>*_]", " ", text)
    # collapse multiple spaces/newlines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


# ---------- OWASP ----------
def clean_owasp() -> None:
    owasp_raw = RAW_DIR / "owasp"
    out_dir = PROCESSED_DIR / "owasp"
    print("Cleaning OWASP markdown...")
    for md_path in sorted(owasp_raw.glob("*.md")):
        try:
            raw = md_path.read_text(encoding="utf-8", errors="ignore")
            cleaned = strip_markdown(raw)
            (out_dir / md_path.name).write_text(cleaned, encoding="utf-8")
            print(f"  ✓ {md_path.name}")
        except Exception as exc:  # pragma: no cover
            print(f"  ! {md_path.name}: {exc}")
    print("OWASP cleaning complete.")


# ---------- CWE ----------
def clean_cwe() -> None:
    csv_path = RAW_DIR / "cwe" / "cwe.csv"
    out_path = PROCESSED_DIR / "cwe" / "cwe_clean.csv"
    keep_cols = [
        "CWE-ID",
        "ID",
        "Name",
        "Description",
        "Summary",
        "Extended Description",
        "Related Weaknesses",
    ]
    if not csv_path.exists():
        print("CWE source not found, skipping.")
        return

    print("Cleaning CWE CSV...")
    rows: List[Dict[str, Any]] = []
    with csv_path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned_row = {}
            for col in keep_cols:
                if col in row:
                    cleaned_row[col] = clean_html(row[col])
            # drop empty rows
            if any(v for v in cleaned_row.values()):
                rows.append(cleaned_row)

    # prune empty columns
    non_empty_cols = [c for c in keep_cols if any(r.get(c) for r in rows)]

    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=non_empty_cols)
        writer.writeheader()
        for r in rows:
            writer.writerow({c: r.get(c, "") for c in non_empty_cols})

    print(f"CWE cleaned rows: {len(rows)} -> saved to {out_path.relative_to(BASE_DIR)}")


# ---------- NVD ----------
def extract_nvd_record(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Supports NVD CVE 2.0-style feed with top-level 'vulnerabilities' and per-item 'cve' node.
    """
    if not isinstance(item, dict):
        return {}
    cve = item.get("cve", {}) if isinstance(item.get("cve"), dict) else {}

    cve_id = cve.get("id")

    # description: pick English description if available
    description = ""
    for d in cve.get("descriptions", []) or []:
        if d.get("lang") == "en" and d.get("value"):
            description = d["value"]
            break
    if not description and cve.get("descriptions"):
        description = cve.get("descriptions")[0].get("value", "")

    published = cve.get("published")
    last_modified = cve.get("lastModified")

    # weaknesses: collect English descriptions
    weakness_tags: List[str] = []
    for w in cve.get("weaknesses", []) or []:
        for d in w.get("description", []) or []:
            if d.get("lang") == "en" and d.get("value"):
                weakness_tags.append(d["value"])

    # references: urls
    references = []
    for r in cve.get("references", []) or []:
        url = r.get("url")
        if url:
            references.append(url)

    # severity / cvss_score from metrics (prefer V3.1 -> V3.0 -> V2)
    cvss_score = None
    severity = None
    metrics = cve.get("metrics", {}) if isinstance(cve.get("metrics"), dict) else {}
    metric_keys = ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]
    for key in metric_keys:
        metric_list = metrics.get(key) or []
        if not isinstance(metric_list, list) or not metric_list:
            continue
        first_metric = metric_list[0]
        cvss_data = first_metric.get("cvssData", {})
        if cvss_data:
            cvss_score = cvss_data.get("baseScore")
            severity = cvss_data.get("baseSeverity") or first_metric.get("baseSeverity") or first_metric.get("severity")
            break

    return {
        "cve_id": cve_id,
        "description": description,
        "published": published,
        "lastModified": last_modified,
        "severity": severity,
        "cvss_score": cvss_score,
        "weaknesses": weakness_tags,
        "references": references,
    }


def clean_nvd() -> None:
    json_path = RAW_DIR / "nvd" / "recent.json"
    out_path = PROCESSED_DIR / "nvd" / "recent_clean.json"
    if not json_path.exists():
        print("NVD source not found, skipping.")
        return

    print("Cleaning NVD recent.json...")
    cleaned: List[Dict[str, Any]] = []
    try:
        data = json.loads(json_path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:  # pragma: no cover
        print(f"  ! Unable to parse NVD JSON: {exc}")
        return

    items = []
    # CVE 2.0 modern feed: data["vulnerabilities"]
    if isinstance(data, dict) and data.get("vulnerabilities"):
        items = data["vulnerabilities"]

    for item in items:
        try:
            cleaned.append(extract_nvd_record(item))
        except Exception as exc:  # pragma: no cover
            print(f"  ! Skipping one NVD item: {exc}")

    out_path.write_text(json.dumps(cleaned, indent=2), encoding="utf-8")
    print(f"NVD cleaned records: {len(cleaned)} -> saved to {out_path.relative_to(BASE_DIR)}")


# ---------- Main ----------
def main() -> None:
    ensure_dirs()
    clean_owasp()
    clean_cwe()
    clean_nvd()
    print("\nAll knowledge-base sources processed. Outputs in knowledge_base/processed/")


if __name__ == "__main__":
    main()
