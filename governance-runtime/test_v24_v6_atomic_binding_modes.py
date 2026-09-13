from __future__ import annotations

import copy
import unittest

from v24_v6_governance_foundation import CURRENT, QUALIFIED, digest
from v24_v6_atomic_binding_modes import (
    derive_atomic_binding_mode_obligation_set,
    validate_atomic_binding_mode_registry,
    validate_atomic_binding_proof,
)

Q = "a" * 64
S = "b" * 64
V = "c" * 64


def seal(record: dict, field: str) -> dict:
    material = dict(record)
    material.pop(field, None)
    record[field] = digest(material)
    return record


def currentness(source_id: str, source_digest: str) -> dict:
    r = {
        "currentness_rule_id": "CURRENT-1",
        "source_object_id": source_id,
        "source_version_or_sequence": "1",
        "source_digest": source_digest,
        "verifier_qualification_digest": Q,
        "result": CURRENT,
        "observed_at_sequence": 1,
        "binding_digest": "",
    }
    return seal(r, "binding_digest")


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


def completeness(registry_id: str, registry_digest: str, expected: list[str], actual: list[str]) -> dict:
    graph = {
        "nodes": [
            {"node_id": registry_id, "omission_sensitive": True},
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
            {"from": registry_id, "to": "ROOT-CONTRACTS"},
            {"from": registry_id, "to": "ROOT-MECHANISMS"},
        ],
    }
    r = {
        "subject_object_id": registry_id,
        "subject_content_digest": registry_digest,
        "expected_member_set_digest": digest(sorted(expected)),
        "actual_member_set_digest": digest(sorted(actual)),
        "set_equality_proof_digest": digest({"expected": sorted(expected), "actual": sorted(actual)}),
        "verifier_qualification_digest": Q,
        "expected_members": sorted(expected),
        "actual_members": sorted(actual),
        "completeness_derivation_graph": graph,
        "derivation_mechanism_qualification_digests": ["7" * 64],
        "derivation_authority_independence_digests": ["8" * 64],
        "source_surface_digests": ["5" * 64, "6" * 64],
        "currentness_bindings": [currentness(registry_id, registry_digest)],
        "result": QUALIFIED,
        "qualification_digest": "",
    }
    return seal(r, "qualification_digest")


def registry_bundle() -> dict:
    src = base_sources()
    obligation = derive_atomic_binding_mode_obligation_set(src)
    entries = [
        {
            "mode_id": "SAME_AUTHORITATIVE_TRANSACTION",
            "proof_schema_digest": S,
            "verifier_mechanism_id": "VERIFY-TX",
            "verifier_qualification_digest": V,
            "verifier_qualification_state": QUALIFIED,
            "currentness_result": CURRENT,
            "required_proof_fields": [
                "transaction_id",
                "transaction_commit_digest",
                "evaluation_digest",
                "condition_digest",
                "decision_context_digest",
            ],
        },
        {
            "mode_id": "CRYPTOGRAPHICALLY_BOUND_SNAPSHOT",
            "proof_schema_digest": "d" * 64,
            "verifier_mechanism_id": "VERIFY-SNAPSHOT",
            "verifier_qualification_digest": "e" * 64,
            "verifier_qualification_state": QUALIFIED,
            "currentness_result": CURRENT,
            "required_proof_fields": [
                "snapshot_digest",
                "snapshot_source_qualification_digest",
                "evaluation_digest",
                "condition_digest",
                "decision_context_digest",
            ],
        },
    ]
    registry = {
        "registry_id": "ATOMIC-BINDING-MODE-REGISTRY",
        "entries": entries,
        "qualification_state": QUALIFIED,
        "currentness_result": CURRENT,
        "content_digest": "",
    }
    material = dict(registry); material.pop("content_digest")
    registry["content_digest"] = digest(material)
    actual = sorted(x["mode_id"] for x in entries)
    cq = completeness(
        registry["registry_id"], registry["content_digest"], obligation["expected_members"], actual
    )
    return {**src, "registry": registry, "completeness_qualification": cq}


def proof_for(bundle: dict, mode_id: str = "SAME_AUTHORITATIVE_TRANSACTION") -> dict:
    rr = validate_atomic_binding_mode_registry(bundle)
    entry = rr["entries"][mode_id]
    if mode_id == "SAME_AUTHORITATIVE_TRANSACTION":
        fields = {
            "transaction_id": "TX-1",
            "transaction_commit_digest": "f" * 64,
            "evaluation_digest": "1" * 64,
            "condition_digest": "2" * 64,
            "decision_context_digest": "6" * 64,
        }
    else:
        fields = {
            "snapshot_digest": "3" * 64,
            "snapshot_source_qualification_digest": "4" * 64,
            "evaluation_digest": "1" * 64,
            "condition_digest": "2" * 64,
            "decision_context_digest": "6" * 64,
        }
    p = {
        "mode_id": mode_id,
        "registry_content_digest": rr["registry_content_digest"],
        "proof_schema_digest": entry["proof_schema_digest"],
        "verifier_mechanism_id": entry["verifier_mechanism_id"],
        "verifier_qualification_digest": entry["verifier_qualification_digest"],
        "proof_fields": fields,
        "proof_material_digest": "",
    }
    p["proof_material_digest"] = digest(
        {
            "mode_id": mode_id,
            "registry_content_digest": p["registry_content_digest"],
            "proof_schema_digest": p["proof_schema_digest"],
            "verifier_mechanism_id": p["verifier_mechanism_id"],
            "verifier_qualification_digest": p["verifier_qualification_digest"],
            "proof_fields": {field: fields.get(field) for field in entry["required_proof_fields"]},
        }
    )
    return p


class AtomicObligationTests(unittest.TestCase):
    def test_obligation_set_positive(self):
        r = derive_atomic_binding_mode_obligation_set(base_sources())
        self.assertTrue(r["qualified"], r["problems"])
        self.assertEqual(
            ["CRYPTOGRAPHICALLY_BOUND_SNAPSHOT", "SAME_AUTHORITATIVE_TRANSACTION"],
            r["expected_members"],
        )

    def test_contract_mode_omitted_by_mechanisms_blocks(self):
        b = base_sources(); b["admitted_binding_mechanisms"][1]["supported_atomic_binding_mode_ids"] = ["SAME_AUTHORITATIVE_TRANSACTION"]
        r = derive_atomic_binding_mode_obligation_set(b)
        self.assertFalse(r["qualified"])
        self.assertIn("ATOMIC_BINDING_MODE_REQUIRED_BUT_UNSUPPORTED:CRYPTOGRAPHICALLY_BOUND_SNAPSHOT", r["problems"])

    def test_mechanism_mode_absent_from_contracts_blocks(self):
        b = base_sources(); b["binding_contracts"][1]["required_atomic_binding_mode_ids"] = ["SAME_AUTHORITATIVE_TRANSACTION"]
        r = derive_atomic_binding_mode_obligation_set(b)
        self.assertFalse(r["qualified"])
        self.assertIn("ATOMIC_BINDING_MODE_SUPPORTED_BUT_UNOBLIGATED:CRYPTOGRAPHICALLY_BOUND_SNAPSHOT", r["problems"])

    def test_stale_binding_contract_blocks(self):
        b = base_sources(); b["binding_contracts"][0]["currentness_result"] = "STALE"
        r = derive_atomic_binding_mode_obligation_set(b)
        self.assertFalse(r["qualified"])
        self.assertTrue(any("CONTRACT_NOT_CURRENT" in p for p in r["problems"]))


class AtomicRegistryTests(unittest.TestCase):
    def test_registry_positive(self):
        r = validate_atomic_binding_mode_registry(registry_bundle())
        self.assertTrue(r["qualified"], r["problems"])

    def test_registry_omitted_mode_blocks(self):
        b = registry_bundle(); b["registry"]["entries"].pop()
        material = dict(b["registry"]); material.pop("content_digest")
        b["registry"]["content_digest"] = digest(material)
        r = validate_atomic_binding_mode_registry(b)
        self.assertFalse(r["qualified"]); self.assertIn("ATOMIC_BINDING_MODE_REGISTRY_SET_EQUALITY_FAILED", r["problems"])

    def test_caller_only_extra_mode_blocks(self):
        b = registry_bundle(); x = copy.deepcopy(b["registry"]["entries"][0]); x["mode_id"] = "CALLER_CUSTOM_MODE"; b["registry"]["entries"].append(x)
        material = dict(b["registry"]); material.pop("content_digest")
        b["registry"]["content_digest"] = digest(material)
        r = validate_atomic_binding_mode_registry(b)
        self.assertFalse(r["qualified"]); self.assertIn("ATOMIC_BINDING_MODE_REGISTRY_SET_EQUALITY_FAILED", r["problems"])

    def test_stale_mode_verifier_blocks(self):
        b = registry_bundle(); b["registry"]["entries"][0]["currentness_result"] = "STALE"
        material = dict(b["registry"]); material.pop("content_digest")
        b["registry"]["content_digest"] = digest(material)
        r = validate_atomic_binding_mode_registry(b)
        self.assertFalse(r["qualified"]); self.assertTrue(any("VERIFIER_NOT_CURRENT" in p for p in r["problems"]))

    def test_unqualified_mode_verifier_blocks(self):
        b = registry_bundle(); b["registry"]["entries"][0]["verifier_qualification_state"] = "INVALID"
        material = dict(b["registry"]); material.pop("content_digest")
        b["registry"]["content_digest"] = digest(material)
        r = validate_atomic_binding_mode_registry(b)
        self.assertFalse(r["qualified"]); self.assertTrue(any("VERIFIER_NOT_QUALIFIED" in p for p in r["problems"]))


class AtomicProofTests(unittest.TestCase):
    def test_registered_transaction_proof_accepted(self):
        b = registry_bundle(); rr = validate_atomic_binding_mode_registry(b); p = proof_for(b)
        r = validate_atomic_binding_proof(p, registry_result=rr, expected_evaluation_digest=p.get("proof_fields", {}).get("evaluation_digest", "1"*64), expected_condition_digest=p.get("proof_fields", {}).get("condition_digest", "2"*64), expected_decision_context_digest=p.get("proof_fields", {}).get("decision_context_digest", "6"*64))
        self.assertTrue(r["qualified"], r["problems"])

    def test_registered_snapshot_proof_accepted(self):
        b = registry_bundle(); rr = validate_atomic_binding_mode_registry(b); p = proof_for(b, "CRYPTOGRAPHICALLY_BOUND_SNAPSHOT")
        r = validate_atomic_binding_proof(p, registry_result=rr, expected_evaluation_digest=p.get("proof_fields", {}).get("evaluation_digest", "1"*64), expected_condition_digest=p.get("proof_fields", {}).get("condition_digest", "2"*64), expected_decision_context_digest=p.get("proof_fields", {}).get("decision_context_digest", "6"*64))
        self.assertTrue(r["qualified"], r["problems"])

    def test_unknown_caller_mode_rejected(self):
        b = registry_bundle(); rr = validate_atomic_binding_mode_registry(b); p = proof_for(b); p["mode_id"] = "CALLER_CUSTOM_MODE"
        r = validate_atomic_binding_proof(p, registry_result=rr, expected_evaluation_digest=p.get("proof_fields", {}).get("evaluation_digest", "1"*64), expected_condition_digest=p.get("proof_fields", {}).get("condition_digest", "2"*64), expected_decision_context_digest=p.get("proof_fields", {}).get("decision_context_digest", "6"*64))
        self.assertFalse(r["qualified"]); self.assertIn("ATOMIC_BINDING_PROOF_MODE_UNKNOWN_OR_UNREGISTERED", r["problems"])

    def test_schema_substitution_rejected(self):
        b = registry_bundle(); rr = validate_atomic_binding_mode_registry(b); p = proof_for(b); p["proof_schema_digest"] = "0" * 64
        r = validate_atomic_binding_proof(p, registry_result=rr, expected_evaluation_digest=p.get("proof_fields", {}).get("evaluation_digest", "1"*64), expected_condition_digest=p.get("proof_fields", {}).get("condition_digest", "2"*64), expected_decision_context_digest=p.get("proof_fields", {}).get("decision_context_digest", "6"*64))
        self.assertFalse(r["qualified"]); self.assertIn("ATOMIC_BINDING_PROOF_SCHEMA_MISMATCH", r["problems"])

    def test_missing_required_field_rejected(self):
        b = registry_bundle(); rr = validate_atomic_binding_mode_registry(b); p = proof_for(b); p["proof_fields"].pop("condition_digest")
        r = validate_atomic_binding_proof(p, registry_result=rr, expected_evaluation_digest=p.get("proof_fields", {}).get("evaluation_digest", "1"*64), expected_condition_digest=p.get("proof_fields", {}).get("condition_digest", "2"*64), expected_decision_context_digest=p.get("proof_fields", {}).get("decision_context_digest", "6"*64))
        self.assertFalse(r["qualified"]); self.assertIn("ATOMIC_BINDING_PROOF_FIELD_MISSING:condition_digest", r["problems"])

    def test_material_digest_tamper_rejected(self):
        b = registry_bundle(); rr = validate_atomic_binding_mode_registry(b); p = proof_for(b); p["proof_fields"]["transaction_id"] = "TX-TAMPER"
        r = validate_atomic_binding_proof(p, registry_result=rr, expected_evaluation_digest=p.get("proof_fields", {}).get("evaluation_digest", "1"*64), expected_condition_digest=p.get("proof_fields", {}).get("condition_digest", "2"*64), expected_decision_context_digest=p.get("proof_fields", {}).get("decision_context_digest", "6"*64))
        self.assertFalse(r["qualified"]); self.assertIn("ATOMIC_BINDING_PROOF_MATERIAL_DIGEST_MISMATCH", r["problems"])



    def test_proof_cannot_be_replayed_for_different_evaluation(self):
        b = registry_bundle(); rr = validate_atomic_binding_mode_registry(b); p = proof_for(b)
        r = validate_atomic_binding_proof(
            p, registry_result=rr, expected_evaluation_digest="9" * 64,
            expected_condition_digest=p["proof_fields"]["condition_digest"],
            expected_decision_context_digest=p["proof_fields"]["decision_context_digest"],
        )
        self.assertFalse(r["qualified"]); self.assertIn("ATOMIC_BINDING_PROOF_EXACT_BINDING_MISMATCH:evaluation_digest", r["problems"])

    def test_proof_cannot_be_replayed_across_decision_context(self):
        b = registry_bundle(); rr = validate_atomic_binding_mode_registry(b); p = proof_for(b)
        r = validate_atomic_binding_proof(
            p, registry_result=rr, expected_evaluation_digest=p["proof_fields"]["evaluation_digest"],
            expected_condition_digest=p["proof_fields"]["condition_digest"],
            expected_decision_context_digest="9" * 64,
        )
        self.assertFalse(r["qualified"]); self.assertIn("ATOMIC_BINDING_PROOF_EXACT_BINDING_MISMATCH:decision_context_digest", r["problems"])

if __name__ == "__main__":
    unittest.main()
