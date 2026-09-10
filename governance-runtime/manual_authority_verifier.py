#!/usr/bin/env python3
"""Verification-only manual governance authority ingress.

This module contains no signing key and exposes no privileged issuer. It verifies
Ed25519 signatures against the human-controlled public trust root committed under
``trust-roots/governance-public.pem``.
"""
from __future__ import annotations

import base64
import binascii
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Mapping

SCHEMA_VERSION = 1
TRUST_ROOT_ID = "SETUGO_MANUAL_GOVERNANCE_ED25519_V1"
TRUSTED_PUBLIC_KEY_PATH = Path(__file__).resolve().parent / "trust-roots" / "governance-public.pem"
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


def canonical_attestation_bytes(attestation: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(attestation),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _verify_ed25519_signature(*, payload: bytes, signature: bytes,
                              public_key_path: Path) -> tuple[bool, str]:
    if not public_key_path.is_file():
        return False, "manual governance public trust root is missing"
    try:
        with tempfile.TemporaryDirectory(prefix="setugo-governance-verify-") as td:
            payload_path = Path(td) / "attestation.json"
            signature_path = Path(td) / "attestation.sig"
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


def verify_manual_authority_attestation(
    attestation: Any,
    signature_b64: Any,
    *,
    candidate_sha: str,
    required_authority_class: str,
    required_scope: str,
    qualification_policy_binding: Mapping[str, Any],
) -> tuple[bool, str]:
    """Verify one human-signed authority attestation against the fixed trust root."""
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

    return _verify_ed25519_signature(
        payload=canonical_attestation_bytes(supplied),
        signature=signature,
        public_key_path=TRUSTED_PUBLIC_KEY_PATH,
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
