from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


LABELS = (
    "persuasion", "negotiation", "inquiry", "deliberation",
    "information seeking", "eristics", "mixed", "unclear",
)


@dataclass(frozen=True)
class Decision:
    label: str
    secondary: str | None
    path: list[str]
    evidence: list[str]
    confidence: str


@dataclass
class Answer:
    summary: str
    participants: list[str]
    dialogue_type: str
    dialogue_phases: list[str]
    dialogue: list[dict[str, str]]
    explanation: str
    unknowns: list[str]
    evidence: list[str]
    decision_path: list[str]
    confidence: str
    mode: str
    audit: dict[str, Any] = field(default_factory=dict, repr=False)

    def public_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("audit", None)
        return data


def validate_answer(answer: Answer) -> None:
    if answer.dialogue_type not in LABELS:
        raise ValueError("Invalid dialogue type")
    if not answer.summary or not answer.explanation:
        raise ValueError("Summary and explanation are required")
    for line in answer.dialogue:
        if not line.get("speaker") or not line.get("text"):
            raise ValueError("Each dialogue line needs speaker and text")
    from .validate import has_private_reference

    visible = str(answer.public_dict())
    if has_private_reference(visible):
        raise ValueError("Internal source reference leaked into visible answer")
