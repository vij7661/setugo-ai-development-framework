#!/usr/bin/env python3
"""Verification-only TESTING manual governance authority ingress.

This verifier is bound to the TESTING governance root. RELEASE and PRODUCTION
terminal authority must use their own phase-scoped roots. No private signing key
or privileged issuer exists in this module.
"""
from __future__ import annotations

import base64
import binascii
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Mapping

from external_governance_root import (
    ExternalGovernanceRootError,
    TRUST_ROOT_ID,
    fetch_external_public_key,
)

SCHEMA_VERSION = 1
REQUIRED_FIELDS = frozenset({
    "schema_version",
    "candidate_sha",
    "authority_class",
    "decision_scope",
    "evidence_ref",
    "source_kind",
    "qualification_policy_id",
    "qualification_policy_version",
    "qualification_policy_hash",
    "trust_root_id",
})
TESTING_PERMITTED_AUTHORITY_CLASSES = frozenset({
    "HUMAN_GOVERNANCE_OWNER",
    "INDEPENDENT_GOVERNANCE_ADJUDICATOR",
})


def canonical_attestation_bytes(attestation: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(attestation),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _verify_ed25519_signature_bytes(*, payload: bytes, signature: bytes,
                                    public_key_bytes: bytes) -> tuple[bool, str]:
    try:
        with tempfile.TemporaryDirectory(prefix="setugo-governance-verify-") as td:
            root = Path(td)
            public_key_path = root / "governance-public.pem"
            payload_path = root / "attestation.json"
            signature_path = root / "attestation.sig"
            public_key_path.write_bytes(public_key_bytes)
            payload_path.write_bytes(payload)
            signature_path.write_bytes(signature)
            result = subprocess.run(
                [
                    "openssl", "pkeyutl", "-verify", "-pubin",
                    "-inkey", str(public_key_path), "-rawin",
                    "-in", str(payload_path), "-sigfile", str(signature_path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                check=False,
            )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"manual governance signature verifier unavailable: {type(exc).__name__}"
    if result.returncode != 0:
        return False, "manual governance Ed25519 signature is invalid"
    return True, "manual governance Ed25519 signature is valid"


def _verify_ed25519_signature(*, payload: bytes, signature: bytes,
                              public_key_path: Path) -> tuple[bool, str]:
    if not public_key_path.is_file():
        return False, "manual governance public trust root is missing"
    return _verify_ed25519_signature_bytes(
        payload=payload,
        signature=signature,
        public_key_bytes=public_key_path.read_bytes(),
    )


def verify_manual_authority_attestation(
    attestation: Any,
    signature_b64: Any,
    *,
    candidate_sha: str,
    required_authority_class: str,
    required_scope: str,
    qualification_policy_binding: Mapping[str, Any],
) -> tuple[bool, str]:
    """Verify one TESTING-scoped human-signed governance attestation."""
    if required_authority_class not in TESTING_PERMITTED_AUTHORITY_CLASSES:
        return False, "TESTING trust root cannot satisfy RELEASE or PRODUCTION authority"
    if not isinstance(attestation, Mapping):
        return False, "manual governance attestation must be a mapping"
    supplied = dict(attestation)
    if set(supplied) != REQUIRED_FIELDS:
        return False, "manual governance attestation fields are missing or unexpected"
    if supplied.get("schema_version") != SCHEMA_VERSION:
        return False, "manual governance attestation schema version is unsupported"
    if supplied.get("trust_root_id") != TRUST_ROOT_ID:
        return False, "manual governance attestation trust root is rebound"
    if supplied.get("source_kind") != "MANUAL_GOVERNANCE_ATTESTATION":
        return False, "TESTING authority requires manual governance attestation"
    if supplied.get("candidate_sha") != candidate_sha:
        return False, "manual governance attestation is not bound to the exact candidate SHA"
    if supplied.get("authority_class") != required_authority_class:
        return False, "manual governance attestation authority class is outside required scope"
    if supplied.get("decision_scope") != required_scope:
        return False, "manual governance attestation decision scope does not match"
    if not isinstance(supplied.get("evidence_ref"), str) or not supplied["evidence_ref"]:
        return False, "manual governance attestation evidence reference is missing"

    expected_policy = {
        "qualification_policy_id": qualification_policy_binding.get("qualification_policy_id"),
        "qualification_policy_version": qualification_policy_binding.get("qualification_policy_version"),
        "qualification_policy_hash": qualification_policy_binding.get("qualification_policy_hash"),
    }
    actual_policy = {key: supplied.get(key) for key in expected_policy}
    if actual_policy != expected_policy:
        return False, "manual governance attestation policy binding is stale or rebound"

    if not isinstance(signature_b64, str) or not signature_b64:
        return False, "manual governance Ed25519 signature is missing"
    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except (binascii.Error, ValueError):
        return False, "manual governance signature is not valid base64"
    if len(signature) != 64:
        return False, "manual governance Ed25519 signature length is invalid"

    try:
        external_public_key = fetch_external_public_key()
    except ExternalGovernanceRootError as exc:
        return False, f"external governance root unavailable or invalid: {exc}"

    return _verify_ed25519_signature_bytes(
        payload=canonical_attestation_bytes(supplied),
        signature=signature,
        public_key_bytes=external_public_key,
    )


def verify_signature_with_explicit_test_key(attestation: Mapping[str, Any], signature_b64: str,
                                            public_key_path: Path) -> tuple[bool, str]:
    """Cryptographic primitive test hook only; governance decisions never call this."""
    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except (binascii.Error, ValueError):
        return False, "test signature is not valid base64"
    return _verify_ed25519_signature(
        payload=canonical_attestation_bytes(attestation),
        signature=signature,
        public_key_path=public_key_path,
    )
