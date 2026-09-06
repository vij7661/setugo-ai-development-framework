"""EXP-I Pilot 11: Ed25519 signer isolation with public-key-only verification."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

from exp_i_composite_integrity import SCOPE
from exp_i_permit_ledger_integrity import PermitLedgerIntegrityAuthority
from exp_i_reconciliation_integrity import ReconciliationIntegrityAuthority

VERSION = "exp-i-pilot11-v1"
KEY_ID = "exp-i-p11-ed25519-key-v1"


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


def _run_openssl(args: list[str], *, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["openssl", *args], input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )


def _ensure_ed25519_keypair(private_path: str | Path, public_path: str | Path) -> None:
    private = Path(private_path)
    public = Path(public_path)
    private.parent.mkdir(parents=True, exist_ok=True)
    if not private.exists():
        result = _run_openssl(["genpkey", "-algorithm", "Ed25519", "-out", str(private)])
        if result.returncode != 0:
            raise RuntimeError("ED25519_PRIVATE_KEY_GENERATION_FAILED")
        try:
            os.chmod(private, 0o600)
        except OSError:
            pass
    if not public.exists():
        result = _run_openssl(["pkey", "-in", str(private), "-pubout", "-out", str(public)])
        if result.returncode != 0:
            raise RuntimeError("ED25519_PUBLIC_KEY_EXPORT_FAILED")


def _ed25519_sign(private_path: str | Path, data: bytes) -> str:
    with tempfile.TemporaryDirectory() as td:
        data_path = Path(td) / "statement.bin"
        sig_path = Path(td) / "signature.bin"
        data_path.write_bytes(data)
        result = _run_openssl([
            "pkeyutl", "-sign", "-rawin", "-inkey", str(private_path),
            "-in", str(data_path), "-out", str(sig_path),
        ])
        if result.returncode != 0:
            raise RuntimeError("ED25519_SIGN_FAILED")
        return base64.b64encode(sig_path.read_bytes()).decode("ascii")


def _ed25519_verify(public_pem: str, data: bytes, signature_b64: str) -> bool:
    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except Exception:
        return False
    with tempfile.TemporaryDirectory() as td:
        pub_path = Path(td) / "public.pem"
        data_path = Path(td) / "statement.bin"
        sig_path = Path(td) / "signature.bin"
        pub_path.write_text(public_pem, encoding="utf-8")
        data_path.write_bytes(data)
        sig_path.write_bytes(signature)
        result = _run_openssl([
            "pkeyutl", "-verify", "-rawin", "-pubin", "-inkey", str(pub_path),
            "-sigfile", str(sig_path), "-in", str(data_path),
        ])
        return result.returncode == 0


def _current_pair(state_db: str, permit_key: bytes, reconciliation_key: bytes) -> dict[str, Any]:
    permit = PermitLedgerIntegrityAuthority(state_db, permit_key)
    reconciliation = ReconciliationIntegrityAuthority(state_db, reconciliation_key)
    con = sqlite3.connect(state_db, timeout=5.0)
    try:
        rows = con.execute("SELECT singleton, issuance_epoch FROM authority_meta ORDER BY singleton").fetchall()
    except sqlite3.Error as exc:
        raise RuntimeError("PERMIT_AUTHORITY_METADATA_UNAVAILABLE") from exc
    finally:
        con.close()
    if len(rows) != 1 or rows[0][0] != 1 or not isinstance(rows[0][1], int) or rows[0][1] < 1:
        raise RuntimeError("PERMIT_AUTHORITY_METADATA_MALFORMED")
    return {
        "permit_ledger_digest": permit.ledger_digest(),
        "reconciliation_digest": reconciliation.reconciliation_digest(),
        "permit_authority_epoch": int(rows[0][1]),
    }


def init_signer_store(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path), isolation_level=None)
    try:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        con.execute(
            """CREATE TABLE IF NOT EXISTS asymmetric_signer_issued(
                issuance_id TEXT PRIMARY KEY,
                generation INTEGER NOT NULL UNIQUE,
                statement_json TEXT NOT NULL,
                checkpoint_digest TEXT NOT NULL,
                signature TEXT NOT NULL
            )"""
        )
        con.execute(
            "CREATE TABLE IF NOT EXISTS asymmetric_signer_meta(singleton INTEGER PRIMARY KEY CHECK(singleton=1), max_generation INTEGER NOT NULL)"
        )
        con.execute("INSERT OR IGNORE INTO asymmetric_signer_meta(singleton,max_generation) VALUES(1,0)")
    finally:
        con.close()


def init_writer_journal(path: str | Path) -> None:
    con = sqlite3.connect(str(path), isolation_level=None)
    try:
        con.execute(
            """CREATE TABLE IF NOT EXISTS asymmetric_composite_journal(
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


def _key_paths(signer_store: str | Path) -> tuple[str, str]:
    base = str(Path(signer_store).resolve())
    return base + ".ed25519-private.pem", base + ".ed25519-public.pem"


def _issue(
    *, signer_store: str, state_db: str, issuance_id: str, generation: int,
    permit_key: bytes, reconciliation_key: bytes, private_path: str,
) -> dict[str, Any]:
    if not issuance_id or not isinstance(generation, int) or generation < 1:
        return {"ok": False, "reason": "REQUEST_INVALID"}
    pair = _current_pair(state_db, permit_key, reconciliation_key)
    con = sqlite3.connect(signer_store, timeout=10.0, isolation_level=None)
    con.row_factory = sqlite3.Row
    try:
        con.execute("BEGIN IMMEDIATE")
        max_generation = int(con.execute(
            "SELECT max_generation FROM asymmetric_signer_meta WHERE singleton=1"
        ).fetchone()[0])
        existing = con.execute(
            "SELECT * FROM asymmetric_signer_issued WHERE issuance_id=?", (issuance_id,)
        ).fetchone()
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
                "ok": True, "replay": True, "statement": stored,
                "checkpoint_digest": str(existing["checkpoint_digest"]),
                "signature": str(existing["signature"]),
            }
        if generation != max_generation + 1:
            con.execute("ROLLBACK")
            return {"ok": False, "reason": "GENERATION_NOT_EXACT_NEXT", "maximum": max_generation}
        if generation == 1:
            predecessor = "GENESIS"
        else:
            prev = con.execute(
                "SELECT checkpoint_digest FROM asymmetric_signer_issued WHERE generation=?", (generation - 1,)
            ).fetchone()
            if prev is None:
                con.execute("ROLLBACK")
                return {"ok": False, "reason": "PREDECESSOR_MISSING"}
            predecessor = str(prev[0])
        body = {
            "permit_ledger_digest": pair["permit_ledger_digest"],
            "reconciliation_digest": pair["reconciliation_digest"],
            "permit_authority_epoch": pair["permit_authority_epoch"],
        }
        statement = {
            "version": VERSION,
            "key_id": KEY_ID,
            "scope": SCOPE,
            "issuance_id": issuance_id,
            "generation": generation,
            "previous_checkpoint_digest": predecessor,
            **body,
            "checkpoint_body_digest": _digest(body),
        }
        signature = _ed25519_sign(private_path, _canon(statement))
        checkpoint_digest = _digest({"statement": statement, "signature": signature})
        con.execute(
            "INSERT INTO asymmetric_signer_issued VALUES(?,?,?,?,?)",
            (issuance_id, generation, json.dumps(statement, sort_keys=True), checkpoint_digest, signature),
        )
        con.execute(
            "UPDATE asymmetric_signer_meta SET max_generation=? WHERE singleton=1", (generation,)
        )
        con.execute("COMMIT")
        return {
            "ok": True, "replay": False, "statement": statement,
            "checkpoint_digest": checkpoint_digest, "signature": signature,
        }
    except sqlite3.IntegrityError:
        try:
            con.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        return {"ok": False, "reason": "SIGNER_CONFLICT"}
    finally:
        con.close()


class PublicCheckpointVerifier:
    """Checkpoint verifier with public-key material only; no signer IPC is required."""

    def __init__(
        self, *, public_key_pem: str, state_db: str | Path,
        permit_integrity_key: bytes, reconciliation_integrity_key: bytes,
        expected_key_id: str = KEY_ID,
    ):
        if "PRIVATE KEY" in public_key_pem:
            raise ValueError("private key material forbidden")
        self.public_key_pem = public_key_pem
        self.state_db = str(state_db)
        self._permit_integrity_key = bytes(permit_integrity_key)
        self._reconciliation_integrity_key = bytes(reconciliation_integrity_key)
        self.expected_key_id = expected_key_id

    def verify_signature(
        self, record: Mapping[str, Any], *, minimum_generation: int,
        previous: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            statement = dict(record["statement"])
            signature = str(record["signature"])
            checkpoint_digest = str(record["checkpoint_digest"])
        except Exception:
            return {"ok": False, "reason": "CHECKPOINT_MALFORMED"}
        required = {
            "version", "key_id", "scope", "issuance_id", "generation",
            "previous_checkpoint_digest", "permit_ledger_digest",
            "reconciliation_digest", "permit_authority_epoch", "checkpoint_body_digest",
        }
        if set(statement) != required:
            return {"ok": False, "reason": "CHECKPOINT_SCHEMA_INVALID"}
        if statement["version"] != VERSION or statement["scope"] != SCOPE:
            return {"ok": False, "reason": "CHECKPOINT_SCOPE_VERSION_INVALID"}
        if statement["key_id"] != self.expected_key_id:
            return {"ok": False, "reason": "CHECKPOINT_KEY_ID_INVALID"}
        body = {
            "permit_ledger_digest": statement["permit_ledger_digest"],
            "reconciliation_digest": statement["reconciliation_digest"],
            "permit_authority_epoch": statement["permit_authority_epoch"],
        }
        if statement["checkpoint_body_digest"] != _digest(body):
            return {"ok": False, "reason": "CHECKPOINT_BODY_DIGEST_INVALID"}
        if _digest({"statement": statement, "signature": signature}) != checkpoint_digest:
            return {"ok": False, "reason": "CHECKPOINT_DIGEST_MISMATCH"}
        if not _ed25519_verify(self.public_key_pem, _canon(statement), signature):
            return {"ok": False, "reason": "CHECKPOINT_SIGNATURE_INVALID"}
        try:
            generation = int(statement["generation"])
        except Exception:
            return {"ok": False, "reason": "CHECKPOINT_GENERATION_INVALID"}
        if generation < int(minimum_generation):
            return {"ok": False, "reason": "CHECKPOINT_ROLLBACK"}
        if previous is None:
            if generation == 1 and statement["previous_checkpoint_digest"] != "GENESIS":
                return {"ok": False, "reason": "CHECKPOINT_PREDECESSOR_INVALID"}
        else:
            prev_decision = self.verify_signature(previous, minimum_generation=1)
            if not prev_decision.get("ok"):
                return {"ok": False, "reason": "PREVIOUS_CHECKPOINT_INVALID"}
            if generation != int(previous["statement"]["generation"]) + 1:
                return {"ok": False, "reason": "CHECKPOINT_GENERATION_LINEAGE_INVALID"}
            if statement["previous_checkpoint_digest"] != previous["checkpoint_digest"]:
                return {"ok": False, "reason": "CHECKPOINT_PREDECESSOR_INVALID"}
        return {"ok": True, "statement": statement, "checkpoint_digest": checkpoint_digest}

    def verify_current(
        self, record: Mapping[str, Any], *, minimum_generation: int,
        previous: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        cryptographic = self.verify_signature(record, minimum_generation=minimum_generation, previous=previous)
        if not cryptographic.get("ok"):
            return cryptographic
        statement = cryptographic["statement"]
        try:
            pair = _current_pair(
                self.state_db, self._permit_integrity_key, self._reconciliation_integrity_key
            )
        except RuntimeError:
            return {"ok": False, "reason": "CURRENT_STATE_UNAVAILABLE"}
        if statement["permit_ledger_digest"] != pair["permit_ledger_digest"]:
            return {"ok": False, "reason": "PERMIT_LEDGER_DRIFT"}
        if statement["reconciliation_digest"] != pair["reconciliation_digest"]:
            return {"ok": False, "reason": "RECONCILIATION_DRIFT"}
        if int(statement["permit_authority_epoch"]) != int(pair["permit_authority_epoch"]):
            return {"ok": False, "reason": "PERMIT_EPOCH_DRIFT"}
        return cryptographic


class AsymmetricCheckpointSignerProcess:
    """Coordinator handle; child alone creates/reads the Ed25519 private key."""

    def __init__(
        self, *, signer_store: str | Path, state_db: str | Path,
        permit_integrity_key: bytes, reconciliation_integrity_key: bytes,
    ):
        self.signer_store = str(signer_store)
        self.state_db = str(state_db)
        init_signer_store(self.signer_store)
        env = dict(os.environ)
        env["EXP_I_P11_PERMIT_KEY_HEX"] = permit_integrity_key.hex()
        env["EXP_I_P11_RECON_KEY_HEX"] = reconciliation_integrity_key.hex()
        self.argv = [sys.executable, str(Path(__file__).resolve()), "--worker", self.signer_store, self.state_db]
        self.proc = subprocess.Popen(
            self.argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, bufsize=1, env=env,
        )
        assert self.proc.stdout is not None
        ready_line = self.proc.stdout.readline()
        if not ready_line:
            raise RuntimeError("SIGNER_START_FAILED")
        ready = json.loads(ready_line)
        self.pid = int(ready["pid"])
        self.public_key_pem = str(ready["public_key_pem"])
        self.key_id = str(ready["key_id"])

    def call(self, request: Mapping[str, Any]) -> dict[str, Any]:
        if self.proc.poll() is not None:
            return {"ok": False, "reason": "SIGNER_UNAVAILABLE"}
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(json.dumps(dict(request), sort_keys=True) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        return json.loads(line) if line else {"ok": False, "reason": "SIGNER_RESPONSE_LOST"}

    def issue(self, issuance_id: str, generation: int) -> dict[str, Any]:
        return self.call({
            "op": "issue", "issuance_id": issuance_id, "generation": generation,
            "scope": SCOPE, "version": VERSION, "key_id": KEY_ID,
        })

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
                self.proc.kill(); self.proc.wait(timeout=5)
        for stream in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            try:
                if stream:
                    stream.close()
            except Exception:
                pass


class PublicKeyCompositeWriter:
    """Writer owns only public checkpoint verification material; minting is signer-only."""

    def __init__(self, *, state_db: str | Path, signer: AsymmetricCheckpointSignerProcess, verifier: PublicCheckpointVerifier):
        self.state_db = str(state_db)
        self.signer = signer
        self.verifier = verifier
        init_writer_journal(self.state_db)

    def issue(self, issuance_id: str, generation: int) -> dict[str, Any]:
        signed = self.signer.issue(issuance_id, generation)
        if not signed.get("ok"):
            raise PermissionError(str(signed.get("reason", "SIGNER_DENIED")))
        verified = self.verifier.verify_current(signed, minimum_generation=generation)
        if not verified.get("ok"):
            raise PermissionError(str(verified.get("reason", "PUBLIC_VERIFICATION_FAILED")))
        statement = dict(signed["statement"])
        if statement.get("issuance_id") != issuance_id or int(statement.get("generation", -1)) != generation:
            raise PermissionError("SIGNER_RESPONSE_BINDING_MISMATCH")
        con = sqlite3.connect(self.state_db, timeout=10.0, isolation_level=None)
        try:
            con.execute("BEGIN IMMEDIATE")
            existing = con.execute(
                "SELECT statement_json,checkpoint_digest,signature,status FROM asymmetric_composite_journal WHERE issuance_id=?",
                (issuance_id,),
            ).fetchone()
            if existing is not None:
                stored = {
                    "ok": True, "statement": json.loads(existing[0]),
                    "checkpoint_digest": existing[1], "signature": existing[2], "status": existing[3],
                }
                if (
                    stored["statement"] != statement
                    or stored["checkpoint_digest"] != signed["checkpoint_digest"]
                    or stored["signature"] != signed["signature"]
                ):
                    con.execute("ROLLBACK")
                    raise PermissionError("WRITER_REPLAY_MISMATCH")
                con.execute("COMMIT")
                return stored
            con.execute(
                "INSERT INTO asymmetric_composite_journal VALUES(?,?,?,?,?,?)",
                (issuance_id, generation, json.dumps(statement, sort_keys=True), signed["checkpoint_digest"], signed["signature"], "CURRENT"),
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

    def read_current(self, issuance_id: str) -> dict[str, Any] | None:
        con = sqlite3.connect(self.state_db)
        try:
            row = con.execute(
                "SELECT statement_json,checkpoint_digest,signature,status FROM asymmetric_composite_journal WHERE issuance_id=?",
                (issuance_id,),
            ).fetchone()
        finally:
            con.close()
        if row is None or row[3] != "CURRENT":
            return None
        return {"statement": json.loads(row[0]), "checkpoint_digest": row[1], "signature": row[2], "status": row[3]}

    def verify_current(self, issuance_id: str, *, minimum_generation: int, current_state: bool = True, previous: Mapping[str, Any] | None = None) -> dict[str, Any]:
        record = self.read_current(issuance_id)
        if record is None:
            return {"ok": False, "reason": "CURRENT_MISSING"}
        if current_state:
            return self.verifier.verify_current(record, minimum_generation=minimum_generation, previous=previous)
        return self.verifier.verify_signature(record, minimum_generation=minimum_generation, previous=previous)


def _worker_main(signer_store: str, state_db: str) -> int:
    permit_key = bytes.fromhex(os.environ.get("EXP_I_P11_PERMIT_KEY_HEX", ""))
    reconciliation_key = bytes.fromhex(os.environ.get("EXP_I_P11_RECON_KEY_HEX", ""))
    if not permit_key or not reconciliation_key:
        raise RuntimeError("SIGNER_STATE_KEYS_UNAVAILABLE")
    init_signer_store(signer_store)
    private_path, public_path = _key_paths(signer_store)
    _ensure_ed25519_keypair(private_path, public_path)
    public_pem = Path(public_path).read_text(encoding="utf-8")
    print(json.dumps({"ready": True, "pid": os.getpid(), "key_id": KEY_ID, "public_key_pem": public_pem}), flush=True)
    for line in sys.stdin:
        try:
            request = json.loads(line)
        except Exception:
            print(json.dumps({"ok": False, "reason": "REQUEST_MALFORMED"}), flush=True)
            continue
        op = request.get("op")
        if op == "stop":
            return 0
        if op == "issue":
            required = {"op", "issuance_id", "generation", "scope", "version", "key_id"}
            if set(request) != required:
                result = {"ok": False, "reason": "ISSUE_REQUEST_SCHEMA_INVALID"}
            elif request.get("scope") != SCOPE or request.get("version") != VERSION or request.get("key_id") != KEY_ID:
                result = {"ok": False, "reason": "ISSUE_REQUEST_BINDING_INVALID"}
            else:
                result = _issue(
                    signer_store=signer_store, state_db=state_db,
                    issuance_id=str(request["issuance_id"]), generation=request["generation"],
                    permit_key=permit_key, reconciliation_key=reconciliation_key,
                    private_path=private_path,
                )
        else:
            result = {"ok": False, "reason": "OPERATION_NOT_ALLOWED"}
        print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        raise SystemExit(_worker_main(sys.argv[2], sys.argv[3]))
    raise SystemExit("worker mode required")
