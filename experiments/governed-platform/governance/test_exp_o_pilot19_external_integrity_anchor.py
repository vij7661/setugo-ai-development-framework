from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from external_integrity_anchor_exp_o import issue_checkpoint, load_checkpoint, recover_external, write_checkpoint
from sqlite_process_crash_exp_o import authority_payload, connect, worker_authority, worker_consume, worker_effect
from sqlite_storage_seal_exp_o import init_sealed_db, seal_state


KEY = b"pilot19-test-trusted-key-material"
WRONG_KEY = b"pilot19-wrong-key-material"
TRUSTED = {"pilot19-k1": KEY}
PROJECT = "governed-platform"
TASK = "EXP-O-PILOT19"
STATE_ID = "authority-ledger-A"


class ExpOPilot19ExternalIntegrityAnchorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.root = Path(self.td.name)

    def tearDown(self) -> None:
        self.td.cleanup()

    def db(self, name: str = "case.db") -> Path:
        return self.root / name

    def cp(self, name: str = "checkpoint.json") -> Path:
        return self.root / name

    def p(self, *, logical_id: str = "auth-1", term: int = 1, index: int = 1, owner: str = "r1",
          epoch: int = 1, semantic: str = "semantic-A", effect: str = "effect-A", key: str = "intent-1"):
        return authority_payload(logical_id=logical_id, term=term, commit_index=index, owner=owner,
                                 lease_epoch=epoch, semantic_digest=semantic, effect_digest=effect,
                                 idempotency_key=key)

    def prepare_active(self, path: Path, payload=None):
        payload = payload or self.p()
        init_sealed_db(path)
        result = worker_authority(str(path), payload, None)
        self.assertTrue(result["authorized"])
        seal_state(path)
        return payload

    def prepare_effect(self, path: Path, payload=None, *, consume: bool = False):
        payload = self.prepare_active(path, payload)
        effect = worker_effect(str(path), payload, None)
        self.assertTrue(effect["executed"])
        if consume:
            consumed = worker_consume(str(path), payload, None)
            self.assertEqual(consumed["decision"], "CONSUMED")
        seal_state(path)
        return payload

    def issue(self, path: Path, cp: Path, *, generation: int = 1, key: bytes = KEY,
              key_id: str = "pilot19-k1", project: str = PROJECT, task: str = TASK,
              state_id: str = STATE_ID):
        return issue_checkpoint(path, cp, key=key, key_id=key_id, project=project, task=task,
                                logical_state_id=state_id, generation=generation)

    def recover(self, path: Path, cp: Path | None, *, minimum: int = 1,
                trusted=None, project: str = PROJECT, task: str = TASK, state_id: str = STATE_ID):
        return recover_external(path, cp, trusted_keys=trusted or TRUSTED, expected_project=project,
                                expected_task=task, expected_logical_state_id=state_id,
                                minimum_generation=minimum)

    def reseal(self, path: Path) -> None:
        seal_state(path)

    # P19-01
    def test_p19_01_clean_externally_anchored_authority_control(self):
        path = self.db(); self.prepare_active(path)
        cp = self.cp(); self.issue(path, cp, generation=1)
        r = self.recover(path, cp, minimum=1)
        self.assertTrue(r["authorized"])
        self.assertTrue(r["local_integrity"])
        self.assertTrue(r["external_integrity"])
        self.assertEqual(r["checkpoint_generation"], 1)
        self.assertNotIn(KEY, path.read_bytes())

    # P19-02
    def test_p19_02_coherent_authority_rewrite_with_recomputed_local_seals(self):
        path = self.db(); self.prepare_active(path)
        cp = self.cp(); self.issue(path, cp)
        conn = connect(path)
        try:
            conn.execute("UPDATE authority SET semantic_digest='semantic-TAMPERED' WHERE status='ACTIVE'")
        finally:
            conn.close()
        self.reseal(path)
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertTrue(r["local_integrity"])
        self.assertEqual(r["reason"], "EXTERNAL_STATE_ROOT_MISMATCH")

    # P19-03
    def test_p19_03_coherent_owner_fence_rewrite_with_recomputed_local_seals(self):
        path = self.db(); self.prepare_active(path, self.p(owner="old"))
        cp = self.cp(); self.issue(path, cp)
        conn = connect(path)
        try:
            conn.execute("UPDATE authority SET owner='forged-owner',term=2,commit_index=2,lease_epoch=2 WHERE status='ACTIVE'")
            conn.execute("UPDATE meta SET max_term=2,max_index=2,max_epoch=2 WHERE id=1")
        finally:
            conn.close()
        self.reseal(path)
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertTrue(r["local_integrity"])
        self.assertEqual(r["reason"], "EXTERNAL_STATE_ROOT_MISMATCH")

    # P19-04
    def test_p19_04_forged_checkpoint_signed_with_wrong_key(self):
        path = self.db(); self.prepare_active(path)
        cp = self.cp(); self.issue(path, cp, key=WRONG_KEY, key_id="pilot19-k1")
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_CHECKPOINT_AUTH_FAILED")

    # P19-05
    def test_p19_05_checkpoint_authentication_tag_byte_mutation(self):
        path = self.db(); self.prepare_active(path)
        cp = self.cp(); self.issue(path, cp)
        record = load_checkpoint(cp)
        tag = str(record["auth_tag"])
        record["auth_tag"] = ("0" if tag[0] != "0" else "1") + tag[1:]
        write_checkpoint(cp, record)
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_CHECKPOINT_AUTH_FAILED")

    # P19-06
    def test_p19_06_valid_old_checkpoint_replay_below_trusted_minimum_generation(self):
        path = self.db(); self.prepare_active(path)
        cp = self.cp(); self.issue(path, cp, generation=1)
        r = self.recover(path, cp, minimum=2)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_CHECKPOINT_ROLLBACK")
        self.assertEqual(r["recovery_status"], "TRUSTED_GENERATION_ROLLBACK_BLOCKED")

    # P19-07
    def test_p19_07_stale_db_local_seals_and_valid_old_checkpoint_bundle(self):
        path = self.db(); self.prepare_active(path, self.p(term=1, index=1, epoch=1, owner="stale"))
        cp = self.cp(); self.issue(path, cp, generation=1)
        r = self.recover(path, cp, minimum=3)
        self.assertFalse(r["authorized"])
        self.assertTrue(r["local_integrity"])
        self.assertEqual(r["reason"], "EXTERNAL_CHECKPOINT_ROLLBACK")

    # P19-08
    def test_p19_08_different_logical_lineage_database_with_current_checkpoint(self):
        a = self.db("a.db"); self.prepare_active(a, self.p(logical_id="auth-A", owner="A"))
        cp = self.cp(); self.issue(a, cp, generation=2)
        b = self.db("b.db"); self.prepare_active(b, self.p(logical_id="auth-B", owner="B", key="intent-B"))
        r = self.recover(b, cp, minimum=2)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_STATE_ROOT_MISMATCH")

    # P19-09
    def test_p19_09_committed_effect_rewritten_with_recomputed_local_seals(self):
        path = self.db(); self.prepare_effect(path)
        cp = self.cp(); self.issue(path, cp)
        conn = connect(path)
        try:
            conn.execute("UPDATE effects SET result_id='forged-result'")
            conn.execute("UPDATE authority SET result_id='forged-result' WHERE status='ACTIVE'")
        finally:
            conn.close()
        self.reseal(path)
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_STATE_ROOT_MISMATCH")

    # P19-10
    def test_p19_10_consumed_authority_resurrected_active_with_recomputed_local_seals(self):
        path = self.db(); self.prepare_effect(path, consume=True)
        cp = self.cp(); self.issue(path, cp)
        conn = connect(path)
        try:
            conn.execute("UPDATE authority SET status='ACTIVE' WHERE status='CONSUMED'")
        finally:
            conn.close()
        self.reseal(path)
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_STATE_ROOT_MISMATCH")

    # P19-11
    def test_p19_11_monotonic_metadata_lowered_with_recomputed_local_seals(self):
        path = self.db(); self.prepare_active(path, self.p(term=4, index=8, epoch=5))
        cp = self.cp(); self.issue(path, cp, generation=4)
        conn = connect(path)
        try:
            conn.execute("UPDATE meta SET max_term=1,max_index=1,max_epoch=1 WHERE id=1")
        finally:
            conn.close()
        self.reseal(path)
        r = self.recover(path, cp, minimum=4)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_STATE_ROOT_MISMATCH")

    # P19-12
    def test_p19_12_idempotency_key_changed_with_recomputed_local_seals(self):
        path = self.db(); self.prepare_active(path)
        cp = self.cp(); self.issue(path, cp)
        conn = connect(path)
        try:
            conn.execute("UPDATE authority SET idempotency_key='intent-forged' WHERE status='ACTIVE'")
        finally:
            conn.close()
        self.reseal(path)
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_STATE_ROOT_MISMATCH")

    # P19-13
    def test_p19_13_semantic_digest_changed_with_recomputed_local_seals(self):
        path = self.db(); self.prepare_active(path)
        cp = self.cp(); self.issue(path, cp)
        conn = connect(path)
        try:
            conn.execute("UPDATE authority SET semantic_digest='semantic-forged' WHERE status='ACTIVE'")
        finally:
            conn.close()
        self.reseal(path)
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_STATE_ROOT_MISMATCH")

    # P19-14
    def test_p19_14_effect_digest_changed_consistently_with_recomputed_local_seals(self):
        path = self.db(); self.prepare_effect(path)
        cp = self.cp(); self.issue(path, cp)
        conn = connect(path)
        try:
            conn.execute("UPDATE authority SET effect_digest='effect-B'")
            conn.execute("UPDATE effects SET effect_digest='effect-B'")
        finally:
            conn.close()
        self.reseal(path)
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_STATE_ROOT_MISMATCH")

    # P19-15
    def test_p19_15_validly_signed_checkpoint_wrong_project_task_scope(self):
        path = self.db(); self.prepare_active(path)
        cp = self.cp(); self.issue(path, cp, project="wrong-project", task="WRONG-TASK")
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_CHECKPOINT_SCOPE_MISMATCH")

    # P19-16
    def test_p19_16_checkpoint_root_replaced_without_valid_authentication(self):
        path = self.db(); self.prepare_active(path)
        cp = self.cp(); self.issue(path, cp)
        record = load_checkpoint(cp)
        original = str(record["state_root"])
        record["state_root"] = "f" * 64 if original != "f" * 64 else "e" * 64
        write_checkpoint(cp, record)
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_CHECKPOINT_AUTH_FAILED")

    # P19-17
    def test_p19_17_external_checkpoint_missing(self):
        path = self.db(); self.prepare_active(path)
        missing = self.cp("missing.json")
        r = self.recover(path, missing)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_CHECKPOINT_MISSING")
        self.assertNotEqual(r.get("reason"), "NO_ACTIVE_AUTHORITY")

    # P19-18
    def test_p19_18_unknown_checkpoint_key_id(self):
        path = self.db(); self.prepare_active(path)
        cp = self.cp(); self.issue(path, cp, key=WRONG_KEY, key_id="unknown-k")
        r = self.recover(path, cp)
        self.assertFalse(r["authorized"])
        self.assertEqual(r["reason"], "EXTERNAL_CHECKPOINT_UNKNOWN_KEY")

    # P19-19
    def test_p19_19_repeated_recovery_same_coherent_forged_bundle_never_promotes(self):
        path = self.db(); self.prepare_active(path)
        cp = self.cp(); self.issue(path, cp)
        conn = connect(path)
        try:
            conn.execute("UPDATE authority SET owner='persistent-forgery' WHERE status='ACTIVE'")
        finally:
            conn.close()
        self.reseal(path)
        results = [self.recover(path, cp) for _ in range(3)]
        self.assertTrue(all(not r.get("authorized", False) for r in results))
        self.assertTrue(all(r.get("reason") == "EXTERNAL_STATE_ROOT_MISMATCH" for r in results))

    # P19-20
    def test_p19_20_clean_higher_generation_liveness_control(self):
        path = self.db("fresh20.db")
        p = self.prepare_active(path, self.p(term=5, index=9, epoch=6, owner="fresh", key="intent-20", semantic="semantic-20", effect="effect-20"))
        first = worker_effect(str(path), p, None)
        self.assertTrue(first["executed"])
        second = worker_effect(str(path), p, None)
        self.assertFalse(second["executed"])
        self.assertEqual(second["decision"], "RECONCILED")
        consumed = worker_consume(str(path), p, None)
        self.assertEqual(consumed["decision"], "CONSUMED")
        self.reseal(path)
        cp = self.cp("cp20.json"); self.issue(path, cp, generation=7)
        recovered = self.recover(path, cp, minimum=7)
        self.assertFalse(recovered["authorized"])
        self.assertTrue(recovered["local_integrity"])
        self.assertTrue(recovered["external_integrity"])
        self.assertEqual(recovered["checkpoint_generation"], 7)
        self.assertEqual(recovered["recovery_status"], "RECOVERED_CONSUMED")
        conn = connect(path)
        try:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM effects").fetchone()[0], 1)
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
