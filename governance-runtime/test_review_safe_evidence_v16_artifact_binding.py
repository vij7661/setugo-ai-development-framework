from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest

import review_safe_evidence_v16_trust as base
from review_safe_evidence_v16_artifact_binding import (
    PinnedArtifactBoundHead,
    artifact_bound_record_signature_message,
    registry_chain_digest,
    validate_validator_binding_certificate,
    validator_binding_certificate_digest,
    validator_binding_signature_message,
    validator_bundle_digest,
    verify_artifact_bound_governance_record,
)
from test_review_safe_evidence_v16_trust import (
    ISSUER,
    ROOT1,
    ROOT2,
    _sig,
    head_for,
    key_entry,
    make_registry,
    make_signed_record,
    resign_registry,
    trust,
)

ROOT_META = {
    "root-1": ("root-key-1", "root-domain-1", ROOT1),
    "root-2": ("root-key-2", "root-domain-2", ROOT2),
}


def make_binding_certificate(chain, signers=("root-1", "root-2")):
    t = trust()
    current = chain[-1]
    cert = {
        "schema_version": 1,
        "object_type": "VALIDATOR_ARTIFACT_BINDING",
        "candidate_id": current["candidate_id"],
        "registry_id": current["registry_id"],
        "registry_sequence": current["sequence"],
        "registry_digest": current["registry_digest"],
        "registry_chain_digest": registry_chain_digest(chain),
        "trust_set_id": t.trust_set_id,
        "trust_set_digest": t.trust_set_digest,
        "validation_profile_digest": base.validation_profile_digest(),
        "validator_bundle_digest": validator_bundle_digest(),
        "certificate_digest": "",
        "bootstrap_signatures": [],
    }
    cert["certificate_digest"] = validator_binding_certificate_digest(cert)
    rows = []
    for root_id in signers:
        key_id, domain, priv = ROOT_META[root_id]
        msg = validator_binding_signature_message(
            cert["certificate_digest"], trust_set_digest=t.trust_set_digest,
            root_id=root_id, key_id=key_id, control_domain_id=domain,
        )
        rows.append({
            "root_id": root_id,
            "key_id": key_id,
            "algorithm": "ED25519",
            "signature_b64": _sig(priv, msg),
        })
    cert["bootstrap_signatures"] = rows
    return cert


def artifact_head(chain, cert):
    return PinnedArtifactBoundHead(
        anchor_id="artifact-head-1",
        registry_head=head_for(chain),
        validator_binding_digest=cert["certificate_digest"],
        validator_bundle_digest=cert["validator_bundle_digest"],
        registry_chain_digest=cert["registry_chain_digest"],
    )


def make_outer(chain, cert, *, inner=None, validator_bundle=None):
    inner = inner or make_signed_record(registry=chain[-1])
    outer = {
        "schema_version": 1,
        "object_type": "ARTIFACT_BOUND_SIGNED_GOVERNANCE_RECORD",
        "validator_binding_digest": cert["certificate_digest"],
        "validator_bundle_digest": validator_bundle or cert["validator_bundle_digest"],
        "inner_record_digest": base.canonical_sha256(inner),
        "inner_record": copy.deepcopy(inner),
        "signature_algorithm": "ED25519",
        "outer_signature_b64": "",
    }
    outer["outer_signature_b64"] = _sig(ISSUER, artifact_bound_record_signature_message(outer))
    return outer


def verify(chain, cert, outer, *, head=None):
    return verify_artifact_bound_governance_record(
        outer,
        binding_certificate=cert,
        registry_chain=chain,
        bootstrap_trust=trust(),
        pinned_artifact_head=head or artifact_head(chain, cert),
        expected_candidate_id="candidate-1",
        expected_generation_id=chain[-1]["generation_id"],
        expected_record_type="RAW_EVIDENCE_CAPTURE",
    )


class ValidatorBundleIdentityTests(unittest.TestCase):
    def test_validator_bundle_digest_changes_when_base_source_bytes_change(self):
        before = validator_bundle_digest()
        original = base.__file__
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "review_safe_evidence_v16_trust.py"
            path.write_bytes(Path(original).read_bytes() + b"\n# drift\n")
            try:
                base.__file__ = str(path)
                after = validator_bundle_digest()
            finally:
                base.__file__ = original
        self.assertNotEqual(before, after)

    def test_valid_binding_certificate_is_threshold_authenticated_but_not_qualified(self):
        chain = [make_registry()]
        cert = make_binding_certificate(chain)
        result = validate_validator_binding_certificate(
            cert, registry_chain=chain, bootstrap_trust=trust(),
            expected_registry_head=head_for(chain),
            pinned_artifact_head=artifact_head(chain, cert),
            expected_candidate_id="candidate-1",
        )
        self.assertTrue(result["valid"], result["problems"])
        self.assertFalse(result["qualified"])
        self.assertFalse(result["artifact_measurement_independently_proven"])
        self.assertEqual(len(result["bootstrap_authenticated_control_domains"]), 2)

    def test_single_bootstrap_root_cannot_authorize_validator_binding(self):
        chain = [make_registry()]
        cert = make_binding_certificate(chain, signers=("root-1",))
        result = validate_validator_binding_certificate(
            cert, registry_chain=chain, bootstrap_trust=trust(),
            expected_registry_head=head_for(chain),
            pinned_artifact_head=artifact_head(chain, cert),
            expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["valid"])
        self.assertIn("VALIDATOR_BINDING_BOOTSTRAP_THRESHOLD_NOT_MET", result["problems"])

    def test_bootstrap_binding_signature_cannot_be_relabelled_to_another_root(self):
        chain = [make_registry()]
        cert = make_binding_certificate(chain)
        forged = copy.deepcopy(cert)
        forged["bootstrap_signatures"][1]["signature_b64"] = forged["bootstrap_signatures"][0]["signature_b64"]
        result = validate_validator_binding_certificate(
            forged, registry_chain=chain, bootstrap_trust=trust(),
            expected_registry_head=head_for(chain),
            pinned_artifact_head=artifact_head(chain, cert),
            expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("VALIDATOR_BINDING_SIGNATURE_INVALID" in p for p in result["problems"]))

    def test_binding_certificate_cannot_be_reused_for_different_registry_chain(self):
        chain_a = [make_registry()]
        cert = make_binding_certificate(chain_a)
        extra = key_entry(
            issuer_id="issuer-2", key_id="issuer-key-2", control_domain="issuer-domain-2",
            public_key_b64=base64_public_key_for_attacker(), valid_from=1,
        )
        chain_b = [make_registry(keys=[key_entry(), extra])]
        result = validate_validator_binding_certificate(
            cert, registry_chain=chain_b, bootstrap_trust=trust(),
            expected_registry_head=head_for(chain_b),
            pinned_artifact_head=artifact_head(chain_a, cert),
            expected_candidate_id="candidate-1",
        )
        self.assertFalse(result["valid"])
        self.assertTrue(any("CHAIN_DIGEST_MISMATCH" in p or "REGISTRY_DIGEST_MISMATCH" in p for p in result["problems"]))


class ArtifactBoundRecordTests(unittest.TestCase):
    def test_valid_artifact_bound_record_passes_but_remains_nonqualified(self):
        chain = [make_registry()]
        cert = make_binding_certificate(chain)
        result = verify(chain, cert, make_outer(chain, cert))
        self.assertTrue(result["valid"], result["problems"])
        self.assertTrue(result["base_record_valid"])
        self.assertTrue(result["binding_certificate_valid"])
        self.assertTrue(result["outer_signature_verified"])
        self.assertFalse(result["qualified"])

    def test_outer_signature_tamper_fails_even_when_inner_record_is_valid(self):
        chain = [make_registry()]
        cert = make_binding_certificate(chain)
        outer = make_outer(chain, cert)
        outer["outer_signature_b64"] = outer["outer_signature_b64"][:-2] + "AA"
        result = verify(chain, cert, outer)
        self.assertFalse(result["valid"])
        self.assertTrue(result["base_record_valid"])
        self.assertIn("ARTIFACT_BOUND_OUTER_SIGNATURE_INVALID", result["problems"])

    def test_different_validator_bundle_fails_even_with_fresh_outer_signature(self):
        chain = [make_registry()]
        cert = make_binding_certificate(chain)
        outer = make_outer(chain, cert, validator_bundle="f" * 64)
        result = verify(chain, cert, outer)
        self.assertFalse(result["valid"])
        self.assertTrue(result["outer_signature_verified"])
        self.assertIn("ARTIFACT_BOUND_RECORD_VALIDATOR_BUNDLE_MISMATCH", result["problems"])

    def test_pinned_binding_digest_mismatch_fails_closed(self):
        chain = [make_registry()]
        cert = make_binding_certificate(chain)
        head = replace(artifact_head(chain, cert), validator_binding_digest="f" * 64)
        result = verify(chain, cert, make_outer(chain, cert), head=head)
        self.assertFalse(result["valid"])
        self.assertTrue(any("PINNED_CERTIFICATE_DIGEST_MISMATCH" in p or "BINDING_DIGEST_MISMATCH" in p for p in result["problems"]))

    def test_mixed_validation_profile_registry_chain_is_forbidden(self):
        r1 = make_registry()
        r1["authority_policy_digest"] = "a" * 64
        resign_registry(r1)
        r2 = make_registry(
            sequence=2, generation_id="gen-2", predecessor=r1["registry_digest"],
            key=key_entry(),
        )
        chain = [r1, r2]
        cert = make_binding_certificate(chain)
        result = verify(chain, cert, make_outer(chain, cert))
        self.assertFalse(result["valid"])
        self.assertIn("MIXED_VALIDATION_PROFILE_CHAIN_FORBIDDEN", result["problems"])

    def test_base_record_alone_is_not_artifact_bound_record(self):
        chain = [make_registry()]
        cert = make_binding_certificate(chain)
        inner = make_signed_record(registry=chain[-1])
        result = verify(chain, cert, inner)
        self.assertFalse(result["valid"])
        self.assertIn("ARTIFACT_BOUND_RECORD_FIELDS_NOT_EXACT", result["problems"])

    def test_valid_result_explicitly_marks_source_measurement_as_not_independently_proven(self):
        chain = [make_registry()]
        cert = make_binding_certificate(chain)
        result = verify(chain, cert, make_outer(chain, cert))
        self.assertTrue(result["valid"], result["problems"])
        self.assertEqual(result["artifact_measurement"], "LOCAL_SOURCE_BYTES_SELF_MEASURED")
        self.assertFalse(result["artifact_measurement_independently_proven"])


def base64_public_key_for_attacker() -> str:
    from test_review_safe_evidence_v16_trust import ATTACKER, _pub
    return _pub(ATTACKER)


if __name__ == "__main__":
    unittest.main()
