from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_composite_authority_process import (
    AUTHORITY_ID,
    SCOPE,
    CompositeCheckpointAuthorityProcess,
    checkpoint_digest,
)
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_use_time_checkpoint import UseTimeCheckpointAuthority

CASE = "EXP-I-P10-CASE"
PERMIT_KEY = b"exp-i-pilot10-permit-key"
PERMIT_INTEGRITY_KEY = b"exp-i-pilot10-permit-integrity-key"
RECON_INTEGRITY_KEY = b"exp-i-pilot10-reconciliation-integrity-key"
CHECKPOINT_KEY = b"exp-i-pilot10-checkpoint-key"
TOKEN_KEY = b"exp-i-pilot10-token-key"


def reviews():
    return [ReviewClaim(x, CASE, "CODE DEFECT", ("CODE",)) for x in ("r1", "r2", "r3")]


def verifier():
    return VerificationArtifact("platform-independent-verifier", True, True, CASE, "CODE DEFECT", ("CODE",))


def signals():
    return {
        "evidence_complete": True,
        "requirement_ambiguity": False,
        "material_conflict": False,
        "r3_completed": True,
        "r3_required": True,
        "r3_available_qualified": True,
        "review_ceiling_reached": False,
        "material_revision_since_review": False,
        "authoritative_failure_established": False,
        "non_material_dissent": False,
        "max_unresolved_severity": "NONE",
    }


class ExpIPilot10CompositeAuthorityProcessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.main_db = self.root / "governance.sqlite"
        self.authority_db = self.root / "composite-authority.sqlite"
        self.permits = DurableConvergencePermitAuthority(self.main_db, PERMIT_KEY)
        self.permits.issue(reviews(), verifier(), signals(), nonce="permit-1")
        self.use_time = UseTimeCheckpointAuthority(
            self.main_db, PERMIT_KEY, PERMIT_INTEGRITY_KEY, TOKEN_KEY
        )
        self.processes = []

    def tearDown(self):
        for p in self.processes:
            try:
                p.stop(kill=True)
            except Exception:
                pass
        self.tmp.cleanup()

    def authority(self):
        p = CompositeCheckpointAuthorityProcess(
            main_db=self.main_db,
            authority_store=self.authority_db,
            checkpoint_key=CHECKPOINT_KEY,
            permit_integrity_key=PERMIT_INTEGRITY_KEY,
            reconciliation_integrity_key=RECON_INTEGRITY_KEY,
        )
        self.processes.append(p)
        return p

    def sql_main(self, statement, params=()):
        con = sqlite3.connect(self.main_db, timeout=5.0)
        try:
            con.execute("PRAGMA ignore_check_constraints=ON")
            con.execute(statement, params)
            con.commit()
        finally:
            con.close()

    def sql_authority(self, statement, params=()):
        con = sqlite3.connect(self.authority_db, timeout=5.0)
        try:
            con.execute(statement, params)
            con.commit()
        finally:
            con.close()

    def issue1(self, a=None):
        a = a or self.authority()
        r = a.issue("issuance-1", 1)
        self.assertTrue(r.get("ok"), r)
        return a, r

    def test_p10_01_authority_is_distinct_process_and_separate_store(self):
        a = self.authority()
        self.assertNotEqual(a.pid, os.getpid())
        self.assertNotEqual(Path(a.store).resolve(), Path(a.main_db).resolve())
        self.assertTrue(Path(a.store).exists())

    def test_p10_02_caller_object_and_argv_do_not_expose_checkpoint_signing_bytes(self):
        a = self.authority()
        self.assertNotIn(CHECKPOINT_KEY.hex(), " ".join(a.argv))
        self.assertNotIn(CHECKPOINT_KEY, a.__dict__.values())
        self.assertFalse(hasattr(a, "checkpoint_key"))
        self.assertEqual(set(a.env_keys), {
            "EXP_I_P10_CHECKPOINT_KEY_HEX",
            "EXP_I_P10_PERMIT_INTEGRITY_KEY_HEX",
            "EXP_I_P10_RECON_INTEGRITY_KEY_HEX",
        })

    def test_p10_03_clean_issue_binds_exact_current_pair_and_epoch(self):
        a, r = self.issue1()
        from exp_i_composite_integrity import CompositeIntegrityAuthority
        pair = CompositeIntegrityAuthority(
            self.main_db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, CHECKPOINT_KEY
        ).current_pair()
        s = r["statement"]
        self.assertEqual(s["permit_ledger_digest"], pair["permit_ledger_digest"])
        self.assertEqual(s["reconciliation_digest"], pair["reconciliation_digest"])
        self.assertEqual(s["permit_authority_epoch"], pair["permit_authority_epoch"])
        self.assertEqual(s["authority_id"], AUTHORITY_ID)
        self.assertEqual(s["scope"], SCOPE)

    def test_p10_04_clean_verify_requires_exact_durable_record_and_current_state(self):
        a, r = self.issue1()
        v = a.verify(r, minimum_generation=1)
        self.assertTrue(v.get("ok"), v)
        self.assertEqual(v["checkpoint_digest"], r["checkpoint_digest"])

    def test_p10_05_unrelated_key_forgery_is_rejected(self):
        a, r = self.issue1()
        forged = json.loads(json.dumps(r))
        forged["auth_tag"] = hmac.new(b"wrong-key", json.dumps(forged["statement"], sort_keys=True, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
        self.assertFalse(a.verify(forged, minimum_generation=1)["ok"])

    def test_p10_06_lower_generation_refused_after_higher_generation(self):
        a, r1 = self.issue1()
        r2 = a.issue("issuance-2", 2)
        self.assertTrue(r2["ok"], r2)
        low = a.issue("issuance-low", 1)
        self.assertFalse(low["ok"])
        self.assertEqual(low["reason"], "CHECKPOINT_GENERATION_ROLLBACK")

    def test_p10_07_same_generation_conflicting_current_state_is_refused(self):
        a, r1 = self.issue1()
        r2 = a.issue("issuance-2", 2)
        self.assertTrue(r2["ok"], r2)
        self.permits.issue(reviews(), verifier(), signals(), nonce="permit-2")
        conflict = a.issue("issuance-conflict", 2)
        self.assertFalse(conflict["ok"])
        self.assertEqual(conflict["reason"], "CHECKPOINT_SAME_GENERATION_EQUIVOCATION")

    def test_p10_08_monotonicity_and_equivocation_memory_survive_restart(self):
        a, r1 = self.issue1()
        r2 = a.issue("issuance-2", 2)
        self.assertTrue(r2["ok"])
        old_pid = a.pid
        a.stop(kill=True)
        b = self.authority()
        self.assertNotEqual(old_pid, b.pid)
        self.assertFalse(b.issue("issuance-low", 1)["ok"])
        self.permits.issue(reviews(), verifier(), signals(), nonce="permit-2")
        self.assertFalse(b.issue("issuance-conflict", 2)["ok"])

    def test_p10_09_exact_issue_replay_is_idempotent(self):
        a, first = self.issue1()
        second = a.issue("issuance-1", 1)
        self.assertTrue(second["ok"])
        self.assertTrue(second["replay"])
        self.assertEqual(first["checkpoint_digest"], second["checkpoint_digest"])
        self.assertEqual(first["auth_tag"], second["auth_tag"])

    def test_p10_10_checkpoint_authentication_mutation_is_rejected(self):
        a, r = self.issue1()
        changed = json.loads(json.dumps(r))
        changed["auth_tag"] = "0" * len(changed["auth_tag"])
        self.assertFalse(a.verify(changed, minimum_generation=1)["ok"])

    def test_p10_11_signed_binding_substitution_is_rejected(self):
        a, r = self.issue1()
        mutations = {
            "scope": "OTHER",
            "authority_id": "other-authority",
            "issuance_id": "other-issuance",
            "generation": 2,
            "permit_ledger_digest": "a" * 64,
            "reconciliation_digest": "b" * 64,
            "permit_authority_epoch": r["statement"]["permit_authority_epoch"] + 1,
            "previous_checkpoint_digest": "c" * 64,
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                changed = json.loads(json.dumps(r))
                changed["statement"][field] = value
                changed["checkpoint_digest"] = checkpoint_digest(changed["statement"])
                self.assertFalse(a.verify(changed, minimum_generation=1)["ok"])

    def test_p10_12_old_valid_checkpoint_below_trusted_minimum_is_rejected(self):
        a, r1 = self.issue1()
        self.assertTrue(a.issue("issuance-2", 2)["ok"])
        v = a.verify(r1, minimum_generation=2)
        self.assertFalse(v["ok"])
        self.assertEqual(v["reason"], "CHECKPOINT_ROLLBACK")

    def test_p10_13_authority_unavailability_fails_closed_without_local_substitution(self):
        a, r = self.issue1()
        a.stop(kill=True)
        v = a.verify(r, minimum_generation=1)
        self.assertFalse(v["ok"])
        self.assertEqual(v["reason"], "CHECKPOINT_AUTHORITY_UNAVAILABLE")
        self.assertFalse(hasattr(a, "verify_locally"))

    def test_p10_14_prior_positive_verify_cannot_rebind_changed_checkpoint(self):
        a, r = self.issue1()
        prior = a.verify(r, minimum_generation=1)
        self.assertTrue(prior["ok"])
        changed = json.loads(json.dumps(r))
        changed["statement"]["issuance_id"] = "substituted"
        changed["checkpoint_digest"] = checkpoint_digest(changed["statement"])
        self.assertFalse(a.verify(changed, minimum_generation=1)["ok"])
        self.assertFalse("authorize" in prior)

    def test_p10_15_prior_positive_verify_fails_after_permit_ledger_changes(self):
        a, r = self.issue1()
        self.assertTrue(a.verify(r, minimum_generation=1)["ok"])
        self.permits.issue(reviews(), verifier(), signals(), nonce="permit-2")
        v = a.verify(r, minimum_generation=1)
        self.assertFalse(v["ok"])
        self.assertEqual(v["reason"], "PERMIT_LEDGER_STALE")

    def test_p10_16_prior_positive_verify_fails_after_reconciliation_or_epoch_change(self):
        a, r = self.issue1()
        self.assertTrue(a.verify(r, minimum_generation=1)["ok"])
        self.sql_main(
            "INSERT INTO convergence_reconciliation(reconciliation_id,token_nonce,permit_nonce,pre_ledger_digest,post_ledger_digest,checkpoint_generation,status,settlement_checkpoint_digest) VALUES(?,?,?,?,?,?,?,?)",
            ("rx", "tx", "permit-1", "a" * 64, "b" * 64, 1, "PENDING", None),
        )
        self.assertEqual(a.verify(r, minimum_generation=1)["reason"], "RECONCILIATION_LEDGER_STALE")
        self.sql_main("DELETE FROM convergence_reconciliation WHERE reconciliation_id='rx'")
        self.sql_main("UPDATE authority_meta SET issuance_epoch=issuance_epoch+1 WHERE singleton=1")
        self.assertEqual(a.verify(r, minimum_generation=1)["reason"], "PERMIT_LEDGER_STALE")

    def test_p10_17_postcommit_response_loss_restarts_as_same_idempotent_checkpoint(self):
        a = self.authority()
        lost = a.issue("issuance-1", 1, crash_after_commit=True)
        self.assertFalse(lost["ok"])
        self.assertEqual(lost["reason"], "CHECKPOINT_AUTHORITY_RESPONSE_LOST")
        b = self.authority()
        replay = b.issue("issuance-1", 1)
        self.assertTrue(replay["ok"], replay)
        self.assertTrue(replay["replay"])
        self.assertTrue(b.verify(replay, minimum_generation=1)["ok"])

    def test_p10_18_authority_store_tamper_or_deletion_blocks_verification(self):
        a, r = self.issue1()
        self.sql_authority(
            "UPDATE issued SET statement_json=? WHERE generation=1",
            (json.dumps({"tampered": True}),),
        )
        self.assertFalse(a.verify(r, minimum_generation=1)["ok"])
        self.sql_authority("DELETE FROM issued WHERE generation=1")
        self.assertFalse(a.verify(r, minimum_generation=1)["ok"])

    def test_p10_19_process_model_reviewer_outputs_have_zero_release_authority(self):
        a, r = self.issue1()
        v = a.verify(r, minimum_generation=1)
        self.assertTrue(v["ok"])
        self.assertFalse(v["reviewer_generated_authority"])
        self.assertFalse(v["production_authority"])
        self.assertFalse(v["release_authority"])
        self.assertFalse(hasattr(reviews()[0], "issue_checkpoint"))

    def test_p10_20_clean_higher_generation_liveness_after_restart(self):
        a, r1 = self.issue1()
        self.assertTrue(a.verify(r1, minimum_generation=1)["ok"])
        r2 = a.issue("issuance-2", 2)
        self.assertTrue(r2["ok"])
        a.stop(kill=True)
        b = self.authority()
        self.assertTrue(b.verify(r2, minimum_generation=2)["ok"])
        r3 = b.issue("issuance-3", 3)
        self.assertTrue(r3["ok"], r3)
        self.assertTrue(b.verify(r3, minimum_generation=3)["ok"])


if __name__ == "__main__":
    unittest.main()
