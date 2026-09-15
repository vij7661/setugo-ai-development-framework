"""V16 Slice 2 repaired independence wrapper.

Construction-stage only. This module binds the exact Slice 2 structural graph to a
bootstrap-threshold-authenticated validation profile / validator bundle and requires
binding signers themselves to be graph-represented, non-candidate-controlled, and
pairwise independent. Generic promotion and authority remain fail-closed while
real-world completeness and independent runtime measurement are unproven.
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
import binascii
import hashlib
from pathlib import Path
from typing import Any, Mapping, Sequence
import unicodedata

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

import review_safe_evidence_v16_trust as base
import review_safe_evidence_v16_independence as core

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
IMPLEMENTATION_QUALIFICATION = "NOT_CLAIMED"
RUNTIME_QUALIFICATION = "NOT_CLAIMED"
SLICE2_BINDING_PROFILE_VERSION = 4
SLICE2_BINDING_SIGNATURE_DOMAIN = "RSE-V16:SLICE2-GRAPH-VALIDATOR-BINDING-ROOT:"
EDGE_SEMANTICS_ID = "PARENT_IDS_ARE_LOAD_BEARING_CONTROL_ANCESTORS_V1"
INDEPENDENCE_RULE_ID = "ANCESTOR_CLOSURE_INTERSECTION_BLOCKS_INDEPENDENCE_V1"
CANDIDATE_CONTROL_RULE_ID = "SUBJECT_ANCESTRY_INTERSECTS_CANDIDATE_ANCESTRY_UNION_V1"
HISTORY_RULE_ID = "DOMAINS_PARENTS_CANDIDATE_MEMBERSHIP_ADDITIVE_WITHIN_EPOCH_V1"
GLOBAL_BLOCKING_RULE_ID = "REAL_WORLD_COMPLETENESS_UNPROVEN_ALWAYS_BLOCKS_GLOBAL_PROMOTION_V1"
GENERATION_RULE_ID = "REGISTRY_AND_GRAPH_HEADS_MUST_MATCH_EXPECTED_GOVERNANCE_GENERATION_V1"
ROLE_RULE_ID = "RECORD_TYPE_DERIVES_REQUIRED_ROLE_FROM_SLICE1_POLICY_V1"
ROOT_QUORUM_RULE_ID = "BOOTSTRAP_ROOTS_GRAPH_REPRESENTED_NONCANDIDATE_PAIRWISE_INDEPENDENT_V1"
REGISTRY_QUORUM_RULE_ID = "REGISTRY_BOOTSTRAP_QUORUM_REQUALIFIED_THROUGH_CURRENT_ADDITIVE_GRAPH_V1"
BINDING_ROOT_QUORUM_RULE_ID = "BINDING_ROOTS_GRAPH_REPRESENTED_NONCANDIDATE_PAIRWISE_INDEPENDENT_V1"
OWNED_SNAPSHOT_RULE_ID = "ONE_FAIL_CLOSED_OWNED_INPUT_SNAPSHOT_PER_PUBLIC_BOUND_OPERATION_V1"

BINDING_CERTIFICATE_FIELDS = frozenset({
    "schema_version", "object_type", "candidate_id", "graph_id", "graph_sequence",
    "graph_generation_id", "graph_digest", "trust_set_id", "trust_set_digest",
    "validation_profile_digest", "validator_bundle_digest", "binding_digest",
    "bootstrap_signatures",
})
BINDING_SIGNATURE_FIELDS = frozenset({"root_id", "key_id", "algorithm", "signature_b64"})


@dataclass(frozen=True)
class PinnedSlice2BindingHead:
    anchor_id: str
    graph_head: core.PinnedControlDomainGraphHead
    binding_digest: str
    validation_profile_digest: str
    validator_bundle_digest: str


def _result(valid: bool, problems: list[str], ok: str, bad: str) -> dict[str, Any]:
    return {
        "state": ok if valid else bad,
        "valid": valid,
        "qualified": False,
        "implementation_qualification": IMPLEMENTATION_QUALIFICATION,
        "runtime_qualification": RUNTIME_QUALIFICATION,
        "authority_effect": AUTHORITY_EFFECT,
        "problems": sorted(set(problems)),
    }


def _sha(value: Any) -> bool:
    return isinstance(value, str) and bool(base.SHA256_RE.fullmatch(value))


def _canonical_id(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and not any(0xD800 <= ord(ch) <= 0xDFFF for ch in value)
        and unicodedata.normalize("NFC", value) == value
    )


def _plain(value: Any, path: str = "$") -> Any:
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
            out[key] = _plain(item, f"{path}.{key}")
        return out
    if type(value) is list:
        return [_plain(v, f"{path}[{i}]") for i, v in enumerate(list(value))]
    if type(value) is tuple:
        return [_plain(v, f"{path}[{i}]") for i, v in enumerate(tuple(value))]
    raise base.CanonicalizationError(f"NON_PLAIN_JSON_CONTAINER:{path}:{type(value).__name__}")


def _snapshot_chain(chain: Sequence[Mapping[str, Any]], label: str) -> list[dict[str, Any]]:
    if type(chain) not in {list, tuple}:
        raise base.CanonicalizationError(f"{label}_CONTAINER_MUST_BE_LIST_OR_TUPLE")
    source_rows = list(chain)
    rows: list[dict[str, Any]] = []
    for i, row in enumerate(source_rows):
        snap = _plain(row, f"${label}[{i}]")
        if type(snap) is not dict:
            raise base.CanonicalizationError(f"{label}_ROW_MUST_BE_OBJECT:{i}")
        rows.append(snap)
    return rows


def _b64(value: Any, size: int) -> bytes | None:
    if not isinstance(value, str):
        return None
    try:
        raw = base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, ValueError, binascii.Error):
        return None
    return raw if len(raw) == size else None


def _verify_ed25519(public_key_b64: str, signature_b64: str, message: bytes) -> bool:
    pub = _b64(public_key_b64, base.ED25519_PUBLIC_KEY_BYTES)
    sig = _b64(signature_b64, base.ED25519_SIGNATURE_BYTES)
    if pub is None or sig is None:
        return False
    try:
        Ed25519PublicKey.from_public_bytes(pub).verify(sig, message)
        return True
    except (InvalidSignature, ValueError):
        return False


def _source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slice2_validation_profile_material() -> dict[str, Any]:
    return {
        "slice2_binding_profile_version": SLICE2_BINDING_PROFILE_VERSION,
        "base_validation_profile_digest": base.validation_profile_digest(),
        "graph_fields": sorted(core.GRAPH_FIELDS),
        "domain_fields": sorted(core.DOMAIN_FIELDS),
        "graph_signature_fields": sorted(core.SIGNATURE_FIELDS),
        "binding_certificate_fields": sorted(BINDING_CERTIFICATE_FIELDS),
        "binding_signature_fields": sorted(BINDING_SIGNATURE_FIELDS),
        "graph_signature_domain": core.GRAPH_SIGNATURE_DOMAIN,
        "slice2_binding_signature_domain": SLICE2_BINDING_SIGNATURE_DOMAIN,
        "edge_semantics_id": EDGE_SEMANTICS_ID,
        "independence_rule_id": INDEPENDENCE_RULE_ID,
        "candidate_control_rule_id": CANDIDATE_CONTROL_RULE_ID,
        "history_rule_id": HISTORY_RULE_ID,
        "global_blocking_rule_id": GLOBAL_BLOCKING_RULE_ID,
        "generation_rule_id": GENERATION_RULE_ID,
        "role_rule_id": ROLE_RULE_ID,
        "root_quorum_rule_id": ROOT_QUORUM_RULE_ID,
        "registry_quorum_rule_id": REGISTRY_QUORUM_RULE_ID,
        "binding_root_quorum_rule_id": BINDING_ROOT_QUORUM_RULE_ID,
        "owned_snapshot_rule_id": OWNED_SNAPSHOT_RULE_ID,
    }


def slice2_validation_profile_digest() -> str:
    return base.canonical_sha256(slice2_validation_profile_material())


def slice2_validator_bundle_material() -> dict[str, Any]:
    paths = [Path(base.__file__).resolve(), Path(core.__file__).resolve(), Path(__file__).resolve()]
    if any(path.suffix != ".py" for path in paths):
        raise base.CanonicalizationError("SLICE2_VALIDATOR_SOURCE_PATH_MUST_BE_PY")
    return {
        "bundle_version": 4,
        "base_validator": {"name": paths[0].name, "sha256": _source_sha256(paths[0])},
        "slice2_structural_core": {"name": paths[1].name, "sha256": _source_sha256(paths[1])},
        "slice2_binding_wrapper": {"name": paths[2].name, "sha256": _source_sha256(paths[2])},
        "validation_profile_digest": slice2_validation_profile_digest(),
    }


def slice2_validator_bundle_digest() -> str:
    return base.canonical_sha256(slice2_validator_bundle_material())


def _binding_material(record: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in {"binding_digest", "bootstrap_signatures"}}


def graph_validator_binding_digest(record: Mapping[str, Any]) -> str:
    return base.canonical_sha256(_binding_material(record))


def graph_validator_binding_signature_message(
    binding_digest: str, *, trust_set_digest: str,
    root_id: str, key_id: str, control_domain_id: str,
) -> bytes:
    if not _sha(binding_digest) or not _sha(trust_set_digest):
        raise ValueError("SLICE2_BINDING_DIGEST_INVALID")
    return SLICE2_BINDING_SIGNATURE_DOMAIN.encode("ascii") + base.canonical_bytes({
        "binding_digest": binding_digest,
        "trust_set_digest": trust_set_digest,
        "root_id": root_id,
        "key_id": key_id,
        "control_domain_id": control_domain_id,
    })


def _verify_binding_signatures(
    certificate: Mapping[str, Any], trust: base.PinnedBootstrapTrustSet,
) -> tuple[list[str], tuple[str, ...]]:
    p: list[str] = []
    digest = certificate.get("binding_digest")
    if not _sha(digest):
        return ["SLICE2_BINDING_SIGNATURE_NO_DIGEST"], ()
    roots = {(r.root_id, r.key_id): r for r in trust.roots}
    seen: set[tuple[str, str]] = set()
    domains: set[str] = set()
    signatures = certificate.get("bootstrap_signatures")
    if type(signatures) is not list or not signatures:
        return ["SLICE2_BINDING_SIGNATURES_REQUIRED"], ()
    for i, sig in enumerate(signatures):
        if type(sig) is not dict or set(sig.keys()) != BINDING_SIGNATURE_FIELDS:
            p.append(f"SLICE2_BINDING_SIGNATURE_MALFORMED:{i}")
            continue
        pair = (sig.get("root_id"), sig.get("key_id"))
        if pair in seen:
            p.append(f"SLICE2_BINDING_SIGNER_DUPLICATE:{i}")
            continue
        seen.add(pair)  # type: ignore[arg-type]
        root = roots.get(pair)  # type: ignore[arg-type]
        if root is None:
            p.append(f"SLICE2_BINDING_SIGNER_UNKNOWN:{i}")
            continue
        try:
            message = graph_validator_binding_signature_message(
                str(digest), trust_set_digest=trust.trust_set_digest,
                root_id=root.root_id, key_id=root.key_id, control_domain_id=root.control_domain_id,
            )
        except (ValueError, base.CanonicalizationError):
            p.append(f"SLICE2_BINDING_SIGNATURE_MESSAGE_INVALID:{i}")
            continue
        if sig.get("algorithm") != "ED25519" or not _verify_ed25519(
            root.public_key_b64, str(sig.get("signature_b64", "")), message,
        ):
            p.append(f"SLICE2_BINDING_SIGNATURE_INVALID:{i}")
            continue
        domains.add(root.control_domain_id)
    if len(domains) < trust.threshold_control_domains:
        p.append("SLICE2_BINDING_BOOTSTRAP_THRESHOLD_NOT_MET")
    return p, tuple(sorted(domains))


def _ancestor_closure(domain_id: str, domains: Mapping[str, tuple[str, ...]]) -> frozenset[str]:
    seen: set[str] = set()
    stack = [domain_id]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(domains.get(node, ()))
    return frozenset(seen)


def _qualify_binding_signers(
    signer_domains: Sequence[str], owned_graph_chain: Sequence[Mapping[str, Any]], threshold: int,
) -> tuple[list[str], tuple[str, ...]]:
    p: list[str] = []
    if type(owned_graph_chain) not in {list, tuple} or not owned_graph_chain:
        return ["SLICE2_BINDING_GRAPH_REQUIRED_FOR_SIGNER_QUALIFICATION"], ()
    current = owned_graph_chain[-1]
    if type(current) is not dict or type(current.get("domains")) is not list:
        return ["SLICE2_BINDING_GRAPH_QUALIFICATION_STATE_INVALID"], ()
    domains: dict[str, tuple[str, ...]] = {}
    for row in current["domains"]:
        if type(row) is dict and isinstance(row.get("control_domain_id"), str) and type(row.get("parent_control_domain_ids")) is list:
            domains[row["control_domain_id"]] = tuple(row["parent_control_domain_ids"])
    candidate_ids = current.get("candidate_domain_ids")
    if type(candidate_ids) is not list:
        return ["SLICE2_BINDING_GRAPH_CANDIDATE_DOMAINS_INVALID"], ()
    candidate_ancestors: set[str] = set()
    for candidate in candidate_ids:
        if isinstance(candidate, str) and candidate in domains:
            candidate_ancestors.update(_ancestor_closure(candidate, domains))
    eligible: list[str] = []
    for domain in sorted(set(signer_domains)):
        if domain not in domains:
            p.append(f"SLICE2_BINDING_SIGNER_DOMAIN_NOT_IN_GRAPH:{domain}")
            continue
        ancestry = _ancestor_closure(domain, domains)
        if ancestry & candidate_ancestors:
            p.append(f"SLICE2_BINDING_SIGNER_CANDIDATE_CONTROLLED:{domain}")
            continue
        eligible.append(domain)
    conflicts: list[str] = []
    for i, left in enumerate(eligible):
        left_anc = _ancestor_closure(left, domains)
        for right in eligible[i + 1:]:
            shared = left_anc & _ancestor_closure(right, domains)
            if shared:
                conflicts.append(f"{left}|{right}|{','.join(sorted(shared))}")
    if conflicts:
        p.append("SLICE2_BINDING_SIGNER_INDEPENDENCE_NOT_MET:" + ";".join(sorted(conflicts)))
    if len(eligible) < threshold or conflicts:
        p.append("SLICE2_BINDING_INDEPENDENT_NONCANDIDATE_THRESHOLD_NOT_MET")
    if p:
        return p, ()
    return p, tuple(sorted(eligible))


def validate_graph_validator_binding_certificate(
    certificate: Mapping[str, Any], *, graph_chain: Sequence[Mapping[str, Any]],
    bootstrap_trust: base.PinnedBootstrapTrustSet,
    expected_graph_head: core.PinnedControlDomainGraphHead,
    pinned_binding_head: PinnedSlice2BindingHead, expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        cert = _plain(certificate, "$slice2_binding_certificate")
        owned_graph = _snapshot_chain(graph_chain, "slice2_graph_chain")
        if type(cert) is not dict:
            raise base.CanonicalizationError("SLICE2_BINDING_CERTIFICATE_MUST_BE_OBJECT")
        profile = slice2_validation_profile_digest()
        bundle = slice2_validator_bundle_digest()
    except (base.CanonicalizationError, OSError) as exc:
        out = _result(False, [f"SLICE2_BINDING_INPUT:{exc}"], "UNREACHABLE", "SLICE2_BINDING_CERTIFICATE_INVALID")
        out.update({"construction_binding_valid": False, "promotion_blocked": True, "bootstrap_authenticated_control_domains": [], "binding_quorum_graph_qualified": False, "graph_completeness_real_world_proven": False, "source_measurement_independently_proven": False})
        return out

    p: list[str] = []
    trust_result = base.validate_bootstrap_trust_set(bootstrap_trust)
    if not trust_result["valid"]:
        p.extend(f"SLICE2_BINDING_TRUST:{x}" for x in trust_result["problems"])
    graph_result = core.validate_control_domain_graph_chain(
        owned_graph, bootstrap_trust=bootstrap_trust,
        expected_current_head=expected_graph_head, expected_candidate_id=expected_candidate_id,
    )
    if not graph_result["valid"]:
        p.extend(f"SLICE2_BINDING_GRAPH:{x}" for x in graph_result["problems"])

    if set(cert.keys()) != BINDING_CERTIFICATE_FIELDS:
        p.append("SLICE2_BINDING_CERTIFICATE_FIELDS_NOT_EXACT")
    if type(cert.get("schema_version")) is not int or cert.get("schema_version") != 1:
        p.append("SLICE2_BINDING_CERTIFICATE_SCHEMA_INVALID")
    if cert.get("object_type") != "SLICE2_GRAPH_VALIDATOR_BINDING":
        p.append("SLICE2_BINDING_CERTIFICATE_OBJECT_TYPE_INVALID")
    for value, code in (
        (expected_candidate_id, "SLICE2_EXPECTED_CANDIDATE_ID"),
        (cert.get("candidate_id"), "SLICE2_BINDING_CANDIDATE_ID"),
        (cert.get("graph_id"), "SLICE2_BINDING_GRAPH_ID"),
        (cert.get("graph_generation_id"), "SLICE2_BINDING_GRAPH_GENERATION_ID"),
        (cert.get("trust_set_id"), "SLICE2_BINDING_TRUST_SET_ID"),
    ):
        if not _canonical_id(value):
            p.append(f"{code}_INVALID")
    expected_pairs = {
        "candidate_id": expected_candidate_id,
        "graph_id": expected_graph_head.graph_id,
        "graph_sequence": expected_graph_head.sequence,
        "graph_generation_id": expected_graph_head.generation_id,
        "graph_digest": expected_graph_head.graph_digest,
        "trust_set_id": bootstrap_trust.trust_set_id,
        "trust_set_digest": bootstrap_trust.trust_set_digest,
        "validation_profile_digest": profile,
        "validator_bundle_digest": bundle,
    }
    for key, expected in expected_pairs.items():
        if cert.get(key) != expected or type(cert.get(key)) is not type(expected):
            p.append(f"SLICE2_BINDING_CERTIFICATE_{key.upper()}_MISMATCH")
    supplied_digest = cert.get("binding_digest")
    if not _sha(supplied_digest):
        p.append("SLICE2_BINDING_CERTIFICATE_DIGEST_INVALID")
    else:
        try:
            if supplied_digest != graph_validator_binding_digest(cert):
                p.append("SLICE2_BINDING_CERTIFICATE_DIGEST_MISMATCH")
        except base.CanonicalizationError:
            p.append("SLICE2_BINDING_CERTIFICATE_CANONICALIZATION_FAILED")
    if type(pinned_binding_head) is not PinnedSlice2BindingHead:
        p.append("SLICE2_PINNED_BINDING_HEAD_TYPE_INVALID")
    else:
        if not _canonical_id(pinned_binding_head.anchor_id):
            p.append("SLICE2_PINNED_BINDING_HEAD_ANCHOR_INVALID")
        if pinned_binding_head.graph_head != expected_graph_head:
            p.append("SLICE2_PINNED_BINDING_HEAD_GRAPH_HEAD_MISMATCH")
        if pinned_binding_head.binding_digest != supplied_digest:
            p.append("SLICE2_PINNED_BINDING_HEAD_DIGEST_MISMATCH")
        if pinned_binding_head.validation_profile_digest != profile:
            p.append("SLICE2_PINNED_BINDING_HEAD_PROFILE_MISMATCH")
        if pinned_binding_head.validator_bundle_digest != bundle:
            p.append("SLICE2_PINNED_BINDING_HEAD_BUNDLE_MISMATCH")

    sig_p, crypto_domains = _verify_binding_signatures(cert, bootstrap_trust)
    p.extend(sig_p)
    qualified_domains: tuple[str, ...] = ()
    if graph_result["valid"]:
        quorum_p, qualified_domains = _qualify_binding_signers(
            crypto_domains, owned_graph, bootstrap_trust.threshold_control_domains,
        )
        p.extend(quorum_p)
    else:
        p.append("SLICE2_BINDING_GRAPH_NOT_VALID_FOR_SIGNER_QUALIFICATION")
    valid = not p
    out = _result(valid, p, "SLICE2_GRAPH_VALIDATOR_BINDING_AUTHENTICATED", "SLICE2_BINDING_CERTIFICATE_INVALID")
    out.update({
        "construction_binding_valid": valid,
        "promotion_blocked": True,
        "validation_profile_digest": profile,
        "validator_bundle_digest": bundle,
        "bootstrap_authenticated_control_domains": list(qualified_domains) if valid else [],
        "binding_quorum_graph_qualified": valid,
        "graph_completeness_real_world_proven": False,
        "source_measurement_independently_proven": False,
    })
    return out


def _snapshot_failure(exc: base.CanonicalizationError, state: str) -> dict[str, Any]:
    out = _result(False, [f"SLICE2_BOUND_INPUT:{exc}"], "UNREACHABLE", state)
    out.update({"promotion_blocked": True})
    return out


def validate_bound_control_domain_graph_chain(
    graph_chain: Sequence[Mapping[str, Any]], *, binding_certificate: Mapping[str, Any],
    bootstrap_trust: base.PinnedBootstrapTrustSet,
    expected_graph_head: core.PinnedControlDomainGraphHead,
    pinned_binding_head: PinnedSlice2BindingHead, expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        owned_graph = _snapshot_chain(graph_chain, "slice2_bound_graph_chain")
    except base.CanonicalizationError as exc:
        out = _snapshot_failure(exc, "BOUND_CONTROL_DOMAIN_GRAPH_INVALID")
        out.update({"construction_graph_accepted": False, "graph_completeness_real_world_proven": False, "source_measurement_independently_proven": False})
        return out
    binding = validate_graph_validator_binding_certificate(
        binding_certificate, graph_chain=owned_graph, bootstrap_trust=bootstrap_trust,
        expected_graph_head=expected_graph_head, pinned_binding_head=pinned_binding_head,
        expected_candidate_id=expected_candidate_id,
    )
    out = _result(binding["valid"], list(binding["problems"]), "BOUND_CONTROL_DOMAIN_GRAPH_STRUCTURALLY_VALID_NONAUTHORITATIVE", "BOUND_CONTROL_DOMAIN_GRAPH_INVALID")
    out.update({"construction_graph_accepted": binding["valid"], "promotion_blocked": True, "graph_completeness_real_world_proven": False, "source_measurement_independently_proven": False})
    return out


def assess_bound_domain_independence(
    subject_a_control_domain_id: str, subject_b_control_domain_id: str, *,
    graph_chain: Sequence[Mapping[str, Any]], binding_certificate: Mapping[str, Any],
    bootstrap_trust: base.PinnedBootstrapTrustSet,
    expected_graph_head: core.PinnedControlDomainGraphHead,
    pinned_binding_head: PinnedSlice2BindingHead, expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        owned_graph = _snapshot_chain(graph_chain, "slice2_bound_graph_chain")
    except base.CanonicalizationError as exc:
        out = _snapshot_failure(exc, "BOUND_INDEPENDENCE_UNPROVEN")
        out.update({"independence_result": "INDEPENDENCE_UNPROVEN", "construction_independence_satisfied": False, "independence_real_world_proven": False})
        return out
    binding = validate_graph_validator_binding_certificate(binding_certificate, graph_chain=owned_graph, bootstrap_trust=bootstrap_trust, expected_graph_head=expected_graph_head, pinned_binding_head=pinned_binding_head, expected_candidate_id=expected_candidate_id)
    core_result = core.assess_domain_independence(subject_a_control_domain_id, subject_b_control_domain_id, graph_chain=owned_graph, bootstrap_trust=bootstrap_trust, expected_current_head=expected_graph_head, expected_candidate_id=expected_candidate_id)
    p = list(binding["problems"])
    if not core_result["valid"]:
        p.extend(f"SLICE2_CORE:{x}" for x in core_result["problems"])
    valid = binding["valid"] and core_result["valid"] and not p
    out = _result(valid, p, core_result["independence_result"], "BOUND_INDEPENDENCE_UNPROVEN")
    out.update({"independence_result": core_result["independence_result"], "shared_load_bearing_ancestors": core_result.get("shared_load_bearing_ancestors", []), "construction_independence_satisfied": binding["valid"] and core_result.get("construction_independence_satisfied") is True, "promotion_blocked": True, "independence_real_world_proven": False, "graph_completeness_real_world_proven": False})
    return out


def assess_bound_candidate_control(
    subject_control_domain_id: str, *, graph_chain: Sequence[Mapping[str, Any]],
    binding_certificate: Mapping[str, Any], bootstrap_trust: base.PinnedBootstrapTrustSet,
    expected_graph_head: core.PinnedControlDomainGraphHead,
    pinned_binding_head: PinnedSlice2BindingHead, expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        owned_graph = _snapshot_chain(graph_chain, "slice2_bound_graph_chain")
    except base.CanonicalizationError as exc:
        out = _snapshot_failure(exc, "BOUND_CANDIDATE_CONTROL_UNPROVEN")
        out.update({"candidate_control_result": "CANDIDATE_CONTROL_UNPROVEN", "construction_candidate_control_clear": False, "control_real_world_completeness_proven": False})
        return out
    binding = validate_graph_validator_binding_certificate(binding_certificate, graph_chain=owned_graph, bootstrap_trust=bootstrap_trust, expected_graph_head=expected_graph_head, pinned_binding_head=pinned_binding_head, expected_candidate_id=expected_candidate_id)
    core_result = core.assess_candidate_control(subject_control_domain_id, graph_chain=owned_graph, bootstrap_trust=bootstrap_trust, expected_current_head=expected_graph_head, expected_candidate_id=expected_candidate_id)
    p = list(binding["problems"])
    if not core_result["valid"]:
        p.extend(f"SLICE2_CORE:{x}" for x in core_result["problems"])
    valid = binding["valid"] and core_result["valid"] and not p
    out = _result(valid, p, core_result["candidate_control_result"], "BOUND_CANDIDATE_CONTROL_UNPROVEN")
    out.update({"candidate_control_result": core_result["candidate_control_result"], "candidate_controlled": core_result.get("candidate_controlled"), "shared_candidate_ancestors": core_result.get("shared_candidate_ancestors", []), "construction_candidate_control_clear": binding["valid"] and core_result.get("construction_candidate_control_clear") is True, "promotion_blocked": True, "control_real_world_completeness_proven": False})
    return out


def _derive_required_role(expected_record_type: str) -> tuple[str | None, list[str]]:
    if not _canonical_id(expected_record_type):
        return None, ["SLICE2_EXPECTED_RECORD_TYPE_INVALID"]
    role = dict(base.RECORD_TYPE_REQUIRED_ROLE).get(expected_record_type)
    return (role, []) if role is not None else (None, ["SLICE2_EXPECTED_RECORD_TYPE_UNKNOWN"])


def _generation_problems(expected_generation: str, registry_head: base.PinnedRegistryHead, graph_head: core.PinnedControlDomainGraphHead) -> list[str]:
    p: list[str] = []
    if not _canonical_id(expected_generation):
        return ["SLICE2_EXPECTED_GOVERNANCE_GENERATION_INVALID"]
    if registry_head.generation_id != expected_generation:
        p.append("SLICE2_REGISTRY_HEAD_GENERATION_MISMATCH")
    if graph_head.generation_id != expected_generation:
        p.append("SLICE2_GRAPH_HEAD_GENERATION_MISMATCH")
    return p


def resolve_bound_registry_key_authority(
    key_id: str, expected_record_type: str, *, expected_governance_generation_id: str,
    registry_chain: Sequence[Mapping[str, Any]], expected_registry_head: base.PinnedRegistryHead,
    graph_chain: Sequence[Mapping[str, Any]], expected_graph_head: core.PinnedControlDomainGraphHead,
    binding_certificate: Mapping[str, Any], pinned_binding_head: PinnedSlice2BindingHead,
    bootstrap_trust: base.PinnedBootstrapTrustSet, expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        owned_graph = _snapshot_chain(graph_chain, "slice2_bound_graph_chain")
        owned_registry = _snapshot_chain(registry_chain, "slice2_bound_registry_chain")
    except base.CanonicalizationError as exc:
        out = _snapshot_failure(exc, "BOUND_REGISTRY_AUTHORITY_UNPROVEN")
        out.update({"authority_structurally_admissible_within_authenticated_graph": False, "authority_admissible": False})
        return out
    role, p = _derive_required_role(expected_record_type)
    p.extend(_generation_problems(expected_governance_generation_id, expected_registry_head, expected_graph_head))
    binding = validate_graph_validator_binding_certificate(binding_certificate, graph_chain=owned_graph, bootstrap_trust=bootstrap_trust, expected_graph_head=expected_graph_head, pinned_binding_head=pinned_binding_head, expected_candidate_id=expected_candidate_id)
    p.extend(f"SLICE2_BINDING:{x}" for x in binding["problems"])
    core_result: dict[str, Any] | None = None
    if role is not None:
        core_result = core.resolve_registry_key_authority(key_id, role, registry_chain=owned_registry, expected_registry_head=expected_registry_head, graph_chain=owned_graph, expected_graph_head=expected_graph_head, bootstrap_trust=bootstrap_trust, expected_candidate_id=expected_candidate_id)
        if core_result.get("authority_structurally_admissible_within_authenticated_graph") is not True:
            p.extend(f"SLICE2_CORE:{x}" for x in core_result["problems"])
    structural = not p and binding["valid"] and core_result is not None and core_result.get("authority_structurally_admissible_within_authenticated_graph") is True
    out = _result(structural, p, "REGISTRY_AUTHORITY_STRUCTURALLY_ADMISSIBLE_WITHIN_AUTHENTICATED_BOUND_GRAPH", "BOUND_REGISTRY_AUTHORITY_UNPROVEN")
    out.update({"authority_structurally_admissible_within_authenticated_graph": structural, "authority_admissible": False, "promotion_blocked": True, "expected_record_type": expected_record_type, "required_role": role, "expected_governance_generation_id": expected_governance_generation_id, "key_id": key_id, "issuer_id": core_result.get("issuer_id") if core_result else None, "control_domain_id": core_result.get("control_domain_id") if core_result else None, "candidate_controlled": core_result.get("candidate_controlled") if core_result else None, "control_real_world_completeness_proven": False})
    return out


def assess_bound_registry_key_independence(
    key_id_a: str, expected_record_type_a: str, key_id_b: str, expected_record_type_b: str, *,
    expected_governance_generation_id: str,
    registry_chain: Sequence[Mapping[str, Any]], expected_registry_head: base.PinnedRegistryHead,
    graph_chain: Sequence[Mapping[str, Any]], expected_graph_head: core.PinnedControlDomainGraphHead,
    binding_certificate: Mapping[str, Any], pinned_binding_head: PinnedSlice2BindingHead,
    bootstrap_trust: base.PinnedBootstrapTrustSet, expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        owned_graph = _snapshot_chain(graph_chain, "slice2_bound_graph_chain")
        owned_registry = _snapshot_chain(registry_chain, "slice2_bound_registry_chain")
    except base.CanonicalizationError as exc:
        out = _snapshot_failure(exc, "BOUND_REGISTRY_KEY_INDEPENDENCE_UNPROVEN")
        out.update({"independence_result": "INDEPENDENCE_UNPROVEN", "construction_independence_satisfied": False, "independence_real_world_proven": False, "authority_admissible": False})
        return out
    a = resolve_bound_registry_key_authority(key_id_a, expected_record_type_a, expected_governance_generation_id=expected_governance_generation_id, registry_chain=owned_registry, expected_registry_head=expected_registry_head, graph_chain=owned_graph, expected_graph_head=expected_graph_head, binding_certificate=binding_certificate, pinned_binding_head=pinned_binding_head, bootstrap_trust=bootstrap_trust, expected_candidate_id=expected_candidate_id)
    b = resolve_bound_registry_key_authority(key_id_b, expected_record_type_b, expected_governance_generation_id=expected_governance_generation_id, registry_chain=owned_registry, expected_registry_head=expected_registry_head, graph_chain=owned_graph, expected_graph_head=expected_graph_head, binding_certificate=binding_certificate, pinned_binding_head=pinned_binding_head, bootstrap_trust=bootstrap_trust, expected_candidate_id=expected_candidate_id)
    p = [f"A:{x}" for x in a["problems"]] + [f"B:{x}" for x in b["problems"]]
    result = "INDEPENDENCE_UNPROVEN"
    shared: list[str] = []
    construction = False
    if a["authority_structurally_admissible_within_authenticated_graph"] and b["authority_structurally_admissible_within_authenticated_graph"]:
        core_result = core.assess_registry_key_independence(key_id_a, a["required_role"], key_id_b, b["required_role"], registry_chain=owned_registry, expected_registry_head=expected_registry_head, graph_chain=owned_graph, expected_graph_head=expected_graph_head, bootstrap_trust=bootstrap_trust, expected_candidate_id=expected_candidate_id)
        p.extend(f"CORE:{x}" for x in core_result["problems"])
        result = core_result["independence_result"]
        shared = list(core_result.get("shared_load_bearing_ancestors", []))
        construction = core_result.get("construction_independence_satisfied") is True and not core_result["problems"]
    valid = result != "INDEPENDENCE_UNPROVEN" and not p
    out = _result(valid, p, result, "BOUND_REGISTRY_KEY_INDEPENDENCE_UNPROVEN")
    out.update({"independence_result": result, "shared_load_bearing_ancestors": shared, "construction_independence_satisfied": construction, "promotion_blocked": True, "independence_real_world_proven": False, "authority_admissible": False, "expected_governance_generation_id": expected_governance_generation_id})
    return out
