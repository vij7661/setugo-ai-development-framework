from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

from .claim_coverage import (
    ClaimCoverageInventory,
    ClaimExtractorIdentity,
    CoverageClaim,
)
from .extraction_work import ExtractionWorkOrder
from .extractor_qualification import ExtractorQualificationRegistry, RISK_ORDER

BUSY_TIMEOUT_MS = 30_000


def _sha256_hex(value: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError("artifact_hash must be a sha256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError("artifact_hash must be a sha256 hex digest") from exc
    return value.lower()


class SQLiteExtractionWorkRegistry:
    """Single-node durable extraction-work and admitted-inventory ledger.

    Issued/consumed work and admitted claim-coverage inventory state survive
    process restart. `consume_for_inventory` validates the inventory, persists
    the exact inventory and marks the work order consumed in one `BEGIN
    IMMEDIATE` transaction. A conflict while retaining the inventory therefore
    rolls back work consumption as well.

    This is not distributed consensus, an externally immutable/WORM ledger,
    a cryptographically signed capability, or proof of remote provider runtime
    identity. A privileged SQLite writer can still rewrite the database.
    """

    durable_replay_protection_enforced = True
    durable_inventory_state_enforced = True
    atomic_inventory_admission_enforced = True

    def __init__(
        self,
        path: str | Path,
        qualification_registry: ExtractorQualificationRegistry,
    ) -> None:
        self.path = str(path)
        self._qualifications = qualification_registry
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
                CREATE TABLE IF NOT EXISTS extraction_work_orders (
                    work_order_id TEXT PRIMARY KEY,
                    artifact_hash TEXT NOT NULL,
                    risk TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    extractor_id TEXT NOT NULL,
                    qualification_ref TEXT NOT NULL,
                    qualification_epoch INTEGER NOT NULL,
                    issued_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    consumed_at TEXT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_extraction_work_artifact ON extraction_work_orders(artifact_hash)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_extraction_work_unconsumed ON extraction_work_orders(consumed_at, work_order_id)"
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS claim_coverage_inventories (
                    inventory_id TEXT PRIMARY KEY,
                    work_order_id TEXT NOT NULL UNIQUE,
                    artifact_hash TEXT NOT NULL,
                    extractor_id TEXT NOT NULL,
                    extractor_provider TEXT NOT NULL,
                    extractor_model TEXT NOT NULL,
                    extractor_sku TEXT NOT NULL,
                    extractor_deployment_path TEXT NOT NULL,
                    extractor_foundation_lineage TEXT NOT NULL,
                    qualification_ref TEXT NOT NULL,
                    qualification_epoch INTEGER NOT NULL,
                    provenance TEXT NOT NULL,
                    complete INTEGER NOT NULL,
                    admitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(artifact_hash, extractor_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS claim_coverage_inventory_claims (
                    inventory_id TEXT NOT NULL,
                    claim_index INTEGER NOT NULL,
                    claim_fingerprint TEXT NOT NULL,
                    claim_text TEXT NOT NULL,
                    claim_type TEXT NOT NULL,
                    material INTEGER NOT NULL,
                    PRIMARY KEY(inventory_id, claim_index),
                    UNIQUE(inventory_id, claim_fingerprint)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_claim_coverage_artifact "
                "ON claim_coverage_inventories(artifact_hash, inventory_id)"
            )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> ExtractionWorkOrder:
        order = ExtractionWorkOrder(
            work_order_id=row["work_order_id"],
            artifact_hash=row["artifact_hash"],
            risk=row["risk"],
            task_type=row["task_type"],
            extractor_id=row["extractor_id"],
            qualification_ref=row["qualification_ref"],
            qualification_epoch=int(row["qualification_epoch"]),
        )
        order.validate()
        return order

    def issue(
        self,
        *,
        artifact_hash: str,
        extractor_identity: ClaimExtractorIdentity,
        risk: str,
        task_type: str = "GENERAL",
    ) -> ExtractionWorkOrder:
        artifact_hash = _sha256_hex(artifact_hash)
        decision = self._qualifications.evaluate(
            extractor_identity,
            risk=risk,
            task_type=task_type,
        )
        if not decision.eligible:
            raise ValueError(f"cannot issue extraction work: {decision.reason}")
        if risk not in RISK_ORDER:
            raise ValueError("invalid extraction work-order risk")

        for _ in range(3):
            order = ExtractionWorkOrder(
                work_order_id="extract-work:" + uuid4().hex,
                artifact_hash=artifact_hash,
                risk=risk,
                task_type=task_type,
                extractor_id=extractor_identity.extractor_id,
                qualification_ref=decision.qualification_ref or extractor_identity.qualification_ref,
                qualification_epoch=decision.qualification_epoch or extractor_identity.qualification_epoch,
            )
            order.validate()
            try:
                with self._connect() as conn:
                    conn.execute(
                        """
                        INSERT INTO extraction_work_orders(
                            work_order_id, artifact_hash, risk, task_type, extractor_id,
                            qualification_ref, qualification_epoch
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            order.work_order_id,
                            order.artifact_hash,
                            order.risk,
                            order.task_type,
                            order.extractor_id,
                            order.qualification_ref,
                            order.qualification_epoch,
                        ),
                    )
                return order
            except sqlite3.IntegrityError:
                continue
        raise RuntimeError("unable to allocate unique extraction work_order_id")

    def _validate_row_inventory(
        self,
        row: sqlite3.Row,
        inventory: ClaimCoverageInventory,
    ) -> ExtractionWorkOrder:
        inventory.validate()
        order = self._from_row(row)
        if row["consumed_at"] is not None:
            raise ValueError("extraction work order already consumed")
        if inventory.artifact_hash.lower() != order.artifact_hash:
            raise ValueError("extraction inventory artifact does not match work order")
        identity = inventory.extractor_identity
        if identity.extractor_id != order.extractor_id:
            raise ValueError("extraction inventory extractor does not match work order")
        if identity.qualification_ref != order.qualification_ref:
            raise ValueError("extraction inventory qualification_ref does not match work order")
        if identity.qualification_epoch != order.qualification_epoch:
            raise ValueError("extraction inventory qualification_epoch does not match work order")

        decision = self._qualifications.evaluate(
            identity,
            risk=order.risk,
            task_type=order.task_type,
        )
        if not decision.eligible:
            raise ValueError(f"extraction work no longer qualified: {decision.reason}")
        return order

    def validate_inventory(
        self,
        work_order_id: str,
        inventory: ClaimCoverageInventory,
    ) -> ExtractionWorkOrder:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM extraction_work_orders WHERE work_order_id=?",
                (work_order_id,),
            ).fetchone()
        if row is None:
            raise ValueError("extraction work order not found")
        return self._validate_row_inventory(row, inventory)

    @staticmethod
    def _persist_inventory(
        conn: sqlite3.Connection,
        work_order_id: str,
        inventory: ClaimCoverageInventory,
    ) -> None:
        identity = inventory.extractor_identity
        try:
            conn.execute(
                """
                INSERT INTO claim_coverage_inventories(
                    inventory_id, work_order_id, artifact_hash, extractor_id,
                    extractor_provider, extractor_model, extractor_sku,
                    extractor_deployment_path, extractor_foundation_lineage,
                    qualification_ref, qualification_epoch, provenance, complete
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    inventory.inventory_id,
                    work_order_id,
                    inventory.artifact_hash.lower(),
                    identity.extractor_id,
                    identity.provider,
                    identity.model,
                    identity.sku,
                    identity.deployment_path,
                    identity.foundation_lineage,
                    identity.qualification_ref,
                    identity.qualification_epoch,
                    inventory.provenance,
                    1 if inventory.complete else 0,
                ),
            )
            for index, claim in enumerate(inventory.claims):
                conn.execute(
                    """
                    INSERT INTO claim_coverage_inventory_claims(
                        inventory_id, claim_index, claim_fingerprint,
                        claim_text, claim_type, material
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        inventory.inventory_id,
                        index,
                        claim.fingerprint,
                        claim.text,
                        claim.claim_type,
                        1 if claim.material else 0,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            raise ValueError("conflicting retained claim coverage inventory") from exc

    def consume_for_inventory(
        self,
        work_order_id: str,
        inventory: ClaimCoverageInventory,
    ) -> ExtractionWorkOrder:
        """Atomically retain one inventory and consume its work order."""
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT * FROM extraction_work_orders WHERE work_order_id=?",
                (work_order_id,),
            ).fetchone()
            if row is None:
                raise ValueError("extraction work order not found")
            order = self._validate_row_inventory(row, inventory)
            self._persist_inventory(conn, work_order_id, inventory)
            updated = conn.execute(
                """
                UPDATE extraction_work_orders
                   SET consumed_at=CURRENT_TIMESTAMP
                 WHERE work_order_id=? AND consumed_at IS NULL
                """,
                (work_order_id,),
            )
            if updated.rowcount != 1:
                raise ValueError("extraction work order already consumed")
            conn.commit()
            return order
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def retained_inventories(self, artifact_hash: str) -> tuple[ClaimCoverageInventory, ...]:
        artifact_hash = _sha256_hex(artifact_hash)
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM claim_coverage_inventories WHERE artifact_hash=? ORDER BY inventory_id",
                (artifact_hash,),
            ).fetchall()
            inventories: list[ClaimCoverageInventory] = []
            for row in rows:
                claim_rows = conn.execute(
                    """
                    SELECT * FROM claim_coverage_inventory_claims
                    WHERE inventory_id=? ORDER BY claim_index
                    """,
                    (row["inventory_id"],),
                ).fetchall()
                identity = ClaimExtractorIdentity(
                    provider=row["extractor_provider"],
                    model=row["extractor_model"],
                    sku=row["extractor_sku"],
                    deployment_path=row["extractor_deployment_path"],
                    foundation_lineage=row["extractor_foundation_lineage"],
                    qualification_ref=row["qualification_ref"],
                    qualification_epoch=int(row["qualification_epoch"]),
                )
                inventory = ClaimCoverageInventory(
                    inventory_id=row["inventory_id"],
                    artifact_hash=row["artifact_hash"],
                    claims=tuple(
                        CoverageClaim(
                            claim_row["claim_text"],
                            claim_row["claim_type"],
                            bool(claim_row["material"]),
                        )
                        for claim_row in claim_rows
                    ),
                    extractor_identity=identity,
                    provenance=row["provenance"],
                    complete=bool(row["complete"]),
                )
                inventory.validate()
                inventories.append(inventory)
        return tuple(inventories)

    def retained_inventory(self, inventory_id: str) -> ClaimCoverageInventory | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT artifact_hash FROM claim_coverage_inventories WHERE inventory_id=?",
                (inventory_id,),
            ).fetchone()
        if row is None:
            return None
        return next(
            (item for item in self.retained_inventories(row["artifact_hash"]) if item.inventory_id == inventory_id),
            None,
        )

    def consume(self, work_order_id: str) -> None:
        conn = self._connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT consumed_at FROM extraction_work_orders WHERE work_order_id=?",
                (work_order_id,),
            ).fetchone()
            if row is None:
                raise ValueError("extraction work order not found")
            if row["consumed_at"] is not None:
                raise ValueError("extraction work order already consumed")
            updated = conn.execute(
                "UPDATE extraction_work_orders SET consumed_at=CURRENT_TIMESTAMP WHERE work_order_id=? AND consumed_at IS NULL",
                (work_order_id,),
            )
            if updated.rowcount != 1:
                raise ValueError("extraction work order already consumed")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get(self, work_order_id: str) -> ExtractionWorkOrder | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM extraction_work_orders WHERE work_order_id=?",
                (work_order_id,),
            ).fetchone()
        return None if row is None else self._from_row(row)

    def is_consumed(self, work_order_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT consumed_at FROM extraction_work_orders WHERE work_order_id=?",
                (work_order_id,),
            ).fetchone()
        if row is None:
            return False
        return row["consumed_at"] is not None
