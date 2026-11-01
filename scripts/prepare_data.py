"""Extract the original report into auditable records; requires pdfplumber.

Run once when source files change. Extracted text is source material, not a
human-verified label or a trained model.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADINGS = re.compile(r"(?m)^(\d+) Setup\s*$")
SUBHEADINGS = re.compile(r"(?m)^(\d+)\.(\d+)\s+([^\n]+)$")


def clean(value: str) -> str:
    lines = [line.strip() for line in value.splitlines()]
    lines = [line for line in lines if line and not re.fullmatch(r"\d+", line)]
    return " ".join(lines).replace("ﬁ", "fi").replace("ﬂ", "fl")


def extract(pdf_path: Path) -> list[dict]:
    import pdfplumber

    pages: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    starts: list[int] = []
    offset = 0
    for page in pages:
        starts.append(offset)
        offset += len(page) + 1
    text = "\n".join(pages)
    matches = list(HEADINGS.finditer(text))
    records: list[dict] = []
    for index, match in enumerate(matches):
        number = int(match.group(1))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[match.end():end]
        sections: dict[str, str] = {}
        section_matches = list(SUBHEADINGS.finditer(block))
        for j, section_match in enumerate(section_matches):
            if int(section_match.group(1)) != number:
                continue
            section_end = section_matches[j + 1].start() if j + 1 < len(section_matches) else len(block)
            heading = section_match.group(3).strip().lower()
            value = clean(block[section_match.end():section_end])
            if heading in sections:
                sections[heading] += " " + value
            else:
                sections[heading] = value
        first_page = sum(start <= match.start() for start in starts)
        last_page = sum(start < end for start in starts)
        scenario = sections.get("scenario", "")
        record = {
            "internal_id": f"original-{number:02d}",
            "number": number,
            "origin": "original_report",
            "title": scenario,
            "situation": scenario,
            "entities": sections.get("entities", ""),
            "communication_type": sections.get("type of communication", ""),
            "description": sections.get("description", ""),
            "dialogue_prompts": sections.get("dialogues", sections.get("dialogue", "")),
            "source_proposed_solutions": sections.get("solutions", sections.get("solution", "")),
            "peas": sections.get("peas", ""),
            "cascading_problems": sections.get("cascading problems", ""),
            "other_sections": {k: v for k, v in sections.items() if k not in {
                "scenario", "entities", "type of communication", "description",
                "dialogues", "dialogue", "solutions", "solution", "peas", "cascading problems",
            }},
            "candidate_dialogue_type": None,
            "label_reason": None,
            "diagram_mapping": {"status": "unverified", "image": None},
            "review_status": "machine_extracted_needs_review",
            "source_location": {"file": pdf_path.name, "pages": list(range(first_page, last_page + 1))},
        }
        records.append(record)
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    args = parser.parse_args()
    records = extract(args.pdf)
    if [r["number"] for r in records] != list(range(1, 33)):
        raise SystemExit(f"Expected cases 1–32, found {[r['number'] for r in records]}")
    output = ROOT / "data" / "scenarios"
    output.mkdir(parents=True, exist_ok=True)
    for record in records:
        (output / f"{record['internal_id']}.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    with (ROOT / "data" / "source_mapping.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["written_case", "source_pages", "diagram_image", "mapping_status", "note"])
        for record in records:
            writer.writerow([record["number"], ",".join(map(str, record["source_location"]["pages"])),
                             "", "unverified", "Match by diagram contents; filenames are not reliable."])
    print(f"Extracted {len(records)} original records to {output}")


if __name__ == "__main__":
    main()
