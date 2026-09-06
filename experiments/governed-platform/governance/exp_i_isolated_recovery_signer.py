"""EXP-I Pilot 17: process-isolated recovery-authorization signer.

The caller supplies only a recovery identity and a target root selector.  The
signer derives all governed permit semantics from authenticated root history and
the trusted-minimum store, owns the Ed25519 private key inside its process, and
persists issuance/rebinding memory before returning a permit.
"""
from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any

from exp_i_asymmetric_checkpoint_signer import _canon, _ensure_ed25519_keypair, _ed25519_sign
from exp_i_isolated_minimum_authority import _permit_body
from exp_i_root_rotation import PlatformRootTrustAuthority, RootMinimumAuthority


def _ensure_ledger(path: str) -> None:
    c = sqlite3.connect(path)
    try:
        c.execute(
            "CREATE TABLE IF NOT EXISTS issuance(" 
            "recovery_id TEXT PRIMARY KEY, target_selector TEXT NOT NULL, "
            "permit_json TEXT NOT NULL, signature TEXT NOT NULL)"
        )
        c.commit()
    finally:
        c.close()


def _signer_paths(store_dir: str) -> tuple[str, str, str]:
    d = Path(store_dir)
    d.mkdir(parents=True, exist_ok=True)
    return str(d / "recovery-signing.private.pem"), str(d / "recovery-signing.public.pem"), str(d / "issuance.db")


def _issue(root_db: str, root_auth: str, minimum_db: str, ledger_db: str, private_path: str, recovery_id: Any, target_selector: Any) -> dict[str, Any]:
    if not isinstance(recovery_id, str) or not recovery_id:
        return {"ok": False, "reason": "RECOVERY_ID_REQUIRED"}
    if not isinstance(target_selector, str) or not target_selector:
        return {"ok": False, "reason": "TARGET_SELECTOR_REQUIRED"}

    c = sqlite3.connect(ledger_db, timeout=10, isolation_level=None)
    try:
        c.execute("BEGIN IMMEDIATE")
        prior = c.execute(
            "SELECT target_selector,permit_json,signature FROM issuance WHERE recovery_id=?",
            (recovery_id,),
        ).fetchone()
        if prior is not None:
            if str(prior[0]) != target_selector:
                c.execute("ROLLBACK")
                return {"ok": False, "reason": "RECOVERY_ID_REBIND_DENIED"}
            permit = json.loads(prior[1])
            signature = str(prior[2])
            c.execute("COMMIT")
            return {"ok": True, "replay": True, "permit": permit, "signature": signature}

        trust = PlatformRootTrustAuthority(root_db, root_auth)
        history = trust.history(None)
        minimum = RootMinimumAuthority(minimum_db)
        me, md = minimum.current()
        target = None
        for item in history:
            r = item["record"]
            if r["active_root_id"] == target_selector or r["transition_id"] == target_selector:
                target = item
                break
        if target is None:
            c.execute("ROLLBACK")
            return {"ok": False, "reason": "TARGET_ROOT_NOT_FOUND"}

        te = int(target["record"]["root_epoch"])
        if te <= me:
            c.execute("ROLLBACK")
            return {"ok": False, "reason": "TARGET_NOT_ABOVE_MINIMUM"}
        if te != me + 1:
            c.execute("ROLLBACK")
            return {"ok": False, "reason": "TARGET_NOT_CONTIGUOUS"}
        if target["record"]["predecessor_root_record_digest"] != md:
            c.execute("ROLLBACK")
            return {"ok": False, "reason": "TARGET_PREDECESSOR_MISMATCH"}

        body = _permit_body(recovery_id, me, md, target)
        signature = _ed25519_sign(private_path, _canon(body))
        c.execute(
            "INSERT INTO issuance VALUES(?,?,?,?)",
            (recovery_id, target_selector, json.dumps(body, sort_keys=True), signature),
        )
        c.execute("COMMIT")
        return {"ok": True, "replay": False, "permit": body, "signature": signature}
    finally:
        c.close()


def _worker(root_db: str, root_auth: str, minimum_db: str, store_dir: str) -> None:
    private_path, public_path, ledger_db = _signer_paths(store_dir)
    _ensure_ed25519_keypair(private_path, public_path)
    _ensure_ledger(ledger_db)
    for line in sys.stdin:
        try:
            req = json.loads(line)
            op = req.get("op")
            if op == "ping":
                out = {"ok": True, "pid": os.getpid(), "public_key_pem": Path(public_path).read_text()}
            elif op == "issue":
                # Deliberately ignore every caller field except identity + selector.
                out = _issue(root_db, root_auth, minimum_db, ledger_db, private_path, req.get("recovery_id"), req.get("target_selector"))
            else:
                out = {"ok": False, "reason": "UNKNOWN_OPERATION"}
        except Exception as e:
            out = {"ok": False, "reason": f"{type(e).__name__}:{e}"}
        print(json.dumps(out, sort_keys=True), flush=True)


class RecoverySignerProcess:
    """Process manager exposes request/restart, never a private-key path or sign primitive."""
    def __init__(self, root_db: str | Path, root_auth: str | Path, minimum_db: str | Path, store_dir: str | Path):
        self.root_db = str(root_db)
        self.root_auth = str(root_auth)
        self.minimum_db = str(minimum_db)
        self.store_dir = str(store_dir)
        self.proc = None
        self._lock = threading.Lock()
        self.start()

    def start(self) -> None:
        if self.proc and self.proc.poll() is None:
            return
        self.proc = subprocess.Popen(
            [sys.executable, __file__, "--worker", self.root_db, self.root_auth, self.minimum_db, self.store_dir],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def stop(self, kill: bool = False) -> None:
        if not self.proc:
            return
        if self.proc.poll() is None:
            (self.proc.kill() if kill else self.proc.terminate())
            self.proc.wait(timeout=5)
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
            self.proc.stdin.write(json.dumps(payload, sort_keys=True) + "\n")
            self.proc.stdin.flush()
            line = self.proc.stdout.readline()
        return json.loads(line) if line else {"ok": False, "reason": "RECOVERY_SIGNER_UNAVAILABLE"}

    def issue(self, recovery_id: str, target_selector: str, **untrusted_extra: Any) -> dict[str, Any]:
        return self.request({"op": "issue", "recovery_id": recovery_id, "target_selector": target_selector, **untrusted_extra})

    @property
    def public_key_pem(self) -> str:
        out = self.request({"op": "ping"})
        if not out.get("ok"):
            raise RuntimeError(out.get("reason", "RECOVERY_SIGNER_UNAVAILABLE"))
        return str(out["public_key_pem"])


if __name__ == "__main__":
    if len(sys.argv) == 6 and sys.argv[1] == "--worker":
        _worker(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        raise SystemExit("WORKER_MODE_REQUIRED")
