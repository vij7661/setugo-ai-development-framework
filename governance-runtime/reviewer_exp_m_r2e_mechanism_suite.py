"""Externally prompted R2E mechanism-integrity suite.

Preregistered after the independent review that found CA-7/CA-8 test-oracle
shortcuts and before the corresponding verifier remediation. This suite is
intentionally independent of the legacy simulated compound cases. Every case
mutates real input/state and invokes the unchanged production/verifier path.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path

from exp_m_deterministic import (
    EvidenceBundle,
    EvidenceDeliveryManifest,
    MaterializationEntry,
    MaterializationResult,
    PersistentAdmissionLedger,
    PhysicalAttemptRecord,
    PredicateContext,
    ProviderCapabilityProfile,
    ProviderCapabilityQualificationRecord,
    ProviderQualificationExecutionPlan,
    RetrievalEvidenceRecord,
    ReviewerReceipt,
    WireDeliveryRecord,
    digest,
    evaluate_admissibility,
    materialize_entries,
    validate_capability,
    validate_retrieval,
    validate_wire_delivery,
)
from exp_m_expectation_authority import load_default_authority, load_predicate_context
from exp_m_test_fixtures import bundle_from_state
from verify_exp_m_prior_evidence import verify_prior_evidence_index
from verify_exp_m_sep_sequence import REVIEWER_SUITE_ANCHORS, verify_reviewer_suite_frozen

ROOT = Path(__file__).resolve().parents[1]
PRIOR_REVIEW_PATH = "experiments/governed-platform/EXP-M-R2E-EXTERNAL-REVIEW-R2.md"


def _git(*args: str, input_bytes: bytes | None = None, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        ("git",) + args,
        cwd=ROOT,
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=True,
    )
    return completed.stdout.decode().strip()


def _git_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(("git", "show", f"{commit}:{path}"), cwd=ROOT)


def _synthetic_commit(
    base: str,
    *,
    replace: dict[str, bytes] | None = None,
    delete: tuple[str, ...] = (),
    message: str,
) -> str:
    replace = replace or {}
    with tempfile.TemporaryDirectory() as td:
        env = dict(os.environ)
        env.update({
            "GIT_INDEX_FILE": str(Path(td) / "index"),
            "GIT_AUTHOR_NAME": "exp-m-adversary",
            "GIT_AUTHOR_EMAIL": "exp-m-adversary@invalid",
            "GIT_COMMITTER_NAME": "exp-m-adversary",
            "GIT_COMMITTER_EMAIL": "exp-m-adversary@invalid",
            "GIT_AUTHOR_DATE": "2001-01-01T00:00:00Z",
            "GIT_COMMITTER_DATE": "2001-01-01T00:00:00Z",
        })
        _git("read-tree", base, env=env)
        for path in delete:
            _git("update-index", "--force-remove", "--", path, env=env)
        for path, raw in replace.items():
            blob = _git("hash-object", "-w", "--stdin", input_bytes=raw)
            _git("update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", env=env)
        tree = _git("write-tree", env=env)
        return _git("commit-tree", tree, "-p", base, input_bytes=(message + "\n").encode(), env=env)


class MechanismIntegrityCompoundSuite(unittest.TestCase):
    def setUp(self):
        self.authority = load_default_authority()
        self.context = load_predicate_context(self.authority)
        self.source = _git("rev-parse", "HEAD")

    def test_ca1_real_forged_context_reaches_production_authority_check(self):
        forged_context = PredicateContext(**{
            name: getattr(self.context, name)
            for name in self.context.__dataclass_fields__
            if name != "expectation_manifest_hash"
        }, expectation_manifest_hash=self.context.expectation_manifest_hash)
        state = {"review_request": {"current": True, "request_id": self.context.request_id},
                 "delivery": {"complete": True}, "disposition": "PASS"}
        bundle = bundle_from_state(state, self.context)
        verdict = evaluate_admissibility(bundle, forged_context, authority=self.authority)
        self.assertFalse(verdict.admissible)
        self.assertIn("expectation_authority_invalid", verdict.reasons)

    def test_ca2_real_mismatched_evidence_token_reaches_cas_verifier(self):
        with tempfile.TemporaryDirectory() as td:
            ledger = PersistentAdmissionLedger(Path(td) / "ledger")
            ledger.seed_protected_state(1, "s1")
            original = {"evidence": {"bundle": "A"}, "generation": 1, "state_hash": "s1"}
            wrong = {"evidence": {"bundle": "B"}, "generation": 1, "state_hash": "s1"}
            cp = ledger.commit_with_verdict(
                "a", 1, "COMMITTED",
                expected_state_hash="s1",
                expected_evidence_token=digest(original),
                verdict_payload=wrong,
            )
            self.assertTrue(cp.void)
            self.assertIn("evidence_token_mismatch", cp.reasons)

    def test_ca3_real_fabricated_delivery_commit_reaches_authority_check(self):
        fake = "f" * 40
        items = {"a": b"a"}
        manifest = EvidenceDeliveryManifest.freeze(self.context.request_id, fake, items)
        materialized = MaterializationResult(True, items, digest({"a": digest(b"a")}), fake, "raw-v1")
        wire = WireDeliveryRecord(self.context.attempt_id, self.context.request_id, "w", "w", self.context.session_id, ("a",))
        receipt = ReviewerReceipt(self.context.attempt_id, self.context.request_id, self.context.session_id, manifest.manifest_hash, ("a",), 1, True)
        ok, reasons = validate_wire_delivery(manifest, materialized, wire, receipt, items, expected_commit=fake, authority=self.authority)
        self.assertFalse(ok)
        self.assertIn("authority_reviewed_commit_mismatch", reasons)

    def test_ca4_real_forged_retrieval_and_delivery_bytes_reach_validators(self):
        forged = b"forged"
        retrieval = RetrievalEvidenceRecord(
            self.context.request_id, self.context.attempt_id, self.context.session_id,
            self.context.retrieval_source, self.context.retrieval_version,
            0, len(forged), digest(forged), len(forged), "tool", 1,
            self.context.final_context_id, self.context.final_context_hash,
        )
        retrieval_ok, _ = validate_retrieval(
            retrieval,
            expected_request=self.context.request_id,
            expected_attempt=self.context.attempt_id,
            expected_session=self.context.session_id,
            expected_source=self.context.retrieval_source,
            expected_version=self.context.retrieval_version,
            expected_context_id=self.context.final_context_id,
            expected_context_hash=self.context.final_context_hash,
            authority=self.authority,
        )
        items = {"a": b"a"}
        commit = self.authority.resolve_reviewed_commit()
        manifest = EvidenceDeliveryManifest.freeze(self.context.request_id, commit, items)
        materialized = MaterializationResult(True, items, digest({"a": digest(b"a")}), commit, "raw-v1")
        wire = WireDeliveryRecord(self.context.attempt_id, self.context.request_id, "w", "w", self.context.session_id, ("a",))
        receipt = ReviewerReceipt(self.context.attempt_id, self.context.request_id, self.context.session_id, manifest.manifest_hash, ("a",), len(forged), True)
        delivery_ok, _ = validate_wire_delivery(manifest, materialized, wire, receipt, {"a": forged}, expected_commit=commit, authority=self.authority)
        self.assertFalse(retrieval_ok or delivery_ok)

    def test_ca5_real_archive_and_schedule_inputs_reach_production_validators(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("../escape", b"x")
        mat = materialize_entries((MaterializationEntry("payload.bin", "payload.bin", "file", buf.getvalue()),), source_hash="s")
        protocol = self.authority.load_r5_protocol()
        n = int(protocol["n_min"])
        ids = tuple(f"a{i}" for i in range(n))
        plan = ProviderQualificationExecutionPlan(
            "r5", "fake", "default", ids[:1], ids[1:], "R5_PRODUCTION", "seed",
            ("d1", "d2", "d3"), ("b1", "b2", "b3", "b4"), "env",
        )
        attempts = tuple(
            PhysicalAttemptRecord(x, x, None, "FIRST", "r", "s", "w" + x, "OK", utc_day="d1", time_block="b1")
            for x in ids
        )
        profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True, supported_formats=("text",), max_context_bytes=1000000)
        record = ProviderCapabilityQualificationRecord("r5", "profile-hash", True, True, 0, "default", ids, ids, "fake", "deterministic", attempt_records=attempts)
        cap_ok, cap_reasons = validate_capability(
            profile, plan, record, now="2026-01-01T00:00:00Z",
            expected_provider="fake", expected_model="deterministic", expected_operating_point="default",
            expected_profile_hash="profile-hash", required_format="text", required_context_bytes=1,
            authority=self.authority,
        )
        self.assertFalse(mat.success)
        self.assertFalse(cap_ok)
        self.assertTrue(any("schedule" in reason for reason in cap_reasons))

    def test_ca6_real_unauthorized_plan_reaches_authority_validator(self):
        profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True, supported_formats=("text",), max_context_bytes=1000000)
        plan = ProviderQualificationExecutionPlan("not-authorized", "fake", "default", ("x",), ("x",))
        record = ProviderCapabilityQualificationRecord(
            "not-authorized", "profile-hash", True, True, 0, "default",
            ("x",), ("x",), "fake", "deterministic",
            attempt_records=(PhysicalAttemptRecord("x", "x", None, "FIRST", "r", "s", "w", "OK"),),
        )
        ok, reasons = validate_capability(
            profile, plan, record, now="2026-01-01T00:00:00Z",
            expected_provider="fake", expected_model="deterministic", expected_operating_point="default",
            expected_profile_hash="profile-hash", required_format="text", required_context_bytes=1,
            authority=self.authority,
        )
        self.assertFalse(ok)
        self.assertIn("qualification_authority_plan_missing", reasons)

    def test_ca7_real_deleted_indexed_artifact_reaches_unmodified_prior_verifier(self):
        mutant = _synthetic_commit(
            self.source,
            delete=(PRIOR_REVIEW_PATH,),
            message="adversary: delete indexed prior review",
        )
        ok, reasons = verify_prior_evidence_index(
            index_commit=self.source,
            source_commit=self.source,
            packet_commit=mutant,
        )
        self.assertFalse(ok)
        self.assertIn("indexed_prior_artifact_deleted_after_source_freeze", reasons)

    def test_ca8_real_reviewer_suite_mutation_reaches_unmodified_freeze_verifier(self):
        target = "governance-runtime/reviewer_exp_m_r2e_authority_suite.py"
        original = _git_bytes(self.source, target)
        mutant = _synthetic_commit(
            self.source,
            replace={target: original + b"\n# adversarial mutation\n"},
            message="adversary: mutate frozen reviewer suite",
        )
        source_files = {
            path: hashlib.sha256(_git_bytes(self.source, path)).hexdigest()
            for path, _ in REVIEWER_SUITE_ANCHORS
        }
        synthetic_freeze = {
            "source_commit": mutant,
            "source_files": source_files,
        }
        ok, reasons = verify_reviewer_suite_frozen(
            source_commit=str(synthetic_freeze["source_commit"]),
            source_files=dict(synthetic_freeze["source_files"]),
        )
        self.assertFalse(ok)
        self.assertTrue(
            "reviewer_suite_hash_drift" in reasons
            or "reviewer_suite_preregister_hash_drift" in reasons
        )

    def test_ca9_real_caller_pass_reaches_derived_disposition(self):
        verdict = evaluate_admissibility(EvidenceBundle({"disposition": "PASS"}), self.context, authority=self.authority)
        self.assertFalse(verdict.admissible)
        self.assertFalse(verdict.predicate_results.get("disposition_promotable", True))

    def test_ca10_real_protocol_unavailable_state_reaches_production_validator(self):
        broken = type(self.authority)(
            self.authority.root_commit,
            self.authority.root_hash,
            self.authority.root,
            False,
        )
        profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True, supported_formats=("text",), max_context_bytes=1000000)
        plan = ProviderQualificationExecutionPlan("r5", "fake", "default", ("a",), ("b",), "R5_PRODUCTION")
        record = ProviderCapabilityQualificationRecord("r5", "profile-hash", True, True, 0, "default", ("a", "b"), ("a", "b"), "fake", "deterministic")
        ok, reasons = validate_capability(
            profile, plan, record, now="2026-01-01T00:00:00Z",
            expected_provider="fake", expected_model="deterministic", expected_operating_point="default",
            expected_profile_hash="profile-hash", required_format="text", required_context_bytes=1,
            authority=broken,
        )
        self.assertFalse(ok)
        self.assertIn("r5_protocol_unavailable", reasons)

    def test_integrity_no_simulation_or_forced_outcome_shortcuts_in_authoritative_suite(self):
        source = Path(__file__).read_text(encoding="utf-8")
        forbidden = ("simulate_", "force_", "mock_", "with_missing_r5_protocol_for_test")
        for token in forbidden:
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
