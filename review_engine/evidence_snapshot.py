from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

BUSY_TIMEOUT_MS = 30_000


def _sha256_hex(value: str, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{field} must be a sha256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{field} must be a sha256 hex digest") from exc
    return value.lower()


@dataclass(frozen=True)
class EvidenceSnapshot:
    """Platform-retained manifest for an exact evidence snapshot.

    This binds an evidence reference to an exact content hash and acquisition
    provenance. It does not by itself prove that an external source was honest
    or that the acquisition path was cryptographically authenticated.
    """

    snapshot_id: str
    evidence_ref: str
    evidence_content_hash: str
    source_locator: str
    acquisition_provenance: str

    def validate(self) -> None:
        for field in (
            "snapshot_id",
            "evidence_ref",
            "source_locator",
            "acquisition_provenance",
        ):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"evidence snapshot {field} required")
        _sha256_hex(self.evidence_content_hash, "evidence_content_hash")


class EvidenceSnapshotRegistry(Protocol):
    durable_snapshot_state_enforced: bool

    def has_exact_snapshot(self, *, evidence_ref: str, evidence_content_hash: str) -> bool: ...


class SQLiteEvidenceSnapshotRegistry:
    """Single-node durable evidence snapshot manifest.

    Admission is a trusted source-ingestion responsibility and intentionally has
    no public Review Engine HTTP write surface. SQLite persistence is not WORM or
    proof of the external source's authenticity.
    """

    durable_snapshot_state_enforced = True

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._init_schema()

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
                CREATE TABLE IF NOT EXISTS evidence_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    evidence_ref TEXT NOT NULL,
                    evidence_content_hash TEXT NOT NULL,
                    source_locator TEXT NOT NULL,
                    acquisition_provenance TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(evidence_ref, evidence_content_hash)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_evidence_snapshot_lookup "
                "ON evidence_snapshots(evidence_ref, evidence_content_hash)"
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> EvidenceSnapshot:
        snapshot = EvidenceSnapshot(
            snapshot_id=row["snapshot_id"],
            evidence_ref=row["evidence_ref"],
            evidence_content_hash=row["evidence_content_hash"],
            source_locator=row["source_locator"],
            acquisition_provenance=row["acquisition_provenance"],
        )
        snapshot.validate()
        return snapshot

    def add(self, snapshot: EvidenceSnapshot) -> None:
        snapshot.validate()
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            by_id = conn.execute(
                "SELECT * FROM evidence_snapshots WHERE snapshot_id=?",
                (snapshot.snapshot_id,),
            ).fetchone()
            if by_id is not None:
                if self._from_row(by_id) == snapshot:
                    conn.commit()
                    return
                raise ValueError("conflicting evidence snapshot_id")

            by_binding = conn.execute(
                "SELECT * FROM evidence_snapshots WHERE evidence_ref=? AND evidence_content_hash=?",
                (snapshot.evidence_ref, snapshot.evidence_content_hash.lower()),
            ).fetchone()
            if by_binding is not None:
                if self._from_row(by_binding) == snapshot:
                    conn.commit()
                    return
                raise ValueError("conflicting retained evidence snapshot binding")

            conn.execute(
                """
                INSERT INTO evidence_snapshots (
                    snapshot_id, evidence_ref, evidence_content_hash,
                    source_locator, acquisition_provenance
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    snapshot.snapshot_id,
                    snapshot.evidence_ref,
                    snapshot.evidence_content_hash.lower(),
                    snapshot.source_locator,
                    snapshot.acquisition_provenance,
                ),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get(self, snapshot_id: str) -> EvidenceSnapshot | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM evidence_snapshots WHERE snapshot_id=?",
                (snapshot_id,),
            ).fetchone()
        return None if row is None else self._from_row(row)

    def has_exact_snapshot(self, *, evidence_ref: str, evidence_content_hash: str) -> bool:
        if not isinstance(evidence_ref, str) or not evidence_ref.strip():
            raise ValueError("evidence_ref required")
        digest = _sha256_hex(evidence_content_hash, "evidence_content_hash")
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM evidence_snapshots WHERE evidence_ref=? AND evidence_content_hash=? LIMIT 1",
                (evidence_ref, digest),
            ).fetchone()
        return row is not None
