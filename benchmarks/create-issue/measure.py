"""Validate dry-run results and report text metrics; semantics require rubric.md."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def tokens(text):
    return re.findall(r"\w+", text.lower())


def fivegrams(text):
    words = tokens(text)
    return {tuple(words[i:i + 5]) for i in range(len(words) - 4)}


def measure(path):
    expected = {case["id"] for case in json.loads((ROOT / "cases.json").read_text())["cases"]}
    rows = json.loads(path.read_text())
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise ValueError(f"{path}: expected {len(expected)} results")
    if {row["id"] for row in rows} != expected:
        raise ValueError(f"{path}: case IDs do not match")
    results = []
    for row in rows:
        for name in ("action", "notes"):
            if not isinstance(row[name], str):
                raise ValueError(f"{row['id']}: {name} must be a string")
        for name in ("body", "brief", "title"):
            if row[name] is not None and not isinstance(row[name], str):
                raise ValueError(f"{row['id']}: {name} must be a string or null")
        for name in ("labels", "questions", "operations"):
            if not isinstance(row[name], list):
                raise ValueError(f"{row['id']}: {name} must be a list")
        body, brief = row["body"] or "", row["brief"] or ""
        a, b = fivegrams(body), fivegrams(brief)
        results.append({
            "id": row["id"],
            "body_words": len(body.split()),
            "brief_words": len(brief.split()),
            "total_words": len(body.split()) + len(brief.split()),
            "shared_fivegrams": len(a & b),
            "shorter_text_fivegrams": min(len(a), len(b)),
            "operations": row["operations"],
        })
    return {"source": str(path), "cases": results}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 measure.py outputs/current.json [outputs/candidate.json]")
    print(json.dumps([measure(Path(p)) for p in sys.argv[1:]], ensure_ascii=False, indent=2))
