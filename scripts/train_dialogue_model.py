"""Train and evaluate a text classifier on reviewed or provisional labels.

Use --provisional only for an explicitly labeled experiment. The default
requires faculty-approved labels and refuses to train if they are absent.
"""

from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_examples(provisional: bool) -> tuple[list[str], list[str], list[str]]:
    labels_path = ROOT / "data" / "training_labels_draft.csv"
    rows = list(csv.DictReader(labels_path.open(encoding="utf-8", newline="")))
    text, labels, groups = [], [], []
    for row in rows:
        approved = row["faculty_approved_type"].strip().lower()
        candidate = row["candidate_type"].strip().lower()
        if approved:
            label = approved
        elif provisional and row["evidence_status"] != "ambiguous":
            label = candidate
        else:
            continue
        number = int(row["case_number"])
        record = json.loads((ROOT / "data" / "scenarios" / f"original-{number:02d}.json").read_text())
        # Do not include dialogue_prompts: some contain the answer word itself.
        text.append(record["situation"] + " " + record["description"])
        labels.append(label)
        groups.append(str(number))
    return text, labels, groups


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provisional", action="store_true",
                        help="Train a clearly experimental model using draft non-ambiguous labels")
    args = parser.parse_args()
    try:
        import joblib
        import sklearn
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
        from sklearn.model_selection import GroupKFold, cross_val_predict
        from sklearn.pipeline import Pipeline
    except ImportError as exc:
        raise SystemExit("Install requirements-training.txt in a virtual environment first") from exc
    texts, labels, groups = load_examples(args.provisional)
    if not texts:
        raise SystemExit("No approved training labels yet. Review data/training_labels_draft.csv, or run --provisional for an experimental model.")
    counts = collections.Counter(labels)
    if len(counts) < 2:
        raise SystemExit("At least two different approved dialogue types are needed")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, min_df=1)),
        ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced")),
    ])
    folds = min(5, len(set(groups)))
    predictions = cross_val_predict(pipeline, texts, labels,
                                    cv=GroupKFold(n_splits=folds), groups=groups)
    metrics = {
        "status": "provisional_experiment" if args.provisional else "faculty_reviewed_training",
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "examples": len(texts),
        "class_support": dict(counts),
        "grouped_folds": folds,
        "accuracy": round(float(accuracy_score(labels, predictions)), 3),
        "macro_f1": round(float(f1_score(labels, predictions, average="macro", zero_division=0)), 3),
        "classification_report": classification_report(labels, predictions, output_dict=True, zero_division=0),
        "confusion_labels": sorted(counts),
        "confusion_matrix": confusion_matrix(labels, predictions, labels=sorted(counts)).tolist(),
        "per_case": [{"case_number": group, "expected": expected, "predicted": predicted}
                     for group, expected, predicted in zip(groups, labels, predictions)],
        "training_input": "original report situation + description only; dialogue answer text excluded",
        "sklearn_version": sklearn.__version__,
        "limitations": ["The labels are provisional unless faculty_approved_type was filled in.",
                        "The dataset is very small and class support is uneven.",
                        "The grouped folds hold out complete original cases, but no independent external dataset is available.",
                        "Model probabilities are not calibrated."],
    }
    pipeline.fit(texts, labels)
    output = ROOT / "models"
    output.mkdir(exist_ok=True)
    suffix = "provisional" if args.provisional else "reviewed"
    model_path = output / f"dialogue_classifier_{suffix}.joblib"
    report_path = output / f"training_report_{suffix}.json"
    joblib.dump(pipeline, model_path)
    report_path.write_text(json.dumps(metrics, indent=2) + "\n")
    print(f"Saved model: {model_path}")
    print(f"Saved report: {report_path}")
    print(f"Examples: {len(texts)}; class support: {dict(counts)}")
    print(f"Grouped cross-validation accuracy: {metrics['accuracy']}; macro-F1: {metrics['macro_f1']}")
    if args.provisional:
        print("EXPERIMENT ONLY: labels are draft, not faculty-approved.")


if __name__ == "__main__":
    main()
