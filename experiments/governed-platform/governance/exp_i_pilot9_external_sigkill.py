"""EXP-I Pilot 9: externally killed composite-checkpoint writer at frozen cut points."""
from __future__ import annotations

import argparse
import json
import os
import signal
import sqlite3
from pathlib import Path
from typing import Any

from exp_i_composite_journal import DurableCompositeJournalAuthority, DurableCompositeRecord

READY_POINTS = (
    "READY_BEFORE_PENDING_INSERT",
    "READY_AFTER_PENDING_COMMIT",
    "READY_AFTER_AUTHENTICATED_PENDING_COMMIT",
    "READY_AFTER_CURRENT_UPDATE_BEFORE_COMMIT",
    "READY_AFTER_CURRENT_COMMIT_BEFORE_RESPONSE",
)


def _canon(value: Any) -> bytes:
    import json as _json
    return _json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _ready_and_block(point: str | None, expected: str) -> None:
    if point != expected:
        return
    print(json.dumps({"ready": expected, "pid": os.getpid(), "self_termination": False}), flush=True)
    while True:
        signal.pause()


def issue_with_external_cut(
    journal: DurableCompositeJournalAuthority,
    issuance_id: str,
    generation: int,
    ready_point: str | None,
) -> DurableCompositeRecord:
    if ready_point not in (None, *READY_POINTS):
        raise ValueError("unknown readiness point")
    if not issuance_id:
        raise ValueError("issuance identity required")
    if not isinstance(generation, int) or generation < 1:
        raise ValueError("generation must be positive")

    pair = journal._pair.current_pair()  # test harness exercises the frozen Pilot 8 mechanism internals
    con = journal._connect()
    try:
        con.execute("BEGIN IMMEDIATE")
        existing_row = con.execute(
            "SELECT * FROM composite_checkpoint_journal WHERE issuance_id=?",
            (issuance_id,),
        ).fetchone()
        existing = journal._row_to_record(existing_row)
        predecessor = journal._expected_predecessor(con, generation)
        prototype = DurableCompositeRecord(
            issuance_id=issuance_id,
            scope=journal._scope,
            generation=generation,
            permit_ledger_digest=pair["permit_ledger_digest"],
            reconciliation_digest=pair["reconciliation_digest"],
            permit_authority_epoch=pair["permit_authority_epoch"],
            previous_checkpoint_digest=predecessor,
            status="PENDING",
            tag="",
        )
        if existing is not None:
            if journal._semantic_tuple(existing) != journal._semantic_tuple(prototype):
                con.rollback()
                raise PermissionError("issuance identity semantic rebinding denied")
            con.rollback()
            if existing.status == "CURRENT" and journal._authentic(existing):
                return existing
            raise PermissionError("existing non-current issuance requires recovery")

        _ready_and_block(ready_point, "READY_BEFORE_PENDING_INSERT")
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
        _ready_and_block(ready_point, "READY_AFTER_PENDING_COMMIT")

        pending_payload = prototype.payload()
        pending_tag = journal._sign_payload(pending_payload)
        con.execute("BEGIN IMMEDIATE")
        update = con.execute(
            "UPDATE composite_checkpoint_journal SET tag=? WHERE issuance_id=? AND status='PENDING'",
            (pending_tag, issuance_id),
        )
        if update.rowcount != 1:
            con.rollback()
            raise PermissionError("pending authentication lost race")
        con.commit()
        _ready_and_block(ready_point, "READY_AFTER_AUTHENTICATED_PENDING_COMMIT")

        current_record = DurableCompositeRecord(
            issuance_id=issuance_id,
            scope=journal._scope,
            generation=generation,
            permit_ledger_digest=pair["permit_ledger_digest"],
            reconciliation_digest=pair["reconciliation_digest"],
            permit_authority_epoch=pair["permit_authority_epoch"],
            previous_checkpoint_digest=predecessor,
            status="CURRENT",
            tag="",
        )
        current_tag = journal._sign_payload(current_record.payload())
        con.execute("BEGIN IMMEDIATE")
        row = con.execute(
            "SELECT * FROM composite_checkpoint_journal WHERE issuance_id=?",
            (issuance_id,),
        ).fetchone()
        durable = journal._row_to_record(row)
        if durable is None or durable.status != "PENDING":
            con.rollback()
            raise PermissionError("issuance no longer pending")
        if journal._semantic_tuple(durable) != journal._semantic_tuple(current_record):
            con.rollback()
            raise PermissionError("durable issuance changed before promotion")
        promotion = con.execute(
            "UPDATE composite_checkpoint_journal SET status='CURRENT', tag=? WHERE issuance_id=? AND status='PENDING'",
            (current_tag, issuance_id),
        )
        if promotion.rowcount != 1:
            con.rollback()
            raise PermissionError("current promotion lost race")
        _ready_and_block(ready_point, "READY_AFTER_CURRENT_UPDATE_BEFORE_COMMIT")
        con.commit()
        _ready_and_block(ready_point, "READY_AFTER_CURRENT_COMMIT_BEFORE_RESPONSE")
        result = journal.get(issuance_id)
        if result is None:
            raise RuntimeError("durable checkpoint missing after commit")
        return result
    except sqlite3.IntegrityError as exc:
        try:
            con.rollback()
        except sqlite3.Error:
            pass
        raise PermissionError("conflicting generation or issuance") from exc
    finally:
        con.close()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--issuance-id", required=True)
    ap.add_argument("--generation", required=True, type=int)
    ap.add_argument("--ready-point")
    ap.add_argument("--permit-integrity-key", required=True)
    ap.add_argument("--reconciliation-integrity-key", required=True)
    ap.add_argument("--composite-key", required=True)
    args = ap.parse_args(argv)

    journal = DurableCompositeJournalAuthority(
        Path(args.db),
        args.permit_integrity_key.encode("utf-8"),
        args.reconciliation_integrity_key.encode("utf-8"),
        args.composite_key.encode("utf-8"),
    )
    record = issue_with_external_cut(journal, args.issuance_id, args.generation, args.ready_point)
    print(json.dumps({"issuance_id": record.issuance_id, "generation": record.generation, "status": record.status, "record_digest": record.record_digest()}, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
