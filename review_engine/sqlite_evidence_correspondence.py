from __future__ import annotations

import sqlite3
from pathlib import Path

from .evidence_correspondence import (
    ClaimEvidenceAssessment,
    EvidenceCorrespondenceAttestation,
    EvidenceVerifierIdentity,
    RetainedEvidenceCorrespondenceRegistry,
)
from .evidence_snapshot import EvidenceSnapshotRegistry
from .evidence_verifier_qualification import EvidenceVerifierQualificationRegistry

BUSY_TIMEOUT_MS = 30_000


class SQLiteQualifiedEvidenceCorrespondenceRegistry:
    """Single-node durable store for qualified evidence correspondence.

    The store persists exact attestation/verifier bindings and re-evaluates
    verifier qualification for the actual review risk/task at assessment time.
    When a snapshot registry is configured, admission also requires an exact
    retained evidence_ref + content-hash binding. SQLite durability is not
    WORM/external immutability; a privileged database writer can still rewrite
    either store.
    """

    qualified_verifier_assessment_enforced = True
    durable_attestation_state_enforced = True

    def __init__(
        self,
        path: str | Path,
        qualification_registry: EvidenceVerifierQualificationRegistry,
        snapshot_registry: EvidenceSnapshotRegistry | None = None,
    ) -> None:
        self.path = str(path)
        self._qualifications = qualification_registry
        self._snapshots = snapshot_registry
        self._init_schema()

    @property
    def retained_snapshot_binding_enforced(self) -> bool:
        return self._snapshots is not None

    @property
    def durable_snapshot_state_enforced(self) -> bool:
        return bool(
            getattr(self._snapshots, "durable_snapshot_state_enforced", False)
        ) if self._snapshots is not None else False

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=BUSY_TIMEOUT_MS / 1000)
        conn.row_factory = sqlite3.Row
        conn.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evidence_correspondence_attestations (
                    attestation_id TEXT PRIMARY KEY,
                    artifact_hash TEXT NOT NULL,
                    claim_fingerprint TEXT NOT NULL,
                    evidence_ref TEXT NOT NULL,
                    evidence_content_hash TEXT NOT NULL,
                    verdict TEXT NOT NULL,
                    verifier_id TEXT NOT NULL,
                    provenance TEXT NOT NULL,
                    qualification_ref TEXT NOT NULL,
                    verifier_provider TEXT NOT NULL,
                    verifier_model TEXT NOT NULL,
                    verifier_sku TEXT NOT NULL,
                    verifier_deployment_path TEXT NOT NULL,
                    verifier_foundation_lineage TEXT NOT NULL,
                    verifier_qualification_epoch INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(artifact_hash, claim_fingerprint, evidence_ref, verifier_id)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_evidence_correspondence_lookup "
                "ON evidence_correspondence_attestations(artifact_hash, claim_fingerprint, evidence_ref)"
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> EvidenceCorrespondenceAttestation:
        identity = EvidenceVerifierIdentity(
            provider=row["verifier_provider"],
            model=row["verifier_model"],
            sku=row["verifier_sku"],
            deployment_path=row["verifier_deployment_path"],
            foundation_lineage=row["verifier_foundation_lineage"],
            qualification_ref=row["qualification_ref"],
            qualification_epoch=int(row["verifier_qualification_epoch"]),
        )
        attestation = EvidenceCorrespondenceAttestation(
            attestation_id=row["attestation_id"],
            artifact_hash=row["artifact_hash"],
            claim_fingerprint=row["claim_fingerprint"],
            evidence_ref=row["evidence_ref"],
            evidence_content_hash=row["evidence_content_hash"],
            verdict=row["verdict"],
            verifier_id=row["verifier_id"],
            provenance=row["provenance"],
            qualification_ref=row["qualification_ref"],
            verifier_identity=identity,
        )
        attestation.validate()
        return attestation

    def _check_static_qualification(self, attestation: EvidenceCorrespondenceAttestation) -> None:
        identity = attestation.verifier_identity
        if identity is None:
            raise ValueError("durable qualified evidence correspondence requires structured verifier identity")
        record = self._qualifications.get(identity.qualification_ref)
        if record is None:
            raise ValueError("evidence verifier qualification reference not found")
        if record.status != "QUALIFIED":
            raise ValueError(f"evidence verifier qualification status is {record.status}")
        bindings = {
            "provider": (record.provider, identity.provider),
            "model": (record.model, identity.model),
            "sku": (record.sku, identity.sku),
            "deployment_path": (record.deployment_path, identity.deployment_path),
            "foundation_lineage": (record.foundation_lineage, identity.foundation_lineage),
            "qualification_epoch": (record.qualification_epoch, identity.qualification_epoch),
        }
        for name, (expected, actual) in bindings.items():
            if expected != actual:
                raise ValueError(f"evidence verifier qualification {name} binding mismatch")

    def _check_snapshot_binding(self, attestation: EvidenceCorrespondenceAttestation) -> None:
        if self._snapshots is None:
            return
        if not self._snapshots.has_exact_snapshot(
            evidence_ref=attestation.evidence_ref,
            evidence_content_hash=attestation.evidence_content_hash,
        ):
            raise ValueError(
                "evidence correspondence attestation does not match a retained evidence snapshot"
            )

    def add(self, attestation: EvidenceCorrespondenceAttestation) -> None:
        attestation.validate()
        self._check_static_qualification(attestation)
        self._check_snapshot_binding(attestation)
        identity = attestation.verifier_identity
        assert identity is not None

        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            by_id = conn.execute(
                "SELECT * FROM evidence_correspondence_attestations WHERE attestation_id=?",
                (attestation.attestation_id,),
            ).fetchone()
            if by_id is not None:
                if self._from_row(by_id) == attestation:
                    conn.commit()
                    return
                raise ValueError("conflicting evidence attestation_id")

            by_binding = conn.execute(
                """
                SELECT * FROM evidence_correspondence_attestations
                WHERE artifact_hash=? AND claim_fingerprint=? AND evidence_ref=? AND verifier_id=?
                """,
                (
                    attestation.artifact_hash.lower(),
                    attestation.claim_fingerprint.lower(),
                    attestation.evidence_ref,
                    attestation.verifier_id,
                ),
            ).fetchone()
            if by_binding is not None:
                if self._from_row(by_binding) == attestation:
                    conn.commit()
                    return
                raise ValueError("conflicting retained evidence correspondence attestation")

            conn.execute(
                """
                INSERT INTO evidence_correspondence_attestations (
                    attestation_id, artifact_hash, claim_fingerprint, evidence_ref,
                    evidence_content_hash, verdict, verifier_id, provenance,
                    qualification_ref, verifier_provider, verifier_model, verifier_sku,
                    verifier_deployment_path, verifier_foundation_lineage,
                    verifier_qualification_epoch
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attestation.attestation_id,
                    attestation.artifact_hash.lower(),
                    attestation.claim_fingerprint.lower(),
                    attestation.evidence_ref,
                    attestation.evidence_content_hash.lower(),
                    attestation.verdict,
                    attestation.verifier_id,
                    attestation.provenance,
                    identity.qualification_ref,
                    identity.provider,
                    identity.model,
                    identity.sku,
                    identity.deployment_path,
                    identity.foundation_lineage,
                    identity.qualification_epoch,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get(self, attestation_id: str) -> EvidenceCorrespondenceAttestation | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM evidence_correspondence_attestations WHERE attestation_id=?",
                (attestation_id,),
            ).fetchone()
        return None if row is None else self._from_row(row)

    def assess(
        self,
        *,
        artifact_hash: str,
        claim: dict,
        risk: str = "LOW",
        task_type: str = "GENERAL",
    ) -> ClaimEvidenceAssessment:
        artifact_hash, _, fingerprint, evidence_refs = RetainedEvidenceCorrespondenceRegistry._claim_inputs(
            artifact_hash=artifact_hash,
            claim=claim,
        )
        if not evidence_refs:
            return RetainedEvidenceCorrespondenceRegistry.assessment_from_records(
                artifact_hash=artifact_hash,
                claim=claim,
                records=(),
            )

        placeholders = ",".join("?" for _ in evidence_refs)
        sql = (
            "SELECT * FROM evidence_correspondence_attestations "
            "WHERE artifact_hash=? AND claim_fingerprint=? "
            f"AND evidence_ref IN ({placeholders})"
        )
        with self._connect() as conn:
            rows = conn.execute(sql, (artifact_hash, fingerprint, *evidence_refs)).fetchall()

        eligible: list[EvidenceCorrespondenceAttestation] = []
        for row in rows:
            attestation = self._from_row(row)
            identity = attestation.verifier_identity
            assert identity is not None
            decision = self._qualifications.evaluate(identity, risk=risk, task_type=task_type)
            if not decision.eligible:
                continue
            # Recheck the retained snapshot at assessment time as well. If a
            # future snapshot registry supports revocation/removal, stale source
            # evidence must not keep producing VERIFIED_SUPPORT.
            if self._snapshots is not None and not self._snapshots.has_exact_snapshot(
                evidence_ref=attestation.evidence_ref,
                evidence_content_hash=attestation.evidence_content_hash,
            ):
                continue
            eligible.append(attestation)

        return RetainedEvidenceCorrespondenceRegistry.assessment_from_records(
            artifact_hash=artifact_hash,
            claim=claim,
            records=eligible,
        )
