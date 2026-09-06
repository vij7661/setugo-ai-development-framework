import dataclasses
import sqlite3
import tempfile
import unittest
from pathlib import Path

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_composite_integrity import CompositeIntegrityAuthority
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_permit_ledger_integrity import PermitLedgerIntegrityAuthority
from exp_i_reconciliation_integrity import ReconciliationIntegrityAuthority
from exp_i_use_time_checkpoint import UseTimeCheckpointAuthority

CASE = "EXP-I-P7-CASE"
PERMIT_KEY = b"exp-i-pilot7-permit-key"
PERMIT_INTEGRITY_KEY = b"exp-i-pilot7-permit-integrity-key"
RECON_INTEGRITY_KEY = b"exp-i-pilot7-reconciliation-integrity-key"
TOKEN_KEY = b"exp-i-pilot7-token-key"
COMPOSITE_KEY = b"exp-i-pilot7-composite-key"


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


class ExpIPilot7CompositeIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "p7.db")
        self.permits = DurableConvergencePermitAuthority(self.db, PERMIT_KEY)
        self.permit_integrity = PermitLedgerIntegrityAuthority(self.db, PERMIT_INTEGRITY_KEY)
        self.use = UseTimeCheckpointAuthority(self.db, PERMIT_KEY, PERMIT_INTEGRITY_KEY, TOKEN_KEY)
        self.recon_integrity = ReconciliationIntegrityAuthority(self.db, RECON_INTEGRITY_KEY)
        self.composite = CompositeIntegrityAuthority(self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY)
        self.permit = self.permits.issue(reviews(), verifier(), signals(), nonce="permit-1")
        self.permit_cp1 = self.permit_integrity.issue_checkpoint(1)
        self.recon_cp1 = self.recon_integrity.issue_checkpoint(1)
        self.composite_cp1 = self.composite.issue_checkpoint(1)

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

    def consume_to_pending(self, token_nonce="token-1"):
        token = self.use.issue_token(self.permit, self.permit_cp1, trusted_min_generation=1, token_nonce=token_nonce)
        return self.use.consume(token, self.permit, reviews(), verifier(), signals())

    def settle_pending(self, decision):
        permit_cp2 = self.permit_integrity.issue_checkpoint(2, previous=self.permit_cp1)
        self.assertTrue(self.use.settle_reconciliation(decision.reconciliation_id, permit_cp2, trusted_min_generation=2))
        return permit_cp2

    def test_p7_01_clean_current_pair_verifies(self):
        d = self.composite.verify_checkpoint(self.composite_cp1, trusted_min_generation=1)
        self.assertTrue(d.valid)
        self.assertFalse(d.production_authority)

    def test_p7_02_permit_mutation_invalidates_composite(self):
        self.sql("UPDATE permit_ledger SET binding_digest=? WHERE nonce='permit-1'", ("a" * 64,))
        self.assertFalse(self.composite.verify_checkpoint(self.composite_cp1, trusted_min_generation=1).valid)

    def test_p7_03_reconciliation_mutation_invalidates_composite(self):
        decision = self.consume_to_pending()
        cp2 = self.composite.issue_checkpoint(2, previous=self.composite_cp1)
        self.sql("UPDATE convergence_reconciliation SET post_ledger_digest=? WHERE reconciliation_id=?", ("b" * 64, decision.reconciliation_id))
        self.assertFalse(self.composite.verify_checkpoint(cp2, trusted_min_generation=2, previous=self.composite_cp1).valid)

    def test_p7_04_both_ledgers_change_after_issue_invalidates_old_composite(self):
        self.consume_to_pending()
        self.permits.advance_epoch()
        self.assertFalse(self.composite.verify_checkpoint(self.composite_cp1, trusted_min_generation=1).valid)

    def test_p7_05_stale_permit_side_with_current_reconciliation_cannot_match(self):
        old_permit_digest = self.composite_cp1.permit_ledger_digest
        self.consume_to_pending()
        current = self.composite.issue_checkpoint(2, previous=self.composite_cp1)
        mixed = dataclasses.replace(current, permit_ledger_digest=old_permit_digest)
        self.assertFalse(self.composite.verify_checkpoint(mixed, trusted_min_generation=2, previous=self.composite_cp1).valid)

    def test_p7_06_current_permit_side_with_stale_reconciliation_cannot_match(self):
        old_recon_digest = self.composite_cp1.reconciliation_digest
        self.consume_to_pending()
        current = self.composite.issue_checkpoint(2, previous=self.composite_cp1)
        mixed = dataclasses.replace(current, reconciliation_digest=old_recon_digest)
        self.assertFalse(self.composite.verify_checkpoint(mixed, trusted_min_generation=2, previous=self.composite_cp1).valid)

    def test_p7_07_old_permit_root_plus_new_recon_root_cannot_manufacture_composite(self):
        self.consume_to_pending()
        recon_cp2 = self.recon_integrity.issue_checkpoint(2, previous=self.recon_cp1)
        mixed = dataclasses.replace(self.composite_cp1, reconciliation_digest=recon_cp2.reconciliation_digest)
        self.assertFalse(self.composite.verify_checkpoint(mixed, trusted_min_generation=1).valid)

    def test_p7_08_new_permit_root_plus_old_recon_root_cannot_manufacture_composite(self):
        self.consume_to_pending()
        permit_cp2 = self.permit_integrity.issue_checkpoint(2, previous=self.permit_cp1)
        mixed = dataclasses.replace(self.composite_cp1, permit_ledger_digest=permit_cp2.ledger_digest)
        self.assertFalse(self.composite.verify_checkpoint(mixed, trusted_min_generation=1).valid)

    def test_p7_09_permit_digest_field_substitution_rejected(self):
        changed = dataclasses.replace(self.composite_cp1, permit_ledger_digest="0" * 64)
        self.assertFalse(self.composite.verify_checkpoint(changed, trusted_min_generation=1).valid)

    def test_p7_10_reconciliation_digest_field_substitution_rejected(self):
        changed = dataclasses.replace(self.composite_cp1, reconciliation_digest="0" * 64)
        self.assertFalse(self.composite.verify_checkpoint(changed, trusted_min_generation=1).valid)

    def test_p7_11_permit_authority_epoch_substitution_rejected(self):
        changed = dataclasses.replace(self.composite_cp1, permit_authority_epoch=999)
        self.assertFalse(self.composite.verify_checkpoint(changed, trusted_min_generation=1).valid)

    def test_p7_12_forged_or_mutated_composite_tag_rejected(self):
        forged = dataclasses.replace(self.composite_cp1, tag="00" * 32)
        self.assertFalse(self.composite.verify_checkpoint(forged, trusted_min_generation=1).valid)

    def test_p7_13_wrong_composite_scope_rejected(self):
        wrong = dataclasses.replace(self.composite_cp1, scope="OTHER")
        self.assertFalse(self.composite.verify_checkpoint(wrong, trusted_min_generation=1).valid)

    def test_p7_14_predecessor_substitution_or_unauthenticated_predecessor_rejected(self):
        self.consume_to_pending()
        cp2 = self.composite.issue_checkpoint(2, previous=self.composite_cp1)
        bad_prev = dataclasses.replace(self.composite_cp1, tag="11" * 32)
        self.assertFalse(self.composite.verify_checkpoint(cp2, trusted_min_generation=2, previous=bad_prev).valid)
        changed = dataclasses.replace(cp2, previous_checkpoint_digest="0" * 64)
        self.assertFalse(self.composite.verify_checkpoint(changed, trusted_min_generation=2, previous=self.composite_cp1).valid)

    def test_p7_15_old_valid_composite_rejected_after_trusted_minimum_advances(self):
        self.consume_to_pending()
        self.composite.issue_checkpoint(2, previous=self.composite_cp1)
        d = self.composite.verify_checkpoint(self.composite_cp1, trusted_min_generation=2)
        self.assertFalse(d.valid)
        self.assertIn("composite checkpoint below trusted minimum", d.reasons)

    def test_p7_16_repeated_restart_same_mixed_pair_never_promotes(self):
        self.consume_to_pending()
        current = self.composite.issue_checkpoint(2, previous=self.composite_cp1)
        mixed = dataclasses.replace(current, reconciliation_digest=self.composite_cp1.reconciliation_digest)
        results = [CompositeIntegrityAuthority(self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY).verify_checkpoint(mixed, trusted_min_generation=2, previous=self.composite_cp1).valid for _ in range(3)]
        self.assertEqual(results, [False, False, False])

    def test_p7_17_side_root_validity_alone_insufficient_without_composite(self):
        self.assertTrue(self.permit_integrity.verify_checkpoint(self.permit_cp1, trusted_min_generation=1).valid)
        self.assertTrue(self.recon_integrity.verify_checkpoint(self.recon_cp1, trusted_min_generation=1).valid)
        self.assertFalse(self.composite.verify_checkpoint(None, trusted_min_generation=1).valid)

    def test_p7_18_composite_verification_has_zero_model_or_production_authority(self):
        d = self.composite.verify_checkpoint(self.composite_cp1, trusted_min_generation=1)
        self.assertFalse(d.reviewer_generated_authority)
        self.assertFalse(d.production_authority)
        self.assertFalse(hasattr(reviews()[0], "issue_composite_checkpoint"))

    def test_p7_19_coordinated_post_consumption_reconciliation_advances_composite(self):
        decision = self.consume_to_pending()
        self.settle_pending(decision)
        cp2 = self.composite.issue_checkpoint(2, previous=self.composite_cp1)
        self.assertTrue(self.composite.verify_checkpoint(cp2, trusted_min_generation=2, previous=self.composite_cp1).valid)

    def test_p7_20_clean_higher_generation_composite_liveness_after_prior_cycle(self):
        decision = self.consume_to_pending("cycle-token")
        self.settle_pending(decision)
        cp2 = self.composite.issue_checkpoint(2, previous=self.composite_cp1)
        restarted = CompositeIntegrityAuthority(self.db, PERMIT_INTEGRITY_KEY, RECON_INTEGRITY_KEY, COMPOSITE_KEY)
        d = restarted.verify_checkpoint(cp2, trusted_min_generation=2, previous=self.composite_cp1)
        self.assertTrue(d.valid)
        self.assertFalse(d.production_authority)


if __name__ == "__main__":
    unittest.main()
