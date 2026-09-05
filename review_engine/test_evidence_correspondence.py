from __future__ import annotations

import unittest

from review_engine.evidence_correspondence import (
    EvidenceCorrespondenceAttestation,
    RetainedEvidenceCorrespondenceRegistry,
    claim_fingerprint,
)
from review_engine.models import content_hash


def attestation(*, artifact_hash: str, claim_text: str, evidence_ref: str, verdict: str, attestation_id: str, verifier_id: str = "verifier-1") -> EvidenceCorrespondenceAttestation:
    return EvidenceCorrespondenceAttestation(
        attestation_id=attestation_id,
        artifact_hash=artifact_hash,
        claim_fingerprint=claim_fingerprint(claim_text),
        evidence_ref=evidence_ref,
        evidence_content_hash=content_hash(f"snapshot:{evidence_ref}"),
        verdict=verdict,
        verifier_id=verifier_id,
        provenance="platform-retained-test-evidence",
        qualification_ref="evidence-verifier-q1",
    )


class EvidenceCorrespondenceTests(unittest.TestCase):
    def test_support_attestation_is_bound_to_exact_artifact_claim_and_evidence_ref(self):
        artifact_hash = content_hash("artifact-v1")
        claim_text = "Revenue increased 40%."
        registry = RetainedEvidenceCorrespondenceRegistry([
            attestation(
                artifact_hash=artifact_hash,
                claim_text=claim_text,
                evidence_ref="report:2026-q3",
                verdict="SUPPORTS",
                attestation_id="a1",
            )
        ])
        assessment = registry.assess(
            artifact_hash=artifact_hash,
            claim={"claim_id": "c1", "text": claim_text, "evidence_refs": ["report:2026-q3"]},
        )
        self.assertEqual(assessment.status, "VERIFIED_SUPPORT")
        self.assertEqual(assessment.attestation_ids, ("a1",))

    def test_stale_or_rephrased_claim_cannot_reuse_attestation(self):
        artifact_hash = content_hash("artifact-v1")
        registry = RetainedEvidenceCorrespondenceRegistry([
            attestation(
                artifact_hash=artifact_hash,
                claim_text="Revenue increased 40%.",
                evidence_ref="report:2026-q3",
                verdict="SUPPORTS",
                attestation_id="a1",
            )
        ])
        changed_claim = registry.assess(
            artifact_hash=artifact_hash,
            claim={"claim_id": "c1", "text": "Revenue increased 41%.", "evidence_refs": ["report:2026-q3"]},
        )
        changed_artifact = registry.assess(
            artifact_hash=content_hash("artifact-v2"),
            claim={"claim_id": "c1", "text": "Revenue increased 40%.", "evidence_refs": ["report:2026-q3"]},
        )
        self.assertEqual(changed_claim.status, "UNVERIFIED")
        self.assertEqual(changed_artifact.status, "UNVERIFIED")

    def test_conflicting_independent_attestations_surface_conflict(self):
        artifact_hash = content_hash("artifact-v1")
        claim_text = "Deployment completed successfully."
        registry = RetainedEvidenceCorrespondenceRegistry([
            attestation(
                artifact_hash=artifact_hash,
                claim_text=claim_text,
                evidence_ref="run:1",
                verdict="SUPPORTS",
                attestation_id="support",
                verifier_id="verifier-a",
            ),
            attestation(
                artifact_hash=artifact_hash,
                claim_text=claim_text,
                evidence_ref="run:1",
                verdict="CONTRADICTS",
                attestation_id="contradict",
                verifier_id="verifier-b",
            ),
        ])
        assessment = registry.assess(
            artifact_hash=artifact_hash,
            claim={"claim_id": "c1", "text": claim_text, "evidence_refs": ["run:1"]},
        )
        self.assertEqual(assessment.status, "CONFLICT")
        self.assertEqual(set(assessment.verifier_ids), {"verifier-a", "verifier-b"})

    def test_conflicting_rewrite_of_same_attestation_id_is_rejected(self):
        artifact_hash = content_hash("artifact-v1")
        claim_text = "Deployment completed successfully."
        registry = RetainedEvidenceCorrespondenceRegistry()
        registry.add(attestation(
            artifact_hash=artifact_hash,
            claim_text=claim_text,
            evidence_ref="run:1",
            verdict="SUPPORTS",
            attestation_id="a1",
        ))
        with self.assertRaisesRegex(ValueError, "attestation_id"):
            registry.add(attestation(
                artifact_hash=artifact_hash,
                claim_text=claim_text,
                evidence_ref="run:1",
                verdict="CONTRADICTS",
                attestation_id="a1",
            ))


if __name__ == "__main__":
    unittest.main()
