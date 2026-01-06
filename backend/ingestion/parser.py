"""BRD/API ingestion utilities.

Parses BRD (DOCX/PDF/TXT) and API Excel sheets into structured records
that conform to requirement_schema.json and api_schema.json.

Dependencies: pandas, python-docx, pdfplumber (optional). Handle missing
libs gracefully; callers should install extras before use.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import List, Dict, Any

try:
    import pandas as pd
except ImportError:  # pragma: no cover
    pd = None  # type: ignore

try:
    import docx  # python-docx
except ImportError:  # pragma: no cover
    docx = None  # type: ignore

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None  # type: ignore


def parse_brd_document(
    path: str,
    *,
    default_priority: str = "P2",
    feature_area: str = "unspecified",
) -> List[Dict[str, Any]]:
    """Parse a BRD/CR DOCX/PDF/TXT into requirement records.

    Heuristics:
    - Split by headings (Markdown-style #, or numbered 1./1)) to form sections.
    - Derive acceptance criteria and risks from lines prefixed with "AC:"/"Risk:".
    - Truncate description to 4k chars to avoid oversized payloads.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(path)

    text = _extract_text(file_path)
    sections = _split_sections_by_heading(text)
    if not sections:
        sections = [(file_path.stem, text)]

    records: List[Dict[str, Any]] = []
    for idx, (title, body) in enumerate(sections, start=1):
        acc, risks = _extract_marked_lines(body)
        req_id = file_path.stem if len(sections) == 1 else f"{file_path.stem}-{idx}"
        records.append(
            {
                "id": req_id,
                "title": title or f"Requirement {req_id}",
                "description": body.strip()[:4000],
                "priority": _normalize_priority(default_priority),
                "feature_area": feature_area,
                "acceptance_criteria": acc,
                "risks": risks,
                "compliance_tags": [],
                "dependencies": [],
                "source": str(file_path),
                "raw_refs": [title] if title else [],
            }
        )
    return records


def parse_api_excel(
    path: str,
    sheet: str | int | None = None,
    column_map: Dict[str, str] | None = None,
) -> List[Dict[str, Any]]:
    """Parse an API Excel sheet into API contract records.

    - `column_map` can rename incoming columns to expected names.
    - JSON-like strings in request/response_schema columns are deserialized.
    - Comma-separated values for errors/tests are normalized to lists.
    Unknown columns are preserved in the record for traceability.
    """
    if pd is None:
        raise ImportError("pandas is required for Excel ingestion. Install pandas before use.")

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(path)

    df_obj = pd.read_excel(file_path, sheet_name=sheet if sheet is not None else 0)
    df = next(iter(df_obj.values())) if isinstance(df_obj, dict) else df_obj
    if column_map:
        df = df.rename(columns=column_map)

    records: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        rec: Dict[str, Any] = {k: _maybe_json(row.get(k)) for k in df.columns}

        rec["path"] = str(rec.get("path", "") or "").strip()
        rec["method"] = str(rec.get("method", "") or "").strip().upper()
        rec["service"] = str(rec.get("service", "") or "").strip()
        rec["version"] = str(rec.get("version", "") or "").strip()
        rec["auth"] = rec.get("auth", "") or ""
        rec["rate_limit"] = rec.get("rate_limit", "") or ""

        rec["request_schema"] = rec.get("request_schema", {}) or {}
        rec["response_schema"] = rec.get("response_schema", {}) or {}

        rec["errors"] = _to_list(rec.get("errors", []))
        rec["tests"] = _to_list(rec.get("tests", []))

        rec["source"] = str(file_path)
        rec.setdefault("raw_refs", [])
        records.append(rec)
    return records


def _maybe_json(val: Any) -> Any:
    if isinstance(val, str):
        s = val.strip()
        if s.startswith("{") or s.startswith("["):
            try:
                return json.loads(s)
            except Exception:
                return val
    return val


def _split_sections_by_heading(text: str) -> List[tuple[str, str]]:
    """Split text by simple heading patterns (#, ##, or numbered lists)."""
    lines = text.splitlines()
    sections: List[tuple[str, str]] = []
    current_title: str | None = None
    current_body: List[str] = []
    heading_re = re.compile(r"^\s*(#+|\d+[.)])\s+(.*)$")

    def push_section():
        if current_title is None and not current_body:
            return
        sections.append((current_title or "", "\n".join(current_body).strip()))

    for line in lines:
        match = heading_re.match(line)
        if match:
            push_section()
            current_title = match.group(2).strip()
            current_body = []
        else:
            current_body.append(line)
    push_section()
    return [(t, b) for t, b in sections if b.strip() or t]


def _extract_marked_lines(body: str) -> tuple[List[str], List[str]]:
    """Capture acceptance criteria and risks from lines prefixed with markers."""
    acc: List[str] = []
    risks: List[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("ac:"):
            acc.append(stripped[3:].strip())
        elif stripped.lower().startswith("risk:"):
            risks.append(stripped[5:].strip())
    return acc, risks


def _to_list(val: Any) -> List[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        parts = [p.strip() for p in val.split(",") if p.strip()]
        return parts
    return [val]


def _normalize_priority(priority: str) -> str:
    allowed = {"P0", "P1", "P2", "P3"}
    p = (priority or "P2").upper()
    return p if p in allowed else "P2"


def _extract_text(file_path: Path) -> str:
    if file_path.suffix.lower() == ".docx":
        if docx is None:
            raise ImportError("python-docx is required to parse DOCX files.")
        document = docx.Document(file_path)  # type: ignore
        return "\n".join(p.text for p in document.paragraphs)
    if file_path.suffix.lower() == ".pdf":
        if pdfplumber is None:
            raise ImportError("pdfplumber is required to parse PDF files.")
        with pdfplumber.open(file_path) as pdf:  # type: ignore
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages)
    # Fallback: plain text
    return file_path.read_text(encoding="utf-8")
