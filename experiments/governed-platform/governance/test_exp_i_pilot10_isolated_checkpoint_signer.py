from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest

from exp_i_claim_convergence_gate import ReviewClaim, VerificationArtifact
from exp_i_composite_integrity import CompositeIntegrityAuthority, SCOPE
from exp_i_durable_convergence_permit import DurableConvergencePermitAuthority
from exp_i_isolated_checkpoint_signer import (
    VERSION,
    IsolatedCompositeSignerProcess,
    KeylessCompositeWriter,
    _canon,
    _digest,
)
from exp_i_use_time_checkpoint import UseTimeCheckpointAuthority

CASE = "EXP-I-P10-CASE"
PERMIT_KEY = b"exp-i-pilot10-permit-key"
PERMIT_INTEGRITY_KEY = b"exp-i-pilot10-permit-integrity-key"
RECON_INTEGRITY_KEY = b"exp-i-pilot10-reconciliation-integrity-key"
COMPOSITE_KEY = b"exp-i-pilot10-composite-key"
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


class ExpIPilot10IsolatedCheckpointSignerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.state_db = str(root / "platform-state.db")
        self.signer_store = str(root / "signer-authority.db")
        self.permits = DurableConvergencePermitAuthority(self.state_db, PERMIT_KEY)
        self.permits.issue(reviews(), verifier(), signals(), nonce="permit-1")
        self.use_time = UseTimeCheckpointAuthority(
            self.state_db, PERMIT_KEY, PERMIT_INTEGRITY_KEY, TOKEN_KEY
        )
        self.signer = self.new_signer()
        self.writer = KeylessCompositeWriter(state_db=self.state_db, signer=self.signer)

    def tearDown(self):
        try:
            self.signer.stop(kill=True)
        except Exception:
            pass
        self.tmp.cleanup()

    def new_signer(self):
        return IsolatedCompositeSignerProcess(
            signer_store=self.signer_store,
            state_db=self.state_db,
            permit_integrity_key=PERMIT_INTEGRITY_KEY,
            reconciliation_integrity_key=RECON_INTEGRITY_KEY,
            composite_key=COMPOSITE_KEY,
        )

    def current_pair(self):
        return CompositeIntegrityAuthority(
            self.state_db,
            PERMIT_INTEGRITY_KEY,
            RECON_INTEGRITY_KEY,
            COMPOSITE_KEY,
        ).current_pair()

    def journal_count(self, generation=None):
        con = sqlite3.connect(self.state_db)
        try:
            if generation is None:
                return con.execute("SELECT COUNT(*) FROM isolated_composite_journal").fetchone()[0]
            return con.execute(
                "SELECT COUNT(*) FROM isolated_composite_journal WHERE generation=? AND status='CURRENT'",
                (generation,),
            ).fetchone()[0]
        finally:
            con.close()

    def test_p10_01_distinct_signer_process_and_store(self):
        self.assertNotEqual(self.signer.pid, os.getpid())
        self.assertNotEqual(Path(self.signer_store).resolve(), Path(self.state_db).resolve())
        self.assertTrue(Path(self.signer_store).exists())
        self.assertIsNone(self.signer.proc.poll())

    def test_p10_02_writer_has_no_composite_signing_key(self):
        key_hex = COMPOSITE_KEY.hex()
        self.assertNotIn("EXP_I_P10_COMPOSITE_KEY_HEX", os.environ)
        self.assertNotIn(key_hex, " ".join(self.signer.argv))
        self.assertNotIn(key_hex, repr(self.writer.__dict__))
        self.assertNotIn(COMPOSITE_KEY, tuple(v for v in self.writer.__dict__.values() if isinstance(v, bytes)))
        self.assertFalse(hasattr(self.writer, "sign"))
        self.assertFalse(hasattr(self.writer, "_sign"))
        denied = self.signer.call({"op": "get_key"})
        self.assertFalse(denied["ok"])

    def test_p10_03_clean_signer_derived_generation1_issuance(self):
        expected = self.current_pair()
        record = self.writer.issue("issuance-1", 1)
        statement = record["statement"]
        self.assertEqual(statement["permit_ledger_digest"], expected["permit_ledger_digest"])
        self.assertEqual(statement["reconciliation_digest"], expected["reconciliation_digest"])
        self.assertEqual(statement["permit_authority_epoch"], expected["permit_authority_epoch"])
        self.assertEqual(statement["previous_checkpoint_digest"], "GENESIS")
        self.assertEqual(record["status"], "CURRENT")
        self.assertTrue(self.writer.verify_current("issuance-1", minimum_generation=1)["ok"])
        self.assertEqual(self.journal_count(1), 1)

    def test_p10_04_writer_supplied_semantic_fields_are_rejected(self):
        forbidden = {
            "op": "issue", "issuance_id": "x", "generation": 1, "scope": SCOPE, "version": VERSION,
            "permit_ledger_digest": "attacker", "reconciliation_digest": "attacker",
            "permit_authority_epoch": 999, "previous_checkpoint_digest": "attacker", "auth_tag": "attacker",
        }
        result = self.signer.call(forbidden)
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "ISSUE_REQUEST_SCHEMA_INVALID")
        self.assertEqual(self.journal_count(), 0)

    def test_p10_05_writer_or_unrelated_key_cannot_forge_checkpoint(self):
        legit = self.signer.issue("issuance-1", 1)
        forged_statement = dict(legit["statement"])
        wrong_tag = hmac.new(PERMIT_INTEGRITY_KEY, _canon(forged_statement), hashlib.sha256).hexdigest()
        forged = {
            "statement": forged_statement,
            "auth_tag": wrong_tag,
            "checkpoint_digest": _digest({"statement": forged_statement, "auth_tag": wrong_tag}),
        }
        decision = self.signer.verify(forged, minimum_generation=1)
        self.assertFalse(decision["ok"])
        self.assertEqual(decision["reason"], "CHECKPOINT_AUTH_FAILED")

    def test_p10_06_issuance_identity_semantic_rebinding_denied(self):
        self.assertTrue(self.signer.issue("issuance-1", 1)["ok"])
        rebound_generation = self.signer.issue("issuance-1", 2)
        self.assertFalse(rebound_generation["ok"])
        self.assertEqual(rebound_generation["reason"], "ISSUANCE_SEMANTIC_REBINDING")
        self.permits.advance_epoch()
        rebound_state = self.signer.issue("issuance-1", 1)
        self.assertFalse(rebound_state["ok"])
        self.assertEqual(rebound_state["reason"], "STATE_DRIFT_REPLAY_DENIED")

    def test_p10_07_same_generation_competing_issuance_denied(self):
        self.assertTrue(self.signer.issue("issuance-1", 1)["ok"])
        conflict = self.signer.issue("issuance-other", 1)
        self.assertFalse(conflict["ok"])

    def test_p10_08_generation_rollback_and_skip_denied(self):
        self.assertTrue(self.signer.issue("issuance-1", 1)["ok"])
        lower = self.signer.issue("lower", 1)
        skip = self.signer.issue("skip", 3)
        self.assertFalse(lower["ok"])
        self.assertFalse(skip["ok"])
        self.assertEqual(skip["reason"], "GENERATION_NOT_EXACT_NEXT")

    def test_p10_09_exact_replay_is_idempotent(self):
        first = self.writer.issue("issuance-1", 1)
        second = self.writer.issue("issuance-1", 1)
        self.assertEqual(first["statement"], second["statement"])
        self.assertEqual(first["checkpoint_digest"], second["checkpoint_digest"])
        self.assertEqual(first["auth_tag"], second["auth_tag"])
        self.assertEqual(self.journal_count(1), 1)

    def test_p10_10_signer_restart_preserves_monotonicity_and_replay(self):
        first = self.writer.issue("issuance-1", 1)
        self.signer.stop()
        self.signer = self.new_signer()
        self.writer = KeylessCompositeWriter(state_db=self.state_db, signer=self.signer)
        replay = self.writer.issue("issuance-1", 1)
        self.assertEqual(first["checkpoint_digest"], replay["checkpoint_digest"])
        self.assertFalse(self.signer.issue("other", 1)["ok"])
        self.assertFalse(self.signer.issue("skip", 3)["ok"])

    def test_p10_11_signer_unavailable_fails_closed_before_writer_mutation(self):
        self.signer.stop(kill=True)
        with self.assertRaises(PermissionError):
            self.writer.issue("issuance-1", 1)
        self.assertEqual(self.journal_count(), 0)

    def test_p10_12_platform_state_drift_invalidates_stale_material(self):
        first = self.writer.issue("issuance-1", 1)
        self.assertTrue(self.writer.verify_current("issuance-1", minimum_generation=1)["ok"])
        self.permits.advance_epoch()
        stale = self.writer.verify_current("issuance-1", minimum_generation=1)
        self.assertFalse(stale["ok"])
        second = self.writer.issue("issuance-2", 2)
        self.assertNotEqual(first["statement"]["permit_authority_epoch"], second["statement"]["permit_authority_epoch"])
        self.assertEqual(second["statement"]["previous_checkpoint_digest"], first["checkpoint_digest"])
        self.assertTrue(self.writer.verify_current("issuance-2", minimum_generation=2)["ok"])

    def test_p10_13_signer_response_mutation_or_substitution_rejected(self):
        legit = self.signer.issue("issuance-1", 1)
        for field, value in (
            ("issuance_id", "other"),
            ("generation", 2),
            ("scope", "OTHER"),
            ("previous_checkpoint_digest", "OTHER"),
            ("permit_ledger_digest", "OTHER"),
        ):
            mutated = json.loads(json.dumps(legit))
            mutated["statement"][field] = value
            decision = self.signer.verify(mutated, minimum_generation=1)
            self.assertFalse(decision["ok"], field)
        tag_mutated = json.loads(json.dumps(legit))
        tag_mutated["auth_tag"] = "0" * 64
        tag_mutated["checkpoint_digest"] = _digest({"statement": tag_mutated["statement"], "auth_tag": tag_mutated["auth_tag"]})
        self.assertFalse(self.signer.verify(tag_mutated, minimum_generation=1)["ok"])

    def test_p10_14_concurrent_writers_cannot_create_duplicate_current_generation(self):
        signer2 = self.new_signer()
        writer2 = KeylessCompositeWriter(state_db=self.state_db, signer=signer2)
        barrier = threading.Barrier(2)
        outcomes = []
        lock = threading.Lock()

        def run(writer, issuance_id):
            barrier.wait()
            try:
                record = writer.issue(issuance_id, 1)
                result = ("ok", issuance_id, record["checkpoint_digest"])
            except PermissionError as exc:
                result = ("denied", issuance_id, str(exc))
            with lock:
                outcomes.append(result)

        t1 = threading.Thread(target=run, args=(self.writer, "issuance-a"))
        t2 = threading.Thread(target=run, args=(writer2, "issuance-b"))
        t1.start(); t2.start(); t1.join(15); t2.join(15)
        signer2.stop(kill=True)
        self.assertFalse(t1.is_alive())
        self.assertFalse(t2.is_alive())
        self.assertEqual(sum(1 for x in outcomes if x[0] == "ok"), 1)
        self.assertEqual(sum(1 for x in outcomes if x[0] == "denied"), 1)
        self.assertEqual(self.journal_count(1), 1)

    def test_p10_15_model_reviewer_writer_authority_remains_zero(self):
        record = self.writer.issue("issuance-1", 1)
        self.assertNotIn("production_authority", record)
        self.assertNotIn("release_authority", record)
        for name in ("deploy", "release", "merge", "approve_release", "mint_production_authority"):
            self.assertFalse(hasattr(self.writer, name))
        self.assertFalse(hasattr(reviews()[0], "mutate_composite_signer"))

    def test_p10_16_clean_higher_generation_liveness_across_restarts(self):
        first = self.writer.issue("issuance-1", 1)
        self.permits.advance_epoch()
        self.signer.stop()
        self.signer = self.new_signer()
        self.writer = KeylessCompositeWriter(state_db=self.state_db, signer=self.signer)
        second = self.writer.issue("issuance-2", 2)
        self.assertEqual(second["statement"]["previous_checkpoint_digest"], first["checkpoint_digest"])
        self.assertEqual(second["statement"]["generation"], 2)
        self.assertTrue(self.writer.verify_current("issuance-2", minimum_generation=2)["ok"])
        self.assertEqual(self.journal_count(1), 1)
        self.assertEqual(self.journal_count(2), 1)


if __name__ == "__main__":
    unittest.main()
