from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path("governance-runtime/review-trust-kernel/evidence_discovery_broker_v2.py")


def load_module(repo_root):
    spec = importlib.util.spec_from_file_location("evidence_discovery_broker_v2", repo_root / MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DiscoveryTargetBindingV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.m = load_module(cls.repo_root)

    def request(self, target="Is individual Goat + Lot supported?"):
        return self.m.build_discovery_request(
            review_id="L9-M02", decision_target=target,
            candidate_sha="c"*40, base_sha="b"*40,
            query_type="READ_FILE", path="docs/FARMER_MANUAL_QA.md",
            reason="Need current source", allowed_prefixes=["docs"])

    def test_v2_01_target_required(self):
        with self.assertRaises(ValueError):
            self.m.build_discovery_request(review_id="x",decision_target="",candidate_sha="c",base_sha="b",query_type="READ_FILE",path="docs/a",reason="r",allowed_prefixes=["docs"])

    def test_v2_02_target_changes_request_identity(self):
        self.assertNotEqual(self.request("A")["request_sha256"], self.request("B")["request_sha256"])

    def test_v2_03_response_carries_target(self):
        req=self.request(); resp=self.m.materialize_response(req,content="x",source_ref="repo:path@sha")
        self.assertEqual(resp["decision_target"],req["decision_target"])

    def test_v2_04_continuation_carries_target(self):
        req=self.request(); resp=self.m.materialize_response(req,content="x",source_ref="repo:path@sha")
        p=self.m.build_continuation_packet(review_id=req["review_id"],decision_target=req["decision_target"],candidate_sha=req["candidate_sha"],base_sha=req["base_sha"],requests=[req],responses=[resp])
        self.assertEqual(p["decision_target"],req["decision_target"])

    def test_v2_05_target_mismatch_fails_closed(self):
        req=self.request(); resp=self.m.materialize_response(req,content="x",source_ref="repo:path@sha")
        with self.assertRaises(ValueError):
            self.m.build_continuation_packet(review_id=req["review_id"],decision_target="different",candidate_sha=req["candidate_sha"],base_sha=req["base_sha"],requests=[req],responses=[resp])

    def test_v2_06_response_binding_mismatch_fails_closed(self):
        req=self.request(); resp=self.m.materialize_response(req,content="x",source_ref="repo:path@sha"); resp["decision_target"]="tampered"
        with self.assertRaises(ValueError):
            self.m.build_continuation_packet(review_id=req["review_id"],decision_target=req["decision_target"],candidate_sha=req["candidate_sha"],base_sha=req["base_sha"],requests=[req],responses=[resp])


if __name__ == "__main__": unittest.main(verbosity=2)
