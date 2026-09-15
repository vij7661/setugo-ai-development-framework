"""V16 Slice 1 authenticated trust foundation.

Construction-stage only. Content integrity, issuer authenticity, validation-policy
identity, registry currentness, and out-of-band trust provisioning are deliberately
separate. All validation results remain non-authoritative construction evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
import binascii
import hashlib
import json
import re
import unicodedata
from typing import Any, Iterable, Mapping, Sequence

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
except Exception:  # pragma: no cover - explicit fail-closed provider boundary
    InvalidSignature = Exception  # type: ignore[assignment]
    Ed25519PublicKey = None  # type: ignore[assignment]

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
IMPLEMENTATION_QUALIFICATION = "NOT_CLAIMED"
RUNTIME_QUALIFICATION = "NOT_CLAIMED"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ED25519_PUBLIC_KEY_BYTES = 32
ED25519_SIGNATURE_BYTES = 64
MAX_CANONICAL_INTEGER = (2**53) - 1
AUTHORITY_POLICY_VERSION = 2
VALIDATION_PROFILE_VERSION = 1
CANONICALIZATION_PROFILE_ID = "RSE-V16-CJSON-NFC-CODEPOINT-V1"
IDENTIFIER_PROFILE_ID = "NFC-ALREADY-CANONICAL-NONEMPTY-V1"
REGISTRY_SIGNATURE_DOMAIN = "RSE-V16:KEY-REGISTRY-ROOT:"
SIGNED_RECORD_SIGNATURE_DOMAIN = "RSE-V16:SIGNED-RECORD:"
SUPPORTED_SIGNATURE_ALGORITHMS = ("ED25519",)

# Kept mutable for compatibility with existing construction tests that simulate
# verifier-code drift between calls. Every validation call snapshots this mapping
# exactly once; no load-bearing decision re-reads the live mapping after ingress.
RECORD_TYPE_REQUIRED_ROLE: dict[str, str] = {
    "GOVERNANCE_GENERATION_WITNESS": "GOVERNANCE_GENERATION_WITNESS_AUTHORITY",
    "REVIEWER_QUALIFICATION": "REVIEWER_QUALIFICATION_AUTHORITY",
    "EVIDENCE_UNIVERSE_DERIVATION": "EVIDENCE_UNIVERSE_DERIVATION_AUTHORITY",
    "OBLIGATION_MATERIALITY": "OBLIGATION_MATERIALITY_AUTHORITY",
    "RAW_EVIDENCE_CAPTURE": "RAW_EVIDENCE_CAPTURE_AUTHORITY",
    "GOVERNED_NA_PROOF": "NA_PROOF_AUTHORITY",
    "NA_CHALLENGE_RESOLUTION": "NA_CHALLENGE_RESOLUTION_AUTHORITY",
    "HIDDEN_MONITOR_EXECUTION": "MONITOR_EXECUTION_AUTHORITY",
    "HIDDEN_MONITOR_COVERAGE": "COVERAGE_CERTIFICATE_AUTHORITY",
    "SEALED_REVIEW_SNAPSHOT": "SNAPSHOT_WRITER_AUTHORITY",
    "SNAPSHOT_WITNESS": "SNAPSHOT_WITNESS_AUTHORITY",
    "CLEAN_ROOM_ATTESTATION": "CLEAN_ROOM_ATTESTATION_AUTHORITY",
    "REVIEW_RESPONSE_RECEIPT": "REVIEW_RESPONSE_RECEIPT_AUTHORITY",
    "BLOCKER_RESOLUTION": "BLOCKER_RESOLUTION_AUTHORITY",
    "EFFECT_TOKEN_ISSUANCE": "EFFECT_TOKEN_ISSUER_AUTHORITY",
    "EFFECT_GATEWAY_VERIFICATION": "EFFECT_GATEWAY_AUTHORITY",
    "RESIDUAL_TRUST_ACCEPTANCE": "RESIDUAL_TRUST_ACCEPTANCE_AUTHORITY",
    "ADJUDICATION": "ADJUDICATION_AUTHORITY",
    "PROJECTION_COMPILATION": "PROJECTION_COMPILER_AUTHORITY",
    "PROJECTION_VERIFICATION": "PROJECTION_VERIFIER_AUTHORITY",
    "DISCLOSURE_CERTIFICATION": "DISCLOSURE_CERTIFIER_AUTHORITY",
    "UNIVERSE_CHALLENGE": "UNIVERSE_CHALLENGE_AUTHORITY",
}
ROLE_VOCABULARY = frozenset(RECORD_TYPE_REQUIRED_ROLE.values())

REGISTRY_TOP_LEVEL_FIELDS = frozenset({
    "schema_version", "object_type", "registry_id", "candidate_id", "generation_id",
    "trust_set_id", "trust_set_digest", "authority_policy_digest", "sequence",
    "predecessor_registry_digest", "keys", "registry_digest", "bootstrap_signatures",
})
REGISTRY_KEY_FIELDS = frozenset({
    "issuer_id", "key_id", "control_domain_id", "algorithm", "public_key_b64",
    "roles", "state", "valid_from_registry_sequence", "revoked_at_registry_sequence",
})
REGISTRY_SIGNATURE_FIELDS = frozenset({"root_id", "key_id", "algorithm", "signature_b64"})
SIGNED_RECORD_FIELDS = frozenset({
    "schema_version", "object_type", "record_type", "record_id", "candidate_id",
    "generation_id", "snapshot_id", "trust_set_id", "trust_set_digest",
    "authority_policy_digest", "issued_registry_sequence", "issued_registry_digest",
    "issuer_id", "key_id", "required_role", "payload_digest", "payload",
    "signature_algorithm", "signature_b64",
})


class CanonicalizationError(ValueError):
    pass


@dataclass(frozen=True)
class BootstrapRoot:
    root_id: str
    key_id: str
    control_domain_id: str
    public_key_b64: str
    algorithm: str = "ED25519"


@dataclass(frozen=True)
class PinnedBootstrapTrustSet:
    trust_set_id: str
    threshold_control_domains: int
    roots: tuple[BootstrapRoot, ...]
    candidate_control_domain_ids: frozenset[str] = frozenset()
    trust_set_digest: str = ""


@dataclass(frozen=True)
class PinnedRegistryHead:
    anchor_id: str
    trust_set_id: str
    trust_set_digest: str
    authority_policy_digest: str
    registry_id: str
    candidate_id: str
    sequence: int
    generation_id: str
    registry_digest: str


@dataclass(frozen=True)
class _RegistryValidation:
    valid: bool
    problems: tuple[str, ...]
    current: dict[str, Any] | None
    snapshots_by_sequence: Mapping[int, dict[str, Any]]
    authenticated_bootstrap_domains: tuple[str, ...]


def _result(valid: bool, problems: Iterable[str], ok: str, bad: str) -> dict[str, Any]:
    return {
        "state": ok if valid else bad,
        "valid": valid,
        "qualified": False,
        "implementation_qualification": IMPLEMENTATION_QUALIFICATION,
        "runtime_qualification": RUNTIME_QUALIFICATION,
        "authority_effect": AUTHORITY_EFFECT,
        "problems": sorted(set(problems)),
    }


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _exact_int(value: Any, *, minimum: int = 0) -> bool:
    return type(value) is int and minimum <= value <= MAX_CANONICAL_INTEGER


def _schema_one(value: Any) -> bool:
    return type(value) is int and value == 1


def _sha256_hex(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.fullmatch(value))


def _b64(value: Any, size: int) -> bytes | None:
    if not isinstance(value, str):
        return None
    try:
        raw = base64.b64decode(value.encode("ascii"), validate=True)
    except (ValueError, UnicodeEncodeError, binascii.Error):
        return None
    return raw if len(raw) == size else None


def _norm_string(value: str, path: str) -> str:
    normalized = unicodedata.normalize("NFC", value)
    if any(0xD800 <= ord(ch) <= 0xDFFF for ch in normalized):
        raise CanonicalizationError(f"LONE_SURROGATE_FORBIDDEN:{path}")
    return normalized


def _escape_canonical_string(value: str, path: str) -> str:
    value = _norm_string(value, path)
    out = ['"']
    named = {"\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f", "\r": "\\r"}
    for ch in value:
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch in named:
            out.append(named[ch])
        elif ord(ch) < 0x20:
            out.append(f"\\u{ord(ch):04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _canonical_text(value: Any, path: str = "$") -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if type(value) is int:
        if abs(value) > MAX_CANONICAL_INTEGER:
            raise CanonicalizationError(f"INTEGER_OUT_OF_CANONICAL_RANGE:{path}")
        return str(value)
    if isinstance(value, float):
        raise CanonicalizationError(f"FLOAT_FORBIDDEN:{path}")
    if isinstance(value, str):
        return _escape_canonical_string(value, path)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(_canonical_text(item, f"{path}[{i}]") for i, item in enumerate(value)) + "]"
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            if not isinstance(raw_key, str):
                raise CanonicalizationError(f"NON_STRING_KEY:{path}")
            key = _norm_string(raw_key, f"{path}.<key>")
            if key in normalized:
                raise CanonicalizationError(f"NORMALIZED_KEY_COLLISION:{path}.{key}")
            normalized[key] = raw_value
        parts = []
        for key in sorted(normalized):  # Unicode scalar/code-point ascending after NFC.
            parts.append(
                _escape_canonical_string(key, f"{path}.<key>") + ":" +
                _canonical_text(normalized[key], f"{path}.{key}")
            )
        return "{" + ",".join(parts) + "}"
    raise CanonicalizationError(f"UNSUPPORTED_TYPE:{path}:{type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    return _canonical_text(value).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _preserve_json_value(value: Any, path: str = "$") -> Any:
    if value is None or isinstance(value, bool):
        return value
    if type(value) is int:
        if abs(value) > MAX_CANONICAL_INTEGER:
            raise CanonicalizationError(f"INTEGER_OUT_OF_CANONICAL_RANGE:{path}")
        return value
    if isinstance(value, str):
        if any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
            raise CanonicalizationError(f"LONE_SURROGATE_FORBIDDEN:{path}")
        return value
    if type(value) is list:
        return [_preserve_json_value(item, f"{path}[{i}]") for i, item in enumerate(value)]
    if type(value) is dict:
        return {key: _preserve_json_value(item, f"{path}.{key}") for key, item in value.items()}
    raise CanonicalizationError(f"UNSUPPORTED_JSON_TYPE:{path}:{type(value).__name__}")


def load_strict_json(raw: bytes | str) -> Any:
    """Parse strict JSON while preserving string value spellings.

    Object keys must already be NFC and normalized duplicates are rejected. String
    values are *not* silently normalized; load-bearing identifier validators reject
    non-NFC spellings at their semantic boundary.
    """
    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="strict")
    elif isinstance(raw, str):
        text = raw
    else:
        raise CanonicalizationError("STRICT_JSON_INPUT_MUST_BE_BYTES_OR_STRING")

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            nkey = _norm_string(key, "$.<key>")
            if key != nkey:
                raise CanonicalizationError(f"NONCANONICAL_OBJECT_KEY:{key}")
            if nkey in out:
                raise CanonicalizationError(f"DUPLICATE_OR_NORMALIZED_KEY:{nkey}")
            out[nkey] = value
        return out

    def reject_float(token: str) -> Any:
        raise CanonicalizationError(f"FLOAT_FORBIDDEN:{token}")

    def parse_int(token: str) -> int:
        value = int(token, 10)
        if abs(value) > MAX_CANONICAL_INTEGER:
            raise CanonicalizationError(f"INTEGER_OUT_OF_CANONICAL_RANGE:{token}")
        return value

    def reject_constant(token: str) -> Any:
        raise CanonicalizationError(f"NONFINITE_NUMBER_FORBIDDEN:{token}")

    try:
        parsed = json.loads(
            text, object_pairs_hook=pairs_hook, parse_float=reject_float,
            parse_int=parse_int, parse_constant=reject_constant,
        )
    except CanonicalizationError:
        raise
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise CanonicalizationError("STRICT_JSON_PARSE_FAILED") from exc
    return _preserve_json_value(parsed)


def _owned_json_snapshot(value: Any, path: str = "$") -> Any:
    """Copy caller-owned data once into plain owned JSON containers.

    Custom Mapping/Sequence objects are rejected. For exact dict/list containers a
    shallow C-level copy is taken before recursion, so later caller mutation cannot
    change the state used after validation.
    """
    if value is None or isinstance(value, bool):
        return value
    if type(value) is int:
        if abs(value) > MAX_CANONICAL_INTEGER:
            raise CanonicalizationError(f"INTEGER_OUT_OF_CANONICAL_RANGE:{path}")
        return value
    if isinstance(value, str):
        if any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
            raise CanonicalizationError(f"LONE_SURROGATE_FORBIDDEN:{path}")
        return value
    if type(value) is dict:
        local = value.copy()
        out: dict[str, Any] = {}
        for key, item in local.items():
            if type(key) is not str:
                raise CanonicalizationError(f"NON_STRING_KEY:{path}")
            out[key] = _owned_json_snapshot(item, f"{path}.{key}")
        return out
    if type(value) is list:
        local = list(value)
        return [_owned_json_snapshot(item, f"{path}[{i}]") for i, item in enumerate(local)]
    if type(value) is tuple:
        local = tuple(value)
        return [_owned_json_snapshot(item, f"{path}[{i}]") for i, item in enumerate(local)]
    raise CanonicalizationError(f"NON_PLAIN_JSON_CONTAINER:{path}:{type(value).__name__}")


def _snapshot_registry_chain(registry_chain: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    if type(registry_chain) not in {list, tuple}:
        raise CanonicalizationError("REGISTRY_CHAIN_CONTAINER_MUST_BE_LIST_OR_TUPLE")
    local = list(registry_chain)
    out: list[dict[str, Any]] = []
    for idx, row in enumerate(local):
        snap = _owned_json_snapshot(row, f"$registry_chain[{idx}]")
        if type(snap) is not dict:
            raise CanonicalizationError(f"REGISTRY_RECORD_MUST_BE_OBJECT:{idx}")
        out.append(snap)
    return out


def _canonical_identifier(value: Any) -> bool:
    if not _nonempty(value):
        return False
    try:
        return value == _norm_string(value, "identifier")
    except CanonicalizationError:
        return False


def _require_identifier(problems: list[str], value: Any, code: str, *, allow_none: bool = False) -> None:
    if allow_none and value is None:
        return
    if not _nonempty(value):
        problems.append(f"{code}_REQUIRED")
    elif not _canonical_identifier(value):
        problems.append(f"{code}_NOT_CANONICAL_NFC")


def _policy_snapshot(mapping: Mapping[str, str] | None = None) -> dict[str, str]:
    source = RECORD_TYPE_REQUIRED_ROLE if mapping is None else mapping
    snap = dict(source)
    for key, value in snap.items():
        if type(key) is not str or type(value) is not str:
            raise CanonicalizationError("AUTHORITY_POLICY_KEY_VALUE_MUST_BE_STRING")
        if not _canonical_identifier(key) or not _canonical_identifier(value):
            raise CanonicalizationError("AUTHORITY_POLICY_IDENTIFIER_NOT_CANONICAL_NFC")
    return snap


def authority_policy_material(mapping: Mapping[str, str] | None = None) -> dict[str, Any]:
    policy = _policy_snapshot(mapping)
    return {
        "authority_policy_version": AUTHORITY_POLICY_VERSION,
        "record_type_required_role": policy,
    }


def validation_profile_material(mapping: Mapping[str, str] | None = None) -> dict[str, Any]:
    policy = _policy_snapshot(mapping)
    return {
        "validation_profile_version": VALIDATION_PROFILE_VERSION,
        "canonicalization_profile": {
            "id": CANONICALIZATION_PROFILE_ID,
            "unicode_normalization": "NFC",
            "object_key_order": "UNICODE_CODEPOINT_ASCENDING_AFTER_NFC",
            "string_encoding": "UTF8_JSON_MINIMAL_ESCAPES_LOWERCASE_U00XX",
            "float_policy": "FORBIDDEN",
            "integer_min": -MAX_CANONICAL_INTEGER,
            "integer_max": MAX_CANONICAL_INTEGER,
        },
        "identifier_profile_id": IDENTIFIER_PROFILE_ID,
        "schema_version_rule": "EXACT_INT_1",
        "registry_top_level_fields": sorted(REGISTRY_TOP_LEVEL_FIELDS),
        "registry_key_fields": sorted(REGISTRY_KEY_FIELDS),
        "registry_signature_fields": sorted(REGISTRY_SIGNATURE_FIELDS),
        "signed_record_fields": sorted(SIGNED_RECORD_FIELDS),
        "supported_signature_algorithms": list(SUPPORTED_SIGNATURE_ALGORITHMS),
        "registry_signature_domain": REGISTRY_SIGNATURE_DOMAIN,
        "signed_record_signature_domain": SIGNED_RECORD_SIGNATURE_DOMAIN,
        "role_vocabulary": sorted(ROLE_VOCABULARY),
        "authority_policy": {
            "version": AUTHORITY_POLICY_VERSION,
            "record_type_required_role": policy,
        },
    }


def validation_profile_digest(mapping: Mapping[str, str] | None = None) -> str:
    return canonical_sha256(validation_profile_material(mapping))


def authority_policy_digest(mapping: Mapping[str, str] | None = None) -> str:
    """Schema-v1 compatibility name for the full load-bearing validation profile."""
    return validation_profile_digest(mapping)


def bootstrap_trust_policy_material(trust: PinnedBootstrapTrustSet) -> dict[str, Any]:
    roots = sorted(
        ({
            "root_id": r.root_id,
            "key_id": r.key_id,
            "control_domain_id": r.control_domain_id,
            "public_key_b64": r.public_key_b64,
            "algorithm": r.algorithm,
        } for r in trust.roots),
        key=lambda row: canonical_bytes(row),
    )
    return {
        "trust_set_id": trust.trust_set_id,
        "threshold_control_domains": trust.threshold_control_domains,
        "roots": roots,
        "candidate_control_domain_ids": sorted(trust.candidate_control_domain_ids),
    }


def bootstrap_trust_set_digest(trust: PinnedBootstrapTrustSet) -> str:
    return canonical_sha256(bootstrap_trust_policy_material(trust))


def _registry_material(record: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in {"registry_digest", "bootstrap_signatures"}}


def registry_digest(record: Mapping[str, Any]) -> str:
    return canonical_sha256(_registry_material(record))


def registry_signature_message(
    digest_hex: str, *, trust_set_id: str, trust_set_digest: str,
    root_id: str, key_id: str, control_domain_id: str,
) -> bytes:
    if not _sha256_hex(digest_hex):
        raise ValueError("REGISTRY_DIGEST_INVALID")
    if not _sha256_hex(trust_set_digest):
        raise ValueError("TRUST_SET_DIGEST_INVALID")
    return REGISTRY_SIGNATURE_DOMAIN.encode("ascii") + canonical_bytes({
        "trust_set_id": trust_set_id,
        "trust_set_digest": trust_set_digest,
        "root_id": root_id,
        "key_id": key_id,
        "control_domain_id": control_domain_id,
        "registry_digest": digest_hex,
    })


def signed_record_signature_message(record: Mapping[str, Any]) -> bytes:
    return SIGNED_RECORD_SIGNATURE_DOMAIN.encode("ascii") + canonical_bytes(
        {k: v for k, v in record.items() if k != "signature_b64"}
    )


def _verify_ed25519(public_key_b64: str, signature_b64: str, message: bytes) -> bool:
    if Ed25519PublicKey is None:
        return False
    pub = _b64(public_key_b64, ED25519_PUBLIC_KEY_BYTES)
    sig = _b64(signature_b64, ED25519_SIGNATURE_BYTES)
    if pub is None or sig is None:
        return False
    try:
        Ed25519PublicKey.from_public_bytes(pub).verify(sig, message)
        return True
    except (InvalidSignature, ValueError):
        return False


def validate_bootstrap_trust_set(trust: PinnedBootstrapTrustSet) -> dict[str, Any]:
    p: list[str] = []
    if type(trust) is not PinnedBootstrapTrustSet:
        return _result(False, ["BOOTSTRAP_TRUST_SET_TYPE_INVALID"], "UNREACHABLE", "BOOTSTRAP_TRUST_SET_INVALID")
    if type(trust.roots) is not tuple:
        p.append("BOOTSTRAP_ROOT_CONTAINER_MUST_BE_TUPLE")
    if type(trust.candidate_control_domain_ids) is not frozenset:
        p.append("BOOTSTRAP_CANDIDATE_DOMAIN_CONTAINER_MUST_BE_FROZENSET")
    if p:
        return _result(False, p, "UNREACHABLE", "BOOTSTRAP_TRUST_SET_INVALID")
    if not all(type(root) is BootstrapRoot for root in trust.roots):
        return _result(False, ["BOOTSTRAP_ROOT_TYPE_INVALID"], "UNREACHABLE", "BOOTSTRAP_TRUST_SET_INVALID")

    _require_identifier(p, trust.trust_set_id, "BOOTSTRAP_TRUST_SET_ID")
    if not _exact_int(trust.threshold_control_domains, minimum=2):
        p.append("BOOTSTRAP_THRESHOLD_MIN_TWO_DOMAINS")
    if not trust.roots:
        p.append("BOOTSTRAP_ROOTS_REQUIRED")
    if not _sha256_hex(trust.trust_set_digest):
        p.append("BOOTSTRAP_TRUST_SET_DIGEST_INVALID")
    else:
        try:
            if trust.trust_set_digest != bootstrap_trust_set_digest(trust):
                p.append("BOOTSTRAP_TRUST_SET_DIGEST_MISMATCH")
        except CanonicalizationError:
            p.append("BOOTSTRAP_TRUST_SET_CANONICALIZATION_FAILED")

    root_ids: set[str] = set()
    key_ids: set[str] = set()
    public_keys: set[bytes] = set()
    domains: set[str] = set()
    for i, root in enumerate(trust.roots):
        _require_identifier(p, root.root_id, f"BOOTSTRAP_ROOT_ID:{i}")
        _require_identifier(p, root.key_id, f"BOOTSTRAP_KEY_ID:{i}")
        _require_identifier(p, root.control_domain_id, f"BOOTSTRAP_CONTROL_DOMAIN:{i}")
        if root.algorithm != "ED25519":
            p.append(f"BOOTSTRAP_ALGORITHM_UNSUPPORTED:{i}")
        pub = _b64(root.public_key_b64, ED25519_PUBLIC_KEY_BYTES)
        if pub is None:
            p.append(f"BOOTSTRAP_PUBLIC_KEY_INVALID:{i}")
        elif pub in public_keys:
            p.append(f"BOOTSTRAP_PUBLIC_KEY_REUSE_FORBIDDEN:{i}")
        else:
            public_keys.add(pub)
        if root.root_id in root_ids:
            p.append(f"BOOTSTRAP_ROOT_ID_DUPLICATE:{root.root_id}")
        if root.key_id in key_ids:
            p.append(f"BOOTSTRAP_KEY_ID_DUPLICATE:{root.key_id}")
        root_ids.add(root.root_id)
        key_ids.add(root.key_id)
        if root.control_domain_id in trust.candidate_control_domain_ids:
            p.append(f"BOOTSTRAP_ROOT_CANDIDATE_CONTROLLED:{root.root_id}")
        if _canonical_identifier(root.control_domain_id):
            domains.add(root.control_domain_id)

    for domain in trust.candidate_control_domain_ids:
        _require_identifier(p, domain, "BOOTSTRAP_CANDIDATE_CONTROL_DOMAIN")
    if _exact_int(trust.threshold_control_domains, minimum=2) and trust.threshold_control_domains > len(domains):
        p.append("BOOTSTRAP_THRESHOLD_EXCEEDS_DISTINCT_DOMAINS")

    out = _result(not p, p, "BOOTSTRAP_TRUST_SET_STRUCTURALLY_VALID", "BOOTSTRAP_TRUST_SET_INVALID")
    out.update({
        "trust_set_digest": trust.trust_set_digest,
        "trust_anchor_origin": "OUT_OF_BAND_PINNED_CONFIG_REQUIRED",
        "trust_anchor_provisioning_proven": False,
        "distinct_root_control_domains": sorted(domains),
    })
    return out


def _validate_pinned_registry_head_with_profile(
    head: PinnedRegistryHead, trust: PinnedBootstrapTrustSet,
    *, expected_candidate_id: str, profile_digest: str,
) -> dict[str, Any]:
    p: list[str] = []
    if type(head) is not PinnedRegistryHead:
        return _result(False, ["REGISTRY_HEAD_TYPE_INVALID"], "UNREACHABLE", "PINNED_REGISTRY_HEAD_INVALID")
    _require_identifier(p, head.anchor_id, "REGISTRY_HEAD_ANCHOR_ID")
    _require_identifier(p, head.trust_set_id, "REGISTRY_HEAD_TRUST_SET_ID")
    _require_identifier(p, head.registry_id, "REGISTRY_HEAD_REGISTRY_ID")
    _require_identifier(p, head.candidate_id, "REGISTRY_HEAD_CANDIDATE_ID")
    _require_identifier(p, head.generation_id, "REGISTRY_HEAD_GENERATION_ID")
    _require_identifier(p, expected_candidate_id, "EXPECTED_CANDIDATE_ID")
    if head.trust_set_id != trust.trust_set_id:
        p.append("REGISTRY_HEAD_TRUST_SET_MISMATCH")
    if head.trust_set_digest != trust.trust_set_digest:
        p.append("REGISTRY_HEAD_TRUST_SET_DIGEST_MISMATCH")
    if not _sha256_hex(head.trust_set_digest):
        p.append("REGISTRY_HEAD_TRUST_SET_DIGEST_INVALID")
    if head.authority_policy_digest != profile_digest:
        p.append("REGISTRY_HEAD_AUTHORITY_POLICY_DIGEST_MISMATCH")
    if not _sha256_hex(head.authority_policy_digest):
        p.append("REGISTRY_HEAD_AUTHORITY_POLICY_DIGEST_INVALID")
    if head.candidate_id != expected_candidate_id:
        p.append("REGISTRY_HEAD_CANDIDATE_MISMATCH")
    if not _exact_int(head.sequence, minimum=1):
        p.append("REGISTRY_HEAD_SEQUENCE_INVALID")
    if not _sha256_hex(head.registry_digest):
        p.append("REGISTRY_HEAD_DIGEST_INVALID")
    trust_result = validate_bootstrap_trust_set(trust)
    if not trust_result["valid"]:
        p.extend(f"REGISTRY_HEAD_TRUST:{x}" for x in trust_result["problems"])
    out = _result(not p, p, "PINNED_REGISTRY_HEAD_STRUCTURALLY_VALID", "PINNED_REGISTRY_HEAD_INVALID")
    out.update({
        "validation_profile_digest": profile_digest,
        "currentness_anchor_origin": "OUT_OF_BAND_PINNED_CURRENTNESS_REQUIRED",
        "currentness_anchor_provisioning_proven": False,
    })
    return out


def validate_pinned_registry_head(
    head: PinnedRegistryHead, trust: PinnedBootstrapTrustSet, *, expected_candidate_id: str
) -> dict[str, Any]:
    try:
        policy = _policy_snapshot()
        profile = validation_profile_digest(policy)
    except CanonicalizationError as exc:
        return _result(False, [f"VALIDATION_PROFILE_INVALID:{exc}"], "UNREACHABLE", "PINNED_REGISTRY_HEAD_INVALID")
    return _validate_pinned_registry_head_with_profile(
        head, trust, expected_candidate_id=expected_candidate_id, profile_digest=profile,
    )


def _snapshot_key_index(snapshot: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    keys = snapshot.get("keys")
    if type(keys) is not list:
        return {}
    return {
        str(k.get("key_id")): k for k in keys
        if type(k) is dict and _canonical_identifier(k.get("key_id"))
    }


def _validate_snapshot(
    record: dict[str, Any], expected_candidate_id: str,
    trust: PinnedBootstrapTrustSet,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    p: list[str] = []
    if set(record.keys()) != REGISTRY_TOP_LEVEL_FIELDS:
        p.append("KEY_REGISTRY_TOP_LEVEL_FIELDS_NOT_EXACT")
    if not _schema_one(record.get("schema_version")):
        p.append("KEY_REGISTRY_SCHEMA_INVALID")
    if record.get("object_type") != "GOVERNANCE_KEY_REGISTRY":
        p.append("KEY_REGISTRY_OBJECT_TYPE_INVALID")
    _require_identifier(p, record.get("registry_id"), "KEY_REGISTRY_ID")
    _require_identifier(p, record.get("candidate_id"), "KEY_REGISTRY_CANDIDATE_ID")
    _require_identifier(p, record.get("generation_id"), "KEY_REGISTRY_GENERATION_ID")
    _require_identifier(p, record.get("trust_set_id"), "KEY_REGISTRY_TRUST_SET_ID")
    if record.get("candidate_id") != expected_candidate_id:
        p.append("KEY_REGISTRY_CANDIDATE_MISMATCH")
    if record.get("trust_set_id") != trust.trust_set_id:
        p.append("KEY_REGISTRY_TRUST_SET_MISMATCH")
    if record.get("trust_set_digest") != trust.trust_set_digest:
        p.append("KEY_REGISTRY_TRUST_SET_DIGEST_MISMATCH")
    if not _sha256_hex(record.get("trust_set_digest")):
        p.append("KEY_REGISTRY_TRUST_SET_DIGEST_INVALID")
    if not _sha256_hex(record.get("authority_policy_digest")):
        p.append("KEY_REGISTRY_AUTHORITY_POLICY_DIGEST_INVALID")

    sequence = record.get("sequence")
    if not _exact_int(sequence, minimum=1):
        p.append("KEY_REGISTRY_SEQUENCE_INVALID")
    predecessor = record.get("predecessor_registry_digest")
    if predecessor != "GENESIS" and not _sha256_hex(predecessor):
        p.append("KEY_REGISTRY_PREDECESSOR_INVALID")

    bootstrap_public_keys = {
        pub for root in trust.roots
        if (pub := _b64(root.public_key_b64, ED25519_PUBLIC_KEY_BYTES)) is not None
    }
    key_index: dict[str, dict[str, Any]] = {}
    keys = record.get("keys")
    public_keys: set[bytes] = set()
    issuer_domains: dict[str, str] = {}
    if type(keys) is not list or not keys:
        p.append("KEY_REGISTRY_KEYS_REQUIRED")
        keys = []
    for i, key in enumerate(keys):
        if type(key) is not dict:
            p.append(f"KEY_REGISTRY_KEY_MALFORMED:{i}")
            continue
        if set(key.keys()) != REGISTRY_KEY_FIELDS:
            p.append(f"KEY_REGISTRY_KEY_FIELDS_NOT_EXACT:{i}")
        for field in ("issuer_id", "key_id", "control_domain_id"):
            _require_identifier(p, key.get(field), f"KEY_REGISTRY_KEY:{i}:{field}")
        if key.get("algorithm") != "ED25519":
            p.append(f"KEY_REGISTRY_KEY_ALGORITHM_UNSUPPORTED:{i}")
        pub = _b64(key.get("public_key_b64"), ED25519_PUBLIC_KEY_BYTES)
        if pub is None:
            p.append(f"KEY_REGISTRY_PUBLIC_KEY_INVALID:{i}")
        else:
            if pub in bootstrap_public_keys:
                p.append(f"KEY_REGISTRY_BOOTSTRAP_PUBLIC_KEY_REUSE_FORBIDDEN:{i}")
            if pub in public_keys:
                p.append(f"KEY_REGISTRY_PUBLIC_KEY_REUSE_FORBIDDEN:{i}")
            else:
                public_keys.add(pub)
        roles = key.get("roles")
        if type(roles) is not list or not roles or not all(type(r) is str and r in ROLE_VOCABULARY for r in roles):
            p.append(f"KEY_REGISTRY_ROLES_INVALID:{i}")
        elif len(roles) != len(set(roles)):
            p.append(f"KEY_REGISTRY_ROLE_DUPLICATE:{i}")
        state = key.get("state")
        if state not in {"ACTIVE", "REVOKED"}:
            p.append(f"KEY_REGISTRY_KEY_STATE_INVALID:{i}")
        valid_from = key.get("valid_from_registry_sequence")
        revoked_at = key.get("revoked_at_registry_sequence")
        if not _exact_int(valid_from, minimum=1):
            p.append(f"KEY_REGISTRY_VALID_FROM_INVALID:{i}")
        elif _exact_int(sequence, minimum=1) and valid_from > sequence:
            p.append(f"KEY_REGISTRY_VALID_FROM_FUTURE:{i}")
        if state == "ACTIVE" and revoked_at is not None:
            p.append(f"KEY_REGISTRY_ACTIVE_WITH_REVOCATION:{i}")
        if state == "REVOKED":
            if not _exact_int(revoked_at, minimum=1):
                p.append(f"KEY_REGISTRY_REVOCATION_SEQUENCE_REQUIRED:{i}")
            elif _exact_int(sequence, minimum=1) and revoked_at > sequence:
                p.append(f"KEY_REGISTRY_REVOCATION_IN_FUTURE:{i}")
            elif _exact_int(valid_from, minimum=1) and revoked_at < valid_from:
                p.append(f"KEY_REGISTRY_REVOCATION_BEFORE_VALIDITY:{i}")
        key_id = key.get("key_id")
        if _canonical_identifier(key_id):
            if key_id in key_index:
                p.append(f"KEY_REGISTRY_KEY_ID_DUPLICATE:{key_id}")
            else:
                key_index[key_id] = key
        issuer, domain = key.get("issuer_id"), key.get("control_domain_id")
        if _canonical_identifier(issuer) and _canonical_identifier(domain):
            prior = issuer_domains.get(issuer)
            if prior is not None and prior != domain:
                p.append(f"KEY_REGISTRY_ISSUER_MULTI_DOMAIN_FORBIDDEN:{issuer}")
            issuer_domains[issuer] = domain

    supplied = record.get("registry_digest")
    if not _sha256_hex(supplied):
        p.append("KEY_REGISTRY_DIGEST_INVALID")
    else:
        try:
            if supplied != registry_digest(record):
                p.append("KEY_REGISTRY_DIGEST_MISMATCH")
        except CanonicalizationError:
            p.append("KEY_REGISTRY_CANONICALIZATION_FAILED")

    signatures = record.get("bootstrap_signatures")
    if type(signatures) is not list or not signatures:
        p.append("KEY_REGISTRY_BOOTSTRAP_SIGNATURES_REQUIRED")
    else:
        for i, sig in enumerate(signatures):
            if type(sig) is not dict:
                p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_MALFORMED:{i}")
                continue
            if set(sig.keys()) != REGISTRY_SIGNATURE_FIELDS:
                p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_FIELDS_NOT_EXACT:{i}")
            _require_identifier(p, sig.get("root_id"), f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_ROOT_ID:{i}")
            _require_identifier(p, sig.get("key_id"), f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_KEY_ID:{i}")
            if sig.get("algorithm") != "ED25519":
                p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_ALGORITHM_UNSUPPORTED:{i}")
            if _b64(sig.get("signature_b64"), ED25519_SIGNATURE_BYTES) is None:
                p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_ENCODING_INVALID:{i}")
    return p, key_index


def _verify_bootstrap_signatures(
    record: dict[str, Any], trust: PinnedBootstrapTrustSet
) -> tuple[list[str], tuple[str, ...]]:
    p: list[str] = []
    digest = record.get("registry_digest")
    if not _sha256_hex(digest):
        return ["KEY_REGISTRY_BOOTSTRAP_CANNOT_VERIFY_WITHOUT_DIGEST"], ()
    roots = {(r.root_id, r.key_id): r for r in trust.roots}
    seen: set[tuple[str, str]] = set()
    domains: set[str] = set()
    signatures = record.get("bootstrap_signatures")
    if type(signatures) is not list:
        return ["KEY_REGISTRY_BOOTSTRAP_SIGNATURES_REQUIRED"], ()
    for i, sig in enumerate(signatures):
        if type(sig) is not dict:
            continue
        pair = (sig.get("root_id"), sig.get("key_id"))
        if pair in seen:
            p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNER_DUPLICATE:{i}")
            continue
        seen.add(pair)  # type: ignore[arg-type]
        root = roots.get(pair)  # type: ignore[arg-type]
        if root is None:
            p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNER_UNKNOWN:{i}")
            continue
        if root.control_domain_id in trust.candidate_control_domain_ids:
            p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNER_CANDIDATE_CONTROLLED:{root.root_id}")
            continue
        try:
            msg = registry_signature_message(
                str(digest), trust_set_id=trust.trust_set_id,
                trust_set_digest=trust.trust_set_digest,
                root_id=root.root_id, key_id=root.key_id,
                control_domain_id=root.control_domain_id,
            )
        except (ValueError, CanonicalizationError):
            p.append(f"KEY_REGISTRY_BOOTSTRAP_MESSAGE_INVALID:{i}")
            continue
        if sig.get("algorithm") != "ED25519" or not _verify_ed25519(
            root.public_key_b64, str(sig.get("signature_b64", "")), msg
        ):
            p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_INVALID:{i}")
            continue
        domains.add(root.control_domain_id)
    if _exact_int(trust.threshold_control_domains, minimum=2) and len(domains) < trust.threshold_control_domains:
        p.append("KEY_REGISTRY_BOOTSTRAP_THRESHOLD_NOT_MET")
    return p, tuple(sorted(domains))


def _validate_chain_owned(
    registry_chain: list[dict[str, Any]], trust: PinnedBootstrapTrustSet,
    expected_candidate_id: str, *, profile_digest: str,
) -> _RegistryValidation:
    p: list[str] = []
    _require_identifier(p, expected_candidate_id, "EXPECTED_CANDIDATE_ID")
    trust_result = validate_bootstrap_trust_set(trust)
    if not trust_result["valid"]:
        p.extend(f"CHAIN:{x}" for x in trust_result["problems"])
        return _RegistryValidation(False, tuple(sorted(set(p))), None, {}, ())
    if not registry_chain:
        return _RegistryValidation(False, ("KEY_REGISTRY_CHAIN_REQUIRED",), None, {}, ())

    previous: dict[str, Any] | None = None
    snapshots: dict[int, dict[str, Any]] = {}
    generations: set[str] = set()
    last_domains: tuple[str, ...] = ()
    for idx, record in enumerate(registry_chain):
        structural, current_keys = _validate_snapshot(record, expected_candidate_id, trust)
        p.extend(f"CHAIN[{idx}]:{x}" for x in structural)
        sig_p, last_domains = _verify_bootstrap_signatures(record, trust)
        p.extend(f"CHAIN[{idx}]:{x}" for x in sig_p)
        seq = record.get("sequence")
        generation = record.get("generation_id")
        if _canonical_identifier(generation):
            if generation in generations:
                p.append(f"KEY_REGISTRY_CHAIN_GENERATION_REUSE_FORBIDDEN:{idx}")
            generations.add(generation)
        if _exact_int(seq, minimum=1):
            if seq in snapshots:
                p.append(f"KEY_REGISTRY_CHAIN_SEQUENCE_DUPLICATE:{seq}")
            snapshots[int(seq)] = record

        if idx == 0:
            if not (type(seq) is int and seq == 1):
                p.append("KEY_REGISTRY_CHAIN_GENESIS_SEQUENCE_MUST_BE_ONE")
            if record.get("predecessor_registry_digest") != "GENESIS":
                p.append("KEY_REGISTRY_CHAIN_GENESIS_PREDECESSOR_REQUIRED")
            for key_id, key in current_keys.items():
                if not (type(key.get("valid_from_registry_sequence")) is int and key.get("valid_from_registry_sequence") == 1):
                    p.append(f"KEY_REGISTRY_CHAIN_GENESIS_KEY_VALID_FROM_MUST_BE_ONE:{key_id}")
        else:
            assert previous is not None
            previous_seq = previous.get("sequence")
            if not (
                _exact_int(previous_seq, minimum=1) and _exact_int(seq, minimum=1)
                and seq == previous_seq + 1
            ):
                p.append(f"KEY_REGISTRY_CHAIN_SEQUENCE_GAP:{idx}")
            if record.get("predecessor_registry_digest") != previous.get("registry_digest"):
                p.append(f"KEY_REGISTRY_CHAIN_PREDECESSOR_MISMATCH:{idx}")
            if record.get("registry_id") != previous.get("registry_id"):
                p.append(f"KEY_REGISTRY_CHAIN_REGISTRY_ID_CHANGED:{idx}")
            if record.get("trust_set_id") != previous.get("trust_set_id") or record.get("trust_set_digest") != previous.get("trust_set_digest"):
                p.append(f"KEY_REGISTRY_CHAIN_TRUST_SET_CHANGED:{idx}")
            if record.get("generation_id") == previous.get("generation_id"):
                p.append(f"KEY_REGISTRY_CHAIN_MATERIAL_UPDATE_REQUIRES_NEW_GENERATION:{idx}")
            previous_keys = _snapshot_key_index(previous)
            for key_id, prior in previous_keys.items():
                current = current_keys.get(key_id)
                if current is None:
                    p.append(f"KEY_REGISTRY_CHAIN_KEY_REMOVAL_FORBIDDEN:{key_id}")
                    continue
                for field in (
                    "issuer_id", "control_domain_id", "algorithm", "public_key_b64",
                    "roles", "valid_from_registry_sequence",
                ):
                    if current.get(field) != prior.get(field):
                        p.append(f"KEY_REGISTRY_CHAIN_KEY_IDENTITY_MUTATION_FORBIDDEN:{key_id}:{field}")
                if prior.get("state") == "REVOKED":
                    if current.get("state") != "REVOKED":
                        p.append(f"KEY_REGISTRY_CHAIN_REVOKED_KEY_REACTIVATION_FORBIDDEN:{key_id}")
                    if current.get("revoked_at_registry_sequence") != prior.get("revoked_at_registry_sequence"):
                        p.append(f"KEY_REGISTRY_CHAIN_REVOCATION_SEQUENCE_MUTATION_FORBIDDEN:{key_id}")
                elif current.get("state") == "REVOKED" and current.get("revoked_at_registry_sequence") != seq:
                    p.append(f"KEY_REGISTRY_CHAIN_REVOCATION_MUST_BIND_CURRENT_SEQUENCE:{key_id}")
            for key_id in set(current_keys) - set(previous_keys):
                key = current_keys[key_id]
                if not (type(key.get("valid_from_registry_sequence")) is int and key.get("valid_from_registry_sequence") == seq):
                    p.append(f"KEY_REGISTRY_CHAIN_NEW_KEY_VALID_FROM_MUST_EQUAL_FIRST_APPEARANCE:{key_id}")
                if key.get("state") != "ACTIVE" or key.get("revoked_at_registry_sequence") is not None:
                    p.append(f"KEY_REGISTRY_CHAIN_NEW_KEY_MUST_ENTER_ACTIVE:{key_id}")
        previous = record

    current = registry_chain[-1]
    if current.get("authority_policy_digest") != profile_digest:
        p.append("KEY_REGISTRY_CURRENT_AUTHORITY_POLICY_DIGEST_MISMATCH")
    valid = not p
    return _RegistryValidation(
        valid, tuple(sorted(set(p))), current if valid else None,
        snapshots if valid else {}, last_domains if valid else (),
    )


def validate_governance_key_registry_chain(
    registry_chain: Sequence[Mapping[str, Any]], trust: PinnedBootstrapTrustSet,
    *, expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        owned_chain = _snapshot_registry_chain(registry_chain)
        policy = _policy_snapshot()
        profile = validation_profile_digest(policy)
    except CanonicalizationError as exc:
        return _result(False, [f"OWNED_INPUT_SNAPSHOT:{exc}"], "UNREACHABLE", "GOVERNANCE_KEY_REGISTRY_CHAIN_INVALID")
    result = _validate_chain_owned(
        owned_chain, trust, expected_candidate_id, profile_digest=profile,
    )
    out = _result(
        result.valid, result.problems,
        "GOVERNANCE_KEY_REGISTRY_CHAIN_AUTHENTICATED_UNDER_PINNED_ROOTS",
        "GOVERNANCE_KEY_REGISTRY_CHAIN_INVALID",
    )
    out.update({
        "validation_profile_digest": profile,
        "trust_anchor_origin": "OUT_OF_BAND_PINNED_CONFIG_REQUIRED",
        "trust_anchor_provisioning_proven": False,
        "registry_currentness_anchored": False,
        "bootstrap_authenticated_control_domains": list(result.authenticated_bootstrap_domains),
    })
    if result.current is not None:
        out.update({
            "registry_id": result.current.get("registry_id"),
            "last_supplied_registry_digest": result.current.get("registry_digest"),
            "last_supplied_registry_sequence": result.current.get("sequence"),
            "last_supplied_generation_id": result.current.get("generation_id"),
            "trust_set_digest": result.current.get("trust_set_digest"),
            "authority_policy_digest": result.current.get("authority_policy_digest"),
        })
    return out


def validate_governance_key_registry_chain_json(
    registry_chain_json: Sequence[bytes | str], trust: PinnedBootstrapTrustSet,
    *, expected_candidate_id: str,
) -> dict[str, Any]:
    if type(registry_chain_json) not in {list, tuple}:
        return _result(False, ["STRICT_JSON_REGISTRY_CHAIN_CONTAINER_INVALID"], "UNREACHABLE", "GOVERNANCE_KEY_REGISTRY_CHAIN_INVALID")
    try:
        parsed = [load_strict_json(raw) for raw in list(registry_chain_json)]
    except (CanonicalizationError, UnicodeEncodeError) as exc:
        return _result(False, [f"STRICT_JSON_INGRESS:{exc}"], "UNREACHABLE", "GOVERNANCE_KEY_REGISTRY_CHAIN_INVALID")
    if not all(type(row) is dict for row in parsed):
        return _result(False, ["STRICT_JSON_REGISTRY_RECORD_MUST_BE_OBJECT"], "UNREACHABLE", "GOVERNANCE_KEY_REGISTRY_CHAIN_INVALID")
    return validate_governance_key_registry_chain(parsed, trust, expected_candidate_id=expected_candidate_id)


def _head_match(current: Mapping[str, Any], head: PinnedRegistryHead) -> list[str]:
    p: list[str] = []
    if current.get("registry_id") != head.registry_id:
        p.append("SIGNED_RECORD_REGISTRY_HEAD_ID_MISMATCH")
    if current.get("candidate_id") != head.candidate_id:
        p.append("SIGNED_RECORD_REGISTRY_HEAD_CANDIDATE_MISMATCH")
    if current.get("sequence") != head.sequence or type(current.get("sequence")) is not type(head.sequence):
        p.append("SIGNED_RECORD_REGISTRY_HEAD_SEQUENCE_MISMATCH")
    if current.get("generation_id") != head.generation_id:
        p.append("SIGNED_RECORD_REGISTRY_HEAD_GENERATION_MISMATCH")
    if current.get("registry_digest") != head.registry_digest:
        p.append("SIGNED_RECORD_REGISTRY_HEAD_DIGEST_MISMATCH")
    if current.get("trust_set_id") != head.trust_set_id:
        p.append("SIGNED_RECORD_REGISTRY_HEAD_TRUST_SET_ID_MISMATCH")
    if current.get("trust_set_digest") != head.trust_set_digest:
        p.append("SIGNED_RECORD_REGISTRY_HEAD_TRUST_SET_DIGEST_MISMATCH")
    if current.get("authority_policy_digest") != head.authority_policy_digest:
        p.append("SIGNED_RECORD_REGISTRY_HEAD_AUTHORITY_POLICY_DIGEST_MISMATCH")
    return p


def verify_signed_governance_record(
    record: Mapping[str, Any], *, registry_chain: Sequence[Mapping[str, Any]],
    bootstrap_trust: PinnedBootstrapTrustSet,
    expected_current_registry_head: PinnedRegistryHead,
    expected_candidate_id: str, expected_generation_id: str,
    expected_record_type: str, expected_snapshot_id: str | None = None,
    forbidden_control_domain_ids: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    try:
        owned_record = _owned_json_snapshot(record, "$record")
        if type(owned_record) is not dict:
            raise CanonicalizationError("SIGNED_RECORD_MUST_BE_OBJECT")
        owned_chain = _snapshot_registry_chain(registry_chain)
        policy = _policy_snapshot()
        profile = validation_profile_digest(policy)
    except CanonicalizationError as exc:
        return _result(False, [f"OWNED_INPUT_SNAPSHOT:{exc}"], "UNREACHABLE", "SIGNED_GOVERNANCE_RECORD_INVALID")

    p: list[str] = []
    _require_identifier(p, expected_candidate_id, "EXPECTED_CANDIDATE_ID")
    _require_identifier(p, expected_generation_id, "EXPECTED_GENERATION_ID")
    _require_identifier(p, expected_record_type, "EXPECTED_RECORD_TYPE")
    if expected_snapshot_id is not None:
        _require_identifier(p, expected_snapshot_id, "EXPECTED_SNAPSHOT_ID")
    if type(forbidden_control_domain_ids) is not frozenset:
        p.append("FORBIDDEN_CONTROL_DOMAIN_CONTAINER_MUST_BE_FROZENSET")
    else:
        for domain in forbidden_control_domain_ids:
            _require_identifier(p, domain, "FORBIDDEN_CONTROL_DOMAIN_ID")

    head_result = _validate_pinned_registry_head_with_profile(
        expected_current_registry_head, bootstrap_trust,
        expected_candidate_id=expected_candidate_id, profile_digest=profile,
    )
    if not head_result["valid"]:
        p.extend(f"SIGNED_RECORD_CURRENTNESS_ANCHOR:{x}" for x in head_result["problems"])
    chain = _validate_chain_owned(
        owned_chain, bootstrap_trust, expected_candidate_id, profile_digest=profile,
    )
    if not chain.valid:
        p.extend(f"SIGNED_RECORD_REGISTRY:{x}" for x in chain.problems)

    record = owned_record
    if set(record.keys()) != SIGNED_RECORD_FIELDS:
        p.append("SIGNED_RECORD_FIELDS_NOT_EXACT")
    if not _schema_one(record.get("schema_version")):
        p.append("SIGNED_RECORD_SCHEMA_INVALID")
    if record.get("object_type") != "SIGNED_GOVERNANCE_RECORD":
        p.append("SIGNED_RECORD_OBJECT_TYPE_INVALID")
    for field, code in (
        ("record_type", "SIGNED_RECORD_TYPE"), ("record_id", "SIGNED_RECORD_ID"),
        ("candidate_id", "SIGNED_RECORD_CANDIDATE_ID"), ("generation_id", "SIGNED_RECORD_GENERATION_ID"),
        ("trust_set_id", "SIGNED_RECORD_TRUST_SET_ID"), ("issuer_id", "SIGNED_RECORD_ISSUER_ID"),
        ("key_id", "SIGNED_RECORD_KEY_ID"), ("required_role", "SIGNED_RECORD_REQUIRED_ROLE"),
    ):
        _require_identifier(p, record.get(field), code)
    _require_identifier(p, record.get("snapshot_id"), "SIGNED_RECORD_SNAPSHOT_ID", allow_none=True)

    if record.get("record_type") != expected_record_type:
        p.append("SIGNED_RECORD_TYPE_MISMATCH")
    canonical_role = policy.get(expected_record_type)
    if canonical_role is None:
        p.append("SIGNED_RECORD_TYPE_POLICY_UNKNOWN")
    if canonical_role is not None and record.get("required_role") != canonical_role:
        p.append("SIGNED_RECORD_REQUIRED_ROLE_MISMATCH")
    if record.get("candidate_id") != expected_candidate_id:
        p.append("SIGNED_RECORD_CANDIDATE_MISMATCH")
    if record.get("generation_id") != expected_generation_id:
        p.append("SIGNED_RECORD_GENERATION_MISMATCH")
    if expected_snapshot_id is None:
        if record.get("snapshot_id") is not None:
            p.append("SIGNED_RECORD_UNEXPECTED_SNAPSHOT_BINDING")
    elif record.get("snapshot_id") != expected_snapshot_id:
        p.append("SIGNED_RECORD_SNAPSHOT_MISMATCH")
    if record.get("trust_set_id") != bootstrap_trust.trust_set_id:
        p.append("SIGNED_RECORD_TRUST_SET_MISMATCH")
    if record.get("trust_set_digest") != bootstrap_trust.trust_set_digest:
        p.append("SIGNED_RECORD_TRUST_SET_DIGEST_MISMATCH")
    if not _sha256_hex(record.get("trust_set_digest")):
        p.append("SIGNED_RECORD_TRUST_SET_DIGEST_INVALID")
    if record.get("authority_policy_digest") != profile:
        p.append("SIGNED_RECORD_AUTHORITY_POLICY_DIGEST_MISMATCH")
    if not _sha256_hex(record.get("authority_policy_digest")):
        p.append("SIGNED_RECORD_AUTHORITY_POLICY_DIGEST_INVALID")
    if record.get("signature_algorithm") != "ED25519":
        p.append("SIGNED_RECORD_SIGNATURE_ALGORITHM_UNSUPPORTED")

    issued_sequence = record.get("issued_registry_sequence")
    if not _exact_int(issued_sequence, minimum=1):
        p.append("SIGNED_RECORD_ISSUED_REGISTRY_SEQUENCE_INVALID")
    if not _sha256_hex(record.get("issued_registry_digest")):
        p.append("SIGNED_RECORD_ISSUED_REGISTRY_DIGEST_INVALID")

    payload_ok = False
    supplied_payload_digest = record.get("payload_digest")
    if not _sha256_hex(supplied_payload_digest):
        p.append("SIGNED_RECORD_PAYLOAD_DIGEST_INVALID")
    else:
        try:
            payload_ok = canonical_sha256(record.get("payload")) == supplied_payload_digest
        except CanonicalizationError:
            p.append("SIGNED_RECORD_PAYLOAD_CANONICALIZATION_FAILED")
        else:
            if not payload_ok:
                p.append("SIGNED_RECORD_PAYLOAD_DIGEST_MISMATCH")

    key: dict[str, Any] | None = None
    currentness_matched = False
    registry_authority_ok = False
    current = chain.current if chain.valid else None
    if current is not None:
        head_p = _head_match(current, expected_current_registry_head) if head_result["valid"] else []
        p.extend(head_p)
        currentness_matched = head_result["valid"] and not head_p
        if current.get("authority_policy_digest") != profile:
            p.append("SIGNED_RECORD_CURRENT_REGISTRY_AUTHORITY_POLICY_DIGEST_MISMATCH")
        if expected_current_registry_head.authority_policy_digest != profile:
            p.append("SIGNED_RECORD_PINNED_HEAD_AUTHORITY_POLICY_DIGEST_MISMATCH")
        if current.get("trust_set_digest") != bootstrap_trust.trust_set_digest:
            p.append("SIGNED_RECORD_CURRENT_REGISTRY_TRUST_SET_DIGEST_MISMATCH")
        if expected_current_registry_head.trust_set_digest != bootstrap_trust.trust_set_digest:
            p.append("SIGNED_RECORD_PINNED_HEAD_TRUST_SET_DIGEST_MISMATCH")
        if record.get("generation_id") != current.get("generation_id"):
            p.append("SIGNED_RECORD_GENERATION_NOT_CURRENT")
        if expected_generation_id != current.get("generation_id"):
            p.append("SIGNED_RECORD_EXPECTED_GENERATION_NOT_CURRENT")
        if not (
            _exact_int(current.get("sequence"), minimum=1)
            and _exact_int(issued_sequence, minimum=1)
            and issued_sequence == current.get("sequence")
        ):
            p.append("SIGNED_RECORD_NOT_ISSUED_UNDER_CURRENT_REGISTRY")
        if record.get("issued_registry_digest") != current.get("registry_digest"):
            p.append("SIGNED_RECORD_ISSUED_REGISTRY_DIGEST_MISMATCH")
        if record.get("issued_registry_digest") != expected_current_registry_head.registry_digest:
            p.append("SIGNED_RECORD_ISSUED_REGISTRY_DIGEST_NOT_PINNED_HEAD")

        snapshot = chain.snapshots_by_sequence.get(int(issued_sequence)) if _exact_int(issued_sequence, minimum=1) else None
        if snapshot is None:
            p.append("SIGNED_RECORD_ISSUANCE_REGISTRY_SNAPSHOT_NOT_FOUND")
        else:
            if snapshot.get("generation_id") != record.get("generation_id"):
                p.append("SIGNED_RECORD_ISSUANCE_GENERATION_MISMATCH")
            if snapshot.get("registry_digest") != record.get("issued_registry_digest"):
                p.append("SIGNED_RECORD_ISSUANCE_DIGEST_MISMATCH")
            if snapshot.get("trust_set_digest") != record.get("trust_set_digest"):
                p.append("SIGNED_RECORD_ISSUANCE_TRUST_SET_DIGEST_MISMATCH")
            if snapshot.get("authority_policy_digest") != record.get("authority_policy_digest"):
                p.append("SIGNED_RECORD_ISSUANCE_AUTHORITY_POLICY_DIGEST_MISMATCH")
            key = _snapshot_key_index(snapshot).get(record.get("key_id")) if _canonical_identifier(record.get("key_id")) else None
            if key is None:
                p.append("SIGNED_RECORD_KEY_NOT_IN_ISSUANCE_REGISTRY")

        before = len(p)
        if key is not None:
            if key.get("issuer_id") != record.get("issuer_id"):
                p.append("SIGNED_RECORD_ISSUER_KEY_BINDING_MISMATCH")
            if key.get("algorithm") != "ED25519":
                p.append("SIGNED_RECORD_KEY_ALGORITHM_UNSUPPORTED")
            roles = key.get("roles")
            if canonical_role is None or type(roles) is not list or canonical_role not in roles:
                p.append("SIGNED_RECORD_ISSUER_ROLE_NOT_AUTHORIZED")
            domain = key.get("control_domain_id")
            if domain in forbidden_control_domain_ids:
                p.append("SIGNED_RECORD_ISSUER_FORBIDDEN_CONTROL_DOMAIN")
            if domain in bootstrap_trust.candidate_control_domain_ids:
                p.append("SIGNED_RECORD_ISSUER_CANDIDATE_CONTROLLED_DOMAIN")
            if key.get("state") != "ACTIVE":
                p.append("SIGNED_RECORD_KEY_NOT_CURRENTLY_ACTIVE")
            if not _exact_int(key.get("valid_from_registry_sequence"), minimum=1) or key.get("valid_from_registry_sequence") > issued_sequence:
                p.append("SIGNED_RECORD_KEY_NOT_YET_VALID")
        registry_authority_ok = key is not None and len(p) == before and currentness_matched and chain.valid

    signature_ok = False
    if _b64(record.get("signature_b64"), ED25519_SIGNATURE_BYTES) is None:
        p.append("SIGNED_RECORD_SIGNATURE_ENCODING_INVALID")
    elif key is not None:
        try:
            message = signed_record_signature_message(record)
        except CanonicalizationError:
            p.append("SIGNED_RECORD_CANONICALIZATION_FAILED")
        else:
            signature_ok = _verify_ed25519(
                str(key.get("public_key_b64", "")),
                str(record.get("signature_b64", "")), message,
            )
            if not signature_ok:
                p.append("SIGNED_RECORD_SIGNATURE_INVALID")

    valid = not p
    out = _result(
        valid, p,
        "SIGNED_GOVERNANCE_RECORD_AUTHENTICATED_UNDER_CURRENT_PINNED_REGISTRY_HEAD",
        "SIGNED_GOVERNANCE_RECORD_INVALID",
    )
    out.update({
        "validation_profile_digest": profile,
        "content_integrity_verified": payload_ok,
        "issuer_signature_verified": signature_ok,
        "authority_registry_verified": registry_authority_ok,
        "registry_currentness_anchor_matched": currentness_matched,
        "trust_anchor_origin": "OUT_OF_BAND_PINNED_CONFIG_REQUIRED",
        "trust_anchor_provisioning_proven": False,
        "currentness_anchor_origin": "OUT_OF_BAND_PINNED_CURRENTNESS_REQUIRED",
        "currentness_anchor_provisioning_proven": False,
    })
    if key is not None:
        out["issuer_control_domain_id"] = key.get("control_domain_id")
    return out


def verify_signed_governance_record_json(
    raw_record: bytes | str, *, registry_chain_json: Sequence[bytes | str],
    bootstrap_trust: PinnedBootstrapTrustSet,
    expected_current_registry_head: PinnedRegistryHead,
    expected_candidate_id: str, expected_generation_id: str,
    expected_record_type: str, expected_snapshot_id: str | None = None,
    forbidden_control_domain_ids: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    if type(registry_chain_json) not in {list, tuple}:
        return _result(False, ["STRICT_JSON_REGISTRY_CHAIN_CONTAINER_INVALID"], "UNREACHABLE", "SIGNED_GOVERNANCE_RECORD_INVALID")
    try:
        record = load_strict_json(raw_record)
        chain = [load_strict_json(raw) for raw in list(registry_chain_json)]
    except (CanonicalizationError, UnicodeEncodeError) as exc:
        return _result(False, [f"STRICT_JSON_INGRESS:{exc}"], "UNREACHABLE", "SIGNED_GOVERNANCE_RECORD_INVALID")
    if type(record) is not dict or not all(type(row) is dict for row in chain):
        return _result(False, ["STRICT_JSON_SIGNED_RECORD_OR_REGISTRY_MUST_BE_OBJECT"], "UNREACHABLE", "SIGNED_GOVERNANCE_RECORD_INVALID")
    return verify_signed_governance_record(
        record, registry_chain=chain, bootstrap_trust=bootstrap_trust,
        expected_current_registry_head=expected_current_registry_head,
        expected_candidate_id=expected_candidate_id,
        expected_generation_id=expected_generation_id,
        expected_record_type=expected_record_type,
        expected_snapshot_id=expected_snapshot_id,
        forbidden_control_domain_ids=forbidden_control_domain_ids,
    )
