from __future__ import annotations

import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

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
from review_engine.sqlite_evidence_correspondence import SQLiteQualifiedEvidenceCorrespondenceRegistry


ARTIFACT_HASH = content_hash("artifact-v1")
CLAIM = "Revenue increased 40%."
EVIDENCE_REF = "report:2026-q3"


def identity() -> EvidenceVerifierIdentity:
    return EvidenceVerifierIdentity(
        provider="verifier-provider",
        model="verifier-model",
        sku="default",
        deployment_path="api",
        foundation_lineage="verifier-lineage",
        qualification_ref="evidence-verifier-q1",
        qualification_epoch=1,
    )


def qualifications() -> EvidenceVerifierQualificationRegistry:
    return EvidenceVerifierQualificationRegistry((
        EvidenceVerifierQualificationRecord(
            qualification_ref="evidence-verifier-q1",
            provider="verifier-provider",
            model="verifier-model",
            sku="default",
            deployment_path="api",
            foundation_lineage="verifier-lineage",
            status="QUALIFIED",
            qualification_epoch=1,
            max_risk="HIGH",
            task_types=("RESEARCH",),
        ),
    ))


def attestation(*, attestation_id: str = "a1", verdict: str = "SUPPORTS") -> EvidenceCorrespondenceAttestation:
    verifier = identity()
    return EvidenceCorrespondenceAttestation(
        attestation_id=attestation_id,
        artifact_hash=ARTIFACT_HASH,
        claim_fingerprint=claim_fingerprint(CLAIM),
        evidence_ref=EVIDENCE_REF,
        evidence_content_hash=content_hash("retained evidence snapshot"),
        verdict=verdict,
        verifier_id=verifier.verifier_id,
        provenance="sqlite-qualified-verifier-test",
        qualification_ref=verifier.qualification_ref,
        verifier_identity=verifier,
    )


def claim() -> dict:
    return {"claim_id": "c1", "text": CLAIM, "evidence_refs": [EVIDENCE_REF]}


class SQLiteEvidenceCorrespondenceTests(unittest.TestCase):
    def test_attestation_survives_registry_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.db"
            q = qualifications()
            first = SQLiteQualifiedEvidenceCorrespondenceRegistry(path, q)
            record = attestation()
            first.add(record)

            restarted = SQLiteQualifiedEvidenceCorrespondenceRegistry(path, q)
            self.assertEqual(restarted.get("a1"), record)
            assessment = restarted.assess(
                artifact_hash=ARTIFACT_HASH,
                claim=claim(),
                risk="HIGH",
                task_type="RESEARCH",
            )
            self.assertEqual(assessment.status, "VERIFIED_SUPPORT")

    def test_conflicting_rewrite_of_persisted_attestation_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.db"
            q = qualifications()
            registry = SQLiteQualifiedEvidenceCorrespondenceRegistry(path, q)
            registry.add(attestation())
            with self.assertRaisesRegex(ValueError, "attestation_id"):
                registry.add(attestation(verdict="CONTRADICTS"))

    def test_revocation_after_restart_removes_persisted_support(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.db"
            q = qualifications()
            first = SQLiteQualifiedEvidenceCorrespondenceRegistry(path, q)
            first.add(attestation())
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
            restarted = SQLiteQualifiedEvidenceCorrespondenceRegistry(path, q)
            assessment = restarted.assess(
                artifact_hash=ARTIFACT_HASH,
                claim=claim(),
                risk="LOW",
                task_type="RESEARCH",
            )
            self.assertEqual(assessment.status, "UNVERIFIED")

    def test_concurrent_conflicting_admission_cannot_both_win(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.db"
            q = qualifications()
            first = SQLiteQualifiedEvidenceCorrespondenceRegistry(path, q)
            second = SQLiteQualifiedEvidenceCorrespondenceRegistry(path, q)

            def add(registry, verdict):
                try:
                    registry.add(attestation(verdict=verdict))
                    return "ADDED"
                except ValueError as exc:
                    return str(exc)

            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(
                    lambda args: add(*args),
                    ((first, "SUPPORTS"), (second, "CONTRADICTS")),
                ))

            self.assertEqual(outcomes.count("ADDED"), 1)
            failures = [value for value in outcomes if value != "ADDED"]
            self.assertEqual(len(failures), 1)
            self.assertIn("attestation_id", failures[0])
            persisted = SQLiteQualifiedEvidenceCorrespondenceRegistry(path, q).get("a1")
            self.assertIsNotNone(persisted)
            self.assertIn(persisted.verdict, {"SUPPORTS", "CONTRADICTS"})


if __name__ == "__main__":
    unittest.main()
