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
    admissibility_registry, complete_delivery, digest, evaluate_admissibility,
    preflight_delivery, validate_attempt_ledger, validate_chunks,
    validate_retry_transparency, validate_witness,
    bundle_from_state, context_from_state,
    ProviderQualificationExecutionPlan, ProviderCapabilityQualificationRecord,
    validate_capability, PersistentAdmissionLedger, admissibility_registry,
)

ROOT = Path(__file__).resolve().parents[1]


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
    try:
        if ledger_path.exists(): ledger_path.unlink()
        ledger = __import__("exp_m_deterministic").PersistentAdmissionLedger(ledger_path); ledger.compare_and_set("void", 1, "VOID")
        case("void_revival_after_reload", __import__("exp_m_deterministic").PersistentAdmissionLedger(ledger_path).compare_and_set("void", 1, "COMMITTED").void)
    finally:
        if ledger_path.exists(): ledger_path.unlink()
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
    first_race = race_ledger.compare_and_set("race", 1, "VOID"); second_race = race_ledger.compare_and_set("race", 1, "COMMITTED")
    case("persistent_race_second_writer", first_race.void and second_race.void)
    for artifact in (race_path, race_path.with_suffix(race_path.suffix + ".sqlite")):
        try: artifact.unlink()
        except OSError: pass
    case("synthetic_phase_metadata", "positive_case_ids = [" not in (ROOT / "governance-runtime" / "run_exp_m_deterministic.py").read_text(encoding="utf-8"))
    case("typed_summary_boolean", not evaluate_admissibility(bundle_from_state({"review_request": {"current": True, "request_id": "r"}, "capability": {"validated": True}, "context_isolation": {"satisfied": True}, "disposition": "PASS"}), context_from_state({})).admissible)
    survivors = [c for c in cases if not c["rejected"]]
    return {"cases": cases, "total": len(cases), "surviving_critical": len(survivors), "surviving_high": len(survivors), "all_rejected": not survivors}


if __name__ == "__main__":
    result = run()
    result["execution"] = {"source_commit": subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip(), "source_tree": subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip(), "utc": datetime.now(timezone.utc).isoformat(), "command": "python governance-runtime/self_falsify_exp_m.py", "interpreter": sys.executable}
    out = ROOT / "experiments" / "governed-platform" / "EXP-M-SELF-FALSIFICATION-RESULTS.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_rejected"] else 1)
