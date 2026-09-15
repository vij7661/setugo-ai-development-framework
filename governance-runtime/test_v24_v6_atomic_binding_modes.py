from __future__ import annotations

import copy
import unittest

from v24_v6_governance_foundation import CURRENT, QUALIFIED, digest
from v24_v6_atomic_binding_modes import (
    canonical_contract_binding_digest,
    canonical_mechanism_binding_digest,
    canonical_mode_entry_content_digest,
    canonical_registry_content_digest,
    derive_atomic_binding_mode_obligation_set,
    validate_atomic_binding_mode_registry,
    validate_atomic_binding_proof,
)
from v24_v6_test_proof_context import build_test_proof_context

Q = "a" * 64
S = "b" * 64
REGISTRY_ID = "ATOMIC-BINDING-MODE-REGISTRY"
REGISTRY_RESULT_ID = "ATOMIC-BINDING-MODE-REGISTRY-RESULT"


def seal(record: dict, field: str) -> dict:
    material = dict(record)
    material.pop(field, None)
    record[field] = digest(material)
    return record


def currentness(source_id: str, source_digest: str, verifier_ref: str) -> dict:
    return seal(
        {
            "currentness_rule_id": "CURRENT-1",
            "source_object_id": source_id,
            "source_version_or_sequence": "1",
            "source_digest": source_digest,
            "verifier_qualification_digest": verifier_ref,
            "result": CURRENT,
            "observed_at_sequence": 1,
            "binding_digest": "",
        },
        "binding_digest",
    )


# Legacy label-only fixture retained for the permanent R7 RED regression.
def base_sources() -> dict:
    contracts = [
        {
            "contract_id": "EVAL-CONTRACT",
            "contract_digest": "1" * 64,
            "qualification_state": QUALIFIED,
            "authority_independence_state": QUALIFIED,
            "currentness_result": CURRENT,
            "control_domain_id": "DOMAIN-C1",
            "required_atomic_binding_mode_ids": ["SAME_AUTHORITATIVE_TRANSACTION"],
        },
        {
            "contract_id": "CONDITION-CONTRACT",
            "contract_digest": "2" * 64,
            "qualification_state": QUALIFIED,
            "authority_independence_state": QUALIFIED,
            "currentness_result": CURRENT,
            "control_domain_id": "DOMAIN-C2",
            "required_atomic_binding_mode_ids": ["CRYPTOGRAPHICALLY_BOUND_SNAPSHOT"],
        },
    ]
    mechanisms = [
        {
            "mechanism_id": "TX-MECHANISM",
            "mechanism_kind": "AUTHORITATIVE_TRANSACTION",
            "mechanism_digest": "3" * 64,
            "admission_state": QUALIFIED,
            "qualification_state": QUALIFIED,
            "authority_independence_state": QUALIFIED,
            "currentness_result": CURRENT,
            "control_domain_id": "DOMAIN-M1",
            "supported_atomic_binding_mode_ids": ["SAME_AUTHORITATIVE_TRANSACTION"],
        },
        {
            "mechanism_id": "SNAPSHOT-MECHANISM",
            "mechanism_kind": "CRYPTOGRAPHIC_SNAPSHOT",
            "mechanism_digest": "4" * 64,
            "admission_state": QUALIFIED,
            "qualification_state": QUALIFIED,
            "authority_independence_state": QUALIFIED,
            "currentness_result": CURRENT,
            "control_domain_id": "DOMAIN-M2",
            "supported_atomic_binding_mode_ids": ["CRYPTOGRAPHICALLY_BOUND_SNAPSHOT"],
        },
    ]
    return {"binding_contracts": contracts, "admitted_binding_mechanisms": mechanisms}


def _source_drafts_and_specs():
    contracts = [
        {
            "contract_id": "EVAL-CONTRACT",
            "contract_digest": "1" * 64,
            "authority_identity_id": "AUTH-EVAL-CONTRACT",
            "qualification_state": QUALIFIED,
            "authority_independence_state": QUALIFIED,
            "currentness_result": CURRENT,
            "control_domain_id": "DOMAIN-C1",
            "required_atomic_binding_mode_ids": ["SAME_AUTHORITATIVE_TRANSACTION"],
        },
        {
            "contract_id": "CONDITION-CONTRACT",
            "contract_digest": "2" * 64,
            "authority_identity_id": "AUTH-CONDITION-CONTRACT",
            "qualification_state": QUALIFIED,
            "authority_independence_state": QUALIFIED,
            "currentness_result": CURRENT,
            "control_domain_id": "DOMAIN-C2",
            "required_atomic_binding_mode_ids": ["CRYPTOGRAPHICALLY_BOUND_SNAPSHOT"],
        },
    ]
    mechanisms = [
        {
            "mechanism_id": "TX-MECHANISM",
            "mechanism_kind": "AUTHORITATIVE_TRANSACTION",
            "mechanism_digest": "3" * 64,
            "authority_identity_id": "AUTH-TX-MECHANISM",
            "admission_state": QUALIFIED,
            "qualification_state": QUALIFIED,
            "authority_independence_state": QUALIFIED,
            "currentness_result": CURRENT,
            "control_domain_id": "DOMAIN-M1",
            "supported_atomic_binding_mode_ids": ["SAME_AUTHORITATIVE_TRANSACTION"],
        },
        {
            "mechanism_id": "SNAPSHOT-MECHANISM",
            "mechanism_kind": "CRYPTOGRAPHIC_SNAPSHOT",
            "mechanism_digest": "4" * 64,
            "authority_identity_id": "AUTH-SNAPSHOT-MECHANISM",
            "admission_state": QUALIFIED,
            "qualification_state": QUALIFIED,
            "authority_independence_state": QUALIFIED,
            "currentness_result": CURRENT,
            "control_domain_id": "DOMAIN-M2",
            "supported_atomic_binding_mode_ids": ["CRYPTOGRAPHICALLY_BOUND_SNAPSHOT"],
        },
    ]
    specs = {}
    for index, contract in enumerate(contracts, 1):
        binding = canonical_contract_binding_digest(contract)
        contract["binding_content_digest"] = binding
        specs[f"contract_{index}_q"] = {
            "kind": "QUALIFICATION",
            "subject_id": contract["contract_id"],
            "content_digest": binding,
        }
        specs[f"contract_{index}_i"] = {
            "kind": "INDEPENDENCE",
            "subject_identity_id": contract["authority_identity_id"],
        }
        specs[f"contract_{index}_c"] = {
            "kind": "CURRENTNESS",
            "source_id": contract["contract_id"],
            "source_digest": binding,
        }
    for index, mechanism in enumerate(mechanisms, 1):
        binding = canonical_mechanism_binding_digest(mechanism)
        mechanism["binding_content_digest"] = binding
        specs[f"mechanism_{index}_admission_q"] = {
            "kind": "QUALIFICATION",
            "subject_id": mechanism["mechanism_id"],
            "content_digest": binding,
        }
        specs[f"mechanism_{index}_q"] = {
            "kind": "QUALIFICATION",
            "subject_id": mechanism["mechanism_id"],
            "content_digest": binding,
        }
        specs[f"mechanism_{index}_i"] = {
            "kind": "INDEPENDENCE",
            "subject_identity_id": mechanism["authority_identity_id"],
        }
        specs[f"mechanism_{index}_c"] = {
            "kind": "CURRENTNESS",
            "source_id": mechanism["mechanism_id"],
            "source_digest": binding,
        }
    return {"binding_contracts": contracts, "admitted_binding_mechanisms": mechanisms}, specs


def _attach_source_refs(src: dict, refs: dict) -> None:
    for index, contract in enumerate(src["binding_contracts"], 1):
        contract.update(
            {
                "qualification_digest": refs[f"contract_{index}_q"],
                "authority_independence_qualification_digest": refs[f"contract_{index}_i"],
                "currentness_binding_digest": refs[f"contract_{index}_c"],
            }
        )
    for index, mechanism in enumerate(src["admitted_binding_mechanisms"], 1):
        mechanism.update(
            {
                "admission_qualification_digest": refs[f"mechanism_{index}_admission_q"],
                "qualification_digest": refs[f"mechanism_{index}_q"],
                "authority_independence_qualification_digest": refs[f"mechanism_{index}_i"],
                "currentness_binding_digest": refs[f"mechanism_{index}_c"],
            }
        )


def proof_closed_sources():
    src, specs = _source_drafts_and_specs()
    context, boundary, refs = build_test_proof_context(specs)
    _attach_source_refs(src, refs)
    return src, context, boundary, specs


def _entry(mode_id: str, schema: str, verifier_id: str, verifier_content: str, fields: list[str]):
    entry = {
        "mode_id": mode_id,
        "proof_schema_digest": schema,
        "verifier_mechanism_id": verifier_id,
        "verifier_mechanism_content_digest": verifier_content,
        "verifier_qualification_state": QUALIFIED,
        "currentness_result": CURRENT,
        "required_proof_fields": fields,
    }
    entry["entry_content_digest"] = canonical_mode_entry_content_digest(entry)
    return entry


def _completeness(registry_digest: str, expected: list[str], actual: list[str], refs: dict):
    graph = {
        "nodes": [
            {"node_id": REGISTRY_ID, "omission_sensitive": True},
            {
                "node_id": "ROOT-CONTRACTS",
                "omission_sensitive": False,
                "root_kind": "NORMATIVE_ARTIFACT_BYTES_STRUCTURE",
                "source_surface_digest": "5" * 64,
            },
            {
                "node_id": "ROOT-MECHANISMS",
                "omission_sensitive": False,
                "root_kind": "CONTROL_PLANE_OBSERVATION",
                "source_surface_digest": "6" * 64,
            },
        ],
        "edges": [
            {"from": REGISTRY_ID, "to": "ROOT-CONTRACTS"},
            {"from": REGISTRY_ID, "to": "ROOT-MECHANISMS"},
        ],
    }
    record = {
        "subject_object_id": REGISTRY_ID,
        "subject_content_digest": registry_digest,
        "expected_member_set_digest": digest(sorted(expected)),
        "actual_member_set_digest": digest(sorted(actual)),
        "set_equality_proof_digest": digest({"expected": sorted(expected), "actual": sorted(actual)}),
        "verifier_qualification_digest": refs["completeness_q"],
        "expected_members": sorted(expected),
        "actual_members": sorted(actual),
        "completeness_derivation_graph": graph,
        "derivation_mechanism_qualification_digests": [refs["completeness_q"]],
        "derivation_authority_independence_digests": [refs["completeness_i"]],
        "source_surface_digests": ["5" * 64, "6" * 64],
        "currentness_bindings": [currentness(REGISTRY_ID, registry_digest, refs["completeness_q"])],
        "result": QUALIFIED,
        "qualification_digest": "",
    }
    return seal(record, "qualification_digest")


def proof_closed_registry_fixture():
    src, specs = _source_drafts_and_specs()
    entries = [
        _entry(
            "SAME_AUTHORITATIVE_TRANSACTION",
            S,
            "VERIFY-TX",
            "7" * 64,
            ["transaction_id", "transaction_commit_digest", "evaluation_digest", "condition_digest"],
        ),
        _entry(
            "CRYPTOGRAPHICALLY_BOUND_SNAPSHOT",
            "d" * 64,
            "VERIFY-SNAPSHOT",
            "8" * 64,
            ["snapshot_digest", "snapshot_source_qualification_digest", "evaluation_digest", "condition_digest"],
        ),
    ]
    registry = {
        "registry_id": REGISTRY_ID,
        "entries": entries,
        "qualification_state": QUALIFIED,
        "currentness_result": CURRENT,
    }
    registry["content_digest"] = canonical_registry_content_digest(registry)
    for index, entry in enumerate(entries, 1):
        specs[f"verifier_{index}_q"] = {
            "kind": "QUALIFICATION",
            "subject_id": entry["verifier_mechanism_id"],
            "content_digest": entry["verifier_mechanism_content_digest"],
        }
        specs[f"verifier_{index}_c"] = {
            "kind": "CURRENTNESS",
            "source_id": entry["verifier_mechanism_id"],
            "source_digest": entry["verifier_mechanism_content_digest"],
        }
    specs["registry_q"] = {
        "kind": "QUALIFICATION",
        "subject_id": REGISTRY_ID,
        "content_digest": registry["content_digest"],
    }
    specs["registry_c"] = {
        "kind": "CURRENTNESS",
        "source_id": REGISTRY_ID,
        "source_digest": registry["content_digest"],
    }
    specs["completeness_q"] = {
        "kind": "QUALIFICATION",
        "subject_id": "ATOMIC-COMPLETENESS-VERIFIER",
        "content_digest": "9" * 64,
    }
    specs["completeness_i"] = {
        "kind": "INDEPENDENCE",
        "subject_identity_id": "ATOMIC-COMPLETENESS-AUTHORITY",
    }
    context, boundary, refs = build_test_proof_context(specs)
    _attach_source_refs(src, refs)
    for index, entry in enumerate(entries, 1):
        entry["verifier_qualification_digest"] = refs[f"verifier_{index}_q"]
        entry["verifier_currentness_binding_digest"] = refs[f"verifier_{index}_c"]
    registry["qualification_digest"] = refs["registry_q"]
    registry["currentness_binding_digest"] = refs["registry_c"]
    obligation = derive_atomic_binding_mode_obligation_set(src, proof_context=context, trusted_boundary=boundary)
    assert obligation["qualified"], obligation["problems"]
    actual = sorted(entry["mode_id"] for entry in entries)
    completeness = _completeness(registry["content_digest"], obligation["expected_members"], actual, refs)
    return {**src, "registry": registry, "completeness_qualification": completeness}, context, boundary, specs


def qualified_registry_result():
    bundle, context, boundary, specs = proof_closed_registry_fixture()
    result = validate_atomic_binding_mode_registry(bundle, proof_context=context, trusted_boundary=boundary)
    assert result["qualified"], result["problems"]
    extended = dict(specs)
    extended["registry_result_q"] = {
        "kind": "QUALIFICATION",
        "subject_id": REGISTRY_RESULT_ID,
        "content_digest": result["registry_result_digest"],
    }
    context, boundary, refs = build_test_proof_context(extended)
    result = validate_atomic_binding_mode_registry(bundle, proof_context=context, trusted_boundary=boundary)
    assert result["qualified"], result["problems"]
    result = dict(result)
    result["registry_result_id"] = REGISTRY_RESULT_ID
    result["registry_result_qualification_digest"] = refs["registry_result_q"]
    return bundle, result, context, boundary, extended


def _proof_fields(mode_id: str):
    if mode_id == "SAME_AUTHORITATIVE_TRANSACTION":
        return {
            "transaction_id": "TX-1",
            "transaction_commit_digest": "f" * 64,
            "evaluation_digest": "1" * 64,
            "condition_digest": "2" * 64,
        }
    return {
        "snapshot_digest": "3" * 64,
        "snapshot_source_qualification_digest": "4" * 64,
        "evaluation_digest": "1" * 64,
        "condition_digest": "2" * 64,
    }


def proof_and_registry(mode_id: str = "SAME_AUTHORITATIVE_TRANSACTION"):
    bundle, rr, context, boundary, specs = qualified_registry_result()
    entry = rr["entries"][mode_id]
    fields = _proof_fields(mode_id)
    proof = {
        "proof_id": f"ATOMIC-PROOF-{mode_id}",
        "mode_id": mode_id,
        "registry_content_digest": rr["registry_content_digest"],
        "registry_result_digest": rr["registry_result_digest"],
        "proof_schema_digest": entry["proof_schema_digest"],
        "verifier_mechanism_id": entry["verifier_mechanism_id"],
        "verifier_qualification_digest": entry["verifier_qualification_digest"],
        "proof_fields": fields,
    }
    proof["proof_material_digest"] = digest(
        {
            "proof_id": proof["proof_id"],
            "mode_id": mode_id,
            "registry_content_digest": proof["registry_content_digest"],
            "registry_result_digest": proof["registry_result_digest"],
            "proof_schema_digest": proof["proof_schema_digest"],
            "verifier_mechanism_id": proof["verifier_mechanism_id"],
            "verifier_qualification_digest": proof["verifier_qualification_digest"],
            "proof_fields": {field: fields.get(field) for field in entry["required_proof_fields"]},
        }
    )
    extended = dict(specs)
    extended["proof_q"] = {
        "kind": "QUALIFICATION",
        "subject_id": proof["proof_id"],
        "content_digest": proof["proof_material_digest"],
    }
    extended["proof_c"] = {
        "kind": "CURRENTNESS",
        "source_id": proof["proof_id"],
        "source_digest": proof["proof_material_digest"],
    }
    context, boundary, refs = build_test_proof_context(extended)
    rr = validate_atomic_binding_mode_registry(bundle, proof_context=context, trusted_boundary=boundary)
    assert rr["qualified"], rr["problems"]
    rr = dict(rr)
    rr["registry_result_id"] = REGISTRY_RESULT_ID
    rr["registry_result_qualification_digest"] = refs["registry_result_q"]
    proof["proof_result_qualification_digest"] = refs["proof_q"]
    proof["proof_currentness_binding_digest"] = refs["proof_c"]
    return proof, rr, context, boundary


class AtomicObligationTests(unittest.TestCase):
    def test_obligation_set_positive(self):
        b, c, t, _ = proof_closed_sources()
        r = derive_atomic_binding_mode_obligation_set(b, proof_context=c, trusted_boundary=t)
        self.assertTrue(r["qualified"], r["problems"])
        self.assertEqual(["CRYPTOGRAPHICALLY_BOUND_SNAPSHOT", "SAME_AUTHORITATIVE_TRANSACTION"], r["expected_members"])

    def test_opaque_sources_without_proof_context_block(self):
        r = derive_atomic_binding_mode_obligation_set(base_sources())
        self.assertFalse(r["qualified"])
        self.assertTrue(any("PROOF" in p or "AUTHORITY_ID_REQUIRED" in p for p in r["problems"]))

    def test_contract_mode_omitted_by_mechanisms_blocks(self):
        b, c, t, _ = proof_closed_sources(); b["admitted_binding_mechanisms"][1]["supported_atomic_binding_mode_ids"] = ["SAME_AUTHORITATIVE_TRANSACTION"]
        r = derive_atomic_binding_mode_obligation_set(b, proof_context=c, trusted_boundary=t)
        self.assertIn("ATOMIC_BINDING_MODE_REQUIRED_BUT_UNSUPPORTED:CRYPTOGRAPHICALLY_BOUND_SNAPSHOT", r["problems"])

    def test_mechanism_mode_absent_from_contracts_blocks(self):
        b, c, t, _ = proof_closed_sources(); b["binding_contracts"][1]["required_atomic_binding_mode_ids"] = ["SAME_AUTHORITATIVE_TRANSACTION"]
        r = derive_atomic_binding_mode_obligation_set(b, proof_context=c, trusted_boundary=t)
        self.assertIn("ATOMIC_BINDING_MODE_SUPPORTED_BUT_UNOBLIGATED:CRYPTOGRAPHICALLY_BOUND_SNAPSHOT", r["problems"])

    def test_stale_binding_contract_blocks(self):
        b, c, t, _ = proof_closed_sources(); b["binding_contracts"][0]["currentness_result"] = "STALE"
        r = derive_atomic_binding_mode_obligation_set(b, proof_context=c, trusted_boundary=t)
        self.assertTrue(any("CONTRACT_NOT_CURRENT" in p for p in r["problems"]))

    def test_mode_set_substitution_reusing_old_contract_proofs_blocks(self):
        b, c, t, _ = proof_closed_sources(); b["binding_contracts"][0]["required_atomic_binding_mode_ids"] = ["CRYPTOGRAPHICALLY_BOUND_SNAPSHOT"]
        r = derive_atomic_binding_mode_obligation_set(b, proof_context=c, trusted_boundary=t)
        self.assertIn("ATOMIC_BINDING_CONTRACT_CONTENT_DIGEST_MISMATCH:EVAL-CONTRACT", r["problems"])
        self.assertTrue(any("ATOMIC_BINDING_CONTRACT_PROOF:EVAL-CONTRACT" in p and "SUBJECT_CONTENT_DIGEST_MISMATCH" in p for p in r["problems"]))

    def test_admission_label_without_admission_proof_blocks(self):
        b, c, t, _ = proof_closed_sources(); b["admitted_binding_mechanisms"][0]["admission_qualification_digest"] = "0" * 64
        r = derive_atomic_binding_mode_obligation_set(b, proof_context=c, trusted_boundary=t)
        self.assertTrue(any("ATOMIC_BINDING_MECHANISM_PROOF:TX-MECHANISM" in p and "UNRESOLVED" in p for p in r["problems"]))


class AtomicRegistryTests(unittest.TestCase):
    def test_registry_positive(self):
        b, c, t, _ = proof_closed_registry_fixture(); r = validate_atomic_binding_mode_registry(b, proof_context=c, trusted_boundary=t)
        self.assertTrue(r["qualified"], r["problems"])

    def test_registry_without_proof_context_blocks(self):
        b, _, _, _ = proof_closed_registry_fixture(); r = validate_atomic_binding_mode_registry(b)
        self.assertFalse(r["qualified"]); self.assertTrue(any("TRUSTED_PROOF_BOUNDARY_REQUIRED" in p for p in r["problems"]))

    def test_registry_omitted_mode_blocks(self):
        b, c, t, _ = proof_closed_registry_fixture(); b["registry"]["entries"].pop()
        r = validate_atomic_binding_mode_registry(b, proof_context=c, trusted_boundary=t)
        self.assertIn("ATOMIC_BINDING_MODE_REGISTRY_SET_EQUALITY_FAILED", r["problems"])
        self.assertIn("ATOMIC_BINDING_MODE_REGISTRY_CONTENT_DIGEST_MISMATCH", r["problems"])

    def test_caller_only_extra_mode_blocks(self):
        b, c, t, _ = proof_closed_registry_fixture(); x = copy.deepcopy(b["registry"]["entries"][0]); x["mode_id"] = "CALLER_CUSTOM_MODE"; x["entry_content_digest"] = canonical_mode_entry_content_digest(x); b["registry"]["entries"].append(x)
        r = validate_atomic_binding_mode_registry(b, proof_context=c, trusted_boundary=t)
        self.assertIn("ATOMIC_BINDING_MODE_REGISTRY_SET_EQUALITY_FAILED", r["problems"])

    def test_stale_mode_verifier_blocks(self):
        b, c, t, _ = proof_closed_registry_fixture(); b["registry"]["entries"][0]["currentness_result"] = "STALE"
        r = validate_atomic_binding_mode_registry(b, proof_context=c, trusted_boundary=t)
        self.assertTrue(any("VERIFIER_NOT_CURRENT" in p for p in r["problems"]))

    def test_unqualified_mode_verifier_blocks(self):
        b, c, t, _ = proof_closed_registry_fixture(); b["registry"]["entries"][0]["verifier_qualification_state"] = "INVALID"
        r = validate_atomic_binding_mode_registry(b, proof_context=c, trusted_boundary=t)
        self.assertTrue(any("VERIFIER_NOT_QUALIFIED" in p for p in r["problems"]))

    def test_verifier_reference_substitution_blocks(self):
        b, c, t, _ = proof_closed_registry_fixture(); b["registry"]["entries"][0]["verifier_qualification_digest"] = "0" * 64
        r = validate_atomic_binding_mode_registry(b, proof_context=c, trusted_boundary=t)
        self.assertTrue(any("ATOMIC_BINDING_MODE_VERIFIER_PROOF:SAME_AUTHORITATIVE_TRANSACTION" in p and "UNRESOLVED" in p for p in r["problems"]))

    def test_completeness_opaque_reference_blocks(self):
        b, c, t, _ = proof_closed_registry_fixture(); b["completeness_qualification"]["verifier_qualification_digest"] = "0" * 64
        r = validate_atomic_binding_mode_registry(b, proof_context=c, trusted_boundary=t)
        self.assertTrue(any("ATOMIC_BINDING_MODE_COMPLETENESS_PROOF" in p and "UNRESOLVED" in p for p in r["problems"]))


class AtomicProofTests(unittest.TestCase):
    def test_registered_transaction_proof_accepted(self):
        p, rr, c, t = proof_and_registry(); r = validate_atomic_binding_proof(p, registry_result=rr, proof_context=c, trusted_boundary=t)
        self.assertTrue(r["qualified"], r["problems"])

    def test_registered_snapshot_proof_accepted(self):
        p, rr, c, t = proof_and_registry("CRYPTOGRAPHICALLY_BOUND_SNAPSHOT"); r = validate_atomic_binding_proof(p, registry_result=rr, proof_context=c, trusted_boundary=t)
        self.assertTrue(r["qualified"], r["problems"])

    def test_registry_result_must_be_qualified(self):
        p, rr, c, t = proof_and_registry(); rr.pop("registry_result_qualification_digest")
        r = validate_atomic_binding_proof(p, registry_result=rr, proof_context=c, trusted_boundary=t)
        self.assertTrue(any("ATOMIC_BINDING_PROOF_REGISTRY_RESULT_PROOF" in x or "REGISTRY_RESULT_QUALIFICATION_DIGEST_INVALID" in x for x in r["problems"]))

    def test_fabricated_registry_result_entries_do_not_override_bound_entries(self):
        p, rr, c, t = proof_and_registry(); fake = copy.deepcopy(rr["entries"]["SAME_AUTHORITATIVE_TRANSACTION"]); fake["proof_schema_digest"] = "0" * 64; rr["entries"]["SAME_AUTHORITATIVE_TRANSACTION"] = fake; p["proof_schema_digest"] = "0" * 64
        r = validate_atomic_binding_proof(p, registry_result=rr, proof_context=c, trusted_boundary=t)
        self.assertIn("ATOMIC_BINDING_PROOF_SCHEMA_MISMATCH", r["problems"])

    def test_unknown_caller_mode_rejected(self):
        p, rr, c, t = proof_and_registry(); p["mode_id"] = "CALLER_CUSTOM_MODE"
        r = validate_atomic_binding_proof(p, registry_result=rr, proof_context=c, trusted_boundary=t)
        self.assertIn("ATOMIC_BINDING_PROOF_MODE_UNKNOWN_OR_UNREGISTERED", r["problems"])

    def test_schema_substitution_rejected(self):
        p, rr, c, t = proof_and_registry(); p["proof_schema_digest"] = "0" * 64
        r = validate_atomic_binding_proof(p, registry_result=rr, proof_context=c, trusted_boundary=t)
        self.assertIn("ATOMIC_BINDING_PROOF_SCHEMA_MISMATCH", r["problems"])

    def test_missing_required_field_rejected(self):
        p, rr, c, t = proof_and_registry(); p["proof_fields"].pop("condition_digest")
        r = validate_atomic_binding_proof(p, registry_result=rr, proof_context=c, trusted_boundary=t)
        self.assertIn("ATOMIC_BINDING_PROOF_FIELD_MISSING:condition_digest", r["problems"])

    def test_material_digest_tamper_rejected(self):
        p, rr, c, t = proof_and_registry(); p["proof_fields"]["transaction_id"] = "TX-TAMPER"
        r = validate_atomic_binding_proof(p, registry_result=rr, proof_context=c, trusted_boundary=t)
        self.assertIn("ATOMIC_BINDING_PROOF_MATERIAL_DIGEST_MISMATCH", r["problems"])

    def test_self_consistent_proof_without_specific_result_qualification_blocks(self):
        p, rr, c, t = proof_and_registry(); p.pop("proof_result_qualification_digest")
        r = validate_atomic_binding_proof(p, registry_result=rr, proof_context=c, trusted_boundary=t)
        self.assertTrue(any("ATOMIC_BINDING_PROOF_RESULT_PROOF" in x or "RESULT_PROOF_DIGEST_INVALID" in x for x in r["problems"]))

    def test_proof_currentness_reference_substitution_blocks(self):
        p, rr, c, t = proof_and_registry(); p["proof_currentness_binding_digest"] = "0" * 64
        r = validate_atomic_binding_proof(p, registry_result=rr, proof_context=c, trusted_boundary=t)
        self.assertTrue(any("ATOMIC_BINDING_PROOF_RESULT_PROOF" in x and "UNRESOLVED" in x for x in r["problems"]))

    def test_registry_binding_material_tamper_blocks(self):
        p, rr, c, t = proof_and_registry(); rr["registry_binding_material"]["actual_members"] = ["SAME_AUTHORITATIVE_TRANSACTION"]
        r = validate_atomic_binding_proof(p, registry_result=rr, proof_context=c, trusted_boundary=t)
        self.assertIn("ATOMIC_BINDING_PROOF_REGISTRY_RESULT_DIGEST_MISMATCH", r["problems"])


if __name__ == "__main__":
    unittest.main()
