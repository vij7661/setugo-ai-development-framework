"""EXP-I Pilot 18: externally killed recovery-signer issuance boundaries.

This module preserves Pilot 17 semantics while adding an independently keyed
anti-rollback issuance checkpoint and a parent-observed crash worker.  The crash
worker reports a precise boundary only after reaching it, then blocks until the
parent externally terminates the process.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from exp_i_asymmetric_checkpoint_signer import _canon, _ensure_ed25519_keypair, _ed25519_sign
from exp_i_isolated_minimum_authority import _permit_body
from exp_i_root_rotation import PlatformRootTrustAuthority, RootMinimumAuthority


def _paths(store_dir: str, anchor_dir: str) -> tuple[str, str, str, str, str]:
    s = Path(store_dir); a = Path(anchor_dir)
    s.mkdir(parents=True, exist_ok=True); a.mkdir(parents=True, exist_ok=True)
    return (
        str(s / "recovery-signing.private.pem"),
        str(s / "recovery-signing.public.pem"),
        str(s / "issuance.db"),
        str(a / "issuance-anchor.json"),
        str(a / "issuance-anchor.key"),
    )


def _ensure_ledger(path: str) -> None:
    c = sqlite3.connect(path)
    try:
        c.execute(
            "CREATE TABLE IF NOT EXISTS issuance("
            "seq INTEGER PRIMARY KEY AUTOINCREMENT, recovery_id TEXT NOT NULL UNIQUE, "
            "target_selector TEXT NOT NULL, permit_json TEXT NOT NULL, signature TEXT NOT NULL)"
        )
        c.commit()
    finally:
        c.close()


def _ensure_anchor_key(path: str) -> bytes:
    p = Path(path)
    if not p.exists():
        p.write_bytes(os.urandom(32))
        try: os.chmod(p, 0o600)
        except OSError: pass
    return p.read_bytes()


def _ledger_state(conn: sqlite3.Connection) -> dict[str, Any]:
    row = conn.execute(
        "SELECT seq,recovery_id,permit_json,signature FROM issuance ORDER BY seq DESC LIMIT 1"
    ).fetchone()
    count = int(conn.execute("SELECT COUNT(*) FROM issuance").fetchone()[0])
    if row is None:
        return {"count": 0, "last_seq": 0, "last_recovery_id": None, "last_digest": "GENESIS"}
    digest = hashlib.sha256((str(row[2]) + "|" + str(row[3])).encode("utf-8")).hexdigest()
    return {"count": count, "last_seq": int(row[0]), "last_recovery_id": str(row[1]), "last_digest": digest}


def _anchor_mac(key: bytes, body: dict[str, Any]) -> str:
    return hmac.new(key, _canon(body), hashlib.sha256).hexdigest()


def _write_anchor(anchor_path: str, key: bytes, body: dict[str, Any]) -> None:
    envelope = {"body": body, "mac": _anchor_mac(key, body)}
    tmp = Path(anchor_path + ".tmp")
    tmp.write_text(json.dumps(envelope, sort_keys=True))
    os.replace(tmp, anchor_path)


def _validate_or_initialize_anchor(conn: sqlite3.Connection, anchor_path: str, anchor_key_path: str) -> tuple[bool, str]:
    key = _ensure_anchor_key(anchor_key_path)
    state = _ledger_state(conn)
    p = Path(anchor_path)
    if not p.exists():
        if state["count"] != 0:
            return False, "ISSUANCE_ANCHOR_MISSING"
        _write_anchor(anchor_path, key, state)
        return True, "OK"
    try:
        env = json.loads(p.read_text()); body = env["body"]; mac = env["mac"]
    except Exception:
        return False, "ISSUANCE_ANCHOR_CORRUPT"
    if not hmac.compare_digest(str(mac), _anchor_mac(key, body)):
        return False, "ISSUANCE_ANCHOR_AUTH_INVALID"
    if body != state:
        return False, "ISSUANCE_ROLLBACK_OR_DIVERGENCE"
    return True, "OK"


def _derive_permit(root_db: str, root_auth: str, minimum_db: str, recovery_id: str, target_selector: str) -> tuple[dict[str, Any] | None, str | None]:
    trust = PlatformRootTrustAuthority(root_db, root_auth)
    history = trust.history(None)
    minimum = RootMinimumAuthority(minimum_db)
    me, md = minimum.current()
    target = None
    for item in history:
        r = item["record"]
        if r["active_root_id"] == target_selector or r["transition_id"] == target_selector:
            target = item; break
    if target is None: return None, "TARGET_ROOT_NOT_FOUND"
    te = int(target["record"]["root_epoch"])
    if te <= me: return None, "TARGET_NOT_ABOVE_MINIMUM"
    if te != me + 1: return None, "TARGET_NOT_CONTIGUOUS"
    if target["record"]["predecessor_root_record_digest"] != md: return None, "TARGET_PREDECESSOR_MISMATCH"
    return _permit_body(recovery_id, me, md, target), None


def _issue(root_db: str, root_auth: str, minimum_db: str, ledger_db: str, private_path: str,
           anchor_path: str, anchor_key_path: str, recovery_id: Any, target_selector: Any) -> dict[str, Any]:
    if not isinstance(recovery_id, str) or not recovery_id: return {"ok": False, "reason": "RECOVERY_ID_REQUIRED"}
    if not isinstance(target_selector, str) or not target_selector: return {"ok": False, "reason": "TARGET_SELECTOR_REQUIRED"}
    c = sqlite3.connect(ledger_db, timeout=10, isolation_level=None)
    try:
        ok, reason = _validate_or_initialize_anchor(c, anchor_path, anchor_key_path)
        if not ok: return {"ok": False, "reason": reason}
        c.execute("BEGIN IMMEDIATE")
        prior = c.execute("SELECT target_selector,permit_json,signature FROM issuance WHERE recovery_id=?", (recovery_id,)).fetchone()
        if prior is not None:
            if str(prior[0]) != target_selector:
                c.execute("ROLLBACK"); return {"ok": False, "reason": "RECOVERY_ID_REBIND_DENIED"}
            permit = json.loads(prior[1]); signature = str(prior[2]); c.execute("COMMIT")
            return {"ok": True, "replay": True, "permit": permit, "signature": signature}
        body, error = _derive_permit(root_db, root_auth, minimum_db, recovery_id, target_selector)
        if error:
            c.execute("ROLLBACK"); return {"ok": False, "reason": error}
        signature = _ed25519_sign(private_path, _canon(body))
        c.execute("INSERT INTO issuance(recovery_id,target_selector,permit_json,signature) VALUES(?,?,?,?)",
                  (recovery_id, target_selector, json.dumps(body, sort_keys=True), signature))
        c.execute("COMMIT")
        _write_anchor(anchor_path, _ensure_anchor_key(anchor_key_path), _ledger_state(c))
        return {"ok": True, "replay": False, "permit": body, "signature": signature}
    finally:
        c.close()


def _normal_worker(root_db: str, root_auth: str, minimum_db: str, store_dir: str, anchor_dir: str) -> None:
    private_path, public_path, ledger_db, anchor_path, anchor_key_path = _paths(store_dir, anchor_dir)
    _ensure_ed25519_keypair(private_path, public_path); _ensure_ledger(ledger_db)
    c = sqlite3.connect(ledger_db); ok, _ = _validate_or_initialize_anchor(c, anchor_path, anchor_key_path); c.close()
    if not ok: pass
    for line in sys.stdin:
        try:
            req = json.loads(line); op = req.get("op")
            if op == "ping": out = {"ok": True, "pid": os.getpid(), "public_key_pem": Path(public_path).read_text()}
            elif op == "issue": out = _issue(root_db, root_auth, minimum_db, ledger_db, private_path, anchor_path, anchor_key_path, req.get("recovery_id"), req.get("target_selector"))
            else: out = {"ok": False, "reason": "UNKNOWN_OPERATION"}
        except Exception as e: out = {"ok": False, "reason": f"{type(e).__name__}:{e}"}
        print(json.dumps(out, sort_keys=True), flush=True)


def _ready(boundary: str, **extra: Any) -> None:
    print(json.dumps({"ready": boundary, "pid": os.getpid(), **extra}, sort_keys=True), flush=True)


def _block() -> None:
    while True: time.sleep(60)


def _crash_worker(boundary: str, root_db: str, root_auth: str, minimum_db: str, store_dir: str, anchor_dir: str,
                  recovery_id: str, target_selector: str) -> None:
    private_path, public_path, ledger_db, anchor_path, anchor_key_path = _paths(store_dir, anchor_dir)
    _ensure_ed25519_keypair(private_path, public_path); _ensure_ledger(ledger_db)
    c = sqlite3.connect(ledger_db, timeout=10, isolation_level=None)
    try:
        ok, reason = _validate_or_initialize_anchor(c, anchor_path, anchor_key_path)
        if not ok:
            _ready("anchor-invalid", reason=reason); _block()
        if boundary == "before_txn":
            _ready(boundary); _block()
        c.execute("BEGIN IMMEDIATE")
        if boundary == "after_begin":
            _ready(boundary); _block()
        prior = c.execute("SELECT 1 FROM issuance WHERE recovery_id=?", (recovery_id,)).fetchone()
        if prior is not None:
            _ready("prior-exists"); _block()
        body, error = _derive_permit(root_db, root_auth, minimum_db, recovery_id, target_selector)
        if error:
            c.execute("ROLLBACK"); _ready("derive-error", reason=error); _block()
        signature = _ed25519_sign(private_path, _canon(body))
        c.execute("INSERT INTO issuance(recovery_id,target_selector,permit_json,signature) VALUES(?,?,?,?)",
                  (recovery_id, target_selector, json.dumps(body, sort_keys=True), signature))
        if boundary == "after_insert_precommit":
            _ready(boundary, permit=body, signature=signature); _block()
        c.execute("COMMIT")
        _write_anchor(anchor_path, _ensure_anchor_key(anchor_key_path), _ledger_state(c))
        if boundary == "after_commit_pre_response":
            _ready(boundary, permit=body, signature=signature); _block()
        raise RuntimeError("UNKNOWN_CRASH_BOUNDARY")
    finally:
        c.close()


class CrashWorkerHandle:
    def __init__(self, proc: subprocess.Popen[str], readiness: dict[str, Any]):
        self.proc = proc; self.readiness = readiness
    @property
    def pid(self) -> int: return int(self.proc.pid)
    def kill(self) -> None:
        if self.proc.poll() is None:
            self.proc.kill(); self.proc.wait(timeout=5)
        for h in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            if h:
                try: h.close()
                except Exception: pass


class CrashConsistentRecoverySignerProcess:
    def __init__(self, root_db: str | Path, root_auth: str | Path, minimum_db: str | Path,
                 store_dir: str | Path, anchor_dir: str | Path):
        self.root_db=str(root_db); self.root_auth=str(root_auth); self.minimum_db=str(minimum_db)
        self.store_dir=str(store_dir); self.anchor_dir=str(anchor_dir); self.proc=None; self._lock=threading.Lock(); self.start()
    def start(self) -> None:
        if self.proc and self.proc.poll() is None: return
        self.proc=subprocess.Popen([sys.executable,__file__,"--worker",self.root_db,self.root_auth,self.minimum_db,self.store_dir,self.anchor_dir],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    def stop(self, kill: bool=False) -> None:
        if not self.proc: return
        if self.proc.poll() is None:
            (self.proc.kill() if kill else self.proc.terminate()); self.proc.wait(timeout=5)
        for h in (self.proc.stdin,self.proc.stdout,self.proc.stderr):
            if h:
                try: h.close()
                except Exception: pass
    def request(self,payload:dict[str,Any])->dict[str,Any]:
        if not self.proc or self.proc.poll() is not None: return {"ok":False,"reason":"RECOVERY_SIGNER_UNAVAILABLE"}
        with self._lock:
            self.proc.stdin.write(json.dumps(payload,sort_keys=True)+"\n"); self.proc.stdin.flush(); line=self.proc.stdout.readline()
        return json.loads(line) if line else {"ok":False,"reason":"RECOVERY_SIGNER_UNAVAILABLE"}
    def issue(self,recovery_id:str,target_selector:str,**untrusted_extra:Any)->dict[str,Any]:
        return self.request({"op":"issue","recovery_id":recovery_id,"target_selector":target_selector,**untrusted_extra})
    @property
    def public_key_pem(self)->str:
        out=self.request({"op":"ping"})
        if not out.get("ok"): raise RuntimeError(out.get("reason","RECOVERY_SIGNER_UNAVAILABLE"))
        return str(out["public_key_pem"])
    def crash_at(self,boundary:str,recovery_id:str,target_selector:str)->CrashWorkerHandle:
        proc=subprocess.Popen([sys.executable,__file__,"--crash-worker",boundary,self.root_db,self.root_auth,self.minimum_db,self.store_dir,self.anchor_dir,recovery_id,target_selector],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        line=proc.stdout.readline()
        if not line:
            err=proc.stderr.read(); raise RuntimeError(f"CRASH_WORKER_NO_READINESS:{err}")
        readiness=json.loads(line)
        return CrashWorkerHandle(proc,readiness)
    def ledger_rows(self)->list[tuple[Any,...]]:
        _,_,ledger_db,_,_=_paths(self.store_dir,self.anchor_dir)
        c=sqlite3.connect(ledger_db); rows=c.execute("SELECT seq,recovery_id,target_selector,permit_json,signature FROM issuance ORDER BY seq").fetchall(); c.close(); return rows


if __name__ == "__main__":
    if len(sys.argv)==7 and sys.argv[1]=="--worker": _normal_worker(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6])
    elif len(sys.argv)==10 and sys.argv[1]=="--crash-worker": _crash_worker(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7],sys.argv[8],sys.argv[9])
    else: raise SystemExit("WORKER_MODE_REQUIRED")
