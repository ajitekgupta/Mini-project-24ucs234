from __future__ import annotations

import re


PRIVATE_REFERENCE = re.compile(
    r"\b(?:original-\d+|scenario\s*#?\s*\d+|scenario\d+\.(?:png|svg)|(?:source|case)\s+(?:id|number)\s*[:#]?\s*\d+)\b",
    re.IGNORECASE,
)


def has_private_reference(text: str) -> bool:
    return bool(PRIVATE_REFERENCE.search(text))


def validate_record(record: dict) -> list[str]:
    issues: list[str] = []
    for field in ("internal_id", "origin", "situation", "description", "source_location"):
        if not record.get(field):
            issues.append(f"Missing {field}")
    if record.get("origin") not in {"original_report", "proposed_addition"}:
        issues.append("Invalid origin")
    return issues
