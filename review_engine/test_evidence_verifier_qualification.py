from __future__ import annotations

import unittest

from review_engine.evidence_correspondence import (
    EvidenceCorrespondenceAttestation,
    EvidenceVerifierIdentity,
    claim_fingerprint,
)
from review_engine.evidence_verifier_qualification import (
    EvidenceVerifierQualificationRecord,
    EvidenceVerifierQualificationRegistry,
)
from review_engine.models import content_hash
from review_engine.qualified_evidence_correspondence import QualifiedRetainedEvidenceCorrespondenceRegistry


ARTIFACT_HASH = content_hash("artifact-v1")
CLAIM = "Revenue increased 40%."


def identity(**overrides) -> EvidenceVerifierIdentity:
    values = {
        "provider": "verifier-provider",
        "model": "verifier-model",
        "sku": "default",
        "deployment_path": "api",
        "foundation_lineage": "verifier-lineage",
        "qualification_ref": "evidence-verifier-q1",
        "qualification_epoch": 1,
    }
    values.update(overrides)
    return EvidenceVerifierIdentity(**values)


def qualifications(*, status: str = "QUALIFIED", epoch: int = 1, max_risk: str = "HIGH", task_types=("RESEARCH",)) -> EvidenceVerifierQualificationRegistry:
    return EvidenceVerifierQualificationRegistry((
        EvidenceVerifierQualificationRecord(
            qualification_ref="evidence-verifier-q1",
            provider="verifier-provider",
            model="verifier-model",
            sku="default",
            deployment_path="api",
            foundation_lineage="verifier-lineage",
            status=status,
            qualification_epoch=epoch,
            max_risk=max_risk,
            task_types=tuple(task_types),
        ),
    ))


def attestation(*, verifier_identity: EvidenceVerifierIdentity | None = None, verifier_id: str | None = None) -> EvidenceCorrespondenceAttestation:
    bound = verifier_identity or identity()
    return EvidenceCorrespondenceAttestation(
        attestation_id="a1",
        artifact_hash=ARTIFACT_HASH,
        claim_fingerprint=claim_fingerprint(CLAIM),
        evidence_ref="report:2026-q3",
        evidence_content_hash=content_hash("snapshot:report:2026-q3"),
        verdict="SUPPORTS",
        verifier_id=verifier_id or bound.verifier_id,
        provenance="qualified-verifier-test",
        qualification_ref=bound.qualification_ref,
        verifier_identity=verifier_identity,
    )


def claim() -> dict:
    return {
        "claim_id": "c1",
        "text": CLAIM,
        "evidence_refs": ["report:2026-q3"],
    }


class EvidenceVerifierQualificationTests(unittest.TestCase):
    def test_exact_qualified_verifier_can_support_in_scope_claim(self):
        verifier = identity()
        registry = QualifiedRetainedEvidenceCorrespondenceRegistry(qualifications())
        registry.add(attestation(verifier_identity=verifier))
        assessment = registry.assess(
            artifact_hash=ARTIFACT_HASH,
            claim=claim(),
            risk="HIGH",
            task_type="RESEARCH",
        )
        self.assertEqual(assessment.status, "VERIFIED_SUPPORT")
        self.assertEqual(assessment.verifier_ids, (verifier.verifier_id,))

    def test_free_verifier_label_without_structured_identity_is_rejected(self):
        registry = QualifiedRetainedEvidenceCorrespondenceRegistry(qualifications())
        forged = EvidenceCorrespondenceAttestation(
            attestation_id="forged",
            artifact_hash=ARTIFACT_HASH,
            claim_fingerprint=claim_fingerprint(CLAIM),
            evidence_ref="report:2026-q3",
            evidence_content_hash=content_hash("snapshot:report:2026-q3"),
            verdict="SUPPORTS",
            verifier_id="verifier-1",
            provenance="forged-label-test",
            qualification_ref="evidence-verifier-q1",
        )
        with self.assertRaisesRegex(ValueError, "structured verifier identity"):
            registry.add(forged)

    def test_provider_model_sku_deployment_lineage_or_epoch_substitution_is_rejected(self):
        cases = (
            ("provider", "substituted-provider"),
            ("model", "substituted-model"),
            ("sku", "other-sku"),
            ("deployment_path", "proxy"),
            ("foundation_lineage", "other-lineage"),
            ("qualification_epoch", 2),
        )
        for field, value in cases:
            with self.subTest(field=field):
                verifier = identity(**{field: value})
                registry = QualifiedRetainedEvidenceCorrespondenceRegistry(qualifications())
                with self.assertRaisesRegex(ValueError, "binding mismatch"):
                    registry.add(attestation(verifier_identity=verifier))

    def test_pending_or_revoked_verifier_is_rejected_at_admission(self):
        for status in ("PENDING", "REVOKED"):
            with self.subTest(status=status):
                registry = QualifiedRetainedEvidenceCorrespondenceRegistry(qualifications(status=status))
                with self.assertRaisesRegex(ValueError, status):
                    registry.add(attestation(verifier_identity=identity()))

    def test_revocation_after_admission_removes_support_at_assessment(self):
        q = qualifications()
        registry = QualifiedRetainedEvidenceCorrespondenceRegistry(q)
        registry.add(attestation(verifier_identity=identity()))
        q.add(
            EvidenceVerifierQualificationRecord(
                qualification_ref="evidence-verifier-q1",
                provider="verifier-provider",
                model="verifier-model",
                sku="default",
                deployment_path="api",
                foundation_lineage="verifier-lineage",
                status="REVOKED",
                qualification_epoch=2,
                max_risk="HIGH",
                task_types=("RESEARCH",),
            )
        )
        assessment = registry.assess(
            artifact_hash=ARTIFACT_HASH,
            claim=claim(),
            risk="LOW",
            task_type="RESEARCH",
        )
        self.assertEqual(assessment.status, "UNVERIFIED")
        self.assertEqual(assessment.attestation_ids, ())

    def test_risk_above_verifier_qualification_ceiling_does_not_verify_support(self):
        registry = QualifiedRetainedEvidenceCorrespondenceRegistry(qualifications(max_risk="LOW"))
        registry.add(attestation(verifier_identity=identity()))
        assessment = registry.assess(
            artifact_hash=ARTIFACT_HASH,
            claim=claim(),
            risk="HIGH",
            task_type="RESEARCH",
        )
        self.assertEqual(assessment.status, "UNVERIFIED")

    def test_task_outside_verifier_qualification_scope_does_not_verify_support(self):
        registry = QualifiedRetainedEvidenceCorrespondenceRegistry(qualifications(task_types=("RESEARCH",)))
        registry.add(attestation(verifier_identity=identity()))
        assessment = registry.assess(
            artifact_hash=ARTIFACT_HASH,
            claim=claim(),
            risk="LOW",
            task_type="CODE_REVIEW",
        )
        self.assertEqual(assessment.status, "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
