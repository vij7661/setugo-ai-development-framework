from __future__ import annotations

import unittest

from review_engine.evidence_correspondence import (
    EvidenceCorrespondenceAttestation,
    RetainedEvidenceCorrespondenceRegistry,
    claim_fingerprint,
)
from review_engine.models import ReviewFinding, ReviewerConfig, ReviewerResponse, ReviewRequest, content_hash
from review_engine.orchestrator import ReviewEngine
from review_engine.qualification import QualificationRecord, QualificationRegistry
from review_engine.truth_contract import TVC_VERSION, neutral_epistemic_review


CLAIM = "Revenue increased 40%."
REVISED = f"stable header\n{CLAIM}\nstable footer"


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
            qualification_ref=config.qualification_ref or f"q-{config.role.lower()}",
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


def unverified_claim_review() -> dict:
    return {
        "version": TVC_VERSION,
        "correspondence": "UNVERIFIED",
        "coherence": "CONSISTENT",
        "pragmatic": "VIABLE",
        "semantic": "PRECISE",
        "contradiction_refs": [],
        "claims": [{
            "claim_id": "revenue",
            "text": CLAIM,
            "claim_type": "EMPIRICAL_FACT",
            "correspondence": "UNVERIFIED",
            "evidence_refs": [],
            "material": True,
        }],
    }


def supported_claim_review() -> dict:
    return {
        "version": TVC_VERSION,
        "correspondence": "SUPPORTED",
        "coherence": "CONSISTENT",
        "pragmatic": "VIABLE",
        "semantic": "PRECISE",
        "contradiction_refs": [],
        "claims": [{
            "claim_id": "revenue",
            "text": CLAIM,
            "claim_type": "EMPIRICAL_FACT",
            "correspondence": "SUPPORTED",
            "evidence_refs": ["report:q3"],
            "material": True,
        }],
    }


class R3PlatformEvidenceClosureTests(unittest.TestCase):
    def _run(self, phase_b_review: dict, evidence_validator=None):
        r1 = cfg("R1", "lineage-r1")
        r2 = cfg("R2", "lineage-r2")
        r3 = cfg("R3", "lineage-r3")
        phase_b_contexts = []

        def invoke(config, context):
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse("R1", None, "stable header\nwrong claim\nstable footer")
            if config.role == "R2":
                finding = ReviewFinding(
                    "r2-local",
                    "R2",
                    "HIGH",
                    True,
                    "replace wrong claim",
                    affected_scope=("claim:c1",),
                    first_invalid_claim="wrong claim",
                )
                return ReviewerResponse("R2", context["artifact"]["artifact_hash"], "localized defect", (finding,))
            if config.role == "R1":
                return ReviewerResponse("R1", None, REVISED)
            if context["phase"] == "INDEPENDENT":
                return ReviewerResponse(
                    "R3",
                    context["artifact"]["artifact_hash"],
                    "material empirical claim remains unverified",
                    epistemic_review=unverified_claim_review(),
                )

            phase_b_contexts.append(context)
            frozen_ids = [f["finding_id"] for f in context["frozen_material_findings"]]
            self.assertIn("tvc-correspondence-revenue", frozen_ids)
            return ReviewerResponse(
                "R3",
                context["artifact_hash"],
                "claims the platform finding is resolved",
                epistemic_review=phase_b_review,
                resolved_finding_ids=("tvc-correspondence-revenue",),
            )

        engine = ReviewEngine(
            invoke,
            qualification_registry=registry(r1, r2, r3),
            evidence_validator=evidence_validator,
        )
        decision = engine.run(
            ReviewRequest("r3-platform-evidence", "material review", risk="HIGH", materiality="MATERIAL"),
            r1=r1,
            r2=r2,
            r3=r3,
        )
        return decision, phase_b_contexts

    def test_model_cannot_close_platform_correspondence_finding_without_verified_support(self):
        decision, contexts = self._run(neutral_epistemic_review())

        self.assertEqual(len(contexts), 1)
        self.assertEqual(contexts[0]["artifact"]["content"], REVISED)
        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertIn("platform-verified evidence", decision.reasons[0])
        self.assertTrue(any(CLAIM in text for text in decision.dissent))

    def test_exact_platform_verified_support_allows_explicit_closure(self):
        validator = RetainedEvidenceCorrespondenceRegistry([
            EvidenceCorrespondenceAttestation(
                attestation_id="attestation-q3",
                artifact_hash=content_hash(REVISED),
                claim_fingerprint=claim_fingerprint(CLAIM),
                evidence_ref="report:q3",
                evidence_content_hash=content_hash("retained q3 report snapshot"),
                verdict="SUPPORTS",
                verifier_id="qualified-verifier",
                provenance="retained-test-evidence",
                qualification_ref="ev-q1",
            )
        ])

        decision, _ = self._run(supported_claim_review(), validator)

        self.assertEqual(decision.state, "CONVERGED_PASS")
        self.assertIn("explicitly closed every frozen material finding", decision.reasons[0])


if __name__ == "__main__":
    unittest.main()
