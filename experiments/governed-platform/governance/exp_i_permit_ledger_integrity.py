from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple


SCOPE = "EXP-I-CONVERGENCE-PERMIT-LEDGER"


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


@dataclass(frozen=True)
class LedgerCheckpoint:
    scope: str
    generation: int
    ledger_digest: str
    previous_checkpoint_digest: str
    tag: str

    def payload(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "generation": self.generation,
            "ledger_digest": self.ledger_digest,
            "previous_checkpoint_digest": self.previous_checkpoint_digest,
        }

    def checkpoint_digest(self) -> str:
        return _sha({"payload": self.payload(), "tag": self.tag})


@dataclass(frozen=True)
class IntegrityDecision:
    valid: bool
    reasons: Tuple[str, ...]
    production_authority: bool = False
    reviewer_generated_authority: bool = False


class PermitLedgerIntegrityAuthority:
    def __init__(self, db_path: str | Path, integrity_key: bytes, *, scope: str = SCOPE):
        if not integrity_key:
            raise ValueError("integrity_key required")
        if not scope:
            raise ValueError("scope required")
        self._db_path = str(db_path)
        self._key = bytes(integrity_key)
        self._scope = scope

    def _sign(self, payload: dict[str, Any]) -> str:
        return hmac.new(self._key, _canonical_json(payload), hashlib.sha256).hexdigest()

    def canonical_state(self) -> dict[str, Any]:
        con = sqlite3.connect(self._db_path, timeout=5.0)
        try:
            epoch_rows = con.execute("SELECT singleton, issuance_epoch FROM authority_meta ORDER BY singleton").fetchall()
            if epoch_rows != [(1, epoch_rows[0][1])] if epoch_rows else True:
                raise RuntimeError("malformed authority metadata cardinality")
            epoch = epoch_rows[0][1]
            if not isinstance(epoch, int) or epoch < 1:
                raise RuntimeError("malformed authority epoch")
            rows = con.execute(
                "SELECT nonce, binding_digest, payload_json, status FROM permit_ledger ORDER BY nonce"
            ).fetchall()
            canonical_rows = []
            seen = set()
            for nonce, binding, payload_json, status in rows:
                if not all(isinstance(x, str) and x for x in (nonce, binding, payload_json, status)):
                    raise RuntimeError("malformed permit ledger row")
                if nonce in seen:
                    raise RuntimeError("duplicate permit nonce")
                seen.add(nonce)
                if status not in {"ISSUED", "CONSUMED"}:
                    raise RuntimeError("malformed permit status")
                try:
                    payload = json.loads(payload_json)
                except Exception as exc:
                    raise RuntimeError("malformed permit payload json") from exc
                normalized_payload = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
                canonical_rows.append({
                    "nonce": nonce,
                    "binding_digest": binding,
                    "payload_json": normalized_payload,
                    "status": status,
                })
            return {"scope": self._scope, "issuance_epoch": epoch, "permits": canonical_rows}
        except sqlite3.Error as exc:
            raise RuntimeError("permit database unavailable or corrupt") from exc
        finally:
            con.close()

    def ledger_digest(self) -> str:
        return _sha(self.canonical_state())

    def issue_checkpoint(self, generation: int, *, previous: LedgerCheckpoint | None = None) -> LedgerCheckpoint:
        if not isinstance(generation, int) or generation < 1:
            raise ValueError("generation must be positive")
        if previous is not None:
            prior = self.verify_checkpoint(previous, trusted_min_generation=previous.generation, previous=None)
            if not prior.valid:
                raise PermissionError("previous checkpoint is not valid current state")
            if generation <= previous.generation:
                raise ValueError("generation must advance")
            previous_digest = previous.checkpoint_digest()
        else:
            previous_digest = "GENESIS"
        payload = {
            "scope": self._scope,
            "generation": generation,
            "ledger_digest": self.ledger_digest(),
            "previous_checkpoint_digest": previous_digest,
        }
        return LedgerCheckpoint(tag=self._sign(payload), **payload)

    def verify_checkpoint(
        self,
        checkpoint: LedgerCheckpoint | None,
        *,
        trusted_min_generation: int,
        previous: LedgerCheckpoint | None = None,
        expected_scope: str | None = None,
    ) -> IntegrityDecision:
        if checkpoint is None:
            return IntegrityDecision(False, ("missing external checkpoint",))
        if not isinstance(trusted_min_generation, int) or trusted_min_generation < 1:
            return IntegrityDecision(False, ("invalid trusted minimum generation",))
        scope = expected_scope or self._scope
        if checkpoint.scope != scope:
            return IntegrityDecision(False, ("checkpoint scope mismatch",))
        if checkpoint.generation < trusted_min_generation:
            return IntegrityDecision(False, ("checkpoint below trusted minimum generation",))
        if not hmac.compare_digest(checkpoint.tag, self._sign(checkpoint.payload())):
            return IntegrityDecision(False, ("invalid checkpoint authentication",))
        if checkpoint.generation < 1:
            return IntegrityDecision(False, ("invalid checkpoint generation",))
        if previous is None:
            if checkpoint.previous_checkpoint_digest != "GENESIS" and checkpoint.generation == 1:
                return IntegrityDecision(False, ("invalid genesis predecessor",))
        else:
            if checkpoint.generation <= previous.generation:
                return IntegrityDecision(False, ("checkpoint generation did not advance",))
            if checkpoint.previous_checkpoint_digest != previous.checkpoint_digest():
                return IntegrityDecision(False, ("checkpoint predecessor mismatch",))
            if not hmac.compare_digest(previous.tag, self._sign(previous.payload())):
                return IntegrityDecision(False, ("invalid predecessor authentication",))
        try:
            current_digest = self.ledger_digest()
        except RuntimeError as exc:
            return IntegrityDecision(False, (str(exc),))
        if checkpoint.ledger_digest != current_digest:
            return IntegrityDecision(False, ("ledger digest mismatch",))
        return IntegrityDecision(True, ("checkpoint and current ledger match",))
