from __future__ import annotations

import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from sqlite_process_crash_exp_o import EXIT_KILLED, KILL_POINTS, authority_payload, connect, init_db, recover, write_anchor

SCRIPT = Path(__file__).with_name("sqlite_process_crash_exp_o.py")
EXPECTED_KILL_POINTS = (
    "AFTER_BEGIN_BEFORE_AUTHORITY_INSERT",
    "AFTER_AUTHORITY_INSERT_BEFORE_COMMIT",
    "AFTER_AUTHORITY_COMMIT_BEFORE_ACK",
    "AFTER_TAKEOVER_INSERT_BEFORE_COMMIT",
    "AFTER_TAKEOVER_COMMIT_BEFORE_ACK",
    "AFTER_EFFECT_INSERT_BEFORE_COMMIT",
    "AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE",
    "AFTER_EVIDENCE_UPDATE_BEFORE_COMMIT",
    "AFTER_CONSUMED_UPDATE_BEFORE_COMMIT",
    "AFTER_CONSUMED_COMMIT_BEFORE_ACK",
)


class ExpOPilot16SQLiteProcessCrashTests(unittest.TestCase):
    def env(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        db = root / "authority.db"
        init_db(db)
        return td, root, db

    def run_worker(self, db: Path, op: str, payload=None, kill_point=None, anchor=None):
        cmd = [sys.executable, str(SCRIPT), "--db", str(db), "--op", op, "--payload", json.dumps(payload or {})]
        if kill_point:
            cmd += ["--kill-point", kill_point]
        if anchor:
            cmd += ["--anchor", str(anchor)]
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        result = None
        if cp.stdout.strip():
            result = json.loads(cp.stdout.strip().splitlines()[-1])
        return cp, result

    def commit_authority(self, db: Path, **kwargs):
        cp, r = self.run_worker(db, "authority", authority_payload(**kwargs))
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertTrue(r["authorized"])
        return r

    def commit_effect(self, db: Path, *, key="intent-1", effect="effect-A", semantic="semantic-A"):
        cp, r = self.run_worker(db, "effect", {"idempotency_key": key, "effect_digest": effect, "semantic_digest": semantic})
        self.assertEqual(cp.returncode, 0, cp.stderr)
        return r

    def test_p16_01_clean_committed_authority_survives_fresh_reopen(self):
        self.assertEqual(KILL_POINTS, EXPECTED_KILL_POINTS)
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        r = recover(db)
        self.assertTrue(r["authorized"])
        self.assertEqual(r["authority"]["owner"], "r1")
        self.assertEqual(r["authority"]["lease_epoch"], 1)

    def test_p16_02_kill_after_begin_before_authority_insert(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        cp, _ = self.run_worker(db, "authority", authority_payload(), "AFTER_BEGIN_BEFORE_AUTHORITY_INSERT")
        self.assertEqual(cp.returncode, EXIT_KILLED)
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "NO_ACTIVE_AUTHORITY")

    def test_p16_03_kill_after_authority_insert_before_commit(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        cp, _ = self.run_worker(db, "authority", authority_payload(), "AFTER_AUTHORITY_INSERT_BEFORE_COMMIT")
        self.assertEqual(cp.returncode, EXIT_KILLED)
        r = recover(db)
        self.assertFalse(r["authorized"])
        with connect(db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM authority").fetchone()[0], 0)

    def test_p16_04_kill_after_authority_commit_before_ack(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        cp, _ = self.run_worker(db, "authority", authority_payload(), "AFTER_AUTHORITY_COMMIT_BEFORE_ACK")
        self.assertEqual(cp.returncode, EXIT_KILLED)
        r = recover(db)
        self.assertTrue(r["authorized"])
        self.assertEqual(r["authority"]["idempotency_key"], "intent-1")

    def test_p16_05_stale_lower_authority_cannot_overwrite_committed_higher_fence(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        cp, high = self.run_worker(db, "takeover", authority_payload(term=2, commit_index=2, owner="r2", lease_epoch=2))
        self.assertEqual(cp.returncode, 0); self.assertTrue(high["authorized"])
        cp, low = self.run_worker(db, "authority", authority_payload(term=1, commit_index=1, owner="r1", lease_epoch=1))
        self.assertEqual(cp.returncode, 0); self.assertFalse(low["authorized"])
        r = recover(db)
        self.assertEqual(r["authority"]["owner"], "r2")
        self.assertEqual(r["authority"]["lease_epoch"], 2)

    def test_p16_06_kill_after_takeover_insert_before_commit(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        cp, _ = self.run_worker(db, "takeover", authority_payload(term=2, commit_index=2, owner="r2", lease_epoch=2), "AFTER_TAKEOVER_INSERT_BEFORE_COMMIT")
        self.assertEqual(cp.returncode, EXIT_KILLED)
        r = recover(db)
        self.assertTrue(r["authorized"])
        self.assertEqual(r["authority"]["owner"], "r1")

    def test_p16_07_kill_after_takeover_commit_before_ack(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        cp, _ = self.run_worker(db, "takeover", authority_payload(term=2, commit_index=2, owner="r2", lease_epoch=2), "AFTER_TAKEOVER_COMMIT_BEFORE_ACK")
        self.assertEqual(cp.returncode, EXIT_KILLED)
        r = recover(db)
        self.assertTrue(r["authorized"])
        self.assertEqual((r["authority"]["term"], r["authority"]["owner"], r["authority"]["lease_epoch"]), (2, "r2", 2))

    def test_p16_08_stale_database_substitution_after_independently_anchored_higher_fence(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        self.run_worker(db, "takeover", authority_payload(term=2, commit_index=2, owner="r2", lease_epoch=2))
        anchor = root / "anchor.json"
        write_anchor(anchor, term=2, commit_index=2, lease_epoch=2)
        stale = root / "stale.db"; init_db(stale)
        self.run_worker(stale, "authority", authority_payload())
        for suffix in ("-wal", "-shm"):
            p = Path(str(db) + suffix)
            if p.exists(): p.unlink()
        shutil.copy2(stale, db)
        r = recover(db, anchor)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "STALE_ROLLBACK_BLOCKED")

    def test_p16_09_authority_row_binding_corruption(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        with connect(db) as conn:
            conn.execute("UPDATE authority SET semantic_digest=NULL WHERE status='ACTIVE'")
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "AUTHORITY_BINDING_INCOMPLETE")

    def test_p16_10_duplicate_active_authority_rows_same_logical_identity(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        with connect(db) as conn:
            conn.execute("INSERT INTO authority(logical_id,term,commit_index,owner,lease_epoch,semantic_digest,effect_digest,idempotency_key,status,result_id) VALUES('auth-1',2,2,'r2',2,'semantic-A','effect-A','intent-1','ACTIVE',NULL)")
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "DUPLICATE_ACTIVE_AUTHORITY")

    def test_p16_11_kill_after_effect_insert_before_commit(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        cp, _ = self.run_worker(db, "effect", {"idempotency_key":"intent-1","effect_digest":"effect-A","semantic_digest":"semantic-A"}, "AFTER_EFFECT_INSERT_BEFORE_COMMIT")
        self.assertEqual(cp.returncode, EXIT_KILLED)
        r = recover(db)
        self.assertTrue(r["authorized"])
        first = self.commit_effect(db)
        self.assertTrue(first["executed"])
        with connect(db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0], 1)

    def test_p16_12_kill_after_effect_commit_before_evidence_update(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        cp, _ = self.run_worker(db, "effect", {"idempotency_key":"intent-1","effect_digest":"effect-A","semantic_digest":"semantic-A"}, "AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE")
        self.assertEqual(cp.returncode, EXIT_KILLED)
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECOVERED_EFFECT")
        replay = self.commit_effect(db)
        self.assertFalse(replay["executed"])
        self.assertEqual(replay["result_id"], r["result_id"])

    def test_p16_13_kill_after_evidence_update_before_commit(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        cp, _ = self.run_worker(db, "effect", {"idempotency_key":"intent-1","effect_digest":"effect-A","semantic_digest":"semantic-A"}, "AFTER_EVIDENCE_UPDATE_BEFORE_COMMIT")
        self.assertEqual(cp.returncode, EXIT_KILLED)
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECOVERED_EFFECT")
        with connect(db) as conn:
            row = conn.execute("SELECT result_id FROM authority WHERE status='ACTIVE'").fetchone()
            self.assertIsNone(row["result_id"])

    def test_p16_14_durable_effect_row_dominates_stale_active_authority(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        first = self.commit_effect(db)
        self.assertTrue(first["executed"])
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["decision"], "RECONCILED")
        again = self.commit_effect(db)
        self.assertFalse(again["executed"])
        self.assertEqual(again["result_id"], first["result_id"])

    def test_p16_15_kill_after_consumed_update_before_commit(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db); first = self.commit_effect(db)
        cp, _ = self.run_worker(db, "consume", {"idempotency_key":"intent-1"}, "AFTER_CONSUMED_UPDATE_BEFORE_COMMIT")
        self.assertEqual(cp.returncode, EXIT_KILLED)
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECOVERED_EFFECT")
        replay = self.commit_effect(db)
        self.assertFalse(replay["executed"]); self.assertEqual(replay["result_id"], first["result_id"])

    def test_p16_16_kill_after_consumed_commit_before_ack(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db); first = self.commit_effect(db)
        cp, _ = self.run_worker(db, "consume", {"idempotency_key":"intent-1"}, "AFTER_CONSUMED_COMMIT_BEFORE_ACK")
        self.assertEqual(cp.returncode, EXIT_KILLED)
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECOVERED_CONSUMED")
        self.assertEqual(r["result_id"], first["result_id"])

    def test_p16_17_idempotency_key_rebinding_after_restart(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db); self.commit_effect(db)
        cp, r = self.run_worker(db, "effect", {"idempotency_key":"intent-1","effect_digest":"effect-B","semantic_digest":"semantic-A"})
        self.assertEqual(cp.returncode, 0)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "IDEMPOTENCY_EFFECT_REBINDING_DENIED")

    def test_p16_18_missing_effect_row_referenced_by_consumed_state(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db); self.commit_effect(db)
        self.run_worker(db, "consume", {"idempotency_key":"intent-1"})
        with connect(db) as conn:
            conn.execute("DELETE FROM effects WHERE idempotency_key='intent-1'")
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "CONSUMED_EFFECT_IDENTITY_MISSING")

    def test_p16_19_wal_reopen_repeated_clean_replay(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db); first = self.commit_effect(db)
        ids = []
        for _ in range(4):
            r = recover(db)
            self.assertFalse(r["authorized"])
            ids.append(r["result_id"])
        self.assertEqual(set(ids), {first["result_id"]})
        with connect(db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0], 1)

    def test_p16_20_fresh_clean_authority_effect_after_prior_isolated_crash_cases(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db, logical_id="fresh", idempotency_key="fresh-intent", effect_digest="fresh-effect", semantic_digest="fresh-semantic")
        first = self.commit_effect(db, key="fresh-intent", effect="fresh-effect", semantic="fresh-semantic")
        cp, consumed = self.run_worker(db, "consume", {"idempotency_key":"fresh-intent"})
        self.assertEqual(cp.returncode, 0)
        self.assertEqual(consumed["result_id"], first["result_id"])
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECOVERED_CONSUMED")
        replay = self.commit_effect(db, key="fresh-intent", effect="fresh-effect", semantic="fresh-semantic")
        self.assertFalse(replay["executed"])
        self.assertEqual(replay["result_id"], first["result_id"])


if __name__ == "__main__":
    unittest.main()
