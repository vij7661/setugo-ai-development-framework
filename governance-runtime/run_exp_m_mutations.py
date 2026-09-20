"""Unified deterministic EXP-M data/state and validator-logic mutations."""
from __future__ import annotations
import json
import sys
import subprocess
import multiprocessing
import pickle
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    EvidenceChunk, EvidenceDeliveryManifest, admissibility_registry,
    ReviewerReceipt,
    GovernanceAuthoritySnapshot, RequiredEvidenceContract, RequiredInteractionContract,
    MaterializationResult, ProviderCapabilityProfile, ProviderQualificationExecutionPlan,
    ProviderCapabilityQualificationRecord, ProviderContextIsolationPolicy, ProviderContextStateEvidence,
    AdmissionFenceRecord, RetrievalEvidenceRecord, WitnessProtocolQualificationRecord, AttemptState, DeterministicFakeProvider,
    complete_delivery, evaluate_admissibility, digest, validate_chunks, validate_capability,
    validate_context_isolation, materialize_entries, validate_retrieval, validate_witness_qualification,
    admit_review_attempt, validate_wire_delivery, WireDeliveryRecord, validate_egress, validate_prompt_isolation,
    validate_registry_version, validate_retry_transparency,
    AccessibilityProofRecord, ReviewerProvenanceRecord, SemanticCoverageRecord, DeliveryCompletenessResult,
    RepresentationRecord,
    PhysicalAttemptRecord,
)

ROOT = Path(__file__).resolve().parents[1]
from exp_m_review_fixtures import FIXTURE_CATALOG, build_negative_fixture
from exp_m_test_fixtures import bundle_from_state
from exp_m_expectation_authority import load_default_authority, load_predicate_context

AUTHORITY = load_default_authority()
FROZEN_MUTATION_CONTEXT = load_predicate_context(AUTHORITY)


def evaluate(state, registry):
    # Mutation fixtures are evaluated against this independently frozen
    # context; expected identities are never derived from the mutated state.
    return evaluate_admissibility(bundle_from_state(state, FROZEN_MUTATION_CONTEXT), FROZEN_MUTATION_CONTEXT, registry, authority=AUTHORITY)


def _mutated_evaluate(predicate, state, registry):
    import exp_m_deterministic as production
    original = production._predicate_validators
    def mutated_validators(context, _original=original, _predicate=predicate):
        validators = _original(context)
        # R2C requires one exact production guard per isolated mutant.  No
        # grouped family is counted as coverage for an individual predicate.
        validators[_predicate] = lambda _state: True
        return validators
    production._predicate_validators = mutated_validators
    try:
        result = evaluate(state, registry)
        return {"admissible": result.admissible, "reasons": list(result.reasons), "predicate_results": dict(result.predicate_results)}
    finally:
        production._predicate_validators = original


def isolated_mutant_result(predicate, state, registry):
    work = ROOT / "experiments" / "governed-platform" / ".exp-m-mutants"
    work.mkdir(parents=True, exist_ok=True)
    stem = predicate.replace("/", "_")
    payload = work / f"{stem}.pkl"; result_path = work / f"{stem}.json"
    payload.write_bytes(pickle.dumps((predicate, state, registry)))
    completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--isolated-worker", str(payload), str(result_path)], cwd=ROOT, timeout=15)
    if completed.returncode != 0 or not result_path.exists(): return None
    return json.loads(result_path.read_text(encoding="utf-8"))


def run() -> dict:
    reg = admissibility_registry()
    mutations = []
    base = {
        "review_request": {"current": True, "request_id": FROZEN_MUTATION_CONTEXT.request_id}, "authority_snapshot": GovernanceAuthoritySnapshot(FROZEN_MUTATION_CONTEXT.authority_snapshot_id, FROZEN_MUTATION_CONTEXT.authority_version, FROZEN_MUTATION_CONTEXT.authority_snapshot_hash, True),
        "evidence_contract": RequiredEvidenceContract("e", FROZEN_MUTATION_CONTEXT.authority_snapshot_id, ("a",)), "interaction_contract": RequiredInteractionContract("i", FROZEN_MUTATION_CONTEXT.authority_snapshot_id, (("a",),)),
        "materialization": MaterializationResult(True, {"a": b"a"}, "rep", "src", "raw-v1"), "representation": RepresentationRecord("raw-v1", "1", "transform", "registry-exp-m-r1", "src", "rep", "params", "coverage"),
        "egress": {"authorized": True, "version": "1"}, "capability": {"validated": True}, "accessibility_policy": {"satisfied": True, "risk_policy_version": "r1"}, "accessibility": AccessibilityProofRecord("proof", "ch", "fake", "inline", "ctx", True),
        "context_isolation": {"satisfied": True, "transition_class": "LOWER"}, "hidden_state_policy": {"satisfied": True}, "context_state": {"clean": True, "sentinel_passed": True, "state_hash": "state"},
        "fence": {"current": True, "version": "1"}, "semantic_context": {"qualified": True, "context_hash": "ctx-h"}, "wire": WireDeliveryRecord("a", "r", "w", "s", "s", ("a",)), "delivery": DeliveryCompletenessResult(True),
        "witness": WitnessProtocolQualificationRecord("w", "fake", "inline", 100, True, "prompt", "2099-01-01T00:00:00Z"), "retrieval": RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, 1, digest(b"a"), 1, "tool", 1, "ctx", "ctx-h"), "retrieval_bytes": b"a", "prompt_isolation": {"current": True}, "semantic_coverage": SemanticCoverageRecord("cov", "ctx", True),
        "reviewer": ReviewerProvenanceRecord("reviewer", "policy", True), "disposition": "PASS", "disposition_promotable": True,
    }
    fixture_by_target = {str(row["target_predicate_id"]): row for row in FIXTURE_CATALOG}
    for predicate in reg.logic_mutation_ids:
        fixture = fixture_by_target.get(predicate)
        if fixture is None or str(fixture.get("fixture_id")) != f"negative:{predicate}":
            raise AssertionError(f"fixture_catalog_mismatch:{predicate}")
        negative_state = build_negative_fixture(base, predicate)
        normal_result = evaluate(negative_state, reg)
        # Each mutant is executed in a fresh spawned process/module instance.
        mutated_payload = isolated_mutant_result(predicate, negative_state, reg)
        mutated_result = type("Result", (), {
            "admissible": bool(mutated_payload and mutated_payload["admissible"]),
            "reasons": tuple(mutated_payload.get("reasons", ()) if mutated_payload else ("isolated_mutant_failed",)),
            "predicate_results": dict(mutated_payload.get("predicate_results", {}) if mutated_payload else {}),
        })()
        # A validator-logic mutant is killed when the exact target guard
        # demonstrably changes from rejecting to accepting its independently
        # frozen negative fixture.  Overall admission may still reject because
        # another required predicate intentionally provides redundant defense.
        target_flipped = (
            normal_result.predicate_results.get(predicate) is False
            and mutated_result.predicate_results.get(predicate) is True
        )
        mutations.append({"id": f"TM-O-{predicate}", "family": "validator_logic", "target": predicate, "target_predicate_id": predicate, "negative_fixture_id": str(fixture["fixture_id"]), "negative_fixture_target_id": str(fixture["target_predicate_id"]), "fixture_constructor": str(fixture["constructor"]), "expected_rejection_predicate": str(fixture["expected_rejection"]), "executed": True, "fixture_hash": digest(negative_state), "expected": "TARGET_GUARD_FLIPS", "actual": "TARGET_GUARD_FLIPPED" if target_flipped else "TARGET_GUARD_NOT_FLIPPED", "negative_control": "REJECT" if not normal_result.admissible else "PASS", "killed": target_flipped, "normal_reasons": list(normal_result.reasons), "mutated_reasons": list(mutated_result.reasons)})
    corpus = b"abcdefghij"; corpus_hash = digest(corpus)
    chunks = [EvidenceChunk.create("request", corpus_hash, 0, 2, corpus[:5]), EvidenceChunk.create("request", corpus_hash, 1, 2, corpus[5:])]
    data_mutations = [
        ("missing_chunk", chunks[:1]),
        ("wrong_request", [EvidenceChunk.create("other", corpus_hash, 0, 2, corpus[:5]), chunks[1]]),
        ("wrong_corpus", [EvidenceChunk.create("request", "wrong", 0, 2, corpus[:5]), chunks[1]]),
        ("duplicate_index", [chunks[0], chunks[0]]),
        ("corrupt_chunk", [EvidenceChunk("request", corpus_hash, 0, 2, b"xxxxx", chunks[0].chunk_hash), chunks[1]]),
        ("empty_chunk", [EvidenceChunk.create("request", corpus_hash, 0, 2, b""), chunks[1]]),
    ]
    for name, candidate in data_mutations:
        ok = validate_chunks(candidate, request_id="request", corpus_hash=corpus_hash)[0]
        mutations.append({"id": f"TM-G-{name}", "family": "data_state", "target": name, "expected": "REJECT", "actual": "PASS" if ok else "REJECT", "killed": not ok})
    profile = ProviderCapabilityProfile("fake", "deterministic", "v", "hash", True, "2099-01-01T00:00:00Z", ("text",), 1000)
    plan = ProviderQualificationExecutionPlan("p", "fake", "op", ("a",), ("a",))
    record = ProviderCapabilityQualificationRecord("p", "hash", True, True, 0, "op", ("a",), ("a",), "fake", "deterministic")
    capability_cases = [
        ("expired_profile", ProviderCapabilityProfile("fake", "deterministic", "v", "hash", True, "2000-01-01T00:00:00Z", ("text",), 1000), "profile_expired"),
        ("wrong_profile_hash", ProviderCapabilityProfile("fake", "deterministic", "v", "wrong", True, "2099-01-01T00:00:00Z", ("text",), 1000), "profile_hash_mismatch"),
        ("wrong_operating_point", plan, "operating_point_mismatch"),
        ("missing_attempt", ProviderCapabilityQualificationRecord("p", "hash", True, True, 0, "op", (), (), "fake", "deterministic"), "qualification_attempt_closure"),
        ("unsupported_format", profile, "unsupported_format"),
    ]
    for name, changed, expected_reason in capability_cases:
        if name == "wrong_operating_point":
            ok, reasons = validate_capability(profile, changed, record, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="other", expected_profile_hash="hash", required_format="text", required_context_bytes=1)
        elif name == "missing_attempt":
            ok, reasons = validate_capability(profile, plan, changed, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)
        elif name == "unsupported_format":
            ok, reasons = validate_capability(ProviderCapabilityProfile("fake", "deterministic", "v", "hash", True, "2099-01-01T00:00:00Z", ("json",), 1000), plan, record, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)
        else:
            ok, reasons = validate_capability(changed, plan, record, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)
        mutations.append({"id": f"TM-R1-{name}", "family": "data_state", "target": name, "expected": "REJECT", "actual": "REJECT" if not ok else "PASS", "reasons": list(reasons), "killed": not ok and expected_reason in reasons})
    context_ok, context_reasons = validate_context_isolation(ProviderContextIsolationPolicy("p", "COMPLETE_READABLE_FENCED_STATE"), ProviderContextStateEvidence(False, ("memory",), False, ""), AdmissionFenceRecord("f", "1", False), transition_class="HIGHEST", expected_transition_class="LOWER", expected_fence_version="1", required_channels=("memory", "config"))
    mutations.append({"id": "TM-R1-context-isolation", "family": "data_state", "target": "dirty_hidden_stale_context", "expected": "REJECT", "actual": "REJECT" if not context_ok else "PASS", "reasons": list(context_reasons), "killed": not context_ok})
    mutations.append({"id": "TM-R1-materialization-traversal", "family": "data_state", "target": "materialization", "expected": "REJECT", "actual": "REJECT" if not materialize_entries({"../escape": b"x"}, source_hash="s").success else "PASS", "killed": not materialize_entries({"../escape": b"x"}, source_hash="s").success})
    wire_items = {"a": b"a"}; wire_manifest = EvidenceDeliveryManifest.freeze("r", "source-commit", wire_items); receipt, wire = DeterministicFakeProvider().deliver(wire_manifest, wire_items)
    wire_ok, wire_reasons = validate_wire_delivery(wire_manifest, materialize_entries(wire_items, source_hash="wrong-source"), wire, receipt, wire_items, expected_commit="source-commit", expected_semantic_hash=wire.semantic_hash)
    mutations.append({"id": "TM-R1-wrong-reviewed-source", "family": "data_state", "target": "reviewed_commit", "expected": "REJECT", "actual": "REJECT" if not wire_ok else "PASS", "reasons": list(wire_reasons), "killed": not wire_ok})
    raw = b"payload"; retrieval = RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, len(raw), digest(raw), len(raw), "tool", 1, "ctx", "ctx-h")
    retrieval_ok, retrieval_reasons = validate_retrieval(retrieval, b"wrong", expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v", expected_context_id="ctx", expected_context_hash="ctx-h")
    mutations.append({"id": "TM-R1-retrieval-bytes", "family": "data_state", "target": "retrieval_returned_bytes", "expected": "REJECT", "actual": "REJECT" if not retrieval_ok else "PASS", "reasons": list(retrieval_reasons), "killed": not retrieval_ok})
    witness = WitnessProtocolQualificationRecord("w", "fake", "inline", 4, True, "prompt", "2000-01-01T00:00:00Z")
    witness_ok, witness_reasons = validate_witness_qualification(witness, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="ok", challenge="extract", final_context_bytes=1, max_final_context_bytes=100)
    mutations.append({"id": "TM-R1-witness-expired", "family": "data_state", "target": "witness_qualification", "expected": "REJECT", "actual": "REJECT" if not witness_ok else "PASS", "reasons": list(witness_reasons), "killed": not witness_ok})
    expected_attempt = AttemptState("a", 1, "auth", "req", "cap", "eg", "ctx", "fence", "prompt", "wit", "session", "reg")
    admission = admit_review_attempt({"generation": 2, "authority_version": "auth", "request_version": "req", "capability_hash": "cap", "egress_version": "eg", "context_hash": "ctx", "fence_version": "fence", "prompt_hash": "prompt", "witness_hash": "wit", "session_hash": "session", "registry_version": "reg"}, expected_attempt, attempt_id="a", expected_generation=1)
    mutations.append({"id": "TM-R1-admission-drift", "family": "data_state", "target": "atomic_admission_generation", "expected": "REJECT", "actual": "REJECT" if admission.void else "PASS", "reasons": list(admission.reasons), "killed": admission.void})
    # R1 integration gates: each mutation exercises the production validator on
    # evidence that would otherwise permit a false-green review.
    egress_ok, egress_reasons = validate_egress({"authorized": False, "version": "1"}, "1")
    mutations.append({"id": "TM-R1-egress-revoked", "family": "data_state", "target": "egress", "expected": "REJECT", "actual": "REJECT" if not egress_ok else "PASS", "reasons": list(egress_reasons), "killed": not egress_ok})
    prompt = __import__("exp_m_deterministic").PromptIsolationQualificationRecord("p", "fake", "inline", True, "2000-01-01T00:00:00Z")
    prompt_ok, prompt_reasons = validate_prompt_isolation(prompt, provider_id="fake", mode="inline", now="2025-01-01T00:00:00Z")
    mutations.append({"id": "TM-R1-prompt-isolation-expired", "family": "data_state", "target": "prompt_isolation", "expected": "REJECT", "actual": "REJECT" if not prompt_ok else "PASS", "reasons": list(prompt_reasons), "killed": not prompt_ok})
    retry_ok, retry_reasons = validate_retry_transparency([{"attempt_id": "a1", "wire_hash": "w"}], automatic_retry_hidden=True)
    mutations.append({"id": "TM-R1-hidden-retry", "family": "data_state", "target": "retry_transparency", "expected": "REJECT", "actual": "REJECT" if not retry_ok else "PASS", "reasons": list(retry_reasons), "killed": not retry_ok})
    retrieval_session = RetrievalEvidenceRecord("r", "a", "wrong-session", "file", "v", 0, len(raw), digest(raw), len(raw), "tool", 1, "ctx", "ctx-h")
    session_ok, session_reasons = validate_retrieval(retrieval_session, raw, expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v", expected_context_id="ctx", expected_context_hash="ctx-h")
    mutations.append({"id": "TM-R1-retrieval-session", "family": "data_state", "target": "retrieval_session", "expected": "REJECT", "actual": "REJECT" if not session_ok else "PASS", "reasons": list(session_reasons), "killed": not session_ok})
    registry_ok, registry_reasons = validate_registry_version("registry-v2", "registry-v1")
    mutations.append({"id": "TM-R1-registry-drift", "family": "data_state", "target": "predicate_registry", "expected": "REJECT", "actual": "REJECT" if not registry_ok else "PASS", "reasons": list(registry_reasons), "killed": not registry_ok})
    bad_wire = WireDeliveryRecord(wire.attempt_id, wire.request_id, wire.wire_hash, "wrong-semantic", wire.session_id, wire.item_ids)
    wire_semantic_ok, wire_semantic_reasons = validate_wire_delivery(wire_manifest, materialize_entries(wire_items, source_hash="source-commit"), bad_wire, receipt, wire_items, expected_commit="source-commit", expected_semantic_hash=wire.semantic_hash)
    mutations.append({"id": "TM-R1-wire-semantic-binding", "family": "data_state", "target": "wire_semantic_hash", "expected": "REJECT", "actual": "REJECT" if not wire_semantic_ok else "PASS", "reasons": list(wire_semantic_reasons), "killed": not wire_semantic_ok})
    summary_state = {p: True for p in reg.predicate_ids}; summary_state["disposition"] = "PASS"
    summary_result = evaluate(summary_state, reg)
    mutations.append({"id": "TM-R2-summary-only", "family": "data_state", "target": "evidence_bundle", "expected": "REJECT", "actual": "REJECT" if not summary_result.admissible else "PASS", "reasons": list(summary_result.reasons), "killed": not summary_result.admissible})
    mismatch_plan = ProviderQualificationExecutionPlan("other", "fake", "op", ("a",), ("a",))
    plan_ok, plan_reasons = validate_capability(profile, mismatch_plan, record, now="2025-01-01T00:00:00Z", expected_provider="fake", expected_model="deterministic", expected_operating_point="op", expected_profile_hash="hash", required_format="text", required_context_bytes=1)
    mutations.append({"id": "TM-R2-plan-record-mismatch", "family": "data_state", "target": "qualification_plan_id", "expected": "REJECT", "actual": "REJECT" if not plan_ok else "PASS", "reasons": list(plan_reasons), "killed": not plan_ok})
    forged_receipt = ReviewerReceipt(receipt.attempt_id, receipt.request_id, receipt.session_id, receipt.manifest_hash, receipt.received_item_ids, receipt.received_bytes, True)
    forged_ok, forged_reasons = validate_wire_delivery(wire_manifest, materialize_entries(wire_items, source_hash="source-commit"), wire, forged_receipt, {"a": b"forged"}, expected_commit="source-commit", expected_semantic_hash=wire.semantic_hash)
    mutations.append({"id": "TM-R2-forged-complete-receipt", "family": "data_state", "target": "receipt_returned_bytes", "expected": "REJECT", "actual": "REJECT" if not forged_ok else "PASS", "reasons": list(forged_reasons), "killed": not forged_ok})
    lineage_ok, lineage_reasons = validate_retry_transparency((PhysicalAttemptRecord("retry", "root", None, "RETRY", "r", "s", "w", "OK"),), planned_root_ids=("root",), expected_request="r", expected_session="s")
    mutations.append({"id": "TM-R2-broken-retry-lineage", "family": "data_state", "target": "retry_lineage", "expected": "REJECT", "actual": "REJECT" if not lineage_ok else "PASS", "reasons": list(lineage_reasons), "killed": not lineage_ok})
    logic = [m for m in mutations if m.get("family") == "validator_logic"]
    data_state = [m for m in mutations if m.get("family") == "data_state"]
    validator_logic_total = len(logic)
    validator_logic_killed_count = sum(1 for m in logic if m.get("killed") is True)
    data_state_total = len(data_state)
    data_state_rejected_count = sum(1 for m in data_state if m.get("actual") == "REJECT" and m.get("killed") is True)
    validator_logic_all_killed = validator_logic_killed_count == validator_logic_total
    data_state_all_rejected = data_state_rejected_count == data_state_total
    # Backward-compatible aggregate fields remain diagnostic only.  The
    # authoritative closure gate is the conjunction of the two family-specific
    # semantics above; unlike R2D it never adds unlike meanings together.
    total = validator_logic_total + data_state_total
    closed = validator_logic_all_killed and data_state_all_rejected
    return {"experiment": "EXP-M", "total_mutations": total,
            "rejected_mutations": data_state_rejected_count,
            "surviving_mutations": (validator_logic_total - validator_logic_killed_count) + (data_state_total - data_state_rejected_count),
            "all_rejected": closed,
            "validator_logic_total": validator_logic_total,
            "validator_logic_killed_count": validator_logic_killed_count,
            "validator_logic_all_killed": validator_logic_all_killed,
            "data_state_total": data_state_total,
            "data_state_rejected_count": data_state_rejected_count,
            "data_state_all_rejected": data_state_all_rejected,
            "mutations": mutations,
            "declared_mutation_targets": list(reg.logic_mutation_ids),
            "executed_mutation_targets": sorted({m["target_predicate_id"] for m in logic if m.get("executed")}),
            "killed_mutation_targets": sorted({m["target_predicate_id"] for m in logic if m.get("executed") and m.get("killed")}),
            "declared_fixture_targets": sorted({m["negative_fixture_target_id"] for m in logic}),
            "executed_fixture_targets": sorted({m["negative_fixture_target_id"] for m in logic if m.get("executed")}),
            "verdict_predicate_ids": list(reg.predicate_ids)}


if __name__ == "__main__" and len(sys.argv) >= 4 and sys.argv[1] == "--isolated-worker":
    predicate, state, registry = pickle.loads(Path(sys.argv[2]).read_bytes())
    Path(sys.argv[3]).write_text(json.dumps(_mutated_evaluate(predicate, state, registry)), encoding="utf-8")
    raise SystemExit(0)

if __name__ == "__main__":
    result = run()
    result["execution"] = {"source_commit": subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=ROOT, text=True).strip(), "source_tree": subprocess.check_output(("git", "rev-parse", "HEAD^{tree}"), cwd=ROOT, text=True).strip(), "utc": datetime.now(timezone.utc).isoformat(), "command": "python governance-runtime/run_exp_m_mutations.py", "interpreter": sys.executable}
    path = ROOT / "experiments" / "governed-platform" / "EXP-M-MUTATION-RESULTS.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_rejected"] else 1)
