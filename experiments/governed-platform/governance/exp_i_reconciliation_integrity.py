from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple

SCOPE = "EXP-I-CONVERGENCE-RECONCILIATION-LEDGER"


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


@dataclass(frozen=True)
class ReconciliationCheckpoint:
    scope: str
    generation: int
    reconciliation_digest: str
    previous_checkpoint_digest: str
    tag: str

    def payload(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "generation": self.generation,
            "reconciliation_digest": self.reconciliation_digest,
            "previous_checkpoint_digest": self.previous_checkpoint_digest,
        }

    def checkpoint_digest(self) -> str:
        return _sha({"payload": self.payload(), "tag": self.tag})


@dataclass(frozen=True)
class ReconciliationIntegrityDecision:
    valid: bool
    reasons: Tuple[str, ...]
    reviewer_generated_authority: bool = False
    production_authority: bool = False


class ReconciliationIntegrityAuthority:
    def __init__(self, db_path: str | Path, integrity_key: bytes, *, scope: str = SCOPE):
        if not integrity_key:
            raise ValueError("integrity_key required")
        self._db_path = str(db_path)
        self._key = bytes(integrity_key)
        self._scope = scope

    def _sign(self, payload: dict[str, Any]) -> str:
        return hmac.new(self._key, _canon(payload), hashlib.sha256).hexdigest()

    def _authentic(self, cp: ReconciliationCheckpoint) -> bool:
        return cp.scope == self._scope and isinstance(cp.generation, int) and cp.generation >= 1 and hmac.compare_digest(cp.tag, self._sign(cp.payload()))

    def canonical_state(self) -> dict[str, Any]:
        con = sqlite3.connect(self._db_path, timeout=5.0)
        try:
            rows = con.execute(
                "SELECT reconciliation_id,token_nonce,permit_nonce,pre_ledger_digest,post_ledger_digest,checkpoint_generation,status,settlement_checkpoint_digest "
                "FROM convergence_reconciliation ORDER BY reconciliation_id"
            ).fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError("reconciliation database unavailable or corrupt") from exc
        finally:
            con.close()
        out = []
        seen_ids, seen_tokens = set(), set()
        for rid, token, permit, pre, post, generation, status, settlement in rows:
            if not all(isinstance(x, str) and x for x in (rid, token, permit, pre, post)):
                raise RuntimeError("malformed reconciliation row")
            if rid in seen_ids or token in seen_tokens:
                raise RuntimeError("duplicate reconciliation identity")
            seen_ids.add(rid); seen_tokens.add(token)
            if not isinstance(generation, int) or generation < 1:
                raise RuntimeError("malformed reconciliation checkpoint generation")
            if status not in {"PENDING", "SETTLED"}:
                raise RuntimeError("malformed reconciliation status")
            if status == "PENDING" and settlement is not None:
                raise RuntimeError("pending reconciliation cannot carry settlement checkpoint")
            if status == "SETTLED" and not (isinstance(settlement, str) and settlement):
                raise RuntimeError("settled reconciliation requires settlement checkpoint")
            out.append({
                "reconciliation_id": rid,
                "token_nonce": token,
                "permit_nonce": permit,
                "pre_ledger_digest": pre,
                "post_ledger_digest": post,
                "checkpoint_generation": generation,
                "status": status,
                "settlement_checkpoint_digest": settlement,
            })
        return {"scope": self._scope, "reconciliations": out}

    def reconciliation_digest(self) -> str:
        return _sha(self.canonical_state())

    def issue_checkpoint(self, generation: int, *, previous: ReconciliationCheckpoint | None = None) -> ReconciliationCheckpoint:
        if not isinstance(generation, int) or generation < 1:
            raise ValueError("generation must be positive")
        if previous is None:
            predecessor = "GENESIS"
        else:
            if not self._authentic(previous):
                raise PermissionError("previous reconciliation checkpoint invalid")
            if generation <= previous.generation:
                raise ValueError("generation must advance")
            predecessor = previous.checkpoint_digest()
        payload = {
            "scope": self._scope,
            "generation": generation,
            "reconciliation_digest": self.reconciliation_digest(),
            "previous_checkpoint_digest": predecessor,
        }
        return ReconciliationCheckpoint(tag=self._sign(payload), **payload)

    def verify_checkpoint(self, checkpoint: ReconciliationCheckpoint | None, *, trusted_min_generation: int, previous: ReconciliationCheckpoint | None = None) -> ReconciliationIntegrityDecision:
        if checkpoint is None:
            return ReconciliationIntegrityDecision(False, ("missing reconciliation checkpoint",))
        if not isinstance(trusted_min_generation, int) or trusted_min_generation < 1:
            return ReconciliationIntegrityDecision(False, ("invalid trusted minimum generation",))
        if checkpoint.scope != self._scope:
            return ReconciliationIntegrityDecision(False, ("reconciliation checkpoint scope mismatch",))
        if checkpoint.generation < trusted_min_generation:
            return ReconciliationIntegrityDecision(False, ("reconciliation checkpoint below trusted minimum",))
        if not self._authentic(checkpoint):
            return ReconciliationIntegrityDecision(False, ("invalid reconciliation checkpoint authentication",))
        if previous is None:
            if checkpoint.generation == 1 and checkpoint.previous_checkpoint_digest != "GENESIS":
                return ReconciliationIntegrityDecision(False, ("invalid reconciliation genesis predecessor",))
        else:
            if not self._authentic(previous):
                return ReconciliationIntegrityDecision(False, ("invalid reconciliation predecessor authentication",))
            if checkpoint.generation <= previous.generation or checkpoint.previous_checkpoint_digest != previous.checkpoint_digest():
                return ReconciliationIntegrityDecision(False, ("reconciliation checkpoint predecessor mismatch",))
        try:
            current = self.reconciliation_digest()
        except RuntimeError as exc:
            return ReconciliationIntegrityDecision(False, (str(exc),))
        if current != checkpoint.reconciliation_digest:
            return ReconciliationIntegrityDecision(False, ("reconciliation digest mismatch",))
        return ReconciliationIntegrityDecision(True, ("reconciliation checkpoint and state match",))
