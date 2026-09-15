from __future__ import annotations

import unittest

from review_safe_evidence_v15 import canonical_hash
from review_safe_evidence_v15_monitors import (
    monitor_construction_frontier,
    validate_hidden_evidence_coverage_certificate,
    validate_hidden_monitor_bundle,
    validate_monitor_record,
)


def seal(r, field):
    r[field] = canonical_hash({k: v for k, v in r.items() if k != field})
    return r


def proof(a, b, result="INDEPENDENT", shared=None):
    return seal({
        "schema_version": 1,
        "proof_id": f"P-{a}-{b}",
        "subject_a": a,
        "subject_b": b,
        "generation_id": "GEN-1",
        "ancestry_graph_digest": "1" * 64,
        "shared_load_bearing_ancestors": list(shared or []),
        "declared_residual_roots": ["R1", "R2"],
        "result": result,
        "proof_digest": "",
    }, "proof_digest")


def descriptor(mid, domain, impl, impl_domain):
    return {
        "monitor_id": mid,
        "control_domain_id": domain,
        "implementation_id": impl,
        "implementation_control_domain_id": impl_domain,
        "currentness_state": "CURRENT",
        "candidate_controlled": False,
    }


def record(mid, domain, impl, impl_domain, obligation, result="NO_REOPEN_FOUND"):
    return seal({
        "schema_version": 1,
        "monitor_id": mid,
        "monitor_control_domain_id": domain,
        "implementation_id": impl,
        "implementation_control_domain_id": impl_domain,
        "algorithm_id": f"ALG-{impl}",
        "algorithm_digest": "2" * 64,
        "obligation_id": obligation,
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "raw_evidence_root_digest": "3" * 64,
        "observation_digest": "4" * 64,
        "result": result,
        "currentness_state": "CURRENT",
        "candidate_controlled": False,
        "observed_sequence": 10,
        "record_digest": "",
    }, "record_digest")


def valid_bundle(reopen=None):
    reopen = set(reopen or [])
    monitors = [
        descriptor("M1", "D1", "I1", "ID1"),
        descriptor("M2", "D2", "I2", "ID2"),
        descriptor("M3", "D3", "I1", "ID1"),
    ]
    obligations = ["O1", "O2"]
    rows = []
    for m in monitors:
        for oid in obligations:
            rows.append(record(
                m["monitor_id"], m["control_domain_id"], m["implementation_id"],
                m["implementation_control_domain_id"], oid,
                "REOPEN_REQUIRED" if oid in reopen and m["monitor_id"] == "M1" else "NO_REOPEN_FOUND",
            ))
    bundle = {
        "schema_version": 1,
        "bundle_id": "MB-1",
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "raw_evidence_root_digest": "3" * 64,
        "threshold_control_domains": 2,
        "monitors": monitors,
        "records": rows,
        "bundle_digest": "",
    }
    seal(bundle, "bundle_digest")
    proofs = [
        proof("D1", "D2"), proof("D1", "D3"), proof("D2", "D3"),
        proof("ID1", "ID2"),
    ]
    return bundle, obligations, proofs


class MonitorRecordTests(unittest.TestCase):
    def test_valid_monitor_record(self):
        self.assertTrue(validate_monitor_record(record("M1", "D1", "I1", "ID1", "O1"))["valid"])

    def test_candidate_controlled_monitor_record_rejected(self):
        r = record("M1", "D1", "I1", "ID1", "O1")
        r["candidate_controlled"] = True
        seal(r, "record_digest")
        self.assertIn("HIDDEN_MONITOR_CANDIDATE_CONTROL_FORBIDDEN", validate_monitor_record(r)["problems"])

    def test_stale_monitor_record_rejected(self):
        r = record("M1", "D1", "I1", "ID1", "O1")
        r["currentness_state"] = "STALE"
        seal(r, "record_digest")
        self.assertIn("HIDDEN_MONITOR_NOT_CURRENT", validate_monitor_record(r)["problems"])


class MonitorBundleTests(unittest.TestCase):
    def test_complete_diverse_bundle_passes(self):
        b, obligations, proofs = valid_bundle()
        out = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=proofs)
        self.assertTrue(out["valid"], out["problems"])
        self.assertFalse(out["promotion_blocked"])
        self.assertEqual(out["monitor_identity_count"], 3)
        self.assertEqual(out["control_domain_count"], 3)
        self.assertEqual(out["implementation_count"], 2)

    def test_monitor_silence_blocks(self):
        b, obligations, proofs = valid_bundle()
        b["records"] = [r for r in b["records"] if not (r["monitor_id"] == "M3" and r["obligation_id"] == "O2")]
        seal(b, "bundle_digest")
        out = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=proofs)
        self.assertIn("HIDDEN_MONITOR_SILENCE_BLOCKING:M3:O2", out["problems"])
        self.assertTrue(out["promotion_blocked"])

    def test_same_control_domain_cannot_create_quorum(self):
        b, obligations, proofs = valid_bundle()
        b["monitors"][1]["control_domain_id"] = "D1"
        for r in b["records"]:
            if r["monitor_id"] == "M2":
                r["monitor_control_domain_id"] = "D1"
                seal(r, "record_digest")
        seal(b, "bundle_digest")
        out = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=proofs)
        self.assertTrue(out["promotion_blocked"])
        self.assertLess(out["control_domain_count"], 3)

    def test_single_implementation_rejected(self):
        b, obligations, proofs = valid_bundle()
        for m in b["monitors"]:
            m["implementation_id"] = "I1"
            m["implementation_control_domain_id"] = "ID1"
        for r in b["records"]:
            r["implementation_id"] = "I1"
            r["implementation_control_domain_id"] = "ID1"
            seal(r, "record_digest")
        seal(b, "bundle_digest")
        out = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=proofs)
        self.assertIn("HIDDEN_MONITOR_IMPLEMENTATION_DIVERSITY_INSUFFICIENT", out["problems"])

    def test_missing_domain_independence_proof_blocks(self):
        b, obligations, proofs = valid_bundle()
        reduced = [p for p in proofs if frozenset((p["subject_a"], p["subject_b"])) != frozenset(("D1", "D2"))]
        out = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=reduced)
        self.assertIn("HIDDEN_MONITOR_DOMAIN_INDEPENDENCE_PROOF_MISSING:D1:D2", out["problems"])

    def test_unproven_implementation_independence_blocks(self):
        b, obligations, proofs = valid_bundle()
        changed = [p for p in proofs if frozenset((p["subject_a"], p["subject_b"])) != frozenset(("ID1", "ID2"))]
        changed.append(proof("ID1", "ID2", "INDEPENDENCE_UNPROVEN"))
        out = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=changed)
        self.assertTrue(any("HIDDEN_MONITOR_IMPLEMENTATION_INDEPENDENCE_UNPROVEN" in x for x in out["problems"]))

    def test_reopen_required_blocks_promotion(self):
        b, obligations, proofs = valid_bundle(reopen=["O2"])
        out = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=proofs)
        self.assertTrue(out["valid"], out["problems"])
        self.assertTrue(out["promotion_blocked"])
        self.assertEqual(out["reopen_required_obligations"], ["O2"])

    def test_unknown_obligation_record_rejected(self):
        b, obligations, proofs = valid_bundle()
        b["records"].append(record("M1", "D1", "I1", "ID1", "OX"))
        seal(b, "bundle_digest")
        out = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=proofs)
        self.assertIn("HIDDEN_MONITOR_UNEXPECTED_RECORD:M1:OX", out["problems"])


class CoverageCertificateTests(unittest.TestCase):
    def certificate(self, monitor_result, obligations, states=None):
        states = states or {oid: ("REOPEN_REQUIRED" if oid in monitor_result["reopen_required_obligations"] else "NO_REOPEN_FOUND") for oid in obligations}
        return seal({
            "schema_version": 1,
            "certificate_id": "HC-1",
            "candidate_id": "C1",
            "snapshot_id": "S1",
            "generation_id": "GEN-1",
            "verifier_id": "HCV-1",
            "verifier_control_domain_id": "D-HCV",
            "verifier_independence_result": "INDEPENDENT",
            "monitor_bundle_digest": "5" * 64,
            "raw_evidence_root_digest": "3" * 64,
            "obligation_set_digest": canonical_hash(sorted(obligations)),
            "obligation_results": states,
            "currentness_state": "CURRENT",
            "certificate_digest": "",
        }, "certificate_digest")

    def test_no_reopen_certificate_passes(self):
        b, obligations, proofs = valid_bundle()
        mr = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=proofs)
        cert = self.certificate(mr, obligations)
        out = validate_hidden_evidence_coverage_certificate(cert, monitor_result=mr, expected_obligations=obligations)
        self.assertTrue(out["valid"], out["problems"])
        self.assertFalse(out["promotion_blocked"])

    def test_reopen_certificate_blocks(self):
        b, obligations, proofs = valid_bundle(reopen=["O1"])
        mr = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=proofs)
        cert = self.certificate(mr, obligations)
        out = validate_hidden_evidence_coverage_certificate(cert, monitor_result=mr, expected_obligations=obligations)
        self.assertTrue(out["valid"], out["problems"])
        self.assertTrue(out["promotion_blocked"])

    def test_certificate_cannot_launder_reopen_to_no_reopen(self):
        b, obligations, proofs = valid_bundle(reopen=["O1"])
        mr = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=proofs)
        cert = self.certificate(mr, obligations, states={"O1": "NO_REOPEN_FOUND", "O2": "NO_REOPEN_FOUND"})
        out = validate_hidden_evidence_coverage_certificate(cert, monitor_result=mr, expected_obligations=obligations)
        self.assertIn("HIDDEN_COVERAGE_CERTIFICATE_RESULT_MISMATCH:O1:REOPEN_REQUIRED", out["problems"])

    def test_stale_certificate_rejected(self):
        b, obligations, proofs = valid_bundle()
        mr = validate_hidden_monitor_bundle(b, expected_obligations=obligations, independence_proofs=proofs)
        cert = self.certificate(mr, obligations)
        cert["currentness_state"] = "STALE"
        seal(cert, "certificate_digest")
        out = validate_hidden_evidence_coverage_certificate(cert, monitor_result=mr, expected_obligations=obligations)
        self.assertIn("HIDDEN_COVERAGE_CERTIFICATE_NOT_CURRENT", out["problems"])

    def test_frontier_non_authoritative(self):
        f = monitor_construction_frontier()
        self.assertFalse(f["qualified"])
        self.assertEqual(f["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
