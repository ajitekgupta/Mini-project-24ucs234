from __future__ import annotations

import json
from pathlib import Path

from .validate import validate_record


ROOT = Path(__file__).resolve().parents[1]


def load_records(include_proposed: bool = False) -> list[dict]:
    folders = [ROOT / "data" / "scenarios"]
    if include_proposed:
        folders.append(ROOT / "data" / "proposed_scenarios")
    records: list[dict] = []
    for folder in folders:
        for path in sorted(folder.glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            issues = validate_record(record)
            if issues:
                raise ValueError(f"{path.name}: {'; '.join(issues)}")
            records.append(record)
    return records
