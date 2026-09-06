import dataclasses
import hashlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_permit_ledger_integrity import LedgerCheckpoint, PermitLedgerIntegrityAuthority, SCOPE

CASE = "EXP-I-P4-CASE"
PERMIT_KEY = b"exp-i-pilot4-permit-key"
INTEGRITY_KEY = b"exp-i-pilot4-integrity-key"


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


def sqlite_backup(src_path, dst_path):
    src = sqlite3.connect(src_path)
    dst = sqlite3.connect(dst_path)
    try:
        src.backup(dst)
    finally:
        dst.close(); src.close()


class ExpIPilot4PermitLedgerIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "permit.db")
        self.permits = DurableConvergencePermitAuthority(self.db, PERMIT_KEY)
        self.integrity = PermitLedgerIntegrityAuthority(self.db, INTEGRITY_KEY)
        self.p = self.permits.issue(reviews(), verifier(), signals(), nonce="p1")
        self.cp1 = self.integrity.issue_checkpoint(1)

    def tearDown(self):
        self.tmp.cleanup()

    def sql(self, statement, params=()):
        con = sqlite3.connect(self.db)
        try:
            con.execute(statement, params)
            con.commit()
        finally:
            con.close()

    def current_checkpoint2(self):
        self.permits.consume(self.p, reviews(), verifier(), signals())
        return self.integrity.issue_checkpoint(2, previous=self.cp1)

    def test_p4_01_clean_current_database_and_checkpoint_verify(self):
        d = self.integrity.verify_checkpoint(self.cp1, trusted_min_generation=1)
        self.assertTrue(d.valid)
        self.assertFalse(d.production_authority)

    def test_p4_02_consumed_status_resurrection_detected(self):
        cp2 = self.current_checkpoint2()
        self.sql("UPDATE permit_ledger SET status='ISSUED' WHERE nonce='p1'")
        self.assertFalse(self.integrity.verify_checkpoint(cp2, trusted_min_generation=2, previous=self.cp1).valid)

    def test_p4_03_permit_row_deletion_detected(self):
        self.sql("DELETE FROM permit_ledger WHERE nonce='p1'")
        self.assertFalse(self.integrity.verify_checkpoint(self.cp1, trusted_min_generation=1).valid)

    def test_p4_04_syntactically_valid_payload_rewrite_detected(self):
        con = sqlite3.connect(self.db)
        payload = json.loads(con.execute("SELECT payload_json FROM permit_ledger WHERE nonce='p1'").fetchone()[0])
        payload["case_id"] = "OTHER"
        con.execute("UPDATE permit_ledger SET payload_json=? WHERE nonce='p1'", (json.dumps(payload, sort_keys=True),))
        con.commit(); con.close()
        self.assertFalse(self.integrity.verify_checkpoint(self.cp1, trusted_min_generation=1).valid)

    def test_p4_05_binding_digest_rewrite_detected(self):
        self.sql("UPDATE permit_ledger SET binding_digest=? WHERE nonce='p1'", ("f" * 64,))
        self.assertFalse(self.integrity.verify_checkpoint(self.cp1, trusted_min_generation=1).valid)

    def test_p4_06_authority_epoch_lowering_detected(self):
        self.permits.advance_epoch()
        cp2 = self.integrity.issue_checkpoint(2, previous=self.cp1)
        self.sql("UPDATE authority_meta SET issuance_epoch=1 WHERE singleton=1")
        self.assertFalse(self.integrity.verify_checkpoint(cp2, trusted_min_generation=2, previous=self.cp1).valid)

    def test_p4_07_coherent_db_rollback_with_old_checkpoint_below_minimum_rejected(self):
        old = str(Path(self.tmp.name) / "old.db")
        sqlite_backup(self.db, old)
        self.permits.consume(self.p, reviews(), verifier(), signals())
        self.integrity.issue_checkpoint(2, previous=self.cp1)
        sqlite_backup(old, self.db)
        d = self.integrity.verify_checkpoint(self.cp1, trusted_min_generation=2)
        self.assertFalse(d.valid)
        self.assertIn("checkpoint below trusted minimum generation", d.reasons)

    def test_p4_08_stale_database_with_current_checkpoint_rejected(self):
        old = str(Path(self.tmp.name) / "old2.db")
        sqlite_backup(self.db, old)
        cp2 = self.current_checkpoint2()
        sqlite_backup(old, self.db)
        self.assertFalse(self.integrity.verify_checkpoint(cp2, trusted_min_generation=2, previous=self.cp1).valid)

    def test_p4_09_current_database_with_stale_checkpoint_rejected(self):
        self.current_checkpoint2()
        self.assertFalse(self.integrity.verify_checkpoint(self.cp1, trusted_min_generation=2).valid)

    def test_p4_10_forged_checkpoint_authentication_rejected(self):
        forged = dataclasses.replace(self.cp1, tag="00" * 32)
        self.assertFalse(self.integrity.verify_checkpoint(forged, trusted_min_generation=1).valid)

    def test_p4_11_checkpoint_field_mutation_after_signing_rejected(self):
        changed = dataclasses.replace(self.cp1, ledger_digest="0" * 64)
        self.assertFalse(self.integrity.verify_checkpoint(changed, trusted_min_generation=1).valid)

    def test_p4_12_wrong_checkpoint_scope_rejected(self):
        wrong = dataclasses.replace(self.cp1, scope="OTHER")
        self.assertFalse(self.integrity.verify_checkpoint(wrong, trusted_min_generation=1).valid)

    def test_p4_13_checkpoint_predecessor_mutation_rejected(self):
        cp2 = self.current_checkpoint2()
        altered_prev = dataclasses.replace(self.cp1, tag="11" * 32)
        d = self.integrity.verify_checkpoint(cp2, trusted_min_generation=2, previous=altered_prev)
        self.assertFalse(d.valid)
        self.assertIn("invalid predecessor authentication", d.reasons)

    def test_p4_14_missing_external_checkpoint_fails_closed(self):
        d = self.integrity.verify_checkpoint(None, trusted_min_generation=1)
        self.assertFalse(d.valid)
        self.assertIn("missing external checkpoint", d.reasons)

    def test_p4_15_storage_rowid_reordering_does_not_change_canonical_digest(self):
        p2 = self.permits.issue(reviews(), verifier(), signals(), nonce="p2")
        before = self.integrity.ledger_digest()
        con = sqlite3.connect(self.db)
        row = con.execute("SELECT nonce,binding_digest,payload_json,status FROM permit_ledger WHERE nonce='p1'").fetchone()
        con.execute("DELETE FROM permit_ledger WHERE nonce='p1'")
        con.execute("INSERT INTO permit_ledger(nonce,binding_digest,payload_json,status) VALUES(?,?,?,?)", row)
        con.commit(); con.close()
        after = self.integrity.ledger_digest()
        self.assertEqual(before, after)
        self.assertEqual(p2.nonce, "p2")

    def test_p4_16_coherent_local_rewrite_without_integrity_key_rejected(self):
        con = sqlite3.connect(self.db)
        payload = json.loads(con.execute("SELECT payload_json FROM permit_ledger WHERE nonce='p1'").fetchone()[0])
        payload["nonce"] = "evil-semantic-value"
        normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        local_digest = hashlib.sha256(normalized.encode()).hexdigest()
        con.execute("UPDATE permit_ledger SET payload_json=?, binding_digest=? WHERE nonce='p1'", (normalized, local_digest))
        con.commit(); con.close()
        self.assertFalse(self.integrity.verify_checkpoint(self.cp1, trusted_min_generation=1).valid)

    def test_p4_17_old_valid_checkpoint_cannot_authorize_after_minimum_advances(self):
        self.current_checkpoint2()
        self.assertFalse(self.integrity.verify_checkpoint(self.cp1, trusted_min_generation=2).valid)

    def test_p4_18_repeated_restart_same_tampered_bundle_never_promotes(self):
        self.sql("UPDATE permit_ledger SET binding_digest=? WHERE nonce='p1'", ("a" * 64,))
        results = [PermitLedgerIntegrityAuthority(self.db, INTEGRITY_KEY).verify_checkpoint(self.cp1, trusted_min_generation=1).valid for _ in range(3)]
        self.assertEqual(results, [False, False, False])

    def test_p4_19_reviewer_model_surface_cannot_mint_trusted_generation(self):
        self.assertFalse(hasattr(reviews()[0], "checkpoint_generation"))
        self.assertFalse(hasattr(self.integrity, "advance_trusted_minimum"))
        self.assertFalse(self.integrity.verify_checkpoint(self.cp1, trusted_min_generation=1).reviewer_generated_authority)

    def test_p4_20_clean_higher_generation_checkpoint_liveness(self):
        cp2 = self.current_checkpoint2()
        d = PermitLedgerIntegrityAuthority(self.db, INTEGRITY_KEY).verify_checkpoint(cp2, trusted_min_generation=2, previous=self.cp1)
        self.assertTrue(d.valid)
        self.assertFalse(d.production_authority)


if __name__ == "__main__":
    unittest.main()
