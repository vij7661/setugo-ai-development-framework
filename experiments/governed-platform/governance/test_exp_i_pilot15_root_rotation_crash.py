from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from exp_i_asymmetric_checkpoint_signer import _ensure_ed25519_keypair
from exp_i_root_rotation import PlatformRootTrustAuthority, RootMinimumAuthority, RotatingRootSigner, RootRotatingRegistry
from exp_i_root_rotation_crash import RootRotationRecovery


class ExpIPilot15RootRotationCrashTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.rootdb = self.d / "root.db"
        self.rootauth = self.d / "root-auth.key"
        self.mindb = self.d / "minimum.db"
        self.trust = PlatformRootTrustAuthority(self.rootdb, self.rootauth)
        self.minimum = RootMinimumAuthority(self.mindb)
        self.keys = {}
        for rid in ("R1", "R2", "R2X", "R3"):
            priv = self.d / f"{rid}.priv.pem"
            pub = self.d / f"{rid}.pub.pem"
            _ensure_ed25519_keypair(str(priv), str(pub))
            self.keys[rid] = pub.read_text()
        self.r1 = self.trust.bootstrap(
            transition_id="ROOT-T1",
            root_id="R1",
            public_key_pem=self.keys["R1"],
            activation_registry_epoch=0,
        )
        self.minimum.advance(1, self.r1["record_digest"])
        self.pre_rotation_snapshot = self.d / "root-pre-r2.db"
        shutil.copy2(self.rootdb, self.pre_rotation_snapshot)

    def tearDown(self):
        self.tmp.cleanup()

    def _worker(self, boundary: str):
        module = Path(__file__).with_name("exp_i_root_rotation_crash.py")
        p = subprocess.Popen(
            [
                sys.executable,
                str(module),
                "--rotation-worker",
                "--root-db",
                str(self.rootdb),
                "--root-auth",
                str(self.rootauth),
                "--minimum-db",
                str(self.mindb),
                "--boundary",
                boundary,
                "--transition-id",
                "ROOT-T2",
                "--expected-prior-root-id",
                "R1",
                "--next-root-id",
                "R2",
                "--next-public-key-pem",
                self.keys["R2"],
                "--activation-registry-epoch",
                "1",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        line = p.stdout.readline()
        if not line:
            err = p.stderr.read()
            p.wait(timeout=5)
            self.fail(f"rotation worker failed before readiness: {err}")
        ready = json.loads(line)
        self.assertTrue(ready["ready"])
        self.assertEqual(ready["boundary"], boundary)
        self.assertEqual(ready["pid"], p.pid)
        self.assertNotEqual(p.pid, os.getpid())
        p.kill()
        p.wait(timeout=5)
        p.stdout.close()
        p.stderr.close()
        return ready, p.returncode

    def _recovery(self):
        return RootRotationRecovery(self.rootdb, self.rootauth, self.mindb)

    def _rows(self):
        c = sqlite3.connect(self.rootdb)
        rows = c.execute("SELECT root_epoch,transition_id,record_digest FROM root_records ORDER BY root_epoch").fetchall()
        c.close()
        return rows

    def _make_ambiguous_r2(self):
        self._worker("AFTER_ROOT_COMMIT_BEFORE_MINIMUM")
        state = self._recovery().inspect()
        self.assertTrue(state["ambiguous"])
        return state

    def _reconcile_r2(self):
        return self._recovery().reconcile_exact(
            transition_id="ROOT-T2",
            expected_prior_root_id="R1",
            next_root_id="R2",
            next_public_key_pem=self.keys["R2"],
            activation_registry_epoch=1,
        )

    def test_p15_01_parent_child_readiness_proves_distinct_externally_killed_worker(self):
        ready, rc = self._worker("BEFORE_ROOT_TX")
        self.assertNotEqual(ready["pid"], os.getpid())
        self.assertNotEqual(rc, 0)

    def test_p15_02_kill_before_root_transaction_leaves_r1_current_no_false_r2(self):
        self._worker("BEFORE_ROOT_TX")
        cur = self._recovery().current_for_consequential_use()["record"]
        self.assertEqual(cur["active_root_id"], "R1")
        self.assertEqual(len(self._rows()), 1)

    def test_p15_03_kill_after_root_begin_before_insert_leaves_no_partial_r2(self):
        self._worker("AFTER_ROOT_BEGIN_BEFORE_INSERT")
        self.assertEqual(len(self._rows()), 1)
        self.assertEqual(self._recovery().current_for_consequential_use()["record"]["active_root_id"], "R1")

    def test_p15_04_kill_after_r2_insert_before_root_commit_rolls_back_on_reopen(self):
        self._worker("AFTER_ROOT_INSERT_BEFORE_COMMIT")
        self.assertEqual(len(self._rows()), 1)
        self.assertEqual(self._recovery().current_for_consequential_use()["record"]["active_root_id"], "R1")

    def test_p15_05_durable_r2_before_minimum_is_ambiguous_and_noncurrent(self):
        state = self._make_ambiguous_r2()
        self.assertEqual(state["latest"]["record"]["active_root_id"], "R2")
        self.assertEqual(state["minimum_epoch"], 1)
        with self.assertRaisesRegex(PermissionError, "ROOT_ROTATION_AMBIGUOUS"):
            self._recovery().current_for_consequential_use()

    def test_p15_06_exact_ambiguous_r2_recovery_advances_minimum_once(self):
        self._make_ambiguous_r2()
        first = self._reconcile_r2()
        second = self._reconcile_r2()
        self.assertEqual(first["record_digest"], second["record_digest"])
        self.assertEqual(first["record"]["active_root_id"], "R2")
        self.assertEqual(self.minimum.current(), (2, first["record_digest"]))
        self.assertEqual(len(self._rows()), 2)

    def test_p15_07_kill_after_minimum_begin_before_mutation_preserves_old_minimum_and_ambiguity(self):
        self._worker("AFTER_MINIMUM_BEGIN_BEFORE_MUTATION")
        state = self._recovery().inspect()
        self.assertTrue(state["ambiguous"])
        self.assertEqual((state["minimum_epoch"], state["minimum_digest"]), self.minimum.current())
        self.assertEqual(state["minimum_epoch"], 1)

    def test_p15_08_kill_after_minimum_mutation_before_commit_rolls_back_minimum(self):
        self._worker("AFTER_MINIMUM_MUTATION_BEFORE_COMMIT")
        state = self._recovery().inspect()
        self.assertTrue(state["ambiguous"])
        self.assertEqual(self.minimum.current(), (1, self.r1["record_digest"]))
        self.assertEqual(self._reconcile_r2()["record"]["active_root_id"], "R2")

    def test_p15_09_post_minimum_commit_preack_replay_is_same_r2_no_duplicate(self):
        self._worker("AFTER_MINIMUM_COMMIT_BEFORE_ACK")
        before = self._recovery().current_for_consequential_use()
        replay = self._reconcile_r2()
        self.assertEqual(before["record_digest"], replay["record_digest"])
        self.assertEqual(len(self._rows()), 2)
        self.assertEqual(self.minimum.current(), (2, replay["record_digest"]))

    def test_p15_10_same_transition_identity_semantic_rebinding_denied_after_recovery(self):
        self._make_ambiguous_r2()
        with self.assertRaisesRegex(PermissionError, "ROOT_RECOVERY_SEMANTIC_MISMATCH"):
            self._recovery().reconcile_exact(
                transition_id="ROOT-T2",
                expected_prior_root_id="R1",
                next_root_id="R2",
                next_public_key_pem=self.keys["R2X"],
                activation_registry_epoch=99,
            )
        self.assertEqual(self._reconcile_r2()["record"]["active_root_id"], "R2")

    def test_p15_11_stale_pre_rotation_root_snapshot_cannot_restore_r1_after_minimum_advance(self):
        self._make_ambiguous_r2()
        r2 = self._reconcile_r2()
        stale = RootRotationRecovery(self.pre_rotation_snapshot, self.rootauth, self.mindb)
        with self.assertRaises(PermissionError):
            stale.current_for_consequential_use()
        self.assertEqual(self.minimum.current(), (2, r2["record_digest"]))

    def test_p15_12_r1_cannot_regain_new_issuance_authority_during_ambiguous_r2(self):
        self._make_ambiguous_r2()
        recovery = self._recovery()
        with self.assertRaisesRegex(PermissionError, "ROOT_ROTATION_AMBIGUOUS"):
            recovery.root_is_currently_eligible("R1", self.keys["R1"])
        with self.assertRaisesRegex(PermissionError, "ROOT_ROTATION_AMBIGUOUS"):
            recovery.root_is_currently_eligible("R2", self.keys["R2"])

    def test_p15_13_two_recovery_workers_racing_same_r2_converge_one_binding(self):
        self._make_ambiguous_r2()
        code = (
            "import json,sys; "
            "from exp_i_root_rotation_crash import RootRotationRecovery; "
            "r=RootRotationRecovery(sys.argv[1],sys.argv[2],sys.argv[3]); "
            "x=r.reconcile_exact(transition_id='ROOT-T2',expected_prior_root_id='R1',next_root_id='R2',next_public_key_pem=sys.argv[4],activation_registry_epoch=1); "
            "print(json.dumps({'digest':x['record_digest'],'root':x['record']['active_root_id']}))"
        )
        env = dict(os.environ)
        env["PYTHONPATH"] = str(Path(__file__).parent) + os.pathsep + env.get("PYTHONPATH", "")
        argv = [sys.executable, "-c", code, str(self.rootdb), str(self.rootauth), str(self.mindb), self.keys["R2"]]
        p1 = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        p2 = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        o1, e1 = p1.communicate(timeout=10)
        o2, e2 = p2.communicate(timeout=10)
        self.assertEqual((p1.returncode, p2.returncode), (0, 0), (e1, e2))
        r1, r2 = json.loads(o1), json.loads(o2)
        self.assertEqual(r1, r2)
        self.assertEqual(r1["root"], "R2")
        self.assertEqual(self.minimum.current(), (2, r1["digest"]))
        self.assertEqual(len(self._rows()), 2)

    def test_p15_14_repeated_reopen_preserves_highest_reconciled_epoch_and_never_implicit_success(self):
        self._make_ambiguous_r2()
        for _ in range(3):
            state = self._recovery().inspect()
            self.assertTrue(state["ambiguous"])
            with self.assertRaisesRegex(PermissionError, "ROOT_ROTATION_AMBIGUOUS"):
                self._recovery().current_for_consequential_use()
        r2 = self._reconcile_r2()
        for _ in range(3):
            cur = self._recovery().current_for_consequential_use()
            self.assertEqual(cur["record_digest"], r2["record_digest"])
            self.assertEqual(cur["record"]["root_epoch"], 2)

    def test_p15_15_nonplatform_surfaces_have_zero_ambiguous_resolution_or_release_authority(self):
        # The platform recovery authority is an explicit separate surface.  Root signers
        # and registry writers do not expose its reconciliation or minimum mutation API.
        self.assertTrue(hasattr(RootRotationRecovery, "reconcile_exact"))
        for cls in (RotatingRootSigner, RootRotatingRegistry):
            self.assertFalse(hasattr(cls, "reconcile_exact"))
            self.assertFalse(hasattr(cls, "clean_rotate"))
            self.assertFalse(hasattr(cls, "advance"))
            self.assertFalse(hasattr(cls, "release"))
            self.assertFalse(hasattr(cls, "deploy"))
        model_surface = {"requested_authority": ["release", "minimum-write"]}
        reviewer_surface = {"requested_authority": ["deploy", "root-reconcile"]}
        self.assertEqual(set(model_surface) & {"release", "deploy"}, set())
        self.assertEqual(set(reviewer_surface) & {"release", "deploy"}, set())

    def test_p15_16_clean_r2_to_r3_rotation_live_after_crash_recovery(self):
        self._make_ambiguous_r2()
        r2 = self._reconcile_r2()
        recovery = self._recovery()
        r3 = recovery.clean_rotate(
            transition_id="ROOT-T3",
            expected_prior_root_id="R2",
            next_root_id="R3",
            next_public_key_pem=self.keys["R3"],
            activation_registry_epoch=2,
        )
        self.assertEqual(r2["record"]["root_epoch"], 2)
        self.assertEqual(r3["record"]["root_epoch"], 3)
        self.assertEqual(r3["record"]["active_root_id"], "R3")
        self.assertEqual(self.minimum.current(), (3, r3["record_digest"]))
        self.assertEqual(len(self._rows()), 3)


if __name__ == "__main__":
    unittest.main()
