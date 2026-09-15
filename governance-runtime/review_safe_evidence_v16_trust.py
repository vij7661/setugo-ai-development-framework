"""Review Safe Evidence V16 authenticated trust foundation.

Construction-stage implementation only. This module separates content integrity,
issuer authenticity, authority admissibility, and out-of-band root provisioning.
No result grants runtime, release, scientific, effect, or terminal authority.
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

ROLE_VOCABULARY = frozenset({
    "GOVERNANCE_GENERATION_WITNESS_AUTHORITY",
    "REVIEWER_QUALIFICATION_AUTHORITY",
    "EVIDENCE_UNIVERSE_DERIVATION_AUTHORITY",
    "OBLIGATION_MATERIALITY_AUTHORITY",
    "RAW_EVIDENCE_CAPTURE_AUTHORITY",
    "NA_PROOF_AUTHORITY",
    "NA_CHALLENGE_RESOLUTION_AUTHORITY",
    "MONITOR_EXECUTION_AUTHORITY",
    "COVERAGE_CERTIFICATE_AUTHORITY",
    "SNAPSHOT_WRITER_AUTHORITY",
    "SNAPSHOT_WITNESS_AUTHORITY",
    "CLEAN_ROOM_ATTESTATION_AUTHORITY",
    "REVIEW_RESPONSE_RECEIPT_AUTHORITY",
    "BLOCKER_RESOLUTION_AUTHORITY",
    "EFFECT_TOKEN_ISSUER_AUTHORITY",
    "EFFECT_GATEWAY_AUTHORITY",
    "RESIDUAL_TRUST_ACCEPTANCE_AUTHORITY",
    "ADJUDICATION_AUTHORITY",
    "PROJECTION_COMPILER_AUTHORITY",
    "PROJECTION_VERIFIER_AUTHORITY",
    "DISCLOSURE_CERTIFIER_AUTHORITY",
    "UNIVERSE_CHALLENGE_AUTHORITY",
})

REGISTRY_TOP_LEVEL_FIELDS = frozenset({
    "schema_version", "object_type", "registry_id", "candidate_id",
    "generation_id", "sequence", "predecessor_registry_digest", "keys",
    "registry_digest", "bootstrap_signatures",
})
REGISTRY_KEY_FIELDS = frozenset({
    "issuer_id", "key_id", "control_domain_id", "algorithm", "public_key_b64",
    "roles", "state", "valid_from_registry_sequence", "revoked_at_registry_sequence",
})
REGISTRY_SIGNATURE_FIELDS = frozenset({"root_id", "key_id", "algorithm", "signature_b64"})
SIGNED_RECORD_FIELDS = frozenset({
    "schema_version", "object_type", "record_type", "record_id", "candidate_id",
    "generation_id", "snapshot_id", "issued_registry_sequence", "issuer_id", "key_id",
    "required_role", "payload_digest", "payload", "signature_algorithm", "signature_b64",
})


class CanonicalizationError(ValueError):
    """Input cannot be represented by the restricted V16 canonical JSON profile."""


@dataclass(frozen=True)
class BootstrapRoot:
    root_id: str
    key_id: str
    control_domain_id: str
    public_key_b64: str
    algorithm: str = "ED25519"


@dataclass(frozen=True)
class PinnedBootstrapTrustSet:
    """Out-of-band root input; provisioning is not proven by this module."""

    trust_set_id: str
    threshold_control_domains: int
    roots: tuple[BootstrapRoot, ...]
    candidate_control_domain_ids: frozenset[str] = frozenset()


@dataclass(frozen=True)
class _RegistryValidation:
    valid: bool
    problems: tuple[str, ...]
    current: Mapping[str, Any] | None
    key_index: Mapping[str, Mapping[str, Any]]
    snapshots_by_sequence: Mapping[int, Mapping[str, Any]]
    authenticated_bootstrap_domains: tuple[str, ...]


def _base_result(valid: bool, problems: Iterable[str], state_ok: str, state_bad: str) -> dict[str, Any]:
    normalized = tuple(sorted(set(problems)))
    return {
        "state": state_ok if valid else state_bad,
        "valid": valid,
        "qualified": False,
        "implementation_qualification": IMPLEMENTATION_QUALIFICATION,
        "runtime_qualification": RUNTIME_QUALIFICATION,
        "authority_effect": AUTHORITY_EFFECT,
        "problems": list(normalized),
    }


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha256_hex(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256_RE.fullmatch(value))


def _strict_b64decode(value: Any, expected_len: int) -> bytes | None:
    if not isinstance(value, str):
        return None
    try:
        raw = base64.b64decode(value.encode("ascii"), validate=True)
    except (ValueError, UnicodeEncodeError, binascii.Error):
        return None
    return raw if len(raw) == expected_len else None


def _normalize_json(value: Any, *, path: str = "$") -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > MAX_CANONICAL_INTEGER:
            raise CanonicalizationError(f"INTEGER_OUT_OF_CANONICAL_RANGE:{path}")
        return value
    if isinstance(value, float):
        raise CanonicalizationError(f"FLOAT_FORBIDDEN:{path}")
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, (list, tuple)):
        return [_normalize_json(v, path=f"{path}[{i}]") for i, v in enumerate(value)]
    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            if not isinstance(raw_key, str):
                raise CanonicalizationError(f"NON_STRING_KEY:{path}")
            key = unicodedata.normalize("NFC", raw_key)
            if key in out:
                raise CanonicalizationError(f"NORMALIZED_KEY_COLLISION:{path}.{key}")
            out[key] = _normalize_json(raw_value, path=f"{path}.{key}")
        return out
    raise CanonicalizationError(f"UNSUPPORTED_TYPE:{path}:{type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    normalized = _normalize_json(value)
    return json.dumps(
        normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_strict_json(raw: bytes | str) -> Any:
    """Strict serialized ingress: UTF-8, no duplicate keys, no floats."""
    if isinstance(raw, bytes):
        text = raw.decode("utf-8", errors="strict")
    elif isinstance(raw, str):
        text = raw
    else:
        raise CanonicalizationError("STRICT_JSON_INPUT_MUST_BE_BYTES_OR_STRING")

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            nkey = unicodedata.normalize("NFC", key)
            if nkey in out:
                raise CanonicalizationError(f"DUPLICATE_OR_NORMALIZED_KEY:{nkey}")
            out[nkey] = value
        return out

    def reject_float(token: str) -> Any:
        raise CanonicalizationError(f"FLOAT_FORBIDDEN:{token}")

    try:
        parsed = json.loads(text, object_pairs_hook=pairs_hook, parse_float=reject_float)
    except CanonicalizationError:
        raise
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise CanonicalizationError("STRICT_JSON_PARSE_FAILED") from exc
    return _normalize_json(parsed)


def _registry_material(record: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in {"registry_digest", "bootstrap_signatures"}}


def registry_digest(record: Mapping[str, Any]) -> str:
    return canonical_sha256(_registry_material(record))


def registry_signature_message(
    digest_hex: str,
    *,
    trust_set_id: str,
    root_id: str,
    key_id: str,
    control_domain_id: str,
) -> bytes:
    if not _sha256_hex(digest_hex):
        raise ValueError("REGISTRY_DIGEST_INVALID")
    identity = {
        "trust_set_id": trust_set_id,
        "root_id": root_id,
        "key_id": key_id,
        "control_domain_id": control_domain_id,
        "registry_digest": digest_hex,
    }
    return b"RSE-V16:KEY-REGISTRY-ROOT:" + canonical_bytes(identity)


def signed_record_signature_message(record: Mapping[str, Any]) -> bytes:
    material = {k: v for k, v in record.items() if k != "signature_b64"}
    return b"RSE-V16:SIGNED-RECORD:" + canonical_bytes(material)


def _verify_ed25519(public_key_b64: str, signature_b64: str, message: bytes) -> bool:
    if Ed25519PublicKey is None:
        return False
    public_raw = _strict_b64decode(public_key_b64, ED25519_PUBLIC_KEY_BYTES)
    sig_raw = _strict_b64decode(signature_b64, ED25519_SIGNATURE_BYTES)
    if public_raw is None or sig_raw is None:
        return False
    try:
        Ed25519PublicKey.from_public_bytes(public_raw).verify(sig_raw, message)
    except (InvalidSignature, ValueError):
        return False
    return True


def validate_bootstrap_trust_set(trust: PinnedBootstrapTrustSet) -> dict[str, Any]:
    p: list[str] = []
    if not _nonempty(trust.trust_set_id):
        p.append("BOOTSTRAP_TRUST_SET_ID_REQUIRED")
    if not isinstance(trust.threshold_control_domains, int) or trust.threshold_control_domains < 2:
        p.append("BOOTSTRAP_THRESHOLD_MIN_TWO_DOMAINS")
    if not trust.roots:
        p.append("BOOTSTRAP_ROOTS_REQUIRED")

    seen_root_ids: set[str] = set()
    seen_key_ids: set[str] = set()
    seen_public_keys: set[bytes] = set()
    domains: set[str] = set()
    for idx, root in enumerate(trust.roots):
        if not _nonempty(root.root_id):
            p.append(f"BOOTSTRAP_ROOT_ID_REQUIRED:{idx}")
        if not _nonempty(root.key_id):
            p.append(f"BOOTSTRAP_KEY_ID_REQUIRED:{idx}")
        if not _nonempty(root.control_domain_id):
            p.append(f"BOOTSTRAP_CONTROL_DOMAIN_REQUIRED:{idx}")
        if root.algorithm != "ED25519":
            p.append(f"BOOTSTRAP_ALGORITHM_UNSUPPORTED:{idx}")
        public_raw = _strict_b64decode(root.public_key_b64, ED25519_PUBLIC_KEY_BYTES)
        if public_raw is None:
            p.append(f"BOOTSTRAP_PUBLIC_KEY_INVALID:{idx}")
        elif public_raw in seen_public_keys:
            p.append(f"BOOTSTRAP_PUBLIC_KEY_REUSE_FORBIDDEN:{idx}")
        else:
            seen_public_keys.add(public_raw)
        if root.root_id in seen_root_ids:
            p.append(f"BOOTSTRAP_ROOT_ID_DUPLICATE:{root.root_id}")
        seen_root_ids.add(root.root_id)
        if root.key_id in seen_key_ids:
            p.append(f"BOOTSTRAP_KEY_ID_DUPLICATE:{root.key_id}")
        seen_key_ids.add(root.key_id)
        if root.control_domain_id in trust.candidate_control_domain_ids:
            p.append(f"BOOTSTRAP_ROOT_CANDIDATE_CONTROLLED:{root.root_id}")
        if _nonempty(root.control_domain_id):
            domains.add(root.control_domain_id)

    if isinstance(trust.threshold_control_domains, int) and trust.threshold_control_domains > len(domains):
        p.append("BOOTSTRAP_THRESHOLD_EXCEEDS_DISTINCT_DOMAINS")

    out = _base_result(not p, p, "BOOTSTRAP_TRUST_SET_STRUCTURALLY_VALID", "BOOTSTRAP_TRUST_SET_INVALID")
    out["trust_anchor_origin"] = "OUT_OF_BAND_PINNED_CONFIG_REQUIRED"
    out["trust_anchor_provisioning_proven"] = False
    out["distinct_root_control_domains"] = sorted(domains)
    return out


def _validate_registry_snapshot_structure(
    record: Mapping[str, Any], *, expected_candidate_id: str
) -> tuple[list[str], dict[str, Mapping[str, Any]]]:
    p: list[str] = []
    if set(record.keys()) != REGISTRY_TOP_LEVEL_FIELDS:
        p.append("KEY_REGISTRY_TOP_LEVEL_FIELDS_NOT_EXACT")
    if record.get("schema_version") != 1:
        p.append("KEY_REGISTRY_SCHEMA_INVALID")
    if record.get("object_type") != "GOVERNANCE_KEY_REGISTRY":
        p.append("KEY_REGISTRY_OBJECT_TYPE_INVALID")
    if not _nonempty(record.get("registry_id")):
        p.append("KEY_REGISTRY_ID_REQUIRED")
    if record.get("candidate_id") != expected_candidate_id:
        p.append("KEY_REGISTRY_CANDIDATE_MISMATCH")
    if not _nonempty(record.get("generation_id")):
        p.append("KEY_REGISTRY_GENERATION_REQUIRED")
    sequence = record.get("sequence")
    if not isinstance(sequence, int) or sequence < 1:
        p.append("KEY_REGISTRY_SEQUENCE_INVALID")
    predecessor = record.get("predecessor_registry_digest")
    if predecessor != "GENESIS" and not _sha256_hex(predecessor):
        p.append("KEY_REGISTRY_PREDECESSOR_INVALID")

    keys = record.get("keys")
    key_index: dict[str, Mapping[str, Any]] = {}
    if not isinstance(keys, list) or not keys:
        p.append("KEY_REGISTRY_KEYS_REQUIRED")
        keys = []
    for idx, key in enumerate(keys):
        if not isinstance(key, Mapping):
            p.append(f"KEY_REGISTRY_KEY_MALFORMED:{idx}")
            continue
        if set(key.keys()) != REGISTRY_KEY_FIELDS:
            p.append(f"KEY_REGISTRY_KEY_FIELDS_NOT_EXACT:{idx}")
        for field in ("issuer_id", "key_id", "control_domain_id"):
            if not _nonempty(key.get(field)):
                p.append(f"KEY_REGISTRY_KEY_FIELD_REQUIRED:{idx}:{field}")
        if key.get("algorithm") != "ED25519":
            p.append(f"KEY_REGISTRY_KEY_ALGORITHM_UNSUPPORTED:{idx}")
        if _strict_b64decode(key.get("public_key_b64"), ED25519_PUBLIC_KEY_BYTES) is None:
            p.append(f"KEY_REGISTRY_PUBLIC_KEY_INVALID:{idx}")
        roles = key.get("roles")
        if not isinstance(roles, list) or not roles or not all(r in ROLE_VOCABULARY for r in roles):
            p.append(f"KEY_REGISTRY_ROLES_INVALID:{idx}")
        elif len(roles) != len(set(roles)):
            p.append(f"KEY_REGISTRY_ROLE_DUPLICATE:{idx}")
        state = key.get("state")
        if state not in {"ACTIVE", "REVOKED"}:
            p.append(f"KEY_REGISTRY_KEY_STATE_INVALID:{idx}")
        valid_from = key.get("valid_from_registry_sequence")
        revoked_at = key.get("revoked_at_registry_sequence")
        if not isinstance(valid_from, int) or valid_from < 1:
            p.append(f"KEY_REGISTRY_VALID_FROM_INVALID:{idx}")
        elif isinstance(sequence, int) and valid_from > sequence:
            p.append(f"KEY_REGISTRY_VALID_FROM_FUTURE:{idx}")
        if state == "ACTIVE" and revoked_at is not None:
            p.append(f"KEY_REGISTRY_ACTIVE_WITH_REVOCATION:{idx}")
        if state == "REVOKED":
            if not isinstance(revoked_at, int) or revoked_at < 1:
                p.append(f"KEY_REGISTRY_REVOCATION_SEQUENCE_REQUIRED:{idx}")
            elif isinstance(sequence, int) and revoked_at > sequence:
                p.append(f"KEY_REGISTRY_REVOCATION_IN_FUTURE:{idx}")
            elif isinstance(valid_from, int) and revoked_at < valid_from:
                p.append(f"KEY_REGISTRY_REVOCATION_BEFORE_VALIDITY:{idx}")
        key_id_value = key.get("key_id")
        if _nonempty(key_id_value):
            if str(key_id_value) in key_index:
                p.append(f"KEY_REGISTRY_KEY_ID_DUPLICATE:{key_id_value}")
            else:
                key_index[str(key_id_value)] = key

    issuer_domains: dict[str, str] = {}
    for key in key_index.values():
        issuer, domain = key.get("issuer_id"), key.get("control_domain_id")
        if _nonempty(issuer) and _nonempty(domain):
            prior = issuer_domains.get(str(issuer))
            if prior is not None and prior != domain:
                p.append(f"KEY_REGISTRY_ISSUER_MULTI_DOMAIN_FORBIDDEN:{issuer}")
            issuer_domains[str(issuer)] = str(domain)

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
    if not isinstance(signatures, list) or not signatures:
        p.append("KEY_REGISTRY_BOOTSTRAP_SIGNATURES_REQUIRED")
    else:
        for idx, sig in enumerate(signatures):
            if not isinstance(sig, Mapping):
                p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_MALFORMED:{idx}")
                continue
            if set(sig.keys()) != REGISTRY_SIGNATURE_FIELDS:
                p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_FIELDS_NOT_EXACT:{idx}")
            if not _nonempty(sig.get("root_id")) or not _nonempty(sig.get("key_id")):
                p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_ID_REQUIRED:{idx}")
            if sig.get("algorithm") != "ED25519":
                p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_ALGORITHM_UNSUPPORTED:{idx}")
            if _strict_b64decode(sig.get("signature_b64"), ED25519_SIGNATURE_BYTES) is None:
                p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_ENCODING_INVALID:{idx}")
    return p, key_index


def _verify_registry_bootstrap_signatures(
    record: Mapping[str, Any], trust: PinnedBootstrapTrustSet
) -> tuple[list[str], tuple[str, ...]]:
    p: list[str] = []
    digest = record.get("registry_digest")
    if not _sha256_hex(digest):
        return ["KEY_REGISTRY_BOOTSTRAP_CANNOT_VERIFY_WITHOUT_DIGEST"], ()
    root_index = {(r.root_id, r.key_id): r for r in trust.roots}
    seen_signers: set[tuple[str, str]] = set()
    authenticated_domains: set[str] = set()
    signatures = record.get("bootstrap_signatures")
    if not isinstance(signatures, list):
        return ["KEY_REGISTRY_BOOTSTRAP_SIGNATURES_REQUIRED"], ()

    for idx, sig in enumerate(signatures):
        if not isinstance(sig, Mapping):
            continue
        pair = (sig.get("root_id"), sig.get("key_id"))
        if pair in seen_signers:
            p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNER_DUPLICATE:{idx}")
            continue
        seen_signers.add(pair)
        root = root_index.get(pair)  # type: ignore[arg-type]
        if root is None:
            p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNER_UNKNOWN:{idx}")
            continue
        if root.control_domain_id in trust.candidate_control_domain_ids:
            p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNER_CANDIDATE_CONTROLLED:{root.root_id}")
            continue
        try:
            message = registry_signature_message(
                str(digest),
                trust_set_id=trust.trust_set_id,
                root_id=root.root_id,
                key_id=root.key_id,
                control_domain_id=root.control_domain_id,
            )
        except (ValueError, CanonicalizationError):
            p.append(f"KEY_REGISTRY_BOOTSTRAP_MESSAGE_INVALID:{idx}")
            continue
        if sig.get("algorithm") != "ED25519" or not _verify_ed25519(
            root.public_key_b64, str(sig.get("signature_b64", "")), message
        ):
            p.append(f"KEY_REGISTRY_BOOTSTRAP_SIGNATURE_INVALID:{idx}")
            continue
        authenticated_domains.add(root.control_domain_id)
    if len(authenticated_domains) < trust.threshold_control_domains:
        p.append("KEY_REGISTRY_BOOTSTRAP_THRESHOLD_NOT_MET")
    return p, tuple(sorted(authenticated_domains))


def _snapshot_key_index(snapshot: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    keys = snapshot.get("keys")
    if not isinstance(keys, list):
        return {}
    return {
        str(k.get("key_id")): k
        for k in keys
        if isinstance(k, Mapping) and _nonempty(k.get("key_id"))
    }


def _validate_registry_chain_internal(
    registry_chain: Sequence[Mapping[str, Any]],
    trust: PinnedBootstrapTrustSet,
    *,
    expected_candidate_id: str,
) -> _RegistryValidation:
    p: list[str] = []
    trust_result = validate_bootstrap_trust_set(trust)
    if not trust_result["valid"]:
        p.extend(f"CHAIN:{x}" for x in trust_result["problems"])
        return _RegistryValidation(False, tuple(sorted(set(p))), None, {}, {}, ())
    if not registry_chain:
        return _RegistryValidation(False, ("KEY_REGISTRY_CHAIN_REQUIRED",), None, {}, {}, ())

    previous: Mapping[str, Any] | None = None
    snapshots: dict[int, Mapping[str, Any]] = {}
    seen_generations: set[str] = set()
    current_index: dict[str, Mapping[str, Any]] = {}
    current_domains: tuple[str, ...] = ()

    for idx, record in enumerate(registry_chain):
        if not isinstance(record, Mapping):
            p.append(f"KEY_REGISTRY_CHAIN_RECORD_MALFORMED:{idx}")
            continue
        structural, key_index = _validate_registry_snapshot_structure(
            record, expected_candidate_id=expected_candidate_id
        )
        p.extend(f"CHAIN[{idx}]:{x}" for x in structural)
        signature_problems, domains = _verify_registry_bootstrap_signatures(record, trust)
        p.extend(f"CHAIN[{idx}]:{x}" for x in signature_problems)

        seq = record.get("sequence")
        generation = record.get("generation_id")
        if _nonempty(generation):
            if str(generation) in seen_generations:
                p.append(f"KEY_REGISTRY_CHAIN_GENERATION_REUSE_FORBIDDEN:{idx}")
            seen_generations.add(str(generation))
        if isinstance(seq, int):
            if seq in snapshots:
                p.append(f"KEY_REGISTRY_CHAIN_SEQUENCE_DUPLICATE:{seq}")
            snapshots[seq] = record

        if idx == 0:
            if seq != 1:
                p.append("KEY_REGISTRY_CHAIN_GENESIS_SEQUENCE_MUST_BE_ONE")
            if record.get("predecessor_registry_digest") != "GENESIS":
                p.append("KEY_REGISTRY_CHAIN_GENESIS_PREDECESSOR_REQUIRED")
            for prior_key_id, key in key_index.items():
                if key.get("valid_from_registry_sequence") != 1:
                    p.append(f"KEY_REGISTRY_CHAIN_GENESIS_KEY_VALID_FROM_MUST_BE_ONE:{prior_key_id}")
        else:
            assert previous is not None
            previous_seq = previous.get("sequence")
            if not isinstance(previous_seq, int) or seq != previous_seq + 1:
                p.append(f"KEY_REGISTRY_CHAIN_SEQUENCE_GAP:{idx}")
            if record.get("predecessor_registry_digest") != previous.get("registry_digest"):
                p.append(f"KEY_REGISTRY_CHAIN_PREDECESSOR_MISMATCH:{idx}")
            if record.get("registry_id") != previous.get("registry_id"):
                p.append(f"KEY_REGISTRY_CHAIN_REGISTRY_ID_CHANGED:{idx}")
            if record.get("generation_id") == previous.get("generation_id"):
                p.append(f"KEY_REGISTRY_CHAIN_MATERIAL_UPDATE_REQUIRES_NEW_GENERATION:{idx}")

            previous_keys = _snapshot_key_index(previous)
            current_keys = key_index
            for prior_key_id, prior_key in previous_keys.items():
                current_key = current_keys.get(prior_key_id)
                if current_key is None:
                    p.append(f"KEY_REGISTRY_CHAIN_KEY_REMOVAL_FORBIDDEN:{prior_key_id}")
                    continue
                for field in (
                    "issuer_id", "control_domain_id", "algorithm", "public_key_b64",
                    "roles", "valid_from_registry_sequence",
                ):
                    if current_key.get(field) != prior_key.get(field):
                        p.append(f"KEY_REGISTRY_CHAIN_KEY_IDENTITY_MUTATION_FORBIDDEN:{prior_key_id}:{field}")
                if prior_key.get("state") == "REVOKED":
                    if current_key.get("state") != "REVOKED":
                        p.append(f"KEY_REGISTRY_CHAIN_REVOKED_KEY_REACTIVATION_FORBIDDEN:{prior_key_id}")
                    if current_key.get("revoked_at_registry_sequence") != prior_key.get("revoked_at_registry_sequence"):
                        p.append(f"KEY_REGISTRY_CHAIN_REVOCATION_SEQUENCE_MUTATION_FORBIDDEN:{prior_key_id}")
                elif current_key.get("state") == "REVOKED" and current_key.get("revoked_at_registry_sequence") != seq:
                    p.append(f"KEY_REGISTRY_CHAIN_REVOCATION_MUST_BIND_CURRENT_SEQUENCE:{prior_key_id}")

            for new_key_id in set(current_keys) - set(previous_keys):
                new_key = current_keys[new_key_id]
                if new_key.get("valid_from_registry_sequence") != seq:
                    p.append(f"KEY_REGISTRY_CHAIN_NEW_KEY_VALID_FROM_MUST_EQUAL_FIRST_APPEARANCE:{new_key_id}")
                if new_key.get("state") != "ACTIVE" or new_key.get("revoked_at_registry_sequence") is not None:
                    p.append(f"KEY_REGISTRY_CHAIN_NEW_KEY_MUST_ENTER_ACTIVE:{new_key_id}")

        previous = record
        current_index = key_index
        current_domains = domains

    valid = not p
    return _RegistryValidation(
        valid,
        tuple(sorted(set(p))),
        registry_chain[-1] if valid else None,
        current_index if valid else {},
        snapshots if valid else {},
        current_domains if valid else (),
    )


def validate_governance_key_registry_chain(
    registry_chain: Sequence[Mapping[str, Any]],
    trust: PinnedBootstrapTrustSet,
    *, expected_candidate_id: str,
) -> dict[str, Any]:
    result = _validate_registry_chain_internal(
        registry_chain, trust, expected_candidate_id=expected_candidate_id
    )
    out = _base_result(
        result.valid, result.problems,
        "GOVERNANCE_KEY_REGISTRY_CHAIN_AUTHENTICATED_UNDER_PINNED_ROOTS",
        "GOVERNANCE_KEY_REGISTRY_CHAIN_INVALID",
    )
    out["trust_anchor_origin"] = "OUT_OF_BAND_PINNED_CONFIG_REQUIRED"
    out["trust_anchor_provisioning_proven"] = False
    out["bootstrap_authenticated_control_domains"] = list(result.authenticated_bootstrap_domains)
    if result.current is not None:
        out["registry_id"] = result.current.get("registry_id")
        out["current_registry_digest"] = result.current.get("registry_digest")
        out["current_registry_sequence"] = result.current.get("sequence")
        out["current_generation_id"] = result.current.get("generation_id")
    return out


def validate_governance_key_registry_chain_json(
    registry_chain_json: Sequence[bytes | str],
    trust: PinnedBootstrapTrustSet,
    *, expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        parsed = [load_strict_json(raw) for raw in registry_chain_json]
    except CanonicalizationError as exc:
        return _base_result(False, [f"STRICT_JSON_INGRESS:{exc}"], "UNREACHABLE", "GOVERNANCE_KEY_REGISTRY_CHAIN_INVALID")
    if not all(isinstance(item, Mapping) for item in parsed):
        return _base_result(False, ["STRICT_JSON_REGISTRY_RECORD_MUST_BE_OBJECT"], "UNREACHABLE", "GOVERNANCE_KEY_REGISTRY_CHAIN_INVALID")
    return validate_governance_key_registry_chain(parsed, trust, expected_candidate_id=expected_candidate_id)


def verify_signed_governance_record(
    record: Mapping[str, Any],
    *,
    registry_chain: Sequence[Mapping[str, Any]],
    bootstrap_trust: PinnedBootstrapTrustSet,
    expected_candidate_id: str,
    expected_generation_id: str,
    expected_record_type: str,
    required_role: str,
    expected_snapshot_id: str | None = None,
    forbidden_control_domain_ids: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    p: list[str] = []
    chain = _validate_registry_chain_internal(
        registry_chain, bootstrap_trust, expected_candidate_id=expected_candidate_id
    )
    if not chain.valid:
        p.extend(f"SIGNED_RECORD_REGISTRY:{x}" for x in chain.problems)

    if set(record.keys()) != SIGNED_RECORD_FIELDS:
        p.append("SIGNED_RECORD_FIELDS_NOT_EXACT")
    if record.get("schema_version") != 1:
        p.append("SIGNED_RECORD_SCHEMA_INVALID")
    if record.get("object_type") != "SIGNED_GOVERNANCE_RECORD":
        p.append("SIGNED_RECORD_OBJECT_TYPE_INVALID")
    if record.get("record_type") != expected_record_type:
        p.append("SIGNED_RECORD_TYPE_MISMATCH")
    if not _nonempty(record.get("record_id")):
        p.append("SIGNED_RECORD_ID_REQUIRED")
    if record.get("candidate_id") != expected_candidate_id:
        p.append("SIGNED_RECORD_CANDIDATE_MISMATCH")
    if record.get("generation_id") != expected_generation_id:
        p.append("SIGNED_RECORD_GENERATION_MISMATCH")
    if expected_snapshot_id is not None and record.get("snapshot_id") != expected_snapshot_id:
        p.append("SIGNED_RECORD_SNAPSHOT_MISMATCH")
    if expected_snapshot_id is None and record.get("snapshot_id") is not None:
        p.append("SIGNED_RECORD_UNEXPECTED_SNAPSHOT_BINDING")
    if required_role not in ROLE_VOCABULARY:
        p.append("SIGNED_RECORD_REQUIRED_ROLE_UNKNOWN")
    if record.get("required_role") != required_role:
        p.append("SIGNED_RECORD_REQUIRED_ROLE_MISMATCH")
    if record.get("signature_algorithm") != "ED25519":
        p.append("SIGNED_RECORD_SIGNATURE_ALGORITHM_UNSUPPORTED")
    if not _nonempty(record.get("issuer_id")) or not _nonempty(record.get("key_id")):
        p.append("SIGNED_RECORD_ISSUER_KEY_REQUIRED")

    payload_digest_ok = False
    supplied_payload_digest = record.get("payload_digest")
    if not _sha256_hex(supplied_payload_digest):
        p.append("SIGNED_RECORD_PAYLOAD_DIGEST_INVALID")
    else:
        try:
            payload_digest_ok = canonical_sha256(record.get("payload")) == supplied_payload_digest
        except CanonicalizationError:
            p.append("SIGNED_RECORD_PAYLOAD_CANONICALIZATION_FAILED")
        else:
            if not payload_digest_ok:
                p.append("SIGNED_RECORD_PAYLOAD_DIGEST_MISMATCH")

    issued_sequence = record.get("issued_registry_sequence")
    if not isinstance(issued_sequence, int) or issued_sequence < 1:
        p.append("SIGNED_RECORD_ISSUED_REGISTRY_SEQUENCE_INVALID")

    key: Mapping[str, Any] | None = None
    authority_registry_ok = False
    current = chain.current if chain.valid else None
    if current is not None:
        current_sequence = current.get("sequence")
        current_generation = current.get("generation_id")
        if current_generation != expected_generation_id:
            p.append("SIGNED_RECORD_EXPECTED_GENERATION_NOT_CURRENT")
        if record.get("generation_id") != current_generation:
            p.append("SIGNED_RECORD_GENERATION_NOT_CURRENT")
        if not isinstance(current_sequence, int):
            p.append("SIGNED_RECORD_CURRENT_REGISTRY_SEQUENCE_INVALID")
        elif issued_sequence != current_sequence:
            p.append("SIGNED_RECORD_NOT_ISSUED_UNDER_CURRENT_REGISTRY")

        issuance_snapshot = chain.snapshots_by_sequence.get(issued_sequence) if isinstance(issued_sequence, int) else None
        if issuance_snapshot is None:
            p.append("SIGNED_RECORD_ISSUANCE_REGISTRY_SNAPSHOT_NOT_FOUND")
        else:
            if issuance_snapshot.get("generation_id") != record.get("generation_id"):
                p.append("SIGNED_RECORD_ISSUANCE_GENERATION_MISMATCH")
            key = _snapshot_key_index(issuance_snapshot).get(str(record.get("key_id")))
            if key is None:
                p.append("SIGNED_RECORD_KEY_NOT_IN_ISSUANCE_REGISTRY")

        if key is not None:
            authority_problems_before = len(p)
            if key.get("issuer_id") != record.get("issuer_id"):
                p.append("SIGNED_RECORD_ISSUER_KEY_BINDING_MISMATCH")
            if key.get("algorithm") != "ED25519":
                p.append("SIGNED_RECORD_KEY_ALGORITHM_UNSUPPORTED")
            roles = key.get("roles")
            if not isinstance(roles, list) or required_role not in roles:
                p.append("SIGNED_RECORD_ISSUER_ROLE_NOT_AUTHORIZED")
            domain = key.get("control_domain_id")
            if domain in forbidden_control_domain_ids:
                p.append("SIGNED_RECORD_ISSUER_FORBIDDEN_CONTROL_DOMAIN")
            if domain in bootstrap_trust.candidate_control_domain_ids:
                p.append("SIGNED_RECORD_ISSUER_CANDIDATE_CONTROLLED_DOMAIN")
            if key.get("valid_from_registry_sequence", 0) > issued_sequence:
                p.append("SIGNED_RECORD_KEY_NOT_YET_VALID")
            if key.get("state") != "ACTIVE":
                p.append("SIGNED_RECORD_KEY_NOT_CURRENTLY_ACTIVE")
            authority_registry_ok = len(p) == authority_problems_before

    signature_ok = False
    if _strict_b64decode(record.get("signature_b64"), ED25519_SIGNATURE_BYTES) is None:
        p.append("SIGNED_RECORD_SIGNATURE_ENCODING_INVALID")
    elif key is not None:
        try:
            message = signed_record_signature_message(record)
        except CanonicalizationError:
            p.append("SIGNED_RECORD_CANONICALIZATION_FAILED")
        else:
            signature_ok = _verify_ed25519(
                str(key.get("public_key_b64", "")), str(record.get("signature_b64", "")), message
            )
            if not signature_ok:
                p.append("SIGNED_RECORD_SIGNATURE_INVALID")

    valid = not p
    out = _base_result(
        valid, p,
        "SIGNED_GOVERNANCE_RECORD_AUTHENTICATED_UNDER_CURRENT_REGISTRY",
        "SIGNED_GOVERNANCE_RECORD_INVALID",
    )
    out["content_integrity_verified"] = payload_digest_ok
    out["issuer_signature_verified"] = signature_ok
    out["authority_registry_verified"] = authority_registry_ok and chain.valid
    out["trust_anchor_origin"] = "OUT_OF_BAND_PINNED_CONFIG_REQUIRED"
    out["trust_anchor_provisioning_proven"] = False
    if key is not None:
        out["issuer_control_domain_id"] = key.get("control_domain_id")
    return out


def verify_signed_governance_record_json(
    raw_record: bytes | str,
    *,
    registry_chain_json: Sequence[bytes | str],
    bootstrap_trust: PinnedBootstrapTrustSet,
    expected_candidate_id: str,
    expected_generation_id: str,
    expected_record_type: str,
    required_role: str,
    expected_snapshot_id: str | None = None,
    forbidden_control_domain_ids: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    try:
        record = load_strict_json(raw_record)
        registry_chain = [load_strict_json(raw) for raw in registry_chain_json]
    except CanonicalizationError as exc:
        return _base_result(False, [f"STRICT_JSON_INGRESS:{exc}"], "UNREACHABLE", "SIGNED_GOVERNANCE_RECORD_INVALID")
    if not isinstance(record, Mapping) or not all(isinstance(x, Mapping) for x in registry_chain):
        return _base_result(False, ["STRICT_JSON_SIGNED_RECORD_OR_REGISTRY_MUST_BE_OBJECT"], "UNREACHABLE", "SIGNED_GOVERNANCE_RECORD_INVALID")
    return verify_signed_governance_record(
        record,
        registry_chain=registry_chain,
        bootstrap_trust=bootstrap_trust,
        expected_candidate_id=expected_candidate_id,
        expected_generation_id=expected_generation_id,
        expected_record_type=expected_record_type,
        required_role=required_role,
        expected_snapshot_id=expected_snapshot_id,
        forbidden_control_domain_ids=forbidden_control_domain_ids,
    )
