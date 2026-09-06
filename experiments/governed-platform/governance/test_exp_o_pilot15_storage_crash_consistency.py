from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from storage_crash_consistency_exp_o import CRASH_POINTS, StorageCrashPrototype, authority_payload, canonical, digest


EXPECTED_CRASH_POINTS = (
    "AFTER_AUTHORITY_RECORD_WRITE_BEFORE_FSYNC",
    "AFTER_AUTHORITY_RECORD_FSYNC_BEFORE_CHECKPOINT",
    "AFTER_CHECKPOINT_WRITE_BEFORE_FSYNC",
    "AFTER_EFFECT_COMMIT_BEFORE_EFFECT_EVIDENCE_WRITE",
    "AFTER_EFFECT_EVIDENCE_WRITE_BEFORE_FSYNC",
    "AFTER_EFFECT_EVIDENCE_FSYNC_BEFORE_AUTHORITY_CONSUMED",
    "AFTER_AUTHORITY_CONSUMED_WRITE_BEFORE_FSYNC",
    "AFTER_AUTHORITY_CONSUMED_FSYNC_BEFORE_CHECKPOINT",
    "AFTER_TAKEOVER_FENCE_WRITE_BEFORE_FSYNC",
    "AFTER_TAKEOVER_FENCE_FSYNC_BEFORE_CHECKPOINT",
)


class ExpOPilot15StorageCrashConsistencyTests(unittest.TestCase):
    def store(self) -> tuple[tempfile.TemporaryDirectory[str], StorageCrashPrototype]:
        td = tempfile.TemporaryDirectory()
        return td, StorageCrashPrototype(td.name)

    def durable_authority(self, s: StorageCrashPrototype, **kwargs):
        frame = s.append_record("AUTHORITY", authority_payload(**kwargs), durable=True)
        s.write_checkpoint(frame["seq"], frame["record_digest"], durable=True)
        return frame

    def restart(self, s: StorageCrashPrototype) -> StorageCrashPrototype:
        return StorageCrashPrototype(s.root)

    def test_p15_01_clean_durable_authority_control(self):
        self.assertEqual(CRASH_POINTS, EXPECTED_CRASH_POINTS)
        td, s = self.store()
        self.addCleanup(td.cleanup)
        frame = self.durable_authority(s)
        r = self.restart(s).recover()
        self.assertTrue(r["authorized"])
        self.assertEqual(r["recovery_status"], "AUTHORITATIVE")
        self.assertEqual(r["authority"], authority_payload())
        self.assertEqual(s.durable_checkpoint()["record_digest"], frame["record_digest"])

    def test_p15_02_authority_write_lost_before_fsync(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        s.append_record("AUTHORITY", authority_payload(), durable=False)
        s.simulate_power_loss()
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "NO_DURABLE_AUTHORITY")

    def test_p15_03_authority_fsynced_but_checkpoint_not_advanced(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        s.append_record("AUTHORITY", authority_payload(), durable=True)
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECONCILIATION_REQUIRED")

    def test_p15_04_torn_final_authority_frame(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        self.durable_authority(s)
        data = s.journal.read_bytes()
        s.journal.write_bytes(data[:-7])
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "TORN_FINAL_FRAME")

    def test_p15_05_checksum_valid_syntax_is_insufficient(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        self.durable_authority(s)
        frame = json.loads(s.journal.read_text().strip())
        frame["record_digest"] = "0" * 64
        s.journal.write_bytes(canonical(frame) + b"\n")
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "RECORD_DIGEST_MISMATCH")

    def test_p15_06_broken_digest_chain(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        first = self.durable_authority(s)
        second = s.append_record("NOTE", {"x": 1}, durable=True)
        lines = s.journal.read_text().splitlines()
        frame2 = json.loads(lines[1])
        frame2["prev_digest"] = "f" * 64
        core = {"seq": frame2["seq"], "record_type": frame2["record_type"], "payload": frame2["payload"], "prev_digest": frame2["prev_digest"]}
        frame2["record_digest"] = digest(core)
        s.journal.write_bytes((lines[0] + "\n").encode() + canonical(frame2) + b"\n")
        self.assertNotEqual(second["prev_digest"], frame2["prev_digest"])
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "PREVIOUS_DIGEST_MISMATCH")
        self.assertEqual(first["seq"], 1)

    def test_p15_07_checkpoint_beyond_validated_prefix(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        frame = s.append_record("AUTHORITY", authority_payload(), durable=True)
        s.write_checkpoint(frame["seq"] + 1, frame["record_digest"], durable=True)
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "CHECKPOINT_BEYOND_VALID_PREFIX")

    def test_p15_08_checkpoint_digest_mismatch(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        frame = s.append_record("AUTHORITY", authority_payload(), durable=True)
        s.write_checkpoint(frame["seq"], "a" * 64, durable=True)
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "CHECKPOINT_DIGEST_MISMATCH")

    def test_p15_09_duplicate_sequence_with_conflicting_content(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        first = s.append_record("AUTHORITY", authority_payload(), durable=True)
        conflict_core = {"seq": 1, "record_type": "AUTHORITY", "payload": authority_payload(owner="r2"), "prev_digest": "GENESIS"}
        conflict = dict(conflict_core); conflict["record_digest"] = digest(conflict_core)
        with open(s.journal, "ab") as f:
            f.write(canonical(conflict) + b"\n")
        s._atomic_json(s.durable_meta, {"durable_seq": 2})
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "SEQUENCE_CONFLICT")
        self.assertNotEqual(first["record_digest"], conflict["record_digest"])

    def test_p15_10_stale_snapshot_substitution_after_durable_fence(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        old = self.durable_authority(s, term=1, index=1, owner="r1", epoch=1)
        high = s.append_record("TAKEOVER_FENCE", authority_payload(term=2, index=2, owner="r2", epoch=2), durable=True)
        s.anchor_fence(term=2, index=2, lease_epoch=2, record_digest=high["record_digest"])
        # Substitute a lower valid-looking journal/checkpoint pair while retaining the independent anchor.
        s.journal.write_bytes(canonical(old) + b"\n")
        s._atomic_json(s.durable_meta, {"durable_seq": 1})
        s._atomic_json(s.checkpoint_durable, {"seq": 1, "record_digest": old["record_digest"]})
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "STALE_ROLLBACK_BLOCKED")

    def test_p15_11_takeover_fence_write_lost_before_fsync(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        old = self.durable_authority(s)
        s.append_record("TAKEOVER_FENCE", authority_payload(term=2, index=2, owner="r2", epoch=2), durable=False)
        s.simulate_power_loss()
        r = self.restart(s).recover()
        self.assertTrue(r["authorized"])
        self.assertEqual(r["authority"]["lease_owner"], "r1")
        self.assertEqual(r["authority"]["lease_epoch"], 1)
        self.assertEqual(old["seq"], 1)

    def test_p15_12_durable_takeover_fence_before_checkpoint(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        self.durable_authority(s)
        high = s.append_record("TAKEOVER_FENCE", authority_payload(term=2, index=2, owner="r2", epoch=2), durable=True)
        s.anchor_fence(term=2, index=2, lease_epoch=2, record_digest=high["record_digest"])
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECONCILIATION_REQUIRED")
        self.assertNotEqual(r.get("authority", {}).get("lease_owner"), "r1")

    def test_p15_13_effect_commits_before_evidence_write(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        self.durable_authority(s)
        first = s.effect_apply("intent-1", "effect-A")
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECONCILIATION_REQUIRED")
        replay = s.effect_apply("intent-1", "effect-A")
        self.assertFalse(replay["executed"])
        self.assertEqual(replay["result_id"], first["result_id"])
        self.assertEqual(s.effect_count(), 1)

    def test_p15_14_effect_evidence_written_but_not_durable(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        self.durable_authority(s)
        first = s.effect_apply("intent-1", "effect-A")
        s.append_record("EFFECT_EVIDENCE", {"idempotency_key": "intent-1", "effect_digest": "effect-A", "result_id": first["result_id"]}, durable=False)
        s.simulate_power_loss()
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(s.effect_count(), 1)
        self.assertFalse(s.effect_apply("intent-1", "effect-A")["executed"])

    def test_p15_15_durable_effect_evidence_before_consumed_authority(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        self.durable_authority(s)
        first = s.effect_apply("intent-1", "effect-A")
        s.append_record("EFFECT_EVIDENCE", {"idempotency_key": "intent-1", "effect_digest": "effect-A", "result_id": first["result_id"]}, durable=True)
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECONCILIATION_REQUIRED")
        replay = s.effect_apply("intent-1", "effect-A")
        self.assertFalse(replay["executed"])
        self.assertEqual(replay["result_id"], first["result_id"])

    def test_p15_16_consumed_record_written_but_not_durable(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        self.durable_authority(s)
        first = s.effect_apply("intent-1", "effect-A")
        ev = s.append_record("EFFECT_EVIDENCE", {"idempotency_key": "intent-1", "effect_digest": "effect-A", "result_id": first["result_id"]}, durable=True)
        s.write_checkpoint(ev["seq"], ev["record_digest"], durable=True)
        s.append_record("AUTHORITY_CONSUMED", {"idempotency_key": "intent-1", "result_id": first["result_id"]}, durable=False)
        s.simulate_power_loss()
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECOVERED_EFFECT")
        self.assertFalse(s.effect_apply("intent-1", "effect-A")["executed"])

    def test_p15_17_consumed_record_durable_before_checkpoint(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        self.durable_authority(s)
        first = s.effect_apply("intent-1", "effect-A")
        ev = s.append_record("EFFECT_EVIDENCE", {"idempotency_key": "intent-1", "effect_digest": "effect-A", "result_id": first["result_id"]}, durable=True)
        s.write_checkpoint(ev["seq"], ev["record_digest"], durable=True)
        s.append_record("AUTHORITY_CONSUMED", {"idempotency_key": "intent-1", "result_id": first["result_id"]}, durable=True)
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECONCILIATION_REQUIRED")
        self.assertEqual(s.effect_count(), 1)

    def test_p15_18_effect_ledger_idempotency_rebinding_corruption(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        self.durable_authority(s)
        first = s.effect_apply("intent-1", "effect-A")
        ledger = json.loads(s.effect_ledger.read_text())
        ledger["effects"]["intent-1"]["effect_digest"] = "effect-B"
        s._atomic_json(s.effect_ledger, ledger)
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EFFECT_LEDGER_REBINDING_CORRUPTION")
        self.assertEqual(s.effect_count(), 1)
        self.assertTrue(first["executed"])

    def test_p15_19_consumed_record_references_missing_effect_identity(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        auth = s.append_record("AUTHORITY", authority_payload(), durable=True)
        consumed = s.append_record("AUTHORITY_CONSUMED", {"idempotency_key": "intent-1", "result_id": "missing-result"}, durable=True)
        s.write_checkpoint(consumed["seq"], consumed["record_digest"], durable=True)
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "CONSUMED_EFFECT_IDENTITY_MISSING")
        self.assertEqual(r["recovery_status"], "RECONCILIATION_REQUIRED")
        self.assertEqual(auth["seq"], 1)

    def test_p15_20_clean_restart_after_all_fault_cases(self):
        td, s = self.store(); self.addCleanup(td.cleanup)
        self.durable_authority(s, key="fresh-intent", effect="fresh-effect", semantic="fresh-semantic")
        first = s.effect_apply("fresh-intent", "fresh-effect")
        ev = s.append_record("EFFECT_EVIDENCE", {"idempotency_key": "fresh-intent", "effect_digest": "fresh-effect", "result_id": first["result_id"]}, durable=True)
        consumed = s.append_record("AUTHORITY_CONSUMED", {"idempotency_key": "fresh-intent", "result_id": first["result_id"]}, durable=True)
        s.write_checkpoint(consumed["seq"], consumed["record_digest"], durable=True)
        r = self.restart(s).recover()
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECOVERED_CONSUMED")
        self.assertEqual(r["original_result_id"], first["result_id"])
        replay = self.restart(s).effect_apply("fresh-intent", "fresh-effect")
        self.assertFalse(replay["executed"])
        self.assertEqual(replay["result_id"], first["result_id"])
        self.assertEqual(s.effect_count(), 1)
        self.assertEqual(ev["seq"], 2)


if __name__ == "__main__":
    unittest.main()
