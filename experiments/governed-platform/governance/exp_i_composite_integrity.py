from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple

from exp_i_permit_ledger_integrity import PermitLedgerIntegrityAuthority
from exp_i_reconciliation_integrity import ReconciliationIntegrityAuthority

SCOPE = "EXP-I-COMPOSITE-GOVERNANCE-STATE"


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


@dataclass(frozen=True)
class CompositeCheckpoint:
    scope: str
    generation: int
    permit_ledger_digest: str
    reconciliation_digest: str
    permit_authority_epoch: int
    previous_checkpoint_digest: str
    tag: str

    def payload(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "generation": self.generation,
            "permit_ledger_digest": self.permit_ledger_digest,
            "reconciliation_digest": self.reconciliation_digest,
            "permit_authority_epoch": self.permit_authority_epoch,
            "previous_checkpoint_digest": self.previous_checkpoint_digest,
        }

    def checkpoint_digest(self) -> str:
        return _sha({"payload": self.payload(), "tag": self.tag})


@dataclass(frozen=True)
class CompositeIntegrityDecision:
    valid: bool
    reasons: Tuple[str, ...]
    reviewer_generated_authority: bool = False
    production_authority: bool = False


class CompositeIntegrityAuthority:
    def __init__(self, db_path: str | Path, permit_integrity_key: bytes, reconciliation_integrity_key: bytes, composite_key: bytes, *, scope: str = SCOPE):
        if not permit_integrity_key or not reconciliation_integrity_key or not composite_key:
            raise ValueError("all integrity keys required")
        self._db_path = str(db_path)
        self._permit = PermitLedgerIntegrityAuthority(self._db_path, permit_integrity_key)
        self._reconciliation = ReconciliationIntegrityAuthority(self._db_path, reconciliation_integrity_key)
        self._key = bytes(composite_key)
        self._scope = scope

    def _sign(self, payload: dict[str, Any]) -> str:
        return hmac.new(self._key, _canon(payload), hashlib.sha256).hexdigest()

    def _authentic(self, checkpoint: CompositeCheckpoint) -> bool:
        return (
            checkpoint.scope == self._scope
            and isinstance(checkpoint.generation, int)
            and checkpoint.generation >= 1
            and hmac.compare_digest(checkpoint.tag, self._sign(checkpoint.payload()))
        )

    def _permit_epoch(self) -> int:
        con = sqlite3.connect(self._db_path, timeout=5.0)
        try:
            rows = con.execute("SELECT singleton, issuance_epoch FROM authority_meta ORDER BY singleton").fetchall()
        except sqlite3.Error as exc:
            raise RuntimeError("permit authority metadata unavailable or corrupt") from exc
        finally:
            con.close()
        if len(rows) != 1 or rows[0][0] != 1 or not isinstance(rows[0][1], int) or rows[0][1] < 1:
            raise RuntimeError("malformed permit authority epoch")
        return int(rows[0][1])

    def current_pair(self) -> dict[str, Any]:
        return {
            "permit_ledger_digest": self._permit.ledger_digest(),
            "reconciliation_digest": self._reconciliation.reconciliation_digest(),
            "permit_authority_epoch": self._permit_epoch(),
        }

    def issue_checkpoint(self, generation: int, *, previous: CompositeCheckpoint | None = None) -> CompositeCheckpoint:
        if not isinstance(generation, int) or generation < 1:
            raise ValueError("generation must be positive")
        if previous is None:
            predecessor = "GENESIS"
        else:
            if not self._authentic(previous):
                raise PermissionError("previous composite checkpoint invalid")
            if generation <= previous.generation:
                raise ValueError("generation must advance")
            predecessor = previous.checkpoint_digest()
        pair = self.current_pair()
        payload = {
            "scope": self._scope,
            "generation": generation,
            "permit_ledger_digest": pair["permit_ledger_digest"],
            "reconciliation_digest": pair["reconciliation_digest"],
            "permit_authority_epoch": pair["permit_authority_epoch"],
            "previous_checkpoint_digest": predecessor,
        }
        return CompositeCheckpoint(tag=self._sign(payload), **payload)

    def verify_checkpoint(self, checkpoint: CompositeCheckpoint | None, *, trusted_min_generation: int, previous: CompositeCheckpoint | None = None) -> CompositeIntegrityDecision:
        if checkpoint is None:
            return CompositeIntegrityDecision(False, ("missing composite checkpoint",))
        if not isinstance(trusted_min_generation, int) or trusted_min_generation < 1:
            return CompositeIntegrityDecision(False, ("invalid trusted minimum composite generation",))
        if checkpoint.scope != self._scope:
            return CompositeIntegrityDecision(False, ("composite checkpoint scope mismatch",))
        if checkpoint.generation < trusted_min_generation:
            return CompositeIntegrityDecision(False, ("composite checkpoint below trusted minimum",))
        if not self._authentic(checkpoint):
            return CompositeIntegrityDecision(False, ("invalid composite checkpoint authentication",))
        if previous is None:
            if checkpoint.generation == 1 and checkpoint.previous_checkpoint_digest != "GENESIS":
                return CompositeIntegrityDecision(False, ("invalid composite genesis predecessor",))
        else:
            if not self._authentic(previous):
                return CompositeIntegrityDecision(False, ("invalid composite predecessor authentication",))
            if checkpoint.generation <= previous.generation or checkpoint.previous_checkpoint_digest != previous.checkpoint_digest():
                return CompositeIntegrityDecision(False, ("composite predecessor mismatch",))
        try:
            current = self.current_pair()
        except RuntimeError as exc:
            return CompositeIntegrityDecision(False, (str(exc),))
        if checkpoint.permit_ledger_digest != current["permit_ledger_digest"]:
            return CompositeIntegrityDecision(False, ("composite permit-ledger digest mismatch",))
        if checkpoint.reconciliation_digest != current["reconciliation_digest"]:
            return CompositeIntegrityDecision(False, ("composite reconciliation digest mismatch",))
        if checkpoint.permit_authority_epoch != current["permit_authority_epoch"]:
            return CompositeIntegrityDecision(False, ("composite permit-authority epoch mismatch",))
        return CompositeIntegrityDecision(True, ("composite checkpoint matches current cross-root state",))
