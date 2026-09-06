"""EXP-I Pilot 15: externally terminated root-rotation crash consistency.

This module deliberately keeps root-trust history and the trusted minimum in
separate SQLite databases.  A newer root record is not consequentially current
until the independent minimum is reconciled to the exact epoch/digest.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import signal
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any

from exp_i_asymmetric_checkpoint_signer import _canon, _digest
from exp_i_registry_root_isolation import fp
from exp_i_root_rotation import (
    PlatformRootTrustAuthority,
    RootMinimumAuthority,
    _root_record_body,
)


BOUNDARIES = {
    "BEFORE_ROOT_TX",
    "AFTER_ROOT_BEGIN_BEFORE_INSERT",
    "AFTER_ROOT_INSERT_BEFORE_COMMIT",
    "AFTER_ROOT_COMMIT_BEFORE_MINIMUM",
    "AFTER_MINIMUM_BEGIN_BEFORE_MUTATION",
    "AFTER_MINIMUM_MUTATION_BEFORE_COMMIT",
    "AFTER_MINIMUM_COMMIT_BEFORE_ACK",
}


def _emit_ready(boundary: str, **extra: Any) -> None:
    print(json.dumps({"ready": True, "boundary": boundary, "pid": os.getpid(), **extra}, sort_keys=True), flush=True)
    # The worker intentionally blocks without cleanup.  The parent must terminate it.
    # EOF also blocks the experiment rather than manufacturing a successful endpoint.
    while True:
        time.sleep(60)


def _root_auth(auth_key_path: str, body: dict[str, Any]) -> str:
    return hmac.new(Path(auth_key_path).read_bytes(), _canon(body), hashlib.sha256).hexdigest()


def _read_root_rows(conn: sqlite3.Connection):
    return conn.execute(
        "SELECT root_epoch,transition_id,record_json,record_digest,record_auth "
        "FROM root_records ORDER BY root_epoch"
    ).fetchall()


def _exact_existing(rows, transition_id: str, expected_prior: str, next_id: str, next_pem: str, activation_registry_epoch: int):
    for er, tid, raw, digest, auth in rows:
        if tid != transition_id:
            continue
        body = json.loads(raw)
        if (
            body.get("prior_root_id") != expected_prior
            or body.get("active_root_id") != next_id
            or body.get("active_public_key_pem") != next_pem
            or int(body.get("activation_registry_epoch", -1)) != int(activation_registry_epoch)
        ):
            raise PermissionError("ROOT_TRANSITION_REBIND_DENIED")
        return {"record": body, "record_digest": str(digest), "record_auth": str(auth)}
    return None


def _rotation_worker(args: argparse.Namespace) -> None:
    if args.boundary not in BOUNDARIES:
        raise SystemExit("UNKNOWN_BOUNDARY")

    # The schema and key are initialized by the parent fixture.  Opening them here
    # must not silently bootstrap or repair authority state.
    root_conn = sqlite3.connect(args.root_db, timeout=10, isolation_level=None)
    min_conn: sqlite3.Connection | None = None
    try:
        if args.boundary == "BEFORE_ROOT_TX":
            _emit_ready(args.boundary)

        root_conn.execute("BEGIN IMMEDIATE")
        if args.boundary == "AFTER_ROOT_BEGIN_BEFORE_INSERT":
            _emit_ready(args.boundary)

        rows = _read_root_rows(root_conn)
        existing = _exact_existing(
            rows,
            args.transition_id,
            args.expected_prior_root_id,
            args.next_root_id,
            args.next_public_key_pem,
            args.activation_registry_epoch,
        )
        if existing is None:
            last = rows[-1] if rows else None
            epoch = 1 if last is None else int(last[0]) + 1
            prior = None if last is None else json.loads(last[2])["active_root_id"]
            if prior != args.expected_prior_root_id:
                raise PermissionError("ROOT_PRIOR_MISMATCH")
            predecessor = "GENESIS" if last is None else str(last[3])
            body = _root_record_body(
                epoch,
                args.transition_id,
                prior,
                args.next_root_id,
                args.next_public_key_pem,
                args.activation_registry_epoch,
                predecessor,
            )
            auth = _root_auth(args.root_auth, body)
            digest = _digest({"record": body, "auth": auth})
            root_conn.execute(
                "INSERT INTO root_records VALUES(?,?,?,?,?)",
                (epoch, args.transition_id, json.dumps(body, sort_keys=True), digest, auth),
            )
            record = {"record": body, "record_digest": digest, "record_auth": auth}
        else:
            record = existing

        if args.boundary == "AFTER_ROOT_INSERT_BEFORE_COMMIT":
            _emit_ready(args.boundary, root_epoch=record["record"]["root_epoch"], record_digest=record["record_digest"])

        root_conn.execute("COMMIT")
        if args.boundary == "AFTER_ROOT_COMMIT_BEFORE_MINIMUM":
            _emit_ready(args.boundary, root_epoch=record["record"]["root_epoch"], record_digest=record["record_digest"])

        min_conn = sqlite3.connect(args.minimum_db, timeout=10, isolation_level=None)
        min_conn.execute("BEGIN IMMEDIATE")
        current = min_conn.execute("SELECT root_epoch,record_digest FROM minimum WHERE id=1").fetchone()
        target_epoch = int(record["record"]["root_epoch"])
        target_digest = str(record["record_digest"])
        if current:
            ce, cd = int(current[0]), str(current[1])
            if target_epoch < ce:
                raise PermissionError("ROOT_MINIMUM_ROLLBACK_DENIED")
            if target_epoch == ce and target_digest != cd:
                raise PermissionError("ROOT_MINIMUM_REBIND_DENIED")

        if args.boundary == "AFTER_MINIMUM_BEGIN_BEFORE_MUTATION":
            _emit_ready(args.boundary, root_epoch=target_epoch, record_digest=target_digest)

        if current is None:
            min_conn.execute("INSERT INTO minimum VALUES(1,?,?)", (target_epoch, target_digest))
        elif target_epoch > int(current[0]):
            min_conn.execute(
                "UPDATE minimum SET root_epoch=?,record_digest=? WHERE id=1",
                (target_epoch, target_digest),
            )

        if args.boundary == "AFTER_MINIMUM_MUTATION_BEFORE_COMMIT":
            _emit_ready(args.boundary, root_epoch=target_epoch, record_digest=target_digest)

        min_conn.execute("COMMIT")
        if args.boundary == "AFTER_MINIMUM_COMMIT_BEFORE_ACK":
            _emit_ready(args.boundary, root_epoch=target_epoch, record_digest=target_digest)

        print(json.dumps({"ok": True, **record}, sort_keys=True), flush=True)
    finally:
        # External-kill endpoints never reach this block. It exists only for a
        # non-killed control invocation and is not scientific crash evidence.
        try:
            root_conn.close()
        finally:
            if min_conn is not None:
                min_conn.close()


class RootRotationRecovery:
    """Fresh-process/connection recovery and consequential-current gate."""

    def __init__(self, root_db: str | Path, root_auth: str | Path, minimum_db: str | Path):
        self.trust = PlatformRootTrustAuthority(root_db, root_auth)
        self.minimum = RootMinimumAuthority(minimum_db)

    def inspect(self) -> dict[str, Any]:
        history = self.trust.history(None)
        latest = history[-1]
        me, md = self.minimum.current()
        reconciled = int(latest["record"]["root_epoch"]) == me and latest["record_digest"] == md
        minimum_entry = history[me - 1] if 0 < me <= len(history) else None
        minimum_valid = minimum_entry is not None and minimum_entry["record_digest"] == md
        return {
            "latest": latest,
            "minimum_epoch": me,
            "minimum_digest": md,
            "minimum_valid": minimum_valid,
            "reconciled": reconciled,
            "ambiguous": minimum_valid and not reconciled,
        }

    def current_for_consequential_use(self) -> dict[str, Any]:
        state = self.inspect()
        if not state["minimum_valid"]:
            raise PermissionError("ROOT_MINIMUM_INVALID")
        if not state["reconciled"]:
            raise PermissionError("ROOT_ROTATION_AMBIGUOUS")
        return state["latest"]

    def reconcile_exact(
        self,
        *,
        transition_id: str,
        expected_prior_root_id: str,
        next_root_id: str,
        next_public_key_pem: str,
        activation_registry_epoch: int,
    ) -> dict[str, Any]:
        history = self.trust.history(None)
        latest = history[-1]
        body = latest["record"]
        expected = {
            "transition_id": transition_id,
            "prior_root_id": expected_prior_root_id,
            "active_root_id": next_root_id,
            "active_public_key_pem": next_public_key_pem,
            "active_public_key_fingerprint": fp(next_public_key_pem),
            "activation_registry_epoch": int(activation_registry_epoch),
        }
        for key, value in expected.items():
            if body.get(key) != value:
                raise PermissionError("ROOT_RECOVERY_SEMANTIC_MISMATCH")

        me, md = self.minimum.current()
        target_epoch = int(body["root_epoch"])
        if target_epoch < me:
            raise PermissionError("ROOT_RECOVERY_BELOW_MINIMUM")
        if target_epoch == me:
            if latest["record_digest"] != md:
                raise PermissionError("ROOT_MINIMUM_REBIND_DENIED")
            return latest
        if target_epoch != me + 1:
            raise PermissionError("ROOT_RECOVERY_NONCONTIGUOUS")
        if body.get("predecessor_root_record_digest") != md:
            raise PermissionError("ROOT_RECOVERY_PREDECESSOR_MISMATCH")

        self.minimum.advance(target_epoch, latest["record_digest"])
        return self.current_for_consequential_use()

    def clean_rotate(
        self,
        *,
        transition_id: str,
        expected_prior_root_id: str,
        next_root_id: str,
        next_public_key_pem: str,
        activation_registry_epoch: int,
    ) -> dict[str, Any]:
        # Refuse to start a new transition while an old one is unresolved.
        self.current_for_consequential_use()
        record = self.trust.rotate(
            transition_id=transition_id,
            expected_prior_root_id=expected_prior_root_id,
            next_root_id=next_root_id,
            next_public_key_pem=next_public_key_pem,
            activation_registry_epoch=activation_registry_epoch,
        )
        self.minimum.advance(int(record["record"]["root_epoch"]), record["record_digest"])
        return self.current_for_consequential_use()

    def root_is_currently_eligible(self, root_id: str, public_key_pem: str) -> bool:
        current = self.current_for_consequential_use()["record"]
        return current["active_root_id"] == root_id and current["active_public_key_fingerprint"] == fp(public_key_pem)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rotation-worker", action="store_true")
    parser.add_argument("--root-db")
    parser.add_argument("--root-auth")
    parser.add_argument("--minimum-db")
    parser.add_argument("--boundary")
    parser.add_argument("--transition-id", default="ROOT-T2")
    parser.add_argument("--expected-prior-root-id", default="R1")
    parser.add_argument("--next-root-id", default="R2")
    parser.add_argument("--next-public-key-pem")
    parser.add_argument("--activation-registry-epoch", type=int, default=1)
    ns = parser.parse_args()
    if not ns.rotation_worker:
        raise SystemExit("ROTATION_WORKER_FLAG_REQUIRED")
    _rotation_worker(ns)
