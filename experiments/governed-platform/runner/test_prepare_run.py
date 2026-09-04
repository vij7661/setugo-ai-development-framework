import json
import unittest

from prepare_run import prepare, select_mechanism


class PrepareRunTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "case_id": "EXP-B-999",
            "experiment_id": "EXP-B",
            "version": "1.0",
            "risk": "HIGH",
            "artifact_ref": "inline:test",
            "authoritative_intent_ref": "hidden-local:intent/EXP-B-999",
            "invariant_refs": ["INV-HIDDEN"],
            "model_visible": {
                "technical_contract": "visible contract",
                "implementation": "visible implementation",
            },
            "ground_truth_ref": "local-hidden:EXP-B-999.ground-truth.json",
        }
        self.mechanism = {
            "mechanism_id": "r1",
            "kind": "llm",
            "adapter": "runtime",
            "provider": "runtime-provider",
            "model": "runtime-model",
            "role": "independent-reviewer",
            "enabled": True,
            "qualification_ref": "qual-1",
            "privacy_class": "project-nonsecret",
        }

    def test_prepared_envelope_exposes_only_model_visible_case_payload(self):
        envelope = prepare(self.case, self.mechanism, "review-v1")
        serialized = json.dumps(envelope)
        self.assertIn("visible contract", serialized)
        self.assertNotIn("local-hidden:EXP-B-999.ground-truth.json", serialized)
        self.assertNotIn("hidden-local:intent/EXP-B-999", serialized)
        self.assertNotIn("INV-HIDDEN", serialized)

    def test_run_id_is_deterministic_for_same_bound_inputs(self):
        first = prepare(self.case, self.mechanism, "review-v1")
        second = prepare(self.case, self.mechanism, "review-v1")
        self.assertEqual(first["run_id"], second["run_id"])
        self.assertEqual(
            first["case_binding"]["model_visible_sha256"],
            second["case_binding"]["model_visible_sha256"],
        )

    def test_changed_visible_payload_changes_run_binding(self):
        first = prepare(self.case, self.mechanism, "review-v1")
        changed = dict(self.case)
        changed["model_visible"] = dict(self.case["model_visible"])
        changed["model_visible"]["implementation"] = "changed"
        second = prepare(changed, self.mechanism, "review-v1")
        self.assertNotEqual(first["run_id"], second["run_id"])
        self.assertNotEqual(
            first["case_binding"]["model_visible_sha256"],
            second["case_binding"]["model_visible_sha256"],
        )

    def test_case_payload_id_must_match_file_identity_when_supplied(self):
        with self.assertRaisesRegex(ValueError, "case identity mismatch"):
            prepare(
                self.case,
                self.mechanism,
                "review-v1",
                expected_case_id="EXP-B-998",
            )

    def test_disabled_mechanism_is_rejected(self):
        config = {"mechanisms": [{**self.mechanism, "enabled": False}]}
        with self.assertRaises(ValueError):
            select_mechanism(config, "r1")


if __name__ == "__main__":
    unittest.main()
