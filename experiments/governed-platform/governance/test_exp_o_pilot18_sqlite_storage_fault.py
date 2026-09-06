from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from sqlite_storage_fault_exp_o import (
    authority_payload,
    checkpoint,
    connect,
    copy_database,
    corrupt_effect_digest,
    corrupt_meta_below_rows,
    create_duplicate_active,
    create_live_wal_snapshot,
    database_full_authority,
    database_full_effect,
    database_full_takeover,
    delete_effect_rows,
    mutate_main_byte,
    mutate_wal_byte,
    recover_strict,
    remove_wal,
    truncate_main,
    truncate_wal,
    worker_authority,
    worker_consume,
    worker_effect,
    worker_takeover,
    write_anchor,
)
from sqlite_storage_seal_exp_o import init_sealed_db, recover_sealed, seal_state


class ExpOPilot18SQLiteStorageFaultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)

    def tearDown(self) -> None:
        self.td.cleanup()

    def db(self, name: str = "case.db") -> Path:
        return self.root / name

    def p(self, *, term: int = 1, index: int = 1, epoch: int = 1, owner: str = "r1", key: str = "intent-1", effect: str = "effect-A", semantic: str = "semantic-A"):
        return authority_payload(logical_id="auth-1", term=term, commit_index=index, owner=owner, lease_epoch=epoch,
                                 semantic_digest=semantic, effect_digest=effect, idempotency_key=key)

    def prepare_active(self, path: Path, payload=None) -> dict:
        init_sealed_db(path)
        payload = payload or self.p()
        result = worker_authority(str(path), payload, None)
        self.assertTrue(result["authorized"])
        seal_state(path)
        return payload

    def prepare_effect(self, path: Path, payload=None, *, consume: bool = False) -> dict:
        payload = self.prepare_active(path, payload)
        result = worker_effect(str(path), payload, None)
        self.assertTrue(result["executed"])
        if consume:
            c = worker_consume(str(path), payload, None)
            self.assertEqual(c["decision"], "CONSUMED")
        seal_state(path)
        return payload

    def assert_denied_not_empty(self, result: dict) -> None:
        self.assertFalse(result.get("authorized", False), result)
        self.assertNotEqual(result.get("reason"), "NO_ACTIVE_AUTHORITY", result)
        self.assertNotEqual(result.get("recovery_status"), "EMPTY", result)

    # P18-01
    def test_p18_01_clean_database_control(self):
        path = self.db()
        p = self.prepare_active(path)
        r = recover_sealed(path)
        self.assertTrue(r["authorized"])
        self.assertTrue(r["storage_integrity"])
        self.assertTrue(r["seal_integrity"])
        self.assertEqual(r["authority"]["semantic_digest"], p["semantic_digest"])
        self.assertEqual(r["authority"]["effect_digest"], p["effect_digest"])
        self.assertEqual(r["authority"]["idempotency_key"], p["idempotency_key"])

    # P18-02
    def test_p18_02_database_full_during_authority_write(self):
        path = self.db()
        init_sealed_db(path); seal_state(path)
        fault = database_full_authority(path, self.p())
        self.assertTrue(fault["fault_observed"])
        self.assertTrue(fault["rolled_back"])
        self.assertIn("full", fault["sqlite_error"].lower())
        r = recover_sealed(path)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "NO_ACTIVE_AUTHORITY")
        self.assertEqual(r["recovery_status"], "EMPTY")

    # P18-03
    def test_p18_03_database_full_during_higher_takeover(self):
        path = self.db()
        self.prepare_active(path, self.p(term=1, index=1, epoch=1, owner="old"))
        fault = database_full_takeover(path, self.p(term=2, index=2, epoch=2, owner="new"))
        self.assertTrue(fault["fault_observed"])
        self.assertTrue(fault["rolled_back"])
        r = recover_sealed(path)
        self.assertTrue(r["authorized"])
        self.assertEqual(r["authority"]["term"], 1)
        self.assertEqual(r["authority"]["owner"], "old")

    # P18-04
    def test_p18_04_database_full_during_effect_insert(self):
        path = self.db()
        p = self.prepare_active(path)
        fault = database_full_effect(path, p)
        self.assertTrue(fault["fault_observed"])
        self.assertTrue(fault["rolled_back"])
        before_retry = recover_sealed(path)
        self.assertTrue(before_retry["authorized"])
        retry = worker_effect(str(path), p, None)
        self.assertTrue(retry["executed"])
        seal_state(path)
        again = worker_effect(str(path), p, None)
        self.assertFalse(again["executed"])
        self.assertEqual(again["decision"], "RECONCILED")

    # P18-05
    def test_p18_05_main_database_header_page_corruption(self):
        path = self.db(); self.prepare_active(path); checkpoint(path)
        fault = mutate_main_byte(path, offset=0)
        self.assertTrue(fault["fault_observed"])
        r = recover_sealed(path)
        self.assert_denied_not_empty(r)
        self.assertFalse(r["storage_integrity"])

    # P18-06
    def test_p18_06_main_database_truncation(self):
        path = self.db(); self.prepare_active(path); checkpoint(path)
        size = path.stat().st_size
        fault = truncate_main(path, keep_bytes=max(1, size // 2))
        self.assertTrue(fault["fault_observed"])
        r = recover_sealed(path)
        self.assert_denied_not_empty(r)

    # P18-07
    def test_p18_07_authority_bearing_page_byte_corruption(self):
        path = self.db(); self.prepare_active(path); checkpoint(path)
        raw = path.read_bytes()
        marker = b"semantic-A"
        offset = raw.find(marker)
        self.assertGreaterEqual(offset, 0, "authority semantic marker must be physically present in checkpointed DB")
        fault = mutate_main_byte(path, offset=offset + 2)
        self.assertTrue(fault["fault_observed"])
        r = recover_sealed(path)
        self.assert_denied_not_empty(r)
        self.assertFalse(r["storage_integrity"])

    # P18-08
    def test_p18_08_monotonic_metadata_fence_corruption(self):
        path = self.db(); self.prepare_active(path, self.p(term=3, index=7, epoch=4))
        corrupt_meta_below_rows(path)
        r = recover_sealed(path)
        self.assert_denied_not_empty(r)
        self.assertFalse(r["storage_integrity"])

    # P18-09
    def test_p18_09_stale_lower_database_substitution_below_anchor(self):
        stale = self.db("stale.db")
        self.prepare_active(stale, self.p(term=1, index=1, epoch=1, owner="stale"))
        anchor = self.root / "anchor.json"
        write_anchor(anchor, term=4, commit_index=9, lease_epoch=5)
        r = recover_sealed(stale, anchor)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "ANCHORED_HIGHER_FENCE_MISSING")
        self.assertEqual(r["recovery_status"], "STALE_ROLLBACK_BLOCKED")

    # P18-10
    def test_p18_10_wal_removed_while_higher_state_exists_only_in_wal(self):
        base = self.db("live.db"); snap = self.db("snap.db")
        higher = self.p(term=2, index=2, epoch=2, owner="higher")
        info = create_live_wal_snapshot(base, snap, higher)
        self.assertTrue(info["wal_created"])
        fault = remove_wal(snap)
        self.assertTrue(fault["fault_observed"])
        anchor = self.root / "anchor10.json"; write_anchor(anchor, term=2, commit_index=2, lease_epoch=2)
        r = recover_strict(snap, anchor)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "ANCHORED_HIGHER_FENCE_MISSING")

    # P18-11
    def test_p18_11_wal_truncation_on_isolated_copy(self):
        base = self.db("live11.db"); snap = self.db("snap11.db")
        higher = self.p(term=3, index=3, epoch=3, owner="higher")
        info = create_live_wal_snapshot(base, snap, higher); self.assertTrue(info["wal_created"])
        fault = truncate_wal(snap, remove_bytes=max(64, info["wal_size"] // 3))
        self.assertTrue(fault["fault_observed"])
        anchor = self.root / "anchor11.json"; write_anchor(anchor, term=3, commit_index=3, lease_epoch=3)
        r = recover_strict(snap, anchor)
        self.assertFalse(r["authorized"], r)
        self.assertIn(r["recovery_status"], {"STALE_ROLLBACK_BLOCKED", "STORAGE_CORRUPT"})

    # P18-12
    def test_p18_12_wal_byte_corruption_on_isolated_copy(self):
        base = self.db("live12.db"); snap = self.db("snap12.db")
        higher = self.p(term=3, index=4, epoch=3, owner="higher")
        info = create_live_wal_snapshot(base, snap, higher); self.assertTrue(info["wal_created"])
        fault = mutate_wal_byte(snap, offset=24)
        self.assertTrue(fault["fault_observed"])
        anchor = self.root / "anchor12.json"; write_anchor(anchor, term=3, commit_index=4, lease_epoch=3)
        r = recover_strict(snap, anchor)
        self.assertFalse(r["authorized"], r)
        self.assertNotEqual(r.get("recovery_status"), "AUTHORITATIVE")

    # P18-13
    def test_p18_13_stale_main_database_with_unrelated_newer_wal(self):
        stale = self.db("stale13.db"); self.prepare_active(stale, self.p(term=1, index=1, epoch=1, owner="stale")); checkpoint(stale)
        live = self.db("live13.db"); wal_source = self.db("wal13.db")
        unrelated = authority_payload(logical_id="unrelated", term=5, commit_index=5, owner="other", lease_epoch=5,
                                      semantic_digest="semantic-X", effect_digest="effect-X", idempotency_key="intent-X")
        info = create_live_wal_snapshot(live, wal_source, unrelated); self.assertTrue(info["wal_created"])
        # Pair bytes deliberately: stale main plus WAL produced for a different DB lineage.
        from sqlite_storage_fault_exp_o import pair_main_and_wal
        pair = pair_main_and_wal(stale, wal_source, self.db("pair13.db")); self.assertTrue(pair["fault_observed"])
        anchor = self.root / "anchor13.json"; write_anchor(anchor, term=5, commit_index=5, lease_epoch=5)
        r = recover_strict(self.db("pair13.db"), anchor)
        self.assertFalse(r["authorized"], r)
        self.assertNotEqual(r.get("recovery_status"), "AUTHORITATIVE")

    # P18-14
    def test_p18_14_effect_row_corruption_after_committed_effect(self):
        path = self.db(); self.prepare_effect(path)
        corrupt_effect_digest(path, "effect-CORRUPTED")
        r = recover_sealed(path)
        self.assert_denied_not_empty(r)
        self.assertFalse(r["storage_integrity"])

    # P18-15
    def test_p18_15_effect_deleted_while_consumed_state_references_it(self):
        path = self.db(); self.prepare_effect(path, consume=True)
        delete_effect_rows(path)
        r = recover_sealed(path)
        self.assert_denied_not_empty(r)
        self.assertFalse(r["storage_integrity"])

    # P18-16
    def test_p18_16_idempotency_key_with_corrupted_different_effect_digest(self):
        path = self.db(); p = self.prepare_effect(path)
        corrupt_effect_digest(path, "effect-B")
        r = recover_sealed(path)
        self.assert_denied_not_empty(r)
        conn = connect(path)
        try:
            count = conn.execute("SELECT COUNT(*) FROM effects WHERE idempotency_key=?", (p["idempotency_key"],)).fetchone()[0]
            self.assertEqual(count, 1)
        finally:
            conn.close()

    # P18-17
    def test_p18_17_duplicate_active_authority_after_storage_mutation(self):
        path = self.db(); self.prepare_active(path)
        create_duplicate_active(path)
        r = recover_sealed(path)
        self.assert_denied_not_empty(r)
        self.assertFalse(r["storage_integrity"])

    # P18-18
    def test_p18_18_integrity_failure_is_not_clean_absence(self):
        path = self.db(); self.prepare_active(path); checkpoint(path)
        mutate_main_byte(path, offset=0)
        r = recover_sealed(path)
        self.assert_denied_not_empty(r)
        self.assertEqual(r["recovery_status"], "STORAGE_CORRUPT")

    # P18-19
    def test_p18_19_repeated_reopen_of_corrupted_copy_stays_fail_closed(self):
        path = self.db(); self.prepare_active(path); checkpoint(path)
        mutate_main_byte(path, offset=0)
        results = [recover_sealed(path) for _ in range(3)]
        self.assertTrue(all(not r.get("authorized", False) for r in results))
        self.assertTrue(all(r.get("recovery_status") == "STORAGE_CORRUPT" for r in results))
        self.assertTrue(all(r.get("reason") != "NO_ACTIVE_AUTHORITY" for r in results))

    # P18-20
    def test_p18_20_fresh_clean_liveness_after_isolated_faults(self):
        path = self.db("fresh20.db")
        p = self.prepare_active(path, self.p(term=7, index=11, epoch=8, owner="fresh", key="intent-20", effect="effect-20", semantic="semantic-20"))
        first = worker_effect(str(path), p, None)
        self.assertTrue(first["executed"])
        second = worker_effect(str(path), p, None)
        self.assertFalse(second["executed"])
        self.assertEqual(second["decision"], "RECONCILED")
        consumed = worker_consume(str(path), p, None)
        self.assertEqual(consumed["decision"], "CONSUMED")
        seal_state(path)
        recovered = recover_sealed(path)
        self.assertFalse(recovered["authorized"])
        self.assertEqual(recovered["recovery_status"], "RECOVERED_CONSUMED")
        conn = connect(path)
        try:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0], 1)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
