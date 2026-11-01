"""Meeting demos: v1 (rules), v2 (retrieval), v3 (explanations), v4 (what-if)."""

from __future__ import annotations

import argparse
import json

from src.pipeline import answer_scenario


def print_answer(answer, version: int, audit: bool) -> None:
    print("\nSituation:", answer.summary)
    print("Participants:", ", ".join(answer.participants) or "not specified")
    print("Dialogue type:", answer.dialogue_type)
    if version >= 2:
        print("\nIllustrative exchange:")
        for line in answer.dialogue:
            print(f"  {line['speaker']}: {line['text']}")
    if version >= 3:
        print("\nWhy:", answer.explanation)
        print("Missing information:", " ".join(answer.unknowns))
    if audit and version >= 2:
        print("\nDeveloper audit:", json.dumps(answer.audit, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Explainable traffic scenario assistant")
    parser.add_argument("scenario", nargs="?", help="New scenario text; prompted when omitted")
    parser.add_argument("--version", type=int, choices=(1, 2, 3, 4), default=4)
    parser.add_argument("--mode", choices=("baseline", "model", "trained"), default="baseline")
    parser.add_argument("--compare", help="Changed scenario text for a what-if comparison (v4)")
    parser.add_argument("--audit", action="store_true", help="Show private retrieval data to developer")
    parser.add_argument("--include-proposed", action="store_true", help="Also search proposed cases 33–42")
    args = parser.parse_args()
    text = args.scenario or input("Describe a new traffic situation: ")
    try:
        answer = answer_scenario(text, mode=args.mode if args.version >= 2 else "baseline",
                                 include_proposed=args.include_proposed)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))
    print_answer(answer, args.version, args.audit)
    if args.compare and args.version == 4:
        try:
            changed = answer_scenario(args.compare, mode=args.mode,
                                      include_proposed=args.include_proposed)
        except (ValueError, RuntimeError) as exc:
            parser.error(str(exc))
        print("\nWHAT-IF COMPARISON")
        print_answer(changed, args.version, args.audit)
        print("\nChanged dialogue type:", "yes" if answer.dialogue_type != changed.dialogue_type else "no")


if __name__ == "__main__":
    main()
