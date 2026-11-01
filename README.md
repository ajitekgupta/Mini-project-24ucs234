# XAI-ITS Scenario Lab

An Explainable AI (XAI) decision-support system for connected and autonomous transportation scenarios. The application analyzes natural-language traffic situations, identifies participating entities (V2V/V2I), classifies communication objectives using formal dialogue theory, generates an illustrative message exchange, and provides a transparent decision path with input-grounded evidence.

> **Academic Report:** For the complete academic methodology, system architecture, 9-step engineering lifecycle, and an itemized breakdown of how each output component enables Explainable AI, see [PROJECT_REPORT.md](PROJECT_REPORT.md).

## Quick Start (Terminal & Local Web App)

The application runs locally using Python 3.10 or newer with zero external dependencies required for the offline baseline:

```bash
# 1. Run the Command-Line Interface (CLI demo)
python3 cli.py --version 3

# 2. Run the Local Web Dashboard
python3 app.py
```

To access the web interface, open `http://127.0.0.1:8765` in any browser. Press `Ctrl+C` in the terminal to stop the server.

## Architecture and Repository Structure

- `app.py` & `web/`: Local web dashboard featuring real-time scenario analysis and counterfactual "What-if" comparative explanations.
- `cli.py`: Interactive command-line interface supporting multiple verbosity levels and execution modes.
- `src/`: Core Python pipeline:
  - `schema.py`: Formal data contracts for `Answer` and `Decision` objects with strict validation.
  - `dialogue_rules.py`: Transparent decision-tree logic providing input-grounded evidence and traceable decision paths.
  - `retrieve.py`: Case-based retrieval engine using TF-IDF vectorization and cosine similarity.
  - `trained.py`: Inference pipeline for the supervised machine learning model.
  - `pipeline.py`: Central integration orchestrator connecting ingestion, retrieval, classification, and validation.
- `data/scenarios/`: 32 structured JSON scenario records extracted from the core ITS curriculum report.
- `data/proposed_scenarios/`: 10 newly authored extension scenarios (cases 33 to 42) with full PEAS specifications and class diagrams.
- `docs/Scenarios_and_Diagrams_33_42.pdf`: Illustrated documentation covering scenarios 33 to 42 and reviewed UML class diagrams.
- `data/labeling_guide.md`: Formal taxonomy guidelines for the seven dialogue purposes and decision boundaries.
- `data/training_labels_draft.csv`: Annotated scenario dataset with ambiguity indicators and candidate categories.
- `models/`: Serialized scikit-learn classifier (`dialogue_classifier_provisional.joblib`) and 5-fold cross-validation metrics.
- `scripts/`: Standalone utilities for data ingestion (`prepare_data.py`), dataset auditing (`audit_sources.py`), model training (`train_dialogue_model.py`), and test evaluation (`evaluate.py`).
- `tests/`: Automated unit tests (`test_core.py`) and standard evaluation test cases (`evaluation_cases.json`).

## Dual-Engine Methodology

Due to the academic scale of the dataset (32 original cases), the project employs a Dual-Engine Architecture to balance deterministic reliability with empirical machine learning:

1. **Deterministic Rule Baseline:** An inspectable decision-tree engine that provides guaranteed transparency, quotes verbatim input clauses, and flags epistemic uncertainties.
2. **Supervised Machine Learning Classifier:** A scikit-learn pipeline (unigram + bigram TF-IDF with Logistic Regression) trained on 22 clean scenario descriptions. In 5-fold grouped cross-validation, it achieves 50% accuracy and 0.392 Macro F1.

### Training the Classifier

The machine learning training pipeline (`scripts/train_dialogue_model.py`) trains on the non-ambiguous scenario records while holding out ambiguous cases pending further ground-truth verification:

```bash
# Train the supervised model on clean scenario descriptions
.venv/bin/python scripts/train_dialogue_model.py --provisional

# Test the trained model in the CLI
.venv/bin/python cli.py --mode trained "A vehicle asks the signal to confirm receipt of an obstruction report."
```

## Optional AI Writing Adapter

The pipeline includes an optional generative language-model adapter (`src/generate.py`) using structured outputs:

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-4o-mini"
python3 cli.py --mode model
```

If API credentials are not set, the application automatically falls back to the deterministic offline template generator.

## Testing and Verification

To execute the automated test and validation suite:

```bash
# Run unit tests (data integrity, privacy guardrails, retrieval, and pipeline checks)
python3 -m unittest discover -s tests -v

# Run source dataset audit
python3 scripts/audit_sources.py

# Run benchmark evaluation across 12 diverse test prompts
python3 scripts/evaluate.py
```

## Scope and Limitations

* **Decision Support:** This application serves as an educational decision-support tool; it does not directly transmit actuation commands to physical traffic controllers or vehicle ECUs.
* **Semantic Granularity:** Keyword and n-gram representations may miss subtle contextual nuances; the system explicitly flags underspecified scenarios as `unclear` or `mixed`.
* **Supervisory Review:** When using the optional language-model adapter, generated dialogue exchanges are illustrative and intended for human supervisory verification.
