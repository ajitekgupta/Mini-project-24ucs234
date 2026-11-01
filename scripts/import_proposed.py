"""Import the separately authored 33–42 package without claiming it is original data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", type=Path)
    args = parser.parse_args()
    items = json.loads(args.json_file.read_text(encoding="utf-8"))
    if [item["id"] for item in items] != list(range(33, 43)):
        raise SystemExit("Expected proposed cases 33–42")
    out = ROOT / "data" / "proposed_scenarios"
    out.mkdir(exist_ok=True)
    for item in items:
        record = {
            "internal_id": f"proposed-{item['id']}",
            "number": item["id"],
            "origin": "proposed_addition",
            "title": item["title"],
            "situation": item["title"],
            "entities": " ".join(item["entities"]),
            "communication_type": item["communication"],
            "description": item["description"],
            "dialogue_prompts": " ".join(f"{a} {b}" for a, b in item["dialogues"]),
            "source_proposed_solutions": " ".join(item["solutions"]),
            "peas": " ".join(item["peas"]),
            "cascading_problems": " ".join(item["cascading"]),
            "candidate_dialogue_type": None,
            "label_reason": None,
            "diagram_mapping": {"status": "authored_match", "image": f"scenario{item['id']}.png"},
            "review_status": "proposed_addition_needs_faculty_review",
            "source_location": {"file": args.json_file.name, "record": item["id"]},
        }
        (out / f"{record['internal_id']}.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    print(f"Imported {len(items)} proposed additions to {out}")


if __name__ == "__main__":
    main()
