"""V16 Slice 2 authenticated control-domain ancestry and independence.

Construction-stage only. Independence is derived from a bootstrap-threshold-
authenticated graph instead of caller-supplied labels. Real-world graph completeness,
root ownership, and out-of-band head provisioning remain unproven.
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
import binascii
from typing import Any, Mapping, Sequence
import unicodedata

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

import review_safe_evidence_v16_trust as base

AUTHORITY_EFFECT = "NONE_EVIDENCE_ONLY"
GRAPH_SIGNATURE_DOMAIN = "RSE-V16:CONTROL-DOMAIN-GRAPH-ROOT:"
GRAPH_FIELDS = frozenset({
    "schema_version", "object_type", "graph_id", "candidate_id", "generation_id",
    "trust_set_id", "trust_set_digest", "sequence", "predecessor_graph_digest",
    "candidate_domain_ids", "domains", "graph_digest", "bootstrap_signatures",
})
DOMAIN_FIELDS = frozenset({"control_domain_id", "parent_control_domain_ids"})
SIGNATURE_FIELDS = frozenset({"root_id", "key_id", "algorithm", "signature_b64"})


@dataclass(frozen=True)
class PinnedControlDomainGraphHead:
    anchor_id: str
    trust_set_id: str
    trust_set_digest: str
    graph_id: str
    candidate_id: str
    sequence: int
    generation_id: str
    graph_digest: str


@dataclass(frozen=True)
class _GraphValidation:
    valid: bool
    problems: tuple[str, ...]
    current: dict[str, Any] | None
    current_domains: Mapping[str, tuple[str, ...]]
    candidate_domains: frozenset[str]
    authenticated_bootstrap_domains: tuple[str, ...]
    current_head_matched: bool


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
    return isinstance(value, str) and bool(base.SHA256_RE.fullmatch(value))


def _exact_int(value: Any, minimum: int = 0) -> bool:
    return type(value) is int and minimum <= value <= base.MAX_CANONICAL_INTEGER


def _canonical_identifier(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    if any(0xD800 <= ord(ch) <= 0xDFFF for ch in value):
        return False
    return unicodedata.normalize("NFC", value) == value


def _require_id(p: list[str], value: Any, code: str) -> None:
    if not isinstance(value, str) or not value.strip():
        p.append(f"{code}_REQUIRED")
    elif not _canonical_identifier(value):
        p.append(f"{code}_NOT_CANONICAL_NFC")


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
        return [_plain(item, f"{path}[{i}]") for i, item in enumerate(list(value))]
    if type(value) is tuple:
        return [_plain(item, f"{path}[{i}]") for i, item in enumerate(tuple(value))]
    raise base.CanonicalizationError(f"NON_PLAIN_JSON_CONTAINER:{path}:{type(value).__name__}")


def _snapshot_chain(chain: Sequence[Mapping[str, Any]], label: str) -> list[dict[str, Any]]:
    if type(chain) not in {list, tuple}:
        raise base.CanonicalizationError(f"{label}_CONTAINER_MUST_BE_LIST_OR_TUPLE")
    out: list[dict[str, Any]] = []
    for i, row in enumerate(list(chain)):
        snap = _plain(row, f"${label}[{i}]")
        if type(snap) is not dict:
            raise base.CanonicalizationError(f"{label}_ROW_MUST_BE_OBJECT:{i}")
        out.append(snap)
    return out


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


def _graph_material(record: Mapping[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in {"graph_digest", "bootstrap_signatures"}}


def control_domain_graph_digest(record: Mapping[str, Any]) -> str:
    return base.canonical_sha256(_graph_material(record))


def control_domain_graph_signature_message(
    graph_digest: str, *, trust_set_digest: str,
    root_id: str, key_id: str, control_domain_id: str,
) -> bytes:
    if not _sha(graph_digest) or not _sha(trust_set_digest):
        raise ValueError("CONTROL_DOMAIN_GRAPH_DIGEST_INVALID")
    return GRAPH_SIGNATURE_DOMAIN.encode("ascii") + base.canonical_bytes({
        "graph_digest": graph_digest,
        "trust_set_digest": trust_set_digest,
        "root_id": root_id,
        "key_id": key_id,
        "control_domain_id": control_domain_id,
    })


def _domain_map(record: Mapping[str, Any]) -> dict[str, tuple[str, ...]]:
    domains = record.get("domains")
    if type(domains) is not list:
        return {}
    out: dict[str, tuple[str, ...]] = {}
    for row in domains:
        if type(row) is dict and _canonical_identifier(row.get("control_domain_id")) and type(row.get("parent_control_domain_ids")) is list:
            out[row["control_domain_id"]] = tuple(row["parent_control_domain_ids"])
    return out


def _cycle_nodes(domains: Mapping[str, tuple[str, ...]]) -> set[str]:
    WHITE, GREY, BLACK = 0, 1, 2
    state = {node: WHITE for node in domains}
    cycle: set[str] = set()

    def visit(node: str, stack: list[str]) -> None:
        if state[node] == BLACK:
            return
        if state[node] == GREY:
            if node in stack:
                cycle.update(stack[stack.index(node):])
            cycle.add(node)
            return
        state[node] = GREY
        stack.append(node)
        for parent in domains.get(node, ()):
            if parent in domains:
                visit(parent, stack)
        stack.pop()
        state[node] = BLACK

    for node in domains:
        if state[node] == WHITE:
            visit(node, [])
    return cycle


def _validate_graph_snapshot(
    record: dict[str, Any], trust: base.PinnedBootstrapTrustSet,
    expected_candidate_id: str,
) -> tuple[list[str], dict[str, tuple[str, ...]], frozenset[str]]:
    p: list[str] = []
    if set(record.keys()) != GRAPH_FIELDS:
        p.append("CONTROL_DOMAIN_GRAPH_FIELDS_NOT_EXACT")
    if type(record.get("schema_version")) is not int or record.get("schema_version") != 1:
        p.append("CONTROL_DOMAIN_GRAPH_SCHEMA_INVALID")
    if record.get("object_type") != "CONTROL_DOMAIN_GRAPH":
        p.append("CONTROL_DOMAIN_GRAPH_OBJECT_TYPE_INVALID")
    for field, code in (
        ("graph_id", "CONTROL_DOMAIN_GRAPH_ID"),
        ("candidate_id", "CONTROL_DOMAIN_CANDIDATE_ID"),
        ("generation_id", "CONTROL_DOMAIN_GENERATION_ID"),
        ("trust_set_id", "CONTROL_DOMAIN_TRUST_SET_ID"),
    ):
        _require_id(p, record.get(field), code)
    if record.get("candidate_id") != expected_candidate_id:
        p.append("CONTROL_DOMAIN_GRAPH_CANDIDATE_MISMATCH")
    if record.get("trust_set_id") != trust.trust_set_id:
        p.append("CONTROL_DOMAIN_GRAPH_TRUST_SET_MISMATCH")
    if record.get("trust_set_digest") != trust.trust_set_digest:
        p.append("CONTROL_DOMAIN_GRAPH_TRUST_SET_DIGEST_MISMATCH")
    if not _sha(record.get("trust_set_digest")):
        p.append("CONTROL_DOMAIN_GRAPH_TRUST_SET_DIGEST_INVALID")
    seq = record.get("sequence")
    if not _exact_int(seq, 1):
        p.append("CONTROL_DOMAIN_GRAPH_SEQUENCE_INVALID")
    predecessor = record.get("predecessor_graph_digest")
    if predecessor != "GENESIS" and not _sha(predecessor):
        p.append("CONTROL_DOMAIN_GRAPH_PREDECESSOR_INVALID")

    raw_domains = record.get("domains")
    domains: dict[str, tuple[str, ...]] = {}
    if type(raw_domains) is not list or not raw_domains:
        p.append("CONTROL_DOMAIN_GRAPH_DOMAINS_REQUIRED")
        raw_domains = []
    for i, row in enumerate(raw_domains):
        if type(row) is not dict:
            p.append(f"CONTROL_DOMAIN_NODE_MALFORMED:{i}")
            continue
        if set(row.keys()) != DOMAIN_FIELDS:
            p.append(f"CONTROL_DOMAIN_NODE_FIELDS_NOT_EXACT:{i}")
        domain_id = row.get("control_domain_id")
        _require_id(p, domain_id, f"CONTROL_DOMAIN_NODE_ID:{i}")
        parents = row.get("parent_control_domain_ids")
        if type(parents) is not list:
            p.append(f"CONTROL_DOMAIN_PARENT_LIST_INVALID:{i}")
            parents = []
        canonical_parents: list[str] = []
        for j, parent in enumerate(parents):
            _require_id(p, parent, f"CONTROL_DOMAIN_PARENT_ID:{i}:{j}")
            if _canonical_identifier(parent):
                canonical_parents.append(parent)
        if len(canonical_parents) != len(set(canonical_parents)):
            p.append(f"CONTROL_DOMAIN_PARENT_DUPLICATE:{i}")
        if _canonical_identifier(domain_id):
            if domain_id in domains:
                p.append(f"CONTROL_DOMAIN_ID_DUPLICATE:{domain_id}")
            else:
                domains[domain_id] = tuple(canonical_parents)

    for domain_id, parents in domains.items():
        for parent in parents:
            if parent == domain_id:
                p.append(f"CONTROL_DOMAIN_SELF_EDGE:{domain_id}")
            elif parent not in domains:
                p.append(f"CONTROL_DOMAIN_UNKNOWN_PARENT:{domain_id}:{parent}")
    cycles = _cycle_nodes(domains)
    if cycles:
        p.append("CONTROL_DOMAIN_GRAPH_CYCLE:" + ",".join(sorted(cycles)))

    raw_candidate_domains = record.get("candidate_domain_ids")
    candidate_domains: frozenset[str] = frozenset()
    if type(raw_candidate_domains) is not list or not raw_candidate_domains:
        p.append("CONTROL_DOMAIN_CANDIDATE_DOMAINS_REQUIRED")
    else:
        candidate_list: list[str] = []
        for i, domain in enumerate(raw_candidate_domains):
            _require_id(p, domain, f"CONTROL_DOMAIN_CANDIDATE_DOMAIN:{i}")
            if _canonical_identifier(domain):
                candidate_list.append(domain)
        if len(candidate_list) != len(set(candidate_list)):
            p.append("CONTROL_DOMAIN_CANDIDATE_DOMAIN_DUPLICATE")
        candidate_domains = frozenset(candidate_list)
        for domain in candidate_domains:
            if domain not in domains:
                p.append(f"CONTROL_DOMAIN_CANDIDATE_DOMAIN_UNKNOWN:{domain}")
        missing_pinned = set(trust.candidate_control_domain_ids) - set(candidate_domains)
        if missing_pinned:
            p.append("CONTROL_DOMAIN_PINNED_CANDIDATE_DOMAIN_MISSING:" + ",".join(sorted(missing_pinned)))

    supplied = record.get("graph_digest")
    if not _sha(supplied):
        p.append("CONTROL_DOMAIN_GRAPH_DIGEST_INVALID")
    else:
        try:
            if supplied != control_domain_graph_digest(record):
                p.append("CONTROL_DOMAIN_GRAPH_DIGEST_MISMATCH")
        except base.CanonicalizationError:
            p.append("CONTROL_DOMAIN_GRAPH_CANONICALIZATION_FAILED")

    signatures = record.get("bootstrap_signatures")
    if type(signatures) is not list or not signatures:
        p.append("CONTROL_DOMAIN_GRAPH_SIGNATURES_REQUIRED")
    else:
        for i, sig in enumerate(signatures):
            if type(sig) is not dict or set(sig.keys()) != SIGNATURE_FIELDS:
                p.append(f"CONTROL_DOMAIN_GRAPH_SIGNATURE_MALFORMED:{i}")
                continue
            _require_id(p, sig.get("root_id"), f"CONTROL_DOMAIN_GRAPH_SIGNATURE_ROOT:{i}")
            _require_id(p, sig.get("key_id"), f"CONTROL_DOMAIN_GRAPH_SIGNATURE_KEY:{i}")
            if sig.get("algorithm") != "ED25519":
                p.append(f"CONTROL_DOMAIN_GRAPH_SIGNATURE_ALGORITHM_INVALID:{i}")
            if _b64(sig.get("signature_b64"), base.ED25519_SIGNATURE_BYTES) is None:
                p.append(f"CONTROL_DOMAIN_GRAPH_SIGNATURE_ENCODING_INVALID:{i}")
    return p, domains, candidate_domains


def _verify_graph_signatures(
    record: dict[str, Any], trust: base.PinnedBootstrapTrustSet,
) -> tuple[list[str], tuple[str, ...]]:
    p: list[str] = []
    digest = record.get("graph_digest")
    if not _sha(digest):
        return ["CONTROL_DOMAIN_GRAPH_SIGNATURE_NO_DIGEST"], ()
    roots = {(r.root_id, r.key_id): r for r in trust.roots}
    seen: set[tuple[str, str]] = set()
    domains: set[str] = set()
    signatures = record.get("bootstrap_signatures")
    if type(signatures) is not list:
        return ["CONTROL_DOMAIN_GRAPH_SIGNATURES_REQUIRED"], ()
    for i, sig in enumerate(signatures):
        if type(sig) is not dict:
            continue
        pair = (sig.get("root_id"), sig.get("key_id"))
        if pair in seen:
            p.append(f"CONTROL_DOMAIN_GRAPH_SIGNER_DUPLICATE:{i}")
            continue
        seen.add(pair)  # type: ignore[arg-type]
        root = roots.get(pair)  # type: ignore[arg-type]
        if root is None:
            p.append(f"CONTROL_DOMAIN_GRAPH_SIGNER_UNKNOWN:{i}")
            continue
        try:
            msg = control_domain_graph_signature_message(
                str(digest), trust_set_digest=trust.trust_set_digest,
                root_id=root.root_id, key_id=root.key_id,
                control_domain_id=root.control_domain_id,
            )
        except ValueError:
            p.append(f"CONTROL_DOMAIN_GRAPH_SIGNATURE_MESSAGE_INVALID:{i}")
            continue
        if sig.get("algorithm") != "ED25519" or not _verify_ed25519(
            root.public_key_b64, str(sig.get("signature_b64", "")), msg,
        ):
            p.append(f"CONTROL_DOMAIN_GRAPH_SIGNATURE_INVALID:{i}")
            continue
        domains.add(root.control_domain_id)
    if len(domains) < trust.threshold_control_domains:
        p.append("CONTROL_DOMAIN_GRAPH_BOOTSTRAP_THRESHOLD_NOT_MET")
    return p, tuple(sorted(domains))


def _head_problems(
    current: dict[str, Any], head: PinnedControlDomainGraphHead,
    trust: base.PinnedBootstrapTrustSet, expected_candidate_id: str,
) -> list[str]:
    p: list[str] = []
    if type(head) is not PinnedControlDomainGraphHead:
        return ["CONTROL_DOMAIN_GRAPH_HEAD_TYPE_INVALID"]
    _require_id(p, head.anchor_id, "CONTROL_DOMAIN_GRAPH_HEAD_ANCHOR")
    if head.trust_set_id != trust.trust_set_id:
        p.append("CONTROL_DOMAIN_GRAPH_HEAD_TRUST_SET_MISMATCH")
    if head.trust_set_digest != trust.trust_set_digest:
        p.append("CONTROL_DOMAIN_GRAPH_HEAD_TRUST_SET_DIGEST_MISMATCH")
    if head.candidate_id != expected_candidate_id:
        p.append("CONTROL_DOMAIN_GRAPH_HEAD_CANDIDATE_MISMATCH")
    if not _exact_int(head.sequence, 1):
        p.append("CONTROL_DOMAIN_GRAPH_HEAD_SEQUENCE_INVALID")
    if not _sha(head.graph_digest):
        p.append("CONTROL_DOMAIN_GRAPH_HEAD_DIGEST_INVALID")
    checks = {
        "graph_id": head.graph_id,
        "candidate_id": head.candidate_id,
        "sequence": head.sequence,
        "generation_id": head.generation_id,
        "graph_digest": head.graph_digest,
        "trust_set_id": head.trust_set_id,
        "trust_set_digest": head.trust_set_digest,
    }
    for key, expected in checks.items():
        if current.get(key) != expected:
            p.append(f"CONTROL_DOMAIN_GRAPH_HEAD_{key.upper()}_MISMATCH")
    return p


def _validate_graph_chain_owned(
    chain: list[dict[str, Any]], trust: base.PinnedBootstrapTrustSet,
    head: PinnedControlDomainGraphHead, expected_candidate_id: str,
) -> _GraphValidation:
    p: list[str] = []
    trust_result = base.validate_bootstrap_trust_set(trust)
    if not trust_result["valid"]:
        p.extend(f"CONTROL_DOMAIN_TRUST:{x}" for x in trust_result["problems"])
        return _GraphValidation(False, tuple(sorted(set(p))), None, {}, frozenset(), (), False)
    if not chain:
        return _GraphValidation(False, ("CONTROL_DOMAIN_GRAPH_CHAIN_REQUIRED",), None, {}, frozenset(), (), False)

    previous: dict[str, Any] | None = None
    previous_domains: dict[str, tuple[str, ...]] = {}
    previous_candidate_domains: frozenset[str] = frozenset()
    generations: set[str] = set()
    current_domains: dict[str, tuple[str, ...]] = {}
    current_candidate_domains: frozenset[str] = frozenset()
    authenticated_domains: tuple[str, ...] = ()

    for i, record in enumerate(chain):
        structural, domains, candidate_domains = _validate_graph_snapshot(record, trust, expected_candidate_id)
        p.extend(f"GRAPH[{i}]:{x}" for x in structural)
        sig_p, authenticated_domains = _verify_graph_signatures(record, trust)
        p.extend(f"GRAPH[{i}]:{x}" for x in sig_p)
        seq = record.get("sequence")
        generation = record.get("generation_id")
        if _canonical_identifier(generation):
            if generation in generations:
                p.append(f"CONTROL_DOMAIN_GRAPH_GENERATION_REUSE:{i}")
            generations.add(generation)
        if i == 0:
            if not (type(seq) is int and seq == 1):
                p.append("CONTROL_DOMAIN_GRAPH_GENESIS_SEQUENCE_MUST_BE_ONE")
            if record.get("predecessor_graph_digest") != "GENESIS":
                p.append("CONTROL_DOMAIN_GRAPH_GENESIS_PREDECESSOR_REQUIRED")
        else:
            assert previous is not None
            if not (_exact_int(previous.get("sequence"), 1) and _exact_int(seq, 1) and seq == previous["sequence"] + 1):
                p.append(f"CONTROL_DOMAIN_GRAPH_SEQUENCE_GAP:{i}")
            if record.get("predecessor_graph_digest") != previous.get("graph_digest"):
                p.append(f"CONTROL_DOMAIN_GRAPH_PREDECESSOR_MISMATCH:{i}")
            if record.get("graph_id") != previous.get("graph_id"):
                p.append(f"CONTROL_DOMAIN_GRAPH_ID_CHANGED:{i}")
            if record.get("candidate_id") != previous.get("candidate_id"):
                p.append(f"CONTROL_DOMAIN_GRAPH_CANDIDATE_CHANGED:{i}")
            if record.get("trust_set_id") != previous.get("trust_set_id") or record.get("trust_set_digest") != previous.get("trust_set_digest"):
                p.append(f"CONTROL_DOMAIN_GRAPH_TRUST_SET_CHANGED:{i}")
            if record.get("generation_id") == previous.get("generation_id"):
                p.append(f"CONTROL_DOMAIN_GRAPH_UPDATE_REQUIRES_NEW_GENERATION:{i}")
            removed_domains = set(previous_domains) - set(domains)
            if removed_domains:
                p.append("CONTROL_DOMAIN_GRAPH_DOMAIN_REMOVAL_FORBIDDEN:" + ",".join(sorted(removed_domains)))
            for domain_id, old_parents in previous_domains.items():
                if domain_id in domains:
                    removed_parents = set(old_parents) - set(domains[domain_id])
                    if removed_parents:
                        p.append(
                            "CONTROL_DOMAIN_GRAPH_PARENT_REMOVAL_FORBIDDEN:"
                            + domain_id + ":" + ",".join(sorted(removed_parents))
                        )
            removed_candidate = set(previous_candidate_domains) - set(candidate_domains)
            if removed_candidate:
                p.append("CONTROL_DOMAIN_GRAPH_CANDIDATE_DOMAIN_REMOVAL_FORBIDDEN:" + ",".join(sorted(removed_candidate)))
        previous = record
        previous_domains = domains
        previous_candidate_domains = candidate_domains
        current_domains = domains
        current_candidate_domains = candidate_domains

    current = chain[-1]
    head_p = _head_problems(current, head, trust, expected_candidate_id)
    p.extend(head_p)
    head_matched = not head_p
    valid = not p
    return _GraphValidation(
        valid, tuple(sorted(set(p))), current if valid else None,
        current_domains if valid else {}, current_candidate_domains if valid else frozenset(),
        authenticated_domains if valid else (), head_matched if valid else False,
    )


def validate_control_domain_graph_chain(
    graph_chain: Sequence[Mapping[str, Any]], *, bootstrap_trust: base.PinnedBootstrapTrustSet,
    expected_current_head: PinnedControlDomainGraphHead, expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        chain = _snapshot_chain(graph_chain, "control_domain_graph_chain")
    except base.CanonicalizationError as exc:
        return _result(False, [f"CONTROL_DOMAIN_GRAPH_INPUT:{exc}"], "UNREACHABLE", "CONTROL_DOMAIN_GRAPH_CHAIN_INVALID")
    result = _validate_graph_chain_owned(chain, bootstrap_trust, expected_current_head, expected_candidate_id)
    out = _result(
        result.valid, list(result.problems),
        "CONTROL_DOMAIN_GRAPH_CHAIN_AUTHENTICATED_CURRENT",
        "CONTROL_DOMAIN_GRAPH_CHAIN_INVALID",
    )
    out.update({
        "promotion_blocked": not result.valid,
        "current_head_matched": result.current_head_matched,
        "graph_completeness_real_world_proven": False,
        "bootstrap_authenticated_control_domains": list(result.authenticated_bootstrap_domains),
        "candidate_domain_ids": sorted(result.candidate_domains),
    })
    if result.current is not None:
        out.update({
            "graph_id": result.current.get("graph_id"),
            "graph_digest": result.current.get("graph_digest"),
            "generation_id": result.current.get("generation_id"),
            "sequence": result.current.get("sequence"),
        })
    return out


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


def _candidate_ancestor_union(
    candidate_domains: frozenset[str], domains: Mapping[str, tuple[str, ...]],
) -> frozenset[str]:
    out: set[str] = set()
    for domain in candidate_domains:
        out.update(_ancestor_closure(domain, domains))
    return frozenset(out)


def assess_domain_independence(
    subject_a_control_domain_id: str, subject_b_control_domain_id: str, *,
    graph_chain: Sequence[Mapping[str, Any]], bootstrap_trust: base.PinnedBootstrapTrustSet,
    expected_current_head: PinnedControlDomainGraphHead, expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        chain = _snapshot_chain(graph_chain, "control_domain_graph_chain")
    except base.CanonicalizationError as exc:
        out = _result(False, [f"CONTROL_DOMAIN_GRAPH_INPUT:{exc}"], "UNREACHABLE", "INDEPENDENCE_UNPROVEN")
        out.update({"independence_result": "INDEPENDENCE_UNPROVEN", "promotion_blocked": True})
        return out
    graph = _validate_graph_chain_owned(chain, bootstrap_trust, expected_current_head, expected_candidate_id)
    p = list(graph.problems)
    for value, code in (
        (subject_a_control_domain_id, "INDEPENDENCE_SUBJECT_A"),
        (subject_b_control_domain_id, "INDEPENDENCE_SUBJECT_B"),
    ):
        _require_id(p, value, code)
    if not graph.valid:
        result = "INDEPENDENCE_UNPROVEN"
        shared: set[str] = set()
    elif subject_a_control_domain_id not in graph.current_domains or subject_b_control_domain_id not in graph.current_domains:
        if subject_a_control_domain_id not in graph.current_domains:
            p.append("INDEPENDENCE_SUBJECT_A_DOMAIN_UNKNOWN")
        if subject_b_control_domain_id not in graph.current_domains:
            p.append("INDEPENDENCE_SUBJECT_B_DOMAIN_UNKNOWN")
        result = "INDEPENDENCE_UNPROVEN"
        shared = set()
    else:
        a = _ancestor_closure(subject_a_control_domain_id, graph.current_domains)
        b = _ancestor_closure(subject_b_control_domain_id, graph.current_domains)
        shared = set(a & b)
        result = "NOT_INDEPENDENT" if shared else "INDEPENDENT_WITHIN_AUTHENTICATED_GRAPH"
    valid = graph.valid and result != "INDEPENDENCE_UNPROVEN" and not p
    out = _result(valid, p, result, "INDEPENDENCE_UNPROVEN" if result == "INDEPENDENCE_UNPROVEN" else result)
    out.update({
        "independence_result": result,
        "shared_load_bearing_ancestors": sorted(shared),
        "promotion_blocked": result != "INDEPENDENT_WITHIN_AUTHENTICATED_GRAPH",
        "independence_real_world_proven": False,
        "graph_completeness_real_world_proven": False,
    })
    return out


def assess_candidate_control(
    subject_control_domain_id: str, *, graph_chain: Sequence[Mapping[str, Any]],
    bootstrap_trust: base.PinnedBootstrapTrustSet,
    expected_current_head: PinnedControlDomainGraphHead, expected_candidate_id: str,
) -> dict[str, Any]:
    try:
        chain = _snapshot_chain(graph_chain, "control_domain_graph_chain")
    except base.CanonicalizationError as exc:
        out = _result(False, [f"CONTROL_DOMAIN_GRAPH_INPUT:{exc}"], "UNREACHABLE", "CANDIDATE_CONTROL_UNPROVEN")
        out.update({"candidate_control_result": "CANDIDATE_CONTROL_UNPROVEN", "promotion_blocked": True})
        return out
    graph = _validate_graph_chain_owned(chain, bootstrap_trust, expected_current_head, expected_candidate_id)
    p = list(graph.problems)
    _require_id(p, subject_control_domain_id, "CANDIDATE_CONTROL_SUBJECT")
    if not graph.valid or subject_control_domain_id not in graph.current_domains:
        if graph.valid and subject_control_domain_id not in graph.current_domains:
            p.append("CANDIDATE_CONTROL_SUBJECT_DOMAIN_UNKNOWN")
        result = "CANDIDATE_CONTROL_UNPROVEN"
        shared: set[str] = set()
    else:
        subject = _ancestor_closure(subject_control_domain_id, graph.current_domains)
        candidate = _candidate_ancestor_union(graph.candidate_domains, graph.current_domains)
        shared = set(subject & candidate)
        result = "CANDIDATE_CONTROLLED" if shared else "NOT_CANDIDATE_CONTROLLED_WITHIN_AUTHENTICATED_GRAPH"
    valid = graph.valid and result != "CANDIDATE_CONTROL_UNPROVEN" and not p
    out = _result(valid, p, result, "CANDIDATE_CONTROL_UNPROVEN" if result == "CANDIDATE_CONTROL_UNPROVEN" else result)
    out.update({
        "candidate_control_result": result,
        "candidate_controlled": True if result == "CANDIDATE_CONTROLLED" else False if result.startswith("NOT_CANDIDATE") else None,
        "shared_candidate_ancestors": sorted(shared),
        "promotion_blocked": result != "NOT_CANDIDATE_CONTROLLED_WITHIN_AUTHENTICATED_GRAPH",
        "control_real_world_completeness_proven": False,
    })
    return out


def _registry_head_matches(current: dict[str, Any], head: base.PinnedRegistryHead) -> bool:
    return (
        current.get("registry_id") == head.registry_id
        and current.get("candidate_id") == head.candidate_id
        and current.get("sequence") == head.sequence
        and current.get("generation_id") == head.generation_id
        and current.get("registry_digest") == head.registry_digest
        and current.get("trust_set_id") == head.trust_set_id
        and current.get("trust_set_digest") == head.trust_set_digest
        and current.get("authority_policy_digest") == head.authority_policy_digest
    )


def resolve_registry_key_authority(
    key_id: str, required_role: str, *, registry_chain: Sequence[Mapping[str, Any]],
    expected_registry_head: base.PinnedRegistryHead,
    graph_chain: Sequence[Mapping[str, Any]], expected_graph_head: PinnedControlDomainGraphHead,
    bootstrap_trust: base.PinnedBootstrapTrustSet, expected_candidate_id: str,
) -> dict[str, Any]:
    p: list[str] = []
    _require_id(p, key_id, "REGISTRY_AUTHORITY_KEY_ID")
    _require_id(p, required_role, "REGISTRY_AUTHORITY_ROLE")
    if required_role not in base.ROLE_VOCABULARY:
        p.append("REGISTRY_AUTHORITY_ROLE_UNKNOWN")
    try:
        registry = _snapshot_chain(registry_chain, "governance_key_registry_chain")
        graph = _snapshot_chain(graph_chain, "control_domain_graph_chain")
    except base.CanonicalizationError as exc:
        out = _result(False, [f"REGISTRY_AUTHORITY_INPUT:{exc}"], "UNREACHABLE", "REGISTRY_AUTHORITY_UNPROVEN")
        out.update({"authority_admissible": False, "promotion_blocked": True})
        return out

    registry_result = base.validate_governance_key_registry_chain(
        registry, bootstrap_trust, expected_candidate_id=expected_candidate_id,
    )
    if not registry_result["valid"]:
        p.extend(f"REGISTRY_AUTHORITY_REGISTRY:{x}" for x in registry_result["problems"])
    head_result = base.validate_pinned_registry_head(
        expected_registry_head, bootstrap_trust, expected_candidate_id=expected_candidate_id,
    )
    if not head_result["valid"]:
        p.extend(f"REGISTRY_AUTHORITY_HEAD:{x}" for x in head_result["problems"])
    current = registry[-1] if registry else {}
    if registry and not _registry_head_matches(current, expected_registry_head):
        p.append("REGISTRY_AUTHORITY_CURRENT_HEAD_MISMATCH")

    graph_result = _validate_graph_chain_owned(
        graph, bootstrap_trust, expected_graph_head, expected_candidate_id,
    )
    if not graph_result.valid:
        p.extend(f"REGISTRY_AUTHORITY_GRAPH:{x}" for x in graph_result.problems)

    key = None
    if type(current.get("keys")) is list:
        for row in current["keys"]:
            if type(row) is dict and row.get("key_id") == key_id:
                key = row
                break
    if key is None:
        p.append("REGISTRY_AUTHORITY_KEY_NOT_FOUND")
    domain_id = None
    candidate_controlled = None
    shared_candidate: list[str] = []
    if key is not None:
        if key.get("state") != "ACTIVE":
            p.append("REGISTRY_AUTHORITY_KEY_NOT_ACTIVE")
        roles = key.get("roles")
        if type(roles) is not list or required_role not in roles:
            p.append("REGISTRY_AUTHORITY_ROLE_NOT_GRANTED")
        domain_id = key.get("control_domain_id")
        if not _canonical_identifier(domain_id):
            p.append("REGISTRY_AUTHORITY_CONTROL_DOMAIN_INVALID")
        elif graph_result.valid:
            if domain_id not in graph_result.current_domains:
                p.append("REGISTRY_AUTHORITY_CONTROL_DOMAIN_NOT_IN_AUTHENTICATED_GRAPH")
            else:
                subject = _ancestor_closure(domain_id, graph_result.current_domains)
                candidate = _candidate_ancestor_union(graph_result.candidate_domains, graph_result.current_domains)
                shared_candidate = sorted(subject & candidate)
                candidate_controlled = bool(shared_candidate)
                if candidate_controlled:
                    p.append("REGISTRY_AUTHORITY_CANDIDATE_CONTROLLED")

    admissible = not p and key is not None and candidate_controlled is False
    out = _result(admissible, p, "REGISTRY_KEY_AUTHORITY_RESOLVED_ADMISSIBLE", "REGISTRY_AUTHORITY_UNPROVEN")
    out.update({
        "authority_admissible": admissible,
        "promotion_blocked": not admissible,
        "key_id": key_id,
        "issuer_id": key.get("issuer_id") if key else None,
        "control_domain_id": domain_id,
        "candidate_controlled": candidate_controlled,
        "shared_candidate_ancestors": shared_candidate,
        "required_role": required_role,
        "control_real_world_completeness_proven": False,
    })
    return out


def assess_registry_key_independence(
    key_id_a: str, required_role_a: str, key_id_b: str, required_role_b: str, *,
    registry_chain: Sequence[Mapping[str, Any]], expected_registry_head: base.PinnedRegistryHead,
    graph_chain: Sequence[Mapping[str, Any]], expected_graph_head: PinnedControlDomainGraphHead,
    bootstrap_trust: base.PinnedBootstrapTrustSet, expected_candidate_id: str,
) -> dict[str, Any]:
    a = resolve_registry_key_authority(
        key_id_a, required_role_a, registry_chain=registry_chain,
        expected_registry_head=expected_registry_head, graph_chain=graph_chain,
        expected_graph_head=expected_graph_head, bootstrap_trust=bootstrap_trust,
        expected_candidate_id=expected_candidate_id,
    )
    b = resolve_registry_key_authority(
        key_id_b, required_role_b, registry_chain=registry_chain,
        expected_registry_head=expected_registry_head, graph_chain=graph_chain,
        expected_graph_head=expected_graph_head, bootstrap_trust=bootstrap_trust,
        expected_candidate_id=expected_candidate_id,
    )
    p = [f"A:{x}" for x in a["problems"]] + [f"B:{x}" for x in b["problems"]]
    if not a["authority_admissible"] or not b["authority_admissible"]:
        result = "INDEPENDENCE_UNPROVEN"
        shared: list[str] = []
    else:
        domain_result = assess_domain_independence(
            a["control_domain_id"], b["control_domain_id"], graph_chain=graph_chain,
            bootstrap_trust=bootstrap_trust, expected_current_head=expected_graph_head,
            expected_candidate_id=expected_candidate_id,
        )
        p.extend(f"DOMAIN:{x}" for x in domain_result["problems"])
        result = domain_result["independence_result"]
        shared = domain_result["shared_load_bearing_ancestors"]
    valid = result != "INDEPENDENCE_UNPROVEN" and not p
    out = _result(valid, p, result, "INDEPENDENCE_UNPROVEN" if result == "INDEPENDENCE_UNPROVEN" else result)
    out.update({
        "independence_result": result,
        "shared_load_bearing_ancestors": shared,
        "promotion_blocked": result != "INDEPENDENT_WITHIN_AUTHENTICATED_GRAPH",
        "subject_a_control_domain_id": a.get("control_domain_id"),
        "subject_b_control_domain_id": b.get("control_domain_id"),
        "independence_real_world_proven": False,
    })
    return out
