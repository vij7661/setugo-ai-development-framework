from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Tuple

from exp_i_claim_convergence_gate import GateState, ReviewClaim, VerificationArtifact, evaluate_review_gate
from exp_i_convergence_permit import ConvergencePermit, PermitDecision, signals_digest, verification_digest
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_permit_ledger_integrity import LedgerCheckpoint, PermitLedgerIntegrityAuthority
from tri_reviewer_convergence import decide_convergence


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


@dataclass(frozen=True)
class UseTimeIntegrityToken:
    issuer: str
    permit_nonce: str
    permit_binding_digest: str
    checkpoint_digest: str
    checkpoint_generation: int
    pre_ledger_digest: str
    authority_epoch: int
    token_nonce: str
    tag: str

    def payload(self) -> dict[str, Any]:
        return {
            "issuer": self.issuer,
            "permit_nonce": self.permit_nonce,
            "permit_binding_digest": self.permit_binding_digest,
            "checkpoint_digest": self.checkpoint_digest,
            "checkpoint_generation": self.checkpoint_generation,
            "pre_ledger_digest": self.pre_ledger_digest,
            "authority_epoch": self.authority_epoch,
            "token_nonce": self.token_nonce,
        }


@dataclass(frozen=True)
class UseTimeDecision:
    state: str
    reasons: Tuple[str, ...]
    reconciliation_id: str | None = None
    reconciliation_status: str | None = None
    terminal_convergence: bool = False
    reviewer_generated_authority: bool = False
    production_authority: bool = False


class UseTimeCheckpointAuthority:
    ISSUER = "exp-i-platform-use-time-integrity-authority"

    def __init__(self, db_path: str | Path, permit_key: bytes, integrity_key: bytes, token_key: bytes):
        if not permit_key or not integrity_key or not token_key:
            raise ValueError("all keys required")
        self._db_path = str(db_path)
        self._permit_key = bytes(permit_key)
        self._integrity_key = bytes(integrity_key)
        self._token_key = bytes(token_key)
        self._permit_auth = DurableConvergencePermitAuthority(self._db_path, self._permit_key)
        self._integrity = PermitLedgerIntegrityAuthority(self._db_path, self._integrity_key)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self._db_path, timeout=5.0, isolation_level=None)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        return con

    def _initialize(self) -> None:
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            con.execute(
                "CREATE TABLE IF NOT EXISTS convergence_reconciliation ("
                "reconciliation_id TEXT PRIMARY KEY, token_nonce TEXT NOT NULL UNIQUE, permit_nonce TEXT NOT NULL, "
                "pre_ledger_digest TEXT NOT NULL, post_ledger_digest TEXT NOT NULL, checkpoint_generation INTEGER NOT NULL, "
                "status TEXT NOT NULL CHECK(status IN ('PENDING','SETTLED')), settlement_checkpoint_digest TEXT)"
            )
            con.execute("COMMIT")
        except Exception:
            try:
                con.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise
        finally:
            con.close()

    def _sign_token(self, payload: dict[str, Any]) -> str:
        return hmac.new(self._token_key, _canon(payload), hashlib.sha256).hexdigest()

    def _valid_token(self, token: UseTimeIntegrityToken) -> bool:
        return hmac.compare_digest(token.tag, self._sign_token(token.payload()))

    def _ledger_state_on_connection(self, con: sqlite3.Connection) -> dict[str, Any]:
        meta = con.execute("SELECT singleton, issuance_epoch FROM authority_meta ORDER BY singleton").fetchall()
        if len(meta) != 1 or meta[0][0] != 1 or not isinstance(meta[0][1], int) or meta[0][1] < 1:
            raise RuntimeError("malformed authority metadata")
        rows = con.execute("SELECT nonce,binding_digest,payload_json,status FROM permit_ledger ORDER BY nonce").fetchall()
        permits = []
        seen = set()
        for nonce, binding, payload_json, status in rows:
            if nonce in seen or status not in {"ISSUED", "CONSUMED"}:
                raise RuntimeError("malformed permit ledger")
            seen.add(nonce)
            try:
                payload = json.loads(payload_json)
            except Exception as exc:
                raise RuntimeError("malformed permit payload") from exc
            permits.append({
                "nonce": nonce,
                "binding_digest": binding,
                "payload_json": json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True),
                "status": status,
            })
        return {"scope": "EXP-I-CONVERGENCE-PERMIT-LEDGER", "issuance_epoch": int(meta[0][1]), "permits": permits}

    def _ledger_digest_on_connection(self, con: sqlite3.Connection) -> str:
        return _sha(self._ledger_state_on_connection(con))

    def issue_token(self, permit: ConvergencePermit, checkpoint: LedgerCheckpoint, *, trusted_min_generation: int, token_nonce: str) -> UseTimeIntegrityToken:
        if not token_nonce:
            raise ValueError("token_nonce required")
        verification = self._integrity.verify_checkpoint(checkpoint, trusted_min_generation=trusted_min_generation)
        if not verification.valid:
            raise PermissionError("current checkpoint not eligible for use-time token")
        if not self._permit_auth._valid_signature(permit):
            raise PermissionError("invalid convergence permit")
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            pre_digest = self._ledger_digest_on_connection(con)
            if pre_digest != checkpoint.ledger_digest:
                raise PermissionError("checkpoint became stale before token issuance")
            row = con.execute("SELECT binding_digest,status FROM permit_ledger WHERE nonce=?", (permit.nonce,)).fetchone()
            if row is None or row[1] != "ISSUED":
                raise PermissionError("permit is not durably issued")
            epoch = self._ledger_state_on_connection(con)["issuance_epoch"]
            if permit.issuance_epoch != epoch:
                raise PermissionError("permit epoch is stale")
            existing = con.execute("SELECT token_nonce FROM convergence_reconciliation WHERE token_nonce=?", (token_nonce,)).fetchone()
            if existing is not None:
                raise PermissionError("token nonce already used")
            payload = {
                "issuer": self.ISSUER,
                "permit_nonce": permit.nonce,
                "permit_binding_digest": row[0],
                "checkpoint_digest": checkpoint.checkpoint_digest(),
                "checkpoint_generation": checkpoint.generation,
                "pre_ledger_digest": pre_digest,
                "authority_epoch": epoch,
                "token_nonce": token_nonce,
            }
            con.execute("COMMIT")
            return UseTimeIntegrityToken(tag=self._sign_token(payload), **payload)
        except Exception:
            try:
                con.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise
        finally:
            con.close()

    def consume(
        self,
        token: UseTimeIntegrityToken,
        permit: ConvergencePermit,
        reviews: Iterable[ReviewClaim],
        verification: VerificationArtifact,
        signals: dict[str, Any],
    ) -> UseTimeDecision:
        if token.issuer != self.ISSUER or not self._valid_token(token):
            return UseTimeDecision("DENIED", ("invalid use-time integrity token",))
        if not self._permit_auth._valid_signature(permit):
            return UseTimeDecision("DENIED", ("invalid convergence permit",))
        claim = evaluate_review_gate(tuple(reviews), verification)
        if claim.state != GateState.ELIGIBLE_FOR_GOVERNANCE_GATE:
            return UseTimeDecision("DENIED", (f"claim gate changed: {claim.state.value}",))
        if permit.case_id != claim.case_id or permit.primary_failure_class != claim.canonical_primary_failure_class or tuple(permit.authorized_artifact_scope) != tuple(claim.canonical_artifact_scope):
            return UseTimeDecision("DENIED", ("permit claim binding mismatch",))
        if permit.verification_digest != verification_digest(verification) or permit.signals_digest != signals_digest(signals):
            return UseTimeDecision("DENIED", ("permit evidence binding mismatch",))
        if token.permit_nonce != permit.nonce:
            return UseTimeDecision("DENIED", ("token permit nonce mismatch",))

        con = self._connect()
        reconciliation_id = f"recon:{token.token_nonce}"
        try:
            con.execute("BEGIN IMMEDIATE")
            pre_digest = self._ledger_digest_on_connection(con)
            if pre_digest != token.pre_ledger_digest:
                con.execute("ROLLBACK")
                return UseTimeDecision("DENIED", ("stale use-time ledger digest",))
            epoch = self._ledger_state_on_connection(con)["issuance_epoch"]
            if epoch != token.authority_epoch or permit.issuance_epoch != epoch:
                con.execute("ROLLBACK")
                return UseTimeDecision("DENIED", ("stale authority epoch",))
            row = con.execute("SELECT binding_digest,payload_json,status FROM permit_ledger WHERE nonce=?", (permit.nonce,)).fetchone()
            if row is None or row[0] != token.permit_binding_digest or row[2] != "ISSUED":
                con.execute("ROLLBACK")
                return UseTimeDecision("DENIED", ("durable permit state changed",))
            try:
                stored_payload = json.loads(row[1])
            except Exception:
                con.execute("ROLLBACK")
                return UseTimeDecision("DENIED", ("malformed durable permit payload",))
            if stored_payload != permit.payload():
                con.execute("ROLLBACK")
                return UseTimeDecision("DENIED", ("durable permit payload mismatch",))
            if con.execute("SELECT 1 FROM convergence_reconciliation WHERE token_nonce=?", (token.token_nonce,)).fetchone() is not None:
                con.execute("ROLLBACK")
                return UseTimeDecision("DENIED", ("use-time token already consumed",))
            changed = con.execute("UPDATE permit_ledger SET status='CONSUMED' WHERE nonce=? AND status='ISSUED'", (permit.nonce,)).rowcount
            if changed != 1:
                con.execute("ROLLBACK")
                return UseTimeDecision("DENIED", ("concurrent consumption lost",))
            post_digest = self._ledger_digest_on_connection(con)
            con.execute(
                "INSERT INTO convergence_reconciliation(reconciliation_id,token_nonce,permit_nonce,pre_ledger_digest,post_ledger_digest,checkpoint_generation,status,settlement_checkpoint_digest) VALUES(?,?,?,?,?,?,?,NULL)",
                (reconciliation_id, token.token_nonce, permit.nonce, pre_digest, post_digest, token.checkpoint_generation, "PENDING"),
            )
            con.execute("COMMIT")
        except sqlite3.Error:
            try:
                con.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            return UseTimeDecision("DENIED", ("durable use-time transaction failed",))
        finally:
            con.close()

        terminal = decide_convergence(signals)
        return UseTimeDecision(
            terminal.state,
            terminal.reasons,
            reconciliation_id=reconciliation_id,
            reconciliation_status="PENDING",
            terminal_convergence=terminal.state in {"CONVERGED_PASS", "CONVERGED_WITH_DISSENT", "CONVERGED_FAIL"},
            reviewer_generated_authority=False,
            production_authority=False,
        )

    def reconciliation_status(self, reconciliation_id: str) -> str | None:
        con = self._connect()
        try:
            row = con.execute("SELECT status FROM convergence_reconciliation WHERE reconciliation_id=?", (reconciliation_id,)).fetchone()
            if row is None:
                return None
            if row[0] not in {"PENDING", "SETTLED"}:
                raise RuntimeError("malformed reconciliation state")
            return row[0]
        finally:
            con.close()

    def settle_reconciliation(self, reconciliation_id: str, checkpoint: LedgerCheckpoint, *, trusted_min_generation: int) -> bool:
        verification = self._integrity.verify_checkpoint(checkpoint, trusted_min_generation=trusted_min_generation)
        if not verification.valid:
            return False
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT post_ledger_digest,checkpoint_generation,status FROM convergence_reconciliation WHERE reconciliation_id=?", (reconciliation_id,)).fetchone()
            if row is None or row[2] not in {"PENDING", "SETTLED"}:
                con.execute("ROLLBACK")
                return False
            if row[2] == "SETTLED":
                con.execute("ROLLBACK")
                return False
            if checkpoint.generation <= int(row[1]):
                con.execute("ROLLBACK")
                return False
            current_digest = self._ledger_digest_on_connection(con)
            if checkpoint.ledger_digest != row[0] or current_digest != row[0]:
                con.execute("ROLLBACK")
                return False
            changed = con.execute("UPDATE convergence_reconciliation SET status='SETTLED', settlement_checkpoint_digest=? WHERE reconciliation_id=? AND status='PENDING'", (checkpoint.checkpoint_digest(), reconciliation_id)).rowcount
            if changed != 1:
                con.execute("ROLLBACK")
                return False
            con.execute("COMMIT")
            return True
        except sqlite3.Error:
            try:
                con.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            return False
        finally:
            con.close()
