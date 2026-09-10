from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from qualification_boundary_policy import policy_binding, verify_authority_binding
from manual_authority_verifier import verify_manual_authority_attestation

HERE = Path(__file__).resolve().parent
ATTESTATION_PATH = HERE / "manual-attestations" / "ed265f37487bccffcc5f4463f5f3b62ee9f2b713.acceptance-boundary.json"
SIGNATURE_PATH = HERE / "manual-attestations" / "ed265f37487bccffcc5f4463f5f3b62ee9f2b713.acceptance-boundary.sig.b64"
SIGNED_SHA = "ed265f37487bccffcc5f4463f5f3b62ee9f2b713"
AUTHORITY = "HUMAN_GOVERNANCE_OWNER"
SCOPE = "ACCEPTANCE_BOUNDARY_APPROVAL"


def _fixture():
    attestation = json.loads(ATTESTATION_PATH.read_text(encoding="utf-8"))
    signature_b64 = SIGNATURE_PATH.read_text(encoding="utf-8").strip()
    return attestation, signature_b64


def test_real_human_signed_attestation_verifies_for_exact_signed_candidate():
    attestation, signature_b64 = _fixture()
    ok, reason = verify_authority_binding(
        {"attestation": attestation, "signature_b64": signature_b64},
        candidate_sha=SIGNED_SHA,
        required_authority_class=AUTHORITY,
        required_scope=SCOPE,
    )
    assert ok, reason


def test_signed_attestation_cannot_replay_to_another_candidate_sha():
    attestation, signature_b64 = _fixture()
    ok, _ = verify_authority_binding(
        {"attestation": attestation, "signature_b64": signature_b64},
        candidate_sha="f" * 40,
        required_authority_class=AUTHORITY,
        required_scope=SCOPE,
    )
    assert not ok


def test_signed_attestation_cannot_escalate_scope():
    attestation, signature_b64 = _fixture()
    ok, _ = verify_authority_binding(
        {"attestation": attestation, "signature_b64": signature_b64},
        candidate_sha=SIGNED_SHA,
        required_authority_class=AUTHORITY,
        required_scope="REVIEW_FINDING_ADJUDICATION",
    )
    assert not ok


def test_signed_attestation_cannot_escalate_authority_class():
    attestation, signature_b64 = _fixture()
    ok, _ = verify_authority_binding(
        {"attestation": attestation, "signature_b64": signature_b64},
        candidate_sha=SIGNED_SHA,
        required_authority_class="INDEPENDENT_GOVERNANCE_ADJUDICATOR",
        required_scope=SCOPE,
    )
    assert not ok


def test_tampered_signed_payload_is_rejected():
    attestation, signature_b64 = _fixture()
    tampered = deepcopy(attestation)
    tampered["evidence_ref"] = "candidate-rewritten-evidence"
    ok, _ = verify_manual_authority_attestation(
        tampered,
        signature_b64,
        candidate_sha=SIGNED_SHA,
        required_authority_class=AUTHORITY,
        required_scope=SCOPE,
        qualification_policy_binding=policy_binding(),
    )
    assert not ok


def test_stale_or_rebound_policy_binding_is_rejected():
    attestation, signature_b64 = _fixture()
    rebound_policy = dict(policy_binding())
    rebound_policy["qualification_policy_hash"] = "0" * 64
    ok, _ = verify_manual_authority_attestation(
        attestation,
        signature_b64,
        candidate_sha=SIGNED_SHA,
        required_authority_class=AUTHORITY,
        required_scope=SCOPE,
        qualification_policy_binding=rebound_policy,
    )
    assert not ok


def test_rebound_trust_root_id_is_rejected():
    attestation, signature_b64 = _fixture()
    tampered = deepcopy(attestation)
    tampered["trust_root_id"] = "ATTACKER_TRUST_ROOT"
    ok, _ = verify_manual_authority_attestation(
        tampered,
        signature_b64,
        candidate_sha=SIGNED_SHA,
        required_authority_class=AUTHORITY,
        required_scope=SCOPE,
        qualification_policy_binding=policy_binding(),
    )
    assert not ok


def test_corrupted_signature_is_rejected():
    attestation, signature_b64 = _fixture()
    replacement = "A" if signature_b64[0] != "A" else "B"
    corrupted = replacement + signature_b64[1:]
    ok, _ = verify_manual_authority_attestation(
        attestation,
        corrupted,
        candidate_sha=SIGNED_SHA,
        required_authority_class=AUTHORITY,
        required_scope=SCOPE,
        qualification_policy_binding=policy_binding(),
    )
    assert not ok
