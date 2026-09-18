"""Successor-4 construction proof-context root attestation verifier.

Construction evidence only. This module pins one public verification key and
accepts only externally pre-signed attestations over exact proof-context and
genesis-scope identities. It does not expose signing capability and grants no
runtime, deployment, release, scientific, or terminal authority.
"""
from __future__ import annotations

import base64
import hashlib
from typing import Any, Mapping

from v24_v6_governance_foundation import AUTHORITY_EFFECT, canonical_json

ATTESTATION_SCHEMA_VERSION = 1
ROOT_KEY_ID = "V24-V6-CONSTRUCTION-ROOT-ATTESTATION-V2"
ROOT_ALGORITHM = "RSA-PKCS1-v1_5-SHA256"
ROOT_ARTIFACT_BLOB_SHA = "5708cdd000474a305100f8736a7386c9f4e3aeb5"
ROOT_PUBLIC_KEY_DER_SHA256 = "fe0f6526541361070cd4e609f49dfe9d2153fb599157ef25e0dda442a099ae65"
ROOT_RSA_PUBLIC_EXPONENT = 65537
ROOT_RSA_MODULUS = int(
    "b219fbca13dad82d6691031d401608c91f57f1f64f153097a531a7be0ed3c154"
    "9bce89285bfa5744136b361d09eba49fbd7105a2ff55b49221e2ed3d5fbb1c5"
    "178792f33b66040c7fc5aebda55fd5426fcf680d8bd627db31e0c787f8ef8dce"
    "d66c0faed8dd32d44abc0517794485c9c2d14857db2dc30c26b6a0cc5476660"
    "b1d63446112f3b6b04dee65c780c95b84c29fbf84d17cec18e6c286b8deb6e7"
    "c4caf3556803f51b8d8596d41cb36b6519bd5a98093d89ce97c7a86ec451814"
    "5f5fe570f703882c0d2efb230ca267a827d161676368f4eafbe595d1b0903051"
    "f018a58317ed95bf7d325c39d866cc2703585a08ca80dadbf029d331bb5bdfa28"
    "5cd",
    16,
)

ATTESTATION_VALID = "CONSTRUCTION_ROOT_ATTESTATION_VALID"
ATTESTATION_REJECTED = "CONSTRUCTION_ROOT_ATTESTATION_REJECTED"

_ALLOWED_ATTESTATION_FIELDS = frozenset(
    {
        "schema_version",
        "key_id",
        "governance_generation_id",
        "proof_context_digest",
        "genesis_scope_digest",
        "signature_b64",
    }
)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def attestation_material(attestation: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": attestation.get("schema_version"),
        "key_id": attestation.get("key_id"),
        "governance_generation_id": attestation.get("governance_generation_id"),
        "proof_context_digest": attestation.get("proof_context_digest"),
        "genesis_scope_digest": attestation.get("genesis_scope_digest"),
    }


def _rsa_pkcs1_v1_5_sha256_verify(message: bytes, signature: bytes) -> bool:
    modulus_size = (ROOT_RSA_MODULUS.bit_length() + 7) // 8
    if len(signature) != modulus_size:
        return False
    encoded_int = pow(int.from_bytes(signature, "big"), ROOT_RSA_PUBLIC_EXPONENT, ROOT_RSA_MODULUS)
    encoded = encoded_int.to_bytes(modulus_size, "big")
    digest_info_prefix = bytes.fromhex("3031300d060960864801650304020105000420")
    digest_bytes = hashlib.sha256(message).digest()
    expected_tail = digest_info_prefix + digest_bytes
    padding_len = modulus_size - len(expected_tail) - 3
    if padding_len < 8:
        return False
    expected = b"\x00\x01" + (b"\xff" * padding_len) + b"\x00" + expected_tail
    return encoded == expected


def verify_construction_attestation(
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
    attestation: Mapping[str, Any] | None,
) -> dict[str, Any]:
    problems: list[str] = []

    if not isinstance(proof_context, Mapping):
        problems.append("ATTESTED_PROOF_CONTEXT_REQUIRED")
    if not isinstance(trusted_boundary, Mapping):
        problems.append("ATTESTED_TRUSTED_BOUNDARY_REQUIRED")
    if not isinstance(attestation, Mapping):
        problems.append("CONSTRUCTION_ROOT_ATTESTATION_REQUIRED")
        return {
            "qualified": False,
            "state": ATTESTATION_REJECTED,
            "problems": problems,
            "authority_effect": AUTHORITY_EFFECT,
            "root_key_id": ROOT_KEY_ID,
            "root_artifact_blob_sha": ROOT_ARTIFACT_BLOB_SHA,
        }

    unexpected = sorted(set(attestation) - _ALLOWED_ATTESTATION_FIELDS)
    if unexpected:
        problems.extend(f"ATTESTATION_FIELD_NOT_ALLOWED:{field}" for field in unexpected)

    if attestation.get("schema_version") != ATTESTATION_SCHEMA_VERSION:
        problems.append("ATTESTATION_SCHEMA_VERSION_MISMATCH")
    if attestation.get("key_id") != ROOT_KEY_ID:
        problems.append("ATTESTATION_ROOT_KEY_ID_MISMATCH")

    generation = attestation.get("governance_generation_id")
    context_digest = attestation.get("proof_context_digest")
    scope_digest = attestation.get("genesis_scope_digest")
    if not isinstance(generation, str) or not generation:
        problems.append("ATTESTATION_GENERATION_REQUIRED")
    if not _is_sha256(context_digest):
        problems.append("ATTESTATION_CONTEXT_DIGEST_INVALID")
    if not _is_sha256(scope_digest):
        problems.append("ATTESTATION_SCOPE_DIGEST_INVALID")

    if isinstance(proof_context, Mapping):
        if proof_context.get("governance_generation_id") != generation:
            problems.append("ATTESTATION_CONTEXT_GENERATION_MISMATCH")
        if proof_context.get("context_digest") != context_digest:
            problems.append("ATTESTATION_CONTEXT_DIGEST_MISMATCH")
        scope = proof_context.get("genesis_trusted_scope")
        actual_scope_digest = scope.get("scope_digest") if isinstance(scope, Mapping) else None
        if actual_scope_digest != scope_digest:
            problems.append("ATTESTATION_CONTEXT_SCOPE_DIGEST_MISMATCH")

    if isinstance(trusted_boundary, Mapping):
        if trusted_boundary.get("governance_generation_id") != generation:
            problems.append("ATTESTATION_BOUNDARY_GENERATION_MISMATCH")
        if trusted_boundary.get("expected_proof_context_digest") != context_digest:
            problems.append("ATTESTATION_BOUNDARY_CONTEXT_DIGEST_MISMATCH")
        if trusted_boundary.get("expected_genesis_scope_digest") != scope_digest:
            problems.append("ATTESTATION_BOUNDARY_SCOPE_DIGEST_MISMATCH")

    signature_b64 = attestation.get("signature_b64")
    if not isinstance(signature_b64, str) or not signature_b64:
        problems.append("ATTESTATION_SIGNATURE_REQUIRED")
    else:
        try:
            signature = base64.b64decode(signature_b64, validate=True)
        except Exception:
            problems.append("ATTESTATION_SIGNATURE_ENCODING_INVALID")
        else:
            message = canonical_json(attestation_material(attestation))
            if not _rsa_pkcs1_v1_5_sha256_verify(message, signature):
                problems.append("ATTESTATION_SIGNATURE_INVALID")

    problems = sorted(set(problems))
    return {
        "qualified": not problems,
        "state": ATTESTATION_VALID if not problems else ATTESTATION_REJECTED,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
        "root_key_id": ROOT_KEY_ID,
        "root_artifact_blob_sha": ROOT_ARTIFACT_BLOB_SHA,
        "public_key_der_sha256": ROOT_PUBLIC_KEY_DER_SHA256,
    }
