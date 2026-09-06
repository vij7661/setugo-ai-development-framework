from __future__ import annotations

import argparse
import json
import os
import signal
import sqlite3

from exp_i_composite_journal import DurableCompositeJournalAuthority, DurableCompositeRecord

READY_POINTS = (
    "READY_BEFORE_INSERT",
    "READY_AFTER_PENDING_COMMIT",
    "READY_AFTER_MATERIAL_COMMIT",
    "READY_AFTER_CURRENT_COMMIT",
)


def marker(point: str) -> None:
    print(json.dumps({"ready": point, "pid": os.getpid(), "self_termination": False}), flush=True)
    signal.pause()


def issue_staged(authority: DurableCompositeJournalAuthority, issuance_id: str, generation: int, ready_point: str | None):
    if ready_point == "READY_BEFORE_INSERT":
        marker(ready_point)

    pair = authority._pair.current_pair()
    con = authority._connect()
    try:
        con.execute("BEGIN IMMEDIATE")
        existing_row = con.execute(
            "SELECT * FROM composite_checkpoint_journal WHERE issuance_id=?",
            (issuance_id,),
        ).fetchone()
        existing = authority._row_to_record(existing_row)
        predecessor = authority._expected_predecessor(con, generation)
        prototype = DurableCompositeRecord(
            issuance_id=issuance_id,
            scope=authority._scope,
            generation=generation,
            permit_ledger_digest=pair["permit_ledger_digest"],
            reconciliation_digest=pair["reconciliation_digest"],
            permit_authority_epoch=pair["permit_authority_epoch"],
            previous_checkpoint_digest=predecessor,
            status="PENDING",
            tag="",
        )
        if existing is not None:
            if authority._semantic_tuple(existing) != authority._semantic_tuple(prototype):
                raise PermissionError("issuance identity semantic rebinding denied")
            con.rollback()
            if existing.status == "CURRENT" and authority._authentic(existing):
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
        if ready_point == "READY_AFTER_PENDING_COMMIT":
            marker(ready_point)

        pending_tag = authority._sign_payload(prototype.payload())
        con.execute("BEGIN IMMEDIATE")
        con.execute(
            "UPDATE composite_checkpoint_journal SET tag=? WHERE issuance_id=? AND status='PENDING'",
            (pending_tag, issuance_id),
        )
        con.commit()
        if ready_point == "READY_AFTER_MATERIAL_COMMIT":
            marker(ready_point)

        current_record = DurableCompositeRecord(
            issuance_id=issuance_id,
            scope=authority._scope,
            generation=generation,
            permit_ledger_digest=pair["permit_ledger_digest"],
            reconciliation_digest=pair["reconciliation_digest"],
            permit_authority_epoch=pair["permit_authority_epoch"],
            previous_checkpoint_digest=predecessor,
            status="CURRENT",
            tag="",
        )
        current_tag = authority._sign_payload(current_record.payload())
        con.execute("BEGIN IMMEDIATE")
        row = con.execute(
            "SELECT * FROM composite_checkpoint_journal WHERE issuance_id=?",
            (issuance_id,),
        ).fetchone()
        durable = authority._row_to_record(row)
        if durable is None or durable.status != "PENDING":
            raise PermissionError("issuance no longer pending")
        if authority._semantic_tuple(durable) != authority._semantic_tuple(current_record):
            raise PermissionError("durable issuance changed before promotion")
        promotion = con.execute(
            "UPDATE composite_checkpoint_journal SET status='CURRENT', tag=? WHERE issuance_id=? AND status='PENDING'",
            (current_tag, issuance_id),
        )
        if promotion.rowcount != 1:
            raise PermissionError("current promotion lost race")
        con.commit()
        if ready_point == "READY_AFTER_CURRENT_COMMIT":
            marker(ready_point)
        result = authority.get(issuance_id)
        if result is None:
            raise RuntimeError("durable current checkpoint missing after commit")
        return result
    except sqlite3.IntegrityError as exc:
        try:
            con.rollback()
        except sqlite3.Error:
            pass
        raise PermissionError("conflicting generation or issuance") from exc
    finally:
        con.close()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True)
    p.add_argument("--issuance-id", required=True)
    p.add_argument("--generation", type=int, required=True)
    p.add_argument("--permit-integrity-key", required=True)
    p.add_argument("--reconciliation-integrity-key", required=True)
    p.add_argument("--composite-key", required=True)
    p.add_argument("--ready-point", choices=READY_POINTS)
    args = p.parse_args()

    authority = DurableCompositeJournalAuthority(
        args.db,
        bytes.fromhex(args.permit_integrity_key),
        bytes.fromhex(args.reconciliation_integrity_key),
        bytes.fromhex(args.composite_key),
    )
    try:
        result = issue_staged(authority, args.issuance_id, args.generation, args.ready_point)
        print(json.dumps({"ok": True, "pid": os.getpid(), "record": result.payload() | {"tag": result.tag}}), flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"ok": False, "pid": os.getpid(), "error": type(exc).__name__, "message": str(exc)}), flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
