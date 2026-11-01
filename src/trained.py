"""Load a locally produced classifier and inspect its text-feature weights."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def predict(text: str, *, reviewed: bool = False) -> dict:
    try:
        import joblib
    except ImportError as exc:
        raise RuntimeError("Install requirements-training.txt to use the trained model") from exc
    suffix = "reviewed" if reviewed else "provisional"
    model_path = ROOT / "models" / f"dialogue_classifier_{suffix}.joblib"
    report_path = ROOT / "models" / f"training_report_{suffix}.json"
    if not model_path.exists() or not report_path.exists():
        raise RuntimeError(f"Trained model is missing; run scripts/train_dialogue_model.py first")
    # Only load project-created artifacts. joblib is a pickle format and must
    # never load an untrusted file.
    model = joblib.load(model_path)
    report = json.loads(report_path.read_text())
    label = str(model.predict([text])[0])
    probabilities = model.predict_proba([text])[0]
    labels = list(model.named_steps["classifier"].classes_)
    probability = float(probabilities[labels.index(label)])
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]
    features = vectorizer.transform([text])
    if len(labels) == 2:
        # scikit-learn stores one coefficient row for a binary classifier.
        sign = 1 if label == labels[1] else -1
        weights = classifier.coef_[0] * sign
    else:
        weights = classifier.coef_[labels.index(label)]
    names = vectorizer.get_feature_names_out()
    contributions = sorted(((names[index], float(value * weights[index]))
                            for index, value in zip(features.indices, features.data)
                            if value * weights[index] > 0), key=lambda pair: pair[1], reverse=True)[:5]
    return {"label": label, "probability": probability,
            "top_features": contributions, "training_status": report["status"],
            "class_support": report["class_support"]}
