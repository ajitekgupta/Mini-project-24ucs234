# XAI-ITS Scenario Lab

A local, educational assistant for new traffic scenarios. It identifies a
communication purpose, writes an illustrative exchange, and shows exact
input evidence plus an inspectable decision path. It also compares a changed
scenario to show when and why the decision changes.

> **Academic Evaluation Note:** For detailed academic methodology, design rationale, and an itemized breakdown of how each output component enables Explainable AI, please see [PROJECT_REPORT.md](PROJECT_REPORT.md).

## Quick Start (Terminal & Local Web App)

Open this repository in VS Code and use the built-in terminal. Python 3.10 or newer is sufficient for the offline application; no external API key is required.

```bash
python3 cli.py --version 3
python3 app.py
```

For the local web interface, open `http://127.0.0.1:8765` in your browser. Press `Ctrl+C` in the terminal to stop the server.

## What each part does

- `data/scenarios/`: 32 machine-extracted original report records, with
  source page locations and pending review status.
- `data/proposed_scenarios/`: ten separately authored additions; excluded
  from retrieval unless explicitly enabled.
- `data/labeling_guide.md`: guidelines for the seven dialogue purposes,
  decision questions, and examples of ambiguous cases.
- `src/retrieve.py`: deterministic TF-IDF cosine retrieval, implemented with
  the Python standard library so offline demos need no packages.
- `src/dialogue_rules.py`: cautious, inspectable baseline for the dialogue
  decision path. It may return `unclear` for weak evidence.
- `src/generate.py`: offline illustrative exchange and an optional language
  model writing adapter.
- `src/pipeline.py`: one entry point used by CLI and browser interface.
- `scripts/evaluate.py`: repeatable baseline evaluation.
- `data/training_labels_draft.csv`: candidate labels extracted from the
  report's Yes/No answers, with ambiguous cases flagged for review.
- `scripts/train_dialogue_model.py`: trains and tests the experimental classifier.

The offline baseline uses rules and the 32 original records as references.
The separate trained option uses 22 original cases with provisional labels;
10 ambiguous cases are held out pending review. The optional API writing
mode uses a pre-trained language model to write dialogue; it does not
fine-tune that model. In trained mode, the path and feature explanation
come from the trained classifier.

## Experimental training

The project's `.venv` already has the training packages installed. In VS
Code's terminal, run:

```bash
.venv/bin/python scripts/train_dialogue_model.py --provisional
.venv/bin/python cli.py --mode trained "A vehicle asks the signal to confirm receipt of an obstruction report."
.venv/bin/python app.py
```

In the browser, choose **Experimental trained classifier**. The model uses
Python, scikit-learn TF-IDF word/phrase features, and Logistic Regression.
It learns a dialogue type from the *situation and description*, without
reading the report's dialogue answer text as input. `joblib` saves the
model in `models/`. Five-fold cross-validation holds out whole original
cases. The current draft result is **50% accuracy and 0.392 macro F1 on 22
cases**. It has no training examples for inquiry, eristics, or mixed
dialogue, and its probabilities are not calibrated. This is a development
result, not a final production accuracy claim. See the report in `models/` for
every held-out prediction.

Before final training, review `data/training_labels_draft.csv` with the
faculty member. Fill `faculty_approved_type` for verified rows and run
`.venv/bin/python scripts/train_dialogue_model.py` without `--provisional`.
Do not rerun `scripts/build_training_labels.py` after editing the CSV unless
you save the reviewed labels; that script overwrites the table.

## Optional AI writing mode

Set `OPENAI_API_KEY` and `OPENAI_MODEL` in your local terminal environment,
then run `python3 cli.py --mode model` or choose **AI writing mode** in the
browser interface. Do not paste credentials into code or a shared document.
The adapter uses the [official Responses API structured output format](https://developers.openai.com/api/docs/guides/structured-outputs).
The exact model name is your choice, subject to your API account. If the
credentials are absent or the generated dialogue fails validation, the app
uses the offline baseline and labels that fallback. A live API call has not
been verified without the student's credentials.

## Rebuild source records

The included JSON is ready to run. To re-extract from the original PDF,
install `pdfplumber` and run:

```bash
python3 -m pip install -r requirements-data.txt
python3 scripts/prepare_data.py "/absolute/path/to/Scenarios (1).pdf"
```

This overwrites the 32 extracted JSON records, so save human corrections
first. `scripts/import_proposed.py` similarly imports the separately authored
`scenarios.json` package. See `data/source_audit.md` before claiming the
records or diagram mappings have been verified.

## Validate and evaluate

```bash
python3 -m unittest discover -s tests -v
python3 scripts/audit_sources.py
python3 scripts/evaluate.py
```

The 12 evaluation prompts are author-created. Label agreement on them is a
development check, not an independent estimate of accuracy. For further evaluation,
review labels, add paraphrases and harder cases, and
keep the test set separate from retrieval records. A full human review of
generated dialogue and explanation quality is still required.

## Limitations

This is educational decision support and does not issue real traffic-control
commands. Keywords and TF-IDF can miss paraphrases or nuanced goals. Source
cases have not all been manually checked, and source diagram numbering is
not reliable. The optional language model may produce unsupported details;
its dialogue is illustrative, and the final answer should be reviewed by a
human in any consequential use.
