import dataclasses
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_permit_ledger_integrity import PermitLedgerIntegrityAuthority
from exp_i_use_time_checkpoint import UseTimeCheckpointAuthority

CASE = "EXP-I-P5-CASE"
PERMIT_KEY = b"exp-i-pilot5-permit-key"
INTEGRITY_KEY = b"exp-i-pilot5-integrity-key"
TOKEN_KEY = b"exp-i-pilot5-token-key"


def reviews():
    return [ReviewClaim(x, CASE, "CODE DEFECT", ("CODE",)) for x in ("r1", "r2", "r3")]


def verifier():
    return VerificationArtifact("platform-independent-verifier", True, True, CASE, "CODE DEFECT", ("CODE",))


def signals(**overrides):
    data = {
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
    data.update(overrides)
    return data


class ExpIPilot5UseTimeCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "permit.db")
        self.permits = DurableConvergencePermitAuthority(self.db, PERMIT_KEY)
        self.integrity = PermitLedgerIntegrityAuthority(self.db, INTEGRITY_KEY)
        self.use = UseTimeCheckpointAuthority(self.db, PERMIT_KEY, INTEGRITY_KEY, TOKEN_KEY)
        self.p = self.permits.issue(reviews(), verifier(), signals(), nonce="p1")
        self.cp1 = self.integrity.issue_checkpoint(1)

    def tearDown(self):
        self.tmp.cleanup()

    def token(self, nonce="t1"):
        return self.use.issue_token(self.p, self.cp1, trusted_min_generation=1, token_nonce=nonce)

    def consume(self, token=None):
        return self.use.consume(token or self.token(), self.p, reviews(), verifier(), signals())

    def checkpoint_after_consumption(self, generation=2):
        return self.integrity.issue_checkpoint(generation, previous=self.cp1)

    def test_p5_01_clean_checkpoint_issues_exact_use_time_token(self):
        t = self.token("clean-token")
        self.assertEqual(t.permit_nonce, self.p.nonce)
        self.assertEqual(t.checkpoint_generation, 1)
        self.assertEqual(t.pre_ledger_digest, self.cp1.ledger_digest)

    def test_p5_02_stale_or_invalid_checkpoint_cannot_issue_token(self):
        bad = dataclasses.replace(self.cp1, tag="00" * 32)
        with self.assertRaises(PermissionError):
            self.use.issue_token(self.p, bad, trusted_min_generation=1, token_nonce="bad")
        with self.assertRaises(PermissionError):
            self.use.issue_token(self.p, self.cp1, trusted_min_generation=2, token_nonce="stale")

    def test_p5_03_token_binds_exact_permit_nonce_and_semantics(self):
        t = self.token("permit-bind")
        p2 = self.permits.issue(reviews(), verifier(), signals(), nonce="p2")
        d = self.use.consume(t, p2, reviews(), verifier(), signals())
        self.assertEqual(d.state, "DENIED")

    def test_p5_04_token_binds_checkpoint_digest_and_generation(self):
        t = self.token("checkpoint-bind")
        changed = dataclasses.replace(t, checkpoint_generation=2)
        self.assertEqual(self.use.consume(changed, self.p, reviews(), verifier(), signals()).state, "DENIED")
        changed2 = dataclasses.replace(t, checkpoint_digest="0" * 64)
        self.assertEqual(self.use.consume(changed2, self.p, reviews(), verifier(), signals()).state, "DENIED")

    def test_p5_05_token_binds_preconsumption_ledger_digest(self):
        t = dataclasses.replace(self.token("digest-bind"), pre_ledger_digest="0" * 64)
        self.assertEqual(self.use.consume(t, self.p, reviews(), verifier(), signals()).state, "DENIED")

    def test_p5_06_ledger_mutation_after_token_before_consumption_denied(self):
        t = self.token("mutate")
        con = sqlite3.connect(self.db)
        con.execute("UPDATE permit_ledger SET binding_digest=? WHERE nonce='p1'", ("a" * 64,))
        con.commit(); con.close()
        self.assertEqual(self.use.consume(t, self.p, reviews(), verifier(), signals()).state, "DENIED")

    def test_p5_07_consumed_status_change_after_token_cannot_reuse_stale_token(self):
        t = self.token("status-change")
        self.permits.consume(self.p, reviews(), verifier(), signals())
        self.assertEqual(self.use.consume(t, self.p, reviews(), verifier(), signals()).state, "DENIED")

    def test_p5_08_unrelated_permit_issue_invalidates_whole_ledger_token(self):
        t = self.token("whole-ledger")
        self.permits.issue(reviews(), verifier(), signals(), nonce="other")
        self.assertEqual(self.use.consume(t, self.p, reviews(), verifier(), signals()).state, "DENIED")

    def test_p5_09_epoch_change_after_token_invalidates_token(self):
        t = self.token("epoch-change")
        self.permits.advance_epoch()
        self.assertEqual(self.use.consume(t, self.p, reviews(), verifier(), signals()).state, "DENIED")

    def test_p5_10_forged_or_mutated_use_time_token_denied(self):
        t = self.token("forge")
        forged = dataclasses.replace(t, tag="ff" * 32)
        mutated = dataclasses.replace(t, token_nonce="different")
        self.assertEqual(self.use.consume(forged, self.p, reviews(), verifier(), signals()).state, "DENIED")
        self.assertEqual(self.use.consume(mutated, self.p, reviews(), verifier(), signals()).state, "DENIED")

    def test_p5_11_exact_token_replay_after_consumption_denied(self):
        t = self.token("replay")
        first = self.consume(t)
        second = self.consume(t)
        self.assertEqual(first.state, "CONVERGED_PASS")
        self.assertEqual(second.state, "DENIED")

    def test_p5_12_two_consumers_race_same_token_at_most_one_transition(self):
        t = self.token("race")
        a = UseTimeCheckpointAuthority(self.db, PERMIT_KEY, INTEGRITY_KEY, TOKEN_KEY)
        b = UseTimeCheckpointAuthority(self.db, PERMIT_KEY, INTEGRITY_KEY, TOKEN_KEY)
        out = []
        lock = threading.Lock()
        def run(auth):
            d = auth.consume(t, self.p, reviews(), verifier(), signals())
            with lock:
                out.append(d.state)
        x = threading.Thread(target=run, args=(a,)); y = threading.Thread(target=run, args=(b,))
        x.start(); y.start(); x.join(); y.join()
        self.assertEqual(out.count("CONVERGED_PASS"), 1)
        self.assertEqual(out.count("DENIED"), 1)

    def test_p5_13_success_records_durable_pending_reconciliation(self):
        d = self.consume(self.token("pending"))
        self.assertEqual(d.state, "CONVERGED_PASS")
        self.assertEqual(d.reconciliation_status, "PENDING")
        self.assertEqual(self.use.reconciliation_status(d.reconciliation_id), "PENDING")

    def test_p5_14_pending_reconciliation_survives_restart(self):
        d = self.consume(self.token("restart-pending"))
        restarted = UseTimeCheckpointAuthority(self.db, PERMIT_KEY, INTEGRITY_KEY, TOKEN_KEY)
        self.assertEqual(restarted.reconciliation_status(d.reconciliation_id), "PENDING")

    def test_p5_15_restart_or_old_positive_checkpoint_does_not_silently_settle(self):
        d = self.consume(self.token("no-auto-settle"))
        restarted = UseTimeCheckpointAuthority(self.db, PERMIT_KEY, INTEGRITY_KEY, TOKEN_KEY)
        self.assertFalse(restarted.settle_reconciliation(d.reconciliation_id, self.cp1, trusted_min_generation=1))
        self.assertEqual(restarted.reconciliation_status(d.reconciliation_id), "PENDING")

    def test_p5_16_same_generation_postconsumption_checkpoint_cannot_settle(self):
        d = self.consume(self.token("same-gen"))
        cp_same = self.integrity.issue_checkpoint(1)
        self.assertFalse(self.use.settle_reconciliation(d.reconciliation_id, cp_same, trusted_min_generation=1))
        self.assertEqual(self.use.reconciliation_status(d.reconciliation_id), "PENDING")

    def test_p5_17_wrong_digest_higher_generation_checkpoint_cannot_settle(self):
        d = self.consume(self.token("wrong-post"))
        cp2 = self.checkpoint_after_consumption(2)
        wrong = dataclasses.replace(cp2, ledger_digest="0" * 64)
        self.assertFalse(self.use.settle_reconciliation(d.reconciliation_id, wrong, trusted_min_generation=2))
        self.assertEqual(self.use.reconciliation_status(d.reconciliation_id), "PENDING")

    def test_p5_18_exact_higher_generation_post_checkpoint_settles_once(self):
        d = self.consume(self.token("settle"))
        cp2 = self.checkpoint_after_consumption(2)
        self.assertTrue(self.use.settle_reconciliation(d.reconciliation_id, cp2, trusted_min_generation=2))
        self.assertEqual(self.use.reconciliation_status(d.reconciliation_id), "SETTLED")
        self.assertFalse(self.use.settle_reconciliation(d.reconciliation_id, cp2, trusted_min_generation=2))

    def test_p5_19_models_reviewers_have_no_control_or_production_authority(self):
        d = self.consume(self.token("authority"))
        self.assertFalse(hasattr(reviews()[0], "settle_reconciliation"))
        self.assertFalse(d.reviewer_generated_authority)
        self.assertFalse(d.production_authority)

    def test_p5_20_clean_new_permit_live_after_reconciled_cycle(self):
        d1 = self.consume(self.token("cycle1"))
        cp2 = self.checkpoint_after_consumption(2)
        self.assertTrue(self.use.settle_reconciliation(d1.reconciliation_id, cp2, trusted_min_generation=2))
        p2 = self.permits.issue(reviews(), verifier(), signals(), nonce="fresh")
        cp3 = self.integrity.issue_checkpoint(3, previous=cp2)
        t2 = self.use.issue_token(p2, cp3, trusted_min_generation=3, token_nonce="cycle2")
        d2 = self.use.consume(t2, p2, reviews(), verifier(), signals())
        self.assertEqual(d2.state, "CONVERGED_PASS")
        self.assertEqual(d2.reconciliation_status, "PENDING")
        self.assertFalse(d2.production_authority)


if __name__ == "__main__":
    unittest.main()
