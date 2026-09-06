"""Pilot 18 minimum-side use-time validation for recovery signer issuance."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from exp_i_isolated_minimum_authority import MinimumAuthorityProcess
from exp_i_recovery_signer_crash_consistency import _paths, _validate_or_initialize_anchor


class CrashAwareMinimumAuthorityProcess:
    """Delegates minimum mutation only after committed issuance correspondence.

    This process owns no recovery-signing key.  It independently checks that the
    exact permit/signature exists in the durable issuance ledger and that the
    ledger corresponds to the independent authenticated anti-rollback anchor,
    then delegates cryptographic/use-time root-state validation to Pilot 16's
    minimum-authority process.
    """

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
            ok, reason = _validate_or_initialize_anchor(c, anchor_path, anchor_key_path)
            if not ok:
                return {"ok": False, "reason": reason}
            recovery_id = permit.get("recovery_id")
            row = c.execute(
                "SELECT permit_json,signature FROM issuance WHERE recovery_id=?",
                (recovery_id,),
            ).fetchone()
            if row is None:
                return {"ok": False, "reason": "ISSUANCE_NOT_COMMITTED"}
            try:
                committed_permit = json.loads(row[0])
            except Exception:
                return {"ok": False, "reason": "ISSUANCE_RECORD_CORRUPT"}
            if committed_permit != permit or str(row[1]) != signature:
                return {"ok": False, "reason": "ISSUANCE_CORRESPONDENCE_MISMATCH"}
        finally:
            c.close()
        return self.inner.advance({"permit": permit, "signature": signature})
