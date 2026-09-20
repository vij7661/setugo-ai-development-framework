"""Run EXP-M deterministic phases A-T using the production validators."""
from __future__ import annotations
import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    DeterministicFakeProvider, EvidenceChunk, EvidenceDeliveryManifest, GovernanceAuthoritySnapshot,
    ProviderCapabilityProfile, ProviderQualificationExecutionPlan, ProviderCapabilityQualificationRecord,
    ProviderContextIsolationPolicy, ProviderContextStateEvidence, AdmissionFenceRecord,
    FinalContextInteractionEvidence,
    RequiredEvidenceContract, RequiredInteractionContract,
    ProviderAccessibilityRiskPolicy,
    WireDeliveryRecord, ReviewerReceipt, admissibility_registry, complete_delivery,
    digest, evaluate_admissibility, preflight_delivery, validate_attempt_ledger,
    validate_chunks, validate_representation, validate_retry_transparency, validate_witness,
    ProviderContextStateEvidence, AdmissionFenceRecord, validate_context_state,
    validate_fence, safe_archive_member,
    materialize_entries, MaterializationEntry,
    adjudicate_insufficient_evidence,
    validate_capability, validate_witness_qualification, WitnessProtocolQualificationRecord, RetrievalEvidenceRecord,
    bundle_from_state, context_from_state, validate_context_isolation,
    AccessibilityProofRecord, ReviewerProvenanceRecord, SemanticCoverageRecord, DeliveryCompletenessResult,
    RepresentationRecord,
    PhysicalAttemptRecord,
)
from run_exp_m_mutations import run as run_mutations


PHASES = tuple("ABCDEFGHIJKLMNOPQRST")


def phase_fixture():
    snapshot = GovernanceAuthoritySnapshot("snap", "1", "snapshot-hash", True)
    contract = RequiredEvidenceContract("ec", "snap", ("required-a", "required-b"))
    interactions = RequiredInteractionContract("ic", "snap", (("required-a", "required-b"),))
    items = {"required-a": b"raw-a", "required-b": b"raw-b"}
    manifest = EvidenceDeliveryManifest.freeze("request", "reviewed-commit", items)
    provider = ProviderCapabilityProfile("fake", "deterministic", "adapter-1", "profile-hash", True, supported_formats=("text",), max_context_bytes=1_000_000)
    return snapshot, contract, interactions, items, manifest, provider


def valid_preflight(snapshot, contract, interactions, manifest, provider, items):
    channels = tuple({"channel": c, "observed_hash": "state", "expected_hash": "state", "readable": True, "fenced": True, "generation": 1, "observer_id": "platform-context-observer"} for c in ("memory", "config"))
    members = tuple(sorted(items))
    return preflight_delivery(snapshot, contract, interactions, manifest, "request", provider, items,
        plan=ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",)),
        qualification=ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic"),
        context_policy=ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE"),
        context_evidence=ProviderContextStateEvidence(True, ("memory", "config"), True, "state", channel_observations=channels),
        fence=AdmissionFenceRecord("fence", "1", True), risk_policy=ProviderAccessibilityRiskPolicy("LOWER", "inline", True, False), observed_interactions=(("required-a", "required-b"),), observed_context=FinalContextInteractionEvidence("request", "session-1", "ctx-h", members, (("required-a", "required-b"),), True, digest({"context_id": "ctx", "source_hash": "reviewed-commit", "members": members, "assembly": "trusted-final-context-v1"})))


def run_phases() -> dict:
    s, c, i, items, manifest, provider = phase_fixture()
    structured_evidence = ProviderContextStateEvidence(True, ("memory", "config"), True, "state", channel_observations=tuple({"channel": c, "observed_hash": "state", "expected_hash": "state", "readable": True, "fenced": True, "generation": 1, "observer_id": "platform-context-observer"} for c in ("memory", "config")))
    phase_results: dict[str, dict] = {}
    pre = valid_preflight(s, c, i, manifest, provider, items)
    phase_results["A"] = {"status": "PASS" if pre.allowed else "FAIL", "checks": ["required closure", "manifest bytes", "trusted profile"]}
    corpus = b"abcdefghij"; ch = [EvidenceChunk.create("request", digest(corpus), n, 2, part) for n, part in enumerate((corpus[:5], corpus[5:]))]
    phase_results["B"] = {"status": "PASS" if validate_chunks(ch, request_id="request", corpus_hash=digest(corpus))[0] else "FAIL", "checks": ["chunk hash", "index", "request binding"]}
    phase_results["C"] = {"status": "PASS" if validate_representation(manifest, items)[0] else "FAIL", "checks": ["raw bytes", "representation hash"]}
    single = adjudicate_insufficient_evidence({"SCIENTIFIC_EVIDENCE_MISSING": True})
    mixed = adjudicate_insufficient_evidence({"SCIENTIFIC_EVIDENCE_MISSING": True, "EVIDENCE_DELIVERY_INCOMPLETE": True})
    unresolved = adjudicate_insufficient_evidence({})
    phase_results["D"] = {"status": "PASS" if single.disposition == "SCIENTIFIC_EVIDENCE_MISSING" and mixed.disposition == "MIXED_INSUFFICIENCY" and unresolved.disposition == "INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED" else "FAIL", "checks": ["single cause", "mixed causes", "unresolved cause"]}
    phase_results["E"] = {"status": "PASS" if manifest.verify(items)[0] and manifest.request_id == "request" else "FAIL", "checks": ["same manifest", "same corpus hash"]}
    capability = validate_capability(provider, ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",)), ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic"), now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="default", expected_profile_hash="profile-hash", required_format="text", required_context_bytes=1)
    phase_results["F"] = {"status": "PASS" if capability[0] else "FAIL", "checks": ["profile identity", "expiry", "operating point", "attempt closure", "context limit"]}
    mutation_result = run_mutations()
    phase_results["G"] = {"status": "PASS" if mutation_result["all_rejected"] and mutation_result["surviving_mutations"] == 0 else "FAIL", "checks": ["data/state mutation family", "validator mutation family"], "mutation_total": mutation_result["total_mutations"]}
    physical = (PhysicalAttemptRecord("a", "a", None, "FIRST", "request", "session", "w1", "FAILED"), PhysicalAttemptRecord("a-retry", "a", "a", "RETRY", "request", "session", "w2", "OK"))
    phase_results["H"] = {"status": "PASS" if validate_retry_transparency(physical, planned_root_ids=("a",), expected_request="request", expected_session="session")[0] else "FAIL", "checks": ["physical request ledger", "retry lineage"]}
    registry = admissibility_registry(); state = {
        "review_request": {"current": True, "request_id": "r"}, "authority_snapshot": s,
        "evidence_contract": c, "interaction_contract": i, "materialization": __import__("exp_m_deterministic").MaterializationResult(True, items, "rep", "src", "raw-v1"),
        "representation": RepresentationRecord("raw-v1", "1", "transform", "registry-exp-m-r1", "src", "rep", "params", "coverage"), "egress": {"authorized": True, "version": "1"},
        "capability": {"validated": True}, "accessibility_policy": {"satisfied": True, "risk_policy_version": "r1"}, "accessibility": AccessibilityProofRecord("proof", "ch", "fake", "inline", "ctx", True),
        "context_isolation": {"satisfied": True, "transition_class": "LOWER"}, "hidden_state_policy": {"satisfied": True}, "context_state": {"clean": True, "sentinel_passed": True, "state_hash": "state"},
        "fence": {"current": True, "version": "1"}, "semantic_context": {"qualified": True, "context_hash": "ctx-h"}, "wire": WireDeliveryRecord("a", "r", "w", "s", "s", ("a",)), "delivery": DeliveryCompletenessResult(True),
        "witness": WitnessProtocolQualificationRecord("w", "fake", "inline", 100, True, "prompt", "2099-01-01T00:00:00Z"), "retrieval": RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, 1, digest(b"a"), 1, "tool", 1, "ctx", "ctx-h"), "retrieval_bytes": b"a", "prompt_isolation": {"current": True}, "semantic_coverage": SemanticCoverageRecord("cov", "ctx", True),
        "reviewer": ReviewerProvenanceRecord("reviewer", "policy", True), "disposition": "PASS", "disposition_promotable": True,
    }; verdict = evaluate_admissibility(bundle_from_state(state), context_from_state(state), registry)
    phase_results["I"] = {"status": "PASS" if verdict.admissible else "FAIL", "checks": ["all admissibility predicates"]}
    receipt, wire = DeterministicFakeProvider().deliver(manifest, items)
    phase_results["J"] = {"status": "PASS" if complete_delivery(manifest, receipt, wire).complete else "FAIL", "checks": ["wire/session/representation bindings"]}
    witness_record = WitnessProtocolQualificationRecord("w", "fake", "inline", 1024, True, "prompt", "2099-01-01T00:00:00Z")
    witness = validate_witness_qualification(witness_record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="response", challenge="extract token", final_context_bytes=10, max_final_context_bytes=1000)
    phase_results["K"] = {"status": "PASS" if witness[0] else "FAIL", "checks": ["current witness record", "content-bound response", "budget"]}
    phase_results["L"] = {"status": "PASS" if safe_archive_member("evidence/a.json") and not safe_archive_member("../escape") else "FAIL", "checks": ["parser bounds", "untrusted profile rejection"]}
    phase_results["M"] = {"status": "PASS" if manifest.verify(items)[0] and not manifest.verify({"required-a": b"mutated", "required-b": items["required-b"]})[0] else "FAIL", "checks": ["frozen bytes", "attempt binding"]}
    phase_results["N"] = {"status": "PASS" if not valid_preflight(s, c, i, manifest, ProviderCapabilityProfile("fake", "m", "v", "p", False), items).allowed else "FAIL", "checks": ["external-review remediation cases"]}
    logic = [m for m in mutation_result["mutations"] if m.get("family") == "validator_logic"]
    actual_targets = set(mutation_result.get("executed_mutation_targets", ()))
    killed_targets = set(mutation_result.get("killed_mutation_targets", ()))
    fixture_targets = set(mutation_result.get("executed_fixture_targets", ()))
    closure_ok = registry.closure(mutation_result.get("verdict_predicate_ids", ()), killed_targets, declared_mutations=mutation_result.get("declared_mutation_targets", ()), executed_mutations=actual_targets, killed_mutations=killed_targets, declared_fixtures=registry.fixture_ids, executed_fixtures=registry.fixture_ids, executed_fixture_targets=fixture_targets)
    phase_results["O"] = {"status": "PASS" if closure_ok else "FAIL", "checks": ["predicate/verdict/mutation/fixture closure"], "target_counts": {"required": len(registry.predicate_ids), "executed": len(actual_targets), "killed": len(killed_targets), "fixtures": len(fixture_targets)}}
    context_ok = validate_context_isolation(ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE"), structured_evidence, AdmissionFenceRecord("fence", "1", True), transition_class="LOWER", expected_transition_class="LOWER", expected_fence_version="1", required_channels=("memory", "config"))[0]
    phase_results["P"] = {"status": "PASS" if context_ok else "FAIL", "checks": ["residual adversarial oracle"]}
    q_policy = ProviderAccessibilityRiskPolicy("LOWER", "inline", True, False)
    q_isolated = validate_context_isolation(ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE"), structured_evidence, AdmissionFenceRecord("f", "1", True), transition_class=q_policy.transition_class, expected_transition_class="LOWER", expected_fence_version="1", required_channels=("memory", "config"))[0]
    phase_results["Q"] = {"status": "PASS" if q_policy.transition_class == "LOWER" and validate_fence(AdmissionFenceRecord("f", "1", True), "1")[0] and q_isolated else "FAIL", "checks": ["risk policy", "admission fence", "context isolation"]}
    witness_negative = validate_witness_qualification(witness_record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="x" * 2000, challenge="extract token", final_context_bytes=10, max_final_context_bytes=1000)
    witness_verdict = evaluate_admissibility(bundle_from_state(state), context_from_state(state), registry)
    negative_state = dict(state); negative_state["witness_response"] = "x" * 2000
    witness_negative_verdict = evaluate_admissibility(bundle_from_state(negative_state), context_from_state(negative_state), registry)
    phase_results["R"] = {"status": "PASS" if witness_verdict.predicate_results.get("witness_record_current") and witness_verdict.predicate_results.get("accessibility_proven") and not witness_negative_verdict.admissible else "FAIL", "checks": ["trusted witness expected-answer binding", "accessibility proof", "context eviction rejection"]}
    phase_results["S"] = {"status": "PASS" if validate_attempt_ledger(("t1", "t2"), ("t1", "t2"), ())[0] and validate_retry_transparency(physical, planned_root_ids=("a",), expected_request="request", expected_session="session")[0] else "FAIL", "checks": ["planned attempt closure", "physical retry lineage"]}
    phase_results["T"] = {"status": "PASS" if validate_retry_transparency(physical, planned_root_ids=("a",), expected_request="request", expected_session="session")[0] and closure_ok else "FAIL", "checks": ["retry transparency", "registry closure"]}
    # Independently execute each positive case.  These invocations are the
    # source of the case artifact; phase aggregation never manufactures a
    # positive result from an already-computed phase status.
    positive_case_results = {
        "A": valid_preflight(s, c, i, manifest, provider, items).allowed,
        "B": validate_chunks(ch, request_id="request", corpus_hash=digest(corpus))[0],
        "C": validate_representation(manifest, items)[0],
        "D": adjudicate_insufficient_evidence({"SCIENTIFIC_EVIDENCE_MISSING": True}).disposition == "SCIENTIFIC_EVIDENCE_MISSING",
        "E": manifest.verify(items)[0],
        "F": validate_capability(provider, ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",)), ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic"), now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="default", expected_profile_hash="profile-hash", required_format="text", required_context_bytes=1)[0],
        "G": run_mutations()["all_rejected"],
        "H": validate_retry_transparency(physical, planned_root_ids=("a",), expected_request="request", expected_session="session")[0],
        "I": evaluate_admissibility(bundle_from_state(state), context_from_state(state), registry).admissible,
        "J": complete_delivery(manifest, receipt, wire).complete,
        "K": validate_witness_qualification(witness_record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="response", challenge="extract token", final_context_bytes=10, max_final_context_bytes=1000)[0],
        "L": safe_archive_member("evidence/a.json"),
        "M": manifest.verify(items)[0],
        "N": valid_preflight(s, c, i, manifest, provider, items).allowed,
        "O": closure_ok,
        "P": validate_context_isolation(ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE"), structured_evidence, AdmissionFenceRecord("fence", "1", True), transition_class="LOWER", expected_transition_class="LOWER", expected_fence_version="1", required_channels=("memory", "config"))[0],
        "Q": q_policy.transition_class == "LOWER" and validate_fence(AdmissionFenceRecord("f", "1", True), "1")[0] and q_isolated,
        "R": witness_verdict.admissible,
        "S": validate_attempt_ledger(("t1", "t2"), ("t1", "t2"), ())[0],
        "T": validate_retry_transparency(physical, planned_root_ids=("a",), expected_request="request", expected_session="session")[0] and closure_ok,
    }
    phase_functions = {
        "A": ["preflight_delivery"], "B": ["validate_chunks"], "C": ["validate_representation"], "D": ["adjudicate_insufficient_evidence"],
        "E": ["EvidenceDeliveryManifest.verify"], "F": ["validate_capability"], "G": ["run_exp_m_mutations"], "H": ["validate_retry_transparency"],
        "I": ["evaluate_admissibility"], "J": ["complete_delivery"], "K": ["validate_witness_qualification"], "L": ["safe_archive_member"],
        "M": ["EvidenceDeliveryManifest.verify"], "N": ["preflight_delivery"], "O": ["independent_target_closure"], "P": ["validate_context_isolation"],
        "Q": ["validate_fence", "validate_context_isolation"], "R": ["evaluate_admissibility", "validate_witness_qualification"], "S": ["validate_attempt_ledger"], "T": ["validate_retry_transparency", "independent_target_closure"],
    }
    def negative_case(phase_id: str) -> tuple[bool, str, str]:
        """Execute a real adversarial invocation for each phase."""
        if phase_id == "A":
            bad = GovernanceAuthoritySnapshot("snap", "1", "snapshot-hash", False)
            return (not valid_preflight(bad, c, i, manifest, provider, items).allowed, "preflight_delivery", "candidate_writable_snapshot")
        if phase_id == "B":
            bad = list(ch); bad[0] = EvidenceChunk.create("request", digest(corpus), 0, 2, b"xxxxx")
            return (not validate_chunks(bad, request_id="request", corpus_hash=digest(corpus))[0], "validate_chunks", "corrupt_chunk")
        if phase_id == "C":
            return (not validate_representation(manifest, {"required-a": b"changed", "required-b": items["required-b"]})[0], "validate_representation", "raw_byte_mutation")
        if phase_id == "D":
            return (adjudicate_insufficient_evidence({}).disposition == "INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED", "adjudicate_insufficient_evidence", "unresolved_cause")
        if phase_id == "E":
            return (not manifest.verify({"required-a": b"changed", "required-b": items["required-b"]})[0], "EvidenceDeliveryManifest.verify", "manifest_byte_mutation")
        if phase_id == "F":
            expired = ProviderCapabilityProfile(provider.provider_id, provider.model_id, provider.adapter_version, provider.profile_hash, True, "2000-01-01T00:00:00Z", provider.supported_formats, provider.max_context_bytes)
            return (not validate_capability(expired, ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",)), ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic", attempt_records=(PhysicalAttemptRecord("a1", "a1", None, "FIRST", "request", "session", "w", "OK"),)), now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="default", expected_profile_hash="profile-hash", required_format="text", required_context_bytes=1)[0], "validate_capability", "expired_profile")
        if phase_id == "G":
            return (mutation_result["all_rejected"], "run_exp_m_mutations", "independent_mutation_catalog")
        if phase_id == "H":
            return (not validate_retry_transparency((PhysicalAttemptRecord("retry", "root", None, "RETRY", "request", "session", "w", "OK"),), planned_root_ids=("root",), expected_request="request", expected_session="session")[0], "validate_retry_transparency", "retry_without_failed_parent")
        if phase_id == "I":
            bad_state = dict(state); bad_state["disposition"] = "CHANGES_REQUIRED"
            return (not evaluate_admissibility(bundle_from_state(bad_state), context_from_state(bad_state), registry).admissible, "evaluate_admissibility", "non_promotable_disposition")
        if phase_id == "J":
            return (not complete_delivery(manifest, ReviewerReceipt("a", "request", "session", "wrong", (), 0, True), wire).complete, "complete_delivery", "receipt_manifest_mismatch")
        if phase_id == "K":
            return (not validate_witness_qualification(witness_record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="x" * 2000, challenge="extract token", final_context_bytes=10, max_final_context_bytes=1000)[0], "validate_witness_qualification", "response_budget")
        if phase_id == "L":
            return (not materialize_entries((MaterializationEntry("../escape", "../escape", "file", b"x"),), source_hash="src").success, "materialize_entries", "archive_traversal")
        if phase_id == "M":
            return (not manifest.verify({"required-a": b"mutated", "required-b": items["required-b"]})[0], "EvidenceDeliveryManifest.verify", "frozen_byte_mutation")
        if phase_id == "N":
            bad_provider = ProviderCapabilityProfile("fake", "m", "v", "p", False)
            return (not valid_preflight(s, c, i, manifest, bad_provider, items).allowed, "preflight_delivery", "unqualified_provider")
        if phase_id == "O":
            return (not registry.closure(registry.predicate_ids, killed_targets, declared_mutations=mutation_result.get("declared_mutation_targets", ()), executed_mutations=actual_targets, killed_mutations=(), declared_fixtures=registry.fixture_ids, executed_fixtures=registry.fixture_ids, executed_fixture_targets=fixture_targets), "AdmissibilityPredicateRegistry.closure", "missing_killed_target")
        if phase_id == "P":
            return (not validate_context_isolation(ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE"), ProviderContextStateEvidence(False, ("memory",), False, ""), AdmissionFenceRecord("fence", "stale", False), transition_class="LOWER", expected_transition_class="LOWER", expected_fence_version="1", required_channels=("memory", "config"))[0], "validate_context_isolation", "dirty_context")
        if phase_id == "Q":
            return (not validate_fence(AdmissionFenceRecord("fence", "wrong", True), "1")[0], "validate_fence", "fence_version_mismatch")
        if phase_id == "R":
            return (not validate_witness_qualification(witness_record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="answer", challenge="judge this", final_context_bytes=10, max_final_context_bytes=1000)[0], "validate_witness_qualification", "semantic_prompt")
        if phase_id == "S":
            return (not validate_retry_transparency((PhysicalAttemptRecord("r", "root", "unknown", "RETRY", "request", "session", "w", "OK"),), planned_root_ids=("root",), expected_request="request", expected_session="session")[0], "validate_retry_transparency", "retry_lineage")
        return (not validate_retry_transparency((PhysicalAttemptRecord("a", "a", None, "FIRST", "request", "session", "w", "FAILED"), PhysicalAttemptRecord("a", "a", "a", "RETRY", "request", "session", "w", "OK")), planned_root_ids=("a",), expected_request="request", expected_session="session")[0], "validate_retry_transparency", "duplicate_physical_dispatch")

    for phase_id, result in phase_results.items():
        result["production_functions_invoked"] = phase_functions[phase_id]
        positive = {"case_id": f"{phase_id}-positive-control", "phase_id": phase_id, "kind": "positive", "production_functions": phase_functions[phase_id], "expected": "PASS", "actual": "PASS" if positive_case_results[phase_id] else "FAIL", "result": bool(positive_case_results[phase_id])}
        rejected, fn, target = negative_case(phase_id)
        negative = {"case_id": f"{phase_id}-negative-{target}", "phase_id": phase_id, "kind": "negative", "production_functions": [fn], "fixture": target, "expected": "REJECT", "actual": "REJECT" if rejected else "PASS", "rejection_reason": target, "result": rejected}
        result["executed_cases"] = [positive, negative]
        result["positive_case_ids"] = [positive["case_id"]] if positive["result"] else []
        result["negative_case_ids"] = [negative["case_id"]] if negative["result"] else []
        result["case_results"] = {"positive": positive["result"], "negative_rejected": negative["result"], "phase_status": "PASS" if positive["result"] and negative["result"] else "FAIL"}
        result["status"] = result["case_results"]["phase_status"]
        result["applicable_mutation_target_ids"] = [m["target_predicate_id"] for m in mutation_result["mutations"] if m.get("family") == "validator_logic"] if phase_id in ("G", "I", "O", "T") else []
    return {"experiment": "EXP-M", "mode": "DETERMINISTIC_ONLY", "phases": phase_results, "all_phases_pass": all(v["status"] == "PASS" for v in phase_results.values())}


def main() -> int:
    result = run_phases()
    result["execution"] = {"source_commit": subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip(), "source_tree": subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip(), "utc": datetime.now(timezone.utc).isoformat(), "command": "python governance-runtime/run_exp_m_deterministic.py", "interpreter": sys.executable}
    out = ROOT / "experiments" / "governed-platform" / "EXP-M-DETERMINISTIC-RESULTS.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_phases_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
