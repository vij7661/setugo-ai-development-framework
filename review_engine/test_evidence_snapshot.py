from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.evidence_correspondence import (
    EvidenceCorrespondenceAttestation,
    EvidenceVerifierIdentity,
    claim_fingerprint,
)
from review_engine.evidence_snapshot import EvidenceSnapshot, SQLiteEvidenceSnapshotRegistry
from review_engine.evidence_verifier_qualification import (
    EvidenceVerifierQualificationRecord,
    EvidenceVerifierQualificationRegistry,
)
from review_engine.models import content_hash
from review_engine.sqlite_evidence_correspondence import SQLiteQualifiedEvidenceCorrespondenceRegistry


ARTIFACT_HASH = content_hash("artifact-v1")
CLAIM = "Revenue increased 40%."
EVIDENCE_REF = "report:2026-q3"
SNAPSHOT_HASH = content_hash("retained evidence snapshot")


def verifier_identity() -> EvidenceVerifierIdentity:
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


def snapshot(*, snapshot_id: str = "snapshot-1", digest: str = SNAPSHOT_HASH) -> EvidenceSnapshot:
    return EvidenceSnapshot(
        snapshot_id=snapshot_id,
        evidence_ref=EVIDENCE_REF,
        evidence_content_hash=digest,
        source_locator="connector://retained/report/2026-q3",
        acquisition_provenance="trusted-source-ingestion-test",
    )


def attestation(*, digest: str = SNAPSHOT_HASH) -> EvidenceCorrespondenceAttestation:
    identity = verifier_identity()
    return EvidenceCorrespondenceAttestation(
        attestation_id="a1",
        artifact_hash=ARTIFACT_HASH,
        claim_fingerprint=claim_fingerprint(CLAIM),
        evidence_ref=EVIDENCE_REF,
        evidence_content_hash=digest,
        verdict="SUPPORTS",
        verifier_id=identity.verifier_id,
        provenance="snapshot-binding-test",
        qualification_ref=identity.qualification_ref,
        verifier_identity=identity,
    )


class EvidenceSnapshotTests(unittest.TestCase):
    def test_snapshot_manifest_survives_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "snapshots.db"
            first = SQLiteEvidenceSnapshotRegistry(path)
            first.add(snapshot())
            restarted = SQLiteEvidenceSnapshotRegistry(path)
            self.assertEqual(restarted.get("snapshot-1"), snapshot())
            self.assertTrue(restarted.has_exact_snapshot(
                evidence_ref=EVIDENCE_REF,
                evidence_content_hash=SNAPSHOT_HASH,
            ))

    def test_attestation_hash_must_match_retained_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            snapshots = SQLiteEvidenceSnapshotRegistry(Path(td) / "snapshots.db")
            snapshots.add(snapshot())
            correspondence = SQLiteQualifiedEvidenceCorrespondenceRegistry(
                Path(td) / "correspondence.db",
                qualifications(),
                snapshot_registry=snapshots,
            )
            with self.assertRaisesRegex(ValueError, "retained evidence snapshot"):
                correspondence.add(attestation(digest=content_hash("invented snapshot")))
            correspondence.add(attestation())

    def test_reference_only_without_retained_snapshot_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            snapshots = SQLiteEvidenceSnapshotRegistry(Path(td) / "snapshots.db")
            correspondence = SQLiteQualifiedEvidenceCorrespondenceRegistry(
                Path(td) / "correspondence.db",
                qualifications(),
                snapshot_registry=snapshots,
            )
            with self.assertRaisesRegex(ValueError, "retained evidence snapshot"):
                correspondence.add(attestation())

    def test_conflicting_snapshot_id_rewrite_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            registry = SQLiteEvidenceSnapshotRegistry(Path(td) / "snapshots.db")
            registry.add(snapshot())
            with self.assertRaisesRegex(ValueError, "snapshot_id"):
                registry.add(EvidenceSnapshot(
                    snapshot_id="snapshot-1",
                    evidence_ref=EVIDENCE_REF,
                    evidence_content_hash=content_hash("other"),
                    source_locator="connector://retained/report/other",
                    acquisition_provenance="rewrite-test",
                ))


if __name__ == "__main__":
    unittest.main()
