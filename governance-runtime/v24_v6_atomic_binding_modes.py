"""V24 I11 V6 remediation R7: atomic-binding mode completeness and proof gating.

Construction-only implementation of V6 Section 13. Every authority-bearing
contract, admitted mechanism, registry verifier, registry result, and individual
atomic-binding proof resolves exact R1 proof records through a separately trusted
proof context. Caller labels and self-consistent SHA-shaped fields are not authority.
"""
from __future__ import annotations

from typing import Any, Mapping

from v24_v6_governance_foundation import (
    AUTHORITY_EFFECT,
    CURRENT,
    QUALIFIED,
    digest,
    validate_registry_completeness_qualification,
)
from v24_v6_proof_reference_closure import (
    CURRENTNESS_BINDING,
    GOVERNED_QUALIFICATION,
    INDEPENDENCE_QUALIFICATION,
    close_governance_dependencies,
)


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _sha(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def _unique_strings(value: Any) -> tuple[list[str], list[str]]:
    if not isinstance(value, list):
        return [], ["LIST_REQUIRED"]
    seen: set[str] = set()
    out: list[str] = []
    problems: list[str] = []
    for item in value:
        if not _nonempty(item):
            problems.append("STRING_MEMBER_INVALID")
        elif item in seen:
            problems.append(f"DUPLICATE_MEMBER:{item}")
        else:
            seen.add(item)
            out.append(item)
    return out, problems


def _append_proof(prefix: str, result: Mapping[str, Any], problems: list[str]) -> bool:
    if result.get("qualified") is True:
        return True
    child = result.get("problems")
    if isinstance(child, list) and child:
        problems.extend(f"{prefix}:{item}" for item in child)
    else:
        problems.append(f"{prefix}:PROOF_REFERENCE_CLOSURE_FAILED")
    return False


def _close(
    requirements: list[Mapping[str, Any]],
    *,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
    prefix: str,
    problems: list[str],
) -> bool:
    result = close_governance_dependencies(
        requirements,
        proof_context,
        trusted_boundary,
    )
    return _append_proof(prefix, result, problems)


def _close_completeness_dependencies(
    record: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None,
    trusted_boundary: Mapping[str, Any] | None,
    prefix: str,
    problems: list[str],
) -> bool:
    requirements: list[Mapping[str, Any]] = []
    for ref in record.get("derivation_mechanism_qualification_digests", []):
        requirements.append({"kind": GOVERNED_QUALIFICATION, "reference_digest": ref})
    for ref in record.get("derivation_authority_independence_digests", []):
        requirements.append({"kind": INDEPENDENCE_QUALIFICATION, "reference_digest": ref})
    verifier = record.get("verifier_qualification_digest")
    if verifier is not None:
        requirements.append({"kind": GOVERNED_QUALIFICATION, "reference_digest": verifier})
    currentness = record.get("currentness_bindings")
    if isinstance(currentness, list):
        for binding in currentness:
            if isinstance(binding, Mapping):
                ref = binding.get("verifier_qualification_digest")
                if ref is not None:
                    requirements.append({"kind": GOVERNED_QUALIFICATION, "reference_digest": ref})
    if not requirements:
        problems.append(f"{prefix}:COMPLETENESS_PROOF_REFERENCES_REQUIRED")
        return False
    return _close(
        requirements,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix=prefix,
        problems=problems,
    )


def canonical_contract_binding_digest(record: Mapping[str, Any]) -> str:
    modes = record.get("required_atomic_binding_mode_ids")
    return digest(
        {
            "contract_id": record.get("contract_id"),
            "contract_digest": record.get("contract_digest"),
            "authority_identity_id": record.get("authority_identity_id"),
            "control_domain_id": record.get("control_domain_id"),
            "required_atomic_binding_mode_ids": sorted(modes) if isinstance(modes, list) else [],
        }
    )


def canonical_mechanism_binding_digest(record: Mapping[str, Any]) -> str:
    modes = record.get("supported_atomic_binding_mode_ids")
    return digest(
        {
            "mechanism_id": record.get("mechanism_id"),
            "mechanism_kind": record.get("mechanism_kind"),
            "mechanism_digest": record.get("mechanism_digest"),
            "authority_identity_id": record.get("authority_identity_id"),
            "control_domain_id": record.get("control_domain_id"),
            "supported_atomic_binding_mode_ids": sorted(modes) if isinstance(modes, list) else [],
        }
    )


def derive_atomic_binding_mode_obligation_set(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive exact mode obligations only from proof-closed contracts/mechanisms."""
    problems: list[str] = []
    contracts = bundle.get("binding_contracts")
    mechanisms = bundle.get("admitted_binding_mechanisms")
    if not isinstance(contracts, list) or not contracts:
        contracts = []
        problems.append("ATOMIC_BINDING_CONTRACTS_REQUIRED")
    if not isinstance(mechanisms, list) or not mechanisms:
        mechanisms = []
        problems.append("ATOMIC_BINDING_MECHANISMS_REQUIRED")

    contract_modes: set[str] = set()
    mechanism_modes: set[str] = set()
    seen_contracts: set[str] = set()
    seen_mechanisms: set[str] = set()
    contract_domains: set[str] = set()
    mechanism_domains: set[str] = set()
    canonical_contracts: list[dict[str, Any]] = []
    canonical_mechanisms: list[dict[str, Any]] = []

    for index, record in enumerate(contracts):
        if not isinstance(record, Mapping):
            problems.append(f"ATOMIC_BINDING_CONTRACT_MALFORMED:{index}")
            continue
        cid = record.get("contract_id")
        if not _nonempty(cid):
            problems.append(f"ATOMIC_BINDING_CONTRACT_ID_REQUIRED:{index}")
            cid = f"INDEX-{index}"
        elif cid in seen_contracts:
            problems.append(f"ATOMIC_BINDING_CONTRACT_DUPLICATE:{cid}")
        seen_contracts.add(cid)
        if not _sha(record.get("contract_digest")):
            problems.append(f"ATOMIC_BINDING_CONTRACT_DIGEST_INVALID:{cid}")
        authority_id = record.get("authority_identity_id")
        if not _nonempty(authority_id):
            problems.append(f"ATOMIC_BINDING_CONTRACT_AUTHORITY_ID_REQUIRED:{cid}")
        modes, mode_problems = _unique_strings(record.get("required_atomic_binding_mode_ids"))
        problems.extend(f"ATOMIC_BINDING_CONTRACT_MODES:{cid}:{x}" for x in mode_problems)
        if not modes:
            problems.append(f"ATOMIC_BINDING_CONTRACT_MODES_REQUIRED:{cid}")
        binding_digest = canonical_contract_binding_digest(record)
        if record.get("binding_content_digest") != binding_digest:
            problems.append(f"ATOMIC_BINDING_CONTRACT_CONTENT_DIGEST_MISMATCH:{cid}")
        for key in (
            "qualification_digest",
            "authority_independence_qualification_digest",
            "currentness_binding_digest",
        ):
            if not _sha(record.get(key)):
                problems.append(f"ATOMIC_BINDING_CONTRACT_PROOF_DIGEST_INVALID:{cid}:{key}")
        for key, expected, error in (
            ("qualification_state", QUALIFIED, f"ATOMIC_BINDING_CONTRACT_NOT_QUALIFIED:{cid}"),
            ("authority_independence_state", QUALIFIED, f"ATOMIC_BINDING_CONTRACT_NOT_INDEPENDENT:{cid}"),
            ("currentness_result", CURRENT, f"ATOMIC_BINDING_CONTRACT_NOT_CURRENT:{cid}"),
        ):
            value = record.get(key)
            if value is not None and value != expected:
                problems.append(error)
        _close(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": record.get("qualification_digest"),
                    "subject_id": cid,
                    "subject_content_digest": binding_digest,
                },
                {
                    "kind": INDEPENDENCE_QUALIFICATION,
                    "reference_digest": record.get("authority_independence_qualification_digest"),
                    "subject_identity_id": authority_id,
                },
                {
                    "kind": CURRENTNESS_BINDING,
                    "reference_digest": record.get("currentness_binding_digest"),
                    "source_id": cid,
                    "source_digest": binding_digest,
                },
            ],
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix=f"ATOMIC_BINDING_CONTRACT_PROOF:{cid}",
            problems=problems,
        )
        domain = record.get("control_domain_id")
        if not _nonempty(domain):
            problems.append(f"ATOMIC_BINDING_CONTRACT_CONTROL_DOMAIN_REQUIRED:{cid}")
        elif domain in contract_domains:
            problems.append(f"ATOMIC_BINDING_CONTRACT_CONTROL_DOMAIN_DUPLICATE:{domain}")
        else:
            contract_domains.add(domain)
        contract_modes.update(modes)
        canonical_contracts.append(
            {
                "contract_id": cid,
                "binding_content_digest": binding_digest,
                "qualification_digest": record.get("qualification_digest"),
                "authority_independence_qualification_digest": record.get("authority_independence_qualification_digest"),
                "currentness_binding_digest": record.get("currentness_binding_digest"),
                "required_atomic_binding_mode_ids": sorted(modes),
            }
        )

    for index, record in enumerate(mechanisms):
        if not isinstance(record, Mapping):
            problems.append(f"ATOMIC_BINDING_MECHANISM_MALFORMED:{index}")
            continue
        mid = record.get("mechanism_id")
        if not _nonempty(mid):
            problems.append(f"ATOMIC_BINDING_MECHANISM_ID_REQUIRED:{index}")
            mid = f"INDEX-{index}"
        elif mid in seen_mechanisms:
            problems.append(f"ATOMIC_BINDING_MECHANISM_DUPLICATE:{mid}")
        seen_mechanisms.add(mid)
        if record.get("mechanism_kind") not in {"AUTHORITATIVE_TRANSACTION", "CRYPTOGRAPHIC_SNAPSHOT"}:
            problems.append(f"ATOMIC_BINDING_MECHANISM_KIND_INVALID:{mid}")
        if not _sha(record.get("mechanism_digest")):
            problems.append(f"ATOMIC_BINDING_MECHANISM_DIGEST_INVALID:{mid}")
        authority_id = record.get("authority_identity_id")
        if not _nonempty(authority_id):
            problems.append(f"ATOMIC_BINDING_MECHANISM_AUTHORITY_ID_REQUIRED:{mid}")
        modes, mode_problems = _unique_strings(record.get("supported_atomic_binding_mode_ids"))
        problems.extend(f"ATOMIC_BINDING_MECHANISM_MODES:{mid}:{x}" for x in mode_problems)
        if not modes:
            problems.append(f"ATOMIC_BINDING_MECHANISM_MODES_REQUIRED:{mid}")
        binding_digest = canonical_mechanism_binding_digest(record)
        if record.get("binding_content_digest") != binding_digest:
            problems.append(f"ATOMIC_BINDING_MECHANISM_CONTENT_DIGEST_MISMATCH:{mid}")
        for key in (
            "admission_qualification_digest",
            "qualification_digest",
            "authority_independence_qualification_digest",
            "currentness_binding_digest",
        ):
            if not _sha(record.get(key)):
                problems.append(f"ATOMIC_BINDING_MECHANISM_PROOF_DIGEST_INVALID:{mid}:{key}")
        for key, expected, error in (
            ("admission_state", QUALIFIED, f"ATOMIC_BINDING_MECHANISM_NOT_ADMITTED:{mid}"),
            ("qualification_state", QUALIFIED, f"ATOMIC_BINDING_MECHANISM_NOT_QUALIFIED:{mid}"),
            ("authority_independence_state", QUALIFIED, f"ATOMIC_BINDING_MECHANISM_NOT_INDEPENDENT:{mid}"),
            ("currentness_result", CURRENT, f"ATOMIC_BINDING_MECHANISM_NOT_CURRENT:{mid}"),
        ):
            value = record.get(key)
            if value is not None and value != expected:
                problems.append(error)
        _close(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": record.get("admission_qualification_digest"),
                    "subject_id": mid,
                    "subject_content_digest": binding_digest,
                },
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": record.get("qualification_digest"),
                    "subject_id": mid,
                    "subject_content_digest": binding_digest,
                },
                {
                    "kind": INDEPENDENCE_QUALIFICATION,
                    "reference_digest": record.get("authority_independence_qualification_digest"),
                    "subject_identity_id": authority_id,
                },
                {
                    "kind": CURRENTNESS_BINDING,
                    "reference_digest": record.get("currentness_binding_digest"),
                    "source_id": mid,
                    "source_digest": binding_digest,
                },
            ],
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix=f"ATOMIC_BINDING_MECHANISM_PROOF:{mid}",
            problems=problems,
        )
        domain = record.get("control_domain_id")
        if not _nonempty(domain):
            problems.append(f"ATOMIC_BINDING_MECHANISM_CONTROL_DOMAIN_REQUIRED:{mid}")
        elif domain in mechanism_domains:
            problems.append(f"ATOMIC_BINDING_MECHANISM_CONTROL_DOMAIN_DUPLICATE:{domain}")
        else:
            mechanism_domains.add(domain)
        mechanism_modes.update(modes)
        canonical_mechanisms.append(
            {
                "mechanism_id": mid,
                "binding_content_digest": binding_digest,
                "admission_qualification_digest": record.get("admission_qualification_digest"),
                "qualification_digest": record.get("qualification_digest"),
                "authority_independence_qualification_digest": record.get("authority_independence_qualification_digest"),
                "currentness_binding_digest": record.get("currentness_binding_digest"),
                "supported_atomic_binding_mode_ids": sorted(modes),
            }
        )

    if contract_modes != mechanism_modes:
        for mode in sorted(contract_modes - mechanism_modes):
            problems.append(f"ATOMIC_BINDING_MODE_REQUIRED_BUT_UNSUPPORTED:{mode}")
        for mode in sorted(mechanism_modes - contract_modes):
            problems.append(f"ATOMIC_BINDING_MODE_SUPPORTED_BUT_UNOBLIGATED:{mode}")
        problems.append("ATOMIC_BINDING_OBLIGATION_SOURCE_SET_MISMATCH")

    expected = sorted(contract_modes | mechanism_modes)
    if not expected:
        problems.append("ATOMIC_BINDING_EXPECTED_UNIVERSE_EMPTY")
    derivation_material = {
        "contracts": sorted(canonical_contracts, key=lambda x: x["contract_id"]),
        "mechanisms": sorted(canonical_mechanisms, key=lambda x: x["mechanism_id"]),
        "expected_members": expected,
    }
    problems = sorted(set(problems))
    return {
        "state": "ATOMIC_BINDING_MODE_OBLIGATION_SET_QUALIFIED" if not problems else "ATOMIC_BINDING_MODE_OBLIGATION_SET_INVALID",
        "qualified": not problems,
        "expected_members": expected,
        "expected_member_set_digest": digest(expected),
        "contract_mode_set_digest": digest(sorted(contract_modes)),
        "mechanism_mode_set_digest": digest(sorted(mechanism_modes)),
        "derivation_digest": digest(derivation_material),
        "derivation_binding_material": derivation_material,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def canonical_mode_entry_content_digest(entry: Mapping[str, Any]) -> str:
    fields = entry.get("required_proof_fields")
    return digest(
        {
            "mode_id": entry.get("mode_id"),
            "proof_schema_digest": entry.get("proof_schema_digest"),
            "verifier_mechanism_id": entry.get("verifier_mechanism_id"),
            "verifier_mechanism_content_digest": entry.get("verifier_mechanism_content_digest"),
            "required_proof_fields": sorted(fields) if isinstance(fields, list) else [],
        }
    )


def canonical_registry_content_digest(registry: Mapping[str, Any]) -> str:
    entries = registry.get("entries")
    canonical_entries = []
    if isinstance(entries, list):
        canonical_entries = [
            {
                "mode_id": entry.get("mode_id"),
                "entry_content_digest": canonical_mode_entry_content_digest(entry),
            }
            for entry in entries
            if isinstance(entry, Mapping)
        ]
    return digest(
        {
            "registry_id": registry.get("registry_id"),
            "entries": sorted(canonical_entries, key=lambda x: str(x["mode_id"])),
        }
    )


def validate_atomic_binding_mode_registry(
    bundle: Mapping[str, Any],
    *,
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate omission-sensitive registry and exact verifier/completeness proofs."""
    problems: list[str] = []
    registry = bundle.get("registry")
    if not isinstance(registry, Mapping):
        registry = {}
        problems.append("ATOMIC_BINDING_MODE_REGISTRY_REQUIRED")

    registry_id = registry.get("registry_id")
    if not _nonempty(registry_id):
        problems.append("ATOMIC_BINDING_MODE_REGISTRY_ID_REQUIRED")
    computed_registry_digest = canonical_registry_content_digest(registry)
    if registry.get("content_digest") != computed_registry_digest:
        problems.append("ATOMIC_BINDING_MODE_REGISTRY_CONTENT_DIGEST_MISMATCH")
    for key in ("qualification_digest", "currentness_binding_digest"):
        if not _sha(registry.get(key)):
            problems.append(f"ATOMIC_BINDING_MODE_REGISTRY_PROOF_DIGEST_INVALID:{key}")
    for key, expected, error in (
        ("qualification_state", QUALIFIED, "ATOMIC_BINDING_MODE_REGISTRY_NOT_QUALIFIED"),
        ("currentness_result", CURRENT, "ATOMIC_BINDING_MODE_REGISTRY_NOT_CURRENT"),
    ):
        value = registry.get(key)
        if value is not None and value != expected:
            problems.append(error)
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": registry.get("qualification_digest"),
                "subject_id": registry_id,
                "subject_content_digest": computed_registry_digest,
            },
            {
                "kind": CURRENTNESS_BINDING,
                "reference_digest": registry.get("currentness_binding_digest"),
                "source_id": registry_id,
                "source_digest": computed_registry_digest,
            },
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="ATOMIC_BINDING_MODE_REGISTRY_PROOF",
        problems=problems,
    )

    entries = registry.get("entries")
    if not isinstance(entries, list) or not entries:
        entries = []
        problems.append("ATOMIC_BINDING_MODE_ENTRIES_REQUIRED")
    entry_by_id: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            problems.append(f"ATOMIC_BINDING_MODE_ENTRY_MALFORMED:{index}")
            continue
        mode_id = entry.get("mode_id")
        if not _nonempty(mode_id):
            problems.append(f"ATOMIC_BINDING_MODE_ID_REQUIRED:{index}")
            continue
        if mode_id in entry_by_id:
            problems.append(f"ATOMIC_BINDING_MODE_DUPLICATE:{mode_id}")
            continue
        if not _sha(entry.get("proof_schema_digest")):
            problems.append(f"ATOMIC_BINDING_MODE_PROOF_SCHEMA_INVALID:{mode_id}")
        if not _nonempty(entry.get("verifier_mechanism_id")):
            problems.append(f"ATOMIC_BINDING_MODE_VERIFIER_REQUIRED:{mode_id}")
        if not _sha(entry.get("verifier_mechanism_content_digest")):
            problems.append(f"ATOMIC_BINDING_MODE_VERIFIER_CONTENT_DIGEST_INVALID:{mode_id}")
        for key in ("verifier_qualification_digest", "verifier_currentness_binding_digest"):
            if not _sha(entry.get(key)):
                problems.append(f"ATOMIC_BINDING_MODE_VERIFIER_PROOF_DIGEST_INVALID:{mode_id}:{key}")
        for key, expected, error in (
            ("verifier_qualification_state", QUALIFIED, f"ATOMIC_BINDING_MODE_VERIFIER_NOT_QUALIFIED:{mode_id}"),
            ("currentness_result", CURRENT, f"ATOMIC_BINDING_MODE_VERIFIER_NOT_CURRENT:{mode_id}"),
        ):
            value = entry.get(key)
            if value is not None and value != expected:
                problems.append(error)
        proof_fields, field_problems = _unique_strings(entry.get("required_proof_fields"))
        problems.extend(f"ATOMIC_BINDING_MODE_PROOF_FIELDS:{mode_id}:{x}" for x in field_problems)
        if not proof_fields:
            problems.append(f"ATOMIC_BINDING_MODE_PROOF_FIELDS_REQUIRED:{mode_id}")
        entry_content_digest = canonical_mode_entry_content_digest(entry)
        if entry.get("entry_content_digest") != entry_content_digest:
            problems.append(f"ATOMIC_BINDING_MODE_ENTRY_CONTENT_DIGEST_MISMATCH:{mode_id}")
        _close(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": entry.get("verifier_qualification_digest"),
                    "subject_id": entry.get("verifier_mechanism_id"),
                    "subject_content_digest": entry.get("verifier_mechanism_content_digest"),
                },
                {
                    "kind": CURRENTNESS_BINDING,
                    "reference_digest": entry.get("verifier_currentness_binding_digest"),
                    "source_id": entry.get("verifier_mechanism_id"),
                    "source_digest": entry.get("verifier_mechanism_content_digest"),
                },
            ],
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix=f"ATOMIC_BINDING_MODE_VERIFIER_PROOF:{mode_id}",
            problems=problems,
        )
        entry_by_id[mode_id] = {
            **dict(entry),
            "required_proof_fields": proof_fields,
            "entry_content_digest": entry_content_digest,
        }

    obligation = derive_atomic_binding_mode_obligation_set(
        bundle,
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
    )
    problems.extend(f"ATOMIC_BINDING_OBLIGATION:{x}" for x in obligation["problems"])
    expected = obligation["expected_members"]
    actual = sorted(entry_by_id)
    if expected != actual:
        problems.append("ATOMIC_BINDING_MODE_REGISTRY_SET_EQUALITY_FAILED")

    completeness = bundle.get("completeness_qualification")
    if not isinstance(completeness, Mapping):
        completeness = {}
        problems.append("ATOMIC_BINDING_MODE_COMPLETENESS_REQUIRED")
    else:
        generic = validate_registry_completeness_qualification(completeness)
        problems.extend(f"ATOMIC_BINDING_MODE_COMPLETENESS:{x}" for x in generic)
        if completeness.get("subject_object_id") != registry_id:
            problems.append("ATOMIC_BINDING_MODE_COMPLETENESS_SUBJECT_ID_MISMATCH")
        if completeness.get("subject_content_digest") != computed_registry_digest:
            problems.append("ATOMIC_BINDING_MODE_COMPLETENESS_SUBJECT_DIGEST_MISMATCH")
        if completeness.get("expected_members") != expected:
            problems.append("ATOMIC_BINDING_MODE_COMPLETENESS_EXPECTED_MEMBERS_MISMATCH")
        if completeness.get("actual_members") != actual:
            problems.append("ATOMIC_BINDING_MODE_COMPLETENESS_ACTUAL_MEMBERS_MISMATCH")
        if completeness.get("expected_member_set_digest") != obligation.get("expected_member_set_digest"):
            problems.append("ATOMIC_BINDING_MODE_COMPLETENESS_EXPECTED_DIGEST_MISMATCH")
        if completeness.get("result") != QUALIFIED:
            problems.append("ATOMIC_BINDING_MODE_COMPLETENESS_NOT_QUALIFIED")
        _close_completeness_dependencies(
            completeness,
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix="ATOMIC_BINDING_MODE_COMPLETENESS_PROOF",
            problems=problems,
        )

    binding_material = {
        "registry_id": registry_id,
        "registry_content_digest": computed_registry_digest,
        "registry_qualification_digest": registry.get("qualification_digest"),
        "registry_currentness_binding_digest": registry.get("currentness_binding_digest"),
        "entries": [entry_by_id[key] for key in sorted(entry_by_id)],
        "expected_members": expected,
        "actual_members": actual,
        "obligation_derivation_digest": obligation.get("derivation_digest"),
        "completeness_qualification_digest": completeness.get("qualification_digest") if isinstance(completeness, Mapping) else None,
    }
    result_digest = digest(binding_material)
    problems = sorted(set(problems))
    return {
        "state": "ATOMIC_BINDING_MODE_REGISTRY_QUALIFIED" if not problems else "ATOMIC_BINDING_MODE_REGISTRY_INVALID",
        "qualified": not problems,
        "registry_id": registry_id,
        "registry_content_digest": computed_registry_digest,
        "registry_qualification_digest": registry.get("qualification_digest"),
        "registry_currentness_binding_digest": registry.get("currentness_binding_digest"),
        "expected_members": expected,
        "actual_members": actual,
        "entries": entry_by_id,
        "registry_result_digest": result_digest,
        "registry_binding_material": binding_material,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_atomic_binding_proof(
    proof: Mapping[str, Any],
    *,
    registry_result: Mapping[str, Any],
    proof_context: Mapping[str, Any] | None = None,
    trusted_boundary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Accept only an exact proof object verified against a qualified registry result."""
    problems: list[str] = []
    material = registry_result.get("registry_binding_material")
    result_digest = registry_result.get("registry_result_digest")
    if not isinstance(material, Mapping):
        material = {}
        problems.append("ATOMIC_BINDING_PROOF_REGISTRY_BINDING_MATERIAL_REQUIRED")
    elif digest(material) != result_digest:
        problems.append("ATOMIC_BINDING_PROOF_REGISTRY_RESULT_DIGEST_MISMATCH")
    registry_result_id = registry_result.get("registry_result_id")
    registry_result_q = registry_result.get("registry_result_qualification_digest")
    if not _nonempty(registry_result_id):
        problems.append("ATOMIC_BINDING_PROOF_REGISTRY_RESULT_ID_REQUIRED")
    if not _sha(registry_result_q):
        problems.append("ATOMIC_BINDING_PROOF_REGISTRY_RESULT_QUALIFICATION_DIGEST_INVALID")
    _close(
        [
            {
                "kind": GOVERNED_QUALIFICATION,
                "reference_digest": registry_result_q,
                "subject_id": registry_result_id,
                "subject_content_digest": result_digest,
            }
        ],
        proof_context=proof_context,
        trusted_boundary=trusted_boundary,
        prefix="ATOMIC_BINDING_PROOF_REGISTRY_RESULT_PROOF",
        problems=problems,
    )
    if registry_result.get("qualified") is not True:
        problems.append("ATOMIC_BINDING_PROOF_REGISTRY_NOT_QUALIFIED")

    bound_entries_raw = material.get("entries")
    bound_entries: dict[str, Mapping[str, Any]] = {}
    if isinstance(bound_entries_raw, list):
        bound_entries = {
            entry.get("mode_id"): entry
            for entry in bound_entries_raw
            if isinstance(entry, Mapping) and _nonempty(entry.get("mode_id"))
        }
    else:
        problems.append("ATOMIC_BINDING_PROOF_BOUND_REGISTRY_ENTRIES_REQUIRED")
    caller_entries = registry_result.get("entries")
    if isinstance(caller_entries, Mapping) and set(caller_entries) != set(bound_entries):
        problems.append("ATOMIC_BINDING_PROOF_CALLER_REGISTRY_ENTRY_SET_MISMATCH")

    mode_id = proof.get("mode_id")
    if mode_id not in bound_entries:
        problems.append("ATOMIC_BINDING_PROOF_MODE_UNKNOWN_OR_UNREGISTERED")
        entry: Mapping[str, Any] = {}
    else:
        entry = bound_entries[mode_id]

    if proof.get("registry_content_digest") != material.get("registry_content_digest"):
        problems.append("ATOMIC_BINDING_PROOF_REGISTRY_DIGEST_MISMATCH")
    if proof.get("registry_result_digest") != result_digest:
        problems.append("ATOMIC_BINDING_PROOF_REGISTRY_RESULT_BINDING_MISMATCH")

    if entry:
        if canonical_mode_entry_content_digest(entry) != entry.get("entry_content_digest"):
            problems.append("ATOMIC_BINDING_PROOF_BOUND_ENTRY_CONTENT_DIGEST_MISMATCH")
        if proof.get("proof_schema_digest") != entry.get("proof_schema_digest"):
            problems.append("ATOMIC_BINDING_PROOF_SCHEMA_MISMATCH")
        if proof.get("verifier_mechanism_id") != entry.get("verifier_mechanism_id"):
            problems.append("ATOMIC_BINDING_PROOF_VERIFIER_MISMATCH")
        if proof.get("verifier_qualification_digest") != entry.get("verifier_qualification_digest"):
            problems.append("ATOMIC_BINDING_PROOF_VERIFIER_QUALIFICATION_MISMATCH")
        _close(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": entry.get("verifier_qualification_digest"),
                    "subject_id": entry.get("verifier_mechanism_id"),
                    "subject_content_digest": entry.get("verifier_mechanism_content_digest"),
                },
                {
                    "kind": CURRENTNESS_BINDING,
                    "reference_digest": entry.get("verifier_currentness_binding_digest"),
                    "source_id": entry.get("verifier_mechanism_id"),
                    "source_digest": entry.get("verifier_mechanism_content_digest"),
                },
            ],
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix="ATOMIC_BINDING_PROOF_VERIFIER_PROOF",
            problems=problems,
        )

        proof_fields = proof.get("proof_fields")
        if not isinstance(proof_fields, Mapping):
            proof_fields = {}
            problems.append("ATOMIC_BINDING_PROOF_FIELDS_REQUIRED")
        required = entry.get("required_proof_fields", [])
        for field in required:
            if field not in proof_fields or proof_fields.get(field) in (None, "", [], {}):
                problems.append(f"ATOMIC_BINDING_PROOF_FIELD_MISSING:{field}")
        extra = sorted(set(proof_fields) - set(required))
        if extra:
            problems.append("ATOMIC_BINDING_PROOF_UNDECLARED_FIELDS:" + ",".join(extra))
        expected_material_digest = digest(
            {
                "proof_id": proof.get("proof_id"),
                "mode_id": mode_id,
                "registry_content_digest": proof.get("registry_content_digest"),
                "registry_result_digest": proof.get("registry_result_digest"),
                "proof_schema_digest": proof.get("proof_schema_digest"),
                "verifier_mechanism_id": proof.get("verifier_mechanism_id"),
                "verifier_qualification_digest": proof.get("verifier_qualification_digest"),
                "proof_fields": {field: proof_fields.get(field) for field in required},
            }
        )
        if proof.get("proof_material_digest") != expected_material_digest:
            problems.append("ATOMIC_BINDING_PROOF_MATERIAL_DIGEST_MISMATCH")
        proof_id = proof.get("proof_id")
        if not _nonempty(proof_id):
            problems.append("ATOMIC_BINDING_PROOF_ID_REQUIRED")
        for key in ("proof_result_qualification_digest", "proof_currentness_binding_digest"):
            if not _sha(proof.get(key)):
                problems.append(f"ATOMIC_BINDING_PROOF_RESULT_PROOF_DIGEST_INVALID:{key}")
        _close(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": proof.get("proof_result_qualification_digest"),
                    "subject_id": proof_id,
                    "subject_content_digest": expected_material_digest,
                },
                {
                    "kind": CURRENTNESS_BINDING,
                    "reference_digest": proof.get("proof_currentness_binding_digest"),
                    "source_id": proof_id,
                    "source_digest": expected_material_digest,
                },
            ],
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix="ATOMIC_BINDING_PROOF_RESULT_PROOF",
            problems=problems,
        )

    problems = sorted(set(problems))
    return {
        "state": "ATOMIC_BINDING_PROOF_ACCEPTED" if not problems else "ATOMIC_BINDING_PROOF_REJECTED",
        "qualified": not problems,
        "mode_id": mode_id,
        "proof_material_digest": proof.get("proof_material_digest"),
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def construction_frontier() -> dict[str, Any]:
    return {
        "state": "V24_V6_R7_ATOMIC_BINDING_MODES_CONSTRUCTION_READY",
        "qualified": False,
        "implementation_workstream": "R7",
        "authority_effect": AUTHORITY_EFFECT,
    }
