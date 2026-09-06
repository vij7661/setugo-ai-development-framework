from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Tuple

from exp_i_claim_convergence_gate import GateState, ReviewClaim, VerificationArtifact, evaluate_review_gate
from exp_i_convergence_permit import ConvergencePermit, PermitDecision, _digest_json, signals_digest, verification_digest
from tri_reviewer_convergence import decide_convergence


class DurableConvergencePermitAuthority:
    ISSUER = "exp-i-platform-convergence-authority"

    def __init__(self, db_path: str | Path, signing_key: bytes):
        if not signing_key:
            raise ValueError("signing_key required")
        self._db_path = str(db_path)
        self._signing_key = bytes(signing_key)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self._db_path, timeout=5.0, isolation_level=None)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def _initialize(self) -> None:
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            con.execute("CREATE TABLE IF NOT EXISTS authority_meta (singleton INTEGER PRIMARY KEY CHECK(singleton=1), issuance_epoch INTEGER NOT NULL CHECK(issuance_epoch >= 1))")
            con.execute("CREATE TABLE IF NOT EXISTS permit_ledger (nonce TEXT PRIMARY KEY, binding_digest TEXT NOT NULL, payload_json TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('ISSUED','CONSUMED'))) ")
            row = con.execute("SELECT issuance_epoch FROM authority_meta WHERE singleton=1").fetchone()
            if row is None:
                con.execute("INSERT INTO authority_meta(singleton, issuance_epoch) VALUES(1,1)")
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
        finally:
            con.close()

    @property
    def issuance_epoch(self) -> int:
        con = self._connect()
        try:
            row = con.execute("SELECT issuance_epoch FROM authority_meta WHERE singleton=1").fetchone()
            if row is None or not isinstance(row[0], int) or row[0] < 1:
                raise RuntimeError("malformed authority epoch state")
            return int(row[0])
        finally:
            con.close()

    def advance_epoch(self) -> int:
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT issuance_epoch FROM authority_meta WHERE singleton=1").fetchone()
            if row is None or not isinstance(row[0], int) or row[0] < 1:
                raise RuntimeError("malformed authority epoch state")
            nxt = int(row[0]) + 1
            con.execute("UPDATE authority_meta SET issuance_epoch=? WHERE singleton=1", (nxt,))
            con.execute("COMMIT")
            return nxt
        except Exception:
            con.execute("ROLLBACK")
            raise
        finally:
            con.close()

    def _sign(self, payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        return hmac.new(self._signing_key, encoded, hashlib.sha256).hexdigest()

    def _valid_signature(self, permit: ConvergencePermit) -> bool:
        return hmac.compare_digest(permit.signature, self._sign(permit.payload()))

    def _binding(self, case_id: str, primary: str, scope: Tuple[str, ...], verification: VerificationArtifact, signals: dict[str, Any], epoch: int) -> str:
        return _digest_json({
            "case_id": case_id,
            "primary_failure_class": primary,
            "authorized_artifact_scope": list(scope),
            "verification_digest": verification_digest(verification),
            "signals_digest": signals_digest(signals),
            "issuance_epoch": epoch,
        })

    def issue(self, reviews: Iterable[ReviewClaim], verification: VerificationArtifact, signals: dict[str, Any], *, nonce: str) -> ConvergencePermit:
        claim = evaluate_review_gate(tuple(reviews), verification)
        if claim.state != GateState.ELIGIBLE_FOR_GOVERNANCE_GATE:
            raise PermissionError(f"claim gate not eligible: {claim.state.value}")
        if not nonce:
            raise ValueError("nonce required")

        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute("SELECT issuance_epoch FROM authority_meta WHERE singleton=1").fetchone()
            if row is None or not isinstance(row[0], int) or row[0] < 1:
                raise RuntimeError("malformed authority epoch state")
            epoch = int(row[0])
            binding = self._binding(claim.case_id, claim.canonical_primary_failure_class, tuple(claim.canonical_artifact_scope), verification, signals, epoch)
            prior = con.execute("SELECT binding_digest, payload_json, status FROM permit_ledger WHERE nonce=?", (nonce,)).fetchone()
            if prior is not None:
                if prior[0] != binding:
                    raise PermissionError("nonce semantic rebinding denied")
                if prior[2] not in {"ISSUED", "CONSUMED"}:
                    raise RuntimeError("malformed permit ledger status")
                payload = json.loads(prior[1])
                con.execute("COMMIT")
                return ConvergencePermit(signature=self._sign(payload), **payload)

            payload = {
                "issuer": self.ISSUER,
                "case_id": claim.case_id,
                "primary_failure_class": claim.canonical_primary_failure_class,
                "authorized_artifact_scope": list(claim.canonical_artifact_scope),
                "verification_digest": verification_digest(verification),
                "signals_digest": signals_digest(signals),
                "issuance_epoch": epoch,
                "nonce": nonce,
            }
            con.execute(
                "INSERT INTO permit_ledger(nonce,binding_digest,payload_json,status) VALUES(?,?,?,?)",
                (nonce, binding, json.dumps(payload, sort_keys=True, separators=(",", ":")), "ISSUED"),
            )
            con.execute("COMMIT")
            return ConvergencePermit(signature=self._sign(payload), **payload)
        except Exception:
            try:
                con.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            raise
        finally:
            con.close()

    def consume(self, permit: ConvergencePermit, reviews: Iterable[ReviewClaim], verification: VerificationArtifact, signals: dict[str, Any]) -> PermitDecision:
        reviews = tuple(reviews)
        if permit.issuer != self.ISSUER:
            return PermitDecision("DENIED", ("non-platform permit issuer",), False)
        if not self._valid_signature(permit):
            return PermitDecision("DENIED", ("invalid permit signature",), False)

        claim = evaluate_review_gate(reviews, verification)
        if claim.state != GateState.ELIGIBLE_FOR_GOVERNANCE_GATE:
            return PermitDecision("DENIED", (f"claim gate changed: {claim.state.value}",), False)
        if permit.case_id != claim.case_id or permit.primary_failure_class != claim.canonical_primary_failure_class or tuple(permit.authorized_artifact_scope) != tuple(claim.canonical_artifact_scope):
            return PermitDecision("DENIED", ("permit claim binding mismatch",), False)
        if permit.verification_digest != verification_digest(verification):
            return PermitDecision("DENIED", ("permit verification binding mismatch",), False)
        if permit.signals_digest != signals_digest(signals):
            return PermitDecision("DENIED", ("permit convergence-signal binding mismatch",), False)

        expected_binding = self._binding(claim.case_id, claim.canonical_primary_failure_class, tuple(claim.canonical_artifact_scope), verification, signals, permit.issuance_epoch)
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            epoch_row = con.execute("SELECT issuance_epoch FROM authority_meta WHERE singleton=1").fetchone()
            if epoch_row is None or not isinstance(epoch_row[0], int) or epoch_row[0] < 1:
                con.execute("ROLLBACK")
                return PermitDecision("DENIED", ("malformed authority epoch state",), False)
            if permit.issuance_epoch != int(epoch_row[0]):
                con.execute("ROLLBACK")
                return PermitDecision("DENIED", ("stale convergence permit epoch",), False)
            row = con.execute("SELECT binding_digest, payload_json, status FROM permit_ledger WHERE nonce=?", (permit.nonce,)).fetchone()
            if row is None:
                con.execute("ROLLBACK")
                return PermitDecision("DENIED", ("missing durable permit record",), False)
            if row[2] not in {"ISSUED", "CONSUMED"}:
                con.execute("ROLLBACK")
                return PermitDecision("DENIED", ("malformed permit ledger status",), False)
            if row[0] != expected_binding:
                con.execute("ROLLBACK")
                return PermitDecision("DENIED", ("durable nonce binding mismatch",), False)
            try:
                stored_payload = json.loads(row[1])
            except Exception:
                con.execute("ROLLBACK")
                return PermitDecision("DENIED", ("malformed durable permit payload",), False)
            if stored_payload != permit.payload():
                con.execute("ROLLBACK")
                return PermitDecision("DENIED", ("durable permit payload mismatch",), False)
            if row[2] == "CONSUMED":
                con.execute("ROLLBACK")
                return PermitDecision("DENIED", ("convergence permit already consumed",), False)
            changed = con.execute("UPDATE permit_ledger SET status='CONSUMED' WHERE nonce=? AND status='ISSUED'", (permit.nonce,)).rowcount
            if changed != 1:
                con.execute("ROLLBACK")
                return PermitDecision("DENIED", ("concurrent permit consumption lost",), False)
            con.execute("COMMIT")
        except sqlite3.Error:
            try:
                con.execute("ROLLBACK")
            except sqlite3.Error:
                pass
            return PermitDecision("DENIED", ("durable permit ledger unavailable or corrupt",), False)
        finally:
            con.close()

        terminal = decide_convergence(signals)
        return PermitDecision(
            state=terminal.state,
            reasons=terminal.reasons,
            terminal_convergence=terminal.state in {"CONVERGED_PASS", "CONVERGED_WITH_DISSENT", "CONVERGED_FAIL"},
            reviewer_generated_authority=False,
            production_authority=False,
        )
