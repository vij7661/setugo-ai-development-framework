"""EXP-I Pilot 12: externally governed Ed25519 checkpoint-key rotation/revocation."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

from exp_i_asymmetric_checkpoint_signer import (
    _canon,
    _digest,
    _ed25519_sign,
    _ed25519_verify,
    _ensure_ed25519_keypair,
    _current_pair,
)
from exp_i_composite_integrity import SCOPE

VERSION = "exp-i-pilot12-v1"
REGISTRY_VERSION = "exp-i-pilot12-trust-registry-v1"


def public_key_fingerprint(public_pem: str) -> str:
    return hashlib.sha256(public_pem.encode("utf-8")).hexdigest()


def init_registry(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path), isolation_level=None)
    try:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        con.execute(
            """CREATE TABLE IF NOT EXISTS trust_events(
                trust_epoch INTEGER PRIMARY KEY,
                event_json TEXT NOT NULL,
                event_digest TEXT NOT NULL UNIQUE,
                signature TEXT NOT NULL
            )"""
        )
    finally:
        con.close()


def init_checkpoint_journal(path: str | Path) -> None:
    con = sqlite3.connect(str(path), isolation_level=None)
    try:
        con.execute(
            """CREATE TABLE IF NOT EXISTS rotating_checkpoint_journal(
                issuance_id TEXT PRIMARY KEY,
                generation INTEGER NOT NULL UNIQUE,
                statement_json TEXT NOT NULL,
                checkpoint_digest TEXT NOT NULL,
                signature TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status='CURRENT')
            )"""
        )
    finally:
        con.close()


class PlatformTrustRegistryAuthority:
    """Only this object can append trust events; readers receive public key only."""

    def __init__(self, registry_db: str | Path):
        self.registry_db = str(registry_db)
        init_registry(self.registry_db)
        base = str(Path(self.registry_db).resolve())
        self._private_path = base + ".registry-private.pem"
        self._public_path = base + ".registry-public.pem"
        _ensure_ed25519_keypair(self._private_path, self._public_path)
        self.public_key_pem = Path(self._public_path).read_text(encoding="utf-8")

    def _latest(self, con: sqlite3.Connection) -> tuple[int, dict[str, Any], str] | None:
        row = con.execute(
            "SELECT trust_epoch,event_json,event_digest FROM trust_events ORDER BY trust_epoch DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return None
        return int(row[0]), json.loads(row[1]), str(row[2])

    def bootstrap(self, *, key_id: str, public_key_pem: str, activation_generation: int = 1) -> dict[str, Any]:
        if not key_id or activation_generation != 1:
            raise ValueError("BOOTSTRAP_INVALID")
        con = sqlite3.connect(self.registry_db, timeout=10.0, isolation_level=None)
        try:
            con.execute("BEGIN IMMEDIATE")
            if self._latest(con) is not None:
                con.execute("ROLLBACK")
                raise PermissionError("REGISTRY_ALREADY_BOOTSTRAPPED")
            event = {
                "registry_version": REGISTRY_VERSION,
                "trust_epoch": 1,
                "event_type": "BOOTSTRAP",
                "prior_key_id": None,
                "prior_status_after": None,
                "active_key_id": key_id,
                "active_public_key_pem": public_key_pem,
                "active_public_key_fingerprint": public_key_fingerprint(public_key_pem),
                "activation_generation": activation_generation,
                "predecessor_event_digest": "GENESIS",
            }
            signature = _ed25519_sign(self._private_path, _canon(event))
            digest = _digest({"event": event, "signature": signature})
            con.execute(
                "INSERT INTO trust_events VALUES(?,?,?,?)",
                (1, json.dumps(event, sort_keys=True), digest, signature),
            )
            con.execute("COMMIT")
            return {"event": event, "event_digest": digest, "signature": signature}
        finally:
            con.close()

    def rotate(self, *, new_key_id: str, new_public_key_pem: str, activation_generation: int) -> dict[str, Any]:
        if not new_key_id or activation_generation < 2:
            raise ValueError("ROTATION_INVALID")
        con = sqlite3.connect(self.registry_db, timeout=10.0, isolation_level=None)
        try:
            con.execute("BEGIN IMMEDIATE")
            latest = self._latest(con)
            if latest is None:
                con.execute("ROLLBACK")
                raise PermissionError("REGISTRY_NOT_BOOTSTRAPPED")
            epoch, prior, predecessor = latest
            if new_key_id == prior["active_key_id"]:
                con.execute("ROLLBACK")
                raise PermissionError("KEY_ID_REUSE_DENIED")
            expected_generation = int(prior["activation_generation"]) + 1
            # Rotation activation must advance exactly one checkpoint generation in this bounded pilot.
            if activation_generation != expected_generation:
                con.execute("ROLLBACK")
                raise PermissionError("ROTATION_GENERATION_NOT_EXACT_NEXT")
            event = {
                "registry_version": REGISTRY_VERSION,
                "trust_epoch": epoch + 1,
                "event_type": "ROTATE_REVOKE",
                "prior_key_id": prior["active_key_id"],
                "prior_status_after": "REVOKED",
                "active_key_id": new_key_id,
                "active_public_key_pem": new_public_key_pem,
                "active_public_key_fingerprint": public_key_fingerprint(new_public_key_pem),
                "activation_generation": activation_generation,
                "predecessor_event_digest": predecessor,
            }
            signature = _ed25519_sign(self._private_path, _canon(event))
            digest = _digest({"event": event, "signature": signature})
            con.execute(
                "INSERT INTO trust_events VALUES(?,?,?,?)",
                (epoch + 1, json.dumps(event, sort_keys=True), digest, signature),
            )
            con.execute("COMMIT")
            return {"event": event, "event_digest": digest, "signature": signature}
        except sqlite3.IntegrityError as exc:
            try:
                con.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise PermissionError("TRUST_ROTATION_CONFLICT") from exc
        finally:
            con.close()


class TrustRegistryReader:
    """Read/verify surface with registry public key only; no trust mutation methods."""

    def __init__(self, registry_db: str | Path, registry_public_key_pem: str):
        if "PRIVATE KEY" in registry_public_key_pem:
            raise ValueError("PRIVATE_REGISTRY_KEY_FORBIDDEN")
        self.registry_db = str(registry_db)
        self.registry_public_key_pem = registry_public_key_pem

    def history(self, *, minimum_trust_epoch: int = 1) -> list[dict[str, Any]]:
        con = sqlite3.connect(self.registry_db)
        try:
            rows = con.execute(
                "SELECT trust_epoch,event_json,event_digest,signature FROM trust_events ORDER BY trust_epoch"
            ).fetchall()
        finally:
            con.close()
        if not rows:
            raise PermissionError("TRUST_REGISTRY_EMPTY")
        out: list[dict[str, Any]] = []
        predecessor = "GENESIS"
        last_epoch = 0
        seen_keys: set[str] = set()
        for epoch_raw, event_json, event_digest, signature in rows:
            epoch = int(epoch_raw)
            event = json.loads(event_json)
            if epoch != last_epoch + 1 or int(event.get("trust_epoch", -1)) != epoch:
                raise PermissionError("TRUST_EPOCH_CHAIN_INVALID")
            if event.get("registry_version") != REGISTRY_VERSION:
                raise PermissionError("TRUST_REGISTRY_VERSION_INVALID")
            if event.get("predecessor_event_digest") != predecessor:
                raise PermissionError("TRUST_PREDECESSOR_INVALID")
            if public_key_fingerprint(str(event.get("active_public_key_pem", ""))) != event.get("active_public_key_fingerprint"):
                raise PermissionError("TRUST_FINGERPRINT_INVALID")
            if not _ed25519_verify(self.registry_public_key_pem, _canon(event), str(signature)):
                raise PermissionError("TRUST_EVENT_SIGNATURE_INVALID")
            if _digest({"event": event, "signature": signature}) != str(event_digest):
                raise PermissionError("TRUST_EVENT_DIGEST_INVALID")
            key_id = str(event.get("active_key_id", ""))
            if not key_id or key_id in seen_keys:
                raise PermissionError("TRUST_KEY_ID_INVALID")
            seen_keys.add(key_id)
            out.append({"event": event, "event_digest": str(event_digest), "signature": str(signature)})
            predecessor = str(event_digest)
            last_epoch = epoch
        if last_epoch < int(minimum_trust_epoch):
            raise PermissionError("TRUST_EPOCH_ROLLBACK")
        return out

    def current(self, *, minimum_trust_epoch: int = 1) -> dict[str, Any]:
        return self.history(minimum_trust_epoch=minimum_trust_epoch)[-1]

    def key_record(self, key_id: str, *, minimum_trust_epoch: int = 1) -> dict[str, Any] | None:
        history = self.history(minimum_trust_epoch=minimum_trust_epoch)
        current = history[-1]["event"]
        for item in history:
            event = item["event"]
            if event["active_key_id"] == key_id:
                status = "ACTIVE" if key_id == current["active_key_id"] else "REVOKED"
                return {**event, "status": status}
        return None


class RotatingCheckpointVerifier:
    def __init__(
        self, *, registry_reader: TrustRegistryReader, state_db: str | Path,
        permit_integrity_key: bytes, reconciliation_integrity_key: bytes,
        minimum_trust_epoch: int = 1,
    ):
        self.registry_reader = registry_reader
        self.state_db = str(state_db)
        self._permit_key = bytes(permit_integrity_key)
        self._reconciliation_key = bytes(reconciliation_integrity_key)
        self.minimum_trust_epoch = int(minimum_trust_epoch)

    def verify_math(self, record: Mapping[str, Any]) -> dict[str, Any]:
        try:
            statement = dict(record["statement"])
            signature = str(record["signature"])
            checkpoint_digest = str(record["checkpoint_digest"])
            key_id = str(statement["key_id"])
            trust_epoch = int(statement["trust_epoch"])
        except Exception:
            return {"ok": False, "reason": "CHECKPOINT_MALFORMED"}
        try:
            history = self.registry_reader.history(minimum_trust_epoch=1)
        except PermissionError as exc:
            return {"ok": False, "reason": str(exc)}
        key_event = next((x["event"] for x in history if x["event"]["active_key_id"] == key_id), None)
        if key_event is None:
            return {"ok": False, "reason": "CHECKPOINT_KEY_UNKNOWN"}
        if int(key_event["trust_epoch"]) != trust_epoch:
            return {"ok": False, "reason": "CHECKPOINT_TRUST_EPOCH_BINDING_INVALID"}
        body = {
            "permit_ledger_digest": statement.get("permit_ledger_digest"),
            "reconciliation_digest": statement.get("reconciliation_digest"),
            "permit_authority_epoch": statement.get("permit_authority_epoch"),
        }
        if statement.get("checkpoint_body_digest") != _digest(body):
            return {"ok": False, "reason": "CHECKPOINT_BODY_DIGEST_INVALID"}
        if statement.get("version") != VERSION or statement.get("scope") != SCOPE:
            return {"ok": False, "reason": "CHECKPOINT_SCOPE_VERSION_INVALID"}
        if _digest({"statement": statement, "signature": signature}) != checkpoint_digest:
            return {"ok": False, "reason": "CHECKPOINT_DIGEST_MISMATCH"}
        if not _ed25519_verify(key_event["active_public_key_pem"], _canon(statement), signature):
            return {"ok": False, "reason": "CHECKPOINT_SIGNATURE_INVALID"}
        return {"ok": True, "statement": statement, "checkpoint_digest": checkpoint_digest}

    def verify_current(self, record: Mapping[str, Any], *, previous: Mapping[str, Any] | None = None) -> dict[str, Any]:
        math = self.verify_math(record)
        if not math.get("ok"):
            return math
        statement = math["statement"]
        try:
            current = self.registry_reader.current(minimum_trust_epoch=self.minimum_trust_epoch)["event"]
        except PermissionError as exc:
            return {"ok": False, "reason": str(exc)}
        if statement["key_id"] != current["active_key_id"]:
            return {"ok": False, "reason": "CHECKPOINT_KEY_REVOKED_OR_INACTIVE"}
        if int(statement["trust_epoch"]) != int(current["trust_epoch"]):
            return {"ok": False, "reason": "CHECKPOINT_TRUST_EPOCH_STALE"}
        if public_key_fingerprint(current["active_public_key_pem"]) != current["active_public_key_fingerprint"]:
            return {"ok": False, "reason": "CHECKPOINT_TRUST_FINGERPRINT_INVALID"}
        if int(statement["generation"]) < int(current["activation_generation"]):
            return {"ok": False, "reason": "CHECKPOINT_BEFORE_KEY_ACTIVATION"}
        try:
            pair = _current_pair(self.state_db, self._permit_key, self._reconciliation_key)
        except RuntimeError:
            return {"ok": False, "reason": "CURRENT_STATE_UNAVAILABLE"}
        if statement["permit_ledger_digest"] != pair["permit_ledger_digest"]:
            return {"ok": False, "reason": "PERMIT_LEDGER_DRIFT"}
        if statement["reconciliation_digest"] != pair["reconciliation_digest"]:
            return {"ok": False, "reason": "RECONCILIATION_DRIFT"}
        if int(statement["permit_authority_epoch"]) != int(pair["permit_authority_epoch"]):
            return {"ok": False, "reason": "PERMIT_EPOCH_DRIFT"}
        if previous is not None:
            prev_math = self.verify_math(previous)
            if not prev_math.get("ok"):
                return {"ok": False, "reason": "PREVIOUS_CHECKPOINT_INVALID"}
            if int(statement["generation"]) != int(previous["statement"]["generation"]) + 1:
                return {"ok": False, "reason": "CHECKPOINT_GENERATION_LINEAGE_INVALID"}
            if statement["previous_checkpoint_digest"] != previous["checkpoint_digest"]:
                return {"ok": False, "reason": "CHECKPOINT_PREDECESSOR_INVALID"}
        elif int(statement["generation"]) == 1 and statement["previous_checkpoint_digest"] != "GENESIS":
            return {"ok": False, "reason": "CHECKPOINT_PREDECESSOR_INVALID"}
        return math


class RotatingCheckpointSignerProcess:
    """Per-key signer. It can read trust state but has no registry mutation API."""

    def __init__(
        self, *, key_id: str, signer_store: str | Path, state_db: str | Path,
        registry_db: str | Path, registry_public_key_pem: str,
        permit_integrity_key: bytes, reconciliation_integrity_key: bytes,
    ):
        self.key_id = key_id
        self.signer_store = str(signer_store)
        self.state_db = str(state_db)
        self.registry_db = str(registry_db)
        Path(self.signer_store).parent.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ)
        env["EXP_I_P12_PERMIT_KEY_HEX"] = permit_integrity_key.hex()
        env["EXP_I_P12_RECON_KEY_HEX"] = reconciliation_integrity_key.hex()
        env["EXP_I_P12_REGISTRY_PUBLIC_B64"] = __import__("base64").b64encode(registry_public_key_pem.encode()).decode()
        self.argv = [
            sys.executable, str(Path(__file__).resolve()), "--worker", key_id,
            self.signer_store, self.state_db, self.registry_db,
        ]
        self.proc = subprocess.Popen(
            self.argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1, env=env,
        )
        assert self.proc.stdout is not None
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("ROTATING_SIGNER_START_FAILED")
        ready = json.loads(line)
        self.pid = int(ready["pid"])
        self.public_key_pem = str(ready["public_key_pem"])
        self.fingerprint = str(ready["fingerprint"])

    def issue(self, issuance_id: str, generation: int) -> dict[str, Any]:
        if self.proc.poll() is not None:
            return {"ok": False, "reason": "SIGNER_UNAVAILABLE"}
        assert self.proc.stdin is not None and self.proc.stdout is not None
        request = {"op": "issue", "issuance_id": issuance_id, "generation": generation}
        self.proc.stdin.write(json.dumps(request, sort_keys=True) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line) if line else {"ok": False, "reason": "SIGNER_RESPONSE_LOST"}

    def call(self, request: Mapping[str, Any]) -> dict[str, Any]:
        if self.proc.poll() is not None:
            return {"ok": False, "reason": "SIGNER_UNAVAILABLE"}
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(dict(request), sort_keys=True) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line) if line else {"ok": False, "reason": "SIGNER_RESPONSE_LOST"}

    def stop(self, *, kill: bool = False) -> None:
        if self.proc.poll() is None:
            if kill:
                self.proc.kill()
            else:
                try:
                    assert self.proc.stdin is not None
                    self.proc.stdin.write('{"op":"stop"}\n'); self.proc.stdin.flush()
                except Exception:
                    self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill(); self.proc.wait(timeout=5)
        for stream in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            try:
                if stream:
                    stream.close()
            except Exception:
                pass


class RotatingCheckpointWriter:
    def __init__(self, *, state_db: str | Path, verifier: RotatingCheckpointVerifier):
        self.state_db = str(state_db)
        self.verifier = verifier
        init_checkpoint_journal(self.state_db)

    def issue(self, *, signer: RotatingCheckpointSignerProcess, issuance_id: str, generation: int, previous: Mapping[str, Any] | None = None) -> dict[str, Any]:
        signed = signer.issue(issuance_id, generation)
        if not signed.get("ok"):
            raise PermissionError(str(signed.get("reason", "SIGNER_DENIED")))
        decision = self.verifier.verify_current(signed, previous=previous)
        if not decision.get("ok"):
            raise PermissionError(str(decision.get("reason", "CHECKPOINT_NOT_CURRENT")))
        con = sqlite3.connect(self.state_db, timeout=10.0, isolation_level=None)
        try:
            con.execute("BEGIN IMMEDIATE")
            existing = con.execute(
                "SELECT statement_json,checkpoint_digest,signature,status FROM rotating_checkpoint_journal WHERE issuance_id=?",
                (issuance_id,),
            ).fetchone()
            if existing is not None:
                stored = {"statement": json.loads(existing[0]), "checkpoint_digest": existing[1], "signature": existing[2], "status": existing[3]}
                if stored["statement"] != signed["statement"] or stored["checkpoint_digest"] != signed["checkpoint_digest"] or stored["signature"] != signed["signature"]:
                    con.execute("ROLLBACK")
                    raise PermissionError("WRITER_REPLAY_MISMATCH")
                con.execute("COMMIT")
                return stored
            con.execute(
                "INSERT INTO rotating_checkpoint_journal VALUES(?,?,?,?,?,?)",
                (issuance_id, generation, json.dumps(signed["statement"], sort_keys=True), signed["checkpoint_digest"], signed["signature"], "CURRENT"),
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


def _signer_store_init(path: str) -> None:
    con = sqlite3.connect(path, isolation_level=None)
    try:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        con.execute(
            """CREATE TABLE IF NOT EXISTS signer_issued(
                issuance_id TEXT PRIMARY KEY,
                generation INTEGER NOT NULL UNIQUE,
                statement_json TEXT NOT NULL,
                checkpoint_digest TEXT NOT NULL,
                signature TEXT NOT NULL
            )"""
        )
    finally:
        con.close()


def _journal_tip(state_db: str) -> tuple[int, str]:
    init_checkpoint_journal(state_db)
    con = sqlite3.connect(state_db)
    try:
        row = con.execute(
            "SELECT generation,checkpoint_digest FROM rotating_checkpoint_journal ORDER BY generation DESC LIMIT 1"
        ).fetchone()
    finally:
        con.close()
    return (0, "GENESIS") if row is None else (int(row[0]), str(row[1]))


def _worker_main(key_id: str, signer_store: str, state_db: str, registry_db: str) -> int:
    import base64
    permit_key = bytes.fromhex(os.environ.get("EXP_I_P12_PERMIT_KEY_HEX", ""))
    recon_key = bytes.fromhex(os.environ.get("EXP_I_P12_RECON_KEY_HEX", ""))
    registry_public = base64.b64decode(os.environ.get("EXP_I_P12_REGISTRY_PUBLIC_B64", "")).decode()
    if not permit_key or not recon_key or not registry_public:
        raise RuntimeError("SIGNER_BOOTSTRAP_MATERIAL_MISSING")
    _signer_store_init(signer_store)
    private_path = signer_store + ".ed25519-private.pem"
    public_path = signer_store + ".ed25519-public.pem"
    _ensure_ed25519_keypair(private_path, public_path)
    public_pem = Path(public_path).read_text(encoding="utf-8")
    fingerprint = public_key_fingerprint(public_pem)
    reader = TrustRegistryReader(registry_db, registry_public)
    print(json.dumps({"ready": True, "pid": os.getpid(), "key_id": key_id, "public_key_pem": public_pem, "fingerprint": fingerprint}), flush=True)
    for line in sys.stdin:
        try:
            request = json.loads(line)
        except Exception:
            print(json.dumps({"ok": False, "reason": "REQUEST_MALFORMED"}), flush=True); continue
        if request.get("op") == "stop":
            return 0
        if request.get("op") != "issue" or set(request) != {"op", "issuance_id", "generation"}:
            print(json.dumps({"ok": False, "reason": "OPERATION_NOT_ALLOWED"}), flush=True); continue
        issuance_id = request.get("issuance_id")
        generation = request.get("generation")
        if not isinstance(issuance_id, str) or not issuance_id or not isinstance(generation, int) or generation < 1:
            print(json.dumps({"ok": False, "reason": "REQUEST_INVALID"}), flush=True); continue
        try:
            current = reader.current()["event"]
        except PermissionError as exc:
            print(json.dumps({"ok": False, "reason": str(exc)}), flush=True); continue
        if current["active_key_id"] != key_id or current["active_public_key_fingerprint"] != fingerprint:
            print(json.dumps({"ok": False, "reason": "SIGNER_KEY_NOT_ACTIVE"}), flush=True); continue
        if generation < int(current["activation_generation"]):
            print(json.dumps({"ok": False, "reason": "GENERATION_BEFORE_KEY_ACTIVATION"}), flush=True); continue
        pair = _current_pair(state_db, permit_key, recon_key)
        tip_generation, predecessor = _journal_tip(state_db)
        con = sqlite3.connect(signer_store, timeout=10.0, isolation_level=None)
        con.row_factory = sqlite3.Row
        try:
            con.execute("BEGIN IMMEDIATE")
            existing = con.execute("SELECT * FROM signer_issued WHERE issuance_id=?", (issuance_id,)).fetchone()
            if existing is not None:
                stored = json.loads(existing["statement_json"])
                if int(existing["generation"]) != generation or stored["permit_ledger_digest"] != pair["permit_ledger_digest"] or stored["reconciliation_digest"] != pair["reconciliation_digest"] or int(stored["permit_authority_epoch"]) != int(pair["permit_authority_epoch"]):
                    con.execute("ROLLBACK")
                    result = {"ok": False, "reason": "ISSUANCE_REBINDING_OR_STATE_DRIFT"}
                else:
                    con.execute("COMMIT")
                    result = {"ok": True, "replay": True, "statement": stored, "checkpoint_digest": str(existing["checkpoint_digest"]), "signature": str(existing["signature"])}
                print(json.dumps(result, sort_keys=True), flush=True); continue
            if generation != tip_generation + 1:
                con.execute("ROLLBACK")
                print(json.dumps({"ok": False, "reason": "GENERATION_NOT_EXACT_NEXT", "tip_generation": tip_generation}), flush=True); continue
            body = {"permit_ledger_digest": pair["permit_ledger_digest"], "reconciliation_digest": pair["reconciliation_digest"], "permit_authority_epoch": pair["permit_authority_epoch"]}
            statement = {
                "version": VERSION, "scope": SCOPE, "key_id": key_id,
                "trust_epoch": int(current["trust_epoch"]), "issuance_id": issuance_id,
                "generation": generation, "previous_checkpoint_digest": predecessor,
                **body, "checkpoint_body_digest": _digest(body),
            }
            signature = _ed25519_sign(private_path, _canon(statement))
            checkpoint_digest = _digest({"statement": statement, "signature": signature})
            con.execute("INSERT INTO signer_issued VALUES(?,?,?,?,?)", (issuance_id, generation, json.dumps(statement, sort_keys=True), checkpoint_digest, signature))
            con.execute("COMMIT")
            result = {"ok": True, "replay": False, "statement": statement, "checkpoint_digest": checkpoint_digest, "signature": signature}
        except sqlite3.IntegrityError:
            try:
                con.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            result = {"ok": False, "reason": "SIGNER_CONFLICT"}
        finally:
            con.close()
        print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 6 and sys.argv[1] == "--worker":
        raise SystemExit(_worker_main(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
    raise SystemExit("worker mode required")
