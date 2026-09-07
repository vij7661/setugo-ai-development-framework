from __future__ import annotations

from copy import deepcopy
import unittest

from test_single_file_review_container import SingleFileReviewContainerTests  # imported so current CI loader executes P2 cases
from review_protocol import (
    DispatchResult,
    build_review_request,
    can_promote_material_transition,
    canonical_hash,
    validate_review_evidence,
    validate_review_semantics,
)


class ReviewSemanticConsistencyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dimensions = [
            {
                "id": "authority_path",
                "mandatory": True,
                "description": "Review the authority and promotion path for bypasses.",
            },
            {
                "id": "raw_byte_integrity",
                "mandatory": True,
                "description": "Independently inspect raw exported artifacts and manifest byte hashes.",
            },
            {
                "id": "optional_usability",
                "mandatory": False,
                "description": "Optional usability observations that do not determine authority safety.",
            },
        ]
        self.request = build_review_request(
            review_request_id="REV-SEM-001",
            trigger="MATERIAL_GOVERNANCE_CHANGE",
            artifact_type="governance_candidate",
            artifact_ref="PR-5",
            artifact_commit="4" * 40,
            proposer={"provider": "openai", "model": "gpt-5.6-sol"},
            required_reviewer={"provider": "deepseek", "model_class": "deepseek"},
            blind_review_required=True,
            review_questions=["Review all governed dimensions independently."],
            evidence_refs=[],
            material_authority_transition=True,
            required_review_dimensions=self.dimensions,
        )
        self.authoritative_state = {
            "active_workstream": {
                "branch": "feature/test",
                "head_commit": "a" * 40,
                "state": "CONSTRUCTION_GREEN",
            },
            "independent_review": {
                "current_review_request_id": "REV-SEM-001",
                "current_review_status": "REVIEW_RECEIVED",
                "current_reviewed_artifact_commit": "4" * 40,
            },
        }
        self.shared_memory = {
            "independent_authority": False,
            "current_work": {
                "authoritative_branch": "feature/test",
                "authoritative_head": "a" * 40,
                "status": "CONSTRUCTION_GREEN",
            },
            "governance_runtime": {
                "current_review_request_id": "REV-SEM-001",
                "current_review_status": "REVIEW_RECEIVED",
            },
            "pending_reviews": [
                {"status": "REVIEW_RECEIVED", "review_request_id": "REV-SEM-001"}
            ],
        }

    def coverage(self, authority="TESTED_SUPPORTED", raw="TESTED_SUPPORTED", optional="TESTED_SUPPORTED"):
        rows = []
        for dimension_id, status in (
            ("authority_path", authority),
            ("raw_byte_integrity", raw),
            ("optional_usability", optional),
        ):
            rows.append(
                {
                    "dimension_id": dimension_id,
                    "status": status,
                    "evidence": [f"evidence:{dimension_id}"] if status in {"TESTED_SUPPORTED", "TESTED_DEFECT_FOUND", "CONTRADICTED"} else [],
                    "assessment": f"coverage for {dimension_id}: {status}",
                }
            )
        return rows

    def evidence(self, *, disposition="PASS", coverage=None, assessment="All mandatory dimensions were directly tested and supported.", findings=None):
        return {
            "review_request_id": "REV-SEM-001",
            "reviewed_artifact_commit": "4" * 40,
            "reviewer": {"provider": "deepseek", "model": "deepseek-reasoner"},
            "disposition": disposition,
            "findings": [] if findings is None else findings,
            "evidence_assessment": assessment,
            "review_coverage": self.coverage() if coverage is None else coverage,
            "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
        }

    def execution(self, evidence):
        return DispatchResult(
            transport="AUTOMATIC_API",
            state="REVIEW_RECEIVED",
            review_request_id="REV-SEM-001",
            payload_hash=canonical_hash(self.request),
            response=deepcopy(evidence),
            reviewer_provider="deepseek",
            reviewer_model="deepseek-reasoner",
            identity_assurance="PROVIDER_ADAPTER_AUTHENTICATED",
        )

    def test_pass_with_required_dimension_not_tested_is_rejected(self):
        evidence = self.evidence(coverage=self.coverage(raw="NOT_TESTED"))
        ok, reason = validate_review_semantics(request=self.request, evidence=evidence)
        self.assertFalse(ok)
        self.assertIn("PASS requires every review dimension", reason)

    def test_pass_with_required_dimension_omitted_is_rejected(self):
        coverage = [row for row in self.coverage() if row["dimension_id"] != "raw_byte_integrity"]
        evidence = self.evidence(coverage=coverage)
        ok, reason = validate_review_semantics(request=self.request, evidence=evidence)
        self.assertFalse(ok)
        self.assertIn("coverage dimensions differ", reason)

    def test_pass_with_all_dimensions_supported_is_semantically_valid(self):
        evidence = self.evidence()
        ok, reason = validate_review_semantics(request=self.request, evidence=evidence)
        self.assertTrue(ok, reason)

    def test_bounded_pass_cannot_hide_mandatory_not_tested_dimension(self):
        evidence = self.evidence(disposition="BOUNDED_PASS", coverage=self.coverage(raw="NOT_TESTED", optional="NOT_TESTED"))
        ok, reason = validate_review_semantics(request=self.request, evidence=evidence)
        self.assertFalse(ok)
        self.assertIn("mandatory", reason)

    def test_bounded_pass_allows_only_optional_gap(self):
        evidence = self.evidence(disposition="BOUNDED_PASS", coverage=self.coverage(optional="NOT_TESTED"))
        ok, reason = validate_review_semantics(request=self.request, evidence=evidence)
        self.assertTrue(ok, reason)

    def test_insufficient_evidence_is_valid_content_but_nonpromotable(self):
        evidence = self.evidence(
            disposition="INSUFFICIENT_EVIDENCE",
            coverage=self.coverage(raw="INACCESSIBLE"),
            assessment="Raw artifacts were inaccessible, so full review could not be completed.",
        )
        execution = self.execution(evidence)
        valid, reason = validate_review_evidence(request=self.request, evidence=evidence, execution=execution)
        self.assertTrue(valid, reason)
        self.assertFalse(
            can_promote_material_transition(
                deterministic_gate_passed=True,
                authoritative_state=self.authoritative_state,
                shared_memory=self.shared_memory,
                review_request=self.request,
                review_evidence=evidence,
                review_execution=execution,
            )
        )

    def test_changes_required_with_contradicted_dimension_is_valid_but_nonpromotable(self):
        evidence = self.evidence(
            disposition="CHANGES_REQUIRED",
            coverage=self.coverage(authority="CONTRADICTED"),
            findings=[{"id": "F1", "severity": "HIGH"}],
            assessment="Authority path contradiction requires repair.",
        )
        execution = self.execution(evidence)
        valid, reason = validate_review_evidence(request=self.request, evidence=evidence, execution=execution)
        self.assertTrue(valid, reason)
        self.assertFalse(
            can_promote_material_transition(
                deterministic_gate_passed=True,
                authoritative_state=self.authoritative_state,
                shared_memory=self.shared_memory,
                review_request=self.request,
                review_evidence=evidence,
                review_execution=execution,
            )
        )

    def test_tested_supported_requires_nonempty_evidence(self):
        coverage = self.coverage()
        coverage[1]["evidence"] = []
        evidence = self.evidence(coverage=coverage)
        ok, reason = validate_review_semantics(request=self.request, evidence=evidence)
        self.assertFalse(ok)
        self.assertIn("non-empty evidence", reason)

    def test_rev008_phrase_regression_rejects_unqualified_pass(self):
        evidence = self.evidence(
            assessment=(
                "The portable review bundle design includes raw artifacts with manifest hashes for byte-integrity verification, "
                "though in this review environment the raw files were not directly accessible; however, the builder logic appears correct."
            )
        )
        ok, reason = validate_review_semantics(request=self.request, evidence=evidence)
        self.assertFalse(ok)
        self.assertIn("free-text evidence assessment contradicts PASS", reason)

    def test_legacy_review_schema_cannot_promote_material_authority(self):
        legacy = build_review_request(
            review_request_id="REV-LEGACY-001",
            trigger="MATERIAL_GOVERNANCE_CHANGE",
            artifact_type="governance_candidate",
            artifact_ref="PR-legacy",
            artifact_commit="5" * 40,
            proposer={"provider": "openai", "model": "gpt-5.6-sol"},
            required_reviewer={"provider": "deepseek", "model_class": "deepseek"},
            blind_review_required=True,
            review_questions=["Review independently."],
            evidence_refs=[],
            material_authority_transition=True,
        )
        evidence = {
            "review_request_id": "REV-LEGACY-001",
            "reviewed_artifact_commit": "5" * 40,
            "reviewer": {"provider": "deepseek", "model": "deepseek-reasoner"},
            "disposition": "PASS",
            "findings": [],
            "evidence_assessment": "Looks good.",
            "independence_attestation": "BLIND_TO_PROPOSER_CONCLUSION",
        }
        execution = DispatchResult(
            transport="AUTOMATIC_API",
            state="REVIEW_RECEIVED",
            review_request_id="REV-LEGACY-001",
            payload_hash=canonical_hash(legacy),
            response=deepcopy(evidence),
            reviewer_provider="deepseek",
            reviewer_model="deepseek-reasoner",
            identity_assurance="PROVIDER_ADAPTER_AUTHENTICATED",
        )
        state = deepcopy(self.authoritative_state)
        state["independent_review"]["current_review_request_id"] = "REV-LEGACY-001"
        state["independent_review"]["current_reviewed_artifact_commit"] = "5" * 40
        memory = deepcopy(self.shared_memory)
        memory["governance_runtime"]["current_review_request_id"] = "REV-LEGACY-001"
        memory["pending_reviews"][0]["review_request_id"] = "REV-LEGACY-001"
        self.assertFalse(
            can_promote_material_transition(
                deterministic_gate_passed=True,
                authoritative_state=state,
                shared_memory=memory,
                review_request=legacy,
                review_evidence=evidence,
                review_execution=execution,
            )
        )


if __name__ == "__main__":
    unittest.main()
