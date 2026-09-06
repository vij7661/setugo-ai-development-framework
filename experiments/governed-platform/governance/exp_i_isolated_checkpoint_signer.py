"""EXP-I Pilot 10: isolated composite-checkpoint signer and keyless writer."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

from exp_i_composite_integrity import CompositeIntegrityAuthority, SCOPE

VERSION = "exp-i-pilot10-v1"


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


def _sign(statement: Mapping[str, Any], key: bytes) -> str:
    return hmac.new(key, _canon(dict(statement)), hashlib.sha256).hexdigest()


def init_signer_store(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path), isolation_level=None)
    try:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS signer_issued(
                issuance_id TEXT PRIMARY KEY,
                generation INTEGER NOT NULL UNIQUE,
                statement_json TEXT NOT NULL,
                checkpoint_digest TEXT NOT NULL,
                auth_tag TEXT NOT NULL
            )
            """
        )
        con.execute(
            "CREATE TABLE IF NOT EXISTS signer_meta(singleton INTEGER PRIMARY KEY CHECK(singleton=1), max_generation INTEGER NOT NULL)"
        )
        con.execute("INSERT OR IGNORE INTO signer_meta(singleton,max_generation) VALUES(1,0)")
    finally:
        con.close()


def init_writer_journal(path: str | Path) -> None:
    con = sqlite3.connect(str(path), isolation_level=None)
    try:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS isolated_composite_journal(
                issuance_id TEXT PRIMARY KEY,
                generation INTEGER NOT NULL UNIQUE,
                statement_json TEXT NOT NULL,
                checkpoint_digest TEXT NOT NULL,
                auth_tag TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status='CURRENT')
            )
            """
        )
    finally:
        con.close()


def _current_pair(state_db: str, permit_key: bytes, reconciliation_key: bytes, composite_key: bytes) -> dict[str, Any]:
    return CompositeIntegrityAuthority(state_db, permit_key, reconciliation_key, composite_key).current_pair()


def _issue(
    signer_store: str,
    state_db: str,
    issuance_id: str,
    generation: int,
    scope: str,
    permit_key: bytes,
    reconciliation_key: bytes,
    composite_key: bytes,
) -> dict[str, Any]:
    if not issuance_id or not isinstance(generation, int) or generation < 1:
        return {"ok": False, "reason": "REQUEST_INVALID"}
    if scope != SCOPE:
        return {"ok": False, "reason": "SCOPE_INVALID"}

    pair = _current_pair(state_db, permit_key, reconciliation_key, composite_key)
    con = sqlite3.connect(signer_store, timeout=10.0, isolation_level=None)
    con.row_factory = sqlite3.Row
    try:
        con.execute("BEGIN IMMEDIATE")
        max_generation = int(con.execute("SELECT max_generation FROM signer_meta WHERE singleton=1").fetchone()[0])
        existing = con.execute("SELECT * FROM signer_issued WHERE issuance_id=?", (issuance_id,)).fetchone()
        if existing is not None:
            stored = json.loads(existing["statement_json"])
            if int(existing["generation"]) != generation:
                con.execute("ROLLBACK")
                return {"ok": False, "reason": "ISSUANCE_SEMANTIC_REBINDING"}
            if (
                stored["permit_ledger_digest"] != pair["permit_ledger_digest"]
                or stored["reconciliation_digest"] != pair["reconciliation_digest"]
                or int(stored["permit_authority_epoch"]) != int(pair["permit_authority_epoch"])
            ):
                con.execute("ROLLBACK")
                return {"ok": False, "reason": "STATE_DRIFT_REPLAY_DENIED"}
            con.execute("COMMIT")
            return {
                "ok": True,
                "replay": True,
                "statement": stored,
                "checkpoint_digest": str(existing["checkpoint_digest"]),
                "auth_tag": str(existing["auth_tag"]),
            }

        if generation != max_generation + 1:
            con.execute("ROLLBACK")
            return {
                "ok": False,
                "reason": "GENERATION_NOT_EXACT_NEXT",
                "maximum": max_generation,
            }

        conflict = con.execute("SELECT issuance_id FROM signer_issued WHERE generation=?", (generation,)).fetchone()
        if conflict is not None:
            con.execute("ROLLBACK")
            return {"ok": False, "reason": "SAME_GENERATION_CONFLICT"}

        if generation == 1:
            predecessor = "GENESIS"
        else:
            prev = con.execute(
                "SELECT checkpoint_digest FROM signer_issued WHERE generation=?",
                (generation - 1,),
            ).fetchone()
            if prev is None:
                con.execute("ROLLBACK")
                return {"ok": False, "reason": "PREDECESSOR_MISSING"}
            predecessor = str(prev[0])

        statement = {
            "version": VERSION,
            "scope": SCOPE,
            "issuance_id": issuance_id,
            "generation": generation,
            "permit_ledger_digest": pair["permit_ledger_digest"],
            "reconciliation_digest": pair["reconciliation_digest"],
            "permit_authority_epoch": pair["permit_authority_epoch"],
            "previous_checkpoint_digest": predecessor,
        }
        tag = _sign(statement, composite_key)
        digest = _digest({"statement": statement, "auth_tag": tag})
        con.execute(
            "INSERT INTO signer_issued VALUES(?,?,?,?,?)",
            (issuance_id, generation, json.dumps(statement, sort_keys=True), digest, tag),
        )
        con.execute("UPDATE signer_meta SET max_generation=? WHERE singleton=1", (generation,))
        con.execute("COMMIT")
        return {"ok": True, "replay": False, "statement": statement, "checkpoint_digest": digest, "auth_tag": tag}
    except sqlite3.IntegrityError:
        try:
            con.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        return {"ok": False, "reason": "SIGNER_CONFLICT"}
    finally:
        con.close()


def _verify(
    record: Mapping[str, Any],
    state_db: str,
    minimum_generation: int,
    permit_key: bytes,
    reconciliation_key: bytes,
    composite_key: bytes,
) -> dict[str, Any]:
    try:
        statement = dict(record["statement"])
        tag = str(record["auth_tag"])
        digest = str(record["checkpoint_digest"])
    except Exception:
        return {"ok": False, "reason": "CHECKPOINT_MALFORMED"}
    if set(statement) != {
        "version", "scope", "issuance_id", "generation", "permit_ledger_digest",
        "reconciliation_digest", "permit_authority_epoch", "previous_checkpoint_digest",
    }:
        return {"ok": False, "reason": "CHECKPOINT_SCHEMA_INVALID"}
    if statement["version"] != VERSION or statement["scope"] != SCOPE:
        return {"ok": False, "reason": "CHECKPOINT_SCOPE_VERSION_INVALID"}
    if _digest({"statement": statement, "auth_tag": tag}) != digest:
        return {"ok": False, "reason": "CHECKPOINT_DIGEST_MISMATCH"}
    if not hmac.compare_digest(_sign(statement, composite_key), tag):
        return {"ok": False, "reason": "CHECKPOINT_AUTH_FAILED"}
    if int(statement["generation"]) < int(minimum_generation):
        return {"ok": False, "reason": "CHECKPOINT_ROLLBACK"}
    pair = _current_pair(state_db, permit_key, reconciliation_key, composite_key)
    if statement["permit_ledger_digest"] != pair["permit_ledger_digest"]:
        return {"ok": False, "reason": "PERMIT_LEDGER_DRIFT"}
    if statement["reconciliation_digest"] != pair["reconciliation_digest"]:
        return {"ok": False, "reason": "RECONCILIATION_DRIFT"}
    if int(statement["permit_authority_epoch"]) != int(pair["permit_authority_epoch"]):
        return {"ok": False, "reason": "PERMIT_EPOCH_DRIFT"}
    return {"ok": True, "checkpoint_digest": digest, "statement": statement}


class IsolatedCompositeSignerProcess:
    """Coordinator-side handle. Keys are used only to seed child env and are not retained on this object."""

    def __init__(
        self,
        *,
        signer_store: str | Path,
        state_db: str | Path,
        permit_integrity_key: bytes,
        reconciliation_integrity_key: bytes,
        composite_key: bytes,
    ):
        self.signer_store = str(signer_store)
        self.state_db = str(state_db)
        init_signer_store(self.signer_store)
        env = dict(os.environ)
        env["EXP_I_P10_PERMIT_KEY_HEX"] = permit_integrity_key.hex()
        env["EXP_I_P10_RECON_KEY_HEX"] = reconciliation_integrity_key.hex()
        env["EXP_I_P10_COMPOSITE_KEY_HEX"] = composite_key.hex()
        self.argv = [sys.executable, str(Path(__file__).resolve()), "--worker", self.signer_store, self.state_db]
        self.proc = subprocess.Popen(
            self.argv,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
        )
        assert self.proc.stdout is not None
        ready = json.loads(self.proc.stdout.readline())
        self.pid = int(ready["pid"])

    def call(self, request: Mapping[str, Any]) -> dict[str, Any]:
        if self.proc.poll() is not None:
            return {"ok": False, "reason": "SIGNER_UNAVAILABLE"}
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(dict(request), sort_keys=True) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line) if line else {"ok": False, "reason": "SIGNER_RESPONSE_LOST"}

    def issue(self, issuance_id: str, generation: int, *, scope: str = SCOPE) -> dict[str, Any]:
        return self.call({"op": "issue", "issuance_id": issuance_id, "generation": generation, "scope": scope, "version": VERSION})

    def verify(self, record: Mapping[str, Any], *, minimum_generation: int) -> dict[str, Any]:
        return self.call({"op": "verify", "record": dict(record), "minimum_generation": minimum_generation, "version": VERSION})

    def stop(self, *, kill: bool = False) -> None:
        if self.proc.poll() is None:
            if kill:
                self.proc.kill()
            else:
                try:
                    assert self.proc.stdin is not None
                    self.proc.stdin.write('{"op":"stop"}\n')
                    self.proc.stdin.flush()
                except Exception:
                    self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        for stream in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            try:
                if stream:
                    stream.close()
            except Exception:
                pass


class KeylessCompositeWriter:
    """Writer persists exact signer-authorized records and owns no composite authentication key."""

    def __init__(self, *, state_db: str | Path, signer: IsolatedCompositeSignerProcess):
        self.state_db = str(state_db)
        self.signer = signer
        init_writer_journal(self.state_db)

    def issue(self, issuance_id: str, generation: int) -> dict[str, Any]:
        signed = self.signer.issue(issuance_id, generation)
        if not signed.get("ok"):
            raise PermissionError(str(signed.get("reason", "SIGNER_DENIED")))
        verified = self.signer.verify(signed, minimum_generation=generation)
        if not verified.get("ok"):
            raise PermissionError(str(verified.get("reason", "SIGNER_VERIFICATION_FAILED")))
        statement = dict(signed["statement"])
        if statement.get("issuance_id") != issuance_id or int(statement.get("generation", -1)) != generation:
            raise PermissionError("SIGNER_RESPONSE_BINDING_MISMATCH")

        con = sqlite3.connect(self.state_db, timeout=10.0, isolation_level=None)
        try:
            con.execute("BEGIN IMMEDIATE")
            existing = con.execute(
                "SELECT statement_json,checkpoint_digest,auth_tag,status FROM isolated_composite_journal WHERE issuance_id=?",
                (issuance_id,),
            ).fetchone()
            if existing is not None:
                stored = {
                    "ok": True,
                    "statement": json.loads(existing[0]),
                    "checkpoint_digest": existing[1],
                    "auth_tag": existing[2],
                    "status": existing[3],
                }
                if (
                    stored["statement"] != statement
                    or stored["checkpoint_digest"] != signed["checkpoint_digest"]
                    or stored["auth_tag"] != signed["auth_tag"]
                ):
                    con.execute("ROLLBACK")
                    raise PermissionError("WRITER_REPLAY_MISMATCH")
                con.execute("COMMIT")
                return stored
            con.execute(
                "INSERT INTO isolated_composite_journal VALUES(?,?,?,?,?,?)",
                (
                    issuance_id,
                    generation,
                    json.dumps(statement, sort_keys=True),
                    signed["checkpoint_digest"],
                    signed["auth_tag"],
                    "CURRENT",
                ),
            )
            con.execute("COMMIT")
            return {**signed, "status": "CURRENT"}
        except sqlite3.IntegrityError as exc:
            try:
                con.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise PermissionError("WRITER_GENERATION_CONFLICT") from exc
        finally:
            con.close()

    def verify_current(self, issuance_id: str, *, minimum_generation: int) -> dict[str, Any]:
        con = sqlite3.connect(self.state_db)
        try:
            row = con.execute(
                "SELECT statement_json,checkpoint_digest,auth_tag,status FROM isolated_composite_journal WHERE issuance_id=?",
                (issuance_id,),
            ).fetchone()
        finally:
            con.close()
        if row is None or row[3] != "CURRENT":
            return {"ok": False, "reason": "CURRENT_MISSING"}
        record = {"statement": json.loads(row[0]), "checkpoint_digest": row[1], "auth_tag": row[2]}
        return self.signer.verify(record, minimum_generation=minimum_generation)


def _worker_main(signer_store: str, state_db: str) -> int:
    permit_key = bytes.fromhex(os.environ.get("EXP_I_P10_PERMIT_KEY_HEX", ""))
    reconciliation_key = bytes.fromhex(os.environ.get("EXP_I_P10_RECON_KEY_HEX", ""))
    composite_key = bytes.fromhex(os.environ.get("EXP_I_P10_COMPOSITE_KEY_HEX", ""))
    if not permit_key or not reconciliation_key or not composite_key:
        raise RuntimeError("signer keys unavailable")
    init_signer_store(signer_store)
    print(json.dumps({"ready": True, "pid": os.getpid()}), flush=True)
    for line in sys.stdin:
        request = json.loads(line)
        op = request.get("op")
        if op == "stop":
            return 0
        if op == "issue":
            if set(request) != {"op", "issuance_id", "generation", "scope", "version"} or request.get("version") != VERSION:
                result = {"ok": False, "reason": "ISSUE_REQUEST_SCHEMA_INVALID"}
            else:
                result = _issue(
                    signer_store,
                    state_db,
                    str(request["issuance_id"]),
                    int(request["generation"]),
                    str(request["scope"]),
                    permit_key,
                    reconciliation_key,
                    composite_key,
                )
            print(json.dumps(result, sort_keys=True), flush=True)
        elif op == "verify":
            if set(request) != {"op", "record", "minimum_generation", "version"} or request.get("version") != VERSION:
                result = {"ok": False, "reason": "VERIFY_REQUEST_SCHEMA_INVALID"}
            else:
                result = _verify(
                    request["record"],
                    state_db,
                    int(request["minimum_generation"]),
                    permit_key,
                    reconciliation_key,
                    composite_key,
                )
            print(json.dumps(result, sort_keys=True), flush=True)
        else:
            print(json.dumps({"ok": False, "reason": "OP_INVALID"}), flush=True)
    return 0


if __name__ == "__main__" and len(sys.argv) == 4 and sys.argv[1] == "--worker":
    raise SystemExit(_worker_main(sys.argv[2], sys.argv[3]))
