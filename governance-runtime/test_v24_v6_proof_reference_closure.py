from __future__ import annotations

import copy
import os
import unittest

from v24_v6_governance_foundation import CURRENT, QUALIFIED, STALE, digest
from v24_v6_test_proof_context import record_test_attestation_inventory
from v24_v6_proof_reference_closure import (
    CURRENTNESS_BINDING,
    GOVERNED_QUALIFICATION,
    INDEPENDENCE_QUALIFICATION,
    PROOF_REFERENCE_CLOSED,
    TRUSTED_BOUNDARY_ANCHOR_ENV,
    close_governance_dependencies,
    resolve_currentness_binding,
    resolve_governed_qualification,
    resolve_independence_qualification,
    seal_proof_context,
    trusted_boundary_anchor_digest,
    validate_proof_context,
)

ROOT_CONTENT = "a" * 64
OTHER_ROOT_CONTENT = "b" * 64
TARGET_CONTENT = "c" * 64
IND_EVIDENCE_CONTENT = "d" * 64
CURRENT_SOURCE_CONTENT = "e" * 64
D1 = "1" * 64
D2 = "2" * 64
D3 = "3" * 64
D4 = "4" * 64
D5 = "5" * 64
D6 = "6" * 64
D7 = "7" * 64
D8 = "8" * 64
D9 = "9" * 64


def anchored_boundary_for(context: dict) -> dict:
    scope = context["genesis_trusted_scope"]
    boundary = {
        "governance_generation_id": context["governance_generation_id"],
        "expected_proof_context_digest": context["context_digest"],
        "expected_genesis_scope_digest": scope["scope_digest"],
    }
    os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = trusted_boundary_anchor_digest(boundary)
    record_test_attestation_inventory(context, boundary)
    return boundary


def seal(record: dict, field: str) -> dict:
    material = dict(record)
    material.pop(field, None)
    record[field] = digest(material)
    return record


def currentness(source_id: str, source_digest: str, verifier_ref: str) -> dict:
    return seal(
        {
            "currentness_rule_id": "CUR-V24",
            "source_object_id": source_id,
            "source_version_or_sequence": "1",
            "source_digest": source_digest,
            "observed_at_sequence": 2,
            "verifier_qualification_digest": verifier_ref,
            "result": CURRENT,
            "binding_digest": "",
        },
        "binding_digest",
    )


def genesis_scope() -> dict:
    trusted = [
        {"object_id": "ROOT-VERIFIER", "content_digest": ROOT_CONTENT},
        {"object_id": "OTHER-ROOT", "content_digest": OTHER_ROOT_CONTENT},
    ]
    return seal(
        {
            "governance_generation_id": "GEN-V24-PRC",
            "genesis_record_digest": D1,
            "root_kernel_digest": D2,
            "trusted_objects": trusted,
            "trusted_object_pair_set_digest": digest(
                sorted(trusted, key=lambda x: (x["object_id"], x["content_digest"]))
            ),
            "permitted_bootstrap_roles": ["BOOTSTRAP_VERIFIER"],
            "residual_trust_reason_ids": ["GENESIS_ROOT"],
            "creation_ceremony_digest": D3,
            "durable_anchor_digest": D4,
            "scope_digest": "",
        },
        "scope_digest",
    )


def root_qualification() -> dict:
    # Transitive references are deliberately opaque.  Exact paired genesis trust
    # is the only permitted recursion terminator and therefore makes these refs
    # non-load-bearing for this one root record.
    return seal(
        {
            "qualification_id": "Q-ROOT",
            "subject_object_id": "ROOT-VERIFIER",
            "subject_content_digest": ROOT_CONTENT,
            "subject_kind": "VERIFIER",
            "subject_owner_id": "ROOT-OWNER",
            "qualification_authority_id": "ROOT-AUTHORITY",
            "authority_member_ids": ["ROOT-MEMBER"],
            "authority_control_domain_ids": ["ROOT-DOMAIN"],
            "independence_qualification_digests": [D5],
            "evidence_record_digests": [D6],
            "evidence_class_ids": ["ROOT-EVIDENCE-CLASS"],
            "verifier_mechanism_id": "ROOT-BOOTSTRAP-VERIFIER",
            "verifier_mechanism_qualification_digest": D7,
            "currentness_bindings": [
                currentness("ROOT-VERIFIER", ROOT_CONTENT, D8)
            ],
            "result": QUALIFIED,
            "proof_digest": D9,
            "qualification_digest": "",
        },
        "qualification_digest",
    )


def independence(root_ref: str) -> dict:
    return seal(
        {
            "independence_qualification_id": "IND-LEAF-AUTHORITY",
            "independence_rule_id": "IND-RULE-V24",
            "subject_identity_id": "LEAF-AUTHORITY",
            "subject_control_closure": ["ORG:LEAF-AUTHORITY", "KMS:LEAF-AUTHORITY"],
            "counterparties": [
                {
                    "identity_id": "COUNTERPARTY-1",
                    "control_closure": ["ORG:EXTERNAL", "KMS:EXTERNAL"],
                }
            ],
            "shared_control_intersections": [],
            "evidence_record_digests": [D1],
            "currentness_bindings": [
                currentness("IND-EVIDENCE", IND_EVIDENCE_CONTENT, root_ref)
            ],
            "result": QUALIFIED,
            "verifier_qualification_digest": root_ref,
            "qualification_digest": "",
        },
        "qualification_digest",
    )


def leaf_qualification(root_ref: str, independence_ref: str) -> dict:
    return seal(
        {
            "qualification_id": "Q-TARGET",
            "subject_object_id": "TARGET-MECHANISM",
            "subject_content_digest": TARGET_CONTENT,
            "subject_kind": "AUTHORITY_BEARING_MECHANISM",
            "subject_owner_id": "TARGET-OWNER",
            "qualification_authority_id": "LEAF-AUTHORITY",
            "authority_member_ids": ["LEAF-MEMBER"],
            "authority_control_domain_ids": ["LEAF-DOMAIN"],
            "independence_qualification_digests": [independence_ref],
            "evidence_record_digests": [D2],
            "evidence_class_ids": ["TARGET-EVIDENCE-CLASS"],
            "verifier_mechanism_id": "ROOT-VERIFIER",
            "verifier_mechanism_qualification_digest": root_ref,
            "currentness_bindings": [
                currentness("TARGET-MECHANISM", TARGET_CONTENT, root_ref)
            ],
            "result": QUALIFIED,
            "proof_digest": D3,
            "qualification_digest": "",
        },
        "qualification_digest",
    )


def wrap(kind: str, record: dict) -> dict:
    field = "binding_digest" if kind == CURRENTNESS_BINDING else "qualification_digest"
    return {
        "record_kind": kind,
        "record_digest": record[field],
        "record": record,
    }


def proof_bundle() -> tuple[dict, dict, dict]:
    root = root_qualification()
    ind = independence(root["qualification_digest"])
    leaf = leaf_qualification(root["qualification_digest"], ind["qualification_digest"])
    standalone_currentness = currentness(
        "CURRENT-SOURCE", CURRENT_SOURCE_CONTENT, root["qualification_digest"]
    )
    context = {
        "proof_context_id": "CTX-V24-PRC-1",
        "governance_generation_id": "GEN-V24-PRC",
        "evidence_records": [
            wrap(GOVERNED_QUALIFICATION, root),
            wrap(INDEPENDENCE_QUALIFICATION, ind),
            wrap(GOVERNED_QUALIFICATION, leaf),
            wrap(CURRENTNESS_BINDING, standalone_currentness),
        ],
        "genesis_trusted_scope": genesis_scope(),
        "context_digest": "",
    }
    seal_proof_context(context)
    return context, anchored_boundary_for(context), {
        "root": root["qualification_digest"],
        "independence": ind["qualification_digest"],
        "leaf": leaf["qualification_digest"],
        "currentness": standalone_currentness["binding_digest"],
    }


def reseal_context(context: dict) -> tuple[dict, dict]:
    seal_proof_context(context)
    return context, anchored_boundary_for(context)


class V24V6ProofReferenceClosureTests(unittest.TestCase):
    def test_exact_proof_closed_path_passes(self):
        context, boundary, refs = proof_bundle()
        self.assertTrue(validate_proof_context(context, boundary)["qualified"])
        result = resolve_governed_qualification(
            refs["leaf"],
            context,
            boundary,
            expected_subject_id="TARGET-MECHANISM",
            expected_subject_content_digest=TARGET_CONTENT,
        )
        self.assertTrue(result["qualified"], result["problems"])
        self.assertEqual(result["state"], PROOF_REFERENCE_CLOSED)
        self.assertIn(refs["root"], result["resolved_digests"])
        self.assertIn(refs["independence"], result["resolved_digests"])
        self.assertIn(refs["leaf"], result["resolved_digests"])

    def test_unknown_qualification_digest_fails(self):
        context, boundary, _ = proof_bundle()
        result = resolve_governed_qualification(D9, context, boundary)
        self.assertFalse(result["qualified"])
        self.assertTrue(any("PROOF_REFERENCE_UNRESOLVED" in x for x in result["problems"]))

    def test_record_key_must_match_recomputed_self_digest(self):
        context, _, _ = proof_bundle()
        context = copy.deepcopy(context)
        context["evidence_records"][2]["record_digest"] = D9
        context, boundary = reseal_context(context)
        result = validate_proof_context(context, boundary)
        self.assertFalse(result["qualified"])
        self.assertTrue(
            any("KEY_SELF_DIGEST_MISMATCH" in x for x in result["problems"]),
            result["problems"],
        )

    def test_wrong_subject_id_fails(self):
        context, boundary, refs = proof_bundle()
        result = resolve_governed_qualification(
            refs["leaf"], context, boundary, expected_subject_id="OTHER-TARGET"
        )
        self.assertFalse(result["qualified"])
        self.assertTrue(any("SUBJECT_ID_MISMATCH" in x for x in result["problems"]))

    def test_wrong_subject_content_digest_fails(self):
        context, boundary, refs = proof_bundle()
        result = resolve_governed_qualification(
            refs["leaf"],
            context,
            boundary,
            expected_subject_content_digest=OTHER_ROOT_CONTENT,
        )
        self.assertFalse(result["qualified"])
        self.assertTrue(any("SUBJECT_DIGEST_MISMATCH" in x for x in result["problems"]))

    def test_nonqualified_record_fails(self):
        context, _, _ = proof_bundle()
        context = copy.deepcopy(context)
        wrapper = context["evidence_records"][2]
        record = wrapper["record"]
        record["result"] = "INVALID"
        seal(record, "qualification_digest")
        wrapper["record_digest"] = record["qualification_digest"]
        context, boundary = reseal_context(context)
        result = resolve_governed_qualification(
            wrapper["record_digest"], context, boundary
        )
        self.assertFalse(result["qualified"])
        self.assertTrue(any("NOT_QUALIFIED" in x for x in result["problems"]))

    def test_stale_embedded_currentness_fails(self):
        context, _, _ = proof_bundle()
        context = copy.deepcopy(context)
        wrapper = context["evidence_records"][2]
        record = wrapper["record"]
        binding = record["currentness_bindings"][0]
        binding["result"] = STALE
        seal(binding, "binding_digest")
        seal(record, "qualification_digest")
        wrapper["record_digest"] = record["qualification_digest"]
        context, boundary = reseal_context(context)
        result = resolve_governed_qualification(
            wrapper["record_digest"], context, boundary
        )
        self.assertFalse(result["qualified"])
        self.assertTrue(any("NONCURRENT" in x or "NOT_CURRENT" in x for x in result["problems"]))

    def test_currentness_wrong_source_fails(self):
        context, boundary, refs = proof_bundle()
        result = resolve_currentness_binding(
            refs["currentness"],
            context,
            boundary,
            expected_source_id="OTHER-SOURCE",
            expected_source_digest=CURRENT_SOURCE_CONTENT,
        )
        self.assertFalse(result["qualified"])
        self.assertTrue(any("SOURCE_ID_MISMATCH" in x for x in result["problems"]))

    def test_independence_shared_control_fails(self):
        context, _, _ = proof_bundle()
        context = copy.deepcopy(context)
        wrapper = context["evidence_records"][1]
        record = wrapper["record"]
        record["counterparties"][0]["control_closure"] = [
            "ORG:LEAF-AUTHORITY",
            "KMS:EXTERNAL",
        ]
        record["shared_control_intersections"] = ["ORG:LEAF-AUTHORITY"]
        seal(record, "qualification_digest")
        wrapper["record_digest"] = record["qualification_digest"]
        context, boundary = reseal_context(context)
        result = resolve_independence_qualification(
            wrapper["record_digest"], context, boundary
        )
        self.assertFalse(result["qualified"])
        self.assertTrue(any("SHARED_CONTROL" in x for x in result["problems"]))

    def test_independence_wrong_subject_fails(self):
        context, boundary, refs = proof_bundle()
        result = resolve_independence_qualification(
            refs["independence"],
            context,
            boundary,
            expected_subject_identity_id="OTHER-AUTHORITY",
        )
        self.assertFalse(result["qualified"])
        self.assertTrue(any("SUBJECT_ID_MISMATCH" in x for x in result["problems"]))

    def test_missing_verifier_qualification_fails(self):
        context, _, _ = proof_bundle()
        context = copy.deepcopy(context)
        wrapper = context["evidence_records"][2]
        record = wrapper["record"]
        record["verifier_mechanism_qualification_digest"] = D9
        seal(record, "qualification_digest")
        wrapper["record_digest"] = record["qualification_digest"]
        context, boundary = reseal_context(context)
        result = resolve_governed_qualification(
            wrapper["record_digest"], context, boundary
        )
        self.assertFalse(result["qualified"])
        self.assertTrue(any("UNRESOLVED" in x for x in result["problems"]))

    def test_exact_paired_genesis_terminates_recursion(self):
        context, boundary, refs = proof_bundle()
        result = resolve_governed_qualification(
            refs["root"],
            context,
            boundary,
            expected_subject_id="ROOT-VERIFIER",
            expected_subject_content_digest=ROOT_CONTENT,
        )
        self.assertTrue(result["qualified"], result["problems"])

    def test_genesis_cross_pair_does_not_terminate(self):
        context, _, _ = proof_bundle()
        context = copy.deepcopy(context)
        wrapper = context["evidence_records"][0]
        record = wrapper["record"]
        # ID is trusted in one pair and digest in another pair, but the composite
        # pair is not trusted.
        record["subject_content_digest"] = OTHER_ROOT_CONTENT
        record["currentness_bindings"][0]["source_digest"] = OTHER_ROOT_CONTENT
        seal(record["currentness_bindings"][0], "binding_digest")
        seal(record, "qualification_digest")
        wrapper["record_digest"] = record["qualification_digest"]
        context, boundary = reseal_context(context)
        result = resolve_governed_qualification(
            wrapper["record_digest"],
            context,
            boundary,
            expected_subject_id="ROOT-VERIFIER",
            expected_subject_content_digest=OTHER_ROOT_CONTENT,
        )
        self.assertFalse(result["qualified"])
        self.assertTrue(any("UNRESOLVED" in x for x in result["problems"]))

    def test_candidate_cannot_supply_missing_trusted_boundary(self):
        context, _, refs = proof_bundle()
        fake_candidate = {
            "governance_proof_context": context,
            "trusted_boundary": {
                "governance_generation_id": context["governance_generation_id"],
                "expected_proof_context_digest": context["context_digest"],
                "expected_genesis_scope_digest": context["genesis_trusted_scope"]["scope_digest"],
            },
        }
        self.assertIn("trusted_boundary", fake_candidate)
        result = resolve_governed_qualification(refs["leaf"], context, None)
        self.assertFalse(result["qualified"])
        self.assertIn("TRUSTED_PROOF_BOUNDARY_REQUIRED", result["problems"])

    def test_requirement_batch_closes_all_references(self):
        context, boundary, refs = proof_bundle()
        result = close_governance_dependencies(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": refs["leaf"],
                    "subject_id": "TARGET-MECHANISM",
                    "subject_content_digest": TARGET_CONTENT,
                },
                {
                    "kind": INDEPENDENCE_QUALIFICATION,
                    "reference_digest": refs["independence"],
                    "subject_identity_id": "LEAF-AUTHORITY",
                },
                {
                    "kind": CURRENTNESS_BINDING,
                    "reference_digest": refs["currentness"],
                    "source_id": "CURRENT-SOURCE",
                    "source_digest": CURRENT_SOURCE_CONTENT,
                },
            ],
            context,
            boundary,
        )
        self.assertTrue(result["qualified"], result["problems"])
        self.assertEqual(result["state"], PROOF_REFERENCE_CLOSED)

    def test_tampered_context_cannot_reuse_old_trusted_digest(self):
        context, boundary, refs = proof_bundle()
        tampered = copy.deepcopy(context)
        tampered["proof_context_id"] = "CTX-TAMPERED"
        seal_proof_context(tampered)
        result = resolve_governed_qualification(refs["leaf"], tampered, boundary)
        self.assertFalse(result["qualified"])
        self.assertIn("PROOF_CONTEXT_TRUSTED_BINDING_MISMATCH", result["problems"])


if __name__ == "__main__":
    unittest.main()
