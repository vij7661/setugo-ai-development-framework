from __future__ import annotations

import copy
import unittest

from v24_v6_governance_foundation import CURRENT, QUALIFIED, digest
from v24_v6_effect_ledger_closure import (
    derive_effect_class_obligation_set,
    validate_durable_governance_ledger,
    validate_effect_class_registry,
    validate_effect_path_against_registry,
)

H = "a" * 64
Q = "b" * 64
E = "c" * 64


def seal(record: dict, field: str) -> dict:
    material = dict(record)
    material.pop(field, None)
    record[field] = digest(material)
    return record


def currentness(source_id: str, source_digest: str) -> dict:
    r = {
        "currentness_rule_id": "CURRENT-RULE-1",
        "source_object_id": source_id,
        "source_version_or_sequence": "1",
        "source_digest": source_digest,
        "verifier_qualification_digest": Q,
        "result": CURRENT,
        "observed_at_sequence": 1,
        "binding_digest": "",
    }
    return seal(r, "binding_digest")


def durable_ledger(kind: str = "MATERIAL_OBSERVATION") -> dict:
    genesis = "0" * 64
    r1 = {
        "record_id": "R-1",
        "ledger_kind": kind,
        "sequence": 1,
        "predecessor_record_digest": genesis,
        "producer_identity_id": "PRODUCER-1",
        "producer_control_domain_id": "DOMAIN-P",
        "evidence_class_id": "EVIDENCE-1",
        "event_or_subject_id": "SUBJECT-1",
        "event_digest": E,
        "record_digest": "",
    }
    seal(r1, "record_digest")
    record_digests = [r1["record_digest"]]
    head = {
        "ledger_id": f"LEDGER-{kind}",
        "ledger_kind": kind,
        "operator_identity_id": "OPERATOR-1",
        "operator_control_domain_id": "DOMAIN-OP",
        "durable_storage_identity": "STORE-1",
        "durable_storage_class": "DURABLE_APPEND_ONLY",
        "durable_anchor_identity": "ANCHOR-1",
        "durable_anchor_class": "INDEPENDENT_DURABLE_ANCHOR",
        "durable_anchor_digest": H,
        "anchor_sequence": 1,
        "latest_sequence": 1,
        "latest_record_digest": r1["record_digest"],
        "cumulative_root_digest": digest(record_digests),
        "fork_or_rollback_detected": False,
        "head_qualification_state": QUALIFIED,
        "currentness_result": CURRENT,
        "head_digest": "",
        "witness_currentness_records": [],
    }
    head_material = dict(head)
    head_material.pop("head_digest")
    head_material.pop("witness_currentness_records")
    head["head_digest"] = digest(head_material)
    witness = {
        "witness_identity_id": "WITNESS-1",
        "witness_control_domain_id": "DOMAIN-W",
        "evidence_class_id": "WITNESS-EVIDENCE",
        "currentness_rule_id": "WITNESS-CURRENT-RULE",
        "independence_qualification_digest": Q,
        "observed_head_digest": head["head_digest"],
        "observed_sequence": 1,
        "currentness_result": CURRENT,
        "independence_result": QUALIFIED,
        "witness_record_digest": "",
    }
    seal(witness, "witness_record_digest")
    head["witness_currentness_records"] = [witness]
    return {"genesis_predecessor_digest": genesis, "records": [r1], "head": head}


def derivations(observation_head: str, extra_effect: str | None = None) -> list[dict]:
    members = ["STATE_WRITE", "REMOTE_EFFECT"]
    values = []
    for idx, source in enumerate(
        ("IMPLEMENTATION_ARTIFACT", "DEPLOYMENT_ARTIFACT", "EFFECT_OBSERVATION"), 1
    ):
        effect_ids = list(members)
        if extra_effect and source == "EFFECT_OBSERVATION":
            effect_ids.append(extra_effect)
        values.append(
            {
                "derivation_id": f"DERIVE-{idx}",
                "source_surface_class": source,
                "source_surface_digest": chr(96 + idx) * 64,
                "derivation_mechanism_qualification_digest": Q,
                "derivation_authority_independence_digest": E,
                "mechanism_qualification_state": QUALIFIED,
                "authority_independence_state": QUALIFIED,
                "currentness_result": CURRENT,
                "control_domain_id": f"DOMAIN-D{idx}",
                "observation_head_digest": observation_head if source == "EFFECT_OBSERVATION" else None,
                "effect_class_ids": effect_ids,
            }
        )
    return values


def completeness(registry_id: str, registry_digest: str, expected: list[str], actual: list[str]) -> dict:
    roots = [
        {
            "node_id": "ROOT-I",
            "omission_sensitive": False,
            "root_kind": "IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY",
            "source_surface_digest": "1" * 64,
        },
        {
            "node_id": "ROOT-D",
            "omission_sensitive": False,
            "root_kind": "IMPLEMENTATION_DEPLOYMENT_ARTIFACT_INVENTORY",
            "source_surface_digest": "2" * 64,
        },
        {
            "node_id": "ROOT-E",
            "omission_sensitive": False,
            "root_kind": "EFFECT_PATH_OBSERVATION",
            "source_surface_digest": "3" * 64,
        },
    ]
    graph = {
        "nodes": [
            {"node_id": registry_id, "omission_sensitive": True},
            *roots,
        ],
        "edges": [
            {"from": registry_id, "to": "ROOT-I"},
            {"from": registry_id, "to": "ROOT-D"},
            {"from": registry_id, "to": "ROOT-E"},
        ],
    }
    rec = {
        "subject_object_id": registry_id,
        "subject_content_digest": registry_digest,
        "expected_member_set_digest": digest(sorted(expected)),
        "actual_member_set_digest": digest(sorted(actual)),
        "set_equality_proof_digest": digest({"expected": sorted(expected), "actual": sorted(actual)}),
        "verifier_qualification_digest": Q,
        "expected_members": sorted(expected),
        "actual_members": sorted(actual),
        "completeness_derivation_graph": graph,
        "derivation_mechanism_qualification_digests": ["4" * 64],
        "derivation_authority_independence_digests": ["5" * 64],
        "source_surface_digests": ["1" * 64, "2" * 64, "3" * 64],
        "currentness_bindings": [currentness(registry_id, registry_digest)],
        "result": QUALIFIED,
        "qualification_digest": "",
    }
    return seal(rec, "qualification_digest")


def registry_bundle(extra_observed: str | None = None) -> dict:
    obs_head = "9" * 64
    ds = derivations(obs_head, extra_observed)
    obligation = derive_effect_class_obligation_set(ds, current_observation_head_digest=obs_head)
    actual = ["REMOTE_EFFECT", "STATE_WRITE"]
    entries = [
        {
            "effect_class_id": cid,
            "proof_schema_digest": H,
            "verifier_mechanism_id": f"VERIFY-{cid}",
            "verifier_qualification_digest": Q,
            "verifier_qualification_state": QUALIFIED,
            "currentness_result": CURRENT,
        }
        for cid in actual
    ]
    registry = {
        "registry_id": "EFFECT-CLASS-REGISTRY",
        "entries": entries,
        "currentness_result": CURRENT,
        "qualification_state": QUALIFIED,
        "content_digest": "",
    }
    material = dict(registry)
    material.pop("content_digest")
    registry["content_digest"] = digest(material)
    cq = completeness(
        registry["registry_id"],
        registry["content_digest"],
        obligation["expected_members"],
        actual,
    )
    return {
        "registry": registry,
        "derivations": ds,
        "current_observation_head_digest": obs_head,
        "completeness_qualification": cq,
    }


def effect_path(effect_class_id: str = "STATE_WRITE") -> dict:
    return {
        "path_id": "PATH-1",
        "source_or_writer_id": "WRITER-1",
        "sink_id": "SINK-1",
        "effect_class_id": effect_class_id,
        "writer_admission_digest": H,
        "capability_digest": Q,
        "guard_mechanism_digest": E,
        "sink_admitted_writer_set_digest": "d" * 64,
        "material_surface_membership_digest": "e" * 64,
        "observation_head_digest": "9" * 64,
        "writer_admission_state": QUALIFIED,
        "capability_state": QUALIFIED,
        "guard_qualification_state": QUALIFIED,
        "sink_admitted_writer_ids": ["WRITER-1"],
        "dependency_edge_digests": ["f" * 64],
        "control_plane_evidence_digests": ["8" * 64],
        "currentness_result": CURRENT,
    }


class DurableLedgerTests(unittest.TestCase):
    def test_material_observation_ledger_positive(self):
        r = validate_durable_governance_ledger(durable_ledger(), ledger_kind="MATERIAL_OBSERVATION")
        self.assertTrue(r["qualified"], r["problems"])

    def test_completeness_ledger_positive(self):
        r = validate_durable_governance_ledger(durable_ledger("COMPLETENESS"), ledger_kind="COMPLETENESS")
        self.assertTrue(r["qualified"], r["problems"])

    def test_process_memory_head_cannot_be_authoritative(self):
        b = durable_ledger(); b["head"]["durable_storage_class"] = "PROCESS_MEMORY"
        r = validate_durable_governance_ledger(b, ledger_kind="MATERIAL_OBSERVATION")
        self.assertFalse(r["qualified"]); self.assertIn("DURABLE_LEDGER_STORAGE_NOT_DURABLE", r["problems"])

    def test_unanchored_local_head_blocks(self):
        b = durable_ledger(); b["head"]["durable_anchor_class"] = "UNANCHORED_LOCAL"
        r = validate_durable_governance_ledger(b, ledger_kind="MATERIAL_OBSERVATION")
        self.assertFalse(r["qualified"]); self.assertIn("DURABLE_LEDGER_ANCHOR_NOT_DURABLE", r["problems"])

    def test_rollback_or_fork_blocks(self):
        b = durable_ledger(); b["head"]["fork_or_rollback_detected"] = True
        r = validate_durable_governance_ledger(b, ledger_kind="MATERIAL_OBSERVATION")
        self.assertFalse(r["qualified"]); self.assertIn("DURABLE_LEDGER_FORK_OR_ROLLBACK_DETECTED", r["problems"])

    def test_same_control_domain_witness_blocks(self):
        b = durable_ledger(); b["head"]["witness_currentness_records"][0]["witness_control_domain_id"] = "DOMAIN-OP"
        seal(b["head"]["witness_currentness_records"][0], "witness_record_digest")
        r = validate_durable_governance_ledger(b, ledger_kind="MATERIAL_OBSERVATION")
        self.assertFalse(r["qualified"]); self.assertIn("DURABLE_LEDGER_NO_QUALIFIED_INDEPENDENT_WITNESS", r["problems"])

    def test_stale_witness_blocks(self):
        b = durable_ledger(); b["head"]["witness_currentness_records"][0]["currentness_result"] = "STALE"
        seal(b["head"]["witness_currentness_records"][0], "witness_record_digest")
        r = validate_durable_governance_ledger(b, ledger_kind="MATERIAL_OBSERVATION")
        self.assertFalse(r["qualified"]); self.assertIn("DURABLE_LEDGER_NO_QUALIFIED_INDEPENDENT_WITNESS", r["problems"])


class EffectClassTests(unittest.TestCase):
    def test_effect_class_registry_positive(self):
        r = validate_effect_class_registry(registry_bundle())
        self.assertTrue(r["qualified"], r["problems"])
        self.assertEqual(["REMOTE_EFFECT", "STATE_WRITE"], r["actual_members"])

    def test_missing_required_source_surface_blocks(self):
        b = registry_bundle(); b["derivations"] = b["derivations"][:-1]
        r = validate_effect_class_registry(b)
        self.assertFalse(r["qualified"])
        self.assertTrue(any("EFFECT_CLASS_REQUIRED_SOURCE_MISSING:EFFECT_OBSERVATION" in p for p in r["problems"]))

    def test_new_observed_effect_class_missing_from_registry_blocks(self):
        b = registry_bundle("UNREGISTERED_NEW_EFFECT")
        r = validate_effect_class_registry(b)
        self.assertFalse(r["qualified"])
        self.assertIn("EFFECT_CLASS_REGISTRY_SET_EQUALITY_FAILED", r["problems"])

    def test_registry_extra_caller_class_not_independently_observed_blocks(self):
        b = registry_bundle()
        b["registry"]["entries"].append(copy.deepcopy(b["registry"]["entries"][0]))
        b["registry"]["entries"][-1]["effect_class_id"] = "CALLER_ONLY"
        material = dict(b["registry"]); material.pop("content_digest")
        b["registry"]["content_digest"] = digest(material)
        r = validate_effect_class_registry(b)
        self.assertFalse(r["qualified"]); self.assertIn("EFFECT_CLASS_REGISTRY_SET_EQUALITY_FAILED", r["problems"])

    def test_stale_effect_class_verifier_blocks(self):
        b = registry_bundle(); b["registry"]["entries"][0]["currentness_result"] = "STALE"
        material = dict(b["registry"]); material.pop("content_digest")
        b["registry"]["content_digest"] = digest(material)
        r = validate_effect_class_registry(b)
        self.assertFalse(r["qualified"])
        self.assertTrue(any("EFFECT_CLASS_ENTRY_NOT_CURRENT" in p for p in r["problems"]))

    def test_registered_effect_path_classifies(self):
        b = registry_bundle(); rr = validate_effect_class_registry(b)
        r = validate_effect_path_against_registry(effect_path(), current_observation_head_digest="9" * 64, registry_result=rr)
        self.assertTrue(r["qualified"], r["problems"])

    def test_unregistered_effect_class_blocks_effect_path(self):
        b = registry_bundle(); rr = validate_effect_class_registry(b)
        r = validate_effect_path_against_registry(effect_path("UNKNOWN_EFFECT"), current_observation_head_digest="9" * 64, registry_result=rr)
        self.assertFalse(r["qualified"])
        self.assertIn("MATERIAL_EFFECT_PATH_EFFECT_CLASS_UNKNOWN_OR_UNREGISTERED", r["problems"])


if __name__ == "__main__":
    unittest.main()
