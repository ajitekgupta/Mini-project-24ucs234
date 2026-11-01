# Source Dataset Audit

Summary of dataset assets, ontology models, and extraction status:

- **Primary Scenario Report:** `Scenarios (1).pdf` (42 pages, 32 numbered scenario cases).
- **Ontology Class Diagrams:** 32 UML diagrams (`dia/scenario1.png` to `scenario32.png`) defining domain entities (`Vehicle`, `TrafficSignal`, `RoadNetwork`, `Sensor`) and communication boundaries.
- **Dialogue Typology Reference:** Formalized taxonomy based on Walton and Krabbe's dialogue classifications, documented in `data/labeling_guide.md`.
- **Extension Scenarios (Cases 33–42):** 10 newly authored scenarios with complete PEAS parameters, communicative solutions, cascading problems, and reviewed UML class diagrams, compiled in `docs/Scenarios_and_Diagrams_33_42.pdf` and stored in `data/proposed_scenarios/`.
- **Structured JSON Conversion:** 32 primary JSON files in `data/scenarios/` storing parsed situation text, entity roles, communication types, and known facts.
- **Label Annotation Matrix:** 22 clean cases annotated across 4 primary categories (Deliberation, Information Seeking, Negotiation, Persuasion); 10 ambiguous cases flagged and held out from model training pending ground-truth calibration.
- **Extraction Audit:** Field coverage and schema compliance are verified programmatically via `scripts/audit_sources.py`.
