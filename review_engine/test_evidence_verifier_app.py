from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from review_engine.app import ReviewEngineApp
from review_engine.configuration import ReviewEngineConfiguration
from review_engine.evidence_correspondence import (
    EvidenceCorrespondenceAttestation,
    EvidenceVerifierIdentity,
    RetainedEvidenceCorrespondenceRegistry,
    claim_fingerprint,
)
from review_engine.evidence_snapshot import EvidenceSnapshot, SQLiteEvidenceSnapshotRegistry
from review_engine.evidence_verifier_qualification import (
    EvidenceVerifierQualificationRecord,
    EvidenceVerifierQualificationRegistry,
)
from review_engine.models import ReviewerConfig, ReviewerResponse, content_hash
from review_engine.qualification import QualificationRecord
from review_engine.qualified_evidence_correspondence import QualifiedRetainedEvidenceCorrespondenceRegistry
from review_engine.request_boundary import PlatformExecutionEnvelope
from review_engine.sqlite_evidence_correspondence import SQLiteQualifiedEvidenceCorrespondenceRegistry


ARTIFACT = "Revenue increased 40%."
CLAIM = ARTIFACT
EVIDENCE_REF = "report:2026-q3"
EVIDENCE_CONTENT = "retained evidence snapshot"
EVIDENCE_HASH = content_hash(EVIDENCE_CONTENT)


def reviewer() -> ReviewerConfig:
    return ReviewerConfig(
        role="R1",
        provider="fake",
        model="reviewer-model",
        sku="default",
        deployment_path="api",
        api_key_env="R1_KEY",
        foundation_lineage="reviewer-lineage",
        qualification_ref="r1-q1",
    )


def governed_configuration() -> ReviewEngineConfiguration:
    return ReviewEngineConfiguration(
        reviewers={"R1": reviewer()},
        provider_specs={},
        qualification_records=(
            QualificationRecord(
                qualification_ref="r1-q1",
                provider="fake",
                model="reviewer-model",
                sku="default",
                deployment_path="api",
                role="R1",
                status="QUALIFIED",
                qualification_epoch=1,
                foundation_lineage="reviewer-lineage",
                max_risk="HIGH",
                task_types=("RESEARCH",),
            ),
        ),
    )


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


def verifier_qualifications(*, max_risk: str = "LOW") -> EvidenceVerifierQualificationRegistry:
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
            max_risk=max_risk,
            task_types=("RESEARCH",),
        ),
    ))


def retained_snapshot() -> EvidenceSnapshot:
    return EvidenceSnapshot(
        snapshot_id="snapshot-1",
        evidence_ref=EVIDENCE_REF,
        evidence_content_hash=EVIDENCE_HASH,
        source_locator="connector://retained/report/2026-q3",
        acquisition_provenance="trusted-source-ingestion-test",
    )


def support_attestation() -> EvidenceCorrespondenceAttestation:
    identity = verifier_identity()
    return EvidenceCorrespondenceAttestation(
        attestation_id="a1",
        artifact_hash=content_hash(ARTIFACT),
        claim_fingerprint=claim_fingerprint(CLAIM),
        evidence_ref=EVIDENCE_REF,
        evidence_content_hash=EVIDENCE_HASH,
        verdict="SUPPORTS",
        verifier_id=identity.verifier_id,
        provenance="qualified-verifier-app-test",
        qualification_ref=identity.qualification_ref,
        verifier_identity=identity,
    )


def snapshot_registry(td: str) -> SQLiteEvidenceSnapshotRegistry:
    registry = SQLiteEvidenceSnapshotRegistry(Path(td) / "snapshots.db")
    registry.add(retained_snapshot())
    return registry


class FakeProviders:
    def invoke(self, config, context):
        return ReviewerResponse(
            role="R1",
            artifact_hash=None,
            output=ARTIFACT,
            findings=(),
            proposed_signals={},
            epistemic_review={
                "version": "TVC-1",
                "correspondence": "SUPPORTED",
                "coherence": "CONSISTENT",
                "pragmatic": "NOT_APPLICABLE",
                "semantic": "PRECISE",
                "claims": [
                    {
                        "claim_id": "c1",
                        "text": CLAIM,
                        "claim_type": "EMPIRICAL_FACT",
                        "correspondence": "SUPPORTED",
                        "evidence_refs": [EVIDENCE_REF],
                        "material": True,
                    }
                ],
                "contradiction_refs": [],
            },
        )


class EvidenceVerifierApplicationTests(unittest.TestCase):
    def test_governed_app_rejects_raw_correspondence_registry(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "qualified verifier assessment"):
                ReviewEngineApp(
                    governed_configuration(),
                    memory_db=str(Path(td) / "memory.db"),
                    sessions_db=str(Path(td) / "sessions.db"),
                    provider_registry=FakeProviders(),
                    execution_envelope=PlatformExecutionEnvelope(task_type="RESEARCH"),
                    evidence_validator=RetainedEvidenceCorrespondenceRegistry(),
                )

    def test_governed_app_rejects_qualified_but_in_memory_correspondence_registry(self):
        validator = QualifiedRetainedEvidenceCorrespondenceRegistry(
            verifier_qualifications(max_risk="HIGH")
        )
        validator.add(support_attestation())
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "durable evidence correspondence attestation state"):
                ReviewEngineApp(
                    governed_configuration(),
                    memory_db=str(Path(td) / "memory.db"),
                    sessions_db=str(Path(td) / "sessions.db"),
                    provider_registry=FakeProviders(),
                    execution_envelope=PlatformExecutionEnvelope(task_type="RESEARCH"),
                    evidence_validator=validator,
                )

    def test_governed_app_rejects_durable_correspondence_without_snapshot_binding(self):
        with tempfile.TemporaryDirectory() as td:
            validator = SQLiteQualifiedEvidenceCorrespondenceRegistry(
                Path(td) / "correspondence.db",
                verifier_qualifications(max_risk="HIGH"),
            )
            validator.add(support_attestation())
            with self.assertRaisesRegex(ValueError, "retained evidence snapshots"):
                ReviewEngineApp(
                    governed_configuration(),
                    memory_db=str(Path(td) / "memory.db"),
                    sessions_db=str(Path(td) / "sessions.db"),
                    provider_registry=FakeProviders(),
                    execution_envelope=PlatformExecutionEnvelope(task_type="RESEARCH"),
                    evidence_validator=validator,
                )

    def test_governed_app_accepts_durable_snapshot_bound_qualified_correspondence_registry(self):
        with tempfile.TemporaryDirectory() as td:
            snapshots = snapshot_registry(td)
            validator = SQLiteQualifiedEvidenceCorrespondenceRegistry(
                Path(td) / "correspondence.db",
                verifier_qualifications(max_risk="HIGH"),
                snapshot_registry=snapshots,
            )
            validator.add(support_attestation())
            app = ReviewEngineApp(
                governed_configuration(),
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=FakeProviders(),
                execution_envelope=PlatformExecutionEnvelope(task_type="RESEARCH"),
                evidence_validator=validator,
            )
            health = app.health()
            self.assertEqual(health["assurance_mode"], "GOVERNED")
            self.assertTrue(health["evidence_correspondence_qualified_verifier"])
            self.assertTrue(health["evidence_correspondence_durable_attestation_state"])
            self.assertTrue(health["evidence_correspondence_retained_snapshot_binding"])
            self.assertTrue(health["evidence_correspondence_durable_snapshot_state"])

    def test_actual_review_risk_is_used_for_snapshot_bound_verifier_qualification(self):
        # The attestation is valid for LOW risk only. If the orchestrator silently
        # used the validator's default LOW scope, this would false-green as
        # VERIFIED_SUPPORT. The HIGH request must make it UNVERIFIED instead.
        with tempfile.TemporaryDirectory() as td:
            snapshots = snapshot_registry(td)
            validator = SQLiteQualifiedEvidenceCorrespondenceRegistry(
                Path(td) / "correspondence.db",
                verifier_qualifications(max_risk="LOW"),
                snapshot_registry=snapshots,
            )
            validator.add(support_attestation())
            app = ReviewEngineApp(
                governed_configuration(),
                memory_db=str(Path(td) / "memory.db"),
                sessions_db=str(Path(td) / "sessions.db"),
                provider_registry=FakeProviders(),
                execution_envelope=PlatformExecutionEnvelope(task_type="RESEARCH"),
                evidence_validator=validator,
            )
            result = app.review({
                "request_id": "verifier-risk-scope",
                "user_input": "analyze the retained revenue result",
                "risk": "HIGH",
            })
            self.assertEqual(result["state"], "HUMAN_REQUIRED")
            events = app.session_events("verifier-risk-scope")
            r1 = next(event for event in events if event["event_type"] == "R1_COMPLETED")
            assessments = r1["payload"]["evidence_correspondence"]
            self.assertEqual(len(assessments), 1)
            self.assertEqual(assessments[0]["status"], "UNVERIFIED")
            findings = r1["payload"]["findings"]
            self.assertTrue(any(
                finding["violated_invariant"] == "TVC-EVIDENCE-CORRESPONDENCE"
                for finding in findings
            ))


if __name__ == "__main__":
    unittest.main()
