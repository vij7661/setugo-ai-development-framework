import json
import tempfile
import unittest
from pathlib import Path

from build_exp_g_candidate_bundle import build_bundle


class ExpGCandidateBundleTests(unittest.TestCase):
    def test_all_candidate_results_are_preserved_and_non_authoritative(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case = root / "case.json"
            case.write_text(json.dumps({"case_id": "EXP-C-001", "prompt": "x"}), encoding="utf-8")
            results = []
            for provider, mechanism, status in [
                ("groq", "a", "SUCCESS"),
                ("openrouter", "b", "FAILED"),
                ("mistral", "c", "SUCCESS"),
                ("gemini", "d", "SUCCESS"),
            ]:
                p = root / f"{provider}.json"
                p.write_text(json.dumps({
                    "provider": provider,
                    "model": f"{provider}-model",
                    "mechanism_id": mechanism,
                    "status": status,
                    "review": {"decision": "PASS"},
                }), encoding="utf-8")
                results.append(str(p))
            bundle = build_bundle(str(case), results, "sha1", "123")
            self.assertEqual(4, bundle["candidate_count"])
            self.assertFalse(bundle["authority"]["candidate_outputs_authoritative"])
            self.assertTrue(all(not c["evidence_eligible"] for c in bundle["candidates"]))
            self.assertTrue(all(c["governance_authority"] == "NONE" for c in bundle["candidates"]))
            self.assertTrue(all(c["qualification_use"] == "CANDIDATE_EVIDENCE_ONLY" for c in bundle["candidates"]))

    def test_bundle_hash_is_deterministic_for_same_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case = root / "case.json"
            result = root / "result.json"
            case.write_text(json.dumps({"case_id": "EXP-C-001"}), encoding="utf-8")
            result.write_text(json.dumps({"provider": "groq", "status": "SUCCESS"}), encoding="utf-8")
            a = build_bundle(str(case), [str(result)], "sha1", "123")
            b = build_bundle(str(case), [str(result)], "sha1", "123")
            self.assertEqual(a["bundle_sha256"], b["bundle_sha256"])

    def test_candidate_agreement_cannot_become_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            case = root / "case.json"
            case.write_text(json.dumps({"case_id": "EXP-C-001"}), encoding="utf-8")
            results = []
            for provider in ["groq", "gemini"]:
                p = root / f"{provider}.json"
                p.write_text(json.dumps({"provider": provider, "status": "SUCCESS", "review": {"decision": "PASS"}}), encoding="utf-8")
                results.append(str(p))
            bundle = build_bundle(str(case), results, "sha1", "123")
            self.assertFalse(bundle["authority"]["candidate_outputs_may_approve_or_release"])


if __name__ == "__main__":
    unittest.main()
