"""Print reproducible coverage and provenance for the source review meeting."""

from __future__ import annotations

import collections
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data import load_records  # noqa: E402


def main() -> None:
    records = load_records()
    print(f"Original written scenarios: {len(records)}")
    for field in ("situation", "entities", "communication_type", "description",
                  "dialogue_prompts", "source_proposed_solutions", "peas", "cascading_problems"):
        missing = [r["number"] for r in records if not r.get(field)]
        print(f"{field}: {len(records) - len(missing)}/32 present; missing in {missing or 'none'}")
    statuses = collections.Counter(r["review_status"] for r in records)
    print("Review status:", dict(statuses))
    print("Diagram mappings verified:", sum(r["diagram_mapping"]["status"] == "verified" for r in records))
    print("Proposed additions (separate):", len(load_records(include_proposed=True)) - len(records))


if __name__ == "__main__":
    main()
