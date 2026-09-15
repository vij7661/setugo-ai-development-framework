"""V24 I11 V6 proof-reference closure repair.

Construction-only resolver for governance proof references.  It makes the R1
qualification/currentness/independence validators load-bearing for downstream
V6 mechanisms.  It does not grant runtime, release, deployment, production,
scientific, or terminal authority.
"""
from __future__ import annotations

from typing import Any, Mapping

from v24_v6_governance_foundation import (
    AUTHORITY_EFFECT,
    CURRENT,
    QUALIFIED,
    digest,
    genesis_scope_match,
    validate_currentness_binding,
    validate_genesis_trusted_scope,
    validate_governed_qualification,
    validate_independence_qualification,
)

GOVERNED_QUALIFICATION = "GOVERNED_QUALIFICATION"
INDEPENDENCE_QUALIFICATION = "INDEPENDENCE_QUALIFICATION"
CURRENTNESS_BINDING = "CURRENTNESS_BINDING"

PROOF_REFERENCE_CLOSED = "PROOF_REFERENCE_CLOSED"
PROOF_REFERENCE_REJECTED = "PROOF_REFERENCE_REJECTED"
PROOF_REFERENCE_CYCLE_REJECTED = "PROOF_REFERENCE_CYCLE_REJECTED"

_SUPPORTED_KINDS = frozenset(
    {GOVERNED_QUALIFICATION, INDEPENDENCE_QUALIFICATION, CURRENTNESS_BINDING}
)
_DIGEST_FIELD = {
    GOVERNED_QUALIFICATION: "qualification_digest",
    INDEPENDENCE_QUALIFICATION: "qualification_digest",
    CURRENTNESS_BINDING: "binding_digest",
}


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _self_digest(record: Mapping[str, Any], field: str) -> str:
    material = dict(record)
    material.pop(field, None)
    return digest(material)


def _context_digest(context: Mapping[str, Any]) -> str:
    material = dict(context)
    material.pop("context_digest", None)
    return digest(material)


def seal_proof_context(context: dict[str, Any]) -> dict[str, Any]:
    """Test/construction helper: deterministically seals an already-built context.

    This helper only computes the context digest.  It does not synthesize proof
    records and it does not make a context trusted.
    """
    context["context_digest"] = _context_digest(context)
    return context


def trusted_boundary_for(context: Mapping[str, Any]) -> dict[str, Any]:
    """Construction helper for tests and frozen successor generation.

    Production authority must bind this boundary outside candidate decision data.
    """
    scope = context.get("genesis_trusted_scope")
    scope_digest = scope.get("scope_digest") if isinstance(scope, Mapping) else None
    return {
        "governance_generation_id": context.get("governance_generation_id"),
        "expected_proof_context_digest": context.get("context_digest"),
        "expected_genesis_scope_digest": scope_digest,
    }


def validate_proof_context(
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
) -> dict[str, Any]:
    problems: list[str] = []
    if not isinstance(trusted_boundary, Mapping):
        return {
            "qualified": False,
            "state": PROOF_REFERENCE_REJECTED,
            "problems": ["TRUSTED_PROOF_BOUNDARY_REQUIRED"],
            "record_count": 0,
            "authority_effect": AUTHORITY_EFFECT,
        }
    generation = trusted_boundary.get("governance_generation_id")
    expected_context_digest = trusted_boundary.get("expected_proof_context_digest")
    expected_scope_digest = trusted_boundary.get("expected_genesis_scope_digest")
    if not _nonempty(generation):
        problems.append("TRUSTED_PROOF_BOUNDARY_GENERATION_REQUIRED")
    if not _is_sha256(expected_context_digest):
        problems.append("TRUSTED_PROOF_CONTEXT_DIGEST_INVALID")
    if not _is_sha256(expected_scope_digest):
        problems.append("TRUSTED_GENESIS_SCOPE_DIGEST_INVALID")

    if not isinstance(proof_context, Mapping):
        problems.append("GOVERNANCE_PROOF_CONTEXT_REQUIRED")
        return {
            "qualified": False,
            "state": PROOF_REFERENCE_REJECTED,
            "problems": sorted(set(problems)),
            "record_count": 0,
            "authority_effect": AUTHORITY_EFFECT,
        }

    for key in ("proof_context_id", "governance_generation_id", "context_digest"):
        if not _nonempty(proof_context.get(key)):
            problems.append(f"PROOF_CONTEXT_FIELD_REQUIRED:{key}")
    if proof_context.get("governance_generation_id") != generation:
        problems.append("PROOF_CONTEXT_GENERATION_MISMATCH")
    supplied_context_digest = proof_context.get("context_digest")
    if not _is_sha256(supplied_context_digest):
        problems.append("PROOF_CONTEXT_DIGEST_INVALID")
    else:
        recomputed = _context_digest(proof_context)
        if supplied_context_digest != recomputed:
            problems.append("PROOF_CONTEXT_DIGEST_MISMATCH")
        if _is_sha256(expected_context_digest) and supplied_context_digest != expected_context_digest:
            problems.append("PROOF_CONTEXT_TRUSTED_BINDING_MISMATCH")

    scope = proof_context.get("genesis_trusted_scope")
    if not isinstance(scope, Mapping):
        problems.append("PROOF_CONTEXT_GENESIS_SCOPE_REQUIRED")
    else:
        for item in validate_genesis_trusted_scope(scope):
            problems.append(f"PROOF_CONTEXT_GENESIS:{item}")
        if scope.get("governance_generation_id") != generation:
            problems.append("PROOF_CONTEXT_GENESIS_GENERATION_MISMATCH")
        if _is_sha256(expected_scope_digest) and scope.get("scope_digest") != expected_scope_digest:
            problems.append("PROOF_CONTEXT_GENESIS_TRUSTED_BINDING_MISMATCH")

    entries = proof_context.get("evidence_records")
    if not isinstance(entries, list) or not entries:
        problems.append("PROOF_CONTEXT_EVIDENCE_RECORDS_REQUIRED")
        entries = []

    seen: set[str] = set()
    for idx, wrapper in enumerate(entries):
        if not isinstance(wrapper, Mapping):
            problems.append(f"PROOF_CONTEXT_RECORD_WRAPPER_MALFORMED:{idx}")
            continue
        kind = wrapper.get("record_kind")
        ref = wrapper.get("record_digest")
        record = wrapper.get("record")
        if kind not in _SUPPORTED_KINDS:
            problems.append(f"PROOF_CONTEXT_RECORD_KIND_UNSUPPORTED:{idx}:{kind}")
            continue
        if not _is_sha256(ref):
            problems.append(f"PROOF_CONTEXT_RECORD_DIGEST_INVALID:{idx}")
            continue
        if ref in seen:
            problems.append(f"PROOF_CONTEXT_RECORD_DIGEST_DUPLICATE:{ref}")
        seen.add(ref)
        if not isinstance(record, Mapping):
            problems.append(f"PROOF_CONTEXT_RECORD_MALFORMED:{idx}")
            continue
        digest_field = _DIGEST_FIELD[kind]
        if record.get(digest_field) != ref:
            problems.append(f"PROOF_CONTEXT_RECORD_KEY_SELF_DIGEST_MISMATCH:{idx}")
        if _self_digest(record, digest_field) != ref:
            problems.append(f"PROOF_CONTEXT_RECORD_RECOMPUTE_MISMATCH:{idx}")
        if kind == GOVERNED_QUALIFICATION:
            structural = validate_governed_qualification(record)
        elif kind == INDEPENDENCE_QUALIFICATION:
            structural = validate_independence_qualification(record)
        else:
            structural = validate_currentness_binding(record)
        for item in structural:
            problems.append(f"PROOF_CONTEXT_RECORD:{idx}:{item}")

    problems = sorted(set(problems))
    return {
        "qualified": not problems,
        "state": PROOF_REFERENCE_CLOSED if not problems else PROOF_REFERENCE_REJECTED,
        "problems": problems,
        "record_count": len(entries),
        "authority_effect": AUTHORITY_EFFECT,
    }


class _Resolver:
    def __init__(
        self,
        proof_context: Mapping[str, Any],
        trusted_boundary: Mapping[str, Any],
    ) -> None:
        self.context = proof_context
        self.boundary = trusted_boundary
        self.scope = proof_context["genesis_trusted_scope"]
        self.index: dict[str, Mapping[str, Any]] = {}
        for wrapper in proof_context["evidence_records"]:
            self.index[wrapper["record_digest"]] = wrapper
        self.active: set[tuple[str, str]] = set()
        self.memo: dict[tuple[Any, ...], tuple[bool, tuple[str, ...]]] = {}
        self.resolved: set[str] = set()

    def _lookup(self, ref: str, kind: str) -> tuple[Mapping[str, Any] | None, list[str]]:
        if not _is_sha256(ref):
            return None, [f"PROOF_REFERENCE_DIGEST_INVALID:{kind}"]
        wrapper = self.index.get(ref)
        if wrapper is None:
            return None, [f"PROOF_REFERENCE_UNRESOLVED:{kind}:{ref}"]
        if wrapper.get("record_kind") != kind:
            return None, [
                f"PROOF_REFERENCE_KIND_MISMATCH:{kind}:{wrapper.get('record_kind')}:{ref}"
            ]
        record = wrapper.get("record")
        if not isinstance(record, Mapping):
            return None, [f"PROOF_REFERENCE_RECORD_MALFORMED:{kind}:{ref}"]
        return record, []

    def resolve_qualification(
        self,
        ref: str,
        *,
        expected_subject_id: str | None = None,
        expected_subject_content_digest: str | None = None,
    ) -> tuple[bool, list[str]]:
        memo_key = (
            GOVERNED_QUALIFICATION,
            ref,
            expected_subject_id,
            expected_subject_content_digest,
        )
        if memo_key in self.memo:
            ok, cached = self.memo[memo_key]
            return ok, list(cached)
        active_key = (GOVERNED_QUALIFICATION, ref)
        if active_key in self.active:
            return False, [f"{PROOF_REFERENCE_CYCLE_REJECTED}:{GOVERNED_QUALIFICATION}:{ref}"]
        record, problems = self._lookup(ref, GOVERNED_QUALIFICATION)
        if record is None:
            return False, problems
        self.active.add(active_key)
        try:
            for item in validate_governed_qualification(record):
                problems.append(f"GOVERNED_QUALIFICATION_INVALID:{ref}:{item}")
            if record.get("result") != QUALIFIED:
                problems.append(f"GOVERNED_QUALIFICATION_NOT_QUALIFIED:{ref}")
            if expected_subject_id is not None and record.get("subject_object_id") != expected_subject_id:
                problems.append(
                    f"GOVERNED_QUALIFICATION_SUBJECT_ID_MISMATCH:{ref}:{expected_subject_id}"
                )
            if (
                expected_subject_content_digest is not None
                and record.get("subject_content_digest") != expected_subject_content_digest
            ):
                problems.append(
                    f"GOVERNED_QUALIFICATION_SUBJECT_DIGEST_MISMATCH:{ref}"
                )
            if problems:
                result = (False, tuple(sorted(set(problems))))
                self.memo[memo_key] = result
                return result[0], list(result[1])

            root = genesis_scope_match(
                self.scope,
                object_id=record["subject_object_id"],
                content_digest=record["subject_content_digest"],
            )
            if root["matched"]:
                self.resolved.add(ref)
                result = (True, tuple())
                self.memo[memo_key] = result
                return True, []

            verifier_ref = record["verifier_mechanism_qualification_digest"]
            ok, child = self.resolve_qualification(
                verifier_ref,
                expected_subject_id=record["verifier_mechanism_id"],
            )
            if not ok:
                problems.extend(
                    f"QUALIFICATION_VERIFIER_DEPENDENCY:{ref}:{item}" for item in child
                )

            for independence_ref in record["independence_qualification_digests"]:
                ok, child = self.resolve_independence(independence_ref)
                if not ok:
                    problems.extend(
                        f"QUALIFICATION_INDEPENDENCE_DEPENDENCY:{ref}:{item}"
                        for item in child
                    )

            for idx, binding in enumerate(record["currentness_bindings"]):
                ok, child = self.validate_embedded_currentness(
                    binding,
                    expected_source_id=record["subject_object_id"],
                    expected_source_digest=record["subject_content_digest"],
                )
                if not ok:
                    problems.extend(
                        f"QUALIFICATION_CURRENTNESS_DEPENDENCY:{ref}:{idx}:{item}"
                        for item in child
                    )

            problems = sorted(set(problems))
            if not problems:
                self.resolved.add(ref)
            result = (not problems, tuple(problems))
            self.memo[memo_key] = result
            return result[0], list(result[1])
        finally:
            self.active.discard(active_key)

    def resolve_independence(
        self,
        ref: str,
        *,
        expected_subject_identity_id: str | None = None,
    ) -> tuple[bool, list[str]]:
        memo_key = (INDEPENDENCE_QUALIFICATION, ref, expected_subject_identity_id)
        if memo_key in self.memo:
            ok, cached = self.memo[memo_key]
            return ok, list(cached)
        active_key = (INDEPENDENCE_QUALIFICATION, ref)
        if active_key in self.active:
            return False, [f"{PROOF_REFERENCE_CYCLE_REJECTED}:{INDEPENDENCE_QUALIFICATION}:{ref}"]
        record, problems = self._lookup(ref, INDEPENDENCE_QUALIFICATION)
        if record is None:
            return False, problems
        self.active.add(active_key)
        try:
            for item in validate_independence_qualification(record):
                problems.append(f"INDEPENDENCE_QUALIFICATION_INVALID:{ref}:{item}")
            if record.get("result") != QUALIFIED:
                problems.append(f"INDEPENDENCE_QUALIFICATION_NOT_QUALIFIED:{ref}")
            if (
                expected_subject_identity_id is not None
                and record.get("subject_identity_id") != expected_subject_identity_id
            ):
                problems.append(
                    f"INDEPENDENCE_SUBJECT_ID_MISMATCH:{ref}:{expected_subject_identity_id}"
                )
            if not problems:
                verifier_ref = record["verifier_qualification_digest"]
                ok, child = self.resolve_qualification(verifier_ref)
                if not ok:
                    problems.extend(
                        f"INDEPENDENCE_VERIFIER_DEPENDENCY:{ref}:{item}" for item in child
                    )
                for idx, binding in enumerate(record["currentness_bindings"]):
                    ok, child = self.validate_embedded_currentness(binding)
                    if not ok:
                        problems.extend(
                            f"INDEPENDENCE_CURRENTNESS_DEPENDENCY:{ref}:{idx}:{item}"
                            for item in child
                        )
            problems = sorted(set(problems))
            if not problems:
                self.resolved.add(ref)
            result = (not problems, tuple(problems))
            self.memo[memo_key] = result
            return result[0], list(result[1])
        finally:
            self.active.discard(active_key)

    def validate_embedded_currentness(
        self,
        record: Mapping[str, Any],
        *,
        expected_source_id: str | None = None,
        expected_source_digest: str | None = None,
    ) -> tuple[bool, list[str]]:
        problems: list[str] = []
        if not isinstance(record, Mapping):
            return False, ["CURRENTNESS_RECORD_MALFORMED"]
        for item in validate_currentness_binding(record):
            problems.append(f"CURRENTNESS_INVALID:{item}")
        if record.get("result") != CURRENT:
            problems.append("CURRENTNESS_NOT_CURRENT")
        if expected_source_id is not None and record.get("source_object_id") != expected_source_id:
            problems.append(f"CURRENTNESS_SOURCE_ID_MISMATCH:{expected_source_id}")
        if (
            expected_source_digest is not None
            and record.get("source_digest") != expected_source_digest
        ):
            problems.append("CURRENTNESS_SOURCE_DIGEST_MISMATCH")
        if not problems:
            ok, child = self.resolve_qualification(record["verifier_qualification_digest"])
            if not ok:
                problems.extend(f"CURRENTNESS_VERIFIER_DEPENDENCY:{item}" for item in child)
        return not problems, sorted(set(problems))

    def resolve_currentness(
        self,
        ref: str,
        *,
        expected_source_id: str | None = None,
        expected_source_digest: str | None = None,
    ) -> tuple[bool, list[str]]:
        memo_key = (CURRENTNESS_BINDING, ref, expected_source_id, expected_source_digest)
        if memo_key in self.memo:
            ok, cached = self.memo[memo_key]
            return ok, list(cached)
        active_key = (CURRENTNESS_BINDING, ref)
        if active_key in self.active:
            return False, [f"{PROOF_REFERENCE_CYCLE_REJECTED}:{CURRENTNESS_BINDING}:{ref}"]
        record, problems = self._lookup(ref, CURRENTNESS_BINDING)
        if record is None:
            return False, problems
        self.active.add(active_key)
        try:
            ok, child = self.validate_embedded_currentness(
                record,
                expected_source_id=expected_source_id,
                expected_source_digest=expected_source_digest,
            )
            if not ok:
                problems.extend(child)
            problems = sorted(set(problems))
            if not problems:
                self.resolved.add(ref)
            result = (not problems, tuple(problems))
            self.memo[memo_key] = result
            return result[0], list(result[1])
        finally:
            self.active.discard(active_key)


def _build_resolver(
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
) -> tuple[_Resolver | None, list[str]]:
    context_result = validate_proof_context(proof_context, trusted_boundary)
    if not context_result["qualified"]:
        return None, list(context_result["problems"])
    assert isinstance(proof_context, Mapping)
    assert isinstance(trusted_boundary, Mapping)
    return _Resolver(proof_context, trusted_boundary), []


def resolve_governed_qualification(
    reference_digest: str,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
    *,
    expected_subject_id: str | None = None,
    expected_subject_content_digest: str | None = None,
) -> dict[str, Any]:
    resolver, problems = _build_resolver(proof_context, trusted_boundary)
    if resolver is not None:
        ok, child = resolver.resolve_qualification(
            reference_digest,
            expected_subject_id=expected_subject_id,
            expected_subject_content_digest=expected_subject_content_digest,
        )
        problems.extend(child)
    else:
        ok = False
    problems = sorted(set(problems))
    return {
        "qualified": bool(resolver is not None and ok and not problems),
        "state": PROOF_REFERENCE_CLOSED if resolver is not None and ok and not problems else PROOF_REFERENCE_REJECTED,
        "reference_digest": reference_digest,
        "problems": problems,
        "resolved_digests": sorted(resolver.resolved) if resolver is not None else [],
        "authority_effect": AUTHORITY_EFFECT,
    }


def resolve_independence_qualification(
    reference_digest: str,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
    *,
    expected_subject_identity_id: str | None = None,
) -> dict[str, Any]:
    resolver, problems = _build_resolver(proof_context, trusted_boundary)
    if resolver is not None:
        ok, child = resolver.resolve_independence(
            reference_digest,
            expected_subject_identity_id=expected_subject_identity_id,
        )
        problems.extend(child)
    else:
        ok = False
    problems = sorted(set(problems))
    return {
        "qualified": bool(resolver is not None and ok and not problems),
        "state": PROOF_REFERENCE_CLOSED if resolver is not None and ok and not problems else PROOF_REFERENCE_REJECTED,
        "reference_digest": reference_digest,
        "problems": problems,
        "resolved_digests": sorted(resolver.resolved) if resolver is not None else [],
        "authority_effect": AUTHORITY_EFFECT,
    }


def resolve_currentness_binding(
    reference_digest: str,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
    *,
    expected_source_id: str | None = None,
    expected_source_digest: str | None = None,
) -> dict[str, Any]:
    resolver, problems = _build_resolver(proof_context, trusted_boundary)
    if resolver is not None:
        ok, child = resolver.resolve_currentness(
            reference_digest,
            expected_source_id=expected_source_id,
            expected_source_digest=expected_source_digest,
        )
        problems.extend(child)
    else:
        ok = False
    problems = sorted(set(problems))
    return {
        "qualified": bool(resolver is not None and ok and not problems),
        "state": PROOF_REFERENCE_CLOSED if resolver is not None and ok and not problems else PROOF_REFERENCE_REJECTED,
        "reference_digest": reference_digest,
        "problems": problems,
        "resolved_digests": sorted(resolver.resolved) if resolver is not None else [],
        "authority_effect": AUTHORITY_EFFECT,
    }


def close_governance_dependencies(
    requirements: list[Mapping[str, Any]],
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Close a deterministic list of downstream governance proof requirements.

    Requirement forms:
      {"kind":"GOVERNED_QUALIFICATION","reference_digest":...,"subject_id":...,"subject_content_digest":...}
      {"kind":"INDEPENDENCE_QUALIFICATION","reference_digest":...,"subject_identity_id":...}
      {"kind":"CURRENTNESS_BINDING","reference_digest":...,"source_id":...,"source_digest":...}
    """
    resolver, problems = _build_resolver(proof_context, trusted_boundary)
    if resolver is None:
        return {
            "qualified": False,
            "state": PROOF_REFERENCE_REJECTED,
            "problems": sorted(set(problems)),
            "resolved_digests": [],
            "authority_effect": AUTHORITY_EFFECT,
        }
    if not isinstance(requirements, list) or not requirements:
        problems.append("PROOF_REQUIREMENTS_NONEMPTY_LIST_REQUIRED")
        requirements = []
    for idx, req in enumerate(requirements):
        if not isinstance(req, Mapping):
            problems.append(f"PROOF_REQUIREMENT_MALFORMED:{idx}")
            continue
        kind = req.get("kind")
        ref = req.get("reference_digest")
        if kind == GOVERNED_QUALIFICATION:
            ok, child = resolver.resolve_qualification(
                ref,
                expected_subject_id=req.get("subject_id"),
                expected_subject_content_digest=req.get("subject_content_digest"),
            )
        elif kind == INDEPENDENCE_QUALIFICATION:
            ok, child = resolver.resolve_independence(
                ref,
                expected_subject_identity_id=req.get("subject_identity_id"),
            )
        elif kind == CURRENTNESS_BINDING:
            ok, child = resolver.resolve_currentness(
                ref,
                expected_source_id=req.get("source_id"),
                expected_source_digest=req.get("source_digest"),
            )
        else:
            ok, child = False, [f"PROOF_REQUIREMENT_KIND_UNSUPPORTED:{idx}:{kind}"]
        if not ok:
            problems.extend(f"PROOF_REQUIREMENT:{idx}:{item}" for item in child)
    problems = sorted(set(problems))
    return {
        "qualified": not problems,
        "state": PROOF_REFERENCE_CLOSED if not problems else PROOF_REFERENCE_REJECTED,
        "problems": problems,
        "resolved_digests": sorted(resolver.resolved),
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_PROOF_REFERENCE_CLOSURE_CONSTRUCTION_READY",
        "qualified": False,
        "authority_effect": AUTHORITY_EFFECT,
    }
