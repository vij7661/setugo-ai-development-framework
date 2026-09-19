"""Unified deterministic EXP-M data/state and validator-logic mutations."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    EvidenceChunk, EvidenceDeliveryManifest, admissibility_registry,
    GovernanceAuthoritySnapshot, RequiredEvidenceContract, RequiredInteractionContract,
    MaterializationResult, ProviderCapabilityProfile, ProviderQualificationExecutionPlan,
    ProviderCapabilityQualificationRecord, ProviderContextIsolationPolicy, ProviderContextStateEvidence,
    AdmissionFenceRecord, RetrievalEvidenceRecord, WitnessProtocolQualificationRecord, AttemptState, DeterministicFakeProvider,
    complete_delivery, evaluate_admissibility, digest, validate_chunks, validate_capability,
    validate_context_isolation, materialize_entries, validate_retrieval, validate_witness_qualification,
    admit_review_attempt, validate_wire_delivery, WireDeliveryRecord, validate_egress, validate_prompt_isolation,
    validate_registry_version, validate_retry_transparency,
)

ROOT = Path(__file__).resolve().parents[1]


def run() -> dict:
    reg = admissibility_registry()
    mutations = []
    base = {
        "review_request": {"current": True, "request_id": "r"}, "authority_snapshot": GovernanceAuthoritySnapshot("s", "1", "h", True),
        "evidence_contract": RequiredEvidenceContract("e", "s", ("a",)), "interaction_contract": RequiredInteractionContract("i", "s", (("a",),)),
        "materialization": MaterializationResult(True, {"a": b"a"}, "rep", "src", "raw-v1"), "representation": {"governed": True, "transform_id": "raw-v1"},
        "egress": {"authorized": True, "version": "1"}, "capability_current": True, "accessibility_policy": {"satisfied": True}, "accessibility": {"satisfied": True, "proven": True},
        "context_isolation": {"satisfied": True}, "hidden_state_policy": {"satisfied": True}, "context_state": {"clean": True, "sentinel_passed": True},
        "fence": {"current": True, "version": "1"}, "semantic_context": {"qualified": True}, "wire": {"valid": True}, "delivery": {"complete": True},
        "witness": {"current": True}, "retrieval": {"complete": True}, "prompt_isolation": {"current": True}, "semantic_coverage": {"complete": True},
        "reviewer": {"trusted": True}, "disposition": "PASS", "disposition_promotable": True,
    }
    def negative(state, predicate):
        s = dict(state)
        mapping = {
            "review_request_current": ("review_request", {"current": False, "request_id": "r"}),
            "authority_snapshot_current": ("authority_snapshot", GovernanceAuthoritySnapshot("s", "1", "h", False)),
            "evidence_contract_closed": ("evidence_contract", RequiredEvidenceContract("e", "s", (), non_vacuous=False)),
            "interaction_contract_closed": ("interaction_contract", RequiredInteractionContract("i", "s", (), closed=False)),
            "materialization_complete": ("materialization", MaterializationResult(False, {}, "", "src", "raw-v1")),
            "representation_governed": ("representation", {"governed": False, "transform_id": ""}),
            "egress_authorized": ("egress", {"authorized": False, "version": "1"}),
            "capability_current": ("capability_current", False), "accessibility_policy_satisfied": ("accessibility_policy", {"satisfied": False}),
            "context_isolation_satisfied": ("context_isolation", {"satisfied": False}), "hidden_state_policy_satisfied": ("hidden_state_policy", {"satisfied": False}),
            "context_state_clean": ("context_state", {"clean": False, "sentinel_passed": False}), "admission_fence_current": ("fence", {"current": False, "version": "1"}),
            "semantic_context_qualified": ("semantic_context", {"qualified": False}), "wire_binding_valid": ("wire", {"valid": False}),
            "delivery_complete": ("delivery", {"complete": False}), "accessibility_proven": ("accessibility", {"satisfied": True, "proven": False}),
            "witness_record_current": ("witness", {"current": False}), "session_retrieval_coverage": ("retrieval", {"complete": False}),
            "prompt_isolation_current": ("prompt_isolation", {"current": False}), "semantic_coverage": ("semantic_coverage", {"complete": False}),
            "reviewer_provenance": ("reviewer", {"trusted": False}), "disposition_promotable": ("disposition", "CHANGES_REQUIRED"),
        }
        key, value = mapping[predicate]; s[key] = value; return s
    for predicate in reg.logic_mutation_ids:
        negative_state = negative(base, predicate)
        mutated_result = evaluate_admissibility(negative_state, reg, disabled_predicates=(predicate,))
        normal_result = evaluate_admissibility(negative_state, reg)
        mutations.append({"id": f"TM-O-{predicate}", "family": "validator_logic", "target": predicate, "expected": "REJECT", "actual": "PASS" if mutated_result.admissible else "REJECT", "negative_control": "REJECT" if not normal_result.admissible else "PASS", "killed": mutated_result.admissible})
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
    context_ok, context_reasons = validate_context_isolation(ProviderContextIsolationPolicy("p", "COMPLETE_READABLE_FENCED_STATE"), ProviderContextStateEvidence(False, ("memory",), False, ""), AdmissionFenceRecord("f", "1", False), transition_class="HIGHEST", required_channels=("memory", "config"))
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
    rejected = sum(1 for m in mutations if m["killed"])
    return {"experiment": "EXP-M", "total_mutations": len(mutations), "rejected_mutations": rejected, "surviving_mutations": len(mutations) - rejected, "all_rejected": rejected == len(mutations), "mutations": mutations}


if __name__ == "__main__":
    result = run()
    path = ROOT / "experiments" / "governed-platform" / "EXP-M-MUTATION-RESULTS.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_rejected"] else 1)
