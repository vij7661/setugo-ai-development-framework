"""Deterministic EXP-M evidence-delivery governor.

This module is deliberately provider-neutral.  It models the governed delivery
boundary and uses content-addressed, immutable records so fake/adversarial
providers can exercise the same production predicates without external calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict, is_dataclass
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping, Sequence
from pathlib import Path


def canonical_json(value: Any) -> bytes:
    if is_dataclass(value):
        value = asdict(value)
    elif isinstance(value, Mapping):
        value = {k: (asdict(v) if is_dataclass(v) else v) for k, v in value.items()}
    def default(obj: Any) -> Any:
        if is_dataclass(obj): return asdict(obj)
        if isinstance(obj, bytes): return {"__bytes_sha256__": sha256(obj).hexdigest(), "size": len(obj)}
        raise TypeError(type(obj).__name__)
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=default) + "\n").encode()


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value)
    return sha256(raw).hexdigest()


@dataclass(frozen=True)
class GovernanceAuthoritySnapshot:
    snapshot_id: str
    version: str
    content_hash: str
    outside_candidate_write_authority: bool = True
    governing_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class RequiredEvidenceContract:
    contract_id: str
    snapshot_id: str
    required_ids: tuple[str, ...]
    optional_ids: tuple[str, ...] = ()
    closed: bool = True
    non_vacuous: bool = True


@dataclass(frozen=True)
class RequiredInteractionContract:
    contract_id: str
    snapshot_id: str
    interactions: tuple[tuple[str, ...], ...]
    closed: bool = True


@dataclass(frozen=True)
class EvidenceDeliveryManifest:
    request_id: str
    reviewed_commit: str
    items: Mapping[str, Mapping[str, Any]]
    manifest_hash: str

    @staticmethod
    def freeze(request_id: str, reviewed_commit: str, items: Mapping[str, bytes]) -> "EvidenceDeliveryManifest":
        records = {k: {"sha256": sha256(v).hexdigest(), "size": len(v)} for k, v in sorted(items.items())}
        body = {"request_id": request_id, "reviewed_commit": reviewed_commit, "items": records}
        return EvidenceDeliveryManifest(request_id, reviewed_commit, records, digest(body))

    def verify(self, items: Mapping[str, bytes]) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        allowed = set(self.items)
        extras = set(items) - allowed
        if extras:
            reasons.append("unknown_manifest_items:" + ",".join(sorted(extras)))
        if not allowed.issubset(items):
            reasons.append("manifest_item_set_mismatch")
        for item_id, meta in self.items.items():
            raw = items.get(item_id)
            if raw is None:
                continue
            if len(raw) != meta.get("size"):
                reasons.append(f"size_mismatch:{item_id}")
            if sha256(raw).hexdigest() != meta.get("sha256"):
                reasons.append(f"hash_mismatch:{item_id}")
        return not reasons, reasons


@dataclass(frozen=True)
class ProviderCapabilityProfile:
    provider_id: str
    model_id: str
    adapter_version: str
    profile_hash: str
    qualified: bool = False
    expires_at: str | None = None
    supported_formats: tuple[str, ...] = ()
    max_context_bytes: int = 0


@dataclass(frozen=True)
class ProviderQualificationExecutionPlan:
    plan_id: str
    provider_id: str
    operating_point: str
    trial_ids: tuple[str, ...]
    confirmation_ids: tuple[str, ...]


@dataclass(frozen=True)
class ProviderCapabilityQualificationRecord:
    plan_id: str
    profile_hash: str
    statistical_qualified: bool
    all_trials_closed: bool
    hard_failures: int = 0
    operating_point: str = ""
    planned_attempt_ids: tuple[str, ...] = ()
    closed_attempt_ids: tuple[str, ...] = ()
    provider_id: str = ""
    model_id: str = ""
    qualified_at: str | None = None
    attempt_records: tuple[Any, ...] = ()


@dataclass(frozen=True)
class ProviderAccessibilityRiskPolicy:
    transition_class: str
    proof_mode: str
    deterministic_required: bool = True
    residual_risk_allowed: bool = False


@dataclass(frozen=True)
class ProviderContextIsolationPolicy:
    policy_id: str
    basis: str
    hidden_state_allowed: bool = False


@dataclass(frozen=True)
class ProviderContextStateEvidence:
    clean: bool
    observable_channels: tuple[str, ...]
    sentinel_passed: bool
    state_hash: str


@dataclass(frozen=True)
class AdmissionFenceRecord:
    fence_id: str
    version: str
    current: bool


@dataclass(frozen=True)
class PromptIsolationQualificationRecord:
    record_id: str
    provider_id: str
    mode: str
    current: bool
    expires_at: str | None = None


@dataclass(frozen=True)
class WitnessProtocolQualificationRecord:
    record_id: str
    provider_id: str
    mode: str
    max_response_bytes: int
    current: bool
    prompt_isolation_mode: str = ""
    expires_at: str | None = None


@dataclass(frozen=True)
class RetrievalEvidenceRecord:
    request_id: str
    attempt_id: str
    session_id: str
    source_id: str
    source_version: str
    start: int
    end: int
    returned_sha256: str
    returned_length: int
    tool_result_id: str
    sequence: int
    final_context_id: str
    final_context_hash: str


@dataclass(frozen=True)
class MaterializationResult:
    success: bool
    entries: Mapping[str, bytes]
    representation_hash: str
    source_hash: str
    transform_id: str
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class MaterializationEntry:
    raw_name: str
    normalized_path: str
    kind: str = "file"
    data: bytes = b""
    link_target: str | None = None
    compressed_size: int = 0
    uncompressed_size: int = 0
    recursion_depth: int = 0
    source_member_id: str = ""


@dataclass(frozen=True)
class RepresentationRecord:
    transform_id: str
    transform_version: str
    transform_hash: str
    registry_version: str
    source_hash: str
    representation_hash: str
    parameters_hash: str
    coverage_hash: str


@dataclass(frozen=True)
class AttemptState:
    attempt_id: str
    generation: int
    authority_version: str
    request_version: str
    capability_hash: str
    egress_version: str
    context_hash: str
    fence_version: str
    prompt_hash: str
    witness_hash: str
    session_hash: str
    registry_version: str
    invalidated: bool = False


@dataclass(frozen=True)
class PhysicalAttemptRecord:
    attempt_id: str
    planned_root_id: str
    parent_attempt_id: str | None
    kind: str
    request_id: str
    session_id: str
    wire_hash: str
    outcome: str


@dataclass(frozen=True)
class AdmissionCheckpoint:
    attempt_id: str
    generation: int
    disposition: str
    committed: bool
    void: bool
    reasons: tuple[str, ...] = ()


class PersistentAdmissionLedger:
    """Small deterministic JSON ledger with terminal VOID/COMMITTED states."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}\n", encoding="utf-8")

    def _read(self) -> dict[str, Any]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, value: Mapping[str, Any]) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        tmp.replace(self.path)

    def compare_and_set(self, attempt_id: str, generation: int, disposition: str) -> AdmissionCheckpoint:
        data = self._read(); current = data.get(attempt_id)
        if current is not None:
            return AdmissionCheckpoint(attempt_id, int(current["generation"]), str(current["disposition"]), False, current["disposition"] == "VOID", ("terminal_state",))
        if disposition not in ("VOID", "COMMITTED"):
            return AdmissionCheckpoint(attempt_id, generation, "VOID", False, True, ("invalid_terminal_state",))
        data[attempt_id] = {"generation": generation, "disposition": disposition}
        self._write(data)
        return AdmissionCheckpoint(attempt_id, generation, disposition, disposition == "COMMITTED", disposition == "VOID", ())


@dataclass(frozen=True)
class EvidenceChunk:
    request_id: str
    corpus_hash: str
    index: int
    total: int
    data: bytes
    chunk_hash: str

    @staticmethod
    def create(request_id: str, corpus_hash: str, index: int, total: int, data: bytes) -> "EvidenceChunk":
        return EvidenceChunk(request_id, corpus_hash, index, total, data, sha256(data).hexdigest())


@dataclass(frozen=True)
class WireDeliveryRecord:
    attempt_id: str
    request_id: str
    wire_hash: str
    semantic_hash: str
    session_id: str
    item_ids: tuple[str, ...]


@dataclass(frozen=True)
class ReviewerReceipt:
    attempt_id: str
    request_id: str
    session_id: str
    manifest_hash: str
    received_item_ids: tuple[str, ...]
    received_bytes: int
    complete: bool


@dataclass(frozen=True)
class AccessibilityProofRecord:
    proof_id: str
    challenge_id: str
    provider_id: str
    mode: str
    final_context_id: str
    valid: bool


@dataclass(frozen=True)
class ReviewerProvenanceRecord:
    reviewer_id: str
    policy_hash: str
    trusted: bool


@dataclass(frozen=True)
class SemanticCoverageRecord:
    coverage_id: str
    context_id: str
    complete: bool


@dataclass(frozen=True)
class DeliveryCompletenessResult:
    complete: bool
    reasons: tuple[str, ...] = ()
    received_item_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class DeliveryPreflightResult:
    allowed: bool
    reasons: tuple[str, ...] = ()
    manifest_hash: str | None = None


@dataclass(frozen=True)
class InsufficientEvidenceAdjudication:
    disposition: str
    causes: tuple[str, ...]


@dataclass(frozen=True)
class AdmissibilityPredicateRegistry:
    version: str
    predicate_ids: tuple[str, ...]
    logic_mutation_ids: tuple[str, ...]
    fixture_ids: tuple[str, ...]

    def closure(self, verdict_ids: Iterable[str], killed_ids: Iterable[str]) -> bool:
        required = set(self.predicate_ids)
        def targets(values: Iterable[Any]) -> set[str]:
            out = set()
            for value in values:
                if isinstance(value, Mapping):
                    target = value.get("target_predicate_id", value.get("target"))
                    if target is not None and value.get("executed", True) and value.get("killed", True): out.add(str(target))
                else:
                    out.add(str(value))
            return out
        return required == targets(verdict_ids) == targets(killed_ids)


@dataclass(frozen=True)
class LogicMutationRecord:
    mutation_id: str
    target_predicate_id: str
    executed: bool
    killed: bool
    fixture_hash: str


@dataclass(frozen=True)
class NegativeFixtureRecord:
    fixture_id: str
    target_predicate_id: str
    fixture_hash: str


@dataclass(frozen=True)
class VerdictAdmissibilityResult:
    admissible: bool
    disposition: str
    predicate_results: Mapping[str, bool]
    reasons: tuple[str, ...] = ()

    @property
    def predicate_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self.predicate_results))


@dataclass(frozen=True)
class PredicateContext:
    """Immutable expectations bound by the governing request, never by evidence."""
    request_id: str
    attempt_id: str
    session_id: str
    reviewed_commit: str
    authority_snapshot_id: str
    authority_snapshot_hash: str
    authority_version: str
    expected_provider: str
    expected_model: str
    expected_adapter: str
    expected_operating_point: str
    expected_profile_hash: str
    expected_egress_version: str
    transition_class: str
    fence_version: str
    prompt_provider: str
    prompt_mode: str
    witness_provider: str
    witness_mode: str
    witness_prompt_mode: str
    retrieval_source: str
    retrieval_version: str
    final_context_id: str
    final_context_hash: str
    max_context_bytes: int
    predicate_registry_version: str
    promotable_dispositions: tuple[str, ...] = ("PASS",)


@dataclass(frozen=True)
class EvidenceBundle:
    """Immutable evidence-bearing bundle consumed by the production verdict."""
    evidence: Mapping[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        return self.evidence.get(key, default)


def context_from_state(state: Mapping[str, Any]) -> PredicateContext:
    """Test/fixture adapter; production callers must supply frozen context explicitly."""
    return PredicateContext(
        request_id=str(state.get("expected_request_id", "r")),
        attempt_id=str(state.get("expected_attempt_id", "a")),
        session_id=str(state.get("expected_session_id", "s")),
        reviewed_commit=str(state.get("expected_reviewed_commit", "commit")),
        authority_snapshot_id=str(state.get("expected_authority_snapshot_id", getattr(state.get("authority_snapshot"), "snapshot_id", ""))),
        authority_snapshot_hash=str(state.get("expected_authority_snapshot_hash", getattr(state.get("authority_snapshot"), "content_hash", ""))),
        authority_version=str(state.get("expected_authority_version", getattr(state.get("authority_snapshot"), "version", ""))),
        expected_provider=str(state.get("expected_provider", "fake")), expected_model=str(state.get("expected_model", "deterministic")),
        expected_adapter=str(state.get("expected_adapter", "adapter")), expected_operating_point=str(state.get("expected_operating_point", "default")),
        expected_profile_hash=str(state.get("expected_profile_hash", "profile-hash")), expected_egress_version=str(state.get("expected_egress_version", "1")),
        transition_class=str(state.get("transition_class", "LOWER")), fence_version=str(state.get("expected_fence_version", "1")),
        prompt_provider=str(state.get("prompt_provider", "fake")), prompt_mode=str(state.get("prompt_mode", "inline")),
        witness_provider=str(state.get("witness_provider", "fake")), witness_mode=str(state.get("witness_mode", "inline")), witness_prompt_mode=str(state.get("witness_prompt_mode", "prompt")),
        retrieval_source=str(state.get("retrieval_source", "file")), retrieval_version=str(state.get("retrieval_version", "v")),
        final_context_id=str(state.get("final_context_id", "ctx")), final_context_hash=str(state.get("final_context_hash", "ctx-h")),
        max_context_bytes=int(state.get("max_context_bytes", 1_000_000)), predicate_registry_version=str(state.get("predicate_registry_version", "2")),
        promotable_dispositions=tuple(state.get("promotable_dispositions", ("PASS",))),
    )


def bundle_from_state(state: Mapping[str, Any]) -> EvidenceBundle:
    return EvidenceBundle(dict(state))


PREDICATES = (
    "review_request_current", "authority_snapshot_current", "evidence_contract_closed",
    "interaction_contract_closed", "materialization_complete", "representation_governed",
    "egress_authorized", "capability_current", "accessibility_policy_satisfied",
    "context_isolation_satisfied", "hidden_state_policy_satisfied", "context_state_clean",
    "admission_fence_current", "semantic_context_qualified", "wire_binding_valid",
    "delivery_complete", "accessibility_proven", "witness_record_current",
    "session_retrieval_coverage", "prompt_isolation_current", "semantic_coverage",
    "reviewer_provenance", "disposition_promotable",
)

# These are intentionally independent declarations.  They are not derived
# from one shared tuple so closure can detect omissions and aliases.
PREDICATE_DEFINITIONS = tuple({"id": p, "validator": f"validate_{p}"} for p in PREDICATES)
LOGIC_MUTATION_TARGETS = (
    "review_request_current", "authority_snapshot_current", "evidence_contract_closed",
    "interaction_contract_closed", "materialization_complete", "representation_governed",
    "egress_authorized", "capability_current", "accessibility_policy_satisfied",
    "context_isolation_satisfied", "hidden_state_policy_satisfied", "context_state_clean",
    "admission_fence_current", "semantic_context_qualified", "wire_binding_valid",
    "delivery_complete", "accessibility_proven", "witness_record_current",
    "session_retrieval_coverage", "prompt_isolation_current", "semantic_coverage",
    "reviewer_provenance", "disposition_promotable",
)
FIXTURE_IDS = tuple(f"negative:{p}" for p in PREDICATES)


def admissibility_registry() -> AdmissibilityPredicateRegistry:
    return AdmissibilityPredicateRegistry("2", tuple(d["id"] for d in PREDICATE_DEFINITIONS), LOGIC_MUTATION_TARGETS, FIXTURE_IDS)


def _predicate_validators(context: PredicateContext) -> dict[str, Any]:
    def egress_valid(state: Mapping[str, Any]) -> bool:
        egress = state.get("egress")
        if not isinstance(egress, Mapping):
            return False
        return validate_egress(egress, context.expected_egress_version)[0]

    def prompt_valid(state: Mapping[str, Any]) -> bool:
        prompt = state.get("prompt_isolation")
        if isinstance(prompt, PromptIsolationQualificationRecord):
            record = prompt
        elif isinstance(prompt, Mapping):
            record = PromptIsolationQualificationRecord(
                str(prompt.get("record_id", "prompt")),
                str(prompt.get("provider_id", context.prompt_provider)),
                str(prompt.get("mode", context.prompt_mode)),
                prompt.get("current") is True,
                prompt.get("expires_at"),
            )
        else:
            return False
        return validate_prompt_isolation(
            record,
            provider_id=context.prompt_provider,
            mode=context.prompt_mode,
            now=str(state.get("now", "2099-01-01T00:00:00Z")),
        )[0]

    return {
        "review_request_current": lambda s: isinstance(s.get("review_request"), Mapping) and s["review_request"].get("current") is True and s["review_request"].get("request_id") == context.request_id,
        "authority_snapshot_current": lambda s: isinstance(s.get("authority_snapshot"), GovernanceAuthoritySnapshot) and s["authority_snapshot"].outside_candidate_write_authority and s["authority_snapshot"].snapshot_id == context.authority_snapshot_id and s["authority_snapshot"].content_hash == context.authority_snapshot_hash and s["authority_snapshot"].version == context.authority_version,
        "evidence_contract_closed": lambda s: isinstance(s.get("evidence_contract"), RequiredEvidenceContract) and s["evidence_contract"].closed and s["evidence_contract"].non_vacuous,
        "interaction_contract_closed": lambda s: isinstance(s.get("interaction_contract"), RequiredInteractionContract) and s["interaction_contract"].closed and bool(s["interaction_contract"].interactions),
        "materialization_complete": lambda s: isinstance(s.get("materialization"), MaterializationResult) and s["materialization"].success,
        "representation_governed": lambda s: isinstance(s.get("representation"), RepresentationRecord) and s["representation"].transform_id in QUALIFIED_TRANSFORMS and s["representation"].registry_version == QUALIFIED_TRANSFORMS[s["representation"].transform_id] and bool(s["representation"].source_hash) and bool(s["representation"].representation_hash) and bool(s["representation"].parameters_hash) and bool(s["representation"].coverage_hash),
        "egress_authorized": egress_valid,
        "capability_current": lambda s: isinstance(s.get("capability"), Mapping) and s["capability"].get("validated") is True,
        "accessibility_policy_satisfied": lambda s: isinstance(s.get("accessibility_policy"), Mapping) and s["accessibility_policy"].get("satisfied") is True and s["accessibility_policy"].get("risk_policy_version") is not None,
        "context_isolation_satisfied": lambda s: isinstance(s.get("context_isolation"), Mapping) and s["context_isolation"].get("satisfied") is True and s["context_isolation"].get("transition_class") == context.transition_class,
        "hidden_state_policy_satisfied": lambda s: isinstance(s.get("hidden_state_policy"), Mapping) and s["hidden_state_policy"].get("satisfied") is True,
        "context_state_clean": lambda s: isinstance(s.get("context_state"), Mapping) and s["context_state"].get("clean") is True and s["context_state"].get("sentinel_passed") is True and bool(s["context_state"].get("state_hash")),
        "admission_fence_current": lambda s: isinstance(s.get("fence"), Mapping) and s["fence"].get("current") is True and s["fence"].get("version") == context.fence_version,
        "semantic_context_qualified": lambda s: isinstance(s.get("semantic_context"), Mapping) and s["semantic_context"].get("qualified") is True and s["semantic_context"].get("context_hash") == context.final_context_hash,
        "wire_binding_valid": lambda s: isinstance(s.get("wire"), WireDeliveryRecord) and s["wire"].request_id == context.request_id and bool(s["wire"].wire_hash) and bool(s["wire"].semantic_hash),
        "delivery_complete": lambda s: isinstance(s.get("delivery"), DeliveryCompletenessResult) and s["delivery"].complete,
        "accessibility_proven": lambda s: isinstance(s.get("accessibility"), AccessibilityProofRecord) and s["accessibility"].valid and s["accessibility"].challenge_id and s["accessibility"].final_context_id == context.final_context_id,
        "witness_record_current": lambda s: isinstance(s.get("witness"), WitnessProtocolQualificationRecord) and s["witness"].current and s["witness"].provider_id == context.witness_provider and s["witness"].mode == context.witness_mode,
        "session_retrieval_coverage": lambda s: isinstance(s.get("retrieval"), RetrievalEvidenceRecord) and validate_retrieval(s["retrieval"], s.get("retrieval_bytes", b""), expected_request=context.request_id, expected_attempt=context.attempt_id, expected_session=context.session_id, expected_source=context.retrieval_source, expected_version=context.retrieval_version, expected_context_id=context.final_context_id, expected_context_hash=context.final_context_hash)[0],
        "prompt_isolation_current": prompt_valid,
        "semantic_coverage": lambda s: isinstance(s.get("semantic_coverage"), SemanticCoverageRecord) and s["semantic_coverage"].complete and s["semantic_coverage"].context_id == context.final_context_id,
        "reviewer_provenance": lambda s: isinstance(s.get("reviewer"), ReviewerProvenanceRecord) and s["reviewer"].trusted and bool(s["reviewer"].policy_hash),
        "disposition_promotable": lambda s: s.get("disposition") in context.promotable_dispositions,
    }


def _validate_disposition(state: Mapping[str, Any], context: PredicateContext, predicate_results: Mapping[str, bool]) -> bool:
    return state.get("disposition") in context.promotable_dispositions and all(v for k, v in predicate_results.items() if k != "disposition_promotable")


def evaluate_admissibility(bundle: EvidenceBundle, context: PredicateContext, registry: AdmissibilityPredicateRegistry | None = None) -> VerdictAdmissibilityResult:
    registry = registry or admissibility_registry()
    validators = _predicate_validators(context)
    state = bundle.evidence
    predicates = {pid: bool(validators[pid](state)) for pid in registry.predicate_ids if pid != "disposition_promotable"}
    reasons = tuple(pid for pid, ok in predicates.items() if not ok)
    # Disposition validation is evaluated against the complete result, not a
    # caller-provided summary field.
    if "disposition_promotable" in registry.predicate_ids:
        predicates["disposition_promotable"] = _validate_disposition(state, context, predicates)
        reasons = tuple(pid for pid, ok in predicates.items() if not ok)
    return VerdictAdmissibilityResult(not reasons, "REVIEW_CONTEXT_QUALIFIED_AVAILABLE" if not reasons else "INADMISSIBLE", predicates, reasons)


def preflight_delivery(
    snapshot: GovernanceAuthoritySnapshot,
    evidence_contract: RequiredEvidenceContract,
    interactions: RequiredInteractionContract,
    manifest: EvidenceDeliveryManifest,
    request_id: str,
    provider: ProviderCapabilityProfile,
    items: Mapping[str, bytes],
    *,
    plan: ProviderQualificationExecutionPlan | None = None,
    qualification: ProviderCapabilityQualificationRecord | None = None,
    now: str = "2099-01-01T00:00:00Z",
    expected_provider: str = "fake",
    expected_model: str = "deterministic",
    expected_operating_point: str = "default",
    expected_profile_hash: str = "profile-hash",
    required_format: str = "text",
    required_context_bytes: int = 0,
    context_policy: ProviderContextIsolationPolicy | None = None,
    context_evidence: ProviderContextStateEvidence | None = None,
    fence: AdmissionFenceRecord | None = None,
    risk_policy: ProviderAccessibilityRiskPolicy | None = None,
    expected_transition_class: str = "LOWER",
    expected_fence_version: str = "1",
    observed_interactions: Sequence[Sequence[str]] | None = None,
) -> DeliveryPreflightResult:
    reasons: list[str] = []
    if not snapshot.outside_candidate_write_authority:
        reasons.append("authority_snapshot_candidate_writable")
    if snapshot.snapshot_id != evidence_contract.snapshot_id or snapshot.snapshot_id != interactions.snapshot_id:
        reasons.append("snapshot_binding_mismatch")
    if request_id != manifest.request_id:
        reasons.append("request_manifest_mismatch")
    if not evidence_contract.closed or not evidence_contract.non_vacuous or not evidence_contract.required_ids or not set(evidence_contract.required_ids).issubset(manifest.items):
        reasons.append("evidence_contract_unresolved")
    if not interactions.closed or not interactions.interactions or any(not set(interaction).issubset(manifest.items) for interaction in interactions.interactions):
        reasons.append("interaction_contract_unresolved")
    if observed_interactions is None or {tuple(x) for x in observed_interactions} != {tuple(x) for x in interactions.interactions}:
        reasons.append("interaction_observation_unbound")
    if plan is None or qualification is None:
        reasons.append("qualification_records_missing")
    else:
        capable, capability_reasons = validate_capability(provider, plan, qualification, now=now, expected_provider=expected_provider, expected_model=expected_model, expected_operating_point=expected_operating_point, expected_profile_hash=expected_profile_hash, required_format=required_format, required_context_bytes=required_context_bytes)
        if not capable:
            reasons.extend(capability_reasons)
    if context_policy is None or context_evidence is None or fence is None or risk_policy is None:
        reasons.append("context_isolation_records_missing")
    else:
        if risk_policy.transition_class != expected_transition_class:
            reasons.append("transition_class_policy_mismatch")
        isolated, isolation_reasons = validate_context_isolation(context_policy, context_evidence, fence, transition_class=risk_policy.transition_class, required_channels=("memory", "config"))
        if not isolated:
            reasons.extend(isolation_reasons)
        if fence.version != expected_fence_version:
            reasons.append("admission_fence_version_mismatch")
    ok, manifest_reasons = manifest.verify(items)
    if not ok:
        reasons.extend(manifest_reasons)
    return DeliveryPreflightResult(not reasons, tuple(reasons), manifest.manifest_hash if not reasons else None)


def complete_delivery(manifest: EvidenceDeliveryManifest, receipt: ReviewerReceipt, wire: WireDeliveryRecord) -> DeliveryCompletenessResult:
    reasons: list[str] = []
    expected = set(manifest.items)
    received = set(receipt.received_item_ids)
    if receipt.manifest_hash != manifest.manifest_hash:
        reasons.append("receipt_manifest_mismatch")
    if receipt.request_id != manifest.request_id or wire.request_id != manifest.request_id:
        reasons.append("request_binding_mismatch")
    if receipt.attempt_id != wire.attempt_id or receipt.session_id != wire.session_id:
        reasons.append("attempt_session_mismatch")
    if received != expected:
        reasons.append("required_item_set_incomplete")
    if not receipt.complete:
        reasons.append("reviewer_receipt_incomplete")
    if set(wire.item_ids) != expected:
        reasons.append("wire_item_set_incomplete")
    return DeliveryCompletenessResult(not reasons, tuple(reasons), tuple(sorted(received)))


def canonical_wire_hash(request_id: str, attempt_id: str, session_id: str, returned_items: Mapping[str, bytes]) -> str:
    return digest({"request_id": request_id, "attempt_id": attempt_id, "session_id": session_id, "items": {k: {"sha256": sha256(v).hexdigest(), "size": len(v)} for k, v in sorted(returned_items.items())}})


def adjudicate_insufficient_evidence(flags: Mapping[str, bool]) -> InsufficientEvidenceAdjudication:
    causes = tuple(sorted(k for k, v in flags.items() if v))
    if len(causes) > 1:
        return InsufficientEvidenceAdjudication("MIXED_INSUFFICIENCY", causes)
    return InsufficientEvidenceAdjudication(causes[0] if causes else "INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED", causes)


class DeterministicFakeProvider:
    """Fake provider exposing a transparent, append-only delivery surface."""

    def __init__(self, *, clean_context: bool = True, supports_formats: Sequence[str] = ("text", "json"), max_context_bytes: int = 1_000_000):
        self.clean_context = clean_context
        self.supports_formats = tuple(supports_formats)
        self.max_context_bytes = max_context_bytes
        self.session_id = "session-1"
        self.receipts: list[ReviewerReceipt] = []

    def deliver(self, manifest: EvidenceDeliveryManifest, items: Mapping[str, bytes], attempt_id: str = "attempt-1") -> tuple[ReviewerReceipt, WireDeliveryRecord]:
        wire_hash = canonical_wire_hash(manifest.request_id, attempt_id, self.session_id, items)
        wire = WireDeliveryRecord(attempt_id, manifest.request_id, wire_hash, wire_hash, self.session_id, tuple(sorted(items)))
        receipt = ReviewerReceipt(attempt_id, manifest.request_id, self.session_id, manifest.manifest_hash, tuple(sorted(items)), sum(map(len, items.values())), True)
        self.receipts.append(receipt)
        return receipt, wire


def validate_chunks(chunks: Sequence[EvidenceChunk], *, request_id: str, corpus_hash: str) -> tuple[bool, tuple[str, ...], bytes]:
    """Validate chunk identity/order and reconstruct only an exact corpus."""
    reasons: list[str] = []
    if not chunks:
        return False, ("chunks_missing",), b""
    totals = {c.total for c in chunks}
    if totals != {len(chunks)}:
        reasons.append("chunk_total_mismatch")
    if any(c.request_id != request_id for c in chunks):
        reasons.append("chunk_request_mismatch")
    if any(c.corpus_hash != corpus_hash for c in chunks):
        reasons.append("chunk_corpus_mismatch")
    indices = [c.index for c in chunks]
    if len(set(indices)) != len(indices):
        reasons.append("chunk_duplicate_index")
    if sorted(indices) != list(range(len(chunks))):
        reasons.append("chunk_index_gap_or_range")
    for c in chunks:
        if sha256(c.data).hexdigest() != c.chunk_hash:
            reasons.append(f"chunk_hash_mismatch:{c.index}")
        if not c.data:
            reasons.append(f"chunk_empty:{c.index}")
    raw = b"".join(c.data for c in sorted(chunks, key=lambda x: x.index))
    if digest(raw) != corpus_hash:
        reasons.append("corpus_hash_mismatch")
    return not reasons, tuple(reasons), raw


def validate_representation(manifest: EvidenceDeliveryManifest, items: Mapping[str, bytes], record: RepresentationRecord | None = None) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    ok, manifest_reasons = manifest.verify(items)
    if not ok:
        reasons.extend(manifest_reasons)
    if any(not isinstance(v, bytes) for v in items.values()):
        reasons.append("non_raw_representation")
    if record is not None:
        if record.transform_id not in QUALIFIED_TRANSFORMS or not record.transform_version or not record.transform_hash or record.registry_version != QUALIFIED_TRANSFORMS[record.transform_id]:
            reasons.append("representation_transform_unqualified")
        if record.source_hash != manifest.manifest_hash or record.representation_hash != digest({k: sha256(v).hexdigest() for k, v in sorted(items.items())}):
            reasons.append("representation_record_mismatch")
        if not record.parameters_hash or not record.coverage_hash:
            reasons.append("representation_coverage_unbound")
    return not reasons, tuple(reasons)


def validate_attempt_ledger(planned_ids: Sequence[str], dispatched_ids: Sequence[str], failed_ids: Sequence[str], retried_ids: Sequence[str] = ()) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if list(planned_ids) != list(dict.fromkeys(planned_ids)):
        reasons.append("duplicate_planned_id")
    if set(dispatched_ids) != set(planned_ids):
        reasons.append("attempt_set_not_closed")
    if any(x in retried_ids and x in failed_ids for x in retried_ids):
        reasons.append("failed_attempt_substituted")
    if len(dispatched_ids) != len(set(dispatched_ids)):
        reasons.append("duplicate_dispatch")
    return not reasons, tuple(reasons)


def validate_retry_transparency(physical_requests: Sequence[Mapping[str, Any] | PhysicalAttemptRecord], *, planned_root_ids: Sequence[str] = (), expected_request: str | None = None, expected_session: str | None = None, automatic_retry_hidden: bool = False) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if automatic_retry_hidden:
        reasons.append("implicit_retry_unobserved")
    if not physical_requests:
        reasons.append("physical_request_missing")
    if any((req.attempt_id if isinstance(req, PhysicalAttemptRecord) else req.get("attempt_id")) is None or (req.wire_hash if isinstance(req, PhysicalAttemptRecord) else req.get("wire_hash")) is None for req in physical_requests):
        reasons.append("wire_attempt_unbound")
    records = [r if isinstance(r, PhysicalAttemptRecord) else PhysicalAttemptRecord(str(r.get("attempt_id", "")), str(r.get("planned_root_id", r.get("attempt_id", ""))), r.get("parent_attempt_id"), str(r.get("kind", "FIRST")), str(r.get("request_id", "")), str(r.get("session_id", "")), str(r.get("wire_hash", "")), str(r.get("outcome", ""))) for r in physical_requests]
    if planned_root_ids:
        firsts = [r for r in records if r.kind == "FIRST"]
        if {r.planned_root_id for r in firsts} != set(planned_root_ids) or len(firsts) != len(set(r.planned_root_id for r in firsts)):
            reasons.append("planned_first_attempt_closure")
        by_id = {r.attempt_id: r for r in records}
        for retry in (r for r in records if r.kind == "RETRY"):
            if retry.attempt_id in planned_root_ids or retry.parent_attempt_id not in by_id or by_id[retry.parent_attempt_id].outcome != "FAILED":
                reasons.append("retry_lineage_invalid")
    if expected_request is not None and any(r.request_id != expected_request for r in records):
        reasons.append("request_identity_mismatch")
    if expected_session is not None and any(r.session_id != expected_session for r in records):
        reasons.append("session_identity_mismatch")
    return not reasons, tuple(reasons)


def validate_witness(challenge: str, response: str, *, max_response_bytes: int, semantic_prompt: bool = False) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if semantic_prompt:
        reasons.append("witness_asks_for_semantic_judgment")
    if not challenge or not response:
        reasons.append("witness_missing")
    if len(response.encode()) > max_response_bytes:
        reasons.append("witness_budget_exceeded")
    return not reasons, tuple(reasons)


def validate_context_state(state: ProviderContextStateEvidence, *, required_channels: Sequence[str]) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not state.clean or not state.sentinel_passed:
        reasons.append("provider_context_not_clean")
    if not set(required_channels).issubset(state.observable_channels):
        reasons.append("context_channel_unobserved")
    if not state.state_hash:
        reasons.append("context_state_unbound")
    return not reasons, tuple(reasons)


def validate_fence(fence: AdmissionFenceRecord, expected_version: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not fence.current:
        reasons.append("admission_fence_not_current")
    if fence.version != expected_version:
        reasons.append("admission_fence_version_mismatch")
    return not reasons, tuple(reasons)


def validate_egress(egress: Mapping[str, Any], expected_version: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if egress.get("authorized") is not True or egress.get("version") != expected_version:
        reasons.append("egress_revoked_or_drifted")
    return not reasons, tuple(reasons)


def validate_prompt_isolation(record: PromptIsolationQualificationRecord, *, provider_id: str, mode: str, now: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not record.current or record.provider_id != provider_id or record.mode != mode:
        reasons.append("prompt_isolation_binding")
    if record.expires_at is not None and record.expires_at <= now:
        reasons.append("prompt_isolation_expired")
    return not reasons, tuple(reasons)


def validate_registry_version(expected_version: str, observed_version: str) -> tuple[bool, tuple[str, ...]]:
    return (True, ()) if expected_version == observed_version else (False, ("predicate_registry_drift",))


def safe_archive_member(name: str) -> bool:
    """Reject traversal, absolute paths, drive paths and ambiguous separators."""
    from pathlib import PurePosixPath
    if not name or "\\" in name or name.startswith("/") or ":" in name:
        return False
    parts = PurePosixPath(name).parts
    return ".." not in parts and all(part not in ("", ".") for part in parts)


QUALIFIED_TRANSFORMS = {"raw-v1": "registry-exp-m-r1"}


def materialize_entries(entries: Mapping[str, bytes] | Sequence[MaterializationEntry], *, source_hash: str, transform_id: str = "raw-v1", max_total_bytes: int = 4_000_000, max_entries: int = 10_000, max_member_bytes: int = 1_000_000, max_recursion_depth: int = 4, max_ratio: int = 100) -> MaterializationResult:
    reasons: list[str] = []
    total = 0
    clean: dict[str, bytes] = {}
    typed = entries if not isinstance(entries, Mapping) else tuple(MaterializationEntry(name, name, "file", value, None, len(value), len(value), 0, name) for name, value in entries.items())
    if transform_id not in QUALIFIED_TRANSFORMS:
        reasons.append("unqualified_transform")
    if len(typed) > max_entries:
        reasons.append("materialization_entry_limit")
    seen: set[str] = set()
    for entry in typed:
        name, value = entry.normalized_path, entry.data
        if not safe_archive_member(entry.raw_name) or not safe_archive_member(name):
            reasons.append(f"unsafe_member:{entry.raw_name}")
            continue
        if name in seen:
            reasons.append(f"duplicate_normalized_member:{name}")
            continue
        seen.add(name)
        if entry.kind not in ("file", "symlink", "archive"):
            reasons.append(f"unsupported_member_kind:{name}")
        if entry.kind == "symlink" and (not entry.link_target or not safe_archive_member(entry.link_target)):
            reasons.append(f"symlink_escape:{name}")
        if entry.recursion_depth > max_recursion_depth:
            reasons.append(f"archive_recursion:{name}")
        if entry.compressed_size and entry.uncompressed_size and entry.uncompressed_size > entry.compressed_size * max_ratio:
            reasons.append(f"decompression_ratio:{name}")
        if not isinstance(value, bytes):
            reasons.append(f"non_bytes:{name}")
            continue
        if len(value) > max_member_bytes:
            reasons.append(f"member_size_limit:{name}")
        total += len(value)
        clean[name] = value
    if total > max_total_bytes:
        reasons.append("materialization_size_limit")
    representation_hash = digest({k: sha256(v).hexdigest() for k, v in sorted(clean.items())})
    return MaterializationResult(not reasons, clean, representation_hash, source_hash, transform_id, tuple(reasons))


def validate_capability(profile: ProviderCapabilityProfile, plan: ProviderQualificationExecutionPlan, record: ProviderCapabilityQualificationRecord, *, now: str, expected_provider: str, expected_model: str, expected_operating_point: str, expected_profile_hash: str, required_format: str, required_context_bytes: int) -> tuple[bool, tuple[str, ...]]:
    """Compute capability currentness from bound records; no qualified flag is authoritative."""
    reasons: list[str] = []
    if not plan.plan_id or not record.plan_id or plan.plan_id != record.plan_id:
        reasons.append("qualification_plan_identity_mismatch")
    if not plan.trial_ids or not plan.confirmation_ids:
        reasons.append("qualification_sets_empty")
    if profile.provider_id != expected_provider or profile.model_id != expected_model:
        reasons.append("provider_model_mismatch")
    if profile.profile_hash != expected_profile_hash or record.profile_hash != expected_profile_hash:
        reasons.append("profile_hash_mismatch")
    if plan.provider_id != expected_provider or record.provider_id != expected_provider or record.model_id != expected_model:
        reasons.append("qualification_identity_mismatch")
    if plan.operating_point != expected_operating_point or record.operating_point != expected_operating_point:
        reasons.append("operating_point_mismatch")
    if required_format not in profile.supported_formats:
        reasons.append("unsupported_format")
    if profile.max_context_bytes < required_context_bytes:
        reasons.append("context_limit_exceeded")
    if not record.statistical_qualified or record.hard_failures != 0:
        reasons.append("qualification_not_statistically_valid")
    if not record.planned_attempt_ids or not record.closed_attempt_ids or set(record.planned_attempt_ids) != set(plan.confirmation_ids) or set(record.closed_attempt_ids) != set(plan.confirmation_ids):
        reasons.append("qualification_attempt_closure")
    if record.attempt_records:
        attempts = list(record.attempt_records)
        roots = [a for a in attempts if getattr(a, "kind", "FIRST") == "FIRST"]
        if {getattr(a, "planned_root_id", "") for a in roots} != set(plan.confirmation_ids) or len(roots) != len(set(getattr(a, "planned_root_id", "") for a in roots)):
            reasons.append("qualification_attempt_records_incomplete")
        if any(getattr(a, "kind", "") == "RETRY" and (getattr(a, "parent_attempt_id", None) is None or not any(getattr(p, "attempt_id", None) == getattr(a, "parent_attempt_id", None) and getattr(p, "outcome", "") == "FAILED" for p in attempts)) for a in attempts):
            reasons.append("qualification_retry_lineage_invalid")
    if profile.expires_at is not None and profile.expires_at <= now:
        reasons.append("profile_expired")
    return not reasons, tuple(reasons)


def validate_context_isolation(policy: ProviderContextIsolationPolicy, evidence: ProviderContextStateEvidence, fence: AdmissionFenceRecord, *, transition_class: str, required_channels: Sequence[str]) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not policy.policy_id or policy.basis not in ("COMPLETE_READABLE_FENCED_STATE", "DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY"):
        reasons.append("context_policy_invalid")
    if transition_class == "HIGHEST" and policy.hidden_state_allowed:
        reasons.append("hidden_state_residual_disallowed")
    clean, clean_reasons = validate_context_state(evidence, required_channels=required_channels)
    if not clean:
        reasons.extend(clean_reasons)
    if not fence.current:
        reasons.append("admission_fence_stale")
    return not reasons, tuple(reasons)


def validate_retrieval(record: RetrievalEvidenceRecord, raw: bytes, *, expected_request: str, expected_attempt: str, expected_session: str, expected_source: str, expected_version: str, expected_context_id: str, expected_context_hash: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if record.request_id != expected_request or record.attempt_id != expected_attempt or record.session_id != expected_session:
        reasons.append("retrieval_identity_mismatch")
    if record.source_id != expected_source or record.source_version != expected_version:
        reasons.append("retrieval_source_mismatch")
    if record.end - record.start != len(raw) or record.returned_length != len(raw) or record.returned_sha256 != sha256(raw).hexdigest():
        reasons.append("retrieval_bytes_mismatch")
    if not record.tool_result_id:
        reasons.append("retrieval_tool_result_missing")
    if record.final_context_id != expected_context_id or record.final_context_hash != expected_context_hash:
        reasons.append("retrieval_final_context_unbound")
    return not reasons, tuple(reasons)


def validate_witness_qualification(record: WitnessProtocolQualificationRecord, *, provider_id: str, mode: str, prompt_mode: str, now: str, response: str, challenge: str, final_context_bytes: int, max_final_context_bytes: int) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not record.current or record.provider_id != provider_id or record.mode != mode or record.prompt_isolation_mode != prompt_mode:
        reasons.append("witness_record_binding")
    if record.expires_at is not None and record.expires_at <= now:
        reasons.append("witness_record_expired")
    if not challenge or not response or len(response.encode()) > record.max_response_bytes:
        reasons.append("witness_response_invalid")
    if final_context_bytes + len(response.encode()) > max_final_context_bytes:
        reasons.append("witness_context_eviction")
    if any(word in challenge.lower() for word in ("summarize", "judge", "evaluate", "defect")):
        reasons.append("witness_semantic_prompt")
    return not reasons, tuple(reasons)


def validate_wire_delivery(manifest: EvidenceDeliveryManifest, materialized: MaterializationResult, wire: WireDeliveryRecord, receipt: ReviewerReceipt, returned_items: Mapping[str, bytes], *, expected_commit: str, expected_semantic_hash: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    completion = complete_delivery(manifest, receipt, wire)
    if not completion.complete:
        reasons.extend(completion.reasons)
    raw_ok, raw_reasons = manifest.verify(returned_items)
    if not raw_ok:
        reasons.extend(raw_reasons)
    if manifest.reviewed_commit != expected_commit:
        reasons.append("reviewed_commit_mismatch")
    if materialized.source_hash != expected_commit:
        reasons.append("materialization_source_mismatch")
    if wire.semantic_hash != expected_semantic_hash:
        reasons.append("semantic_wire_hash_mismatch")
    if materialized.representation_hash != digest({k: sha256(v).hexdigest() for k, v in sorted(returned_items.items())}):
        reasons.append("representation_hash_mismatch")
    if receipt.received_bytes != sum(len(v) for v in returned_items.values()):
        reasons.append("receipt_byte_count_mismatch")
    expected_wire_hash = canonical_wire_hash(manifest.request_id, wire.attempt_id, wire.session_id, returned_items)
    if wire.wire_hash != expected_wire_hash:
        reasons.append("wire_hash_mismatch")
    if wire.semantic_hash != expected_wire_hash:
        reasons.append("semantic_envelope_hash_mismatch")
    return not reasons, tuple(reasons)


def admit_review_attempt(current: Mapping[str, Any], expected: AttemptState, *, attempt_id: str, expected_generation: int, ledger: PersistentAdmissionLedger | None = None) -> AdmissionCheckpoint:
    """Final compare-and-set admission; any drift permanently voids the attempt."""
    reasons: list[str] = []
    if attempt_id != expected.attempt_id or expected.invalidated:
        reasons.append("attempt_invalidated")
    if current.get("generation") != expected_generation or current.get("generation") != expected.generation:
        reasons.append("generation_drift")
    for field_name in ("authority_version", "request_version", "capability_hash", "egress_version", "context_hash", "fence_version", "prompt_hash", "witness_hash", "session_hash", "registry_version"):
        if current.get(field_name) != getattr(expected, field_name):
            reasons.append(f"state_drift:{field_name}")
    if reasons:
        checkpoint = ledger.compare_and_set(attempt_id, expected.generation, "VOID") if ledger else AdmissionCheckpoint(attempt_id, expected.generation, "VOID", False, True, tuple(reasons))
        return AdmissionCheckpoint(checkpoint.attempt_id, checkpoint.generation, checkpoint.disposition, False, True, tuple(reasons) + tuple(checkpoint.reasons))
    if ledger:
        checkpoint = ledger.compare_and_set(attempt_id, expected.generation, "COMMITTED")
        return checkpoint
    return AdmissionCheckpoint(attempt_id, expected.generation, "ADMITTED", True, False, ())


def admit_review_attempt_with_evidence(bundle: EvidenceBundle, context: PredicateContext, current: Mapping[str, Any], expected: AttemptState, *, attempt_id: str, expected_generation: int, registry: AdmissibilityPredicateRegistry | None = None, ledger: PersistentAdmissionLedger | None = None) -> AdmissionCheckpoint:
    """Final admission path: revalidate evidence immediately before persistent CAS."""
    verdict = evaluate_admissibility(bundle, context, registry)
    if not verdict.admissible:
        if ledger:
            ledger.compare_and_set(attempt_id, expected.generation, "VOID")
        return AdmissionCheckpoint(attempt_id, expected.generation, "VOID", False, True, verdict.reasons)
    return admit_review_attempt(current, expected, attempt_id=attempt_id, expected_generation=expected_generation, ledger=ledger)
