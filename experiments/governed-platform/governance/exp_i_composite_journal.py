from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple

from exp_i_composite_integrity import CompositeIntegrityAuthority

SCOPE = "EXP-I-COMPOSITE-JOURNAL"


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


@dataclass(frozen=True)
class DurableCompositeRecord:
    issuance_id: str
    scope: str
    generation: int
    permit_ledger_digest: str
    reconciliation_digest: str
    permit_authority_epoch: int
    previous_checkpoint_digest: str
    status: str
    tag: str

    def payload(self) -> dict[str, Any]:
        return {
            "issuance_id": self.issuance_id,
            "scope": self.scope,
            "generation": self.generation,
            "permit_ledger_digest": self.permit_ledger_digest,
            "reconciliation_digest": self.reconciliation_digest,
            "permit_authority_epoch": self.permit_authority_epoch,
            "previous_checkpoint_digest": self.previous_checkpoint_digest,
            "status": self.status,
        }

    def record_digest(self) -> str:
        return _sha({"payload": self.payload(), "tag": self.tag})


@dataclass(frozen=True)
class DurableCompositeDecision:
    valid: bool
    reasons: Tuple[str, ...]
    reviewer_generated_authority: bool = False
    production_authority: bool = False
    release_authority: bool = False


class DurableCompositeJournalAuthority:
    def __init__(
        self,
        db_path: str | Path,
        permit_integrity_key: bytes,
        reconciliation_integrity_key: bytes,
        composite_key: bytes,
        *,
        scope: str = SCOPE,
    ):
        if not composite_key:
            raise ValueError("composite key required")
        self._db_path = str(db_path)
        self._pair = CompositeIntegrityAuthority(
            self._db_path,
            permit_integrity_key,
            reconciliation_integrity_key,
            composite_key,
        )
        self._key = bytes(composite_key)
        self._scope = scope
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self._db_path, timeout=5.0)
        con.row_factory = sqlite3.Row
        return con

    def _init_schema(self) -> None:
        con = self._connect()
        try:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS composite_checkpoint_journal (
                    issuance_id TEXT PRIMARY KEY,
                    scope TEXT NOT NULL,
                    generation INTEGER NOT NULL UNIQUE,
                    permit_ledger_digest TEXT NOT NULL,
                    reconciliation_digest TEXT NOT NULL,
                    permit_authority_epoch INTEGER NOT NULL,
                    previous_checkpoint_digest TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('PENDING','CURRENT')),
                    tag TEXT NOT NULL
                )
                """
            )
            con.commit()
        finally:
            con.close()

    def _sign_payload(self, payload: dict[str, Any]) -> str:
        return hmac.new(self._key, _canon(payload), hashlib.sha256).hexdigest()

    def _authentic(self, record: DurableCompositeRecord) -> bool:
        if record.scope != self._scope or record.status not in {"PENDING", "CURRENT"}:
            return False
        if not isinstance(record.generation, int) or record.generation < 1:
            return False
        if not record.tag:
            return False
        return hmac.compare_digest(record.tag, self._sign_payload(record.payload()))

    def _row_to_record(self, row: sqlite3.Row | None) -> DurableCompositeRecord | None:
        if row is None:
            return None
        return DurableCompositeRecord(
            issuance_id=row["issuance_id"],
            scope=row["scope"],
            generation=int(row["generation"]),
            permit_ledger_digest=row["permit_ledger_digest"],
            reconciliation_digest=row["reconciliation_digest"],
            permit_authority_epoch=int(row["permit_authority_epoch"]),
            previous_checkpoint_digest=row["previous_checkpoint_digest"],
            status=row["status"],
            tag=row["tag"],
        )

    def get(self, issuance_id: str) -> DurableCompositeRecord | None:
        con = self._connect()
        try:
            row = con.execute(
                "SELECT * FROM composite_checkpoint_journal WHERE issuance_id=?",
                (issuance_id,),
            ).fetchone()
            return self._row_to_record(row)
        finally:
            con.close()

    def _latest_current(self, con: sqlite3.Connection) -> DurableCompositeRecord | None:
        row = con.execute(
            "SELECT * FROM composite_checkpoint_journal WHERE status='CURRENT' ORDER BY generation DESC LIMIT 1"
        ).fetchone()
        return self._row_to_record(row)

    def latest_current(self) -> DurableCompositeRecord | None:
        con = self._connect()
        try:
            return self._latest_current(con)
        finally:
            con.close()

    def _expected_predecessor(self, con: sqlite3.Connection, generation: int) -> str:
        if generation == 1:
            prior = self._latest_current(con)
            if prior is not None:
                raise PermissionError("generation one cannot follow existing current checkpoint")
            return "GENESIS"
        prior = con.execute(
            "SELECT * FROM composite_checkpoint_journal WHERE generation=? AND status='CURRENT'",
            (generation - 1,),
        ).fetchone()
        prior_record = self._row_to_record(prior)
        if prior_record is None or not self._authentic(prior_record):
            raise PermissionError("missing or invalid durable predecessor")
        return prior_record.record_digest()

    @staticmethod
    def _semantic_tuple(record: DurableCompositeRecord) -> tuple[Any, ...]:
        return (
            record.scope,
            record.generation,
            record.permit_ledger_digest,
            record.reconciliation_digest,
            record.permit_authority_epoch,
            record.previous_checkpoint_digest,
        )

    def issue(
        self,
        issuance_id: str,
        generation: int,
        *,
        crash_at: str | None = None,
    ) -> DurableCompositeRecord:
        if not issuance_id:
            raise ValueError("issuance identity required")
        if not isinstance(generation, int) or generation < 1:
            raise ValueError("generation must be positive")
        if crash_at not in {None, "before_insert", "after_pending", "after_material", "after_current"}:
            raise ValueError("unknown crash point")
        if crash_at == "before_insert":
            raise RuntimeError("simulated crash before journal insert")

        pair = self._pair.current_pair()
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            existing_row = con.execute(
                "SELECT * FROM composite_checkpoint_journal WHERE issuance_id=?",
                (issuance_id,),
            ).fetchone()
            existing = self._row_to_record(existing_row)
            predecessor = self._expected_predecessor(con, generation)
            prototype = DurableCompositeRecord(
                issuance_id=issuance_id,
                scope=self._scope,
                generation=generation,
                permit_ledger_digest=pair["permit_ledger_digest"],
                reconciliation_digest=pair["reconciliation_digest"],
                permit_authority_epoch=pair["permit_authority_epoch"],
                previous_checkpoint_digest=predecessor,
                status="PENDING",
                tag="",
            )
            if existing is not None:
                if self._semantic_tuple(existing) != self._semantic_tuple(prototype):
                    raise PermissionError("issuance identity semantic rebinding denied")
                con.rollback()
                if existing.status == "CURRENT" and self._authentic(existing):
                    return existing
                raise PermissionError("existing non-current issuance requires recovery")

            con.execute(
                """
                INSERT INTO composite_checkpoint_journal(
                    issuance_id, scope, generation, permit_ledger_digest,
                    reconciliation_digest, permit_authority_epoch,
                    previous_checkpoint_digest, status, tag
                ) VALUES(?,?,?,?,?,?,?,?,?)
                """,
                (
                    prototype.issuance_id,
                    prototype.scope,
                    prototype.generation,
                    prototype.permit_ledger_digest,
                    prototype.reconciliation_digest,
                    prototype.permit_authority_epoch,
                    prototype.previous_checkpoint_digest,
                    "PENDING",
                    "",
                ),
            )
            con.commit()
            if crash_at == "after_pending":
                raise RuntimeError("simulated crash after pending insert")

            pending_payload = prototype.payload()
            pending_tag = self._sign_payload(pending_payload)
            con.execute("BEGIN IMMEDIATE")
            con.execute(
                "UPDATE composite_checkpoint_journal SET tag=? WHERE issuance_id=? AND status='PENDING'",
                (pending_tag, issuance_id),
            )
            con.commit()
            if crash_at == "after_material":
                raise RuntimeError("simulated crash after durable authenticated material")

            current_record = DurableCompositeRecord(
                issuance_id=issuance_id,
                scope=self._scope,
                generation=generation,
                permit_ledger_digest=pair["permit_ledger_digest"],
                reconciliation_digest=pair["reconciliation_digest"],
                permit_authority_epoch=pair["permit_authority_epoch"],
                previous_checkpoint_digest=predecessor,
                status="CURRENT",
                tag="",
            )
            current_tag = self._sign_payload(current_record.payload())
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT * FROM composite_checkpoint_journal WHERE issuance_id=?",
                (issuance_id,),
            ).fetchone()
            durable = self._row_to_record(row)
            if durable is None or durable.status != "PENDING":
                raise PermissionError("issuance no longer pending")
            if self._semantic_tuple(durable) != self._semantic_tuple(current_record):
                raise PermissionError("durable issuance changed before promotion")
            con.execute(
                "UPDATE composite_checkpoint_journal SET status='CURRENT', tag=? WHERE issuance_id=? AND status='PENDING'",
                (current_tag, issuance_id),
            )
            if con.total_changes != 1:
                raise PermissionError("current promotion lost race")
            con.commit()
            result = self.get(issuance_id)
            assert result is not None
            if crash_at == "after_current":
                raise RuntimeError("simulated crash after current commit")
            return result
        except sqlite3.IntegrityError as exc:
            try:
                con.rollback()
            except sqlite3.Error:
                pass
            raise PermissionError("conflicting generation or issuance") from exc
        finally:
            con.close()

    def recover(self, issuance_id: str) -> DurableCompositeDecision:
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT * FROM composite_checkpoint_journal WHERE issuance_id=?",
                (issuance_id,),
            ).fetchone()
            record = self._row_to_record(row)
            if record is None:
                con.rollback()
                return DurableCompositeDecision(False, ("missing durable issuance",))
            if record.status == "CURRENT":
                con.rollback()
                return self.verify_record(record, trusted_min_generation=record.generation)
            if record.status != "PENDING":
                con.rollback()
                return DurableCompositeDecision(False, ("invalid durable issuance status",))
            if not self._authentic(record):
                con.rollback()
                return DurableCompositeDecision(False, ("pending issuance lacks valid authenticated material",))
            try:
                expected_predecessor = self._expected_predecessor(con, record.generation)
                current_pair = self._pair.current_pair()
            except (PermissionError, RuntimeError) as exc:
                con.rollback()
                return DurableCompositeDecision(False, (str(exc),))
            if record.previous_checkpoint_digest != expected_predecessor:
                con.rollback()
                return DurableCompositeDecision(False, ("pending predecessor no longer current",))
            if record.permit_ledger_digest != current_pair["permit_ledger_digest"]:
                con.rollback()
                return DurableCompositeDecision(False, ("pending permit-ledger binding no longer current",))
            if record.reconciliation_digest != current_pair["reconciliation_digest"]:
                con.rollback()
                return DurableCompositeDecision(False, ("pending reconciliation binding no longer current",))
            if record.permit_authority_epoch != current_pair["permit_authority_epoch"]:
                con.rollback()
                return DurableCompositeDecision(False, ("pending permit-authority epoch no longer current",))
            current = DurableCompositeRecord(
                issuance_id=record.issuance_id,
                scope=record.scope,
                generation=record.generation,
                permit_ledger_digest=record.permit_ledger_digest,
                reconciliation_digest=record.reconciliation_digest,
                permit_authority_epoch=record.permit_authority_epoch,
                previous_checkpoint_digest=record.previous_checkpoint_digest,
                status="CURRENT",
                tag="",
            )
            tag = self._sign_payload(current.payload())
            con.execute(
                "UPDATE composite_checkpoint_journal SET status='CURRENT', tag=? WHERE issuance_id=? AND status='PENDING'",
                (tag, issuance_id),
            )
            if con.total_changes != 1:
                con.rollback()
                return DurableCompositeDecision(False, ("pending recovery lost race",))
            con.commit()
            return DurableCompositeDecision(True, ("pending issuance reconciled to current exactly once",))
        finally:
            con.close()

    def verify_record(
        self,
        record: DurableCompositeRecord | None,
        *,
        trusted_min_generation: int,
    ) -> DurableCompositeDecision:
        if record is None:
            return DurableCompositeDecision(False, ("missing durable composite checkpoint",))
        if not isinstance(trusted_min_generation, int) or trusted_min_generation < 1:
            return DurableCompositeDecision(False, ("invalid trusted minimum generation",))
        if record.status != "CURRENT":
            return DurableCompositeDecision(False, ("durable composite checkpoint not current",))
        if record.generation < trusted_min_generation:
            return DurableCompositeDecision(False, ("durable composite checkpoint below trusted minimum",))
        if not self._authentic(record):
            return DurableCompositeDecision(False, ("invalid durable composite authentication",))
        con = self._connect()
        try:
            durable_row = con.execute(
                "SELECT * FROM composite_checkpoint_journal WHERE issuance_id=?",
                (record.issuance_id,),
            ).fetchone()
            durable = self._row_to_record(durable_row)
            if durable is None:
                return DurableCompositeDecision(False, ("durable composite journal entry missing",))
            if durable != record:
                return DurableCompositeDecision(False, ("supplied composite record differs from durable journal",))
            current_at_generation = con.execute(
                "SELECT COUNT(*) FROM composite_checkpoint_journal WHERE generation=? AND status='CURRENT'",
                (record.generation,),
            ).fetchone()[0]
            if current_at_generation != 1:
                return DurableCompositeDecision(False, ("ambiguous current checkpoint generation",))
            if record.generation == 1:
                if record.previous_checkpoint_digest != "GENESIS":
                    return DurableCompositeDecision(False, ("invalid durable genesis predecessor",))
            else:
                prev_row = con.execute(
                    "SELECT * FROM composite_checkpoint_journal WHERE generation=? AND status='CURRENT'",
                    (record.generation - 1,),
                ).fetchone()
                prev = self._row_to_record(prev_row)
                if prev is None or not self._authentic(prev) or record.previous_checkpoint_digest != prev.record_digest():
                    return DurableCompositeDecision(False, ("durable predecessor mismatch",))
        finally:
            con.close()
        try:
            pair = self._pair.current_pair()
        except RuntimeError as exc:
            return DurableCompositeDecision(False, (str(exc),))
        if record.permit_ledger_digest != pair["permit_ledger_digest"]:
            return DurableCompositeDecision(False, ("current permit-ledger digest mismatch",))
        if record.reconciliation_digest != pair["reconciliation_digest"]:
            return DurableCompositeDecision(False, ("current reconciliation digest mismatch",))
        if record.permit_authority_epoch != pair["permit_authority_epoch"]:
            return DurableCompositeDecision(False, ("current permit-authority epoch mismatch",))
        return DurableCompositeDecision(True, ("durable composite record matches current governance state",))

    def verify_latest(self, *, trusted_min_generation: int) -> DurableCompositeDecision:
        record = self.latest_current()
        return self.verify_record(record, trusted_min_generation=trusted_min_generation)
