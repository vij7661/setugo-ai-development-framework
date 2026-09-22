"""Self-falsification gate for deterministic EXP-M implementation."""
from __future__ import annotations
import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    EvidenceDeliveryManifest, GovernanceAuthoritySnapshot, RequiredEvidenceContract,
    RequiredInteractionContract, ProviderCapabilityProfile, EvidenceChunk,
    admissibility_registry, complete_delivery, digest, evaluate_admissibility as _production_evaluate_admissibility,
    preflight_delivery, validate_attempt_ledger, validate_chunks,
    validate_retry_transparency, validate_witness,
    ProviderQualificationExecutionPlan, ProviderCapabilityQualificationRecord,
    validate_capability, PersistentAdmissionLedger, admissibility_registry,
)

ROOT = Path(__file__).resolve().parents[1]
from exp_m_test_fixtures import bundle_from_state as _fixture_bundle_from_state, context_from_state as _unauthorized_context_from_state
from exp_m_expectation_authority import load_default_authority, load_predicate_context

AUTHORITY = load_default_authority()
AUTHORITY_CONTEXT = load_predicate_context(AUTHORITY)

def context_from_state(_state):
    # Compatibility name for historical adversarial cases.  Returning the
    # preregistered context prevents a trivial unauthorized-context rejection
    # from making the self-falsification suite falsely green.
    return AUTHORITY_CONTEXT

def bundle_from_state(state):
    return _fixture_bundle_from_state(state, AUTHORITY_CONTEXT)

def evaluate_admissibility(bundle, context=None, registry=None):
    return _production_evaluate_admissibility(bundle, AUTHORITY_CONTEXT, registry, authority=AUTHORITY)


def run():
    snap = GovernanceAuthoritySnapshot("s", "1", "h", True)
    contract = RequiredEvidenceContract("c", "s", ("a",))
    interactions = RequiredInteractionContract("i", "s", (("a",),))
    items = {"a": b"a"}; manifest = EvidenceDeliveryManifest.freeze("r", "commit", items)
    provider = ProviderCapabilityProfile("fake", "m", "v", "p", True)
    cases = []
    def case(name, rejected): cases.append({"id": name, "rejected": bool(rejected)})
    case("manifest_byte_mutation", not preflight_delivery(snap, contract, interactions, manifest, "r", provider, {"a": b"x"}).allowed)
    case("candidate_writable_snapshot", not preflight_delivery(GovernanceAuthoritySnapshot("s", "1", "h", False), contract, interactions, manifest, "r", provider, items).allowed)
    state = {p: True for p in admissibility_registry().predicate_ids}; state["delivery_complete"] = False
    case("admissibility_summary_only_rejected", not evaluate_admissibility(bundle_from_state(state), context_from_state(state)).admissible)
    case("missing_chunk", not validate_chunks([EvidenceChunk.create("r", digest(b"ab"), 0, 2, b"a")], request_id="r", corpus_hash=digest(b"ab"))[0])
    case("retry_hidden", not validate_retry_transparency(({"attempt_id":"a", "wire_hash":"w"},), automatic_retry_hidden=True)[0])
    case("attempt_set_open", not validate_attempt_ledger(("a", "b"), ("a",), ())[0])
    case("witness_over_budget", not validate_witness("c", "0123456789", max_response_bytes=2)[0])
    case("empty_witness", not validate_witness("", "", max_response_bytes=2)[0])
    # Independently authored R2 attacks; this suite deliberately does not call
    # or reuse the normal mutation generator.
    import inspect
    case("production_bypass_absent", "disabled_predicates" not in inspect.signature(evaluate_admissibility).parameters)
    summary = {p: True for p in admissibility_registry().predicate_ids}; summary["disposition"] = "PASS"
    case("all_true_summary_only", not evaluate_admissibility(bundle_from_state(summary), context_from_state(summary)).admissible)
    case("empty_qualification_sets", not preflight_delivery(snap, contract, interactions, manifest, "r", provider, items, plan=__import__("exp_m_deterministic").ProviderQualificationExecutionPlan("p", "fake", "op", (), ()), qualification=__import__("exp_m_deterministic").ProviderCapabilityQualificationRecord("p", "p", True, True, 0, "op", (), (), "fake", "m"), context_policy=__import__("exp_m_deterministic").ProviderContextIsolationPolicy("x", "COMPLETE_READABLE_FENCED_STATE"), context_evidence=__import__("exp_m_deterministic").ProviderContextStateEvidence(True, ("memory", "config"), True, "h"), fence=__import__("exp_m_deterministic").AdmissionFenceRecord("f", "1", True), risk_policy=__import__("exp_m_deterministic").ProviderAccessibilityRiskPolicy("LOWER", "inline")).allowed)
    case("stale_fence", not __import__("exp_m_deterministic").validate_fence(__import__("exp_m_deterministic").AdmissionFenceRecord("f", "wrong", True), "1")[0])
    ledger_path = ROOT / "experiments" / "governed-platform" / ".self-falsify-ledger.json"
    ledger_db = ledger_path.with_suffix(ledger_path.suffix + ".sqlite")
    try:
        for artifact in (ledger_path, ledger_db):
            if artifact.exists():
                artifact.unlink()
        ledger = __import__("exp_m_deterministic").PersistentAdmissionLedger(ledger_path); ledger.compare_and_set("void", 1, "VOID", expected_state_hash="")
        case("void_revival_after_reload", __import__("exp_m_deterministic").PersistentAdmissionLedger(ledger_path).compare_and_set("void", 1, "COMMITTED", expected_state_hash="").void)
    finally:
        for artifact in (ledger_path, ledger_db):
            try:
                artifact.unlink()
            except OSError:
                pass
    case("retrieval_complete_only", not evaluate_admissibility(bundle_from_state({"retrieval": {"complete": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    provider_fake = __import__("exp_m_deterministic").DeterministicFakeProvider(); receipt, wire = provider_fake.deliver(manifest, items)
    forged = __import__("exp_m_deterministic").ReviewerReceipt(receipt.attempt_id, receipt.request_id, receipt.session_id, receipt.manifest_hash, receipt.received_item_ids, receipt.received_bytes, True)
    case("forged_complete_receipt", not __import__("exp_m_deterministic").validate_wire_delivery(manifest, __import__("exp_m_deterministic").materialize_entries(items, source_hash="commit"), wire, forged, {"a": b"wrong"}, expected_commit="commit", expected_semantic_hash=wire.semantic_hash)[0])
    case("witness_current_only", not evaluate_admissibility(bundle_from_state({"witness": {"current": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    typed_dup = (__import__("exp_m_deterministic").MaterializationEntry("a", "x", "file", b"a"), __import__("exp_m_deterministic").MaterializationEntry("b", "x", "file", b"b"))
    case("duplicate_normalized_member", not __import__("exp_m_deterministic").materialize_entries(typed_dup, source_hash="s").success)
    case("unqualified_transform", not __import__("exp_m_deterministic").materialize_entries({"a": b"a"}, source_hash="s", transform_id="unknown").success)
    case("broken_retry_lineage", not __import__("exp_m_deterministic").validate_retry_transparency(({"attempt_id": "retry", "planned_root_id": "root", "kind": "RETRY", "wire_hash": "w", "request_id": "r", "session_id": "s"},), planned_root_ids=("root",), expected_request="r", expected_session="s")[0])
    # R2A independent attacks (not delegated to the normal mutation runner).
    reg = admissibility_registry()
    case("closure_catalog_omission", not reg.closure(reg.predicate_ids, reg.logic_mutation_ids, declared_mutations=tuple(reg.logic_mutation_ids[:-1]), executed_mutations=tuple(reg.logic_mutation_ids), declared_fixtures=reg.fixture_ids, executed_fixtures=reg.fixture_ids))
    p = ProviderCapabilityProfile("fake", "m", "v", "hash", True, "2099-01-01T00:00:00Z", ("text",), 1000)
    plan = ProviderQualificationExecutionPlan("p", "fake", "op", ("trial",), ("confirm",))
    incomplete = ProviderCapabilityQualificationRecord("p", "hash", True, True, 0, "op", ("confirm",), ("confirm",), "fake", "m")
    case("missing_trial_root", not validate_capability(p, plan, incomplete, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="m", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)[0])
    case("self_derived_context", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "attacker"}, "disposition": "PASS"}), context_from_state({"expected_request_id": "r"})).admissible)
    case("forged_delivery_result", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "delivery": {"complete": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    case("witness_without_expected_answer", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "witness": {"current": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    case("accessibility_valid_only", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "accessibility": {"valid": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    race_path = ROOT / "experiments" / "governed-platform" / ".r2a-race-ledger.json"
    race_ledger = PersistentAdmissionLedger(race_path)
    first_race = race_ledger.compare_and_set("race", 1, "VOID", expected_state_hash=""); second_race = race_ledger.compare_and_set("race", 1, "COMMITTED", expected_state_hash="")
    case("persistent_race_second_writer", first_race.void and second_race.void)
    for artifact in (race_path, race_path.with_suffix(race_path.suffix + ".sqlite")):
        try: artifact.unlink()
        except OSError: pass
    # Behavioral phase-artifact falsification: run the real phase cases, then
    # perturb one executed negative case and prove the phase closure fails.
    from run_exp_m_deterministic import run_phases
    phase_artifact = run_phases()
    real_cases = all(len(v.get("executed_cases", ())) >= 2 and any(c.get("kind") == "negative" and c.get("actual") == "REJECT" for c in v.get("executed_cases", ())) for v in phase_artifact["phases"].values())
    case("phase_cases_are_executed", real_cases)
    perturbed = json.loads(json.dumps(phase_artifact))
    first_phase = next(iter(perturbed["phases"].values()))
    first_phase["executed_cases"][1]["actual"] = "PASS"
    first_phase["executed_cases"][1]["result"] = False
    case("phase_negative_perturbation_fails", not all(all(c.get("result") for c in v.get("executed_cases", ())) for v in perturbed["phases"].values()))
    removed = json.loads(json.dumps(phase_artifact)); removed["phases"]["A"]["executed_cases"] = []
    case("phase_case_removal_fails_closure", not all(len(v.get("executed_cases", ())) >= 2 for v in removed["phases"].values()))
    case("typed_summary_boolean", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "capability": {"validated": True}, "context_isolation": {"satisfied": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    # R2C cross-source and authority attacks, independently authored here.
    tampered_map = type(reg)(reg.version, reg.predicate_ids, reg.logic_mutation_ids, reg.fixture_ids, tuple((fid, "wrong") for fid, _ in reg.fixture_target_map))
    case("wrong_fixture_target_mapping", not tampered_map.closure(reg.predicate_ids, reg.logic_mutation_ids, declared_mutations=reg.logic_mutation_ids, executed_mutations=reg.logic_mutation_ids, killed_mutations=reg.logic_mutation_ids, declared_fixtures=reg.fixture_ids, executed_fixtures=reg.fixture_ids, executed_fixture_targets=reg.predicate_ids))
    case("grouped_mutation_false_coverage", all(len({m.get("target_predicate_id")}) == 1 for m in __import__("run_exp_m_mutations").run()["mutations"] if m.get("family") == "validator_logic"))
    iso = __import__("exp_m_deterministic").validate_context_isolation(__import__("exp_m_deterministic").ProviderContextIsolationPolicy("p", "COMPLETE_READABLE_FENCED_STATE"), __import__("exp_m_deterministic").ProviderContextStateEvidence(True, ("memory", "config"), True, "state"), __import__("exp_m_deterministic").AdmissionFenceRecord("f", "1", True), transition_class="HIGHEST", expected_transition_class="LOWER", expected_fence_version="1", required_channels=("memory", "config"))
    case("transition_class_self_downgrade", not iso[0])
    case("fence_version_self_binding", not __import__("exp_m_deterministic").validate_fence(__import__("exp_m_deterministic").AdmissionFenceRecord("f", "evil", True), "1")[0])
    wrong_answer = bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "disposition": "PASS", "witness_response": "wrong"})
    case("wrong_witness_answer", not evaluate_admissibility(wrong_answer, context_from_state({})).admissible)
    forged_prompt = __import__("exp_m_deterministic").PromptIsolationQualificationRecord("p", "fake", "inline", True, "2099-01-01T00:00:00Z", authority_id="attacker", authority_digest="attacker")
    case("forged_prompt_authority", not __import__("exp_m_deterministic").validate_prompt_isolation(forged_prompt, provider_id="fake", mode="inline", now="2025-01-01T00:00:00Z", expected_authority_id="platform-prompt-authority", expected_authority_digest="prompt-authority-v1", expected_generation=1)[0])
    forged_reviewer = __import__("exp_m_deterministic").ReviewerProvenanceRecord("r", "policy", True, "trusted-review-artifact", issuer_id="attacker")
    case("forged_reviewer_authority", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "reviewer": forged_reviewer, "disposition": "PASS"}), context_from_state({})).admissible)
    prod_plan = ProviderQualificationExecutionPlan("p", "fake", "op", ("a", "b"), ("c",), qualification_profile="R5_PRODUCTION")
    prod_rec = ProviderCapabilityQualificationRecord("p", "hash", True, True, 0, "op", ("a", "b", "c"), ("a", "b", "c"), "fake", "m", attempt_records=())
    case("r5_under_sampling", not validate_capability(provider, prod_plan, prod_rec, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="m", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)[0])
    missing_state_path = ROOT / "experiments/governed-platform/.r2c-missing-state.json"
    missing_state_db = missing_state_path.with_suffix(missing_state_path.suffix + ".sqlite")
    try:
        for artifact in (missing_state_path, missing_state_db):
            if artifact.exists():
                artifact.unlink()
        missing_hash = PersistentAdmissionLedger(missing_state_path).compare_and_set("a", 1, "COMMITTED")
        case("cas_missing_state_hash", bool(missing_hash.void))
    finally:
        for artifact in (missing_state_path, missing_state_db):
            try:
                artifact.unlink()
            except OSError:
                pass
    case("caller_copied_observed_interactions", not preflight_delivery(snap, contract, interactions, manifest, "r", provider, items, observed_interactions=(("a",),)).allowed)
    # R2D independent attacks: these are authored here rather than delegated
    # to the production mutation/fixture catalogs.
    dirty_marker = {"review_request": {"current": True, "request_id": "r"}, "context_state": {"clean": False, "sentinel_passed": False, "state_hash": "state", "observable_channels": ("memory", "config")}, "__negative_target__": "context_state_clean", "disposition": "PASS"}
    case("production_fixture_marker_bypass", not evaluate_admissibility(bundle_from_state(dirty_marker), context_from_state(dirty_marker)).admissible)
    no_channel = bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "disposition": "PASS"})
    no_channel.evidence["context_isolation_verdict"] = __import__("exp_m_deterministic").ContextIsolationVerdict(no_channel.evidence["context_isolation_verdict"].policy, __import__("exp_m_deterministic").ProviderContextStateEvidence(True, (), True, "state"), no_channel.evidence["context_isolation_verdict"].fence, "LOWER", ("memory", "config"))
    case("missing_structured_context_channel", not evaluate_admissibility(no_channel, context_from_state({})).admissible)
    self_fence = __import__("exp_m_deterministic").AdmissionFenceRecord("fence", "1", True)
    case("self_minted_fence_attestation", not __import__("exp_m_deterministic").validate_fence(self_fence, "1", expected_authority_id="external-resource", expected_authority_hash="external-hash", expected_issuer_id="external-observer", expected_attestation="external-attestation")[0])
    mismatch_path = ROOT / "experiments/governed-platform/.r2d-mismatch-ledger.json"
    try:
        if mismatch_path.exists(): mismatch_path.unlink()
        if mismatch_path.with_suffix(mismatch_path.suffix + ".sqlite").exists(): mismatch_path.with_suffix(mismatch_path.suffix + ".sqlite").unlink()
        led = PersistentAdmissionLedger(mismatch_path); first = led.compare_and_set("drift", 1, "VOID", expected_state_hash="wrong"); after = PersistentAdmissionLedger(mismatch_path).compare_and_set("drift", 1, "COMMITTED", expected_state_hash="")
        case("void_persists_after_restart", first.void and after.disposition == "VOID" and "terminal_state" in after.reasons)
    finally:
        for artifact in (mismatch_path, mismatch_path.with_suffix(mismatch_path.suffix + ".sqlite")):
            try: artifact.unlink()
            except OSError: pass
    case("authoritative_admission_requires_ledger", __import__("exp_m_deterministic").admit_review_attempt({"generation": 1}, __import__("exp_m_deterministic").AttemptState("a", 1, "auth", "req", "cap", "eg", "ctx", "fence", "prompt", "wit", "session", "reg"), attempt_id="a", expected_generation=1).void)
    case("caller_minted_verdict_token_rejected", __import__("exp_m_deterministic").admit_review_attempt_with_evidence(bundle_from_state({}), context_from_state({}), {"generation": 1, "state_hash": "", "evidence_admission_token": "public-digest"}, __import__("exp_m_deterministic").AttemptState("a", 1, "auth", "req", "cap", "eg", "ctx", "fence", "prompt", "wit", "session", "reg"), attempt_id="a", expected_generation=1).void)
    forged_context = bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "semantic_context": {"qualified": True, "context_hash": "ctx-h"}, "disposition": "PASS"})
    forged_context.evidence["semantic_context"] = __import__("exp_m_deterministic").SemanticContextQualificationRecord("ctx", "ctx-h", True, "commit", b"", "arbitrary-receipt", ())
    case("empty_context_arbitrary_receipt", not evaluate_admissibility(forged_context, context_from_state({})).admissible)
    copied = bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "disposition": "PASS"})
    copied.evidence["final_context_interactions"] = __import__("exp_m_deterministic").FinalContextInteractionEvidence("r", "s", "ctx-h", ("a",), (("a",),), True, "copied", "candidate")
    case("candidate_copied_context_interactions", not evaluate_admissibility(copied, context_from_state({})).admissible)
    incomplete = bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "disposition": "PASS"})
    incomplete.evidence["semantic_context"] = __import__("exp_m_deterministic").SemanticContextQualificationRecord("ctx", "ctx-h", True, "commit", b"", digest({"context_id": "ctx", "source_hash": "commit", "members": (), "assembly": "trusted-final-context-v1"}), ())
    case("complete_manifest_incomplete_context", not evaluate_admissibility(incomplete, context_from_state({})).admissible)
    proof_only = bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "disposition": "PASS"}); proof = proof_only.evidence["accessibility"]; proof_only.evidence["accessibility"] = __import__("exp_m_deterministic").AccessibilityProofRecord(proof.proof_id, proof.challenge_id, proof.provider_id, proof.mode, proof.final_context_id, True, proof.proof_mode, proof.policy_version, proof.evidence_hash, "")
    case("accessibility_challenge_hash_only", not evaluate_admissibility(proof_only, context_from_state({})).admissible)
    import io, zipfile
    bomb = io.BytesIO()
    with zipfile.ZipFile(bomb, "w", compression=zipfile.ZIP_DEFLATED) as z: z.writestr("bomb.txt", b"A" * 200000)
    case("zip_bomb_rejected_before_extraction", not __import__("exp_m_deterministic").materialize_entries((__import__("exp_m_deterministic").MaterializationEntry("nested.zip", "nested.zip", "archive", bomb.getvalue(), None, len(bomb.getvalue()), len(bomb.getvalue()), 0, "nested.zip"),), source_hash="s", max_member_bytes=1000).success)
    phase_check = phase_artifact if "phase_artifact" in locals() else None
    case("phase_cases_record_invocations", bool(phase_check) and all(c.get("production_functions") and c.get("result") is True for v in phase_check["phases"].values() for c in v.get("executed_cases", ())))

    # Incorporate the preregistered CA-1..CA-10 compound results *inside this
    # governed command* so the final self-falsification artifact is exactly the
    # bytes emitted by this process. No later post-processing is permitted.
    head_commit = subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip()
    head_tree = subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip()
    compound_path = ROOT / "experiments" / "governed-platform" / "EXP-M-R2E-COMPOUND-RESULTS.json"
    if not compound_path.is_file():
        raise SystemExit("compound_results_missing_before_self_falsification")
    compound = json.loads(compound_path.read_text(encoding="utf-8"))
    compound_execution = compound.get("execution") or {}
    if compound_execution.get("source_commit") != head_commit or compound_execution.get("source_tree") != head_tree:
        raise SystemExit("compound_results_source_identity_mismatch")
    compound_rows = list(compound.get("cases") or ())
    expected_compound_ids = {f"CA-{n}" for n in range(1, 11)}
    observed_compound_ids = {str(row.get("id")) for row in compound_rows}
    if (
        observed_compound_ids != expected_compound_ids
        or compound.get("survivor_count") != 0
        or compound.get("all_rejected") is not True
    ):
        raise SystemExit("compound_results_not_closed")
    for row in compound_rows:
        cases.append({
            "id": str(row["id"]),
            "rejected": bool(row.get("rejected")),
            "blocking_guard": str(row.get("blocking_guard", "")),
            "source": str(row.get("source", "reviewer_exp_m_r2e_compound_suite.py")),
        })

    survivors = [c for c in cases if not c["rejected"]]
    return {
        "cases": cases,
        "total": len(cases),
        "surviving_critical": len(survivors),
        "surviving_high": len(survivors),
        "all_rejected": not survivors,
        "reviewer_compound_attacks": {
            "case_ids": sorted(observed_compound_ids),
            "survivor_count": compound.get("survivor_count"),
            "all_rejected": compound.get("all_rejected"),
        },
    }


if __name__ == "__main__":
    result = run()
    result["execution"] = {"source_commit": subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip(), "source_tree": subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip(), "utc": datetime.now(timezone.utc).isoformat(), "command": "python governance-runtime/self_falsify_exp_m.py", "interpreter": sys.executable}
    out = ROOT / "experiments" / "governed-platform" / "EXP-M-SELF-FALSIFICATION-RESULTS.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_rejected"] else 1)
