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

from exp_i_composite_integrity import CompositeIntegrityAuthority

VERSION = "exp-i-pilot10-v1"
SCOPE = "EXP-I-COMPOSITE-AUTHORITY"
AUTHORITY_ID = "composite-authority-A"


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


def checkpoint_digest(statement: Mapping[str, Any]) -> str:
    return _digest(dict(statement))


def _tag(statement: Mapping[str, Any], key: bytes) -> str:
    return hmac.new(key, _canon(dict(statement)), hashlib.sha256).hexdigest()


def init_authority_store(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path), isolation_level=None)
    try:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS issued (
                generation INTEGER PRIMARY KEY,
                issuance_id TEXT NOT NULL UNIQUE,
                statement_json TEXT NOT NULL,
                checkpoint_digest TEXT NOT NULL,
                auth_tag TEXT NOT NULL
            )
            """
        )
        con.execute(
            "CREATE TABLE IF NOT EXISTS meta(singleton INTEGER PRIMARY KEY CHECK(singleton=1), max_generation INTEGER NOT NULL)"
        )
        con.execute("INSERT OR IGNORE INTO meta(singleton,max_generation) VALUES(1,0)")
    finally:
        con.close()


def _current_pair(main_db: str, permit_integrity_key: bytes, reconciliation_integrity_key: bytes, checkpoint_key: bytes) -> dict[str, Any]:
    authority = CompositeIntegrityAuthority(
        main_db,
        permit_integrity_key,
        reconciliation_integrity_key,
        checkpoint_key,
    )
    return authority.current_pair()


def _predecessor(con: sqlite3.Connection, generation: int) -> str:
    if generation == 1:
        count = con.execute("SELECT COUNT(*) FROM issued").fetchone()[0]
        if count:
            raise PermissionError("GENESIS_AFTER_EXISTING_STATE")
        return "GENESIS"
    row = con.execute(
        "SELECT checkpoint_digest FROM issued WHERE generation=?",
        (generation - 1,),
    ).fetchone()
    if row is None:
        raise PermissionError("PREDECESSOR_MISSING")
    return str(row[0])


def _statement(*, issuance_id: str, generation: int, pair: Mapping[str, Any], predecessor: str) -> dict[str, Any]:
    return {
        "version": VERSION,
        "scope": SCOPE,
        "authority_id": AUTHORITY_ID,
        "issuance_id": issuance_id,
        "generation": int(generation),
        "permit_ledger_digest": str(pair["permit_ledger_digest"]),
        "reconciliation_digest": str(pair["reconciliation_digest"]),
        "permit_authority_epoch": int(pair["permit_authority_epoch"]),
        "previous_checkpoint_digest": predecessor,
    }


def _issue(
    authority_store: str,
    main_db: str,
    issuance_id: str,
    generation: int,
    checkpoint_key: bytes,
    permit_integrity_key: bytes,
    reconciliation_integrity_key: bytes,
) -> dict[str, Any]:
    if not issuance_id or generation < 1:
        return {"ok": False, "reason": "ISSUE_REQUEST_INVALID"}
    pair = _current_pair(main_db, permit_integrity_key, reconciliation_integrity_key, checkpoint_key)
    con = sqlite3.connect(authority_store, isolation_level=None, timeout=5.0)
    con.row_factory = sqlite3.Row
    try:
        con.execute("BEGIN IMMEDIATE")
        maximum = int(con.execute("SELECT max_generation FROM meta WHERE singleton=1").fetchone()[0])
        existing_id = con.execute("SELECT * FROM issued WHERE issuance_id=?", (issuance_id,)).fetchone()
        existing_gen = con.execute("SELECT * FROM issued WHERE generation=?", (generation,)).fetchone()

        # Exact durable replay is resolved before new-issuance predecessor admission.
        # Otherwise a committed generation-1 retry is incorrectly rejected as a
        # new genesis after state already exists.
        if existing_id is not None:
            try:
                old_statement = json.loads(existing_id["statement_json"])
            except Exception:
                con.execute("ROLLBACK")
                return {"ok": False, "reason": "AUTHORITY_RECORD_MISMATCH"}
            stored_digest = str(existing_id["checkpoint_digest"])
            stored_tag = str(existing_id["auth_tag"])
            if checkpoint_digest(old_statement) != stored_digest or not hmac.compare_digest(
                _tag(old_statement, checkpoint_key), stored_tag
            ):
                con.execute("ROLLBACK")
                return {"ok": False, "reason": "AUTHORITY_RECORD_MISMATCH"}
            exact_current_binding = (
                int(existing_id["generation"]) == generation
                and old_statement.get("version") == VERSION
                and old_statement.get("scope") == SCOPE
                and old_statement.get("authority_id") == AUTHORITY_ID
                and old_statement.get("issuance_id") == issuance_id
                and int(old_statement.get("generation", -1)) == generation
                and old_statement.get("permit_ledger_digest") == str(pair["permit_ledger_digest"])
                and old_statement.get("reconciliation_digest") == str(pair["reconciliation_digest"])
                and int(old_statement.get("permit_authority_epoch", -1)) == int(pair["permit_authority_epoch"])
            )
            if not exact_current_binding:
                con.execute("ROLLBACK")
                return {"ok": False, "reason": "ISSUANCE_ID_REBINDING"}
            con.execute("COMMIT")
            return {
                "ok": True,
                "replay": True,
                "statement": old_statement,
                "checkpoint_digest": stored_digest,
                "auth_tag": stored_tag,
            }

        if generation < maximum:
            con.execute("ROLLBACK")
            return {"ok": False, "reason": "CHECKPOINT_GENERATION_ROLLBACK", "maximum": maximum}

        # If the requested generation already exists but the issuance identity did
        # not match above, it is necessarily a distinct statement at that
        # generation and must not be treated as an idempotent replay.
        if existing_gen is not None:
            con.execute("ROLLBACK")
            return {"ok": False, "reason": "CHECKPOINT_SAME_GENERATION_EQUIVOCATION"}

        try:
            predecessor = _predecessor(con, generation)
        except PermissionError as exc:
            con.execute("ROLLBACK")
            return {"ok": False, "reason": str(exc)}
        statement = _statement(issuance_id=issuance_id, generation=generation, pair=pair, predecessor=predecessor)
        digest = checkpoint_digest(statement)
        tag = _tag(statement, checkpoint_key)
        con.execute(
            "INSERT INTO issued(generation,issuance_id,statement_json,checkpoint_digest,auth_tag) VALUES(?,?,?,?,?)",
            (generation, issuance_id, json.dumps(statement, sort_keys=True), digest, tag),
        )
        if generation > maximum:
            con.execute("UPDATE meta SET max_generation=? WHERE singleton=1", (generation,))
        con.execute("COMMIT")
        return {"ok": True, "replay": False, "statement": statement, "checkpoint_digest": digest, "auth_tag": tag}
    except BaseException:
        try:
            con.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        con.close()


def _verify(
    authority_store: str,
    main_db: str,
    record: Mapping[str, Any],
    minimum_generation: int,
    checkpoint_key: bytes,
    permit_integrity_key: bytes,
    reconciliation_integrity_key: bytes,
) -> dict[str, Any]:
    try:
        statement = dict(record["statement"])
        supplied_digest = str(record["checkpoint_digest"])
        supplied_tag = str(record["auth_tag"])
    except Exception:
        return {"ok": False, "reason": "CHECKPOINT_MALFORMED"}
    digest = checkpoint_digest(statement)
    if digest != supplied_digest:
        return {"ok": False, "reason": "CHECKPOINT_DIGEST_MISMATCH"}
    if not hmac.compare_digest(_tag(statement, checkpoint_key), supplied_tag):
        return {"ok": False, "reason": "CHECKPOINT_AUTH_FAILED"}
    if statement.get("version") != VERSION or statement.get("scope") != SCOPE or statement.get("authority_id") != AUTHORITY_ID:
        return {"ok": False, "reason": "CHECKPOINT_SCOPE_MISMATCH"}
    try:
        generation = int(statement["generation"])
    except Exception:
        return {"ok": False, "reason": "CHECKPOINT_GENERATION_INVALID"}
    if generation < int(minimum_generation):
        return {"ok": False, "reason": "CHECKPOINT_ROLLBACK"}

    con = sqlite3.connect(authority_store, timeout=5.0)
    con.row_factory = sqlite3.Row
    try:
        row = con.execute("SELECT * FROM issued WHERE generation=?", (generation,)).fetchone()
        if row is None:
            return {"ok": False, "reason": "AUTHORITY_RECORD_MISSING"}
        try:
            durable_statement = json.loads(row["statement_json"])
        except Exception:
            return {"ok": False, "reason": "AUTHORITY_RECORD_MISMATCH"}
        durable_digest = checkpoint_digest(durable_statement)
        durable_tag = _tag(durable_statement, checkpoint_key)
        if (
            durable_statement != statement
            or durable_digest != str(row["checkpoint_digest"])
            or durable_digest != digest
            or not hmac.compare_digest(durable_tag, str(row["auth_tag"]))
            or not hmac.compare_digest(str(row["auth_tag"]), supplied_tag)
        ):
            return {"ok": False, "reason": "AUTHORITY_RECORD_MISMATCH"}
        if str(row["issuance_id"]) != str(statement.get("issuance_id")):
            return {"ok": False, "reason": "AUTHORITY_ISSUANCE_MISMATCH"}
        if generation == 1:
            if statement.get("previous_checkpoint_digest") != "GENESIS":
                return {"ok": False, "reason": "PREDECESSOR_MISMATCH"}
        else:
            prev = con.execute("SELECT checkpoint_digest FROM issued WHERE generation=?", (generation - 1,)).fetchone()
            if prev is None or str(prev[0]) != str(statement.get("previous_checkpoint_digest")):
                return {"ok": False, "reason": "PREDECESSOR_MISMATCH"}
    finally:
        con.close()

    try:
        pair = _current_pair(main_db, permit_integrity_key, reconciliation_integrity_key, checkpoint_key)
    except Exception:
        return {"ok": False, "reason": "CURRENT_GOVERNANCE_STATE_INVALID"}
    if statement.get("permit_ledger_digest") != pair["permit_ledger_digest"]:
        return {"ok": False, "reason": "PERMIT_LEDGER_STALE"}
    if statement.get("reconciliation_digest") != pair["reconciliation_digest"]:
        return {"ok": False, "reason": "RECONCILIATION_LEDGER_STALE"}
    if int(statement.get("permit_authority_epoch", -1)) != int(pair["permit_authority_epoch"]):
        return {"ok": False, "reason": "PERMIT_AUTHORITY_EPOCH_STALE"}
    return {
        "ok": True,
        "checkpoint_digest": digest,
        "generation": generation,
        "authority_id": AUTHORITY_ID,
        "reviewer_generated_authority": False,
        "production_authority": False,
        "release_authority": False,
    }


class CompositeCheckpointAuthorityProcess:
    def __init__(
        self,
        *,
        main_db: str | Path,
        authority_store: str | Path,
        checkpoint_key: bytes,
        permit_integrity_key: bytes,
        reconciliation_integrity_key: bytes,
    ):
        self.main_db = str(main_db)
        self.store = str(authority_store)
        init_authority_store(self.store)
        env = dict(os.environ)
        env["EXP_I_P10_CHECKPOINT_KEY_HEX"] = checkpoint_key.hex()
        env["EXP_I_P10_PERMIT_INTEGRITY_KEY_HEX"] = permit_integrity_key.hex()
        env["EXP_I_P10_RECON_INTEGRITY_KEY_HEX"] = reconciliation_integrity_key.hex()
        self.env_keys = (
            "EXP_I_P10_CHECKPOINT_KEY_HEX",
            "EXP_I_P10_PERMIT_INTEGRITY_KEY_HEX",
            "EXP_I_P10_RECON_INTEGRITY_KEY_HEX",
        )
        self.argv = [sys.executable, str(Path(__file__).resolve()), "--worker", self.main_db, self.store]
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
        ready_line = self.proc.stdout.readline()
        if not ready_line:
            raise RuntimeError("composite checkpoint authority failed to start")
        ready = json.loads(ready_line)
        self.pid = int(ready["pid"])

    def call(self, request: Mapping[str, Any]) -> dict[str, Any]:
        if self.proc.poll() is not None:
            return {"ok": False, "reason": "CHECKPOINT_AUTHORITY_UNAVAILABLE"}
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(dict(request), sort_keys=True) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            return {"ok": False, "reason": "CHECKPOINT_AUTHORITY_RESPONSE_LOST"}
        return json.loads(line)

    def issue(self, issuance_id: str, generation: int, *, crash_after_commit: bool = False) -> dict[str, Any]:
        return self.call({"op": "issue", "issuance_id": issuance_id, "generation": generation, "crash_after_commit": crash_after_commit})

    def verify(self, record: Mapping[str, Any], *, minimum_generation: int) -> dict[str, Any]:
        return self.call({"op": "verify", "record": dict(record), "minimum_generation": minimum_generation})

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
                self.proc.wait(timeout=4)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=4)
        for stream in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            try:
                if stream:
                    stream.close()
            except Exception:
                pass


def _worker(main_db: str, authority_store: str) -> int:
    checkpoint_key = bytes.fromhex(os.environ.get("EXP_I_P10_CHECKPOINT_KEY_HEX", ""))
    permit_integrity_key = bytes.fromhex(os.environ.get("EXP_I_P10_PERMIT_INTEGRITY_KEY_HEX", ""))
    reconciliation_integrity_key = bytes.fromhex(os.environ.get("EXP_I_P10_RECON_INTEGRITY_KEY_HEX", ""))
    if not checkpoint_key or not permit_integrity_key or not reconciliation_integrity_key:
        return 2
    init_authority_store(authority_store)
    print(json.dumps({"ready": True, "pid": os.getpid(), "authority_id": AUTHORITY_ID}), flush=True)
    for line in sys.stdin:
        try:
            req = json.loads(line)
            op = req.get("op")
            if op == "stop":
                return 0
            if op == "issue":
                result = _issue(
                    authority_store,
                    main_db,
                    str(req.get("issuance_id", "")),
                    int(req.get("generation", -1)),
                    checkpoint_key,
                    permit_integrity_key,
                    reconciliation_integrity_key,
                )
                if req.get("crash_after_commit") and result.get("ok"):
                    os._exit(94)
                print(json.dumps(result, sort_keys=True), flush=True)
            elif op == "verify":
                result = _verify(
                    authority_store,
                    main_db,
                    req.get("record", {}),
                    int(req.get("minimum_generation", -1)),
                    checkpoint_key,
                    permit_integrity_key,
                    reconciliation_integrity_key,
                )
                print(json.dumps(result, sort_keys=True), flush=True)
            else:
                print(json.dumps({"ok": False, "reason": "OP_INVALID"}), flush=True)
        except Exception as exc:
            print(json.dumps({"ok": False, "reason": "AUTHORITY_ERROR", "error": type(exc).__name__}), flush=True)
    return 0


if __name__ == "__main__" and len(sys.argv) == 4 and sys.argv[1] == "--worker":
    raise SystemExit(_worker(sys.argv[2], sys.argv[3]))
