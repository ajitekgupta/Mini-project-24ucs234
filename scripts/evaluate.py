"""Repeatable evaluation of the rule and explanation contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import answer_scenario  # noqa: E402
from src.validate import has_private_reference  # noqa: E402


def main() -> None:
    cases = json.loads((ROOT / "tests" / "evaluation_cases.json").read_text())
    correct = grounded = private_free = 0
    rows = []
    for case in cases:
        answer = answer_scenario(case["prompt"])
        label_ok = answer.dialogue_type in case["acceptable"]
        evidence_ok = all(fact in case["prompt"] for fact in answer.evidence)
        leakage_ok = not has_private_reference(str(answer.public_dict()))
        correct += label_ok
        grounded += evidence_ok
        private_free += leakage_ok
        rows.append({"name": case["name"], "expected": case["acceptable"],
                     "predicted": answer.dialogue_type, "label_ok": label_ok,
                     "evidence_exact_from_input": evidence_ok, "private_reference_free": leakage_ok})
    report = {"scope": "baseline rule classifier; author-reviewed prompts, not faculty labels",
              "count": len(cases), "label_agreement": f"{correct}/{len(cases)}",
              "evidence_span_checks": f"{grounded}/{len(cases)}",
              "private_reference_checks": f"{private_free}/{len(cases)}",
              "cases": rows,
              "limitations": ["These prompts are small and author-created; accuracy is not a real-world safety claim.",
                              "Exact evidence checks do not establish that all generated statements are factually correct.",
                              "Human review is still needed for dialogue quality and explanations."]}
    target = ROOT / "evaluation_report.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, indent=2))
    print("Detailed results:", target)


if __name__ == "__main__":
    main()
