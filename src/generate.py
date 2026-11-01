"""Illustrative dialogue generation. The decision and explanation stay deterministic."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request


def baseline_dialogue(label: str, participants: list[str], situation: str) -> list[dict[str, str]]:
    first = participants[0] if participants else "Participant 1"
    second = participants[1] if len(participants) > 1 else "Participant 2"
    topics = [
        (r"obstruction|pothole|block(?:ed|ing)? lane|blockage", "the reported obstruction"),
        (r"parking|park |parking space", "the parking request"),
        (r"pedestrian|crosswalk", "the pedestrian crossing"),
        (r"train|railway", "the rail crossing"),
        (r"signal.*(?:outage|power)|power.*signal", "the reported signal outage"),
        (r"construction|work zone", "the construction area"),
        (r"breakdown|broken vehicle", "the vehicle breakdown"),
    ]
    topic = next((name for pattern, name in topics if re.search(pattern, situation, re.IGNORECASE)),
                 "the reported situation")
    lines = {
        "information seeking": (f"I have an update about {topic}. Can you confirm what you have received?",
                                "I will check the report. Please confirm what you observed and where."),
        "deliberation": (f"We need to decide how to respond to {topic}. What is confirmed so far?",
                         "Let us verify the conditions and agree on a coordinated response."),
        "negotiation": (f"Our plans concerning {topic} may compete. Can we agree on an order?",
                        "Let us confirm each need and agree on a workable arrangement."),
        "persuasion": (f"I interpret {topic} differently. Here is the observation behind my view.",
                       "Please share the evidence so we can resolve the disagreement."),
        "inquiry": (f"The facts about {topic} are uncertain. Which observation can we check first?",
                    "Let us compare the reports before drawing a conclusion."),
        "eristics": ("We are in disagreement. Let us state the issue clearly.",
                     "We should seek a neutral review if we cannot discuss it constructively."),
        "mixed": ("First, can we confirm what is known?",
                  "After that, we can decide together what to do."),
        "unclear": ("What exactly needs to be decided or confirmed?",
                    "Please identify who is involved and what each participant knows."),
    }
    a, b = lines[label]
    return [{"speaker": first, "text": a}, {"speaker": second, "text": b}]


DIALOGUE_SCHEMA = {
    "type": "object", "properties": {
        "dialogue": {"type": "array", "items": {"type": "object", "properties": {
            "speaker": {"type": "string"}, "text": {"type": "string"}},
            "required": ["speaker", "text"], "additionalProperties": False}},
    }, "required": ["dialogue"], "additionalProperties": False,
}


def model_dialogue(text: str, label: str, participants: list[str], related: list[dict]) -> list[dict[str, str]]:
    """Use the Responses API; credentials never enter source files or logs."""
    key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")
    if not key or not model:
        raise RuntimeError("Set OPENAI_API_KEY and OPENAI_MODEL for model mode")
    summaries = [r["situation"] for r in related]
    prompt = (
        "Write a short, illustrative two-line traffic communication exchange. "
        "Use only the facts in NEW INPUT; related examples are context, not facts to copy. "
        "Do not mention source cases or IDs. Do not claim physical equipment has actually acted. "
        "Use the supplied participant names when possible. Express uncertainty when needed.\n\n"
        f"NEW INPUT: {text}\nDIALOGUE TYPE: {label}\nPARTICIPANTS: {participants}\n"
        f"RELATED EXAMPLE SITUATIONS: {summaries}"
    )
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": "You write illustrative, cautious dialogue for an educational traffic scenario app."},
            {"role": "user", "content": prompt},
        ],
        "text": {"format": {"type": "json_schema", "name": "traffic_dialogue",
                            "schema": DIALOGUE_SCHEMA, "strict": True}},
    }
    request = urllib.request.Request(
        os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/") + "/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=35) as response:
            result = json.load(response)
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Model request failed: {exc}") from exc
    contents = [part.get("text", "") for item in result.get("output", [])
                for part in item.get("content", []) if part.get("type") == "output_text"]
    if not contents:
        raise RuntimeError("Model returned no text")
    data = json.loads("".join(contents))
    lines = data.get("dialogue")
    if not isinstance(lines, list) or not 1 <= len(lines) <= 4:
        raise RuntimeError("Model returned invalid dialogue")
    if any(not isinstance(line, dict) or not isinstance(line.get("speaker"), str)
           or not isinstance(line.get("text"), str) or not line["text"].strip() for line in lines):
        raise RuntimeError("Model returned invalid dialogue lines")
    return lines
