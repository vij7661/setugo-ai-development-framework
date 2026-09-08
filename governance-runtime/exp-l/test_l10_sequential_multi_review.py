from __future__ import annotations

import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path

MODULE_PATH = Path("governance-runtime/review-trust-kernel/sequential_review_v1.py")


def load_module(repo_root):
    spec = importlib.util.spec_from_file_location("sequential_review_v1", repo_root / MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SequentialMultiReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.m = load_module(cls.repo_root)

    def setUp(self):
        self.request = {
            "review_request_id": "RR-L10-001",
            "subject": "material governance transition",
        }
        self.packet = {
            "candidate_sha": "c" * 40,
            "base_sha": "b" * 40,
            "evidence_manifest_hash": "sha256:" + "1" * 64,
            "corpus_hash": "sha256:" + "2" * 64,
            "evidence_ids": ["E1", "E2"],
        }
        self.r2_pass = {
            "review_id": "R2-001",
            "disposition": "PASS",
            "findings": [],
            "evidence_ids": ["E1", "E2"],
            "uncertainties": [],
        }
        self.r2_fail = {
            "review_id": "R2-002",
            "disposition": "CHANGES_REQUIRED",
            "findings": [{"id": "F1", "severity": "HIGH"}],
            "evidence_ids": ["E1"],
            "uncertainties": ["missing corroboration"],
        }

    def test_l10_01_high_risk_pass_still_requires_r3(self):
        policy = {"risk_class": "TRUST_KERNEL", "promotion_authoritative": False}
        self.assertTrue(self.m.requires_r3(policy, self.r2_pass))

    def test_l10_02_high_risk_fail_still_requires_r3(self):
        policy = {"risk_class": "PROMOTION_AUTHORITY", "promotion_authoritative": True}
        self.assertTrue(self.m.requires_r3(policy, self.r2_fail))

    def test_l10_03_policy_required_dual_review_routes_r3(self):
        policy = {"risk_class": "LOW", "policy_requires_dual_review": True}
        self.assertTrue(self.m.requires_r3(policy, self.r2_pass))

    def test_l10_04_low_risk_without_trigger_may_stop_after_r2(self):
        policy = {"risk_class": "LOW", "policy_requires_dual_review": False}
        self.assertFalse(self.m.requires_r3(policy, self.r2_pass))

    def test_l10_05_normalized_handoff_is_byte_deterministic(self):
        a = dict(self.r2_fail)
        b = {k: self.r2_fail[k] for k in reversed(list(self.r2_fail.keys()))}
        self.assertEqual(self.m.normalize_r2_result(a), self.m.normalize_r2_result(b))
        self.assertEqual(
            self.m.sha256_json(self.m.normalize_r2_result(a)),
            self.m.sha256_json(self.m.normalize_r2_result(b)),
        )

    def test_l10_06_all_raw_material_fields_survive_normalization(self):
        normalized = self.m.normalize_r2_result(self.r2_fail)
        self.assertEqual(set(normalized.keys()), set(self.r2_fail.keys()))
        self.assertEqual(normalized["findings"], self.r2_fail["findings"])
        self.assertEqual(normalized["uncertainties"], self.r2_fail["uncertainties"])

    def test_l10_07_mutated_frozen_packet_is_rejected(self):
        policy = {"risk_class": "TRUST_KERNEL"}
        handoff = self.m.build_frozen_handoff(
            review_request=self.request,
            frozen_packet=self.packet,
            policy=policy,
            r2_result=self.r2_pass,
        )
        mutated = deepcopy(self.packet)
        mutated["corpus_hash"] = "sha256:" + "9" * 64
        self.assertFalse(
            self.m.verify_frozen_handoff(
                handoff,
                review_request=self.request,
                frozen_packet=mutated,
                policy=policy,
                r2_result=self.r2_pass,
            )
        )

    def test_l10_08_handoff_binds_request_evidence_and_r2_hashes(self):
        policy = {"risk_class": "TRUST_KERNEL"}
        handoff = self.m.build_frozen_handoff(
            review_request=self.request,
            frozen_packet=self.packet,
            policy=policy,
            r2_result=self.r2_fail,
        )
        self.assertEqual(handoff["review_request_hash"], self.m.sha256_json(self.request))
        self.assertEqual(handoff["frozen_packet_hash"], self.m.sha256_json(self.packet))
        self.assertEqual(handoff["r2_raw_hash"], self.m.sha256_json(self.r2_fail))
        self.assertEqual(handoff["r2_normalized_hash"], self.m.sha256_json(handoff["r2_normalized"]))

    def test_l10_09_r1_middle_opinion_field_is_forbidden(self):
        poisoned = dict(self.r2_pass)
        poisoned["r1_opinion"] = "promote anyway"
        with self.assertRaises(ValueError):
            self.m.normalize_r2_result(poisoned)

    def test_l10_10_changed_policy_inputs_change_routing_identity(self):
        a = {"risk_class": "LOW", "policy_requires_dual_review": False}
        b = {"risk_class": "LOW", "policy_requires_dual_review": True}
        self.assertNotEqual(self.m.route_identity(a), self.m.route_identity(b))

    def test_l10_11_unregistered_material_field_cannot_be_silently_dropped(self):
        expanded = dict(self.r2_pass)
        expanded["new_material_claim"] = "something future schema added"
        with self.assertRaises(ValueError):
            self.m.normalize_r2_result(expanded)

    def test_l10_12_r2_disposition_does_not_change_high_risk_routing(self):
        policy = {"risk_class": "SECURITY"}
        self.assertEqual(
            self.m.requires_r3(policy, self.r2_pass),
            self.m.requires_r3(policy, self.r2_fail),
        )
        self.assertTrue(self.m.requires_r3(policy, self.r2_pass))


if __name__ == "__main__":
    unittest.main(verbosity=2)
