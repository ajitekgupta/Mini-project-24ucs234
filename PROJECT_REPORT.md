# Project Report: Explainable AI in Intelligent Transportation Systems (XAI-ITS)

**Project Title:** XAI-ITS Scenario Lab: Dialogue Goal Classification and Explainable Decision Support  
**Academic Context:** B.Tech Computer Science & Engineering — Mini Project  
**Repository:** `traffic-dialogue-ai`  

---

## 1. Executive Summary

Intelligent Transportation Systems (ITS) increasingly rely on connected autonomous vehicles (CAVs), smart traffic signals, and roadside infrastructure (V2V and V2I communication). When unusual or hazardous traffic situations occur (such as sudden road obstructions, signal outages, or overtaking conflicts), entities must communicate effectively to coordinate actions.

This project implements an **Explainable AI (XAI) decision-support system** that analyzes written traffic scenarios, identifies participating entities, classifies the primary communication purpose using formal dialogue theory, generates an illustrative message exchange, and provides a fully inspectable, evidence-backed explanation. 

Rather than treating AI as an opaque black box, the system grounds every recommendation in verbatim input facts, exposes its step-by-step decision path, and highlights missing situational variables.

---

## 2. Problem Statement and Scope

### 2.1 The Challenge in ITS Communication
Connected transportation networks are Cyber-Physical Systems (CPS). When multiple autonomous or semi-autonomous agents interact:
* Different situations require fundamentally different communication goals (e.g., verifying a sensor report vs. negotiating right-of-way vs. coordinating detour plans).
* Human operators and traffic controllers cannot trust black-box AI recommendations without knowing **why** a specific action or dialogue was chosen.
* Real-world traffic prompts often omit critical context (such as exact location or confirmation of signal receipt). A reliable system must explicitly communicate what it *does not know* rather than guessing.

### 2.2 System Scope
* **Input:** A natural-language description of an emerging traffic event.
* **Outputs:** Participant identification, dialogue type classification, an illustrative two-line message exchange, grounded textual explanation, decision path trace, and identified uncertainties.
* **Domain Boundary:** This project is an educational decision-support tool. It does not issue physical actuator commands or direct traffic signal controllers.

---

## 3. Theoretical Framework: Walton’s Dialogue Typology

The system classifies communication goals according to Walton’s dialogue typology adapted for multi-agent transportation systems:

| Dialogue Type | ITS Meaning | Typical Traffic Example |
| :--- | :--- | :--- |
| **Information Seeking** | One participant possesses information that another lacks. | A vehicle asks a traffic signal whether it received an obstruction report. |
| **Deliberation** | Participants share a common problem and must agree on a joint course of action. | A traffic signal and surrounding vehicles coordinate detour routes around a closed lane. |
| **Inquiry** | Participants jointly investigate uncertain facts to establish ground truth. | Two sensor nodes cross-validate conflicting obstacle detections. |
| **Negotiation** | Participants have conflicting preferences and work toward a compromise. | Two vehicles arrive simultaneously at an uncontrolled merge point or parking spot. |
| **Persuasion** | One participant attempts to change the belief or state of another using evidence. | A vehicle transmits sensor telemetry to persuade an infrastructure controller that a reported hazard is real. |
| **Eristics** | Adversarial interaction or unresolved conflict without consensus. | Uncooperative autonomous agents encountering communication protocol deadlocks. |
| **Mixed** | A multi-phase dialogue where the purpose transitions as facts emerge. | Phase 1: Information Seeking (confirming hazard) followed by Phase 2: Deliberation (coordinating response). |
| **Unclear** | Insufficient evidence in the input to assign a definitive category. | An underspecified description lacking agent goals or actions. |

---

## 4. Dataset Architecture and Engineering Design

### 4.1 The 32 Primary Course Scenarios
The foundational dataset was extracted from the 42-page course report (`Scenarios (1).pdf`):
* **Structured JSON Conversion:** Each of the 32 written scenarios was parsed into a standardized JSON schema (`data/scenarios/original-01.json` to `original-32.json`) capturing `situation`, `entities`, `communication_type`, `description`, `known_facts`, `goals`, `dialogue_prompts`, and source locations.
* **UML Class Diagram Role:** The 32 associated class diagrams (`dia/`) provide a formal domain ontology (e.g., `Vehicle`, `TrafficSignal`, `ObstructionSensor`, `ObstructionReporter`), establishing consistent agent roles and relational boundaries.

### 4.2 Data Labeling and Ambiguity Analysis
The source report contained Yes/No analytical answers rather than explicit category labels. In `data/training_labels_draft.csv`:
* **22 Clean Scenarios:** Confidently labeled based on explicit communication goals (9 Deliberation, 5 Information Seeking, 5 Negotiation, 3 Persuasion).
* **10 Ambiguous Scenarios:** Cases 4, 11, 21, 22, and 23–28 involve conditional goals, multi-stage interactions, or describe physical roadway hazards without clear communicative intent.
* **Academic Integrity Decision:** These 10 ambiguous cases were deliberately **held out from model training** pending faculty review. Fabricating labels for ambiguous cases would introduce artificial bias into the model.

### 4.3 Faculty-Assigned Extension: Scenarios 33–42
As instructed by the faculty supervisor, ten comprehensive new ITS scenarios (cases 33 to 42) were authored and modeled with complete PEAS specifications, communication dialogues, solutions, cascading problems, and reviewed UML class diagrams:
* **Compiled Document:** The full illustrated document containing all 10 scenarios and their 10 class diagrams is preserved in [`docs/Scenarios_and_Diagrams_33_42.pdf`](docs/Scenarios_and_Diagrams_33_42.pdf).
* **Machine-Readable Conversion:** All 10 authored cases are converted into standardized JSON format in `data/proposed_scenarios/proposed-33.json` to `proposed-42.json`.
* **Interactive Reference Extension:** In the web interface and CLI, an optional checkbox (`Include proposed cases 33–42`) allows users to expand the TF-IDF retrieval knowledge base from 32 to 42 records to benchmark new inputs against these newly authored situations.

---

## 5. System Architecture: The Dual-Engine Approach

### 5.1 Rationale for Dual Approaches (Why Not Just Deep Learning?)
In machine learning, **32 records is an exceptionally small sample size**. 
* Attempting to fine-tune a large neural network on 22 or 32 examples guarantees severe overfitting: the model would memorize exact phrases rather than learning generalizable semantics.
* To achieve true academic rigor, the project implements a **Dual-Engine Architecture** that pairs a deterministic baseline with an empirical machine learning model:

```
                          [User Input Scenario]
                                    |
          +-------------------------+-------------------------+
          |                                                   |
          v                                                   v
 [Engine 1: Rule Baseline]                       [Engine 2: Trained Classifier]
  - Decision-tree logic                           - scikit-learn Pipeline
  - Keyword & pattern matching                    - TF-IDF unigram + bigram
  - Verbatim text quotation                       - Multi-class Logistic Regression
  - 100% deterministic & inspectable              - Learned statistical associations
          |                                                   |
          +-------------------------+-------------------------+
                                    |
                                    v
                     [Grounded Explainable Output]
```

### 5.2 Engine 1: Deterministic Rule Baseline (`src/dialogue_rules.py`)
* Operates on a structured decision tree reflecting course dialogue guidelines.
* Evaluates communicative intent, information asymmetry, and consensus requirements.
* Provides guaranteed explainability by quoting the exact clauses that triggered each branch.

### 5.3 Engine 2: Supervised Machine Learning Classifier (`src/trained.py`)
* **Pipeline:** Word and phrase level TF-IDF vectorization (`ngram_range=(1, 2)`, sublinear term frequency) coupled with a multi-class Logistic Regression classifier (`class_weight='balanced'`).
* **Training Input:** Trained strictly on scenario and description text; dialogue prompt answers were excluded so the target label is not leaked into features.
* **Validation Setup:** Evaluated using Grouped 5-Fold Cross-Validation, ensuring all data from a single case is held out during testing.
* **Experimental Findings:** Achieved **50.0% accuracy (11/22 correct) and 0.392 Macro F1** across 4 dialogue classes.
* **Transparent Reporting:** The model explicitly flags that its probabilities are uncalibrated and exposes its top contributing TF-IDF feature weights for every prediction.

---

## 6. Anatomy of the Output: What Each Component Means in Explainable AI

When a user submits a scenario (e.g., *"A vehicle reports an obstruction ahead, but the nearby traffic signal has not yet received the report"*), the system produces an `Answer` object. 

Below is an itemized breakdown of what each output field tells the user and how it directly advances the goals of Explainable AI (XAI):

```
+------------------------------------------------------------------------------------+
| 1. Scenario Summary & Participants                                                 |
|    Summary: Condensed representation of the input event.                           |
|    Participants: ["reporting vehicle", "traffic signal"]                          |
+------------------------------------------------------------------------------------+
| 2. Suggested Dialogue Purpose                                                      |
|    Dialogue Type: information seeking                                              |
|    Phases: ["information seeking"]                                                 |
+------------------------------------------------------------------------------------+
| 3. Illustrative Exchange                                                           |
|    Vehicle: "Reporting obstruction ahead; requesting confirmation of receipt."     |
|    Signal:  "Report not yet logged in local registry; transmit sensor telemetry."  |
+------------------------------------------------------------------------------------+
| 4. Grounded Explanation & Evidence                                                 |
|    Quoted Evidence: "nearby traffic signal has not yet received the report"        |
|    Decision Path: Unacknowledged hazard report -> Information seeking              |
|    Confidence: High (Rule Baseline) / Provisional (Trained Classifier)             |
+------------------------------------------------------------------------------------+
| 5. Epistemic Uncertainty (Missing Information)                                     |
|    - "Has the intended recipient received and acknowledged the report?"            |
|    - "Where exactly is the situation taking place?"                                |
+------------------------------------------------------------------------------------+
```

### Detailed Component Explanations:

### 1. Identified Participants (`participants`)
* **What it tells the user:** Which agents or infrastructure nodes are actively involved in the scenario (e.g., vehicle, roadside unit, traffic signal, emergency responder).
* **XAI Value (Agent Attribution):** Verifies that the system correctly mapped the physical actors and communication topology (V2V vs. V2I) before formulating decisions.

### 2. Dialogue Type and Phases (`dialogue_type`, `dialogue_phases`)
* **What it tells the user:** The formal communicative objective (e.g., *Information Seeking*, *Deliberation*). If the interaction involves multiple stages, `dialogue_phases` indicates the sequence of goals.
* **XAI Value (Semantic Transparency):** Replaces vague action predictions with standardized, academically grounded dialogue categories that human operators can validate.

### 3. Illustrative Exchange (`dialogue`)
* **What it tells the user:** A concrete, readable two-line transcript showing how the participants should initiate and respond to the situation.
* **XAI Value (Behavioral Concreteness):** Translates abstract classifications into tangible communication behavior, showing exactly how the chosen dialogue type manifests in practice.

### 4. Verbatim Input Evidence (`evidence`)
* **What it tells the user:** The specific sentences or clauses extracted directly from the user's input text that justified the classification (e.g., *“nearby traffic signal has not yet received the report”*).
* **XAI Value (Faithful Grounding):** Guarantees that the explanation is tethered to actual user input rather than hallucinated facts or ungrounded external assumptions.

### 5. Inspectable Decision Path (`decision_path`)
* **What it tells the user:** The explicit logical chain traveled by the system:
  * In Baseline Mode: `[Identified unacknowledged report -> Evaluated information asymmetry -> Selected information seeking]`.
  * In Trained Mode: `[Raw Text -> TF-IDF N-Gram Features -> Logistic Regression Weights -> Predicted Class]`.
* **XAI Value (Algorithmic Auditability):** Allows an examiner, engineer, or auditor to trace the exact rules or statistical weights that produced the final label.

### 6. Missing Information and Uncertainty (`unknowns`, `confidence`)
* **What it tells the user:** Specific critical facts omitted by the scenario (e.g., unconfirmed location, unknown acknowledgment status) along with an honest assessment of confidence.
* **XAI Value (Epistemic Humility):** A key pillar of safe AI in transportation is acknowledging what the system *does not know*. Rather than guessing when information is incomplete, the system actively prompts for missing parameters.

### 7. Counterfactual / "What-if" Comparison (UI Feature)
* **What it tells the user:** In the web interface, users can enter a modified scenario (e.g., changing *"has not received"* to *"signal confirms receipt and coordinates detour"*). The system presents a side-by-side comparison of the decisions.
* **XAI Value (Contrastive Explanation):** Cognitive science shows that humans understand decisions best through contrast (*"Why action A instead of action B?"*). The What-if tool proves that changing a single key fact cleanly flips the dialogue goal from *Information Seeking* to *Deliberation*.

---

## 7. Experimental Verification and Test Results

The codebase includes an automated test and verification suite:

1. **Unit Test Suite (`tests/test_core.py`):**
   * 10 automated test cases verifying schema conformance, record validation, privacy guardrails (ensuring internal case IDs never leak into user-facing outputs), TF-IDF retrieval reproducibility, and model prediction behavior.
   * **Result:** 10 / 10 Tests Passed.

2. **Baseline Development Benchmark (`scripts/evaluate.py`):**
   * Evaluated across 12 author-created diverse transportation test prompts.
   * **Result:** 12 / 12 Agreement on expected dialogue types.

3. **Machine Learning Model Evaluation (`models/training_report_provisional.json`):**
   * Evaluated via 5-Fold Grouped Cross-Validation on 22 draft-labeled cases.
   * **Accuracy:** 50.0% (11 / 22 cases correctly predicted).
   * **Macro F1 Score:** 0.392.
   * **Analysis:** Deliberation, Negotiation, and Persuasion demonstrated positive predictive capability; Information Seeking suffered from low recall due to limited training samples. This empirical outcome reinforces the necessity of the Dual-Engine design.

---

## 8. Step-by-Step Engineering Lifecycle (What Was Done)

To develop this project systematically, the engineering process was divided into nine sequential development milestones:

| Phase | Development Step | Tasks Completed & Deliverables |
| :--- | :--- | :--- |
| **Phase 1** | **Literature & Taxonomy Definition** | Studied Walton's 7 dialogue types and adapted them to vehicular Cyber-Physical Systems (V2V/V2I). Formulated the decision-tree logic based on course reference guidelines. |
| **Phase 2** | **Data Mining & JSON Conversion** | Extracted all 32 unstructured case studies from `Scenarios (1).pdf` into standardized, machine-readable JSON records (`original-01.json` to `original-32.json`). |
| **Phase 3** | **Ontology & Diagram Integration** | Audited the 32 UML class diagrams (`dia/`) to extract domain entities (`Vehicle`, `TrafficSignal`, `Sensor`), establishing participant roles and system boundaries. |
| **Phase 4** | **Label Auditing & Ambiguity Filtering** | Created `data/training_labels_draft.csv`. Filtered out 10 ambiguous/conditional cases from training to prevent false ground-truth bias, leaving 22 clean cases. |
| **Phase 5** | **Core Architecture & Schema Validation** | Developed `src/schema.py` and `src/validate.py` defining strict data contracts (`Answer`, `Decision`) with built-in privacy guardrails against ID leakage. |
| **Phase 6** | **Deterministic Rule Baseline** | Built `src/dialogue_rules.py` containing the transparent decision-tree logic that quotes verbatim input evidence and traces decision branches. |
| **Phase 7** | **Case Retrieval Engine** | Implemented `src/retrieve.py` using TF-IDF vectorization and cosine similarity to index and search historical scenario records offline. |
| **Phase 8** | **Machine Learning Classifier** | Implemented `scripts/train_dialogue_model.py` and `src/trained.py` using scikit-learn (TF-IDF + Logistic Regression), evaluated via 5-fold cross-validation. |
| **Phase 9** | **User Interfaces & Evaluation** | Built the multi-level CLI (`cli.py`), the local web interface (`app.py`), the What-if comparison tool, and automated test suites (`tests/test_core.py`). |

---

## 9. Summary

1. **Structured Data Extraction:** Transcribed 32 complex unstructured scenario cases and ontology concepts from `Scenarios (1).pdf` and UML diagrams into validated JSON records.
2. **Dialogue Taxonomy Formalization:** Applied Walton’s dialogue framework to ITS scenarios, authoring `labeling_guide.md` and curating the 32-case draft labeling matrix.
3. **Dual-Engine Pipeline Implementation:** Built the complete Python core (`src/`), incorporating the deterministic decision tree, TF-IDF case retrieval, and scikit-learn classifier pipeline.
4. **Explainable AI Architecture:** Designed the 7-component inspectable explanation model, emphasizing verbatim evidence quoting, decision path tracing, and missing-variable identification.
5. **Interactive User Interfaces:** Developed both a multi-level command-line tool (`cli.py`) and a local browser dashboard (`app.py`) featuring comparative "What-if" analysis.
6. **Academic Integrity & Limitation Reporting:** Explicitly held out 10 ambiguous cases, separated the 10 proposed cases, and reported honest cross-validation metrics rather than claiming unverified perfection.

---

## 10. Future Work

* **Faculty Label Calibration:** Complete formal faculty review of `data/training_labels_draft.csv` to convert provisional labels into verified ground truth.
* **Dataset Expansion:** Synthesize and annotate additional balanced scenarios across underrepresented classes (Inquiry, Eristics, Information Seeking).
* **V2X Protocol Integration:** Map dialogue outputs directly to standard vehicular messaging payloads (e.g., IEEE 1609.3 / SAE J2735 Basic Safety Messages).
