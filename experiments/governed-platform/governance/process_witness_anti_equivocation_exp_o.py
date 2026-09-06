"""EXP-O Pilot 21: process-isolated witnesses with durable anti-equivocation memory."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from typing import Any, Mapping, Sequence

from multi_witness_checkpoint_exp_o import recover_multi_witness, statement_digest

VERSION = "exp-o-pilot21-v1"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _tag(*, witness_id: str, key_id: str, digest: str, key: bytes) -> str:
    unsigned = {"witness_id": witness_id, "key_id": key_id, "statement_digest": digest}
    return hmac.new(key, _canonical(unsigned), hashlib.sha256).hexdigest()


def _connect_history(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), isolation_level=None, timeout=5.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute("CREATE TABLE IF NOT EXISTS witness_meta(id INTEGER PRIMARY KEY CHECK(id=1), max_generation INTEGER NOT NULL)")
    conn.execute("INSERT OR IGNORE INTO witness_meta(id,max_generation) VALUES(1,-1)")
    conn.execute("CREATE TABLE IF NOT EXISTS signed_statements(generation INTEGER PRIMARY KEY, statement_digest TEXT NOT NULL, auth_tag TEXT NOT NULL)")
    return conn


def _sign_durable(*, store: str | Path, witness_id: str, key_id: str, key: bytes,
                  statement: Mapping[str, Any], crash_after_commit: bool = False) -> dict[str, Any]:
    try:
        generation = int(statement["generation"])
    except Exception:
        return {"approved": False, "reason": "GENERATION_INVALID", "witness_id": witness_id}
    digest = statement_digest(statement)
    conn = _connect_history(store)
    try:
        conn.execute("BEGIN IMMEDIATE")
        max_generation = int(conn.execute("SELECT max_generation FROM witness_meta WHERE id=1").fetchone()[0])
        row = conn.execute("SELECT statement_digest,auth_tag FROM signed_statements WHERE generation=?", (generation,)).fetchone()
        if generation < max_generation:
            conn.execute("ROLLBACK")
            return {"approved": False, "reason": "GENERATION_ROLLBACK_REFUSED", "witness_id": witness_id,
                    "generation": generation, "max_generation": max_generation}
        if row is not None:
            old_digest, old_tag = str(row[0]), str(row[1])
            if not hmac.compare_digest(old_digest, digest):
                conn.execute("ROLLBACK")
                return {"approved": False, "reason": "SAME_GENERATION_EQUIVOCATION_REFUSED", "witness_id": witness_id,
                        "generation": generation, "existing_statement_digest": old_digest, "requested_statement_digest": digest}
            conn.execute("COMMIT")
            result = {"approved": True, "replay": True, "witness_id": witness_id, "key_id": key_id,
                      "statement_digest": digest, "auth_tag": old_tag, "statement": dict(statement), "generation": generation}
            if crash_after_commit:
                os._exit(91)
            return result
        tag = _tag(witness_id=witness_id, key_id=key_id, digest=digest, key=key)
        conn.execute("INSERT INTO signed_statements(generation,statement_digest,auth_tag) VALUES(?,?,?)", (generation, digest, tag))
        if generation > max_generation:
            conn.execute("UPDATE witness_meta SET max_generation=? WHERE id=1", (generation,))
        conn.execute("COMMIT")
        result = {"approved": True, "replay": False, "witness_id": witness_id, "key_id": key_id,
                  "statement_digest": digest, "auth_tag": tag, "statement": dict(statement), "generation": generation}
        if crash_after_commit:
            os._exit(91)
        return result
    except BaseException:
        try:
            conn.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        conn.close()


def history_snapshot(path: str | Path) -> dict[str, Any]:
    conn = _connect_history(path)
    try:
        rows = conn.execute("SELECT generation,statement_digest,auth_tag FROM signed_statements ORDER BY generation").fetchall()
        maximum = int(conn.execute("SELECT max_generation FROM witness_meta WHERE id=1").fetchone()[0])
        return {"max_generation": maximum,
                "rows": [{"generation": int(g), "statement_digest": str(d), "auth_tag": str(t)} for g, d, t in rows]}
    finally:
        conn.close()


class WitnessProcess:
    """Long-lived child. The raw key is injected only into this child's environment."""
    def __init__(self, *, witness_id: str, key_id: str, key: bytes, store: str | Path):
        self.witness_id = witness_id
        self.key_id = key_id
        self.store = str(store)
        env = dict(os.environ)
        env["EXP_O_WITNESS_KEY_HEX"] = bytes(key).hex()
        self.argv = [sys.executable, str(Path(__file__).resolve()), "--worker", witness_id, key_id, self.store]
        self.proc = subprocess.Popen(self.argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, bufsize=1, env=env)
        ready = json.loads(self.proc.stdout.readline())
        if not ready.get("ready"):
            raise RuntimeError(f"witness failed readiness: {ready}")
        self.pid = int(ready["pid"])

    def request(self, statement: Mapping[str, Any], *, crash_after_commit: bool = False) -> dict[str, Any]:
        if self.proc.poll() is not None:
            return {"transport": "UNAVAILABLE", "returncode": self.proc.returncode, "witness_id": self.witness_id}
        request = {"op": "sign", "statement": dict(statement), "crash_after_commit": bool(crash_after_commit)}
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(request, sort_keys=True) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            self.proc.wait(timeout=5)
            return {"transport": "UNKNOWN_AFTER_REQUEST", "returncode": self.proc.returncode, "witness_id": self.witness_id}
        response = json.loads(line)
        response["transport"] = "RESPONSE"
        return response

    def stop(self, *, kill: bool = False) -> None:
        if self.proc.poll() is None:
            if kill:
                self.proc.kill()
            else:
                try:
                    assert self.proc.stdin is not None
                    self.proc.stdin.write(json.dumps({"op": "stop"}) + "\n")
                    self.proc.stdin.flush()
                except Exception:
                    self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill(); self.proc.wait(timeout=5)


def coordinator_request_payload(statement: Mapping[str, Any]) -> dict[str, Any]:
    """The coordinator's request surface deliberately contains no signing material."""
    return {"op": "sign", "statement": dict(statement), "crash_after_commit": False}


def recover_process_witness(db_path: str | Path, records: Sequence[Mapping[str, Any]], *,
                            verifier_config: Mapping[str, Mapping[str, Any]], expected_project: str,
                            expected_task: str, expected_logical_state_id: str, minimum_generation: int) -> dict[str, Any]:
    usable = [dict(r) for r in records if r.get("approved") is True and r.get("transport", "RESPONSE") == "RESPONSE"]
    result = recover_multi_witness(db_path, usable, witness_config=verifier_config,
                                   expected_project=expected_project, expected_task=expected_task,
                                   expected_logical_state_id=expected_logical_state_id,
                                   minimum_generation=minimum_generation)
    result["process_witness_records_seen"] = len(records)
    result["process_witness_approved_records"] = len(usable)
    return result


def _worker_main(witness_id: str, key_id: str, store: str) -> int:
    key_hex = os.environ.get("EXP_O_WITNESS_KEY_HEX", "")
    if not key_hex:
        print(json.dumps({"ready": False, "reason": "KEY_MISSING"}), flush=True)
        return 2
    key = bytes.fromhex(key_hex)
    _connect_history(store).close()
    print(json.dumps({"ready": True, "pid": os.getpid(), "witness_id": witness_id, "store": str(Path(store).resolve())}), flush=True)
    for line in sys.stdin:
        try:
            req = json.loads(line)
        except Exception:
            print(json.dumps({"approved": False, "reason": "REQUEST_MALFORMED", "witness_id": witness_id}), flush=True)
            continue
        if req.get("op") == "stop":
            return 0
        if req.get("op") != "sign" or not isinstance(req.get("statement"), dict):
            print(json.dumps({"approved": False, "reason": "REQUEST_INVALID", "witness_id": witness_id}), flush=True)
            continue
        result = _sign_durable(store=store, witness_id=witness_id, key_id=key_id, key=key,
                               statement=req["statement"], crash_after_commit=bool(req.get("crash_after_commit", False)))
        result["pid"] = os.getpid()
        print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__" and len(sys.argv) >= 5 and sys.argv[1] == "--worker":
    raise SystemExit(_worker_main(sys.argv[2], sys.argv[3], sys.argv[4]))


__all__ = ["VERSION", "WitnessProcess", "coordinator_request_payload", "history_snapshot", "recover_process_witness"]
