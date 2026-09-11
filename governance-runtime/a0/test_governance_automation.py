import base64
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("governance_automation.py")
spec = importlib.util.spec_from_file_location("governance_automation", MODULE_PATH)
ga = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(ga)


def sample_manifest():
    return {
        "schema_version": 1,
        "phase": "PRODUCTION_QUALIFICATION",
        "repository": "vij7661/setugo-ai-development-framework",
        "authoritative_source_sha": "1" * 40,
        "candidate_sha": "2" * 40,
        "checker_sha": "3" * 40,
        "policy_id": "QUALIFICATION_BOUNDARY_OWNERSHIP",
        "policy_version": 7,
        "policy_hash": "4" * 64,
        "required_checks": ["check-a", "check-b"],
        "required_review_type": "MANUAL_INDEPENDENT_REVIEW",
        "authority_required": True,
        "environment": "production-candidate",
        "artifact_digest": "sha256:" + "5" * 64,
        "known_reds": [{"id": "RED-1"}],
        "open_findings": [],
        "next_action": "REQUEST_MANUAL_REVIEW",
    }


class ManifestTests(unittest.TestCase):
    def test_valid_manifest(self):
        m = sample_manifest()
        self.assertIs(ga.validate_manifest(m), m)
        self.assertEqual(len(ga.manifest_digest(m)), 64)

    def test_wrong_policy_hash_fails(self):
        m = sample_manifest()
        m["policy_hash"] = "bad"
        with self.assertRaises(ga.GovernanceError):
            ga.validate_manifest(m)

    def test_extra_field_fails(self):
        m = sample_manifest()
        m["assistant_says_pass"] = True
        with self.assertRaises(ga.GovernanceError):
            ga.validate_manifest(m)

    def test_duplicate_checks_fail(self):
        m = sample_manifest()
        m["required_checks"] = ["check-a", "check-a"]
        with self.assertRaises(ga.GovernanceError):
            ga.validate_manifest(m)


class EvidenceTests(unittest.TestCase):
    def test_duplicate_evidence_fails(self):
        ref = "sha256:" + "a" * 64
        with self.assertRaises(ga.GovernanceError):
            ga.validate_evidence_records([{"evidence_ref": ref}, {"evidence_ref": ref}])

    def test_signature_invalid_base64_fails(self):
        with self.assertRaises(ga.GovernanceError):
            ga.validate_signature_b64("not@@base64")

    def test_signature_wrong_length_fails(self):
        text = base64.b64encode(b"short").decode("ascii")
        with self.assertRaises(ga.GovernanceError):
            ga.validate_signature_b64(text)

    def test_signature_64_bytes_passes_shape_only(self):
        raw = b"x" * 64
        self.assertEqual(ga.validate_signature_b64(base64.b64encode(raw).decode("ascii")), raw)

    def test_attestation_requires_hash_bound_evidence(self):
        with self.assertRaises(ga.GovernanceError):
            ga.build_unsigned_attestation(
                sample_manifest(),
                authority_class="HUMAN_RELEASE_AUTHORITY",
                decision_scope="TERMINAL_ACTION:PRODUCTION:PROMOTE",
                evidence_ref="conversation:looks-good",
                trust_root_id="ROOT_V1",
            )

    def test_no_signing_capability_exists(self):
        forbidden = {"sign", "sign_attestation", "mint_authority", "private_key"}
        exported = set(dir(ga))
        self.assertTrue(forbidden.isdisjoint(exported))


class ReadinessTests(unittest.TestCase):
    def test_manual_review_blocks(self):
        report = ga.readiness_report(
            sample_manifest(),
            checks={"check-a": "SUCCESS", "check-b": "SUCCESS"},
            review_state="NOT_PERFORMED",
            authority_state="VERIFIED",
        )
        self.assertFalse(report["ready"])
        self.assertTrue(any(x["type"] == "MANUAL_REVIEW_NOT_VERIFIED" for x in report["blockers"]))

    def test_authority_blocks(self):
        report = ga.readiness_report(
            sample_manifest(),
            checks={"check-a": "SUCCESS", "check-b": "SUCCESS"},
            review_state="VERIFIED_PASS",
            authority_state="ABSENT",
        )
        self.assertFalse(report["ready"])
        self.assertTrue(any(x["type"] == "HUMAN_AUTHORITY_NOT_VERIFIED" for x in report["blockers"]))

    def test_missing_check_blocks(self):
        report = ga.readiness_report(
            sample_manifest(),
            checks={"check-a": "SUCCESS"},
            review_state="VERIFIED_PASS",
            authority_state="VERIFIED",
        )
        self.assertFalse(report["ready"])
        self.assertTrue(any(x["type"] == "CHECKS_NOT_GREEN" for x in report["blockers"]))

    def test_known_red_history_is_counted(self):
        report = ga.readiness_report(
            sample_manifest(),
            checks={"check-a": "SUCCESS", "check-b": "SUCCESS"},
            review_state="VERIFIED_PASS",
            authority_state="VERIFIED",
            last_red={"id": "RED-1"},
        )
        self.assertEqual(report["known_red_count"], 1)
        self.assertEqual(report["last_red"], {"id": "RED-1"})
        self.assertTrue(report["ready"])


class PRLifecycleTests(unittest.TestCase):
    def test_superseded_wins(self):
        self.assertEqual(
            ga.classify_pr(merged=False, open_state=True, draft=False, review_required=False, review_satisfied=False, superseded=True, historical_only=False),
            "SUPERSEDED",
        )

    def test_review_pending(self):
        self.assertEqual(
            ga.classify_pr(merged=False, open_state=True, draft=True, review_required=True, review_satisfied=False, superseded=False, historical_only=False),
            "REVIEW_PENDING",
        )


class PreflightTests(unittest.TestCase):
    def _repo(self):
        td = tempfile.TemporaryDirectory()
        repo = Path(td.name)
        subprocess.run(["git", "init", "-b", "candidate"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "a0@example.invalid"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "A0 Test"], cwd=repo, check=True)
        (repo / "x.txt").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "base"], cwd=repo, check=True, capture_output=True)
        base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
        (repo / "x.txt").write_text("candidate\n", encoding="utf-8")
        subprocess.run(["git", "commit", "-am", "candidate"], cwd=repo, check=True, capture_output=True)
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
        return td, repo, base, head

    def test_preflight_pass(self):
        td, repo, base, head = self._repo()
        self.addCleanup(td.cleanup)
        m = sample_manifest()
        m["authoritative_source_sha"] = base
        m["candidate_sha"] = head
        result = ga.preflight(repo, m, expected_branch="candidate")
        self.assertEqual(result["result"], "PREFLIGHT_PASS")

    def test_stale_candidate_fails(self):
        td, repo, base, head = self._repo()
        self.addCleanup(td.cleanup)
        m = sample_manifest()
        m["authoritative_source_sha"] = base
        m["candidate_sha"] = base
        with self.assertRaises(ga.GovernanceError):
            ga.preflight(repo, m, expected_branch="candidate")

    def test_wrong_branch_fails(self):
        td, repo, base, head = self._repo()
        self.addCleanup(td.cleanup)
        m = sample_manifest()
        m["authoritative_source_sha"] = base
        m["candidate_sha"] = head
        with self.assertRaises(ga.GovernanceError):
            ga.preflight(repo, m, expected_branch="phase/production")


if __name__ == "__main__":
    unittest.main(verbosity=2)
