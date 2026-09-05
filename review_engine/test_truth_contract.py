from __future__ import annotations

import unittest

from review_engine.evidence_correspondence import (
    EvidenceCorrespondenceAttestation,
    RetainedEvidenceCorrespondenceRegistry,
    claim_fingerprint,
)
from review_engine.models import ReviewRequest, ReviewerConfig, ReviewerResponse, content_hash
from review_engine.orchestrator import ReviewEngine
from review_engine.qualification import QualificationRecord, QualificationRegistry
from review_engine.truth_contract import (
    TVC_VERSION,
    evaluate_truth_contract,
    neutral_epistemic_review,
    validate_epistemic_review,
)


def cfg(role: str, lineage: str) -> ReviewerConfig:
    return ReviewerConfig(
        role=role,
        provider=f"p-{role.lower()}",
        model=f"m-{role.lower()}",
        sku="default",
        deployment_path="api",
        api_key_env=f"{role}_KEY",
        foundation_lineage=lineage,
        qualification_ref=f"q-{role.lower()}",
    )


def registry(*configs: ReviewerConfig) -> QualificationRegistry:
    return QualificationRegistry(tuple(
        QualificationRecord(
            qualification_ref=config.qualification_ref,
            provider=config.provider,
            model=config.model,
            sku=config.sku,
            deployment_path=config.deployment_path,
            role=config.role,
            status="QUALIFIED",
            qualification_epoch=1,
            foundation_lineage=config.foundation_lineage,
            max_risk="CRITICAL",
            task_types=("*",),
        )
        for config in configs
    ))


def unsupported_material_fact() -> dict:
    return {
        "version": TVC_VERSION,
        "correspondence": "UNVERIFIED",
        "coherence": "CONSISTENT",
        "pragmatic": "VIABLE",
        "semantic": "PRECISE",
        "contradiction_refs": [],
        "claims": [{
            "claim_id": "c1",
            "text": "The external system already approved this change.",
            "claim_type": "EMPIRICAL_FACT",
            "correspondence": "UNVERIFIED",
            "evidence_refs": [],
            "material": True,
        }],
    }


def supported_material_fact(text: str = "Revenue increased 40%.", evidence_ref: str = "report:q3") -> dict:
    return {
        "version": TVC_VERSION,
        "correspondence": "SUPPORTED",
        "coherence": "CONSISTENT",
        "pragmatic": "VIABLE",
        "semantic": "PRECISE",
        "contradiction_refs": [],
        "claims": [{
            "claim_id": "c1",
            "text": text,
            "claim_type": "EMPIRICAL_FACT",
            "correspondence": "SUPPORTED",
            "evidence_refs": [evidence_ref],
            "material": True,
        }],
    }


class TruthContractTests(unittest.TestCase):
    def test_supported_empirical_fact_requires_evidence_handle(self):
        review = neutral_epistemic_review()
        review["correspondence"] = "SUPPORTED"
        review["claims"] = [{
            "claim_id": "c1",
            "text": "Deployment completed.",
            "claim_type": "EMPIRICAL_FACT",
            "correspondence": "SUPPORTED",
            "evidence_refs": [],
            "material": True,
        }]
        with self.assertRaisesRegex(ValueError, "supported empirical fact requires evidence_refs"):
            validate_epistemic_review(review)

    def test_reviewer_supported_material_fact_is_unverified_without_platform_correspondence(self):
        artifact_hash = content_hash("Revenue increased 40%.")
        result = evaluate_truth_contract(
            "R2",
            supported_material_fact(),
            artifact_hash=artifact_hash,
        )
        finding = next(f for f in result.findings if f.violated_invariant == "TVC-EVIDENCE-CORRESPONDENCE")
        self.assertEqual(finding.severity, "HIGH")
        self.assertTrue(finding.material)
        self.assertEqual(result.evidence_assessments[0]["status"], "UNVERIFIED")

    def test_platform_retained_support_attestation_can_clear_exact_bound_claim(self):
        text = "Revenue increased 40%."
        artifact_hash = content_hash(text)
        evidence_ref = "report:q3"
        validator = RetainedEvidenceCorrespondenceRegistry([
            EvidenceCorrespondenceAttestation(
                attestation_id="a1",
                artifact_hash=artifact_hash,
                claim_fingerprint=claim_fingerprint(text),
                evidence_ref=evidence_ref,
                evidence_content_hash=content_hash("exact report snapshot"),
                verdict="SUPPORTS",
                verifier_id="qualified-evidence-verifier",
                provenance="platform-retained-test",
                qualification_ref="ev-q1",
            )
        ])
        result = evaluate_truth_contract(
            "R2",
            supported_material_fact(text, evidence_ref),
            artifact_hash=artifact_hash,
            evidence_validator=validator,
        )
        self.assertFalse(any(f.violated_invariant == "TVC-EVIDENCE-CORRESPONDENCE" for f in result.findings))
        self.assertEqual(result.evidence_assessments[0]["status"], "VERIFIED_SUPPORT")
        self.assertEqual(result.evidence_assessments[0]["attestation_ids"], ("a1",))

    def test_unverified_material_empirical_claim_becomes_platform_finding(self):
        result = evaluate_truth_contract("R2", unsupported_material_fact())
        self.assertEqual(result.findings[0].violated_invariant, "TVC-CORRESPONDENCE")
        self.assertEqual(result.findings[0].severity, "HIGH")
        self.assertTrue(result.findings[0].material)

    def test_contradiction_cannot_be_reported_without_refs(self):
        review = neutral_epistemic_review()
        review["coherence"] = "CONTRADICTED"
        with self.assertRaisesRegex(ValueError, "requires contradiction_refs"):
            validate_epistemic_review(review)

    def test_misleading_semantics_is_material_contract_finding(self):
        review = neutral_epistemic_review()
        review["semantic"] = "MISLEADING"
        result = evaluate_truth_contract("R3", review)
        finding = next(f for f in result.findings if f.violated_invariant == "TVC-SEMANTIC-PRECISION")
        self.assertEqual(finding.severity, "HIGH")
        self.assertTrue(finding.material)

    def test_r2_clean_response_cannot_erase_material_r1_truth_finding(self):
        r1 = cfg("R1", "lineage-r1")
        r2 = cfg("R2", "lineage-r2")
        calls = []

        def invoke(config, context):
            calls.append(config.role)
            if config.role == "R1":
                return ReviewerResponse(
                    "R1",
                    None,
                    "The external system already approved this change.",
                    epistemic_review=unsupported_material_fact(),
                )
            return ReviewerResponse(
                "R2",
                context["artifact"]["artifact_hash"],
                "No additional material defect found.",
                epistemic_review=neutral_epistemic_review(),
            )

        decision = ReviewEngine(invoke, qualification_registry=registry(r1, r2)).run(
            ReviewRequest("tvc-route", "answer a simple question"),
            r1=r1,
            r2=r2,
            r3=None,
        )
        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertEqual(calls, ["R1", "R2", "R1"])
        self.assertIn("no artifact revision", decision.reasons[0])

    def test_material_r1_truth_finding_can_be_corrected_then_blindly_verified(self):
        r1 = cfg("R1", "lineage-r1")
        r2 = cfg("R2", "lineage-r2")
        r3 = cfg("R3", "lineage-r3")
        calls = []

        def invoke(config, context):
            calls.append(config.role)
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse(
                    "R1",
                    None,
                    "The external system already approved this change.",
                    epistemic_review=unsupported_material_fact(),
                )
            if config.role == "R2":
                return ReviewerResponse(
                    "R2",
                    context["artifact"]["artifact_hash"],
                    "Independent review confirms the claim must be qualified.",
                    epistemic_review=neutral_epistemic_review(),
                )
            if config.role == "R1":
                self.assertTrue(context["review_targets"])
                return ReviewerResponse(
                    "R1",
                    None,
                    "The available evidence does not establish external approval.",
                    epistemic_review=neutral_epistemic_review(),
                )
            return ReviewerResponse(
                "R3",
                context["artifact"]["artifact_hash"],
                "The revised wording no longer asserts unverified approval.",
                epistemic_review=neutral_epistemic_review(),
            )

        decision = ReviewEngine(invoke, qualification_registry=registry(r1, r2, r3)).run(
            ReviewRequest("tvc-correct", "answer a simple question"),
            r1=r1,
            r2=r2,
            r3=r3,
        )
        self.assertEqual(decision.state, "CONVERGED_PASS")
        self.assertEqual(calls, ["R1", "R2", "R1", "R3"])
        self.assertIn("does not establish", decision.final_output)

    def test_unqualified_mode_cannot_clear_r1_material_truth_failure(self):
        r1 = cfg("R1", "lineage-r1")
        calls = []

        def invoke(config, context):
            calls.append(config.role)
            return ReviewerResponse(
                "R1",
                None,
                "The external system already approved this change.",
                epistemic_review=unsupported_material_fact(),
            )

        decision = ReviewEngine(invoke).run(
            ReviewRequest("tvc-unqualified", "simple question"),
            r1=r1,
            r2=None,
            r3=None,
        )
        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertEqual(calls, ["R1"])
        self.assertIn("Truth & Veracity", decision.reasons[0])


if __name__ == "__main__":
    unittest.main()
