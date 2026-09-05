from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import uuid4

from .claim_coverage import ClaimCoverageInventory, ClaimExtractorIdentity
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
    """Single-node durable extraction-work ledger with atomic consumption.

    Issued and consumed work state survives process restart. `consume_for_inventory`
    validates the inventory and marks the order consumed in one SQLite write
    transaction, so concurrent consumers of one work order cannot both succeed.

    This is not distributed consensus, an externally immutable/WORM ledger,
    a cryptographically signed capability, or proof of remote provider runtime
    identity. A privileged SQLite writer can still rewrite the database.
    """

    durable_replay_protection_enforced = True

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

        # UUID collision is already extraordinarily unlikely; retry a bounded
        # number of times so uniqueness remains a database-enforced invariant.
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

    def consume_for_inventory(
        self,
        work_order_id: str,
        inventory: ClaimCoverageInventory,
    ) -> ExtractionWorkOrder:
        """Atomically validate and consume one work order for one inventory."""
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
