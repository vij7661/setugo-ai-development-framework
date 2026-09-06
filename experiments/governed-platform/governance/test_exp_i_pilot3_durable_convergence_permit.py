import dataclasses
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority

CASE = "EXP-I-P3-CASE"
KEY = b"exp-i-pilot3-test-key"


def r(reviewer_id, primary="CODE DEFECT", scope=("CODE",), case_id=CASE):
    return ReviewClaim(reviewer_id, case_id, primary, tuple(scope))


def reviews(primary="CODE DEFECT", scope=("CODE",), case_id=CASE):
    return [r("r1", primary, scope, case_id), r("r2", primary, scope, case_id), r("r3", primary, scope, case_id)]


def v(primary="CODE DEFECT", scope=("CODE",), case_id=CASE, issuer="platform-independent-verifier"):
    return VerificationArtifact(issuer, True, True, case_id, primary, tuple(scope))


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


class ExpIPilot3DurablePermitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / "permit.db")
        self.auth = DurableConvergencePermitAuthority(self.db, KEY)

    def tearDown(self):
        self.tmp.cleanup()

    def restart(self):
        return DurableConvergencePermitAuthority(self.db, KEY)

    def issue(self, nonce="n1", rs=None, ver=None, sig=None):
        return self.auth.issue(rs or reviews(), ver or v(), sig or signals(), nonce=nonce)

    def test_p3_01_issue_persists_nonce_binding_before_return(self):
        p = self.issue("persist")
        con = sqlite3.connect(self.db)
        row = con.execute("SELECT status,binding_digest FROM permit_ledger WHERE nonce='persist'").fetchone()
        con.close()
        self.assertEqual(row[0], "ISSUED")
        self.assertTrue(row[1])
        self.assertEqual(p.nonce, "persist")

    def test_p3_02_unconsumed_permit_survives_restart_and_consumes_once(self):
        p = self.issue("restart-live")
        d = self.restart().consume(p, reviews(), v(), signals())
        self.assertEqual(d.state, "CONVERGED_PASS")

    def test_p3_03_consumed_permit_stays_denied_after_restart(self):
        p = self.issue("consumed")
        self.assertEqual(self.auth.consume(p, reviews(), v(), signals()).state, "CONVERGED_PASS")
        self.assertEqual(self.restart().consume(p, reviews(), v(), signals()).state, "DENIED")

    def test_p3_04_repeated_restart_cannot_resurrect_consumed(self):
        p = self.issue("repeat")
        self.auth.consume(p, reviews(), v(), signals())
        self.assertTrue(all(self.restart().consume(p, reviews(), v(), signals()).state == "DENIED" for _ in range(3)))

    def test_p3_05_nonce_semantic_rebinding_denied_after_restart(self):
        self.issue("bind")
        other = self.restart()
        with self.assertRaises(PermissionError):
            other.issue(reviews("TEST DEFECT", ("TEST",)), v("TEST DEFECT", ("TEST",)), signals(), nonce="bind")

    def test_p3_06_exact_same_nonce_issue_is_idempotent_before_consumption(self):
        a = self.issue("idem")
        b = self.restart().issue(reviews(), v(), signals(), nonce="idem")
        self.assertEqual(a, b)

    def test_p3_07_forged_signature_denied_after_restart(self):
        p = dataclasses.replace(self.issue("forge"), signature="00" * 32)
        self.assertEqual(self.restart().consume(p, reviews(), v(), signals()).state, "DENIED")

    def test_p3_08_case_substitution_denied_after_restart(self):
        p = self.issue("case")
        self.assertEqual(self.restart().consume(p, reviews(case_id="OTHER"), v(case_id="OTHER"), signals()).state, "DENIED")

    def test_p3_09_class_substitution_denied_after_restart(self):
        p = self.issue("class")
        self.assertEqual(self.restart().consume(p, reviews("TEST DEFECT", ("TEST",)), v("TEST DEFECT", ("TEST",)), signals()).state, "DENIED")

    def test_p3_10_scope_substitution_denied_after_restart(self):
        p = self.issue("scope")
        rs = reviews("CODE DEFECT", ("CODE", "TEST"))
        ver = v("CODE DEFECT", ("CODE", "TEST"))
        self.assertEqual(self.restart().consume(p, rs, ver, signals()).state, "DENIED")

    def test_p3_11_verifier_substitution_denied_after_restart(self):
        p = self.issue("verifier")
        self.assertEqual(self.restart().consume(p, reviews(), v(issuer="other-verifier"), signals()).state, "DENIED")

    def test_p3_12_signal_substitution_denied_after_restart(self):
        p = self.issue("signals")
        self.assertEqual(self.restart().consume(p, reviews(), v(), signals(non_material_dissent=True)).state, "DENIED")

    def test_p3_13_epoch_advance_is_durable_and_invalidates_old_permit(self):
        p = self.issue("epoch")
        self.auth.advance_epoch()
        restarted = self.restart()
        self.assertEqual(restarted.issuance_epoch, 2)
        self.assertEqual(restarted.consume(p, reviews(), v(), signals()).state, "DENIED")

    def test_p3_14_stale_instance_cannot_consume_after_other_advances_epoch(self):
        p = self.issue("stale-instance")
        other = self.restart()
        other.advance_epoch()
        self.assertEqual(self.auth.consume(p, reviews(), v(), signals()).state, "DENIED")

    def test_p3_15_two_instances_race_one_permit_at_most_one_terminal(self):
        p = self.issue("race")
        a, b = self.restart(), self.restart()
        out = []
        lock = threading.Lock()
        def run(auth):
            d = auth.consume(p, reviews(), v(), signals())
            with lock:
                out.append(d.state)
        t1, t2 = threading.Thread(target=run, args=(a,)), threading.Thread(target=run, args=(b,))
        t1.start(); t2.start(); t1.join(); t2.join()
        self.assertEqual(out.count("CONVERGED_PASS"), 1)
        self.assertEqual(out.count("DENIED"), 1)

    def test_p3_16_rejected_attempt_does_not_consume_valid_permit(self):
        p = self.issue("reject-first")
        bad = self.auth.consume(p, reviews(), v(), signals(non_material_dissent=True))
        good = self.auth.consume(p, reviews(), v(), signals())
        self.assertEqual(bad.state, "DENIED")
        self.assertEqual(good.state, "CONVERGED_PASS")

    def test_p3_17_malformed_ledger_status_fails_closed(self):
        p = self.issue("malformed")
        con = sqlite3.connect(self.db)
        con.execute("PRAGMA ignore_check_constraints=ON")
        con.execute("UPDATE permit_ledger SET status='BROKEN' WHERE nonce='malformed'")
        con.commit(); con.close()
        self.assertEqual(self.restart().consume(p, reviews(), v(), signals()).state, "DENIED")

    def test_p3_18_deleted_consumed_record_is_not_claimed_tamper_resistant(self):
        p = self.issue("delete-gap")
        self.auth.consume(p, reviews(), v(), signals())
        con = sqlite3.connect(self.db)
        con.execute("DELETE FROM permit_ledger WHERE nonce='delete-gap'")
        con.commit(); con.close()
        d = self.restart().consume(p, reviews(), v(), signals())
        self.assertEqual(d.state, "DENIED")
        self.assertIn("missing durable permit record", d.reasons)

    def test_p3_19_reviewer_inputs_have_no_direct_ledger_control_fields(self):
        p = self.issue("no-reviewer-control")
        self.assertFalse(hasattr(reviews()[0], "ledger_status"))
        self.assertFalse(hasattr(p, "production_authority"))
        self.assertFalse(self.auth.consume(p, reviews(), v(), signals()).production_authority)

    def test_p3_20_fresh_clean_permit_live_after_prior_attack_vectors(self):
        old = self.issue("old")
        self.auth.consume(old, reviews(), v(), signals())
        fresh = self.auth.issue(reviews(), v(), signals(), nonce="fresh")
        first = self.restart().consume(fresh, reviews(), v(), signals())
        second = self.restart().consume(fresh, reviews(), v(), signals())
        self.assertEqual(first.state, "CONVERGED_PASS")
        self.assertEqual(second.state, "DENIED")
        self.assertFalse(first.production_authority)


if __name__ == "__main__":
    unittest.main()
