from __future__ import annotations

import unittest

from review_safe_evidence_v15 import canonical_hash
from review_safe_evidence_v15_universe import (
    universe_construction_frontier,
    validate_derivation_record,
    validate_universe_challenge,
    validate_universe_completeness_certificate,
    validate_universe_derivation_bundle,
)


def seal(r, field):
    r[field] = canonical_hash({k: v for k, v in r.items() if k != field})
    return r


def proof(a, b, result="INDEPENDENT"):
    return seal({
        "schema_version": 1,
        "proof_id": f"P-{a}-{b}",
        "subject_a": a,
        "subject_b": b,
        "generation_id": "GEN-1",
        "ancestry_graph_digest": "a" * 64,
        "shared_load_bearing_ancestors": [],
        "declared_residual_roots": ["R1", "R2"],
        "result": result,
        "proof_digest": "",
    }, "proof_digest")


def derivation(stream, domain, roots, obligations):
    return seal({
        "schema_version": 1,
        "derivation_id": f"DER-{stream}",
        "stream_class": stream,
        "authority_id": f"AUTH-{stream}",
        "control_domain_id": domain,
        "generation_id": "GEN-1",
        "source_roots": list(roots),
        "source_graph_digest": "b" * 64,
        "obligations": list(obligations),
        "candidate_controlled": False,
        "currentness_state": "CURRENT",
        "record_digest": "",
    }, "record_digest")


def valid_bundle(shared_source=False):
    rows = [
        derivation("NORMATIVE", "D1", ["SRC-N"], ["O1", "O2"]),
        derivation("AUTHORITY_SURFACE", "D2", ["SRC-S" if not shared_source else "SRC-N"], ["O1", "O3"]),
        derivation("HISTORICAL", "D3", ["SRC-H"], ["O1", "O4"]),
    ]
    union = sorted({"O1", "O2", "O3", "O4"})
    b = {
        "schema_version": 1,
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "derivations": rows,
        "unclassified_material_surfaces": [],
        "expected_union_digest": canonical_hash(union),
        "bundle_digest": "",
    }
    seal(b, "bundle_digest")
    proofs = [proof("D1", "D2"), proof("D1", "D3"), proof("D2", "D3")]
    return b, proofs


def valid_challenge(obligations, discovered=None):
    discovered = list(discovered or [])
    expanded = sorted(set(obligations) | set(discovered))
    r = {
        "schema_version": 1,
        "challenge_id": "CH-1",
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "challenge_authority_id": "CHA-1",
        "challenge_control_domain_id": "D4",
        "challenge_algorithm_id": "NEG-SPACE-V1",
        "verifier_id": "V-CH",
        "verifier_independence_result": "INDEPENDENT",
        "candidate_controlled": False,
        "authority_may_remove_obligations": False,
        "discovered_obligations": discovered,
        "removed_obligations": [],
        "result": "OBLIGATION_ADDED" if discovered else "NO_NEW_OBLIGATION_FOUND",
        "source_root_digest": "c" * 64,
        "coverage_digest": "d" * 64,
        "expanded_union_digest": canonical_hash(expanded),
        "challenge_digest": "",
    }
    return seal(r, "challenge_digest")


class DerivationTests(unittest.TestCase):
    def test_valid_derivation_record(self):
        self.assertTrue(validate_derivation_record(
            derivation("NORMATIVE", "D1", ["S1"], ["O1"]))["valid"])

    def test_candidate_controlled_derivation_rejected(self):
        r = derivation("NORMATIVE", "D1", ["S1"], ["O1"])
        r["candidate_controlled"] = True
        seal(r, "record_digest")
        self.assertIn("UNIVERSE_DERIVATION_CANDIDATE_CONTROL_FORBIDDEN",
                      validate_derivation_record(r)["problems"])

    def test_three_stream_union_passes(self):
        b, proofs = valid_bundle()
        out = validate_universe_derivation_bundle(b, proofs)
        self.assertTrue(out["valid"], out["problems"])
        self.assertEqual(out["authoritative_obligations"], ["O1", "O2", "O3", "O4"])
        self.assertIn("O2", out["divergence"])

    def test_missing_stream_blocks(self):
        b, proofs = valid_bundle()
        b["derivations"] = [r for r in b["derivations"] if r["stream_class"] != "HISTORICAL"]
        seal(b, "bundle_digest")
        out = validate_universe_derivation_bundle(b, proofs)
        self.assertIn("UNIVERSE_DERIVATION_STREAM_MISSING:HISTORICAL", out["problems"])

    def test_same_control_domain_blocks(self):
        b, proofs = valid_bundle()
        b["derivations"][1]["control_domain_id"] = "D1"
        seal(b["derivations"][1], "record_digest")
        seal(b, "bundle_digest")
        self.assertIn("UNIVERSE_DERIVATION_CONTROL_DOMAIN_COLLAPSE",
                      validate_universe_derivation_bundle(b, proofs)["problems"])

    def test_missing_independence_proof_blocks(self):
        b, proofs = valid_bundle()
        out = validate_universe_derivation_bundle(b, proofs[:-1])
        self.assertTrue(any("UNIVERSE_DERIVATION_INDEPENDENCE_PROOF_MISSING" in x
                            for x in out["problems"]))

    def test_unclassified_material_surface_blocks(self):
        b, proofs = valid_bundle()
        b["unclassified_material_surfaces"] = ["SURFACE-X"]
        seal(b, "bundle_digest")
        out = validate_universe_derivation_bundle(b, proofs)
        self.assertIn("UNIVERSE_UNCLASSIFIED_MATERIAL_SURFACE_BLOCKING:SURFACE-X", out["problems"])

    def test_shared_source_circularity_blocks_common_obligation(self):
        b, proofs = valid_bundle(shared_source=True)
        b["derivations"][2]["source_roots"] = ["SRC-N"]
        seal(b["derivations"][2], "record_digest")
        seal(b, "bundle_digest")
        out = validate_universe_derivation_bundle(b, proofs)
        self.assertTrue(any(x.startswith("UNIVERSE_SHARED_SOURCE_CIRCULARITY:O1")
                            for x in out["problems"]))

    def test_union_digest_tamper_rejected(self):
        b, proofs = valid_bundle()
        b["expected_union_digest"] = "0" * 64
        seal(b, "bundle_digest")
        self.assertIn("UNIVERSE_AUTHORITATIVE_UNION_DIGEST_MISMATCH",
                      validate_universe_derivation_bundle(b, proofs)["problems"])


class ChallengeTests(unittest.TestCase):
    def test_no_new_challenge_passes(self):
        obligations = ["O1", "O2"]
        out = validate_universe_challenge(valid_challenge(obligations),
                                          authoritative_obligations=obligations)
        self.assertTrue(out["valid"], out["problems"])

    def test_challenge_can_add_obligation(self):
        obligations = ["O1", "O2"]
        out = validate_universe_challenge(valid_challenge(obligations, ["O3"]),
                                          authoritative_obligations=obligations)
        self.assertTrue(out["valid"], out["problems"])
        self.assertEqual(out["expanded_obligations"], ["O1", "O2", "O3"])

    def test_challenge_cannot_remove_obligation(self):
        r = valid_challenge(["O1", "O2"])
        r["removed_obligations"] = ["O2"]
        seal(r, "challenge_digest")
        self.assertIn("UNIVERSE_CHALLENGE_REMOVED_OBLIGATION_FORBIDDEN",
                      validate_universe_challenge(r, authoritative_obligations=["O1", "O2"])["problems"])

    def test_challenge_remove_authority_forbidden(self):
        r = valid_challenge(["O1"])
        r["authority_may_remove_obligations"] = True
        seal(r, "challenge_digest")
        self.assertIn("UNIVERSE_CHALLENGE_REMOVE_AUTHORITY_FORBIDDEN",
                      validate_universe_challenge(r, authoritative_obligations=["O1"])["problems"])

    def test_no_new_result_with_discovered_obligation_rejected(self):
        r = valid_challenge(["O1"], ["O2"])
        r["result"] = "NO_NEW_OBLIGATION_FOUND"
        seal(r, "challenge_digest")
        self.assertIn("UNIVERSE_CHALLENGE_NO_NEW_WITH_DISCOVERED",
                      validate_universe_challenge(r, authoritative_obligations=["O1"])["problems"])

    def test_challenge_verifier_independence_required(self):
        r = valid_challenge(["O1"])
        r["verifier_independence_result"] = "INDEPENDENCE_UNPROVEN"
        seal(r, "challenge_digest")
        self.assertIn("UNIVERSE_CHALLENGE_VERIFIER_INDEPENDENCE_REQUIRED",
                      validate_universe_challenge(r, authoritative_obligations=["O1"])["problems"])


class CertificateTests(unittest.TestCase):
    def certificate(self, unresolved=0):
        b, proofs = valid_bundle()
        d = validate_universe_derivation_bundle(b, proofs)
        c_rec = valid_challenge(d["authoritative_obligations"])
        c = validate_universe_challenge(c_rec, authoritative_obligations=d["authoritative_obligations"])
        cert = {
            "schema_version": 1,
            "certificate_id": "UC-1",
            "candidate_id": "C1",
            "snapshot_id": "S1",
            "generation_id": "GEN-1",
            "certificate_verifier_id": "UV-1",
            "verifier_independence_result": "INDEPENDENT",
            "authoritative_union_digest": c["expanded_union_digest"],
            "challenge_digest": c_rec["challenge_digest"],
            "bound_challenge_digest": c_rec["challenge_digest"],
            "unresolved_unknown_count": unresolved,
            "certificate_digest": "",
        }
        seal(cert, "certificate_digest")
        return cert, d, c

    def test_certificate_binds_valid_derivation_and_challenge(self):
        cert, d, c = self.certificate()
        out = validate_universe_completeness_certificate(cert, derivation_result=d, challenge_result=c)
        self.assertTrue(out["valid"], out["problems"])

    def test_certificate_blocks_unresolved_unknowns(self):
        cert, d, c = self.certificate(unresolved=1)
        self.assertIn("UNIVERSE_CERTIFICATE_UNRESOLVED_UNKNOWN_BLOCKING",
                      validate_universe_completeness_certificate(
                          cert, derivation_result=d, challenge_result=c)["problems"])

    def test_frontier_non_authoritative(self):
        f = universe_construction_frontier()
        self.assertFalse(f["qualified"])
        self.assertEqual(f["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
