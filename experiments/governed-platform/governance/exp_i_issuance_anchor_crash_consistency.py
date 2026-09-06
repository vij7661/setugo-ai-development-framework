"""EXP-I Pilot 19: issuance-ledger / anti-rollback-anchor crash consistency.

Pilot 19 extends Pilot 18 without merging the two durable authorities.  The
issuance ledger records a monotonic *reconciliation receipt* for the last anchor
state it observed as durably installed.  The independently authenticated anchor
remains a separate artifact.  Consequential use requires exact correspondence
between the committed issuance, the ledger receipt and the external anchor.

A ledger-ahead state is repairable only when it is the uniquely derivable next
committed issuance above the last reconciled receipt.  Anchor-ahead, stale,
conflicting or non-contiguous states fail closed unless the exact post-replace /
pre-receipt state can be proven from the committed ledger.
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
from exp_i_isolated_minimum_authority import MinimumAuthorityProcess
from exp_i_recovery_signer_crash_consistency import _derive_permit


def _paths(store_dir: str | Path, anchor_dir: str | Path) -> tuple[str, str, str, str, str]:
    s = Path(store_dir); a = Path(anchor_dir)
    s.mkdir(parents=True, exist_ok=True); a.mkdir(parents=True, exist_ok=True)
    return (
        str(s / "recovery-signing.private.pem"),
        str(s / "recovery-signing.public.pem"),
        str(s / "issuance.db"),
        str(a / "issuance-anchor.json"),
        str(a / "issuance-anchor.key"),
    )


def _ensure_anchor_key(path: str) -> bytes:
    p = Path(path)
    if not p.exists():
        p.write_bytes(os.urandom(32))
        try:
            os.chmod(p, 0o600)
        except OSError:
            pass
    return p.read_bytes()


def _ensure_ledger(path: str) -> None:
    c = sqlite3.connect(path)
    try:
        c.execute(
            "CREATE TABLE IF NOT EXISTS issuance("
            "seq INTEGER PRIMARY KEY AUTOINCREMENT, recovery_id TEXT NOT NULL UNIQUE, "
            "target_selector TEXT NOT NULL, permit_json TEXT NOT NULL, signature TEXT NOT NULL)"
        )
        c.execute(
            "CREATE TABLE IF NOT EXISTS anchor_receipt("
            "id INTEGER PRIMARY KEY CHECK(id=1), generation INTEGER NOT NULL, "
            "state_json TEXT NOT NULL, anchor_hash TEXT NOT NULL)"
        )
        c.commit()
    finally:
        c.close()


def _row_digest(permit_json: str, signature: str) -> str:
    return hashlib.sha256((permit_json + "|" + signature).encode("utf-8")).hexdigest()


def _ledger_state(conn: sqlite3.Connection, generation: int | None = None) -> dict[str, Any]:
    total = int(conn.execute("SELECT COUNT(*) FROM issuance").fetchone()[0])
    n = total if generation is None else int(generation)
    if n < 0 or n > total:
        raise ValueError("INVALID_LEDGER_GENERATION")
    if n == 0:
        return {"generation": 0, "last_seq": 0, "last_recovery_id": None, "last_digest": "GENESIS"}
    row = conn.execute(
        "SELECT seq,recovery_id,permit_json,signature FROM issuance ORDER BY seq LIMIT 1 OFFSET ?", (n - 1,)
    ).fetchone()
    if row is None:
        raise ValueError("LEDGER_PREFIX_MISSING")
    return {
        "generation": n,
        "last_seq": int(row[0]),
        "last_recovery_id": str(row[1]),
        "last_digest": _row_digest(str(row[2]), str(row[3])),
    }


def _anchor_mac(key: bytes, body: dict[str, Any]) -> str:
    return hmac.new(key, _canon(body), hashlib.sha256).hexdigest()


def _anchor_hash(body: dict[str, Any], mac: str) -> str:
    return hashlib.sha256(_canon({"body": body, "mac": mac})).hexdigest()


def _anchor_envelope(key: bytes, body: dict[str, Any]) -> dict[str, Any]:
    mac = _anchor_mac(key, body)
    return {"body": body, "mac": mac}


def _write_anchor_temp(anchor_path: str, key: bytes, body: dict[str, Any]) -> Path:
    tmp = Path(anchor_path + ".tmp")
    tmp.write_text(json.dumps(_anchor_envelope(key, body), sort_keys=True))
    with tmp.open("rb") as fh:
        os.fsync(fh.fileno())
    return tmp


def _replace_anchor(anchor_path: str, tmp: Path) -> None:
    os.replace(tmp, anchor_path)


def _read_anchor(anchor_path: str, key: bytes) -> tuple[dict[str, Any] | None, str | None, str | None]:
    p = Path(anchor_path)
    if not p.exists():
        return None, None, "ISSUANCE_ANCHOR_MISSING"
    try:
        env = json.loads(p.read_text()); body = env["body"]; mac = str(env["mac"])
    except Exception:
        return None, None, "ISSUANCE_ANCHOR_CORRUPT"
    if not isinstance(body, dict) or not hmac.compare_digest(mac, _anchor_mac(key, body)):
        return None, None, "ISSUANCE_ANCHOR_AUTH_INVALID"
    return body, _anchor_hash(body, mac), None


def _receipt(conn: sqlite3.Connection) -> tuple[int, dict[str, Any], str] | None:
    row = conn.execute("SELECT generation,state_json,anchor_hash FROM anchor_receipt WHERE id=1").fetchone()
    if row is None:
        return None
    return int(row[0]), json.loads(str(row[1])), str(row[2])


def _store_receipt(conn: sqlite3.Connection, body: dict[str, Any], anchor_hash: str) -> None:
    generation = int(body["generation"])
    current = _receipt(conn)
    if current is not None and generation < current[0]:
        raise RuntimeError("ANCHOR_RECEIPT_ROLLBACK")
    conn.execute(
        "INSERT INTO anchor_receipt(id,generation,state_json,anchor_hash) VALUES(1,?,?,?) "
        "ON CONFLICT(id) DO UPDATE SET generation=excluded.generation,state_json=excluded.state_json,anchor_hash=excluded.anchor_hash",
        (generation, json.dumps(body, sort_keys=True), anchor_hash),
    )


def _initialize_pair(conn: sqlite3.Connection, anchor_path: str, anchor_key_path: str) -> None:
    key = _ensure_anchor_key(anchor_key_path)
    if int(conn.execute("SELECT COUNT(*) FROM issuance").fetchone()[0]) != 0:
        return
    body, ah, err = _read_anchor(anchor_path, key)
    rec = _receipt(conn)
    if body is None and err == "ISSUANCE_ANCHOR_MISSING" and rec is None:
        genesis = _ledger_state(conn, 0)
        tmp = _write_anchor_temp(anchor_path, key, genesis); _replace_anchor(anchor_path, tmp)
        _, ah2, err2 = _read_anchor(anchor_path, key)
        if err2 or ah2 is None:
            raise RuntimeError(err2 or "ANCHOR_INIT_FAILED")
        conn.execute("BEGIN IMMEDIATE")
        _store_receipt(conn, genesis, ah2); conn.execute("COMMIT")


def _pair_status(conn: sqlite3.Connection, anchor_path: str, anchor_key_path: str) -> dict[str, Any]:
    key = _ensure_anchor_key(anchor_key_path)
    body, ah, err = _read_anchor(anchor_path, key)
    rec = _receipt(conn)
    current = _ledger_state(conn)
    if err:
        return {"state": "FAIL_CLOSED", "reason": err, "ledger": current}
    assert body is not None and ah is not None
    try:
        ag = int(body["generation"])
    except Exception:
        return {"state": "FAIL_CLOSED", "reason": "ISSUANCE_ANCHOR_CORRUPT", "ledger": current}
    if rec is None:
        return {"state": "FAIL_CLOSED", "reason": "ANCHOR_RECEIPT_MISSING", "ledger": current, "anchor": body}
    rg, rb, rh = rec
    lg = int(current["generation"])

    # Exact fully reconciled state.
    if body == current and rb == body and rh == ah and rg == ag == lg:
        return {"state": "RECONCILED", "reason": "OK", "ledger": current, "anchor": body, "receipt_generation": rg}

    # Already-reconciled anchor rolled back: retained receipt is newer.
    if ag < rg:
        return {"state": "FAIL_CLOSED", "reason": "STALE_ANCHOR_ROLLBACK", "ledger": current, "anchor": body, "receipt_generation": rg}

    # Ledger rolled back after a newer anchor/receipt was reconciled.
    if lg < rg or ag > lg:
        return {"state": "FAIL_CLOSED", "reason": "STALE_LEDGER_OR_ANCHOR_AHEAD", "ledger": current, "anchor": body, "receipt_generation": rg}

    # Legitimate crash after ledger commit before anchor replacement: exactly one
    # committed row above the last reconciled anchor/receipt.
    if lg == rg + 1 and ag == rg and body == rb and rh == ah:
        prefix = _ledger_state(conn, rg)
        if prefix != body:
            return {"state": "FAIL_CLOSED", "reason": "LEDGER_PREFIX_CONFLICT", "ledger": current, "anchor": body, "receipt_generation": rg}
        return {"state": "LEDGER_AHEAD_EXACT", "reason": "RECONCILIATION_REQUIRED", "ledger": current, "anchor": body, "receipt_generation": rg}

    # Legitimate crash after atomic anchor replace but before receipt commit.
    if lg == rg + 1 and ag == lg and body == current and rb == _ledger_state(conn, rg):
        return {"state": "ANCHOR_REPLACED_RECEIPT_PENDING", "reason": "RECONCILIATION_REQUIRED", "ledger": current, "anchor": body, "receipt_generation": rg, "anchor_hash": ah}

    if ag == lg and body != current:
        return {"state": "FAIL_CLOSED", "reason": "CONFLICTING_SAME_GENERATION_ANCHOR", "ledger": current, "anchor": body, "receipt_generation": rg}
    return {"state": "FAIL_CLOSED", "reason": "ISSUANCE_ANCHOR_DIVERGENCE", "ledger": current, "anchor": body, "receipt_generation": rg}


def _reconcile(conn: sqlite3.Connection, anchor_path: str, anchor_key_path: str, crash_boundary: str | None = None) -> dict[str, Any]:
    # BEGIN IMMEDIATE serializes reconcilers through the ledger authority without
    # making the ledger alone sufficient for authority; external anchor
    # correspondence is still required before RECONCILED is returned.
    conn.execute("BEGIN IMMEDIATE")
    try:
        st = _pair_status(conn, anchor_path, anchor_key_path)
        if st["state"] == "RECONCILED":
            conn.execute("COMMIT"); return {"ok": True, "replay": True, "status": st}
        key = _ensure_anchor_key(anchor_key_path)
        if st["state"] == "LEDGER_AHEAD_EXACT":
            if crash_boundary == "after_ledger_commit_before_anchor":
                print(json.dumps({"ready": crash_boundary, "pid": os.getpid(), "status": st}, sort_keys=True), flush=True); _block()
            target = st["ledger"]
            tmp = _write_anchor_temp(anchor_path, key, target)
            if crash_boundary == "after_anchor_temp_before_replace":
                print(json.dumps({"ready": crash_boundary, "pid": os.getpid(), "status": st}, sort_keys=True), flush=True); _block()
            _replace_anchor(anchor_path, tmp)
            _, ah, err = _read_anchor(anchor_path, key)
            if err or ah is None:
                raise RuntimeError(err or "ANCHOR_REPLACE_VERIFY_FAILED")
            if crash_boundary == "after_anchor_replace_before_response":
                print(json.dumps({"ready": crash_boundary, "pid": os.getpid(), "anchor": target}, sort_keys=True), flush=True); _block()
            _store_receipt(conn, target, ah)
            conn.execute("COMMIT")
            return {"ok": True, "replay": False, "status": _pair_status(conn, anchor_path, anchor_key_path)}
        if st["state"] == "ANCHOR_REPLACED_RECEIPT_PENDING":
            _store_receipt(conn, st["ledger"], str(st["anchor_hash"]))
            conn.execute("COMMIT")
            return {"ok": True, "replay": False, "status": _pair_status(conn, anchor_path, anchor_key_path)}
        conn.execute("ROLLBACK")
        return {"ok": False, "reason": st["reason"], "status": st}
    except Exception:
        try:
            conn.execute("ROLLBACK")
        except Exception:
            pass
        raise


def _issue(root_db: str, root_auth: str, minimum_db: str, ledger_db: str, private_path: str,
           anchor_path: str, anchor_key_path: str, recovery_id: Any, target_selector: Any) -> dict[str, Any]:
    if not isinstance(recovery_id, str) or not recovery_id:
        return {"ok": False, "reason": "RECOVERY_ID_REQUIRED"}
    if not isinstance(target_selector, str) or not target_selector:
        return {"ok": False, "reason": "TARGET_SELECTOR_REQUIRED"}
    c = sqlite3.connect(ledger_db, timeout=10, isolation_level=None)
    try:
        st = _pair_status(c, anchor_path, anchor_key_path)
        if st["state"] != "RECONCILED":
            return {"ok": False, "reason": st["reason"], "status": st}
        c.execute("BEGIN IMMEDIATE")
        prior = c.execute("SELECT target_selector,permit_json,signature FROM issuance WHERE recovery_id=?", (recovery_id,)).fetchone()
        if prior is not None:
            if str(prior[0]) != target_selector:
                c.execute("ROLLBACK"); return {"ok": False, "reason": "RECOVERY_ID_REBIND_DENIED"}
            permit = json.loads(str(prior[1])); signature = str(prior[2]); c.execute("COMMIT")
            return {"ok": True, "replay": True, "permit": permit, "signature": signature}
        body, error = _derive_permit(root_db, root_auth, minimum_db, recovery_id, target_selector)
        if error:
            c.execute("ROLLBACK"); return {"ok": False, "reason": error}
        signature = _ed25519_sign(private_path, _canon(body))
        c.execute("INSERT INTO issuance(recovery_id,target_selector,permit_json,signature) VALUES(?,?,?,?)",
                  (recovery_id, target_selector, json.dumps(body, sort_keys=True), signature))
        c.execute("COMMIT")
        rec = _reconcile(c, anchor_path, anchor_key_path)
        if not rec.get("ok"):
            return {"ok": False, "reason": rec.get("reason", "RECONCILIATION_FAILED")}
        return {"ok": True, "replay": False, "permit": body, "signature": signature}
    finally:
        c.close()


def _block() -> None:
    while True:
        time.sleep(60)


def _normal_worker(root_db: str, root_auth: str, minimum_db: str, store_dir: str, anchor_dir: str) -> None:
    private_path, public_path, ledger_db, anchor_path, anchor_key_path = _paths(store_dir, anchor_dir)
    _ensure_ed25519_keypair(private_path, public_path); _ensure_ledger(ledger_db)
    c = sqlite3.connect(ledger_db, timeout=10, isolation_level=None)
    try:
        _initialize_pair(c, anchor_path, anchor_key_path)
    finally:
        c.close()
    for line in sys.stdin:
        try:
            req = json.loads(line); op = req.get("op")
            if op == "ping":
                out = {"ok": True, "pid": os.getpid(), "public_key_pem": Path(public_path).read_text()}
            elif op == "status":
                c = sqlite3.connect(ledger_db); out = {"ok": True, "status": _pair_status(c, anchor_path, anchor_key_path)}; c.close()
            elif op == "reconcile":
                c = sqlite3.connect(ledger_db, timeout=10, isolation_level=None); out = _reconcile(c, anchor_path, anchor_key_path); c.close()
            elif op == "issue":
                out = _issue(root_db, root_auth, minimum_db, ledger_db, private_path, anchor_path, anchor_key_path, req.get("recovery_id"), req.get("target_selector"))
            else:
                out = {"ok": False, "reason": "UNKNOWN_OPERATION"}
        except Exception as e:
            out = {"ok": False, "reason": f"{type(e).__name__}:{e}"}
        print(json.dumps(out, sort_keys=True), flush=True)


def _crash_worker(boundary: str, root_db: str, root_auth: str, minimum_db: str, store_dir: str, anchor_dir: str,
                  recovery_id: str, target_selector: str) -> None:
    private_path, public_path, ledger_db, anchor_path, anchor_key_path = _paths(store_dir, anchor_dir)
    _ensure_ed25519_keypair(private_path, public_path); _ensure_ledger(ledger_db)
    c = sqlite3.connect(ledger_db, timeout=10, isolation_level=None)
    try:
        _initialize_pair(c, anchor_path, anchor_key_path)
        st = _pair_status(c, anchor_path, anchor_key_path)
        if st["state"] != "RECONCILED":
            print(json.dumps({"ready": "pair-invalid", "pid": os.getpid(), "status": st}, sort_keys=True), flush=True); _block()
        c.execute("BEGIN IMMEDIATE")
        prior = c.execute("SELECT 1 FROM issuance WHERE recovery_id=?", (recovery_id,)).fetchone()
        if prior is not None:
            c.execute("ROLLBACK"); print(json.dumps({"ready": "prior-exists", "pid": os.getpid()}, sort_keys=True), flush=True); _block()
        body, error = _derive_permit(root_db, root_auth, minimum_db, recovery_id, target_selector)
        if error:
            c.execute("ROLLBACK"); print(json.dumps({"ready": "derive-error", "pid": os.getpid(), "reason": error}, sort_keys=True), flush=True); _block()
        signature = _ed25519_sign(private_path, _canon(body))
        c.execute("INSERT INTO issuance(recovery_id,target_selector,permit_json,signature) VALUES(?,?,?,?)",
                  (recovery_id, target_selector, json.dumps(body, sort_keys=True), signature))
        c.execute("COMMIT")
        # Every P19 crash boundary begins only after durable ledger COMMIT.
        _reconcile(c, anchor_path, anchor_key_path, crash_boundary=boundary)
        raise RuntimeError("UNKNOWN_CRASH_BOUNDARY")
    finally:
        c.close()


class CrashWorkerHandle:
    def __init__(self, proc: subprocess.Popen[str], readiness: dict[str, Any]):
        self.proc = proc; self.readiness = readiness
    @property
    def pid(self) -> int:
        return int(self.proc.pid)
    def kill(self) -> None:
        if self.proc.poll() is None:
            self.proc.kill(); self.proc.wait(timeout=5)
        for h in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            if h:
                try:
                    h.close()
                except Exception:
                    pass


class IssuanceAnchorCrashConsistentSignerProcess:
    def __init__(self, root_db: str | Path, root_auth: str | Path, minimum_db: str | Path,
                 store_dir: str | Path, anchor_dir: str | Path):
        self.root_db = str(root_db); self.root_auth = str(root_auth); self.minimum_db = str(minimum_db)
        self.store_dir = str(store_dir); self.anchor_dir = str(anchor_dir); self.proc = None; self._lock = threading.Lock(); self.start()
    def start(self) -> None:
        if self.proc and self.proc.poll() is None:
            return
        self.proc = subprocess.Popen(
            [sys.executable, __file__, "--worker", self.root_db, self.root_auth, self.minimum_db, self.store_dir, self.anchor_dir],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
    def stop(self, kill: bool = False) -> None:
        if not self.proc:
            return
        if self.proc.poll() is None:
            (self.proc.kill() if kill else self.proc.terminate()); self.proc.wait(timeout=5)
        for h in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            if h:
                try:
                    h.close()
                except Exception:
                    pass
    def request(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.proc or self.proc.poll() is not None:
            return {"ok": False, "reason": "RECOVERY_SIGNER_UNAVAILABLE"}
        with self._lock:
            assert self.proc.stdin is not None and self.proc.stdout is not None
            self.proc.stdin.write(json.dumps(payload, sort_keys=True) + "\n"); self.proc.stdin.flush(); line = self.proc.stdout.readline()
        return json.loads(line) if line else {"ok": False, "reason": "RECOVERY_SIGNER_UNAVAILABLE"}
    def issue(self, recovery_id: str, target_selector: str, **untrusted_extra: Any) -> dict[str, Any]:
        return self.request({"op": "issue", "recovery_id": recovery_id, "target_selector": target_selector, **untrusted_extra})
    def reconcile(self) -> dict[str, Any]:
        return self.request({"op": "reconcile"})
    def status(self) -> dict[str, Any]:
        return self.request({"op": "status"})
    @property
    def public_key_pem(self) -> str:
        out = self.request({"op": "ping"})
        if not out.get("ok"):
            raise RuntimeError(out.get("reason", "RECOVERY_SIGNER_UNAVAILABLE"))
        return str(out["public_key_pem"])
    def crash_at(self, boundary: str, recovery_id: str, target_selector: str) -> CrashWorkerHandle:
        proc = subprocess.Popen(
            [sys.executable, __file__, "--crash-worker", boundary, self.root_db, self.root_auth, self.minimum_db, self.store_dir, self.anchor_dir, recovery_id, target_selector],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
        )
        assert proc.stdout is not None
        line = proc.stdout.readline()
        if not line:
            err = proc.stderr.read() if proc.stderr else ""; raise RuntimeError(f"CRASH_WORKER_NO_READINESS:{err}")
        return CrashWorkerHandle(proc, json.loads(line))
    def ledger_rows(self) -> list[tuple[Any, ...]]:
        _, _, ledger_db, _, _ = _paths(self.store_dir, self.anchor_dir)
        c = sqlite3.connect(ledger_db); rows = c.execute("SELECT seq,recovery_id,target_selector,permit_json,signature FROM issuance ORDER BY seq").fetchall(); c.close(); return rows


class ReconciledMinimumAuthorityProcess:
    """Minimum mutation requires exact committed + reconciled issuance evidence."""
    def __init__(self, root_db: str | Path, root_auth: str | Path, minimum_db: str | Path,
                 recovery_public_key_pem: str, store_dir: str | Path, anchor_dir: str | Path):
        self.store_dir = str(store_dir); self.anchor_dir = str(anchor_dir)
        self.inner = MinimumAuthorityProcess(root_db, root_auth, minimum_db, recovery_public_key_pem)
    def stop(self, kill: bool = False) -> None:
        self.inner.stop(kill=kill)
    def advance(self, authorization: dict[str, Any]) -> dict[str, Any]:
        permit = authorization.get("permit"); signature = authorization.get("signature")
        if not isinstance(permit, dict) or not isinstance(signature, str):
            return {"ok": False, "reason": "RECOVERY_AUTHORIZATION_REQUIRED"}
        _, _, ledger_db, anchor_path, anchor_key_path = _paths(self.store_dir, self.anchor_dir)
        c = sqlite3.connect(ledger_db)
        try:
            st = _pair_status(c, anchor_path, anchor_key_path)
            if st["state"] != "RECONCILED":
                return {"ok": False, "reason": "ISSUANCE_ANCHOR_UNRESOLVED", "status": st}
            row = c.execute("SELECT permit_json,signature FROM issuance WHERE recovery_id=?", (permit.get("recovery_id"),)).fetchone()
            if row is None:
                return {"ok": False, "reason": "ISSUANCE_NOT_COMMITTED"}
            if json.loads(str(row[0])) != permit or str(row[1]) != signature:
                return {"ok": False, "reason": "ISSUANCE_CORRESPONDENCE_MISMATCH"}
        finally:
            c.close()
        return self.inner.advance({"permit": permit, "signature": signature})


if __name__ == "__main__":
    if len(sys.argv) == 7 and sys.argv[1] == "--worker":
        _normal_worker(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    elif len(sys.argv) == 10 and sys.argv[1] == "--crash-worker":
        _crash_worker(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], sys.argv[9])
    else:
        raise SystemExit("WORKER_MODE_REQUIRED")
