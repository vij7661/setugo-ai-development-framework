from __future__ import annotations

import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tempfile
import threading
import unittest

from exp_i_asymmetric_checkpoint_signer import (
    KEY_ID,
    VERSION,
    AsymmetricCheckpointSignerProcess,
    PublicCheckpointVerifier,
    PublicKeyCompositeWriter,
    _canon,
    _digest,
    _ed25519_sign,
    _ensure_ed25519_keypair,
    _key_paths,
)
from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_composite_integrity import SCOPE
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_use_time_checkpoint import UseTimeCheckpointAuthority

CASE = "EXP-I-P11-CASE"
PERMIT_KEY = b"exp-i-pilot11-permit-key"
PERMIT_INTEGRITY_KEY = b"exp-i-pilot11-permit-integrity-key"
RECON_INTEGRITY_KEY = b"exp-i-pilot11-reconciliation-integrity-key"
TOKEN_KEY = b"exp-i-pilot11-token-key"


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


class ExpIPilot11AsymmetricCheckpointSignerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.state_db = str(root / "platform-state.db")
        self.signer_store = str(root / "asymmetric-signer-authority.db")
        self.permits = DurableConvergencePermitAuthority(self.state_db, PERMIT_KEY)
        self.permits.issue(reviews(), verifier_artifact(), signals(), nonce="permit-1")
        self.use_time = UseTimeCheckpointAuthority(
            self.state_db, PERMIT_KEY, PERMIT_INTEGRITY_KEY, TOKEN_KEY
        )
        self.signer = self.new_signer()
        self.verifier = self.new_verifier(self.signer.public_key_pem)
        self.writer = PublicKeyCompositeWriter(
            state_db=self.state_db, signer=self.signer, verifier=self.verifier
        )

    def tearDown(self):
        try:
            self.signer.stop(kill=True)
        except Exception:
            pass
        self.tmp.cleanup()

    def new_signer(self):
        return AsymmetricCheckpointSignerProcess(
            signer_store=self.signer_store,
            state_db=self.state_db,
            permit_integrity_key=PERMIT_INTEGRITY_KEY,
            reconciliation_integrity_key=RECON_INTEGRITY_KEY,
        )

    def new_verifier(self, public_key_pem, *, key_id=KEY_ID):
        return PublicCheckpointVerifier(
            public_key_pem=public_key_pem,
            state_db=self.state_db,
            permit_integrity_key=PERMIT_INTEGRITY_KEY,
            reconciliation_integrity_key=RECON_INTEGRITY_KEY,
            expected_key_id=key_id,
        )

    def journal_count(self, generation=None):
        con = sqlite3.connect(self.state_db)
        try:
            if generation is None:
                return con.execute("SELECT COUNT(*) FROM asymmetric_composite_journal").fetchone()[0]
            return con.execute(
                "SELECT COUNT(*) FROM asymmetric_composite_journal WHERE generation=? AND status='CURRENT'",
                (generation,),
            ).fetchone()[0]
        finally:
            con.close()

    def unrelated_keypair(self):
        root = Path(self.tmp.name) / ("unrelated-" + os.urandom(4).hex())
        private = str(root) + ".private.pem"
        public = str(root) + ".public.pem"
        _ensure_ed25519_keypair(private, public)
        return private, Path(public).read_text(encoding="utf-8")

    def test_p11_01_signer_owns_private_key_writer_verifier_do_not(self):
        private_path, public_path = _key_paths(self.signer_store)
        self.assertNotEqual(self.signer.pid, os.getpid())
        self.assertTrue(Path(private_path).exists())
        self.assertTrue(Path(public_path).exists())
        self.assertNotIn("PRIVATE KEY", self.signer.public_key_pem)
        self.assertNotIn(private_path, " ".join(self.signer.argv))
        self.assertNotIn("PRIVATE KEY", repr(self.writer.__dict__))
        self.assertNotIn("PRIVATE KEY", repr(self.verifier.__dict__))
        self.assertFalse(hasattr(self.writer, "sign"))
        self.assertFalse(hasattr(self.verifier, "sign"))
        self.assertFalse(self.signer.call({"op": "get_private_key"})["ok"])

    def test_p11_02_public_key_cannot_mint(self):
        legitimate = self.signer.issue("issuance-1", 1)
        forged = json.loads(json.dumps(legitimate))
        forged["signature"] = "AAAA"
        forged["checkpoint_digest"] = _digest({
            "statement": forged["statement"], "signature": forged["signature"]
        })
        self.assertFalse(self.verifier.verify_signature(forged, minimum_generation=1)["ok"])
        self.assertFalse(hasattr(self.verifier, "issue"))
        self.assertFalse(hasattr(self.verifier, "_private_key"))

    def test_p11_03_clean_generation1_issue_and_offline_verify(self):
        record = self.writer.issue("issuance-1", 1)
        self.assertEqual(record["status"], "CURRENT")
        self.assertEqual(record["statement"]["key_id"], KEY_ID)
        self.assertEqual(record["statement"]["previous_checkpoint_digest"], "GENESIS")
        decision = self.verifier.verify_signature(record, minimum_generation=1)
        self.assertTrue(decision["ok"])
        self.assertEqual(self.journal_count(1), 1)

    def test_p11_04_verifier_succeeds_while_signer_unavailable(self):
        record = self.writer.issue("issuance-1", 1)
        public = self.signer.public_key_pem
        self.signer.stop(kill=True)
        fresh_verifier = self.new_verifier(public)
        self.assertTrue(fresh_verifier.verify_signature(record, minimum_generation=1)["ok"])
        self.assertFalse(self.signer.issue("issuance-2", 2)["ok"])

    def test_p11_05_signer_outage_blocks_new_writer_mutation(self):
        self.signer.stop(kill=True)
        with self.assertRaises(PermissionError):
            self.writer.issue("issuance-1", 1)
        self.assertEqual(self.journal_count(), 0)

    def test_p11_06_private_key_substitution_denied(self):
        legitimate = self.signer.issue("issuance-1", 1)
        wrong_private, _ = self.unrelated_keypair()
        forged = json.loads(json.dumps(legitimate))
        forged["signature"] = _ed25519_sign(wrong_private, _canon(forged["statement"]))
        forged["checkpoint_digest"] = _digest({
            "statement": forged["statement"], "signature": forged["signature"]
        })
        decision = self.verifier.verify_signature(forged, minimum_generation=1)
        self.assertFalse(decision["ok"])
        self.assertEqual(decision["reason"], "CHECKPOINT_SIGNATURE_INVALID")

    def test_p11_07_public_key_and_key_id_substitution_denied(self):
        legitimate = self.signer.issue("issuance-1", 1)
        _, wrong_public = self.unrelated_keypair()
        wrong_verifier = self.new_verifier(wrong_public)
        self.assertFalse(wrong_verifier.verify_signature(legitimate, minimum_generation=1)["ok"])
        mutated = json.loads(json.dumps(legitimate))
        mutated["statement"]["key_id"] = "attacker-key"
        mutated["checkpoint_digest"] = _digest({
            "statement": mutated["statement"], "signature": mutated["signature"]
        })
        decision = self.verifier.verify_signature(mutated, minimum_generation=1)
        self.assertFalse(decision["ok"])
        self.assertEqual(decision["reason"], "CHECKPOINT_KEY_ID_INVALID")

    def test_p11_08_signed_field_mutation_denied(self):
        legitimate = self.signer.issue("issuance-1", 1)
        mutations = (
            ("issuance_id", "other"),
            ("generation", 2),
            ("scope", "OTHER"),
            ("previous_checkpoint_digest", "OTHER"),
            ("permit_ledger_digest", "OTHER"),
            ("reconciliation_digest", "OTHER"),
            ("permit_authority_epoch", 999),
            ("checkpoint_body_digest", "0" * 64),
        )
        for field, value in mutations:
            mutated = json.loads(json.dumps(legitimate))
            mutated["statement"][field] = value
            mutated["checkpoint_digest"] = _digest({
                "statement": mutated["statement"], "signature": mutated["signature"]
            })
            self.assertFalse(
                self.verifier.verify_signature(mutated, minimum_generation=1)["ok"], field
            )

    def test_p11_09_writer_supplied_governed_semantic_fields_rejected(self):
        request = {
            "op": "issue", "issuance_id": "x", "generation": 1,
            "scope": SCOPE, "version": VERSION, "key_id": KEY_ID,
            "permit_ledger_digest": "attacker",
            "reconciliation_digest": "attacker",
            "permit_authority_epoch": 999,
            "previous_checkpoint_digest": "attacker",
            "signature": "attacker",
        }
        result = self.signer.call(request)
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "ISSUE_REQUEST_SCHEMA_INVALID")
        self.assertEqual(self.journal_count(), 0)

    def test_p11_10_exact_replay_idempotent(self):
        first = self.writer.issue("issuance-1", 1)
        second = self.writer.issue("issuance-1", 1)
        self.assertEqual(first["checkpoint_digest"], second["checkpoint_digest"])
        self.assertEqual(first["signature"], second["signature"])
        self.assertEqual(self.journal_count(1), 1)

    def test_p11_11_same_generation_competitor_denied(self):
        self.assertTrue(self.signer.issue("issuance-1", 1)["ok"])
        conflict = self.signer.issue("issuance-other", 1)
        self.assertFalse(conflict["ok"])
        self.assertEqual(conflict["reason"], "GENERATION_NOT_EXACT_NEXT")

    def test_p11_12_rollback_and_generation_skip_denied(self):
        self.assertTrue(self.signer.issue("issuance-1", 1)["ok"])
        rollback = self.signer.issue("rollback", 1)
        skip = self.signer.issue("skip", 3)
        self.assertFalse(rollback["ok"])
        self.assertFalse(skip["ok"])
        self.assertEqual(rollback["reason"], "GENERATION_NOT_EXACT_NEXT")
        self.assertEqual(skip["reason"], "GENERATION_NOT_EXACT_NEXT")

    def test_p11_13_signer_restart_preserves_monotonicity_and_replay(self):
        first = self.writer.issue("issuance-1", 1)
        public_before = self.signer.public_key_pem
        self.signer.stop()
        self.signer = self.new_signer()
        self.assertEqual(public_before, self.signer.public_key_pem)
        self.verifier = self.new_verifier(self.signer.public_key_pem)
        self.writer = PublicKeyCompositeWriter(
            state_db=self.state_db, signer=self.signer, verifier=self.verifier
        )
        replay = self.writer.issue("issuance-1", 1)
        self.assertEqual(first["checkpoint_digest"], replay["checkpoint_digest"])
        self.assertFalse(self.signer.issue("other", 1)["ok"])
        self.assertFalse(self.signer.issue("skip", 3)["ok"])

    def test_p11_14_stale_valid_signature_not_current_after_state_drift(self):
        record = self.writer.issue("issuance-1", 1)
        self.assertTrue(self.verifier.verify_signature(record, minimum_generation=1)["ok"])
        self.assertTrue(self.verifier.verify_current(record, minimum_generation=1)["ok"])
        self.permits.advance_epoch()
        self.assertTrue(self.verifier.verify_signature(record, minimum_generation=1)["ok"])
        stale = self.verifier.verify_current(record, minimum_generation=1)
        self.assertFalse(stale["ok"])
        self.assertIn(stale["reason"], {"PERMIT_LEDGER_DRIFT", "PERMIT_EPOCH_DRIFT"})

    def test_p11_15_model_reviewer_writer_verifier_authority_remains_zero(self):
        record = self.writer.issue("issuance-1", 1)
        decision = self.verifier.verify_current(record, minimum_generation=1)
        self.assertTrue(decision["ok"])
        for obj in (record, decision):
            self.assertNotIn("production_authority", obj)
            self.assertNotIn("release_authority", obj)
            self.assertNotIn("merge_authority", obj)
            self.assertNotIn("approval_authority", obj)
        self.assertFalse(hasattr(self.writer, "approve"))
        self.assertFalse(hasattr(self.verifier, "approve"))
        self.assertFalse(hasattr(self.signer, "approve"))

    def test_p11_16_clean_generation2_liveness_after_restarts(self):
        first = self.writer.issue("issuance-1", 1)
        self.permits.advance_epoch()
        self.signer.stop()
        self.signer = self.new_signer()
        fresh_verifier = self.new_verifier(self.signer.public_key_pem)
        self.verifier = fresh_verifier
        self.writer = PublicKeyCompositeWriter(
            state_db=self.state_db, signer=self.signer, verifier=fresh_verifier
        )
        second = self.writer.issue("issuance-2", 2)
        self.assertEqual(second["statement"]["previous_checkpoint_digest"], first["checkpoint_digest"])
        self.assertEqual(second["statement"]["generation"], 2)
        self.assertTrue(
            fresh_verifier.verify_current(
                second, minimum_generation=2, previous=first
            )["ok"]
        )
        self.assertEqual(self.journal_count(1), 1)
        self.assertEqual(self.journal_count(2), 1)


if __name__ == "__main__":
    unittest.main()
