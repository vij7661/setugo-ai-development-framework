from __future__ import annotations

import os
import unittest

from v24_v6_governance_foundation import CURRENT, QUALIFIED, digest
from v24_v6_proof_reference_closure import (
    CURRENTNESS_BINDING,
    GOVERNED_QUALIFICATION,
    INDEPENDENCE_QUALIFICATION,
    TRUSTED_BOUNDARY_ANCHOR_ENV,
    resolve_governed_qualification,
    seal_proof_context,
    trusted_boundary_anchor_digest,
)


D1 = "01" * 32
D2 = "02" * 32
D3 = "03" * 32
D4 = "04" * 32
D5 = "05" * 32
D6 = "06" * 32
D7 = "07" * 32
D8 = "08" * 32
D9 = "09" * 32
ROOT_CONTENT = "f0" * 32
TARGET_CONTENT = "aa" * 32


def _seal(record: dict, field: str) -> dict:
    material = dict(record)
    material.pop(field, None)
    record[field] = digest(material)
    return record


def _currentness(source_id: str, source_digest: str, verifier_ref: str) -> dict:
    return _seal(
        {
            "currentness_rule_id": "ATTACK-CURRENTNESS-RULE",
            "source_object_id": source_id,
            "source_version_or_sequence": "1",
            "source_digest": source_digest,
            "observed_at_sequence": 1,
            "verifier_qualification_digest": verifier_ref,
            "result": CURRENT,
            "binding_digest": "",
        },
        "binding_digest",
    )


def _wrap(kind: str, record: dict) -> dict:
    field = "binding_digest" if kind == CURRENTNESS_BINDING else "qualification_digest"
    return {
        "record_kind": kind,
        "record_digest": record[field],
        "record": dict(record),
    }


def attacker_constructed_bundle() -> tuple[dict, dict, str]:
    trusted = [{"object_id": "ATTACK-ROOT-VERIFIER", "content_digest": ROOT_CONTENT}]
    scope = _seal(
        {
            "governance_generation_id": "GEN-ATTACK",
            "genesis_record_digest": D1,
            "root_kernel_digest": D2,
            "trusted_objects": trusted,
            "trusted_object_pair_set_digest": digest(trusted),
            "permitted_bootstrap_roles": ["ATTACK_BOOTSTRAP_VERIFIER"],
            "residual_trust_reason_ids": ["ATTACK_GENESIS_ROOT"],
            "creation_ceremony_digest": D3,
            "durable_anchor_digest": D4,
            "scope_digest": "",
        },
        "scope_digest",
    )

    root = _seal(
        {
            "qualification_id": "ATTACK-Q-ROOT",
            "subject_object_id": "ATTACK-ROOT-VERIFIER",
            "subject_content_digest": ROOT_CONTENT,
            "subject_kind": "VERIFIER",
            "subject_owner_id": "ATTACK-ROOT-OWNER",
            "qualification_authority_id": "ATTACK-ROOT-AUTHORITY",
            "authority_member_ids": ["ATTACK-ROOT-MEMBER"],
            "authority_control_domain_ids": ["ATTACK-ROOT-DOMAIN"],
            "independence_qualification_digests": [D5],
            "evidence_record_digests": [D6],
            "evidence_class_ids": ["ATTACK-ROOT-EVIDENCE"],
            "verifier_mechanism_id": "ATTACK-BOOTSTRAP-VERIFIER",
            "verifier_mechanism_qualification_digest": D7,
            "currentness_bindings": [
                _currentness("ATTACK-ROOT-VERIFIER", ROOT_CONTENT, D8)
            ],
            "result": QUALIFIED,
            "proof_digest": D9,
            "qualification_digest": "",
        },
        "qualification_digest",
    )
    root_ref = root["qualification_digest"]

    independence = _seal(
        {
            "independence_qualification_id": "ATTACK-IND",
            "independence_rule_id": "ATTACK-INDEPENDENCE-RULE",
            "subject_identity_id": "ATTACK-LEAF-AUTHORITY",
            "subject_control_closure": [
                "ORG:ATTACK-LEAF-AUTHORITY",
                "KMS:ATTACK-LEAF-AUTHORITY",
            ],
            "counterparties": [
                {
                    "identity_id": "ATTACK-EXTERNAL",
                    "control_closure": [
                        "ORG:ATTACK-EXTERNAL",
                        "KMS:ATTACK-EXTERNAL",
                    ],
                }
            ],
            "shared_control_intersections": [],
            "evidence_record_digests": [D1],
            "currentness_bindings": [
                _currentness("IND-EVIDENCE", D2, root_ref)
            ],
            "result": QUALIFIED,
            "verifier_qualification_digest": root_ref,
            "qualification_digest": "",
        },
        "qualification_digest",
    )
    independence_ref = independence["qualification_digest"]

    leaf = _seal(
        {
            "qualification_id": "ATTACK-Q-LEAF",
            "subject_object_id": "ATTACK-TARGET",
            "subject_content_digest": TARGET_CONTENT,
            "subject_kind": "ATTACK_OBJECT",
            "subject_owner_id": "ATTACK-OWNER",
            "qualification_authority_id": "ATTACK-LEAF-AUTHORITY",
            "authority_member_ids": ["ATTACK-MEMBER"],
            "authority_control_domain_ids": ["ATTACK-DOMAIN"],
            "independence_qualification_digests": [independence_ref],
            "evidence_record_digests": [D3],
            "evidence_class_ids": ["ATTACK-EVIDENCE"],
            "verifier_mechanism_id": "ATTACK-ROOT-VERIFIER",
            "verifier_mechanism_qualification_digest": root_ref,
            "currentness_bindings": [
                _currentness("ATTACK-TARGET", TARGET_CONTENT, root_ref)
            ],
            "result": QUALIFIED,
            "proof_digest": D4,
            "qualification_digest": "",
        },
        "qualification_digest",
    )
    leaf_ref = leaf["qualification_digest"]

    context = {
        "proof_context_id": "ATTACK-CONTEXT",
        "governance_generation_id": "GEN-ATTACK",
        "evidence_records": [
            _wrap(GOVERNED_QUALIFICATION, root),
            _wrap(INDEPENDENCE_QUALIFICATION, independence),
            _wrap(GOVERNED_QUALIFICATION, leaf),
        ],
        "genesis_trusted_scope": scope,
        "context_digest": "",
    }
    seal_proof_context(context)
    boundary = {
        "governance_generation_id": context["governance_generation_id"],
        "expected_proof_context_digest": context["context_digest"],
        "expected_genesis_scope_digest": context["genesis_trusted_scope"]["scope_digest"],
    }
    return context, boundary, leaf_ref


class Successor4ExternalAnchorRed(unittest.TestCase):
    def test_same_process_caller_cannot_self_update_anchor_and_self_grant(self):
        context, boundary, leaf_ref = attacker_constructed_bundle()
        old = os.environ.get(TRUSTED_BOUNDARY_ANCHOR_ENV)
        try:
            # This is the missing successor-3 attack: the same caller that built
            # the forged context also rewrites the alleged external anchor.
            os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = trusted_boundary_anchor_digest(boundary)
            result = resolve_governed_qualification(
                leaf_ref,
                context,
                boundary,
                expected_subject_id="ATTACK-TARGET",
                expected_subject_content_digest=TARGET_CONTENT,
            )
        finally:
            if old is None:
                os.environ.pop(TRUSTED_BOUNDARY_ANCHOR_ENV, None)
            else:
                os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = old

        self.assertFalse(result["qualified"], result)
        self.assertNotEqual("PROOF_REFERENCE_CLOSED", result["state"], result)


if __name__ == "__main__":
    unittest.main()
