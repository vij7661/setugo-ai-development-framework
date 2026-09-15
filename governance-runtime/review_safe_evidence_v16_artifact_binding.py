"""V16 Slice 1 exact-validator-artifact binding extension.

Construction-stage only. This module does not make self-measurement an independent
runtime attestation. It binds exact source-byte identity into bootstrap-authorized,
pinned, issuer-signed evidence so ordinary verifier drift cannot silently reuse old
authority state. Independent runtime measurement remains required for qualification.
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
import binascii
import hashlib
from pathlib import Path
from typing import Any, Mapping, Sequence

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

import review_safe_evidence_v16_trust as base

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
VALIDATOR_BINDING_PROFILE_VERSION = 1
VALIDATOR_BINDING_SIGNATURE_DOMAIN = "RSE-V16:VALIDATOR-BINDING-ROOT:"
ARTIFACT_BOUND_RECORD_SIGNATURE_DOMAIN = "RSE-V16:ARTIFACT-BOUND-RECORD:"
SHA256_RE = base.SHA256_RE

BINDING_CERTIFICATE_FIELDS = frozenset({
    "schema_version", "object_type", "candidate_id", "registry_id",
    "registry_sequence", "registry_digest", "registry_chain_digest",
    "trust_set_id", "trust_set_digest", "validation_profile_digest",
    "validator_bundle_digest", "certificate_digest", "bootstrap_signatures",
})
BINDING_SIGNATURE_FIELDS = frozenset({"root_id", "key_id", "algorithm", "signature_b64"})
ARTIFACT_BOUND_RECORD_FIELDS = frozenset({
    "schema_version", "object_type", "validator_binding_digest",
    "validator_bundle_digest", "inner_record_digest", "inner_record",
    "signature_algorithm", "outer_signature_b64",
})


@dataclass(frozen=True)
class PinnedArtifactBoundHead:
    anchor_id: str
    registry_head: base.PinnedRegistryHead
    validator_binding_digest: str
    validator_bundle_digest: str
    registry_chain_digest: str


def _result(valid: bool, problems: list[str], ok: str, bad: str) -> dict[str, Any]:
    return {
        "state": ok if valid else bad,
        "valid": valid,
        "qualified": False,
        "implementation_qualification": "NOT_CLAIMED",
        "runtime_qualification": "NOT_CLAIMED",
        "authority_effect": AUTHORITY_EFFECT,
        "problems": sorted(set(problems)),
    }


def _sha(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.fullmatch(value))


def _plain_snapshot(value: Any, path: str = "$") -> Any:
    if value is None or isinstance(value, bool):
        return value
    if type(value) is int:
        if abs(value) > base.MAX_CANONICAL_INTEGER:
            raise base.CanonicalizationError(f"INTEGER_OUT_OF_CANONICAL_RANGE:{path}")
        return value
    if isinstance(value, str):
        if any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
            raise base.CanonicalizationError(f"LONE_SURROGATE_FORBIDDEN:{path}")
        return value
    if type(value) is dict:
        local = value.copy()
        out: dict[str, Any] = {}
        for key, item in local.items():
            if type(key) is not str:
                raise base.CanonicalizationError(f"NON_STRING_KEY:{path}")
            out[key] = _plain_snapshot(item, f"{path}.{key}")
        return out
    if type(value) is list:
        local = list(value)
        return [_plain_snapshot(item, f"{path}[{i}]") for i, item in enumerate(local)]
    if type(value) is tuple:
        local = tuple(value)
        return [_plain_snapshot(item, f"{path}[{i}]") for i, item in enumerate(local)]
    raise base.CanonicalizationError(f"NON_PLAIN_JSON_CONTAINER:{path}:{type(value).__name__}")


def _decode_b64(value: Any, size: int) -> bytes | None:
    if not isinstance(value, str):
        return None
    try:
        raw = base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, ValueError, binascii.Error):
        return None
    return raw if len(raw) == size else None


def _verify_ed25519(public_key_b64: str, signature_b64: str, message: bytes) -> bool:
    pub = _decode_b64(public_key_b64, base.ED25519_PUBLIC_KEY_BYTES)
    sig = _decode_b64(signature_b64, base.ED25519_SIGNATURE_BYTES)
    if pub is None or sig is None:
        return False
    try:
        Ed25519PublicKey.from_public_bytes(pub).verify(sig, message)
        return True
    except (InvalidSignature, ValueError):
        return False


def _source_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validator_bundle_material() -> dict[str, Any]:
    base_path = Path(base.__file__).resolve()
    binding_path = Path(__file__).resolve()
    if base_path.suffix != ".py" or binding_path.suffix != ".py":
        raise base.CanonicalizationError("VALIDATOR_SOURCE_PATH_MUST_BE_PY")
    return {
        "validator_binding_profile_version": VALIDATOR_BINDING_PROFILE_VERSION,
        "base_validator": {"name": base_path.name, "sha256": _source_digest(base_path)},
        "artifact_binding_validator": {"name": binding_path.name, "sha256": _source_digest(binding_path)},
        "validation_profile_digest": base.validation_profile_digest(),
        "binding_signature_domain": VALIDATOR_BINDING_SIGNATURE_DOMAIN,
        "artifact_bound_record_signature_domain": ARTIFACT_BOUND_RECORD_SIGNATURE_DOMAIN,
    }


def validator_bundle_digest() -> str:
    return base.canonical_sha256(validator_bundle_material())


def registry_chain_digest(registry_chain: Sequence[Mapping[str, Any]]) -> str:
    if type(registry_chain) not in {list, tuple}:
        raise base.CanonicalizationError("REGISTRY_CHAIN_CONTAINER_MUST_BE_LIST_OR_TUPLE")
    rows = list(registry_chain)
    digests: list[str] = []
    for i, row in enumerate(rows):
        snap = _plain_snapshot(row, f"$registry_chain[{i}]")
        if type(snap) is not dict or not _sha(snap.get("registry_digest")):
            raise base.CanonicalizationError(f"REGISTRY_CHAIN_DIGEST_MISSING:{i}")
        digests.append(snap["registry_digest"])
    if not digests:
        raise base.CanonicalizationError("REGISTRY_CHAIN_REQUIRED")
    return base.canonical_sha256(digests)


def _certificate_material(record: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in {"certificate_digest", "bootstrap_signatures"}}


def validator_binding_certificate_digest(record: Mapping[str, Any]) -> str:
    return base.canonical_sha256(_certificate_material(record))


def validator_binding_signature_message(
    certificate_digest: str, *, trust_set_digest: str,
    root_id: str, key_id: str, control_domain_id: str,
) -> bytes:
    if not _sha(certificate_digest) or not _sha(trust_set_digest):
        raise ValueError("VALIDATOR_BINDING_DIGEST_INVALID")
    return VALIDATOR_BINDING_SIGNATURE_DOMAIN.encode("ascii") + base.canonical_bytes({
        "certificate_digest": certificate_digest,
        "trust_set_digest": trust_set_digest,
        "root_id": root_id,
        "key_id": key_id,
        "control_domain_id": control_domain_id,
    })


def artifact_bound_record_signature_message(record: Mapping[str, Any]) -> bytes:
    return ARTIFACT_BOUND_RECORD_SIGNATURE_DOMAIN.encode("ascii") + base.canonical_bytes(
        {k: v for k, v in record.items() if k != "outer_signature_b64"}
    )


def _validate_artifact_head(
    head: PinnedArtifactBoundHead, *, local_bundle_digest: str,
    expected_registry_head: base.PinnedRegistryHead,
) -> list[str]:
    p: list[str] = []
    if type(head) is not PinnedArtifactBoundHead:
        return ["ARTIFACT_HEAD_TYPE_INVALID"]
    if not isinstance(head.anchor_id, str) or not head.anchor_id.strip():
        p.append("ARTIFACT_HEAD_ANCHOR_ID_REQUIRED")
    if head.registry_head != expected_registry_head:
        p.append("ARTIFACT_HEAD_REGISTRY_HEAD_MISMATCH")
    if not _sha(head.validator_binding_digest):
        p.append("ARTIFACT_HEAD_BINDING_DIGEST_INVALID")
    if head.validator_bundle_digest != local_bundle_digest:
        p.append("ARTIFACT_HEAD_VALIDATOR_BUNDLE_MISMATCH")
    if not _sha(head.validator_bundle_digest):
        p.append("ARTIFACT_HEAD_VALIDATOR_BUNDLE_DIGEST_INVALID")
    if not _sha(head.registry_chain_digest):
        p.append("ARTIFACT_HEAD_REGISTRY_CHAIN_DIGEST_INVALID")
    return p


def validate_validator_binding_certificate(
    record: Mapping[str, Any], *, registry_chain: Sequence[Mapping[str, Any]],
    bootstrap_trust: base.PinnedBootstrapTrustSet,
    expected_registry_head: base.PinnedRegistryHead,
    pinned_artifact_head: PinnedArtifactBoundHead,
    expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        cert = _plain_snapshot(record, "$binding_certificate")
        chain = [_plain_snapshot(r, f"$registry_chain[{i}]") for i, r in enumerate(list(registry_chain))]
        if type(cert) is not dict or not all(type(r) is dict for r in chain):
            raise base.CanonicalizationError("BINDING_CERT_OR_REGISTRY_NOT_OBJECT")
        local_bundle = validator_bundle_digest()
        local_profile = base.validation_profile_digest()
        chain_digest = registry_chain_digest(chain)
    except (base.CanonicalizationError, OSError) as exc:
        return _result(False, [f"VALIDATOR_BINDING_INPUT:{exc}"], "UNREACHABLE", "VALIDATOR_BINDING_CERTIFICATE_INVALID")

    p = _validate_artifact_head(
        pinned_artifact_head, local_bundle_digest=local_bundle,
        expected_registry_head=expected_registry_head,
    )
    trust_result = base.validate_bootstrap_trust_set(bootstrap_trust)
    if not trust_result["valid"]:
        p.extend(f"VALIDATOR_BINDING_TRUST:{x}" for x in trust_result["problems"])
    chain_result = base.validate_governance_key_registry_chain(
        chain, bootstrap_trust, expected_candidate_id=expected_candidate_id,
    )
    if not chain_result["valid"]:
        p.extend(f"VALIDATOR_BINDING_REGISTRY:{x}" for x in chain_result["problems"])

    if set(cert.keys()) != BINDING_CERTIFICATE_FIELDS:
        p.append("VALIDATOR_BINDING_CERTIFICATE_FIELDS_NOT_EXACT")
    if type(cert.get("schema_version")) is not int or cert.get("schema_version") != 1:
        p.append("VALIDATOR_BINDING_CERTIFICATE_SCHEMA_INVALID")
    if cert.get("object_type") != "VALIDATOR_ARTIFACT_BINDING":
        p.append("VALIDATOR_BINDING_CERTIFICATE_OBJECT_TYPE_INVALID")
    current = chain[-1] if chain else {}
    expected_pairs = {
        "candidate_id": expected_candidate_id,
        "registry_id": expected_registry_head.registry_id,
        "registry_sequence": expected_registry_head.sequence,
        "registry_digest": expected_registry_head.registry_digest,
        "registry_chain_digest": chain_digest,
        "trust_set_id": bootstrap_trust.trust_set_id,
        "trust_set_digest": bootstrap_trust.trust_set_digest,
        "validation_profile_digest": local_profile,
        "validator_bundle_digest": local_bundle,
    }
    for key, expected in expected_pairs.items():
        if cert.get(key) != expected:
            p.append(f"VALIDATOR_BINDING_CERTIFICATE_{key.upper()}_MISMATCH")
    if current:
        if current.get("registry_digest") != expected_registry_head.registry_digest:
            p.append("VALIDATOR_BINDING_CURRENT_REGISTRY_NOT_PINNED_HEAD")
        if current.get("authority_policy_digest") != local_profile:
            p.append("VALIDATOR_BINDING_CURRENT_PROFILE_MISMATCH")
    if pinned_artifact_head.registry_chain_digest != chain_digest:
        p.append("VALIDATOR_BINDING_PINNED_CHAIN_DIGEST_MISMATCH")
    if cert.get("certificate_digest") != pinned_artifact_head.validator_binding_digest:
        p.append("VALIDATOR_BINDING_PINNED_CERTIFICATE_DIGEST_MISMATCH")
    supplied_digest = cert.get("certificate_digest")
    if not _sha(supplied_digest):
        p.append("VALIDATOR_BINDING_CERTIFICATE_DIGEST_INVALID")
    else:
        try:
            if supplied_digest != validator_binding_certificate_digest(cert):
                p.append("VALIDATOR_BINDING_CERTIFICATE_DIGEST_MISMATCH")
        except base.CanonicalizationError:
            p.append("VALIDATOR_BINDING_CERTIFICATE_CANONICALIZATION_FAILED")

    signatures = cert.get("bootstrap_signatures")
    roots = {(r.root_id, r.key_id): r for r in bootstrap_trust.roots}
    domains: set[str] = set()
    seen: set[tuple[str, str]] = set()
    if type(signatures) is not list or not signatures:
        p.append("VALIDATOR_BINDING_BOOTSTRAP_SIGNATURES_REQUIRED")
    else:
        for i, sig in enumerate(signatures):
            if type(sig) is not dict or set(sig.keys()) != BINDING_SIGNATURE_FIELDS:
                p.append(f"VALIDATOR_BINDING_SIGNATURE_MALFORMED:{i}")
                continue
            pair = (sig.get("root_id"), sig.get("key_id"))
            if pair in seen:
                p.append(f"VALIDATOR_BINDING_SIGNATURE_DUPLICATE:{i}")
                continue
            seen.add(pair)  # type: ignore[arg-type]
            root = roots.get(pair)  # type: ignore[arg-type]
            if root is None:
                p.append(f"VALIDATOR_BINDING_SIGNER_UNKNOWN:{i}")
                continue
            try:
                msg = validator_binding_signature_message(
                    str(supplied_digest), trust_set_digest=bootstrap_trust.trust_set_digest,
                    root_id=root.root_id, key_id=root.key_id,
                    control_domain_id=root.control_domain_id,
                )
            except ValueError:
                p.append(f"VALIDATOR_BINDING_SIGNATURE_MESSAGE_INVALID:{i}")
                continue
            if sig.get("algorithm") != "ED25519" or not _verify_ed25519(
                root.public_key_b64, str(sig.get("signature_b64", "")), msg,
            ):
                p.append(f"VALIDATOR_BINDING_SIGNATURE_INVALID:{i}")
                continue
            domains.add(root.control_domain_id)
    if len(domains) < bootstrap_trust.threshold_control_domains:
        p.append("VALIDATOR_BINDING_BOOTSTRAP_THRESHOLD_NOT_MET")

    valid = not p
    out = _result(valid, p, "VALIDATOR_ARTIFACT_BINDING_CERTIFICATE_VALID", "VALIDATOR_BINDING_CERTIFICATE_INVALID")
    out.update({
        "validator_bundle_digest": local_bundle,
        "registry_chain_digest": chain_digest,
        "artifact_measurement": "LOCAL_SOURCE_BYTES_SELF_MEASURED",
        "artifact_measurement_independently_proven": False,
        "bootstrap_authenticated_control_domains": sorted(domains),
    })
    return out


def verify_artifact_bound_governance_record(
    record: Mapping[str, Any], *, binding_certificate: Mapping[str, Any],
    registry_chain: Sequence[Mapping[str, Any]],
    bootstrap_trust: base.PinnedBootstrapTrustSet,
    pinned_artifact_head: PinnedArtifactBoundHead,
    expected_candidate_id: str, expected_generation_id: str,
    expected_record_type: str, expected_snapshot_id: str | None = None,
    forbidden_control_domain_ids: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    try:
        outer = _plain_snapshot(record, "$artifact_bound_record")
        chain = [_plain_snapshot(r, f"$registry_chain[{i}]") for i, r in enumerate(list(registry_chain))]
        cert = _plain_snapshot(binding_certificate, "$binding_certificate")
        if type(outer) is not dict or type(cert) is not dict or not all(type(r) is dict for r in chain):
            raise base.CanonicalizationError("ARTIFACT_BOUND_INPUT_NOT_OBJECT")
        local_bundle = validator_bundle_digest()
        local_profile = base.validation_profile_digest()
        chain_digest = registry_chain_digest(chain)
    except (base.CanonicalizationError, OSError) as exc:
        return _result(False, [f"ARTIFACT_BOUND_INPUT:{exc}"], "UNREACHABLE", "ARTIFACT_BOUND_RECORD_INVALID")

    p: list[str] = []
    if any(r.get("authority_policy_digest") != local_profile for r in chain):
        p.append("MIXED_VALIDATION_PROFILE_CHAIN_FORBIDDEN")
    binding_result = validate_validator_binding_certificate(
        cert, registry_chain=chain, bootstrap_trust=bootstrap_trust,
        expected_registry_head=pinned_artifact_head.registry_head,
        pinned_artifact_head=pinned_artifact_head,
        expected_candidate_id=expected_candidate_id,
    )
    if not binding_result["valid"]:
        p.extend(f"ARTIFACT_BOUND_BINDING:{x}" for x in binding_result["problems"])

    if set(outer.keys()) != ARTIFACT_BOUND_RECORD_FIELDS:
        p.append("ARTIFACT_BOUND_RECORD_FIELDS_NOT_EXACT")
    if type(outer.get("schema_version")) is not int or outer.get("schema_version") != 1:
        p.append("ARTIFACT_BOUND_RECORD_SCHEMA_INVALID")
    if outer.get("object_type") != "ARTIFACT_BOUND_SIGNED_GOVERNANCE_RECORD":
        p.append("ARTIFACT_BOUND_RECORD_OBJECT_TYPE_INVALID")
    if outer.get("validator_binding_digest") != pinned_artifact_head.validator_binding_digest:
        p.append("ARTIFACT_BOUND_RECORD_BINDING_DIGEST_MISMATCH")
    if outer.get("validator_bundle_digest") != local_bundle:
        p.append("ARTIFACT_BOUND_RECORD_VALIDATOR_BUNDLE_MISMATCH")
    if pinned_artifact_head.registry_chain_digest != chain_digest:
        p.append("ARTIFACT_BOUND_RECORD_CHAIN_DIGEST_MISMATCH")

    inner = outer.get("inner_record")
    if type(inner) is not dict:
        p.append("ARTIFACT_BOUND_INNER_RECORD_REQUIRED")
        inner = {}
    supplied_inner_digest = outer.get("inner_record_digest")
    if not _sha(supplied_inner_digest):
        p.append("ARTIFACT_BOUND_INNER_RECORD_DIGEST_INVALID")
    else:
        try:
            if supplied_inner_digest != base.canonical_sha256(inner):
                p.append("ARTIFACT_BOUND_INNER_RECORD_DIGEST_MISMATCH")
        except base.CanonicalizationError:
            p.append("ARTIFACT_BOUND_INNER_RECORD_CANONICALIZATION_FAILED")

    base_result = base.verify_signed_governance_record(
        inner, registry_chain=chain, bootstrap_trust=bootstrap_trust,
        expected_current_registry_head=pinned_artifact_head.registry_head,
        expected_candidate_id=expected_candidate_id,
        expected_generation_id=expected_generation_id,
        expected_record_type=expected_record_type,
        expected_snapshot_id=expected_snapshot_id,
        forbidden_control_domain_ids=forbidden_control_domain_ids,
    )
    if not base_result["valid"]:
        p.extend(f"ARTIFACT_BOUND_BASE:{x}" for x in base_result["problems"])

    outer_signature_ok = False
    if outer.get("signature_algorithm") != "ED25519":
        p.append("ARTIFACT_BOUND_SIGNATURE_ALGORITHM_UNSUPPORTED")
    current = chain[-1] if chain else {}
    key = None
    if base_result["valid"]:
        for candidate in current.get("keys", []) if type(current.get("keys")) is list else []:
            if type(candidate) is dict and candidate.get("key_id") == inner.get("key_id"):
                key = candidate
                break
    if key is None:
        p.append("ARTIFACT_BOUND_ISSUER_KEY_NOT_RESOLVED")
    else:
        try:
            msg = artifact_bound_record_signature_message(outer)
        except base.CanonicalizationError:
            p.append("ARTIFACT_BOUND_RECORD_CANONICALIZATION_FAILED")
        else:
            outer_signature_ok = _verify_ed25519(
                str(key.get("public_key_b64", "")), str(outer.get("outer_signature_b64", "")), msg,
            )
            if not outer_signature_ok:
                p.append("ARTIFACT_BOUND_OUTER_SIGNATURE_INVALID")

    valid = not p
    out = _result(valid, p, "ARTIFACT_BOUND_GOVERNANCE_RECORD_VALID", "ARTIFACT_BOUND_RECORD_INVALID")
    out.update({
        "base_record_valid": bool(base_result.get("valid")),
        "binding_certificate_valid": bool(binding_result.get("valid")),
        "outer_signature_verified": outer_signature_ok,
        "validator_bundle_digest": local_bundle,
        "registry_chain_digest": chain_digest,
        "artifact_measurement": "LOCAL_SOURCE_BYTES_SELF_MEASURED",
        "artifact_measurement_independently_proven": False,
    })
    return out
