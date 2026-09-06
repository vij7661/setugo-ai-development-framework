from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import threading
import unittest

from exp_i_asymmetric_checkpoint_signer import _digest
from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_key_rotation_registry import (
    PlatformTrustRegistryAuthority,
    RotatingCheckpointSignerProcess,
    RotatingCheckpointVerifier,
    RotatingCheckpointWriter,
    TrustRegistryReader,
    public_key_fingerprint,
)

CASE = "EXP-I-P12-CASE"
PERMIT_KEY = b"exp-i-pilot12-permit-key"
PERMIT_INTEGRITY_KEY = b"exp-i-pilot12-permit-integrity-key"
RECON_INTEGRITY_KEY = b"exp-i-pilot12-reconciliation-integrity-key"


def reviews():
    return [ReviewClaim(x, CASE, "CODE DEFECT", ("CODE",)) for x in ("r1", "r2", "r3")]


def verifier_artifact():
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


class ExpIPilot12KeyRotationRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.state_db = str(root / "platform-state.db")
        self.registry_db = str(root / "trust-registry.db")
        self.permits = DurableConvergencePermitAuthority(self.state_db, PERMIT_KEY)
        self.permits.issue(reviews(), verifier_artifact(), signals(), nonce="permit-1")
        self.registry = PlatformTrustRegistryAuthority(self.registry_db)
        self.signers = []
        self.k1 = self.new_signer("K1")
        self.k2 = self.new_signer("K2")
        self.k3 = self.new_signer("K3")
        self.registry.bootstrap(key_id="K1", public_key_pem=self.k1.public_key_pem, activation_generation=1)
        self.reader = TrustRegistryReader(self.registry_db, self.registry.public_key_pem)
        self.verifier = self.new_verifier(minimum=1)
        self.writer = RotatingCheckpointWriter(state_db=self.state_db, verifier=self.verifier)

    def tearDown(self):
        for signer in self.signers:
            try:
                signer.stop(kill=True)
            except Exception:
                pass
        self.tmp.cleanup()

    def new_signer(self, key_id, *, store_suffix=None):
        store = str(Path(self.tmp.name) / f"signer-{store_suffix or key_id}.db")
        signer = RotatingCheckpointSignerProcess(
            key_id=key_id,
            signer_store=store,
            state_db=self.state_db,
            registry_db=self.registry_db,
            registry_public_key_pem=self.registry.public_key_pem,
            permit_integrity_key=PERMIT_INTEGRITY_KEY,
            reconciliation_integrity_key=RECON_INTEGRITY_KEY,
        )
        self.signers.append(signer)
        return signer

    def restart_signer(self, signer):
        key_id = signer.key_id
        store = signer.signer_store
        signer.stop()
        replacement = RotatingCheckpointSignerProcess(
            key_id=key_id,
            signer_store=store,
            state_db=self.state_db,
            registry_db=self.registry_db,
            registry_public_key_pem=self.registry.public_key_pem,
            permit_integrity_key=PERMIT_INTEGRITY_KEY,
            reconciliation_integrity_key=RECON_INTEGRITY_KEY,
        )
        self.signers.append(replacement)
        return replacement

    def new_verifier(self, *, minimum):
        reader = TrustRegistryReader(self.registry_db, self.registry.public_key_pem)
        return RotatingCheckpointVerifier(
            registry_reader=reader,
            state_db=self.state_db,
            permit_integrity_key=PERMIT_INTEGRITY_KEY,
            reconciliation_integrity_key=RECON_INTEGRITY_KEY,
            minimum_trust_epoch=minimum,
        )

    def rotate_k2(self):
        result = self.registry.rotate(
            new_key_id="K2", new_public_key_pem=self.k2.public_key_pem, activation_generation=2
        )
        self.verifier.minimum_trust_epoch = 2
        return result

    def issue_k1(self):
        return self.writer.issue(signer=self.k1, issuance_id="issuance-1", generation=1)

    def issue_k2(self, previous):
        return self.writer.issue(
            signer=self.k2, issuance_id="issuance-2", generation=2, previous=previous
        )

    def journal_count(self, generation=None):
        con = sqlite3.connect(self.state_db)
        try:
            if generation is None:
                return con.execute("SELECT COUNT(*) FROM rotating_checkpoint_journal").fetchone()[0]
            return con.execute(
                "SELECT COUNT(*) FROM rotating_checkpoint_journal WHERE generation=? AND status='CURRENT'",
                (generation,),
            ).fetchone()[0]
        finally:
            con.close()

    def test_p12_01_trust_registry_distinct_and_signer_cannot_mutate(self):
        self.assertNotEqual(Path(self.registry_db).resolve(), Path(self.k1.signer_store).resolve())
        self.assertNotEqual(Path(self.registry_db).resolve(), Path(self.state_db).resolve())
        self.assertFalse(hasattr(self.k1, "rotate"))
        self.assertFalse(hasattr(self.k1, "revoke"))
        self.assertFalse(hasattr(self.writer, "rotate"))
        self.assertFalse(hasattr(self.verifier, "rotate"))
        denied = self.k1.call({"op": "rotate", "new_key_id": "attacker"})
        self.assertFalse(denied["ok"])
        self.assertEqual(denied["reason"], "OPERATION_NOT_ALLOWED")

    def test_p12_02_clean_k1_baseline(self):
        first = self.issue_k1()
        self.assertEqual(first["statement"]["key_id"], "K1")
        self.assertEqual(first["statement"]["trust_epoch"], 1)
        self.assertTrue(self.verifier.verify_current(first)["ok"])
        self.assertEqual(self.journal_count(1), 1)

    def test_p12_03_clean_atomic_k1_to_k2_revocation_rotation(self):
        event = self.rotate_k2()["event"]
        self.assertEqual(event["trust_epoch"], 2)
        self.assertEqual(event["prior_key_id"], "K1")
        self.assertEqual(event["prior_status_after"], "REVOKED")
        self.assertEqual(event["active_key_id"], "K2")
        self.assertEqual(event["activation_generation"], 2)
        current = self.reader.current(minimum_trust_epoch=2)["event"]
        self.assertEqual(current["active_key_id"], "K2")
        self.assertEqual(len(self.reader.history(minimum_trust_epoch=2)), 2)
        self.assertEqual(self.reader.key_record("K1", minimum_trust_epoch=2)["status"], "REVOKED")
        self.assertEqual(self.reader.key_record("K2", minimum_trust_epoch=2)["status"], "ACTIVE")

    def test_p12_04_cryptographically_valid_k1_rejected_after_revocation(self):
        first = self.issue_k1()
        self.assertTrue(self.verifier.verify_math(first)["ok"])
        self.rotate_k2()
        self.assertTrue(self.verifier.verify_math(first)["ok"])
        decision = self.verifier.verify_current(first)
        self.assertFalse(decision["ok"])
        self.assertEqual(decision["reason"], "CHECKPOINT_KEY_REVOKED_OR_INACTIVE")

    def test_p12_05_new_k1_issuance_blocked_after_revocation(self):
        first = self.issue_k1()
        self.rotate_k2()
        result = self.k1.issue("issuance-old-key", 2)
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "SIGNER_KEY_NOT_ACTIVE")
        self.assertEqual(self.journal_count(), 1)
        self.assertTrue(self.verifier.verify_math(first)["ok"])

    def test_p12_06_key_id_substitution_denied(self):
        first = self.issue_k1()
        self.rotate_k2()
        mutated = json.loads(json.dumps(first))
        mutated["statement"]["key_id"] = "K2"
        mutated["checkpoint_digest"] = _digest({
            "statement": mutated["statement"], "signature": mutated["signature"]
        })
        decision = self.verifier.verify_math(mutated)
        self.assertFalse(decision["ok"])
        self.assertIn(decision["reason"], {"CHECKPOINT_TRUST_EPOCH_BINDING_INVALID", "CHECKPOINT_SIGNATURE_INVALID"})

    def test_p12_07_public_key_fingerprint_substitution_denied(self):
        self.rotate_k2()
        con = sqlite3.connect(self.registry_db, isolation_level=None)
        try:
            row = con.execute("SELECT event_json FROM trust_events WHERE trust_epoch=2").fetchone()
            event = json.loads(row[0])
            event["active_public_key_pem"] = self.k3.public_key_pem
            event["active_public_key_fingerprint"] = public_key_fingerprint(self.k3.public_key_pem)
            con.execute("UPDATE trust_events SET event_json=? WHERE trust_epoch=2", (json.dumps(event, sort_keys=True),))
        finally:
            con.close()
        with self.assertRaises(PermissionError) as ctx:
            self.reader.current(minimum_trust_epoch=2)
        self.assertIn(str(ctx.exception), {"TRUST_EVENT_SIGNATURE_INVALID", "TRUST_EVENT_DIGEST_INVALID"})

    def test_p12_08_trust_epoch_rollback_denied(self):
        first = self.issue_k1()
        stale_db = str(Path(self.tmp.name) / "stale-registry.db")
        con = sqlite3.connect(self.registry_db)
        stale = sqlite3.connect(stale_db)
        try:
            con.backup(stale)
        finally:
            stale.close(); con.close()
        self.rotate_k2()
        stale_reader = TrustRegistryReader(stale_db, self.registry.public_key_pem)
        with self.assertRaises(PermissionError) as ctx:
            stale_reader.current(minimum_trust_epoch=2)
        self.assertEqual(str(ctx.exception), "TRUST_EPOCH_ROLLBACK")
        self.assertTrue(self.verifier.verify_math(first)["ok"])

    def test_p12_09_stale_registry_or_positive_cache_cannot_reenable_k1(self):
        first = self.issue_k1()
        self.assertTrue(self.verifier.verify_current(first)["ok"])
        self.rotate_k2()
        self.assertFalse(self.verifier.verify_current(first)["ok"])
        fresh = self.new_verifier(minimum=2)
        self.assertFalse(fresh.verify_current(first)["ok"])

    def test_p12_10_mixed_key_lineage_substitution_denied(self):
        first = self.issue_k1()
        self.rotate_k2()
        second = self.issue_k2(first)
        wrong_previous = json.loads(json.dumps(first))
        wrong_previous["checkpoint_digest"] = "0" * 64
        decision = self.verifier.verify_current(second, previous=wrong_previous)
        self.assertFalse(decision["ok"])
        self.assertIn(decision["reason"], {"PREVIOUS_CHECKPOINT_INVALID", "CHECKPOINT_PREDECESSOR_INVALID"})
        self.assertEqual(second["statement"]["previous_checkpoint_digest"], first["checkpoint_digest"])

    def test_p12_11_exact_k2_replay_idempotent(self):
        first = self.issue_k1()
        self.rotate_k2()
        second = self.issue_k2(first)
        replay = self.issue_k2(first)
        self.assertEqual(second["checkpoint_digest"], replay["checkpoint_digest"])
        self.assertEqual(second["signature"], replay["signature"])
        self.assertEqual(self.journal_count(2), 1)

    def test_p12_12_concurrent_rotation_vs_issuance_has_one_authoritative_outcome(self):
        first = self.issue_k1()
        barrier = threading.Barrier(2)
        outcomes = []

        def issue_old():
            barrier.wait()
            try:
                result = self.writer.issue(
                    signer=self.k1, issuance_id="race-k1", generation=2, previous=first
                )
                outcomes.append(("issue", True, result))
            except Exception as exc:
                outcomes.append(("issue", False, str(exc)))

        def rotate():
            barrier.wait()
            try:
                result = self.registry.rotate(
                    new_key_id="K2", new_public_key_pem=self.k2.public_key_pem, activation_generation=2
                )
                outcomes.append(("rotate", True, result))
            except Exception as exc:
                outcomes.append(("rotate", False, str(exc)))

        a = threading.Thread(target=issue_old); b = threading.Thread(target=rotate)
        a.start(); b.start(); a.join(); b.join()
        current = self.reader.current(minimum_trust_epoch=2)["event"]
        self.assertEqual(current["active_key_id"], "K2")
        k1_rows = []
        con = sqlite3.connect(self.state_db)
        try:
            rows = con.execute("SELECT statement_json,checkpoint_digest,signature FROM rotating_checkpoint_journal WHERE generation=2").fetchall()
            for row in rows:
                record = {"statement": json.loads(row[0]), "checkpoint_digest": row[1], "signature": row[2]}
                if record["statement"]["key_id"] == "K1":
                    k1_rows.append(record)
        finally:
            con.close()
        for record in k1_rows:
            self.assertFalse(self.new_verifier(minimum=2).verify_current(record, previous=first)["ok"])
        self.assertLessEqual(self.journal_count(2), 1)
        self.assertEqual(len([x for x in outcomes if x[0] == "rotate" and x[1]]), 1)

    def test_p12_13_signer_restart_preserves_active_key_and_trust_epoch(self):
        first = self.issue_k1()
        self.rotate_k2()
        old_fp = self.k2.fingerprint
        self.k2 = self.restart_signer(self.k2)
        self.assertEqual(self.k2.fingerprint, old_fp)
        self.assertFalse(self.k1.issue("old-after-rotation", 2)["ok"])
        second = self.issue_k2(first)
        self.assertEqual(second["statement"]["trust_epoch"], 2)
        self.assertEqual(second["statement"]["key_id"], "K2")

    def test_p12_14_verifier_restart_uses_current_registry_not_stale_positive(self):
        first = self.issue_k1()
        self.assertTrue(self.verifier.verify_current(first)["ok"])
        self.rotate_k2()
        fresh = self.new_verifier(minimum=2)
        decision = fresh.verify_current(first)
        self.assertFalse(decision["ok"])
        self.assertEqual(decision["reason"], "CHECKPOINT_KEY_REVOKED_OR_INACTIVE")

    def test_p12_15_authority_separation_remains_zero_outside_platform_registry(self):
        first = self.issue_k1()
        objects = (self.k1, self.writer, self.verifier, self.reader)
        for obj in objects:
            self.assertFalse(hasattr(obj, "rotate"))
            self.assertFalse(hasattr(obj, "revoke"))
            self.assertFalse(hasattr(obj, "approve"))
            self.assertFalse(hasattr(obj, "release"))
        for payload in (first, self.verifier.verify_current(first)):
            for key in ("production_authority", "release_authority", "merge_authority", "approval_authority"):
                self.assertNotIn(key, payload)

    def test_p12_16_clean_k2_to_k3_second_rotation_liveness(self):
        first = self.issue_k1()
        self.rotate_k2()
        second = self.issue_k2(first)
        event3 = self.registry.rotate(
            new_key_id="K3", new_public_key_pem=self.k3.public_key_pem, activation_generation=3
        )["event"]
        self.assertEqual(event3["trust_epoch"], 3)
        self.assertEqual(event3["prior_key_id"], "K2")
        self.assertEqual(event3["active_key_id"], "K3")
        self.k3 = self.restart_signer(self.k3)
        fresh = self.new_verifier(minimum=3)
        writer = RotatingCheckpointWriter(state_db=self.state_db, verifier=fresh)
        third = writer.issue(signer=self.k3, issuance_id="issuance-3", generation=3, previous=second)
        self.assertEqual(third["statement"]["trust_epoch"], 3)
        self.assertEqual(third["statement"]["key_id"], "K3")
        self.assertEqual(third["statement"]["previous_checkpoint_digest"], second["checkpoint_digest"])
        self.assertTrue(fresh.verify_current(third, previous=second)["ok"])
        self.assertEqual(self.journal_count(1), 1)
        self.assertEqual(self.journal_count(2), 1)
        self.assertEqual(self.journal_count(3), 1)


if __name__ == "__main__":
    unittest.main()
