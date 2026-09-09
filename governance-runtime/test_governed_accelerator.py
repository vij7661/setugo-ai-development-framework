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


class GovernedAcceleratorTests(unittest.TestCase):
    def run_cli(self, *args: str):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, text=True, capture_output=True)

    def test_acc01_status_exact_head_can_be_checked(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        p = self.run_cli("status", "--expected-sha", head)
        self.assertEqual(0, p.returncode, p.stderr)
        body = json.loads(p.stdout)
        self.assertTrue(body["head_match"])
        self.assertIn("stop_condition", body)
        self.assertFalse(body["promotion_authority_granted"])

    def test_acc01_status_mismatch_fails_closed(self):
        p = self.run_cli("status", "--expected-sha", "0" * 40)
        self.assertEqual(2, p.returncode)
        self.assertFalse(json.loads(p.stdout)["head_match"])

    def test_acc03_full_packet_embeds_and_hashes_files(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        with tempfile.TemporaryDirectory() as td:
            m = Path(td) / "m.json"
            out = Path(td) / "packet.json"
            m.write_text(json.dumps({"candidate_sha": head, "required_files": ["governance-runtime/governed_accelerator.py"], "mandatory_dimensions": ["d1"]}))
            p = self.run_cli("packet", "--manifest", str(m), "--output", str(out), "--mode", "full")
            self.assertEqual(0, p.returncode, p.stderr)
            body = json.loads(out.read_text())
            self.assertEqual(head, body["candidate_sha"])
            self.assertEqual(64, len(body["artifacts"][0]["sha256"]))
            self.assertFalse(body["promotion_authority_granted"])

    def test_acc04_missing_required_file_fails(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        with tempfile.TemporaryDirectory() as td:
            m = Path(td) / "m.json"
            m.write_text(json.dumps({"candidate_sha": head, "required_files": ["NO-SUCH-FILE"]}))
            p = self.run_cli("packet", "--manifest", str(m), "--output", str(Path(td)/"x.json"))
            self.assertEqual(2, p.returncode)

    def test_acc05_delta_requires_prior_binding(self):
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        with tempfile.TemporaryDirectory() as td:
            m = Path(td) / "m.json"
            m.write_text(json.dumps({"candidate_sha": head, "required_files": ["governance-runtime/governed_accelerator.py"]}))
            p = self.run_cli("packet", "--manifest", str(m), "--output", str(Path(td)/"x.json"), "--mode", "delta")
            self.assertEqual(2, p.returncode)

    def test_acc07_ingest_wrong_candidate_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td) / "r.json"
            r.write_text(json.dumps({"reviewed_artifact_commit": "1"*40, "review_coverage": []}))
            p = self.run_cli("ingest", "--review", str(r), "--candidate-sha", "2"*40)
            self.assertEqual(2, p.returncode)

    def test_acc08_ingest_duplicate_or_missing_dimensions_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td) / "r.json"
            r.write_text(json.dumps({"reviewed_artifact_commit": "2"*40, "review_coverage": [{"dimension_id":"d1","evidence":"x"},{"dimension_id":"d1","evidence":"x"}]}))
            p = self.run_cli("ingest", "--review", str(r), "--candidate-sha", "2"*40, "--dimension", "d1")
            self.assertEqual(2, p.returncode)

    def test_acc09_pass_remains_non_authoritative(self):
        with tempfile.TemporaryDirectory() as td:
            r = Path(td) / "r.json"
            r.write_text(json.dumps({"reviewed_artifact_commit": "2"*40, "disposition":"PASS", "findings":[], "review_coverage": [{"dimension_id":"d1","evidence":"direct evidence"}]}))
            p = self.run_cli("ingest", "--review", str(r), "--candidate-sha", "2"*40, "--dimension", "d1")
            self.assertEqual(0, p.returncode, p.stderr)
            body = json.loads(p.stdout)
            self.assertFalse(body["counts_for_promotion"])
            self.assertTrue(body["requires_deterministic_adjudication"])


if __name__ == "__main__":
    unittest.main()
