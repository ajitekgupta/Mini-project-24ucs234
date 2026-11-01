# Dialogue Labeling Guide

This guide defines the operational decision logic and categorization framework for classifying communication goals in Intelligent Transportation Systems (ITS), based on Walton and Krabbe's dialogue typology.

## Communication Goal Framework

1. **Disagreement or Conflict between Participants:**
   - If resolving a disagreement about a factual claim or observation: **Persuasion**.
   - If settling competing interests (e.g., resource or space allocation): **Negotiation**.
   - If the interaction is uncooperative or adversarial without consensus seeking: **Eristics**.
2. **Shared Common Problem (No Conflict):**
   - If jointly investigating uncertain facts to establish truth: **Inquiry**.
   - If coordinating a shared decision or action plan: **Deliberation**.
3. **Information Asymmetry:**
   - If one participant requests knowledge or verification that another possesses: **Information Seeking**.
4. **Multi-Stage Interaction:**
   - If the exchange transitions through successive objectives (e.g., verifying a hazard report, then coordinating a detour): **Mixed**.
5. **Insufficient Information:**
   - If the scenario description lacks sufficient communicative intent or facts: **Unclear**.

*Note on Domain Semantics:* In traffic systems, the term "conflict" often refers to a physical roadway hazard or merge point. In this communication typology, it refers specifically to the *dialogue relationship* between participants.

## Reference Scenarios and Classifications

| Traffic Situation | Candidate Dialogue Type | Classification Rationale |
| :--- | :--- | :--- |
| A signal has not received a vehicle's hazard report. | **Information Seeking** | An acknowledgment and unconfirmed transmission must be verified. |
| Participants confirm a lane is blocked and coordinate detour warnings. | **Deliberation** | Entities share a common problem and agree on a joint action plan. |
| Two vehicles arrive simultaneously at a single available parking space. | **Negotiation** | Entities have competing priorities and seek a fair allocation. |
| Two roadside sensors report conflicting obstacle detections. | **Inquiry** | Entities compare independent evidence to establish ground truth. |
| A vehicle transmits sensor telemetry to prove an obstruction report is valid. | **Persuasion** | The goal is to resolve disagreement regarding an unverified claim. |
| Initial report verification followed by traffic rerouting coordination. | **Mixed** | Transitions from Information Seeking to Deliberation. |

## Annotation and Explainability Requirements

For each scenario evaluated by the system:
1. **Quoted Evidence:** The classification must quote verbatim phrases from the input prompt.
2. **Identified Participants:** Active communicating entities must be explicitly recognized.
3. **Traceable Decision Path:** The sequence of logic steps must be surfaced to the user.
4. **Epistemic Uncertainty:** Missing parameters or unverified conditions must be explicitly highlighted.
