from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOVERNANCE = HERE / "governance"
if str(GOVERNANCE) not in sys.path:
    sys.path.insert(0, str(GOVERNANCE))

import test_slice5_authoritative_state_ledger as v1tests  # noqa: E402
from authoritative_state_ledger_v2 import AuthoritativeStateLedger  # noqa: E402


class Slice5AuthoritativeStateLedgerV2Tests(v1tests.Slice5AuthoritativeStateLedgerTests):
    def setUp(self) -> None:
        super().setUp()
        self.ledger = AuthoritativeStateLedger(self.db)

    def _seed_project(self, project_id: str, key: str, value: str) -> None:
        self.ledger.apply_command(
            project_id=project_id,
            idempotency_key=key,
            command_type="PATCH_STATE",
            payload={"set": {"status": value}},
            expected_version=0,
            effect_type="NOTIFY",
            effect_payload={"status": value},
        )

    def test_s5_16_audit_detects_tampered_or_missing_lineage(self):
        projects = {
            "payload": "audit-payload",
            "state": "audit-state",
            "effect": "audit-effect",
            "missing": "audit-missing",
        }
        for name, project in projects.items():
            self._seed_project(project, f"intent-{name}", "ready")
            clean = self.ledger.audit(project)
            self.assertTrue(clean["valid"], clean)
            self.assertEqual(clean["event_count"], 1)
            self.assertEqual(clean["final_version"], 1)

        con = sqlite3.connect(self.db)
        try:
            con.execute(
                "UPDATE accepted_events SET payload_json=? WHERE project_id=?",
                (json.dumps({"set": {"status": "tampered"}}), projects["payload"]),
            )
            con.execute(
                "UPDATE project_state SET state_json=? WHERE project_id=?",
                (json.dumps({"status": "tampered"}), projects["state"]),
            )
            con.execute(
                "UPDATE outbox SET effect_payload_json=? WHERE project_id=?",
                (json.dumps({"status": "tampered"}), projects["effect"]),
            )
            con.execute(
                "DELETE FROM accepted_events WHERE project_id=?",
                (projects["missing"],),
            )
            con.commit()
        finally:
            con.close()

        payload_audit = self.ledger.audit(projects["payload"])
        self.assertFalse(payload_audit["valid"], payload_audit)
        self.assertTrue(
            any(p.startswith("command_digest:") or p.startswith("result_state_replay:") for p in payload_audit["problems"]),
            payload_audit,
        )

        state_audit = self.ledger.audit(projects["state"])
        self.assertFalse(state_audit["valid"], state_audit)
        self.assertTrue(
            "current_state_digest" in state_audit["problems"] or "current_state_lineage" in state_audit["problems"],
            state_audit,
        )

        effect_audit = self.ledger.audit(projects["effect"])
        self.assertFalse(effect_audit["valid"], effect_audit)
        self.assertTrue(
            any(p.startswith("effect_digest:") or p.startswith("command_digest:") for p in effect_audit["problems"]),
            effect_audit,
        )

        missing_audit = self.ledger.audit(projects["missing"])
        self.assertFalse(missing_audit["valid"], missing_audit)
        self.assertTrue(
            "state_without_events" in missing_audit["problems"] or any(p.startswith("orphan_outbox:") for p in missing_audit["problems"]),
            missing_audit,
        )


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)
