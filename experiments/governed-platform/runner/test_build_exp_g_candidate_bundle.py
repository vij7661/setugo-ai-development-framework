import json
import tempfile
import unittest
from pathlib import Path

from build_exp_g_candidate_bundle import build_bundle


class ExpGCandidateBundleTests(unittest.TestCase):
    def _case(self, root):
        case = root / "case.json"
        case.write_text(json.dumps({
            "case_id": "EXP-C-001",
            "experiment_id": "EXP-C",
            "version": "1.0",
            "risk": "HIGH",
            "artifact_ref": "inline:test",
            "authoritative_intent_ref": "hidden:intent",
            "invariant_refs": ["hidden:inv"],
            "ground_truth_ref": "local-hidden:truth",
            "model_visible": {"contract": "visible contract", "task": "review"},
        }), encoding="utf-8")
        return case

    def test_all_candidate_results_are_preserved_and_non_authoritative(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case = self._case(root)
            results = []
            for provider, mechanism, status in [
                ("groq", "a", "PASS"),
                ("openrouter", "b", "PASS"),
                ("mistral", "c", "ERROR"),
                ("gemini", "d", "PASS"),
            ]:
                p = root / f"{provider}.json"
                p.write_text(json.dumps({
                    "provider": provider,
                    "mechanism_version": f"{provider}-model",
                    "mechanism_id": mechanism,
                    "status": status,
                    "runtime_metadata": {
                        "completion_complete": status == "PASS",
                        "error_type": "RuntimeError" if status == "ERROR" else None,
                        "error": "rate limited" if status == "ERROR" else None,
                    },
                }), encoding="utf-8")
                results.append(str(p))
            bundle = build_bundle(str(case), results, "sha1", "123")
            self.assertEqual(4, bundle["candidate_count"])
            self.assertFalse(bundle["authority"]["candidate_outputs_authoritative"])
            self.assertTrue(all(not c["evidence_eligible"] for c in bundle["candidates"]))
            self.assertTrue(all(c["governance_authority"] == "NONE" for c in bundle["candidates"]))
            self.assertTrue(all(c["qualification_use"] == "CANDIDATE_EVIDENCE_ONLY" for c in bundle["candidates"]))
            mistral = next(c for c in bundle["candidates"] if c["provider"] == "mistral")
            self.assertEqual("ERROR", mistral["execution_status"])
            self.assertEqual("rate limited", mistral["error"])

    def test_review_bundle_excludes_protected_case_references(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case = self._case(root)
            result = root / "result.json"
            result.write_text(json.dumps({"provider": "groq", "mechanism_version": "m", "status": "PASS"}), encoding="utf-8")
            bundle = build_bundle(str(case), [str(result)], "sha1", "123")
            encoded = json.dumps(bundle["review_case"])
            self.assertNotIn("ground_truth_ref", encoded)
            self.assertNotIn("authoritative_intent_ref", encoded)
            self.assertNotIn("invariant_refs", encoded)
            self.assertEqual({"contract": "visible contract", "task": "review"}, bundle["review_case"]["model_visible"])
            self.assertFalse(bundle["blinding"]["protected_ground_truth_included"])

    def test_bundle_hash_is_deterministic_for_same_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case = self._case(root)
            result = root / "result.json"
            result.write_text(json.dumps({"provider": "groq", "mechanism_version": "m", "status": "PASS"}), encoding="utf-8")
            a = build_bundle(str(case), [str(result)], "sha1", "123")
            b = build_bundle(str(case), [str(result)], "sha1", "123")
            self.assertEqual(a["bundle_sha256"], b["bundle_sha256"])

    def test_candidate_agreement_cannot_become_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case = self._case(root)
            results = []
            for provider in ["groq", "gemini"]:
                p = root / f"{provider}.json"
                p.write_text(json.dumps({"provider": provider, "mechanism_version": provider + "-model", "status": "PASS"}), encoding="utf-8")
                results.append(str(p))
            bundle = build_bundle(str(case), results, "sha1", "123")
            self.assertFalse(bundle["authority"]["candidate_outputs_may_approve_or_release"])


if __name__ == "__main__":
    unittest.main()
