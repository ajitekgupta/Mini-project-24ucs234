"""Inspectable, cautious guidance based on the supplied dialogue decision tree.

These patterns are a baseline, not a claim of complete natural-language understanding.
The evidence list always consists of exact sentences from the new user input.
"""

from __future__ import annotations

import re

from .schema import Decision


PATTERNS = {
    "hostility": r"\b(?:insult|hostile|shout|argu(?:e|ing) just to win|attack each other|antagonis\w*)\b",
    "disagreement": r"\b(?:disagree|dispute|deny|denies|contrary opinions|believes? .* but .* believes?|argue whether)\b",
    "competing": r"\b(?:both want|same (?:spot|space|lane)|competing|compete|conflicting interests|make a deal|settle who|take turns)\b",
    "joint_truth": r"\b(?:investigate|determine whether|find out whether|why did|what caused|contradictory reports|conflicting reports|verify whether|check whether)\b",
    "missing_info": r"\b(?:has not (?:yet )?(?:received|heard)|have not (?:yet )?(?:received|heard)|did not receive|does not know|do not know|unaware|not informed|ask(?:s|ed)? (?:for|whether)|request(?:s|ed)? (?:an? )?(?:update|confirmation|information)|confirm (?:receipt|whether)|acknowledg\w*|where is|what is the status)\b",
    "joint_action": r"\b(?:decide|coordinate|agree on (?:a|the) (?:plan|action|response)|plan (?:how|a)|choose (?:a|the) (?:route|action)|what to do next|how to respond|how to manage|allocate|schedule)\b",
    "sequence": r"\b(?:first .* then|after .* (?:then|decide|coordinate)|followed by|once .* confirmed)\b",
}


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text.strip()) if s.strip()]


def classify(text: str) -> Decision:
    hits: dict[str, list[str]] = {}
    for name, pattern in PATTERNS.items():
        hits[name] = [sentence for sentence in sentences(text)
                      if re.search(pattern, sentence, flags=re.IGNORECASE)]
    evidence: list[str] = []

    def add(*names: str) -> None:
        for name in names:
            for sentence in hits[name]:
                if sentence not in evidence:
                    evidence.append(sentence)

    if hits["hostility"]:
        add("hostility")
        return Decision("eristics", None,
                        ["Conflict or antagonism is explicit", "Neither resolution nor settlement is stated as the goal", "Eristics"],
                        evidence, "medium")
    if hits["competing"]:
        add("competing")
        return Decision("negotiation", None,
                        ["Competing interests are explicit", "A settlement or allocation is needed", "Negotiation"],
                        evidence, "medium")
    if hits["disagreement"] and not hits["joint_truth"]:
        add("disagreement")
        return Decision("persuasion", None,
                        ["Disagreement about a claim or opinion is explicit", "Resolution of the disagreement is the goal", "Persuasion"],
                        evidence, "medium")
    if hits["joint_truth"]:
        add("joint_truth", "disagreement")
        return Decision("inquiry", None,
                        ["Participants share an unresolved question", "They need to investigate what is true", "Inquiry"],
                        evidence, "medium")
    if hits["missing_info"]:
        add("missing_info", "joint_action", "sequence")
        secondary = "deliberation" if hits["joint_action"] and hits["sequence"] else None
        path = ["A participant lacks information or acknowledgement", "The immediate goal is to obtain or confirm it", "Information seeking"]
        if secondary:
            path.append("After confirmation, a shared action may require deliberation")
        return Decision("information seeking", secondary, path, evidence, "medium")
    if hits["joint_action"]:
        add("joint_action")
        return Decision("deliberation", None,
                        ["A shared practical problem is stated", "The participants need to choose an action", "Deliberation"],
                        evidence, "medium")
    return Decision("unclear", None,
                    ["The text does not make the participants' dialogue goal clear", "Ask for the missing goal before selecting a type"],
                    [], "low")


def find_participants(text: str) -> list[str]:
    if re.search(r"\b(?:two vehicles|both vehicles|vehicle 1.*vehicle 2|two drivers|both drivers)\b", text, re.IGNORECASE):
        return ["Vehicle 1", "Vehicle 2"]
    labels = [
        (r"\b(?:vehicle|car|driver|bus|truck|ambulance)s?\b", "Vehicle or driver"),
        (r"\b(?:traffic signal|traffic light|signal controller|signal)s?\b", "Traffic signal"),
        (r"\bpedestrians?\b", "Pedestrian"),
        (r"\b(?:train|railway signal)s?\b", "Train or railway signal"),
        (r"\b(?:operator|traffic manager)s?\b", "Traffic operator"),
        (r"\b(?:sensor|detector)s?\b", "Sensor or detector"),
        (r"\b(?:emergency services|responder)s?\b", "Emergency responder"),
    ]
    return [label for pattern, label in labels if re.search(pattern, text, re.IGNORECASE)]
