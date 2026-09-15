"""V16 Slice 1 authenticated trust foundation.

Construction-stage only. Content integrity, issuer authenticity, authority policy,
registry currentness, and out-of-band trust provisioning are deliberately separate.
All validation results remain non-authoritative construction evidence.
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
except Exception:  # pragma: no cover
    InvalidSignature = Exception  # type: ignore[assignment]
    Ed25519PublicKey = None  # type: ignore[assignment]

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
IMPLEMENTATION_QUALIFICATION = "NOT_CLAIMED"
RUNTIME_QUALIFICATION = "NOT_CLAIMED"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ED25519_PUBLIC_KEY_BYTES = 32
ED25519_SIGNATURE_BYTES = 64
MAX_CANONICAL_INTEGER = (2**53) - 1

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
    "sequence", "predecessor_registry_digest", "keys", "registry_digest", "bootstrap_signatures",
})
REGISTRY_KEY_FIELDS = frozenset({
    "issuer_id", "key_id", "control_domain_id", "algorithm", "public_key_b64",
    "roles", "state", "valid_from_registry_sequence", "revoked_at_registry_sequence",
})
REGISTRY_SIGNATURE_FIELDS = frozenset({"root_id", "key_id", "algorithm", "signature_b64"})
SIGNED_RECORD_FIELDS = frozenset({
    "schema_version", "object_type", "record_type", "record_id", "candidate_id",
    "generation_id", "snapshot_id", "trust_set_id", "issued_registry_sequence",
    "issued_registry_digest", "issuer_id", "key_id", "required_role", "payload_digest",
    "payload", "signature_algorithm", "signature_b64",
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


@dataclass(frozen=True)
class PinnedRegistryHead:
    anchor_id: str
    trust_set_id: str
    registry_id: str
    candidate_id: str
    sequence: int
    generation_id: str
    registry_digest: str


@dataclass(frozen=True)
class _RegistryValidation:
    valid: bool
    problems: tuple[str, ...]
    current: Mapping[str, Any] | None
    snapshots_by_sequence: Mapping[int, Mapping[str, Any]]
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
    value = unicodedata.normalize("NFC", value)
    if any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
        raise CanonicalizationError(f"LONE_SURROGATE_FORBIDDEN:{path}")
    return value


def _normalize(value: Any, path: str = "$") -> Any:
    if value is None or isinstance(value, bool):
        return value
    if type(value) is int:
        if abs(value) > MAX_CANONICAL_INTEGER:
            raise CanonicalizationError(f"INTEGER_OUT_OF_CANONICAL_RANGE:{path}")
        return value
    if isinstance(value, float):
        raise CanonicalizationError(f"FLOAT_FORBIDDEN:{path}")
    if isinstance(value, str):
        return _norm_string(value, path)
    if isinstance(value, (list, tuple)):
        return [_normalize(item, f"{path}[{i}]") for i, item in enumerate(value)]
    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            if not isinstance(raw_key, str):
                raise CanonicalizationError(f"NON_STRING_KEY:{path}")
            key = _norm_string(raw_key, f"{path}.<key>")
            if key in out:
                raise CanonicalizationError(f"NORMALIZED_KEY_COLLISION:{path}.{key}")
            out[key] = _normalize(raw_value, f"{path}.{key}")
        return out
    raise CanonicalizationError(f"UNSUPPORTED_TYPE:{path}:{type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        _normalize(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_strict_json(raw: bytes | str) -> Any:
    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="strict")
    elif isinstance(raw, str):
        text = raw
    else:
        raise CanonicalizationError("STRICT_JSON_INPUT_MUST_BE_BYTES_OR_STRING")

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            key = _norm_string(key, "$.<key>")
            if key in out:
                raise CanonicalizationError(f"DUPLICATE_OR_NORMALIZED_KEY:{key}")
            out[key] = value
        return out

    def reject_float(token: str) -> Any:
        raise CanonicalizationError(f"FLOAT_FORBIDDEN:{token}")

    try:
        parsed = json.loads(text, object_pairs_hook=pairs_hook, parse_float=reject_float)
    except CanonicalizationError:
        raise
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise CanonicalizationError("STRICT_JSON_PARSE_FAILED") from exc
    return _normalize(parsed)


def _registry_material(record: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in {"registry_digest", "bootstrap_signatures"}}


def registry_digest(record: Mapping[str, Any]) -> str:
    return canonical_sha256(_registry_material(record))


def registry_signature_message(
    digest_hex: str, *, trust_set_id: str, root_id: str, key_id: str, control_domain_id: str
) -> bytes:
    if not _sha256_hex(digest_hex):
        raise ValueError("REGISTRY_DIGEST_INVALID")
    return b"RSE-V16:KEY-REGISTRY-ROOT:" + canonical_bytes({
        "trust_set_id": trust_set_id,
        "root_id": root_id,
        "key_id": key_id,
        "control_domain_id": control_domain_id,
        "registry_digest": digest_hex,
    })


def signed_record_signature_message(record: Mapping[str, Any]) -> bytes:
    return b"RSE-V16:SIGNED-RECORD:" + canonical_bytes(
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
    if not _nonempty(trust.trust_set_id):
        p.append("BOOTSTRAP_TRUST_SET_ID_REQUIRED")
    if not _exact_int(trust.threshold_control_domains, minimum=2):
        p.append("BOOTSTRAP_THRESHOLD_MIN_TWO_DOMAINS")
    if not trust.roots:
        p.append("BOOTSTRAP_ROOTS_REQUIRED")
    root_ids: set[str] = set()
    key_ids: set[str] = set()
    public_keys: set[bytes] = set()
    domains: set[str] = set()
    for i, root in enumerate(trust.roots):
        if not _nonempty(root.root_id): p.append(f"BOOTSTRAP_ROOT_ID_REQUIRED:{i}")
        if not _nonempty(root.key_id): p.append(f"BOOTSTRAP_KEY_ID_REQUIRED:{i}")
        if not _nonempty(root.control_domain_id): p.append(f"BOOTSTRAP_CONTROL_DOMAIN_REQUIRED:{i}")
        if root.algorithm != "ED25519": p.append(f"BOOTSTRAP_ALGORITHM_UNSUPPORTED:{i}")
        pub = _b64(root.public_key_b64, ED25519_PUBLIC_KEY_BYTES)
        if pub is None:
            p.append(f"BOOTSTRAP_PUBLIC_KEY_INVALID:{i}")
        elif pub in public_keys:
            p.append(f"BOOTSTRAP_PUBLIC_KEY_REUSE_FORBIDDEN:{i}")
        else:
            public_keys.add(pub)
        if root.root_id in root_ids: p.append(f"BOOTSTRAP_ROOT_ID_DUPLICATE:{root.root_id}")
        if root.key_id in key_ids: p.append(f"BOOTSTRAP_KEY_ID_DUPLICATE:{root.key_id}")
        root_ids.add(root.root_id); key_ids.add(root.key_id)
        if root.control_domain_id in trust.candidate_control_domain_ids:
            p.append(f"BOOTSTRAP_ROOT_CANDIDATE_CONTROLLED:{root.root_id}")
        if _nonempty(root.control_domain_id): domains.add(root.control_domain_id)
    if _exact_int(trust.threshold_control_domains, minimum=2) and trust.threshold_control_domains > len(domains):
        p.append("BOOTSTRAP_THRESHOLD_EXCEEDS_DISTINCT_DOMAINS")
    out = _result(not p, p, "BOOTSTRAP_TRUST_SET_STRUCTURALLY_VALID", "BOOTSTRAP_TRUST_SET_INVALID")
    out.update({
        "trust_anchor_origin": "OUT_OF_BAND_PINNED_CONFIG_REQUIRED",
        "trust_anchor_provisioning_proven": False,
        "distinct_root_control_domains": sorted(domains),
    })
    return out


def validate_pinned_registry_head(
    head: PinnedRegistryHead, trust: PinnedBootstrapTrustSet, *, expected_candidate_id: str
) -> dict[str, Any]:
    p: list[str] = []
    if not _nonempty(head.anchor_id): p.append("REGISTRY_HEAD_ANCHOR_ID_REQUIRED")
    if head.trust_set_id != trust.trust_set_id: p.append("REGISTRY_HEAD_TRUST_SET_MISMATCH")
    if not _nonempty(head.registry_id): p.append("REGISTRY_HEAD_REGISTRY_ID_REQUIRED")
    if head.candidate_id != expected_candidate_id: p.append("REGISTRY_HEAD_CANDIDATE_MISMATCH")
    if not _exact_int(head.sequence, minimum=1): p.append("REGISTRY_HEAD_SEQUENCE_INVALID")
    if not _nonempty(head.generation_id): p.append("REGISTRY_HEAD_GENERATION_REQUIRED")
    if not _sha256_hex(head.registry_digest): p.append("REGISTRY_HEAD_DIGEST_INVALID")
    out = _result(not p, p, "PINNED_REGISTRY_HEAD_STRUCTURALLY_VALID", "PINNED_REGISTRY_HEAD_INVALID")
    out.update({
        "currentness_anchor_origin": "OUT_OF_BAND_PINNED_CURRENTNESS_REQUIRED",
        "currentness_anchor_provisioning_proven": False,
    })
    return out


def _snapshot_key_index(snapshot: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    keys = snapshot.get("keys")
    if not isinstance(keys, list): return {}
    return {str(k.get("key_id")): k for k in keys if isinstance(k, Mapping) and _nonempty(k.get("key_id"))}


def _validate_snapshot(record: Mapping[str, Any], expected_candidate_id: str) -> tuple[list[str], dict[str, Mapping[str, Any]]]:
    p: list[str] = []
    if set(record.keys()) != REGISTRY_TOP_LEVEL_FIELDS: p.append("KEY_REGISTRY_TOP_LEVEL_FIELDS_NOT_EXACT")
    if record.get("schema_version") != 1: p.append("KEY_REGISTRY_SCHEMA_INVALID")
    if record.get("object_type") != "GOVERNANCE_KEY_REGISTRY": p.append("KEY_REGISTRY_OBJECT_TYPE_INVALID")
    if not _nonempty(record.get("registry_id")): p.append("KEY_REGISTRY_ID_REQUIRED")
    if record.get("candidate_id") != expected_candidate_id: p.append("KEY_REGISTRY_CANDIDATE_MISMATCH")
    if not _nonempty(record.get("generation_id")): p.append("KEY_REGISTRY_GENERATION_REQUIRED")
    sequence = record.get("sequence")
    if not _exact_int(sequence, minimum=1): p.append("KEY_REGISTRY_SEQUENCE_INVALID")
    predecessor = record.get("predecessor_registry_digest")
    if predecessor != "GENESIS" and not _sha256_hex(predecessor): p.append("KEY_REGISTRY_PREDECESSOR_INVALID")

    key_index: dict[str, Mapping[str, Any]] = {}
    keys = record.get("keys")
    public_keys: set[bytes] = set()
    issuer_domains: dict[str, str] = {}
    if not isinstance(keys, list) or not keys:
        p.append("KEY_REGISTRY_KEYS_REQUIRED"); keys = []
    for i, key in enumerate(keys):
        if not isinstance(key, Mapping):
            p.append(f"KEY_REGISTRY_KEY_MALFORMED:{i}"); continue
        if set(key.keys()) != REGISTRY_KEY_FIELDS: p.append(f"KEY_REGISTRY_KEY_FIELDS_NOT_EXACT:{i}")
        for field in ("issuer_id", "key_id", "control_domain_id"):
            if not _nonempty(key.get(field)): p.append(f"KEY_REGISTRY_KEY_FIELD_REQUIRED:{i}:{field}")
        if key.get("algorithm") != "ED25519": p.append(f"KEY_REGISTRY_KEY_ALGORITHM_UNSUPPORTED:{i}")
        pub = _b64(key.get("public_key_b64"), ED25519_PUBLIC_KEY_BYTES)
        if pub is None: p.append(f"KEY_REGISTRY_PUBLIC_KEY_INVALID:{i}")
        elif pub in public_keys: p.append(f"KEY_REGISTRY_PUBLIC_KEY_REUSE_FORBIDDEN:{i}")
        else: public_keys.add(pub)
        roles = key.get("roles")
        if not isinstance(roles, list) or not roles or not all(isinstance(r, str) and r in ROLE_VOCABULARY for r in roles):
            p.append(f"KEY_REGISTRY_ROLES_INVALID:{i}")
        elif len(roles) != len(set(roles)): p.append(f"KEY_REGISTRY_ROLE_DUPLICATE:{i}")
        state = key.get("state")
        if state not in {"ACTIVE", "REVOKED"}: p.append(f"KEY_REGISTRY_KEY_STATE_INVALID:{i}")
        valid_from = key.get("valid_from_registry_sequence")
        revoked_at = key.get("revoked_at_registry_sequence")
        if not _exact_int(valid_from, minimum=1): p.append(f"KEY_REGISTRY_VALID_FROM_INVALID:{i}")
        elif _exact_int(sequence, minimum=1) and valid_from > sequence: p.append(f"KEY_REGISTRY_VALID_FROM_FUTURE:{i}")
        if state == "ACTIVE" and revoked_at is not None: p.append(f"KEY_REGISTRY_ACTIVE_WITH_REVOCATION:{i}")
        if state == "REVOKED":
            if not _exact_int(revoked_at, minimum=1): p.append(f"KEY_REGISTRY_REVOCATION_SEQUENCE_REQUIRED:{i}")
            elif _exact_int(sequence, minimum=1) and revoked_at > sequence: p.append(f"KEY_REGISTRY_REVOCATION_IN_FUTURE:{i}")
            elif _exact_int(valid_from, minimum=1) and revoked_at < valid_from: p.append(f"KEY_REGISTRY_REVOCATION_BEFORE_VALIDITY:{i}")
        key_id = key.get("key_id")
        if _nonempty(key_id):
            if str(key_id) in key_index: p.append(f"KEY_REGISTRY_KEY_ID_DUPLICATE:{key_id}")
            else: key_index[str(key_id)] = key
        issuer, domain = key.get("issuer_id"), key.get("control_domain_id")
        if _nonempty(issuer) and _nonempty(domain):
            prior = issuer_domains.get(str(issuer))
            if prior is not None and prior != domain: p.append(f"KEY_REGISTRY_ISSUER_MULTI_DOMAIN_FORBIDDEN:{issuer}")
            issuer_domains[str(issuer)] = str(domain)

    supplied = record.get("registry_digest")
    if not _sha256_hex(supplied): p.append("KEY_REGISTRY_DIGEST_INVALID")
    else:
        try:
            if supplied != registry_digest(record): p.append("KEY_REGISTRY_DIGEST_MISMATCH")
        except CanonicalizationError:
            p.append("KEY_REGISTRY_CANONICALIZATION_FAILED")
    signatures = record.get("bootstrap_signatures")
    if not isinstance(signatures, list) or not signatures:
        p.append("KEY_REGISTRY_BOOTSTRAP_SIGNATURES_REQUIRED")
    else:
        for i, sig in enumerate(signatures):
            if not isinstance(sig, Mapping): p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_MALFORMED:{i}"); continue
            if set(sig.keys()) != REGISTRY_SIGNATURE_FIELDS: p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_FIELDS_NOT_EXACT:{i}")
            if not _nonempty(sig.get("root_id")) or not _nonempty(sig.get("key_id")): p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_ID_REQUIRED:{i}")
            if sig.get("algorithm") != "ED25519": p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_ALGORITHM_UNSUPPORTED:{i}")
            if _b64(sig.get("signature_b64"), ED25519_SIGNATURE_BYTES) is None: p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_ENCODING_INVALID:{i}")
    return p, key_index


def _verify_bootstrap_signatures(record: Mapping[str, Any], trust: PinnedBootstrapTrustSet) -> tuple[list[str], tuple[str, ...]]:
    p: list[str] = []
    digest = record.get("registry_digest")
    if not _sha256_hex(digest): return ["KEY_REGISTRY_BOOTSTRAP_CANNOT_VERIFY_WITHOUT_DIGEST"], ()
    roots = {(r.root_id, r.key_id): r for r in trust.roots}
    seen: set[tuple[str, str]] = set(); domains: set[str] = set()
    signatures = record.get("bootstrap_signatures")
    if not isinstance(signatures, list): return ["KEY_REGISTRY_BOOTSTRAP_SIGNATURES_REQUIRED"], ()
    for i, sig in enumerate(signatures):
        if not isinstance(sig, Mapping): continue
        pair = (sig.get("root_id"), sig.get("key_id"))
        if pair in seen: p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNER_DUPLICATE:{i}"); continue
        seen.add(pair)
        root = roots.get(pair)  # type: ignore[arg-type]
        if root is None: p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNER_UNKNOWN:{i}"); continue
        if root.control_domain_id in trust.candidate_control_domain_ids:
            p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNER_CANDIDATE_CONTROLLED:{root.root_id}"); continue
        try:
            msg = registry_signature_message(str(digest), trust_set_id=trust.trust_set_id,
                root_id=root.root_id, key_id=root.key_id, control_domain_id=root.control_domain_id)
        except (ValueError, CanonicalizationError):
            p.append(f"KEY_REGISTRY_BOOTSTRAP_MESSAGE_INVALID:{i}"); continue
        if sig.get("algorithm") != "ED25519" or not _verify_ed25519(root.public_key_b64, str(sig.get("signature_b64", "")), msg):
            p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_INVALID:{i}"); continue
        domains.add(root.control_domain_id)
    if _exact_int(trust.threshold_control_domains, minimum=2) and len(domains) < trust.threshold_control_domains:
        p.append("KEY_REGISTRY_BOOTSTRAP_THRESHOLD_NOT_MET")
    return p, tuple(sorted(domains))


def _validate_chain(registry_chain: Sequence[Mapping[str, Any]], trust: PinnedBootstrapTrustSet, expected_candidate_id: str) -> _RegistryValidation:
    p: list[str] = []
    trust_result = validate_bootstrap_trust_set(trust)
    if not trust_result["valid"]:
        return _RegistryValidation(False, tuple(f"CHAIN:{x}" for x in trust_result["problems"]), None, {}, ())
    if not registry_chain: return _RegistryValidation(False, ("KEY_REGISTRY_CHAIN_REQUIRED",), None, {}, ())
    previous: Mapping[str, Any] | None = None
    snapshots: dict[int, Mapping[str, Any]] = {}
    generations: set[str] = set()
    last_domains: tuple[str, ...] = ()
    for idx, record in enumerate(registry_chain):
        if not isinstance(record, Mapping): p.append(f"KEY_REGISTRY_CHAIN_RECORD_MALFORMED:{idx}"); continue
        structural, current_keys = _validate_snapshot(record, expected_candidate_id)
        p.extend(f"CHAIN[{idx}]:{x}" for x in structural)
        sig_p, last_domains = _verify_bootstrap_signatures(record, trust)
        p.extend(f"CHAIN[{idx}]:{x}" for x in sig_p)
        seq = record.get("sequence"); generation = record.get("generation_id")
        if _nonempty(generation):
            if generation in generations: p.append(f"KEY_REGISTRY_CHAIN_GENERATION_REUSE_FORBIDDEN:{idx}")
            generations.add(str(generation))
        if _exact_int(seq, minimum=1):
            if seq in snapshots: p.append(f"KEY_REGISTRY_CHAIN_SEQUENCE_DUPLICATE:{seq}")
            snapshots[int(seq)] = record
        if idx == 0:
            if seq != 1 or type(seq) is not int: p.append("KEY_REGISTRY_CHAIN_GENESIS_SEQUENCE_MUST_BE_ONE")
            if record.get("predecessor_registry_digest") != "GENESIS": p.append("KEY_REGISTRY_CHAIN_GENESIS_PREDECESSOR_REQUIRED")
            for key_id, key in current_keys.items():
                if key.get("valid_from_registry_sequence") != 1 or type(key.get("valid_from_registry_sequence")) is not int:
                    p.append(f"KEY_REGISTRY_CHAIN_GENESIS_KEY_VALID_FROM_MUST_BE_ONE:{key_id}")
        else:
            assert previous is not None
            previous_seq = previous.get("sequence")
            if not (_exact_int(previous_seq, minimum=1) and _exact_int(seq, minimum=1) and seq == previous_seq + 1):
                p.append(f"KEY_REGISTRY_CHAIN_SEQUENCE_GAP:{idx}")
            if record.get("predecessor_registry_digest") != previous.get("registry_digest"): p.append(f"KEY_REGISTRY_CHAIN_PREDECESSOR_MISMATCH:{idx}")
            if record.get("registry_id") != previous.get("registry_id"): p.append(f"KEY_REGISTRY_CHAIN_REGISTRY_ID_CHANGED:{idx}")
            if record.get("generation_id") == previous.get("generation_id"): p.append(f"KEY_REGISTRY_CHAIN_MATERIAL_UPDATE_REQUIRES_NEW_GENERATION:{idx}")
            previous_keys = _snapshot_key_index(previous)
            for key_id, prior in previous_keys.items():
                current = current_keys.get(key_id)
                if current is None: p.append(f"KEY_REGISTRY_CHAIN_KEY_REMOVAL_FORBIDDEN:{key_id}"); continue
                for field in ("issuer_id", "control_domain_id", "algorithm", "public_key_b64", "roles", "valid_from_registry_sequence"):
                    if current.get(field) != prior.get(field): p.append(f"KEY_REGISTRY_CHAIN_KEY_IDENTITY_MUTATION_FORBIDDEN:{key_id}:{field}")
                if prior.get("state") == "REVOKED":
                    if current.get("state") != "REVOKED": p.append(f"KEY_REGISTRY_CHAIN_REVOKED_KEY_REACTIVATION_FORBIDDEN:{key_id}")
                    if current.get("revoked_at_registry_sequence") != prior.get("revoked_at_registry_sequence"): p.append(f"KEY_REGISTRY_CHAIN_REVOCATION_SEQUENCE_MUTATION_FORBIDDEN:{key_id}")
                elif current.get("state") == "REVOKED" and current.get("revoked_at_registry_sequence") != seq:
                    p.append(f"KEY_REGISTRY_CHAIN_REVOCATION_MUST_BIND_CURRENT_SEQUENCE:{key_id}")
            for key_id in set(current_keys) - set(previous_keys):
                key = current_keys[key_id]
                if key.get("valid_from_registry_sequence") != seq or type(key.get("valid_from_registry_sequence")) is not int:
                    p.append(f"KEY_REGISTRY_CHAIN_NEW_KEY_VALID_FROM_MUST_EQUAL_FIRST_APPEARANCE:{key_id}")
                if key.get("state") != "ACTIVE" or key.get("revoked_at_registry_sequence") is not None:
                    p.append(f"KEY_REGISTRY_CHAIN_NEW_KEY_MUST_ENTER_ACTIVE:{key_id}")
        previous = record
    valid = not p
    return _RegistryValidation(valid, tuple(sorted(set(p))), registry_chain[-1] if valid else None, snapshots if valid else {}, last_domains if valid else ())


def validate_governance_key_registry_chain(registry_chain: Sequence[Mapping[str, Any]], trust: PinnedBootstrapTrustSet, *, expected_candidate_id: str) -> dict[str, Any]:
    result = _validate_chain(registry_chain, trust, expected_candidate_id)
    out = _result(result.valid, result.problems, "GOVERNANCE_KEY_REGISTRY_CHAIN_AUTHENTICATED_UNDER_PINNED_ROOTS", "GOVERNANCE_KEY_REGISTRY_CHAIN_INVALID")
    out.update({
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
        })
    return out


def validate_governance_key_registry_chain_json(registry_chain_json: Sequence[bytes | str], trust: PinnedBootstrapTrustSet, *, expected_candidate_id: str) -> dict[str, Any]:
    try:
        parsed = [load_strict_json(raw) for raw in registry_chain_json]
    except (CanonicalizationError, UnicodeEncodeError) as exc:
        return _result(False, [f"STRICT_JSON_INGRESS:{exc}"], "UNREACHABLE", "GOVERNANCE_KEY_REGISTRY_CHAIN_INVALID")
    if not all(isinstance(row, Mapping) for row in parsed):
        return _result(False, ["STRICT_JSON_REGISTRY_RECORD_MUST_BE_OBJECT"], "UNREACHABLE", "GOVERNANCE_KEY_REGISTRY_CHAIN_INVALID")
    return validate_governance_key_registry_chain(parsed, trust, expected_candidate_id=expected_candidate_id)


def _head_match(current: Mapping[str, Any], head: PinnedRegistryHead) -> list[str]:
    p: list[str] = []
    if current.get("registry_id") != head.registry_id: p.append("SIGNED_RECORD_REGISTRY_HEAD_ID_MISMATCH")
    if current.get("candidate_id") != head.candidate_id: p.append("SIGNED_RECORD_REGISTRY_HEAD_CANDIDATE_MISMATCH")
    if current.get("sequence") != head.sequence or type(current.get("sequence")) is not type(head.sequence): p.append("SIGNED_RECORD_REGISTRY_HEAD_SEQUENCE_MISMATCH")
    if current.get("generation_id") != head.generation_id: p.append("SIGNED_RECORD_REGISTRY_HEAD_GENERATION_MISMATCH")
    if current.get("registry_digest") != head.registry_digest: p.append("SIGNED_RECORD_REGISTRY_HEAD_DIGEST_MISMATCH")
    return p


def verify_signed_governance_record(
    record: Mapping[str, Any], *, registry_chain: Sequence[Mapping[str, Any]],
    bootstrap_trust: PinnedBootstrapTrustSet, expected_current_registry_head: PinnedRegistryHead,
    expected_candidate_id: str, expected_generation_id: str, expected_record_type: str,
    expected_snapshot_id: str | None = None,
    forbidden_control_domain_ids: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    p: list[str] = []
    head_result = validate_pinned_registry_head(expected_current_registry_head, bootstrap_trust, expected_candidate_id=expected_candidate_id)
    if not head_result["valid"]: p.extend(f"SIGNED_RECORD_CURRENTNESS_ANCHOR:{x}" for x in head_result["problems"])
    chain = _validate_chain(registry_chain, bootstrap_trust, expected_candidate_id)
    if not chain.valid: p.extend(f"SIGNED_RECORD_REGISTRY:{x}" for x in chain.problems)

    if set(record.keys()) != SIGNED_RECORD_FIELDS: p.append("SIGNED_RECORD_FIELDS_NOT_EXACT")
    if record.get("schema_version") != 1: p.append("SIGNED_RECORD_SCHEMA_INVALID")
    if record.get("object_type") != "SIGNED_GOVERNANCE_RECORD": p.append("SIGNED_RECORD_OBJECT_TYPE_INVALID")
    if record.get("record_type") != expected_record_type: p.append("SIGNED_RECORD_TYPE_MISMATCH")
    canonical_role = RECORD_TYPE_REQUIRED_ROLE.get(expected_record_type)
    if canonical_role is None: p.append("SIGNED_RECORD_TYPE_POLICY_UNKNOWN")
    if canonical_role is not None and record.get("required_role") != canonical_role: p.append("SIGNED_RECORD_REQUIRED_ROLE_MISMATCH")
    if not _nonempty(record.get("record_id")): p.append("SIGNED_RECORD_ID_REQUIRED")
    if record.get("candidate_id") != expected_candidate_id: p.append("SIGNED_RECORD_CANDIDATE_MISMATCH")
    if record.get("generation_id") != expected_generation_id: p.append("SIGNED_RECORD_GENERATION_MISMATCH")
    if expected_snapshot_id is None:
        if record.get("snapshot_id") is not None: p.append("SIGNED_RECORD_UNEXPECTED_SNAPSHOT_BINDING")
    elif record.get("snapshot_id") != expected_snapshot_id: p.append("SIGNED_RECORD_SNAPSHOT_MISMATCH")
    if record.get("trust_set_id") != bootstrap_trust.trust_set_id: p.append("SIGNED_RECORD_TRUST_SET_MISMATCH")
    if record.get("signature_algorithm") != "ED25519": p.append("SIGNED_RECORD_SIGNATURE_ALGORITHM_UNSUPPORTED")
    if not _nonempty(record.get("issuer_id")) or not _nonempty(record.get("key_id")): p.append("SIGNED_RECORD_ISSUER_KEY_REQUIRED")
    issued_sequence = record.get("issued_registry_sequence")
    if not _exact_int(issued_sequence, minimum=1): p.append("SIGNED_RECORD_ISSUED_REGISTRY_SEQUENCE_INVALID")
    if not _sha256_hex(record.get("issued_registry_digest")): p.append("SIGNED_RECORD_ISSUED_REGISTRY_DIGEST_INVALID")

    payload_ok = False
    supplied_payload_digest = record.get("payload_digest")
    if not _sha256_hex(supplied_payload_digest): p.append("SIGNED_RECORD_PAYLOAD_DIGEST_INVALID")
    else:
        try: payload_ok = canonical_sha256(record.get("payload")) == supplied_payload_digest
        except CanonicalizationError: p.append("SIGNED_RECORD_PAYLOAD_CANONICALIZATION_FAILED")
        else:
            if not payload_ok: p.append("SIGNED_RECORD_PAYLOAD_DIGEST_MISMATCH")

    key: Mapping[str, Any] | None = None
    currentness_matched = False
    registry_authority_ok = False
    current = chain.current if chain.valid else None
    if current is not None:
        head_p = _head_match(current, expected_current_registry_head) if head_result["valid"] else []
        p.extend(head_p)
        currentness_matched = head_result["valid"] and not head_p
        if expected_current_registry_head.trust_set_id != bootstrap_trust.trust_set_id: p.append("SIGNED_RECORD_REGISTRY_HEAD_TRUST_SET_MISMATCH")
        if record.get("generation_id") != current.get("generation_id"): p.append("SIGNED_RECORD_GENERATION_NOT_CURRENT")
        if expected_generation_id != current.get("generation_id"): p.append("SIGNED_RECORD_EXPECTED_GENERATION_NOT_CURRENT")
        if not (_exact_int(current.get("sequence"), minimum=1) and _exact_int(issued_sequence, minimum=1) and issued_sequence == current.get("sequence")):
            p.append("SIGNED_RECORD_NOT_ISSUED_UNDER_CURRENT_REGISTRY")
        if record.get("issued_registry_digest") != current.get("registry_digest"): p.append("SIGNED_RECORD_ISSUED_REGISTRY_DIGEST_MISMATCH")
        if record.get("issued_registry_digest") != expected_current_registry_head.registry_digest: p.append("SIGNED_RECORD_ISSUED_REGISTRY_DIGEST_NOT_PINNED_HEAD")
        snapshot = chain.snapshots_by_sequence.get(int(issued_sequence)) if _exact_int(issued_sequence, minimum=1) else None
        if snapshot is None: p.append("SIGNED_RECORD_ISSUANCE_REGISTRY_SNAPSHOT_NOT_FOUND")
        else:
            if snapshot.get("generation_id") != record.get("generation_id"): p.append("SIGNED_RECORD_ISSUANCE_GENERATION_MISMATCH")
            if snapshot.get("registry_digest") != record.get("issued_registry_digest"): p.append("SIGNED_RECORD_ISSUANCE_DIGEST_MISMATCH")
            key = _snapshot_key_index(snapshot).get(str(record.get("key_id")))
            if key is None: p.append("SIGNED_RECORD_KEY_NOT_IN_ISSUANCE_REGISTRY")
        before = len(p)
        if key is not None:
            if key.get("issuer_id") != record.get("issuer_id"): p.append("SIGNED_RECORD_ISSUER_KEY_BINDING_MISMATCH")
            if key.get("algorithm") != "ED25519": p.append("SIGNED_RECORD_KEY_ALGORITHM_UNSUPPORTED")
            roles = key.get("roles")
            if canonical_role is None or not isinstance(roles, list) or canonical_role not in roles: p.append("SIGNED_RECORD_ISSUER_ROLE_NOT_AUTHORIZED")
            domain = key.get("control_domain_id")
            if domain in forbidden_control_domain_ids: p.append("SIGNED_RECORD_ISSUER_FORBIDDEN_CONTROL_DOMAIN")
            if domain in bootstrap_trust.candidate_control_domain_ids: p.append("SIGNED_RECORD_ISSUER_CANDIDATE_CONTROLLED_DOMAIN")
            if key.get("state") != "ACTIVE": p.append("SIGNED_RECORD_KEY_NOT_CURRENTLY_ACTIVE")
            if not _exact_int(key.get("valid_from_registry_sequence"), minimum=1) or key.get("valid_from_registry_sequence") > issued_sequence:
                p.append("SIGNED_RECORD_KEY_NOT_YET_VALID")
        registry_authority_ok = key is not None and len(p) == before and currentness_matched and chain.valid

    signature_ok = False
    if _b64(record.get("signature_b64"), ED25519_SIGNATURE_BYTES) is None: p.append("SIGNED_RECORD_SIGNATURE_ENCODING_INVALID")
    elif key is not None:
        try: message = signed_record_signature_message(record)
        except CanonicalizationError: p.append("SIGNED_RECORD_CANONICALIZATION_FAILED")
        else:
            signature_ok = _verify_ed25519(str(key.get("public_key_b64", "")), str(record.get("signature_b64", "")), message)
            if not signature_ok: p.append("SIGNED_RECORD_SIGNATURE_INVALID")

    valid = not p
    out = _result(valid, p, "SIGNED_GOVERNANCE_RECORD_AUTHENTICATED_UNDER_CURRENT_PINNED_REGISTRY_HEAD", "SIGNED_GOVERNANCE_RECORD_INVALID")
    out.update({
        "content_integrity_verified": payload_ok,
        "issuer_signature_verified": signature_ok,
        "authority_registry_verified": registry_authority_ok,
        "registry_currentness_anchor_matched": currentness_matched,
        "trust_anchor_origin": "OUT_OF_BAND_PINNED_CONFIG_REQUIRED",
        "trust_anchor_provisioning_proven": False,
        "currentness_anchor_origin": "OUT_OF_BAND_PINNED_CURRENTNESS_REQUIRED",
        "currentness_anchor_provisioning_proven": False,
    })
    if key is not None: out["issuer_control_domain_id"] = key.get("control_domain_id")
    return out


def verify_signed_governance_record_json(
    raw_record: bytes | str, *, registry_chain_json: Sequence[bytes | str],
    bootstrap_trust: PinnedBootstrapTrustSet, expected_current_registry_head: PinnedRegistryHead,
    expected_candidate_id: str, expected_generation_id: str, expected_record_type: str,
    expected_snapshot_id: str | None = None,
    forbidden_control_domain_ids: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    try:
        record = load_strict_json(raw_record)
        chain = [load_strict_json(raw) for raw in registry_chain_json]
    except (CanonicalizationError, UnicodeEncodeError) as exc:
        return _result(False, [f"STRICT_JSON_INGRESS:{exc}"], "UNREACHABLE", "SIGNED_GOVERNANCE_RECORD_INVALID")
    if not isinstance(record, Mapping) or not all(isinstance(row, Mapping) for row in chain):
        return _result(False, ["STRICT_JSON_SIGNED_RECORD_OR_REGISTRY_MUST_BE_OBJECT"], "UNREACHABLE", "SIGNED_GOVERNANCE_RECORD_INVALID")
    return verify_signed_governance_record(
        record, registry_chain=chain, bootstrap_trust=bootstrap_trust,
        expected_current_registry_head=expected_current_registry_head,
        expected_candidate_id=expected_candidate_id, expected_generation_id=expected_generation_id,
        expected_record_type=expected_record_type, expected_snapshot_id=expected_snapshot_id,
        forbidden_control_domain_ids=forbidden_control_domain_ids,
    )
