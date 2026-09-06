"""EXP-I Pilot 9: parent-driven SIGKILL around the exact composite-journal issue() path.

The worker calls DurableCompositeJournalAuthority.issue() unchanged.  A test-only
connection proxy observes the exact SQLite statements/commits and exposes the
preregistered readiness cut points without reimplementing checkpoint semantics.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
from pathlib import Path
from typing import Any, Callable

from exp_i_composite_journal import DurableCompositeJournalAuthority

READY_POINTS = (
    "READY_BEFORE_PENDING_INSERT",
    "READY_AFTER_PENDING_COMMIT",
    "READY_AFTER_AUTHENTICATED_PENDING_COMMIT",
    "READY_AFTER_CURRENT_UPDATE_BEFORE_COMMIT",
    "READY_AFTER_CURRENT_COMMIT_BEFORE_RESPONSE",
)


def _ready_and_block(point: str | None, expected: str) -> None:
    if point != expected:
        return
    print(json.dumps({"ready": expected, "pid": os.getpid(), "self_termination": False}), flush=True)
    while True:
        signal.pause()


class _ObservedConnection:
    """Transparent test-only proxy over the exact sqlite3.Connection used by issue()."""

    def __init__(self, inner: Any, ready_point: str):
        self._inner = inner
        self._ready_point = ready_point
        self._phase: str | None = None

    def execute(self, sql: str, parameters: Any = ()):
        normalized = " ".join(sql.split()).upper()

        if normalized.startswith("INSERT INTO COMPOSITE_CHECKPOINT_JOURNAL"):
            _ready_and_block(self._ready_point, "READY_BEFORE_PENDING_INSERT")
            cursor = self._inner.execute(sql, parameters)
            self._phase = "PENDING_INSERT_EXECUTED"
            return cursor

        if normalized.startswith("UPDATE COMPOSITE_CHECKPOINT_JOURNAL SET TAG="):
            cursor = self._inner.execute(sql, parameters)
            self._phase = "PENDING_AUTH_UPDATE_EXECUTED"
            return cursor

        if normalized.startswith("UPDATE COMPOSITE_CHECKPOINT_JOURNAL SET STATUS='CURRENT'"):
            cursor = self._inner.execute(sql, parameters)
            self._phase = "CURRENT_UPDATE_EXECUTED"
            _ready_and_block(self._ready_point, "READY_AFTER_CURRENT_UPDATE_BEFORE_COMMIT")
            return cursor

        return self._inner.execute(sql, parameters)

    def commit(self) -> None:
        phase = self._phase
        self._inner.commit()
        if phase == "PENDING_INSERT_EXECUTED":
            self._phase = "PENDING_COMMITTED"
            _ready_and_block(self._ready_point, "READY_AFTER_PENDING_COMMIT")
        elif phase == "PENDING_AUTH_UPDATE_EXECUTED":
            self._phase = "PENDING_AUTH_COMMITTED"
            _ready_and_block(self._ready_point, "READY_AFTER_AUTHENTICATED_PENDING_COMMIT")
        elif phase == "CURRENT_UPDATE_EXECUTED":
            self._phase = "CURRENT_COMMITTED"
            _ready_and_block(self._ready_point, "READY_AFTER_CURRENT_COMMIT_BEFORE_RESPONSE")

    def rollback(self) -> None:
        return self._inner.rollback()

    def close(self) -> None:
        return self._inner.close()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)


def _instrument_exact_issue_path(journal: DurableCompositeJournalAuthority, ready_point: str) -> None:
    if ready_point not in READY_POINTS:
        raise ValueError("unknown readiness point")
    original_connect: Callable[[], Any] = journal._connect

    def observed_connect() -> _ObservedConnection:
        return _ObservedConnection(original_connect(), ready_point)

    journal._connect = observed_connect  # type: ignore[method-assign]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", required=True)
    ap.add_argument("--issuance-id", required=True)
    ap.add_argument("--generation", required=True, type=int)
    ap.add_argument("--ready-point", required=True, choices=READY_POINTS)
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
    _instrument_exact_issue_path(journal, args.ready_point)

    # Exact frozen mechanism under test; no duplicated issue transition exists here.
    record = journal.issue(args.issuance_id, args.generation)
    print(
        json.dumps(
            {
                "issuance_id": record.issuance_id,
                "generation": record.generation,
                "status": record.status,
                "record_digest": record.record_digest(),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
