from __future__ import annotations

import copy
import os
import unittest

from test_v24_v6_decision_apply import attach_proofs as attach_decision_proofs
from test_v24_v6_decision_apply import bundle as decision_bundle
from test_v24_v6_normative_clause_projection import coverage_fixture
from test_v24_v6_proof_reference_closure import ROOT_CONTENT, proof_bundle
from v24_v6_decision_apply import evaluate_decision_apply_latch
from v24_v6_normative_clause_projection import validate_catalog_candidate_coverage
from v24_v6_proof_reference_closure import (
    TRUSTED_BOUNDARY_ANCHOR_ENV,
    resolve_governed_qualification,
    seal_proof_context,
    trusted_boundary_anchor_digest,
)


class Successor3ManualReviewRegressions(unittest.TestCase):
    def test_prc1_self_constructed_trusted_boundary_is_rejected(self):
        context, _, refs = proof_bundle()
        forged_context = copy.deepcopy(context)
        forged_context["proof_context_id"] = "ATTACKER-CONSTRUCTED-CONTEXT"
        seal_proof_context(forged_context)
        scope = forged_context["genesis_trusted_scope"]
        self_built_boundary = {
            "governance_generation_id": forged_context["governance_generation_id"],
            "expected_proof_context_digest": forged_context["context_digest"],
            "expected_genesis_scope_digest": scope["scope_digest"],
        }

        # Reproduce the exact Successor-3 attack: the same caller computes and
        # rewrites the old environment digest to match its forged boundary.
        # Successor-4 must ignore that mutable value and still require an
        # externally issued asymmetric root attestation.
        old = os.environ.get(TRUSTED_BOUNDARY_ANCHOR_ENV)
        try:
            os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = trusted_boundary_anchor_digest(
                self_built_boundary
            )
            result = resolve_governed_qualification(
                refs["root"],
                forged_context,
                self_built_boundary,
                expected_subject_id="ROOT-VERIFIER",
                expected_subject_content_digest=ROOT_CONTENT,
            )
        finally:
            if old is None:
                os.environ.pop(TRUSTED_BOUNDARY_ANCHOR_ENV, None)
            else:
                os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = old

        self.assertFalse(result["qualified"], result)
        self.assertIn("ROOT_ATTESTATION_REQUIRED", result["problems"])

    def test_ncp1_control_reassignment_requires_new_authorized_binding(self):
        coverage, context, boundary, _ = coverage_fixture()
        coverage["catalog_descriptors"][0]["control_id"] = (
            "CTRL-COMPLETELY-DIFFERENT-UNAUTHORIZED"
        )
        result = validate_catalog_candidate_coverage(
            coverage,
            proof_context=context,
            trusted_boundary=boundary,
        )
        self.assertFalse(result["qualified"], result)

    def test_da1_decision_for_one_path_cannot_authorize_another_current_path(self):
        b = decision_bundle()
        b["material_effect_path"]["path_id"] = "PATH-2"
        b["material_effect_path"]["path_content_digest"] = "e" * 64
        context, boundary = attach_decision_proofs(b)
        result = evaluate_decision_apply_latch(
            b,
            proof_context=context,
            trusted_boundary=boundary,
        )
        self.assertFalse(result["allowed"], result)


if __name__ == "__main__":
    unittest.main()
