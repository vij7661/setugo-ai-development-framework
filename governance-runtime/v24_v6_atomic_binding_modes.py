"""V24 I11 V6 remediation R7: atomic-binding mode completeness and proof gating.

Construction-only implementation of V6 Section 13.  The registry is
omission-sensitive; callers cannot create authority by naming a mode.
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


def _without(record: Mapping[str, Any], *fields: str) -> dict[str, Any]:
    out = dict(record)
    for field in fields:
        out.pop(field, None)
    return out


def derive_atomic_binding_mode_obligation_set(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Derive exact atomic-mode obligations independently of the mode registry.

    Active condition/evaluation contracts and admitted transaction/snapshot
    mechanisms must independently expose the same complete mode set.  A mode
    missing on either side blocks qualification instead of silently shrinking
    the expected universe.
    """
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
        if record.get("qualification_state") != QUALIFIED:
            problems.append(f"ATOMIC_BINDING_CONTRACT_NOT_QUALIFIED:{cid}")
        if record.get("authority_independence_state") != QUALIFIED:
            problems.append(f"ATOMIC_BINDING_CONTRACT_NOT_INDEPENDENT:{cid}")
        if record.get("currentness_result") != CURRENT:
            problems.append(f"ATOMIC_BINDING_CONTRACT_NOT_CURRENT:{cid}")
        domain = record.get("control_domain_id")
        if not _nonempty(domain):
            problems.append(f"ATOMIC_BINDING_CONTRACT_CONTROL_DOMAIN_REQUIRED:{cid}")
        elif domain in contract_domains:
            problems.append(f"ATOMIC_BINDING_CONTRACT_CONTROL_DOMAIN_DUPLICATE:{domain}")
        else:
            contract_domains.add(domain)
        modes, mode_problems = _unique_strings(record.get("required_atomic_binding_mode_ids"))
        problems.extend(
            f"ATOMIC_BINDING_CONTRACT_MODES:{cid}:{problem}" for problem in mode_problems
        )
        if not modes:
            problems.append(f"ATOMIC_BINDING_CONTRACT_MODES_REQUIRED:{cid}")
        contract_modes.update(modes)
        canonical_contracts.append(
            {
                "contract_id": cid,
                "contract_digest": record.get("contract_digest"),
                "control_domain_id": domain,
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
        if record.get("mechanism_kind") not in {
            "AUTHORITATIVE_TRANSACTION",
            "CRYPTOGRAPHIC_SNAPSHOT",
        }:
            problems.append(f"ATOMIC_BINDING_MECHANISM_KIND_INVALID:{mid}")
        if not _sha(record.get("mechanism_digest")):
            problems.append(f"ATOMIC_BINDING_MECHANISM_DIGEST_INVALID:{mid}")
        if record.get("admission_state") != QUALIFIED:
            problems.append(f"ATOMIC_BINDING_MECHANISM_NOT_ADMITTED:{mid}")
        if record.get("qualification_state") != QUALIFIED:
            problems.append(f"ATOMIC_BINDING_MECHANISM_NOT_QUALIFIED:{mid}")
        if record.get("authority_independence_state") != QUALIFIED:
            problems.append(f"ATOMIC_BINDING_MECHANISM_NOT_INDEPENDENT:{mid}")
        if record.get("currentness_result") != CURRENT:
            problems.append(f"ATOMIC_BINDING_MECHANISM_NOT_CURRENT:{mid}")
        domain = record.get("control_domain_id")
        if not _nonempty(domain):
            problems.append(f"ATOMIC_BINDING_MECHANISM_CONTROL_DOMAIN_REQUIRED:{mid}")
        elif domain in mechanism_domains:
            problems.append(f"ATOMIC_BINDING_MECHANISM_CONTROL_DOMAIN_DUPLICATE:{domain}")
        else:
            mechanism_domains.add(domain)
        modes, mode_problems = _unique_strings(record.get("supported_atomic_binding_mode_ids"))
        problems.extend(
            f"ATOMIC_BINDING_MECHANISM_MODES:{mid}:{problem}" for problem in mode_problems
        )
        if not modes:
            problems.append(f"ATOMIC_BINDING_MECHANISM_MODES_REQUIRED:{mid}")
        mechanism_modes.update(modes)
        canonical_mechanisms.append(
            {
                "mechanism_id": mid,
                "mechanism_kind": record.get("mechanism_kind"),
                "mechanism_digest": record.get("mechanism_digest"),
                "control_domain_id": domain,
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
    problems = sorted(set(problems))
    return {
        "state": "ATOMIC_BINDING_MODE_OBLIGATION_SET_QUALIFIED" if not problems else "ATOMIC_BINDING_MODE_OBLIGATION_SET_INVALID",
        "qualified": not problems,
        "expected_members": expected,
        "expected_member_set_digest": digest(expected),
        "contract_mode_set_digest": digest(sorted(contract_modes)),
        "mechanism_mode_set_digest": digest(sorted(mechanism_modes)),
        "derivation_digest": digest(
            {
                "contracts": sorted(canonical_contracts, key=lambda x: x["contract_id"]),
                "mechanisms": sorted(canonical_mechanisms, key=lambda x: x["mechanism_id"]),
            }
        ),
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def _registry_content_digest(registry: Mapping[str, Any]) -> str:
    return digest(_without(registry, "content_digest"))


def validate_atomic_binding_mode_registry(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Validate omission-sensitive registry and current verifier proofs."""
    problems: list[str] = []
    registry = bundle.get("registry")
    if not isinstance(registry, Mapping):
        registry = {}
        problems.append("ATOMIC_BINDING_MODE_REGISTRY_REQUIRED")

    registry_id = registry.get("registry_id")
    if not _nonempty(registry_id):
        problems.append("ATOMIC_BINDING_MODE_REGISTRY_ID_REQUIRED")
    if registry.get("qualification_state") != QUALIFIED:
        problems.append("ATOMIC_BINDING_MODE_REGISTRY_NOT_QUALIFIED")
    if registry.get("currentness_result") != CURRENT:
        problems.append("ATOMIC_BINDING_MODE_REGISTRY_NOT_CURRENT")
    computed_registry_digest = _registry_content_digest(registry)
    if registry.get("content_digest") != computed_registry_digest:
        problems.append("ATOMIC_BINDING_MODE_REGISTRY_CONTENT_DIGEST_MISMATCH")

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
        if not _sha(entry.get("verifier_qualification_digest")):
            problems.append(f"ATOMIC_BINDING_MODE_VERIFIER_DIGEST_INVALID:{mode_id}")
        if entry.get("verifier_qualification_state") != QUALIFIED:
            problems.append(f"ATOMIC_BINDING_MODE_VERIFIER_NOT_QUALIFIED:{mode_id}")
        if entry.get("currentness_result") != CURRENT:
            problems.append(f"ATOMIC_BINDING_MODE_VERIFIER_NOT_CURRENT:{mode_id}")
        proof_fields, field_problems = _unique_strings(entry.get("required_proof_fields"))
        problems.extend(
            f"ATOMIC_BINDING_MODE_PROOF_FIELDS:{mode_id}:{problem}"
            for problem in field_problems
        )
        if not proof_fields:
            problems.append(f"ATOMIC_BINDING_MODE_PROOF_FIELDS_REQUIRED:{mode_id}")
        entry_by_id[mode_id] = {**dict(entry), "required_proof_fields": proof_fields}

    obligation = derive_atomic_binding_mode_obligation_set(bundle)
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
        if completeness.get("expected_member_set_digest") != obligation.get(
            "expected_member_set_digest"
        ):
            problems.append("ATOMIC_BINDING_MODE_COMPLETENESS_EXPECTED_DIGEST_MISMATCH")
        if completeness.get("result") != QUALIFIED:
            problems.append("ATOMIC_BINDING_MODE_COMPLETENESS_NOT_QUALIFIED")

    problems = sorted(set(problems))
    return {
        "state": "ATOMIC_BINDING_MODE_REGISTRY_QUALIFIED" if not problems else "ATOMIC_BINDING_MODE_REGISTRY_INVALID",
        "qualified": not problems,
        "registry_id": registry_id,
        "registry_content_digest": computed_registry_digest,
        "expected_members": expected,
        "actual_members": actual,
        "entries": entry_by_id,
        "problems": problems,
        "authority_effect": AUTHORITY_EFFECT,
    }


def validate_atomic_binding_proof(
    proof: Mapping[str, Any], *, registry_result: Mapping[str, Any]
) -> dict[str, Any]:
    """A proof is authoritative only through an exact current registered mode."""
    problems: list[str] = []
    if registry_result.get("qualified") is not True:
        problems.append("ATOMIC_BINDING_PROOF_REGISTRY_NOT_QUALIFIED")
    mode_id = proof.get("mode_id")
    entries = registry_result.get("entries")
    if not isinstance(entries, Mapping) or mode_id not in entries:
        problems.append("ATOMIC_BINDING_PROOF_MODE_UNKNOWN_OR_UNREGISTERED")
        entry: Mapping[str, Any] = {}
    else:
        entry = entries[mode_id]

    if proof.get("registry_content_digest") != registry_result.get("registry_content_digest"):
        problems.append("ATOMIC_BINDING_PROOF_REGISTRY_DIGEST_MISMATCH")
    if entry:
        if proof.get("proof_schema_digest") != entry.get("proof_schema_digest"):
            problems.append("ATOMIC_BINDING_PROOF_SCHEMA_MISMATCH")
        if proof.get("verifier_mechanism_id") != entry.get("verifier_mechanism_id"):
            problems.append("ATOMIC_BINDING_PROOF_VERIFIER_MISMATCH")
        if proof.get("verifier_qualification_digest") != entry.get(
            "verifier_qualification_digest"
        ):
            problems.append("ATOMIC_BINDING_PROOF_VERIFIER_QUALIFICATION_MISMATCH")
        if entry.get("verifier_qualification_state") != QUALIFIED:
            problems.append("ATOMIC_BINDING_PROOF_VERIFIER_NOT_QUALIFIED")
        if entry.get("currentness_result") != CURRENT:
            problems.append("ATOMIC_BINDING_PROOF_VERIFIER_NOT_CURRENT")

        material = proof.get("proof_fields")
        if not isinstance(material, Mapping):
            material = {}
            problems.append("ATOMIC_BINDING_PROOF_FIELDS_REQUIRED")
        required = entry.get("required_proof_fields", [])
        for field in required:
            if field not in material or material.get(field) in (None, "", [], {}):
                problems.append(f"ATOMIC_BINDING_PROOF_FIELD_MISSING:{field}")
        extra = sorted(set(material) - set(required))
        if extra:
            problems.append("ATOMIC_BINDING_PROOF_UNDECLARED_FIELDS:" + ",".join(extra))
        expected_material_digest = digest(
            {
                "mode_id": mode_id,
                "registry_content_digest": proof.get("registry_content_digest"),
                "proof_schema_digest": proof.get("proof_schema_digest"),
                "verifier_mechanism_id": proof.get("verifier_mechanism_id"),
                "verifier_qualification_digest": proof.get("verifier_qualification_digest"),
                "proof_fields": {field: material.get(field) for field in required},
            }
        )
        if proof.get("proof_material_digest") != expected_material_digest:
            problems.append("ATOMIC_BINDING_PROOF_MATERIAL_DIGEST_MISMATCH")

    problems = sorted(set(problems))
    return {
        "state": "ATOMIC_BINDING_PROOF_ACCEPTED" if not problems else "ATOMIC_BINDING_PROOF_REJECTED",
        "qualified": not problems,
        "mode_id": mode_id,
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
