#!/usr/bin/env python3
"""Verification-only RELEASE manual authority ingress.

This verifier accepts only the separately pinned RELEASE governance root and
only HUMAN_RELEASE_AUTHORITY terminal scopes. It contains no private key and
grants no authority by itself.
"""
from __future__ import annotations

import base64
import binascii
import json
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Mapping

from release_external_governance_root import (
    RELEASE_TRUST_ROOT_ID,
    ReleaseExternalGovernanceRootError,
    fetch_release_external_public_key,
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
PERMITTED_AUTHORITY_CLASS = "HUMAN_RELEASE_AUTHORITY"
PERMITTED_SCOPES = frozenset({
    "TERMINAL_ACTION:RELEASE:MERGE_RELEASE_CANDIDATE",
    "TERMINAL_ACTION:RELEASE:BEGIN_PRODUCTION_QUALIFICATION",
})


def canonical_attestation_bytes(attestation: Mapping[str, Any]) -> bytes:
    return json.dumps(
        dict(attestation), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _verify_ed25519_signature_bytes(*, payload: bytes, signature: bytes,
                                    public_key_bytes: bytes) -> tuple[bool, str]:
    try:
        with tempfile.TemporaryDirectory(prefix="setugo-release-governance-verify-") as td:
            root = Path(td)
            public_key_path = root / "release-public.pem"
            payload_path = root / "attestation.json"
            signature_path = root / "attestation.sig"
            public_key_path.write_bytes(public_key_bytes)
            payload_path.write_bytes(payload)
            signature_path.write_bytes(signature)
            result = subprocess.run(
                ["openssl", "pkeyutl", "-verify", "-pubin", "-inkey",
                 str(public_key_path), "-rawin", "-in", str(payload_path),
                 "-sigfile", str(signature_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                check=False,
            )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"release governance signature verifier unavailable: {type(exc).__name__}"
    if result.returncode != 0:
        return False, "release governance Ed25519 signature is invalid"
    return True, "release governance Ed25519 signature is valid"


def verify_release_authority_attestation(
    attestation: Any,
    signature_b64: Any,
    *,
    candidate_sha: str,
    required_authority_class: str,
    required_scope: str,
    qualification_policy_binding: Mapping[str, Any],
) -> tuple[bool, str]:
    if required_authority_class != PERMITTED_AUTHORITY_CLASS:
        return False, "release trust root cannot satisfy non-RELEASE authority class"
    if required_scope not in PERMITTED_SCOPES:
        return False, "release trust root cannot satisfy scope outside RELEASE terminal policy"
    if not isinstance(attestation, Mapping):
        return False, "release governance attestation must be a mapping"
    supplied = dict(attestation)
    if set(supplied) != REQUIRED_FIELDS:
        return False, "release governance attestation fields are missing or unexpected"
    if supplied.get("schema_version") != SCHEMA_VERSION:
        return False, "release governance attestation schema version is unsupported"
    if supplied.get("trust_root_id") != RELEASE_TRUST_ROOT_ID:
        return False, "release governance attestation trust root is rebound"
    if supplied.get("source_kind") != "MANUAL_GOVERNANCE_ATTESTATION":
        return False, "RELEASE authority requires manual governance attestation"
    if supplied.get("candidate_sha") != candidate_sha:
        return False, "release governance attestation is not bound to the exact candidate SHA"
    if supplied.get("authority_class") != required_authority_class:
        return False, "release governance attestation authority class is outside required scope"
    if supplied.get("decision_scope") != required_scope:
        return False, "release governance attestation decision scope does not match"
    if not isinstance(supplied.get("evidence_ref"), str) or not supplied["evidence_ref"]:
        return False, "release governance attestation evidence reference is missing"

    expected_policy = {
        "qualification_policy_id": qualification_policy_binding.get("qualification_policy_id"),
        "qualification_policy_version": qualification_policy_binding.get("qualification_policy_version"),
        "qualification_policy_hash": qualification_policy_binding.get("qualification_policy_hash"),
    }
    actual_policy = {key: supplied.get(key) for key in expected_policy}
    if actual_policy != expected_policy:
        return False, "release governance attestation policy binding is stale or rebound"

    if not isinstance(signature_b64, str) or not signature_b64:
        return False, "release governance Ed25519 signature is missing"
    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except (binascii.Error, ValueError):
        return False, "release governance signature is not valid base64"
    if len(signature) != 64:
        return False, "release governance Ed25519 signature length is invalid"

    try:
        public_key = fetch_release_external_public_key()
    except ReleaseExternalGovernanceRootError as exc:
        return False, f"release governance root unavailable or invalid: {exc}"

    return _verify_ed25519_signature_bytes(
        payload=canonical_attestation_bytes(supplied),
        signature=signature,
        public_key_bytes=public_key,
    )
