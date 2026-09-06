from __future__ import annotations

import copy
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_composite_authority_process import CompositeCheckpointAuthorityProcess
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_external_monotonic_anchor import ExternalMonotonicAnchor

CASE = "EXP-I-P12-CASE"
PERMIT_KEY = b"exp-i-pilot12-permit-key"
PERMIT_INTEGRITY_KEY = b"exp-i-pilot12-permit-integrity-key"
RECON_INTEGRITY_KEY = b"exp-i-pilot12-reconciliation-integrity-key"
CHECKPOINT_KEY = b"exp-i-pilot12-checkpoint-key"
ANCHOR_KEY = b"exp-i-pilot12-external-anchor-key"
MINIMUM_KEY = b"exp-i-pilot12-external-minimum-key"


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


def sqlite_snapshot(source: Path, destination: Path) -> None:
    src = sqlite3.connect(source)
    dst = sqlite3.connect(destination)
    try:
        src.backup(dst)
    finally:
        dst.close(); src.close()


def sqlite_restore(snapshot: Path, destination: Path) -> None:
    src = sqlite3.connect(snapshot)
    dst = sqlite3.connect(destination)
    try:
        src.backup(dst)
    finally:
        dst.close(); src.close()


class ExpIPilot12CoherentAuthorityStoreRollbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.main_db = self.root / "governance.sqlite"
        self.authority_db = self.root / "authority.sqlite"
        self.anchor_file = self.root / "external" / "anchor.json"
        self.minimum_file = self.root / "external" / "minimum.json"
        self.permits = DurableConvergencePermitAuthority(self.main_db, PERMIT_KEY)
        self.permits.issue(reviews(), verifier(), signals(), nonce="permit-1")
        self.processes = []
        self.anchor = ExternalMonotonicAnchor(
            self.anchor_file, self.minimum_file, anchor_key=ANCHOR_KEY, minimum_key=MINIMUM_KEY
        )

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

    def issue_and_anchor(self, generation: int, issuance_id: str | None = None):
        p = self.authority()
        r = p.issue(issuance_id or f"issuance-{generation}", generation)
        self.assertTrue(r.get("ok"), r)
        a = self.anchor.advance(generation=generation, checkpoint_digest=r["checkpoint_digest"])
        self.assertTrue(a.get("ok"), a)
        return p, r

    def advance_governance(self, nonce: str):
        self.permits.issue(reviews(), verifier(), signals(), nonce=nonce)

    def verify_all(self, p, r, minimum=None):
        pv = p.verify(r, minimum_generation=int(r["statement"]["generation"]))
        ev = self.anchor.verify_authority_store(self.authority_db, r, requested_minimum=minimum)
        return pv, ev

    def gen2_with_gen1_snapshots(self, *, change_governance=False):
        p1, r1 = self.issue_and_anchor(1)
        auth1 = self.root / "authority-gen1.sqlite"
        main1 = self.root / "main-gen1.sqlite"
        sqlite_snapshot(self.authority_db, auth1)
        sqlite_snapshot(self.main_db, main1)
        anchor1 = self.root / "anchor-gen1.json"
        minimum1 = self.root / "minimum-gen1.json"
        shutil.copy2(self.anchor_file, anchor1)
        shutil.copy2(self.minimum_file, minimum1)
        if change_governance:
            self.advance_governance("permit-2")
        p2 = self.authority()
        r2 = p2.issue("issuance-2", 2)
        self.assertTrue(r2.get("ok"), r2)
        self.assertTrue(self.anchor.advance(generation=2, checkpoint_digest=r2["checkpoint_digest"]).get("ok"))
        return p1, p2, r1, r2, auth1, main1, anchor1, minimum1

    def test_p12_01_clean_generation_one_authority_store_and_external_anchor_verify(self):
        p, r = self.issue_and_anchor(1)
        pv, ev = self.verify_all(p, r)
        self.assertTrue(pv.get("ok"), pv)
        self.assertTrue(ev.get("ok"), ev)
        self.assertEqual(ev["trusted_minimum"], 1)

    def test_p12_02_advance_generation_two_then_restore_full_generation_one_authority_snapshot_is_rejected(self):
        _, p2, r1, _, auth1, *_ = self.gen2_with_gen1_snapshots()
        sqlite_restore(auth1, self.authority_db)
        self.assertFalse(self.anchor.verify_authority_store(self.authority_db, r1).get("ok"))
        self.assertEqual(self.anchor.trusted_minimum(), 2)

    def test_p12_03_stale_store_plus_current_anchor_is_rejected(self):
        _, _, _, r2, auth1, *_ = self.gen2_with_gen1_snapshots()
        sqlite_restore(auth1, self.authority_db)
        ev = self.anchor.verify_authority_store(self.authority_db, r2)
        self.assertFalse(ev.get("ok"))

    def test_p12_04_current_store_plus_stale_anchor_below_trusted_minimum_is_rejected(self):
        _, _, _, r2, _, _, anchor1, _ = self.gen2_with_gen1_snapshots()
        shutil.copy2(anchor1, self.anchor_file)
        ev = self.anchor.verify_authority_store(self.authority_db, r2)
        self.assertFalse(ev.get("ok"))
        self.assertEqual(self.anchor.trusted_minimum(), 2)

    def test_p12_05_coherent_old_store_plus_old_valid_anchor_below_trusted_minimum_is_rejected(self):
        _, _, r1, _, auth1, _, anchor1, _ = self.gen2_with_gen1_snapshots()
        sqlite_restore(auth1, self.authority_db)
        shutil.copy2(anchor1, self.anchor_file)
        ev = self.anchor.verify_authority_store(self.authority_db, r1)
        self.assertFalse(ev.get("ok"))
        self.assertEqual(ev.get("reason"), "CHECKPOINT_BELOW_EXTERNAL_MINIMUM")

    def test_p12_06_lowering_only_authority_meta_max_generation_is_detected(self):
        _, _, _, r2, *_ = self.gen2_with_gen1_snapshots()
        con = sqlite3.connect(self.authority_db)
        try:
            con.execute("UPDATE meta SET max_generation=1 WHERE singleton=1"); con.commit()
        finally:
            con.close()
        ev = self.anchor.verify_authority_store(self.authority_db, r2)
        self.assertFalse(ev.get("ok"))
        self.assertEqual(ev.get("reason"), "AUTHORITY_META_ANCHOR_MISMATCH")

    def test_p12_07_deleting_latest_generation_while_meta_remains_high_is_detected(self):
        _, _, _, r2, *_ = self.gen2_with_gen1_snapshots()
        con = sqlite3.connect(self.authority_db)
        try:
            con.execute("DELETE FROM issued WHERE generation=2"); con.commit()
        finally:
            con.close()
        ev = self.anchor.verify_authority_store(self.authority_db, r2)
        self.assertFalse(ev.get("ok"))
        self.assertEqual(ev.get("reason"), "ANCHORED_AUTHORITY_ROW_MISSING")

    def test_p12_08_forged_anchor_authentication_is_rejected(self):
        _, r = self.issue_and_anchor(1)
        data = json.loads(self.anchor_file.read_text())
        data["tag"] = "0" * 64
        self.anchor_file.write_text(json.dumps(data))
        self.assertEqual(self.anchor.verify_checkpoint(r).get("reason"), "ANCHOR_INVALID")

    def test_p12_09_anchor_generation_mutation_after_authentication_is_rejected(self):
        _, r = self.issue_and_anchor(1)
        data = json.loads(self.anchor_file.read_text()); data["payload"]["generation"] = 2
        self.anchor_file.write_text(json.dumps(data))
        self.assertEqual(self.anchor.verify_checkpoint(r).get("reason"), "ANCHOR_INVALID")

    def test_p12_10_anchor_checkpoint_digest_mutation_after_authentication_is_rejected(self):
        _, r = self.issue_and_anchor(1)
        data = json.loads(self.anchor_file.read_text()); data["payload"]["checkpoint_digest"] = "f" * 64
        self.anchor_file.write_text(json.dumps(data))
        self.assertEqual(self.anchor.verify_checkpoint(r).get("reason"), "ANCHOR_INVALID")

    def test_p12_11_anchor_scope_or_authority_identity_substitution_is_rejected(self):
        _, r = self.issue_and_anchor(1)
        for field, value in (("scope", "OTHER"), ("authority_id", "other-authority")):
            original = json.loads(self.anchor_file.read_text())
            tampered = copy.deepcopy(original); tampered["payload"][field] = value
            self.anchor_file.write_text(json.dumps(tampered))
            self.assertEqual(self.anchor.verify_checkpoint(r).get("reason"), "ANCHOR_INVALID")
            self.anchor_file.write_text(json.dumps(original))

    def test_p12_12_missing_anchor_fails_closed(self):
        _, r = self.issue_and_anchor(1)
        self.anchor_file.unlink()
        self.assertEqual(self.anchor.verify_checkpoint(r).get("reason"), "ANCHOR_MISSING")

    def test_p12_13_malformed_anchor_fails_closed(self):
        _, r = self.issue_and_anchor(1)
        self.anchor_file.write_text("{not-json")
        self.assertEqual(self.anchor.verify_checkpoint(r).get("reason"), "ANCHOR_INVALID")

    def test_p12_14_trusted_minimum_cannot_be_lowered_by_model_or_request_payload(self):
        _, _, r1, r2, *_ = self.gen2_with_gen1_snapshots()
        self.assertEqual(self.anchor.trusted_minimum(), 2)
        self.assertFalse(self.anchor.verify_checkpoint(r1, requested_minimum=1).get("ok"))
        self.assertTrue(self.anchor.verify_checkpoint(r2, requested_minimum=1).get("ok"))

    def test_p12_15_two_live_authority_processes_observe_same_external_minimum(self):
        _, p2, _, r2, *_ = self.gen2_with_gen1_snapshots()
        p3 = self.authority()
        self.assertTrue(p2.verify(r2, minimum_generation=2).get("ok"))
        self.assertTrue(p3.verify(r2, minimum_generation=2).get("ok"))
        self.assertEqual(self.anchor.verify_authority_store(self.authority_db, r2)["trusted_minimum"], 2)

    def test_p12_16_old_positive_verification_cannot_survive_external_minimum_advance(self):
        p1, r1 = self.issue_and_anchor(1)
        self.assertTrue(self.anchor.verify_authority_store(self.authority_db, r1).get("ok"))
        p2 = self.authority(); r2 = p2.issue("issuance-2", 2)
        self.assertTrue(r2.get("ok"), r2)
        self.assertTrue(self.anchor.advance(generation=2, checkpoint_digest=r2["checkpoint_digest"]).get("ok"))
        self.assertFalse(self.anchor.verify_authority_store(self.authority_db, r1).get("ok"))

    def test_p12_17_coherent_governance_and_authority_store_rollback_still_blocked_by_external_minimum(self):
        p1, p2, r1, r2, auth1, main1, *_ = self.gen2_with_gen1_snapshots(change_governance=True)
        p1.stop(kill=True); p2.stop(kill=True)
        sqlite_restore(auth1, self.authority_db)
        sqlite_restore(main1, self.main_db)
        p3 = self.authority()
        self.assertTrue(p3.verify(r1, minimum_generation=1).get("ok"))
        ev = self.anchor.verify_authority_store(self.authority_db, r1)
        self.assertFalse(ev.get("ok"))
        self.assertEqual(self.anchor.trusted_minimum(), 2)

    def test_p12_18_repeated_restart_with_stale_snapshot_never_promotes(self):
        p1, p2, r1, _, auth1, main1, *_ = self.gen2_with_gen1_snapshots(change_governance=True)
        p1.stop(kill=True); p2.stop(kill=True)
        sqlite_restore(auth1, self.authority_db); sqlite_restore(main1, self.main_db)
        for _ in range(4):
            p = self.authority()
            self.assertTrue(p.verify(r1, minimum_generation=1).get("ok"))
            self.assertFalse(self.anchor.verify_authority_store(self.authority_db, r1).get("ok"))
            p.stop(kill=True)

    def test_p12_19_models_reviewers_have_zero_anchor_release_or_production_authority(self):
        _, r = self.issue_and_anchor(1)
        ev = self.anchor.verify_authority_store(self.authority_db, r)
        self.assertTrue(ev.get("ok"), ev)
        self.assertFalse(ev.get("reviewer_generated_authority"))
        self.assertFalse(ev.get("production_authority"))
        self.assertFalse(ev.get("release_authority"))

    def test_p12_20_clean_higher_generation_store_and_anchor_liveness_after_rollback_attacks(self):
        p1, r1 = self.issue_and_anchor(1)
        p2 = self.authority(); r2 = p2.issue("issuance-2", 2)
        self.assertTrue(r2.get("ok"), r2)
        self.assertTrue(self.anchor.advance(generation=2, checkpoint_digest=r2["checkpoint_digest"]).get("ok"))
        p3 = self.authority(); r3 = p3.issue("issuance-3", 3)
        self.assertTrue(r3.get("ok"), r3)
        self.assertTrue(self.anchor.advance(generation=3, checkpoint_digest=r3["checkpoint_digest"]).get("ok"))
        self.assertTrue(p1.verify(r3, minimum_generation=3).get("ok"))
        ev = self.anchor.verify_authority_store(self.authority_db, r3)
        self.assertTrue(ev.get("ok"), ev)
        self.assertEqual(ev["trusted_minimum"], 3)


if __name__ == "__main__":
    unittest.main()
