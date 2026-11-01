"""Create a draft label review table from the report's dialogue sections.

Candidate labels below are annotations of the supplied report, not faculty
approval. Rerunning this script overwrites the CSV, so copy reviewed changes
before rerunning it.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LABELS = {
    1: ("negotiation", "inferred", "Settlement is discussed, with different vehicle interests."),
    2: ("deliberation", "inferred", "No conflict; common practical problem; not theoretical."),
    3: ("deliberation", "inferred", "No conflict; common practical problem; not theoretical."),
    4: ("inquiry", "ambiguous", "Report answers theoretical=yes, but describes updating obstruction status; check inquiry versus information seeking."),
    5: ("deliberation", "inferred", "No conflict; common practical problem; not theoretical."),
    6: ("information seeking", "inferred", "No common problem; signal lacks status information."),
    7: ("persuasion", "inferred", "Report gives conflict=yes and reason good=yes; check whether participants actually dispute a claim."),
    8: ("deliberation", "inferred", "No conflict; common practical problem; not theoretical."),
    9: ("information seeking", "inferred", "No common problem; priority vehicle seeks route information."),
    10: ("information seeking", "inferred", "No common problem; vehicle seeks parking information."),
    11: ("persuasion", "ambiguous", "Report says conflict=yes, but describes network flow rather than conflicting opinions."),
    12: ("deliberation", "inferred", "No conflict; common practical problem; not theoretical."),
    13: ("negotiation", "inferred", "Report asks whether settlement is good and answers yes."),
    14: ("information seeking", "explicit", "Report explicitly calls this info-seeking."),
    15: ("deliberation", "inferred", "No conflict; common practical problem; not theoretical."),
    16: ("negotiation", "inferred", "Competing vehicle maneuvers; settlement branches are described."),
    17: ("persuasion", "inferred", "Report gives conflict=yes and reason good=yes; check whether goal is persuasion."),
    18: ("persuasion", "explicit", "Report explicitly writes persuasion."),
    19: ("negotiation", "inferred", "Conflict and settlement are described."),
    20: ("deliberation", "explicit", "Report explicitly writes deliberation."),
    21: ("negotiation", "ambiguous", "Report gives negotiation if settlement succeeds and eristics if it fails."),
    22: ("mixed", "ambiguous", "Report explicitly lists information seeking followed by deliberation."),
    23: ("persuasion", "ambiguous", "Report writes persuasion, but conflict is a traffic hazard; check dialogue goal."),
    24: ("persuasion", "ambiguous", "Report writes persuasion, but conflict is different travel speeds; check dialogue goal."),
    25: ("persuasion", "ambiguous", "Report writes persuasion, but conflict is poor coordination; check dialogue goal."),
    26: ("persuasion", "ambiguous", "Report writes persuasion, but conflict is a safety issue; check dialogue goal."),
    27: ("persuasion", "ambiguous", "Report writes persuasion, but conflict is a policy priority; check dialogue goal."),
    28: ("persuasion", "ambiguous", "Report writes persuasion, but conflict is congestion; check dialogue goal."),
    29: ("deliberation", "explicit", "Report explicitly writes deliberation."),
    30: ("negotiation", "explicit", "Report explicitly writes negotiation."),
    31: ("information seeking", "explicit", "Report explicitly writes info-seeking."),
    32: ("deliberation", "explicit", "Report explicitly writes deliberation."),
}


def main() -> None:
    records = [json.loads(path.read_text()) for path in sorted((ROOT / "data" / "scenarios").glob("original-*.json"))]
    if [r["number"] for r in records] != list(range(1, 33)):
        raise SystemExit("Expected 32 original records")
    target = ROOT / "data" / "training_labels_draft.csv"
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case_number", "situation", "dialogue_answers_from_report",
                                                   "candidate_type", "evidence_status", "review_note",
                                                   "faculty_approved_type", "reviewer", "review_date"])
        writer.writeheader()
        for record in records:
            label, status, note = LABELS[record["number"]]
            writer.writerow({"case_number": record["number"], "situation": record["situation"],
                             "dialogue_answers_from_report": record["dialogue_prompts"],
                             "candidate_type": label, "evidence_status": status,
                             "review_note": note, "faculty_approved_type": "",
                             "reviewer": "", "review_date": ""})
    print(f"Wrote {len(records)} draft rows to {target}")
    print("Candidate labels are provisional. Faculty-approved labels remain blank.")


if __name__ == "__main__":
    main()
