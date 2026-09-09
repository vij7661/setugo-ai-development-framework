from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = HERE / "governed_accelerator.py"


def manifest(head: str, *, phase: str = "TESTING") -> dict:
    return {
        "candidate_sha": head,
        "phase": phase,
        "required_files": ["governance-runtime/governed_accelerator.py"],
        "review_scope": ["bounded implementation and falsification quality"],
        "mandatory_dimensions": ["d1"],
        "explicit_nonclaims": ["production readiness"],
        "out_of_scope_dimensions": ["production IAM"],
        "allowed_evidence": ["embedded artifacts", "exact-head test evidence"],
    }


class GovernedAcceleratorTests(unittest.TestCase):
    def run_cli(self, *args: str):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, text=True, capture_output=True)

    def test_acc01_status_exact_head_can_be_checked(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        p = self.run_cli("status", "--expected-sha", head, "--phase", "TESTING")
        self.assertEqual(0, p.returncode, p.stderr)
        body = json.loads(p.stdout)
        self.assertTrue(body["head_match"])
        self.assertEqual("TESTING", body["phase"])
        self.assertIn("stop_condition", body)
        self.assertFalse(body["promotion_authority_granted"])

    def test_acc01_status_mismatch_fails_closed(self):
        p = self.run_cli("status", "--expected-sha", "0" * 40)
        self.assertEqual(2, p.returncode)
        self.assertFalse(json.loads(p.stdout)["head_match"])

    def test_acc03_testing_packet_is_phase_explicit_and_manual_default(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        with tempfile.TemporaryDirectory() as td:
            m = Path(td) / "m.json"
            out = Path(td) / "packet.json"
            m.write_text(json.dumps(manifest(head)))
            p = self.run_cli("packet", "--manifest", str(m), "--output", str(out), "--mode", "full")
            self.assertEqual(0, p.returncode, p.stderr)
            body = json.loads(out.read_text())
            self.assertEqual(head, body["candidate_sha"])
            self.assertEqual("TESTING", body["review_phase"])
            self.assertEqual("MANUAL", body["review_boundary"]["review_transport_policy"]["default_transport"])
            self.assertFalse(body["review_boundary"]["review_transport_policy"]["external_api_allowed"])
            self.assertIn("not a production-readiness review", body["review_boundary"]["reviewer_instruction"])
            self.assertEqual(64, len(body["artifacts"][0]["sha256"]))
            self.assertFalse(body["production_readiness_claimed"])

    def test_acc03b_testing_api_allowed_only_when_explicitly_justified(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        with tempfile.TemporaryDirectory() as td:
            m = manifest(head)
            m["api_boundary_under_test"] = True
            mp = Path(td) / "m.json"; out = Path(td) / "p.json"
            mp.write_text(json.dumps(m))
            p = self.run_cli("packet", "--manifest", str(mp), "--output", str(out))
            self.assertEqual(0, p.returncode, p.stderr)
            body = json.loads(out.read_text())
            self.assertTrue(body["review_boundary"]["review_transport_policy"]["external_api_allowed"])
            self.assertFalse(body["review_boundary"]["review_transport_policy"]["automatic_api_dispatch"])

    def test_acc04_missing_required_file_fails(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        with tempfile.TemporaryDirectory() as td:
            m = manifest(head); m["required_files"] = ["NO-SUCH-FILE"]
            mp = Path(td) / "m.json"; mp.write_text(json.dumps(m))
            p = self.run_cli("packet", "--manifest", str(mp), "--output", str(Path(td)/"x.json"))
            self.assertEqual(2, p.returncode)

    def test_acc05_delta_requires_prior_binding(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        with tempfile.TemporaryDirectory() as td:
            m = Path(td) / "m.json"; m.write_text(json.dumps(manifest(head)))
            p = self.run_cli("packet", "--manifest", str(m), "--output", str(Path(td)/"x.json"), "--mode", "delta")
            self.assertEqual(2, p.returncode)

    def test_acc07_ingest_wrong_candidate_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td) / "r.json"
            r.write_text(json.dumps({"reviewed_artifact_commit": "1"*40, "review_phase":"TESTING", "review_coverage": []}))
            p = self.run_cli("ingest", "--review", str(r), "--candidate-sha", "2"*40, "--phase", "TESTING")
            self.assertEqual(2, p.returncode)

    def test_acc08_ingest_duplicate_or_missing_dimensions_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td) / "r.json"
            r.write_text(json.dumps({"reviewed_artifact_commit": "2"*40, "review_phase":"TESTING", "review_coverage": [{"dimension_id":"d1","evidence":"x"},{"dimension_id":"d1","evidence":"x"}]}))
            p = self.run_cli("ingest", "--review", str(r), "--candidate-sha", "2"*40, "--phase", "TESTING", "--dimension", "d1")
            self.assertEqual(2, p.returncode)

    def test_acc09_testing_pass_remains_evidence_and_findings_need_adjudication(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td) / "r.json"
            r.write_text(json.dumps({
                "reviewed_artifact_commit": "2"*40,
                "review_phase":"TESTING",
                "disposition":"PASS",
                "findings":[{"finding_id":"F1","finding_phase":"PRODUCTION","violates_current_contract":False}],
                "review_coverage": [{"dimension_id":"d1","evidence":"direct evidence"}],
            }))
            p = self.run_cli("ingest", "--review", str(r), "--candidate-sha", "2"*40, "--phase", "TESTING", "--dimension", "d1")
            self.assertEqual(0, p.returncode, p.stderr)
            body = json.loads(p.stdout)
            self.assertFalse(body["counts_for_production_qualification"])
            self.assertTrue(body["requires_deterministic_adjudication"])
            self.assertFalse(body["raw_findings_promoted_to_governance_rules"])
            self.assertEqual(1, body["deferred_to_production"])
            self.assertEqual("DEFERRED_TO_PRODUCTION", body["adjudication_queue"][0]["phase_classification"])

    def test_acc10_review_phase_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td) / "r.json"
            r.write_text(json.dumps({"reviewed_artifact_commit":"2"*40,"review_phase":"PRODUCTION","review_coverage":[{"dimension_id":"d1","evidence":"x"}]}))
            p = self.run_cli("ingest", "--review", str(r), "--candidate-sha", "2"*40, "--phase", "TESTING", "--dimension", "d1")
            self.assertEqual(2, p.returncode)

    def test_acc11_promotion_must_be_adjacent_and_exact_sha(self):
        sha = "3" * 40
        p = self.run_cli(
            "promote-check",
            "--source-phase", "TESTING", "--destination-phase", "RELEASE",
            "--source-branch", "phase/testing", "--destination-branch", "phase/release",
            "--source-sha", sha, "--qualified-sha", sha,
            "--evidence-ref", "test-evidence", "--decision-ref", "decision-1",
        )
        self.assertEqual(0, p.returncode, p.stderr)
        body = json.loads(p.stdout)
        self.assertTrue(body["promotion_direction_valid"])
        self.assertFalse(body["raw_reviewer_findings_forwarded_as_rules"])

        bad = self.run_cli(
            "promote-check",
            "--source-phase", "TESTING", "--destination-phase", "PRODUCTION",
            "--source-branch", "phase/testing", "--destination-branch", "phase/production",
            "--source-sha", sha, "--qualified-sha", sha,
            "--evidence-ref", "x", "--decision-ref", "y",
        )
        self.assertNotEqual(0, bad.returncode)

    def test_acc12_testing_pass_definition_is_not_production_ready(self):
        p = self.run_cli("testing-pass-requirements")
        self.assertEqual(0, p.returncode, p.stderr)
        body = json.loads(p.stdout)
        self.assertEqual("READY_TO_BEGIN_RELEASE_QUALIFICATION", body["means"])
        self.assertEqual("PRODUCTION_READY", body["does_not_mean"])


if __name__ == "__main__":
    unittest.main()
