from __future__ import annotations

import json
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import unittest

from sqlite_parent_sigkill_exp_o import READY_POINTS
from sqlite_process_crash_exp_o import authority_payload, connect, init_db, recover, write_anchor

SCRIPT = Path(__file__).with_name("sqlite_parent_sigkill_exp_o.py")
EXPECTED_READY_POINTS = (
    "READY_AFTER_BEGIN_BEFORE_AUTHORITY_INSERT",
    "READY_AFTER_AUTHORITY_INSERT_BEFORE_COMMIT",
    "READY_AFTER_AUTHORITY_COMMIT_BEFORE_ACK",
    "READY_AFTER_TAKEOVER_INSERT_BEFORE_COMMIT",
    "READY_AFTER_TAKEOVER_COMMIT_BEFORE_ACK",
    "READY_AFTER_EFFECT_INSERT_BEFORE_COMMIT",
    "READY_AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE",
    "READY_AFTER_CONSUMED_UPDATE_BEFORE_COMMIT",
)


class ExpOPilot17ParentSigkillSQLiteTests(unittest.TestCase):
    def env(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        db = root / "authority.db"
        init_db(db)
        return td, root, db

    def run_clean(self, db: Path, op: str, payload=None):
        cp = subprocess.run(
            [sys.executable, str(SCRIPT), "--db", str(db), "--op", op, "--payload", json.dumps(payload or {})],
            capture_output=True, text=True, timeout=10,
        )
        result = json.loads(cp.stdout.strip().splitlines()[-1]) if cp.stdout.strip() else None
        return cp, result

    def kill_at_ready(self, db: Path, op: str, payload, ready_point: str):
        p = subprocess.Popen(
            [sys.executable, str(SCRIPT), "--db", str(db), "--op", op,
             "--payload", json.dumps(payload or {}), "--ready-point", ready_point],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        assert p.stdout is not None
        line = p.stdout.readline().strip()
        self.assertTrue(line, "worker did not emit readiness marker")
        marker = json.loads(line)
        self.assertEqual(marker["ready"], ready_point)
        self.assertEqual(marker["pid"], p.pid)
        self.assertFalse(marker["self_termination"])
        self.assertIsNone(p.poll(), "worker must still be alive and blocked before parent kill")
        p.kill()
        stdout_tail, stderr = p.communicate(timeout=10)
        self.assertEqual(p.returncode, -signal.SIGKILL, f"stdout={stdout_tail!r} stderr={stderr!r}")
        return marker, p.returncode

    def commit_authority(self, db: Path, **kwargs):
        cp, r = self.run_clean(db, "authority", authority_payload(**kwargs))
        self.assertEqual(cp.returncode, 0, cp.stderr)
        self.assertTrue(r["authorized"])
        return r

    def commit_effect(self, db: Path, key="intent-1", effect="effect-A", semantic="semantic-A"):
        cp, r = self.run_clean(db, "effect", {"idempotency_key": key, "effect_digest": effect, "semantic_digest": semantic})
        self.assertEqual(cp.returncode, 0, cp.stderr)
        return r

    def test_p17_01_readiness_protocol_proves_distinct_externally_killed_worker(self):
        self.assertEqual(READY_POINTS, EXPECTED_READY_POINTS)
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        marker, rc = self.kill_at_ready(db, "authority", authority_payload(), "READY_AFTER_BEGIN_BEFORE_AUTHORITY_INSERT")
        self.assertGreater(marker["pid"], 1)
        self.assertEqual(rc, -signal.SIGKILL)
        self.assertFalse(recover(db)["authorized"])

    def test_p17_02_parent_kill_after_begin_before_authority_insert(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.kill_at_ready(db, "authority", authority_payload(), "READY_AFTER_BEGIN_BEFORE_AUTHORITY_INSERT")
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "NO_ACTIVE_AUTHORITY")

    def test_p17_03_parent_kill_after_authority_insert_before_commit(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.kill_at_ready(db, "authority", authority_payload(), "READY_AFTER_AUTHORITY_INSERT_BEFORE_COMMIT")
        r = recover(db)
        self.assertFalse(r["authorized"])
        with connect(db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM authority").fetchone()[0], 0)

    def test_p17_04_parent_kill_after_authority_commit_before_ack(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.kill_at_ready(db, "authority", authority_payload(), "READY_AFTER_AUTHORITY_COMMIT_BEFORE_ACK")
        r = recover(db)
        self.assertTrue(r["authorized"])
        self.assertEqual((r["authority"]["owner"], r["authority"]["lease_epoch"]), ("r1", 1))

    def test_p17_05_parent_kill_after_takeover_insert_before_commit(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        self.kill_at_ready(db, "takeover", authority_payload(term=2, commit_index=2, owner="r2", lease_epoch=2), "READY_AFTER_TAKEOVER_INSERT_BEFORE_COMMIT")
        r = recover(db)
        self.assertTrue(r["authorized"])
        self.assertEqual((r["authority"]["term"], r["authority"]["owner"]), (1, "r1"))

    def test_p17_06_parent_kill_after_takeover_commit_before_ack(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        self.kill_at_ready(db, "takeover", authority_payload(term=2, commit_index=2, owner="r2", lease_epoch=2), "READY_AFTER_TAKEOVER_COMMIT_BEFORE_ACK")
        r = recover(db)
        self.assertTrue(r["authorized"])
        self.assertEqual((r["authority"]["term"], r["authority"]["owner"], r["authority"]["lease_epoch"]), (2, "r2", 2))

    def test_p17_07_stale_lower_authority_after_killed_committed_takeover_is_denied(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        self.kill_at_ready(db, "takeover", authority_payload(term=2, commit_index=2, owner="r2", lease_epoch=2), "READY_AFTER_TAKEOVER_COMMIT_BEFORE_ACK")
        cp, low = self.run_clean(db, "authority", authority_payload())
        self.assertEqual(cp.returncode, 0)
        self.assertFalse(low["authorized"])
        self.assertEqual(recover(db)["authority"]["owner"], "r2")

    def test_p17_08_stale_database_substitution_below_independent_anchor(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        self.kill_at_ready(db, "takeover", authority_payload(term=2, commit_index=2, owner="r2", lease_epoch=2), "READY_AFTER_TAKEOVER_COMMIT_BEFORE_ACK")
        anchor = root / "anchor.json"
        write_anchor(anchor, term=2, commit_index=2, lease_epoch=2)
        stale = root / "stale.db"; init_db(stale)
        cp, _ = self.run_clean(stale, "authority", authority_payload())
        self.assertEqual(cp.returncode, 0)
        with connect(stale) as conn:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        for suffix in ("-wal", "-shm"):
            p = Path(str(db) + suffix)
            if p.exists(): p.unlink()
        shutil.copy2(stale, db)
        r = recover(db, anchor)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "STALE_ROLLBACK_BLOCKED")

    def test_p17_09_parent_kill_after_effect_insert_before_commit(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        payload = {"idempotency_key":"intent-1","effect_digest":"effect-A","semantic_digest":"semantic-A"}
        self.kill_at_ready(db, "effect", payload, "READY_AFTER_EFFECT_INSERT_BEFORE_COMMIT")
        self.assertTrue(recover(db)["authorized"])
        first = self.commit_effect(db)
        self.assertTrue(first["executed"])
        with connect(db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0], 1)

    def test_p17_10_parent_kill_after_effect_commit_before_evidence_update(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        payload = {"idempotency_key":"intent-1","effect_digest":"effect-A","semantic_digest":"semantic-A"}
        self.kill_at_ready(db, "effect", payload, "READY_AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE")
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECOVERED_EFFECT")
        replay = self.commit_effect(db)
        self.assertFalse(replay["executed"])
        self.assertEqual(replay["result_id"], r["result_id"])

    def test_p17_11_repeated_retry_after_posteffect_kill_is_same_result(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        payload = {"idempotency_key":"intent-1","effect_digest":"effect-A","semantic_digest":"semantic-A"}
        self.kill_at_ready(db, "effect", payload, "READY_AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE")
        ids = []
        for _ in range(4):
            r = self.commit_effect(db)
            self.assertFalse(r["executed"])
            ids.append(r["result_id"])
        self.assertEqual(len(set(ids)), 1)
        with connect(db) as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0], 1)

    def test_p17_12_idempotency_rebinding_after_posteffect_kill_is_denied(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        payload = {"idempotency_key":"intent-1","effect_digest":"effect-A","semantic_digest":"semantic-A"}
        self.kill_at_ready(db, "effect", payload, "READY_AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE")
        cp, r = self.run_clean(db, "effect", {"idempotency_key":"intent-1","effect_digest":"effect-B","semantic_digest":"semantic-A"})
        self.assertEqual(cp.returncode, 0)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "IDEMPOTENCY_EFFECT_REBINDING_DENIED")

    def test_p17_13_parent_kill_after_consumed_update_before_commit(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db); first = self.commit_effect(db)
        self.kill_at_ready(db, "consume", {"idempotency_key":"intent-1"}, "READY_AFTER_CONSUMED_UPDATE_BEFORE_COMMIT")
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["recovery_status"], "RECOVERED_EFFECT")
        replay = self.commit_effect(db)
        self.assertFalse(replay["executed"])
        self.assertEqual(replay["result_id"], first["result_id"])

    def test_p17_14_malformed_active_authority_after_restart_fails_closed(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        with connect(db) as conn:
            conn.execute("UPDATE authority SET effect_digest=NULL WHERE status='ACTIVE'")
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "AUTHORITY_BINDING_INCOMPLETE")

    def test_p17_15_duplicate_active_authority_ambiguity_fails_closed(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        with connect(db) as conn:
            conn.execute("INSERT INTO authority(logical_id,term,commit_index,owner,lease_epoch,semantic_digest,effect_digest,idempotency_key,status,result_id) VALUES('auth-1',2,2,'r2',2,'semantic-A','effect-A','intent-1','ACTIVE',NULL)")
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "DUPLICATE_ACTIVE_AUTHORITY")

    def test_p17_16_consumed_state_missing_effect_identity_fails_closed(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db); self.commit_effect(db)
        cp, consumed = self.run_clean(db, "consume", {"idempotency_key":"intent-1"})
        self.assertEqual(cp.returncode, 0)
        with connect(db) as conn:
            conn.execute("DELETE FROM effects WHERE idempotency_key='intent-1'")
        r = recover(db)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "CONSUMED_EFFECT_IDENTITY_MISSING")

    def test_p17_17_repeated_fresh_reopen_after_parent_kill_is_stable(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db)
        payload = {"idempotency_key":"intent-1","effect_digest":"effect-A","semantic_digest":"semantic-A"}
        self.kill_at_ready(db, "effect", payload, "READY_AFTER_EFFECT_COMMIT_BEFORE_EVIDENCE_UPDATE")
        ids = []
        for _ in range(5):
            r = recover(db)
            self.assertFalse(r["authorized"])
            ids.append(r["result_id"])
        self.assertEqual(len(set(ids)), 1)

    def test_p17_18_clean_positive_liveness_control(self):
        td, root, db = self.env(); self.addCleanup(td.cleanup)
        self.commit_authority(db, logical_id="fresh", idempotency_key="fresh-intent", effect_digest="fresh-effect", semantic_digest="fresh-semantic")
        first = self.commit_effect(db, key="fresh-intent", effect="fresh-effect", semantic="fresh-semantic")
        self.assertTrue(first["executed"])
        cp, consumed = self.run_clean(db, "consume", {"idempotency_key":"fresh-intent"})
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
