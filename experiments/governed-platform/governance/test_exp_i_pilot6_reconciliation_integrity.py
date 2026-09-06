import dataclasses
import sqlite3
import tempfile
import unittest
from pathlib import Path

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_permit_ledger_integrity import PermitLedgerIntegrityAuthority
from exp_i_reconciliation_integrity import ReconciliationIntegrityAuthority
from exp_i_use_time_checkpoint import UseTimeCheckpointAuthority

CASE = "EXP-I-P6-CASE"
PERMIT_KEY = b"exp-i-pilot6-permit-key"
LEDGER_KEY = b"exp-i-pilot6-ledger-key"
TOKEN_KEY = b"exp-i-pilot6-token-key"
RECON_KEY = b"exp-i-pilot6-reconciliation-key"


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


class ExpIPilot6ReconciliationIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "p6.db")
        self.permits = DurableConvergencePermitAuthority(self.db, PERMIT_KEY)
        self.ledger = PermitLedgerIntegrityAuthority(self.db, LEDGER_KEY)
        self.use = UseTimeCheckpointAuthority(self.db, PERMIT_KEY, LEDGER_KEY, TOKEN_KEY)
        self.recon = ReconciliationIntegrityAuthority(self.db, RECON_KEY)
        self.permit = self.permits.issue(reviews(), verifier(), signals(), nonce="permit-1")
        self.ledger_cp1 = self.ledger.issue_checkpoint(1)
        token = self.use.issue_token(self.permit, self.ledger_cp1, trusted_min_generation=1, token_nonce="token-1")
        self.decision = self.use.consume(token, self.permit, reviews(), verifier(), signals())
        self.rid = self.decision.reconciliation_id
        self.recon_cp1 = self.recon.issue_checkpoint(1)

    def tearDown(self):
        self.tmp.cleanup()

    def sql(self, stmt, params=()):
        con = sqlite3.connect(self.db)
        try:
            con.execute("PRAGMA ignore_check_constraints=ON")
            con.execute(stmt, params)
            con.commit()
        finally:
            con.close()

    def settle(self):
        ledger_cp2 = self.ledger.issue_checkpoint(2, previous=self.ledger_cp1)
        self.assertTrue(self.use.settle_reconciliation(self.rid, ledger_cp2, trusted_min_generation=2))
        return ledger_cp2

    def test_p6_01_clean_pending_reconciliation_and_checkpoint_verify(self):
        d = self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=1)
        self.assertTrue(d.valid)
        self.assertFalse(d.production_authority)

    def test_p6_02_pending_to_settled_local_rewrite_detected(self):
        self.sql("UPDATE convergence_reconciliation SET status='SETTLED', settlement_checkpoint_digest='forged' WHERE reconciliation_id=?", (self.rid,))
        self.assertFalse(self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=1).valid)

    def test_p6_03_settled_to_pending_local_rollback_detected(self):
        self.settle()
        cp2 = self.recon.issue_checkpoint(2, previous=self.recon_cp1)
        self.sql("UPDATE convergence_reconciliation SET status='PENDING', settlement_checkpoint_digest=NULL WHERE reconciliation_id=?", (self.rid,))
        self.assertFalse(self.recon.verify_checkpoint(cp2, trusted_min_generation=2, previous=self.recon_cp1).valid)

    def test_p6_04_reconciliation_row_deletion_detected(self):
        self.sql("DELETE FROM convergence_reconciliation WHERE reconciliation_id=?", (self.rid,))
        self.assertFalse(self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=1).valid)

    def test_p6_05_post_ledger_digest_substitution_detected(self):
        self.sql("UPDATE convergence_reconciliation SET post_ledger_digest=? WHERE reconciliation_id=?", ("0" * 64, self.rid))
        self.assertFalse(self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=1).valid)

    def test_p6_06_pre_ledger_digest_substitution_detected(self):
        self.sql("UPDATE convergence_reconciliation SET pre_ledger_digest=? WHERE reconciliation_id=?", ("1" * 64, self.rid))
        self.assertFalse(self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=1).valid)

    def test_p6_07_checkpoint_generation_lowering_detected(self):
        self.sql("UPDATE convergence_reconciliation SET checkpoint_generation=0 WHERE reconciliation_id=?", (self.rid,))
        self.assertFalse(self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=1).valid)

    def test_p6_08_checkpoint_generation_inflation_detected(self):
        self.sql("UPDATE convergence_reconciliation SET checkpoint_generation=999 WHERE reconciliation_id=?", (self.rid,))
        self.assertFalse(self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=1).valid)

    def test_p6_09_permit_nonce_substitution_detected(self):
        self.sql("UPDATE convergence_reconciliation SET permit_nonce='other' WHERE reconciliation_id=?", (self.rid,))
        self.assertFalse(self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=1).valid)

    def test_p6_10_token_nonce_substitution_detected(self):
        self.sql("UPDATE convergence_reconciliation SET token_nonce='other' WHERE reconciliation_id=?", (self.rid,))
        self.assertFalse(self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=1).valid)

    def test_p6_11_settlement_checkpoint_digest_substitution_detected(self):
        self.settle()
        cp2 = self.recon.issue_checkpoint(2, previous=self.recon_cp1)
        self.sql("UPDATE convergence_reconciliation SET settlement_checkpoint_digest='evil' WHERE reconciliation_id=?", (self.rid,))
        self.assertFalse(self.recon.verify_checkpoint(cp2, trusted_min_generation=2, previous=self.recon_cp1).valid)

    def test_p6_12_coherent_full_row_rewrite_without_reconciliation_key_fails(self):
        self.sql("UPDATE convergence_reconciliation SET post_ledger_digest=?, checkpoint_generation=77 WHERE reconciliation_id=?", ("f" * 64, self.rid))
        self.assertFalse(self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=1).valid)

    def test_p6_13_old_valid_checkpoint_rejected_after_trusted_minimum_advances(self):
        self.settle()
        self.recon.issue_checkpoint(2, previous=self.recon_cp1)
        d = self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=2)
        self.assertFalse(d.valid)
        self.assertIn("reconciliation checkpoint below trusted minimum", d.reasons)

    def test_p6_14_stale_reconciliation_state_plus_current_checkpoint_rejected(self):
        self.settle()
        cp2 = self.recon.issue_checkpoint(2, previous=self.recon_cp1)
        self.sql("UPDATE convergence_reconciliation SET status='PENDING', settlement_checkpoint_digest=NULL WHERE reconciliation_id=?", (self.rid,))
        self.assertFalse(self.recon.verify_checkpoint(cp2, trusted_min_generation=2, previous=self.recon_cp1).valid)

    def test_p6_15_current_reconciliation_state_plus_stale_checkpoint_rejected(self):
        self.settle()
        self.recon.issue_checkpoint(2, previous=self.recon_cp1)
        self.assertFalse(self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=2).valid)

    def test_p6_16_forged_or_mutated_reconciliation_checkpoint_rejected(self):
        forged = dataclasses.replace(self.recon_cp1, tag="00" * 32)
        changed = dataclasses.replace(self.recon_cp1, reconciliation_digest="0" * 64)
        self.assertFalse(self.recon.verify_checkpoint(forged, trusted_min_generation=1).valid)
        self.assertFalse(self.recon.verify_checkpoint(changed, trusted_min_generation=1).valid)

    def test_p6_17_wrong_scope_or_predecessor_rejected(self):
        wrong_scope = dataclasses.replace(self.recon_cp1, scope="OTHER")
        self.assertFalse(self.recon.verify_checkpoint(wrong_scope, trusted_min_generation=1).valid)
        self.settle()
        cp2 = self.recon.issue_checkpoint(2, previous=self.recon_cp1)
        bad_prev = dataclasses.replace(self.recon_cp1, tag="11" * 32)
        self.assertFalse(self.recon.verify_checkpoint(cp2, trusted_min_generation=2, previous=bad_prev).valid)

    def test_p6_18_repeated_restart_tampered_state_never_promotes(self):
        self.sql("UPDATE convergence_reconciliation SET post_ledger_digest=? WHERE reconciliation_id=?", ("a" * 64, self.rid))
        results = [ReconciliationIntegrityAuthority(self.db, RECON_KEY).verify_checkpoint(self.recon_cp1, trusted_min_generation=1).valid for _ in range(3)]
        self.assertEqual(results, [False, False, False])

    def test_p6_19_reviewers_models_have_no_reconciliation_checkpoint_authority(self):
        d = self.recon.verify_checkpoint(self.recon_cp1, trusted_min_generation=1)
        self.assertFalse(hasattr(reviews()[0], "issue_reconciliation_checkpoint"))
        self.assertFalse(d.reviewer_generated_authority)
        self.assertFalse(d.production_authority)

    def test_p6_20_clean_higher_generation_settled_checkpoint_liveness(self):
        self.settle()
        cp2 = self.recon.issue_checkpoint(2, previous=self.recon_cp1)
        d = ReconciliationIntegrityAuthority(self.db, RECON_KEY).verify_checkpoint(cp2, trusted_min_generation=2, previous=self.recon_cp1)
        self.assertTrue(d.valid)
        self.assertFalse(d.production_authority)


if __name__ == "__main__":
    unittest.main()
