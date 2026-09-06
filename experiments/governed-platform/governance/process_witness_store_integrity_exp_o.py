"""EXP-O Pilot 22: sealed witness stores + externally authenticated history checkpoints."""
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

VERSION = "exp-o-pilot22-v1"


def _canonical(v: Any) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _digest(v: Any) -> str:
    return hashlib.sha256(_canonical(v)).hexdigest()


def _row_seal(generation: int, digest: str, tag: str) -> str:
    return _digest({"generation": int(generation), "statement_digest": digest, "auth_tag": tag})


def _meta_seal(store_identity: str, max_generation: int) -> str:
    return _digest({"store_identity": store_identity, "max_generation": int(max_generation)})


def _connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), isolation_level=None, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    return conn


def init_store(path: str | Path, *, store_identity: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = _connect(path)
    try:
        conn.execute("CREATE TABLE IF NOT EXISTS witness_meta(id INTEGER PRIMARY KEY CHECK(id=1), store_identity TEXT NOT NULL, max_generation INTEGER NOT NULL, meta_seal TEXT NOT NULL)")
        conn.execute("CREATE TABLE IF NOT EXISTS signed_statements(generation INTEGER PRIMARY KEY, statement_digest TEXT NOT NULL, auth_tag TEXT NOT NULL, row_seal TEXT NOT NULL)")
        if conn.execute("SELECT 1 FROM witness_meta WHERE id=1").fetchone() is None:
            conn.execute("INSERT INTO witness_meta(id,store_identity,max_generation,meta_seal) VALUES(1,?,?,?)", (store_identity, -1, _meta_seal(store_identity, -1)))
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()


def verify_store(path: str | Path, *, expected_store_identity: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"ok": False, "reason": "WITNESS_STORE_MISSING"}
    try:
        conn = sqlite3.connect(str(p), isolation_level=None, timeout=2.0)
        conn.row_factory = sqlite3.Row
        try:
            quick = [str(r[0]) for r in conn.execute("PRAGMA quick_check").fetchall()]
            if quick != ["ok"]:
                return {"ok": False, "reason": "WITNESS_SQLITE_INTEGRITY_FAILED", "integrity": quick[:8]}
            tables = {str(r[0]) for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not {"witness_meta", "signed_statements"}.issubset(tables):
                return {"ok": False, "reason": "WITNESS_STORE_SCHEMA_MISSING"}
            meta = conn.execute("SELECT store_identity,max_generation,meta_seal FROM witness_meta WHERE id=1").fetchone()
            if meta is None:
                return {"ok": False, "reason": "WITNESS_META_MISSING"}
            sid = str(meta["store_identity"]); maximum = int(meta["max_generation"]); seal = str(meta["meta_seal"])
            if sid != expected_store_identity:
                return {"ok": False, "reason": "WITNESS_STORE_IDENTITY_MISMATCH"}
            if not hmac.compare_digest(seal, _meta_seal(sid, maximum)):
                return {"ok": False, "reason": "WITNESS_META_SEAL_MISMATCH"}
            rows = conn.execute("SELECT generation,statement_digest,auth_tag,row_seal FROM signed_statements ORDER BY generation").fetchall()
            generations = []
            logical_rows = []
            for row in rows:
                g = int(row["generation"]); d = str(row["statement_digest"]); t = str(row["auth_tag"]); rs = str(row["row_seal"])
                if not hmac.compare_digest(rs, _row_seal(g, d, t)):
                    return {"ok": False, "reason": "WITNESS_ROW_SEAL_MISMATCH", "generation": g}
                generations.append(g); logical_rows.append({"generation": g, "statement_digest": d, "auth_tag": t})
            observed_max = max(generations) if generations else -1
            if observed_max != maximum:
                return {"ok": False, "reason": "WITNESS_MONOTONIC_HISTORY_MISMATCH", "max_generation": maximum, "observed_max": observed_max}
            root = _digest({"store_identity": sid, "max_generation": maximum, "rows": logical_rows})
            return {"ok": True, "store_identity": sid, "max_generation": maximum, "history_root": root, "rows": logical_rows}
        except sqlite3.Error as exc:
            return {"ok": False, "reason": "WITNESS_STORE_READ_ERROR", "error": str(exc)}
        finally:
            conn.close()
    except sqlite3.Error as exc:
        return {"ok": False, "reason": "WITNESS_STORE_OPEN_FAILED", "error": str(exc)}


def make_history_checkpoint(path: str | Path, *, witness_id: str, key_id: str, store_identity: str,
                            checkpoint_generation: int, checkpoint_key: bytes) -> dict[str, Any]:
    v = verify_store(path, expected_store_identity=store_identity)
    if not v.get("ok"):
        raise ValueError(f"cannot checkpoint invalid store: {v}")
    statement = {"version": VERSION, "witness_id": witness_id, "key_id": key_id, "store_identity": store_identity,
                 "max_generation": int(v["max_generation"]), "history_root": str(v["history_root"]),
                 "checkpoint_generation": int(checkpoint_generation)}
    tag = hmac.new(checkpoint_key, _canonical(statement), hashlib.sha256).hexdigest()
    return {**statement, "checkpoint_auth_tag": tag}


def verify_history_checkpoint(path: str | Path, checkpoint: Mapping[str, Any], *, expected_witness_id: str,
                              expected_key_id: str, expected_store_identity: str, minimum_checkpoint_generation: int,
                              checkpoint_key: bytes) -> dict[str, Any]:
    local = verify_store(path, expected_store_identity=expected_store_identity)
    if not local.get("ok"):
        return {"ok": False, "reason": local.get("reason"), "local": local}
    try:
        statement = {k: checkpoint[k] for k in ("version","witness_id","key_id","store_identity","max_generation","history_root","checkpoint_generation")}
        tag = str(checkpoint["checkpoint_auth_tag"])
    except Exception:
        return {"ok": False, "reason": "WITNESS_CHECKPOINT_MALFORMED"}
    expected = hmac.new(checkpoint_key, _canonical(statement), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(tag, expected):
        return {"ok": False, "reason": "WITNESS_CHECKPOINT_AUTH_FAILED"}
    if statement["version"] != VERSION:
        return {"ok": False, "reason": "WITNESS_CHECKPOINT_VERSION_MISMATCH"}
    if str(statement["witness_id"]) != expected_witness_id or str(statement["key_id"]) != expected_key_id or str(statement["store_identity"]) != expected_store_identity:
        return {"ok": False, "reason": "WITNESS_CHECKPOINT_SCOPE_MISMATCH"}
    if int(statement["checkpoint_generation"]) < int(minimum_checkpoint_generation):
        return {"ok": False, "reason": "WITNESS_CHECKPOINT_ROLLBACK"}
    if int(statement["max_generation"]) != int(local["max_generation"]):
        return {"ok": False, "reason": "WITNESS_CHECKPOINT_MAX_GENERATION_MISMATCH"}
    if not hmac.compare_digest(str(statement["history_root"]), str(local["history_root"])):
        return {"ok": False, "reason": "WITNESS_HISTORY_ROOT_MISMATCH"}
    return {"ok": True, "local": local, "checkpoint_generation": int(statement["checkpoint_generation"])}


def _sign_tag(*, witness_id: str, key_id: str, digest: str, key: bytes) -> str:
    unsigned = {"witness_id": witness_id, "key_id": key_id, "statement_digest": digest}
    return hmac.new(key, _canonical(unsigned), hashlib.sha256).hexdigest()


def _commit_signature(path: str | Path, *, witness_id: str, key_id: str, key: bytes, store_identity: str,
                      statement: Mapping[str, Any]) -> dict[str, Any]:
    generation = int(statement["generation"]); digest = statement_digest(statement)
    conn = _connect(path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        meta = conn.execute("SELECT max_generation FROM witness_meta WHERE id=1").fetchone()
        if meta is None:
            conn.execute("ROLLBACK"); return {"approved": False, "reason": "WITNESS_META_MISSING", "witness_id": witness_id}
        maximum = int(meta[0])
        row = conn.execute("SELECT statement_digest,auth_tag FROM signed_statements WHERE generation=?", (generation,)).fetchone()
        if generation < maximum:
            conn.execute("ROLLBACK"); return {"approved": False, "reason": "GENERATION_ROLLBACK_REFUSED", "witness_id": witness_id, "max_generation": maximum}
        if row is not None:
            old_d, old_t = str(row[0]), str(row[1])
            if not hmac.compare_digest(old_d, digest):
                conn.execute("ROLLBACK"); return {"approved": False, "reason": "SAME_GENERATION_EQUIVOCATION_REFUSED", "witness_id": witness_id}
            conn.execute("COMMIT")
            return {"approved": True, "replay": True, "witness_id": witness_id, "key_id": key_id, "statement_digest": digest, "auth_tag": old_t, "statement": dict(statement), "generation": generation}
        tag = _sign_tag(witness_id=witness_id, key_id=key_id, digest=digest, key=key)
        conn.execute("INSERT INTO signed_statements(generation,statement_digest,auth_tag,row_seal) VALUES(?,?,?,?)", (generation, digest, tag, _row_seal(generation, digest, tag)))
        if generation > maximum:
            conn.execute("UPDATE witness_meta SET max_generation=?,meta_seal=? WHERE id=1", (generation, _meta_seal(store_identity, generation)))
        conn.execute("COMMIT")
        return {"approved": True, "replay": False, "witness_id": witness_id, "key_id": key_id, "statement_digest": digest, "auth_tag": tag, "statement": dict(statement), "generation": generation}
    except BaseException:
        try: conn.execute("ROLLBACK")
        except Exception: pass
        raise
    finally:
        conn.close()


class SealedWitnessProcess:
    def __init__(self, *, witness_id: str, key_id: str, signing_key: bytes, checkpoint_key: bytes,
                 store: str | Path, store_identity: str):
        self.witness_id=witness_id; self.key_id=key_id; self.store=str(store); self.store_identity=store_identity
        if not Path(self.store).exists():
            init_store(self.store, store_identity=store_identity)
        env=dict(os.environ); env["EXP_O_WITNESS_KEY_HEX"]=signing_key.hex(); env["EXP_O_WITNESS_CHECKPOINT_KEY_HEX"]=checkpoint_key.hex()
        self.argv=[sys.executable,str(Path(__file__).resolve()),"--worker",witness_id,key_id,self.store,store_identity]
        self.proc=subprocess.Popen(self.argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,env=env)
        ready=json.loads(self.proc.stdout.readline())
        if not ready.get("ready"): raise RuntimeError(str(ready))
        self.pid=int(ready["pid"])
    def request(self, statement: Mapping[str,Any], *, checkpoint: Mapping[str,Any], minimum_checkpoint_generation: int,
                crash_after_history_commit: bool=False) -> dict[str,Any]:
        if self.proc.poll() is not None: return {"transport":"UNAVAILABLE","witness_id":self.witness_id,"returncode":self.proc.returncode}
        req={"op":"sign","statement":dict(statement),"checkpoint":dict(checkpoint),"minimum_checkpoint_generation":int(minimum_checkpoint_generation),"crash_after_history_commit":bool(crash_after_history_commit)}
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(req,sort_keys=True)+"\n"); self.proc.stdin.flush(); line=self.proc.stdout.readline()
        if not line:
            self.proc.wait(timeout=5); return {"transport":"UNKNOWN_AFTER_REQUEST","witness_id":self.witness_id,"returncode":self.proc.returncode}
        out=json.loads(line); out["transport"]="RESPONSE"; return out
    def stop(self, *, kill: bool=False) -> None:
        if self.proc.poll() is None:
            if kill: self.proc.kill()
            else:
                try:
                    assert self.proc.stdin is not None; self.proc.stdin.write('{"op":"stop"}\n'); self.proc.stdin.flush()
                except Exception: self.proc.terminate()
            try: self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired: self.proc.kill(); self.proc.wait(timeout=5)
        for stream in (self.proc.stdin,self.proc.stdout,self.proc.stderr):
            try:
                if stream is not None: stream.close()
            except Exception: pass


def recover_sealed_process_witness(db_path: str | Path, records: Sequence[Mapping[str,Any]], *, verifier_config: Mapping[str,Mapping[str,Any]], expected_project: str, expected_task: str, expected_logical_state_id: str, minimum_generation: int) -> dict[str,Any]:
    usable=[dict(r) for r in records if r.get("approved") is True and r.get("transport","RESPONSE")=="RESPONSE"]
    return recover_multi_witness(db_path,usable,witness_config=verifier_config,expected_project=expected_project,expected_task=expected_task,expected_logical_state_id=expected_logical_state_id,minimum_generation=minimum_generation)


def _worker_main(witness_id: str,key_id: str,store: str,store_identity: str) -> int:
    sk=bytes.fromhex(os.environ.get("EXP_O_WITNESS_KEY_HEX","")); ck=bytes.fromhex(os.environ.get("EXP_O_WITNESS_CHECKPOINT_KEY_HEX",""))
    if not sk or not ck:
        print(json.dumps({"ready":False,"reason":"KEY_MISSING"}),flush=True); return 2
    if not Path(store).exists():
        init_store(store,store_identity=store_identity)
    print(json.dumps({"ready":True,"pid":os.getpid(),"witness_id":witness_id,"store":str(Path(store).resolve())}),flush=True)
    for line in sys.stdin:
        req=json.loads(line)
        if req.get("op")=="stop": return 0
        if req.get("op")!="sign":
            print(json.dumps({"approved":False,"reason":"REQUEST_INVALID","witness_id":witness_id}),flush=True); continue
        chk=verify_history_checkpoint(store,req.get("checkpoint",{}),expected_witness_id=witness_id,expected_key_id=key_id,expected_store_identity=store_identity,minimum_checkpoint_generation=int(req.get("minimum_checkpoint_generation",0)),checkpoint_key=ck)
        if not chk.get("ok"):
            print(json.dumps({"approved":False,"reason":chk.get("reason"),"witness_id":witness_id,"pid":os.getpid()}),flush=True); continue
        result=_commit_signature(store,witness_id=witness_id,key_id=key_id,key=sk,store_identity=store_identity,statement=req["statement"])
        if req.get("crash_after_history_commit") and result.get("approved"):
            os._exit(92)
        result["pid"]=os.getpid(); print(json.dumps(result,sort_keys=True),flush=True)
    return 0


if __name__=="__main__" and len(sys.argv)>=6 and sys.argv[1]=="--worker":
    raise SystemExit(_worker_main(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]))

__all__=["VERSION","SealedWitnessProcess","init_store","make_history_checkpoint","verify_store","verify_history_checkpoint","recover_sealed_process_witness"]
