"""One public entry point for CLI and web versions."""

from __future__ import annotations

import re

from .data import load_records
from .dialogue_rules import classify, find_participants, sentences
from .generate import baseline_dialogue, model_dialogue
from .retrieve import Retriever
from .schema import Answer, validate_answer
from .validate import has_private_reference


def missing_questions(text: str, label: str) -> list[str]:
    lowered = text.lower()
    questions: list[str] = []
    if label in {"information seeking", "mixed"} and not re.search(r"\b(?:acknowledged|confirmed receipt|received the report)\b", lowered):
        questions.append("Has the intended recipient received and acknowledged the report?")
    if not re.search(r"\b(?:near|at|on|location|intersection|lane|road)\b", lowered):
        questions.append("Where exactly is the situation taking place?")
    if label in {"inquiry", "unclear"}:
        questions.append("Which observation could resolve the uncertainty?")
    elif label in {"negotiation", "deliberation"}:
        questions.append("What constraints and priorities do the participants need to agree on?")
    if not questions:
        questions.append("Are the observations independently confirmed and still current?")
    return questions[:2]


def answer_scenario(new_text: str, *, mode: str = "baseline", include_proposed: bool = False,
                    records: list[dict] | None = None) -> Answer:
    text = " ".join(new_text.split())
    if not text:
        raise ValueError("Enter a traffic situation or question")
    if len(text) > 4000:
        raise ValueError("Input must be 4,000 characters or shorter")
    if mode not in {"baseline", "model", "trained"}:
        raise ValueError("Mode must be baseline, model, or trained")
    record_list = records if records is not None else load_records(include_proposed)
    decision = classify(text)
    participants = find_participants(text)
    matches = Retriever(record_list).search(text)
    related = [record for record, _ in matches if _ >= 0.045]
    dialogue_type = "mixed" if decision.secondary else decision.label
    phases = [decision.label] + ([decision.secondary] if decision.secondary else [])
    summary = " ".join(sentences(text)[:2])[:350]
    evidence = decision.evidence[:3]
    if evidence:
        quoted = "; ".join(f"“{item[:180]}”" for item in evidence)
        explanation = f"The input says {quoted} Decision path: {' → '.join(decision.path)}."
    else:
        explanation = "The input does not state a clear communication goal. Decision path: " + " → ".join(decision.path) + "."
    explanation += " This is a suggested communication purpose, not a verified traffic-control instruction."
    decision_path = decision.path
    confidence = decision.confidence
    trained_details = None
    if mode == "trained":
        from .trained import predict

        trained_details = predict(text)
        dialogue_type = trained_details["label"]
        phases = [dialogue_type]
        decision_path = ["Situation and description text", "TF-IDF word and phrase features",
                         f"Trained classifier: {dialogue_type}"]
        terms = [term for term, _ in trained_details["top_features"]]
        explanation = (
            f"The experimental classifier suggests {dialogue_type}. "
            + (f"Its strongest supporting text features here are: {', '.join(terms)}. " if terms else "")
            + "These are model associations, not proof or a causal explanation. "
            + "The model was trained on draft labels from a small set of original scenarios and has not been faculty validated."
        )
        evidence = [sentence for sentence in sentences(text)
                    if any(term in sentence.lower() for term in terms)][:3]
        confidence = "provisional; probability is uncalibrated"
    dialogue = baseline_dialogue(dialogue_type, participants, text)
    actual_mode = "baseline"
    if mode == "model":
        try:
            candidate = model_dialogue(text, dialogue_type, participants, related)
            allowed_speakers = set(participants) | {"Participant 1", "Participant 2"}
            if any(line["speaker"] not in allowed_speakers or has_private_reference(line["text"])
                   for line in candidate):
                raise ValueError("Model output used unsupported speakers or private references")
            dialogue = candidate
            actual_mode = "model"
        except (RuntimeError, ValueError, KeyError, TypeError) as exc:
            actual_mode = "baseline (model unavailable or output rejected)"
            model_error = str(exc)
        else:
            model_error = None
    else:
        model_error = None
    if mode == "trained":
        actual_mode = "experimental trained classifier (draft labels)"
    answer = Answer(
        summary=summary,
        participants=participants,
        dialogue_type=dialogue_type,
        dialogue_phases=phases,
        dialogue=dialogue,
        explanation=explanation,
        unknowns=missing_questions(text, dialogue_type),
        evidence=evidence,
        decision_path=decision_path,
        confidence=confidence,
        mode=actual_mode,
        audit={
            "retrieved": [{"internal_id": record["internal_id"], "score": round(score, 4)}
                          for record, score in matches],
            "record_count": len(record_list),
            "model_error": model_error,
            "baseline_label": "mixed" if decision.secondary else decision.label,
            "trained_details": trained_details,
        },
    )
    validate_answer(answer)
    return answer
