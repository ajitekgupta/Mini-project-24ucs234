from __future__ import annotations

import json
import io
import unittest
from pathlib import Path
from unittest.mock import patch

from src.data import ROOT, load_records
from src.pipeline import answer_scenario
from src.retrieve import Retriever
from src.validate import has_private_reference, validate_record


class CoreTests(unittest.TestCase):
    def test_source_coverage_and_provenance(self):
        originals = load_records()
        self.assertEqual(len(originals), 32)
        self.assertEqual([r["number"] for r in originals], list(range(1, 33)))
        self.assertTrue(all(r["origin"] == "original_report" and not validate_record(r) for r in originals))
        self.assertTrue(all(r["review_status"] == "machine_extracted_needs_review" for r in originals))

    def test_proposed_data_is_separate(self):
        records = load_records(include_proposed=True)
        self.assertEqual(len(records), 42)
        self.assertEqual(sum(r["origin"] == "proposed_addition" for r in records), 10)

    def test_retrieval_of_distinct_topics(self):
        retriever = Retriever(load_records())
        obstruction = retriever.search("vehicle detects an obstruction blocking the road")
        railway = retriever.search("train crossing closes and traffic must wait")
        self.assertIn(obstruction[0][0]["number"], {2, 3, 4})
        self.assertEqual(railway[0][0]["number"], 11)

    def test_counterfactual_changes_type(self):
        first = answer_scenario("A vehicle reports an obstruction, but the signal has not received the report.")
        second = answer_scenario("The signal confirms the obstruction report. They decide how to coordinate warnings.")
        self.assertEqual(first.dialogue_type, "information seeking")
        self.assertEqual(second.dialogue_type, "deliberation")

    def test_two_vehicle_roles_are_distinct(self):
        answer = answer_scenario("Two vehicles both want the same parking space and need to settle who may use it first.")
        self.assertEqual(answer.participants, ["Vehicle 1", "Vehicle 2"])
        self.assertEqual(answer.dialogue_type, "negotiation")

    def test_evidence_and_privacy(self):
        prompt = "Two sensors give contradictory reports. Operators investigate which is accurate."
        answer = answer_scenario(prompt)
        self.assertTrue(all(item in prompt for item in answer.evidence))
        self.assertFalse(has_private_reference(str(answer.public_dict())))
        self.assertIn("retrieved", answer.audit)
        self.assertNotIn("audit", answer.public_dict())

    def test_empty_input_rejected(self):
        with self.assertRaises(ValueError):
            answer_scenario("   ")

    def test_model_adapter_contract_with_mock_response(self):
        result = {"output": [{"content": [{"type": "output_text", "text": json.dumps({
            "dialogue": [
                {"speaker": "Vehicle or driver", "text": "Can you confirm receipt of my report?"},
                {"speaker": "Traffic signal", "text": "I will check whether it arrived."},
            ]})}]}]}
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-only", "OPENAI_MODEL": "test-model"}):
            with patch("urllib.request.urlopen", return_value=io.BytesIO(json.dumps(result).encode())):
                answer = answer_scenario("A vehicle reports an obstruction, but the traffic signal has not received it.", mode="model")
        self.assertEqual(answer.mode, "model")
        self.assertEqual(answer.dialogue[0]["speaker"], "Vehicle or driver")

    def test_model_mode_falls_back_without_credentials(self):
        with patch.dict("os.environ", {"OPENAI_API_KEY": "", "OPENAI_MODEL": ""}):
            answer = answer_scenario("A vehicle asks the signal to confirm receipt.", mode="model")
        self.assertIn("baseline", answer.mode)
        self.assertEqual(len(answer.dialogue), 2)

    def test_trained_mode_uses_model_trace(self):
        try:
            import sklearn  # noqa: F401
        except ImportError:
            self.skipTest("Training dependencies are optional")
        if not (ROOT / "models" / "dialogue_classifier_provisional.joblib").exists():
            self.skipTest("Build the provisional model first")
        answer = answer_scenario("A vehicle asks a signal whether it received a parking report.", mode="trained")
        self.assertIn(answer.dialogue_type, {"negotiation", "deliberation", "information seeking", "persuasion"})
        self.assertIn("TF-IDF", " ".join(answer.decision_path))
        self.assertIn("not proof", answer.explanation)
        self.assertTrue(all(item in answer.summary for item in answer.evidence))
        self.assertNotIn("audit", answer.public_dict())


if __name__ == "__main__":
    unittest.main()
