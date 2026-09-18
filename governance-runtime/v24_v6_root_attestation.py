"""V24 I11 V6 construction root-attestation verification.

Verify-only construction mechanism for Successor-4.  The signing private key is
not present in this repository/module.  The verifier pins the exact V3 public
key issued on the isolated trust branch and grants construction evidence only;
it does not grant runtime, deployment, release, scientific, or terminal
authority.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
from typing import Any, Mapping

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
RUNTIME_QUALIFICATION_STATE = "NOT_CLAIMED"

ROOT_ATTESTATION_SCHEMA_VERSION = 1
ROOT_ATTESTATION_KEY_ID = "V24-V6-CONSTRUCTION-ROOT-ATTESTATION-V3"
ROOT_ATTESTATION_ALGORITHM = "RSA-PKCS1-v1_5-SHA256"
ROOT_ATTESTATION_PURPOSE = "V24_V6_CONSTRUCTION_PROOF_CONTEXT_ATTESTATION"

TRUST_BRANCH = "trust/v24-v6-construction-root-attestation-v3"
TRUST_COMMIT_SHA = "2515582a5e2f0e1041bf5cc83523ffa732620724"
TRUST_PUBLIC_ARTIFACT_BLOB_SHA = "7722a5725324fb805283bce9764b2d151a774ec2"
TRUST_SIGNATURE_BUNDLE_BLOB_SHA = "b16e2a2bfac013e6e600cf9944595a88eefd2ca8"
TRUST_CEREMONY_BLOB_SHA = "cc2d8bec17b6775392094920f9549ca2e5174d44"
TRUST_PUBLIC_KEY_DER_SHA256 = "fbb2cea7474505f0c0d8f77be81c97a949d4ea70eb38b7caef4ffd0e9606f61c"

_RSA_MODULUS = int("a859b1d6e482ee3a0b59cefea9a1506f27e2a76fb30b142bd2f224a3930ff4f904f765c3ad749dd81f7fa9a702f0a84cf29fdb25cefa8437c6403f72167195e4b87daa9f4dd2a3d25afd611f3732a3bbe1ab0225ed1922528e2b84fd141dea95f9feb07e901d94e6fb033af3f1a1c718c8c8952f8bf66a29723d3a7b8755e030dd5d29a87be2472a3fa3d2b51596092734a78113f4c6846790f02b6a9e2bce87abb69ebaf86fe2eb0d3de78c6f3dee723957f30593fc6bc4e7f41026ccb22d5271f3a391b355d5a62281f0193f33e5de96df50bbdfe554769cafe55b7a8f1e471ce47deb03bdbfafc37af2669570f89d1d512ebfb55c55e515dd9c69df9be65b", 16)
_RSA_PUBLIC_EXPONENT = 65537
_SHA256_DIGESTINFO_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")

_ATTESTATION_FIELDS = frozenset(
    {
        "schema_version",
        "key_id",
        "algorithm",
        "purpose",
        "governance_generation_id",
        "proof_context_digest",
        "genesis_trusted_scope_digest",
        "signature_b64",
    }
)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def canonical_attestation_material(
    *,
    governance_generation_id: str,
    proof_context_digest: str,
    genesis_trusted_scope_digest: str,
) -> dict[str, Any]:
    """Return the exact public material covered by the detached signature."""
    return {
        "algorithm": ROOT_ATTESTATION_ALGORITHM,
        "genesis_trusted_scope_digest": genesis_trusted_scope_digest,
        "governance_generation_id": governance_generation_id,
        "key_id": ROOT_ATTESTATION_KEY_ID,
        "proof_context_digest": proof_context_digest,
        "purpose": ROOT_ATTESTATION_PURPOSE,
        "schema_version": ROOT_ATTESTATION_SCHEMA_VERSION,
    }


def canonical_attestation_bytes(
    *,
    governance_generation_id: str,
    proof_context_digest: str,
    genesis_trusted_scope_digest: str,
) -> bytes:
    material = canonical_attestation_material(
        governance_generation_id=governance_generation_id,
        proof_context_digest=proof_context_digest,
        genesis_trusted_scope_digest=genesis_trusted_scope_digest,
    )
    return json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _rsa_pkcs1_v1_5_sha256_verify(message: bytes, signature: bytes) -> bool:
    """Verify RSA PKCS#1 v1.5 SHA-256 using the pinned public key only."""
    modulus_len = (_RSA_MODULUS.bit_length() + 7) // 8
    if len(signature) != modulus_len:
        return False
    signature_int = int.from_bytes(signature, "big")
    if signature_int <= 0 or signature_int >= _RSA_MODULUS:
        return False
    encoded = pow(signature_int, _RSA_PUBLIC_EXPONENT, _RSA_MODULUS).to_bytes(
        modulus_len, "big"
    )
    digest = hashlib.sha256(message).digest()
    digest_info = _SHA256_DIGESTINFO_PREFIX + digest
    padding_len = modulus_len - len(digest_info) - 3
    if padding_len < 8:
        return False
    expected = b"\x00\x01" + (b"\xff" * padding_len) + b"\x00" + digest_info
    return hmac.compare_digest(encoded, expected)


def validate_root_attestation(
    attestation: Mapping[str, Any] | None,
    *,
    governance_generation_id: str,
    proof_context_digest: str,
    genesis_trusted_scope_digest: str,
) -> list[str]:
    """Fail closed unless exact context/scope identity has the pinned V3 signature."""
    if not isinstance(attestation, Mapping):
        return ["ROOT_ATTESTATION_REQUIRED"]

    problems: list[str] = []
    if set(attestation.keys()) != _ATTESTATION_FIELDS:
        problems.append("ROOT_ATTESTATION_FIELDS_EXACT_REQUIRED")

    if attestation.get("schema_version") != ROOT_ATTESTATION_SCHEMA_VERSION:
        problems.append("ROOT_ATTESTATION_SCHEMA_MISMATCH")
    if attestation.get("key_id") != ROOT_ATTESTATION_KEY_ID:
        problems.append("ROOT_ATTESTATION_KEY_ID_MISMATCH")
    if attestation.get("algorithm") != ROOT_ATTESTATION_ALGORITHM:
        problems.append("ROOT_ATTESTATION_ALGORITHM_MISMATCH")
    if attestation.get("purpose") != ROOT_ATTESTATION_PURPOSE:
        problems.append("ROOT_ATTESTATION_PURPOSE_MISMATCH")
    if attestation.get("governance_generation_id") != governance_generation_id:
        problems.append("ROOT_ATTESTATION_GENERATION_MISMATCH")
    if attestation.get("proof_context_digest") != proof_context_digest:
        problems.append("ROOT_ATTESTATION_CONTEXT_DIGEST_MISMATCH")
    if attestation.get("genesis_trusted_scope_digest") != genesis_trusted_scope_digest:
        problems.append("ROOT_ATTESTATION_SCOPE_DIGEST_MISMATCH")

    if not _is_sha256(proof_context_digest):
        problems.append("ROOT_ATTESTATION_CONTEXT_DIGEST_INVALID")
    if not _is_sha256(genesis_trusted_scope_digest):
        problems.append("ROOT_ATTESTATION_SCOPE_DIGEST_INVALID")
    if problems:
        return sorted(set(problems))

    encoded_signature = attestation.get("signature_b64")
    if not isinstance(encoded_signature, str) or not encoded_signature:
        return ["ROOT_ATTESTATION_SIGNATURE_REQUIRED"]
    try:
        signature = base64.b64decode(encoded_signature, validate=True)
    except (binascii.Error, ValueError):
        return ["ROOT_ATTESTATION_SIGNATURE_ENCODING_INVALID"]

    message = canonical_attestation_bytes(
        governance_generation_id=governance_generation_id,
        proof_context_digest=proof_context_digest,
        genesis_trusted_scope_digest=genesis_trusted_scope_digest,
    )
    if not _rsa_pkcs1_v1_5_sha256_verify(message, signature):
        return ["ROOT_ATTESTATION_SIGNATURE_INVALID"]
    return []
