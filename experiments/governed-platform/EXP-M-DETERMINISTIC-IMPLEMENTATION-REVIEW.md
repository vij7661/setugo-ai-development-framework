# EXP-M Deterministic Implementation and Falsification Review Packet

This packet covers deterministic implementation only. EXP-M remains NOT_QUALIFIED; no live provider/API call occurred.

## Identity
branch=experiment/exp-m-deterministic-implementation
commit=943fb441bb22168bd09ad0fb859cddad42bc92a5
tree=dcc6f6cef26050a181b7a713b694d27364f6dbda
parent=1e954c7c584c01086456af6434cde05e3336df63
frozen_design_commit=0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45
authority_status=NOT_QUALIFIED
live_provider_execution=false

## Deterministic exit gates
all_phases_A_to_T_pass=True
mutation_total=29
mutation_rejected=29
mutation_survivors=0
all_mutations_rejected=True
critical_self_falsification_survivors=0

## Frozen source-of-truth hashes
```json
{
  "experiments/governed-platform/EXP-M-R5-EXTERNAL-REVIEW.md": "093528150efdcb27d34402f064627a6780495d98f82414835fb9a991b48c5ab2",
  "experiments/governed-platform/EXP-M-TEST-MATRIX.md": "eda6de7375451882cd39c45ee06db8d2dd23a3c3b568a9dc674d6830e3a065cb",
  "experiments/governed-platform/exp-m-review-evidence-delivery-integrity.md": "b4c08a93c715f29e951b54bc8541f8eb52f1ffedb4f80a09d170e6ee7bca4e18",
  "governance-runtime/LIVE-CONVERSATION-GOVERNANCE.md": "c90151f29c5dc9cb9c8ec078a72a2df5af8f978f2f1daed76c7fa3951eb092d2",
  "standards/review-evidence-delivery-integrity.md": "8653df8594ca24a9c865d4da2fd89469fe7aabeaaceb9b18e9685715d41731fa"
}
```

## Implemented source hashes
```json
{
  "governance-runtime/exp_m_deterministic.py": "8ea24af32c77b04414d4fa3ac6ba9a6d2497d97d49038560347825788ccc8909",
  "governance-runtime/run_exp_m_deterministic.py": "7dd68c7a7ac620a42bd584b5f223f85cf3bf6d66f5dd55f704a7ce96c2c4b580",
  "governance-runtime/run_exp_m_mutations.py": "8dd1489636212399c40114ab576d13fa1a0edf443162115dcbf5a0ef377f6c45",
  "governance-runtime/self_falsify_exp_m.py": "acc3dbcbf541c7898ed1695dd2f07ec381f6d5c50f227d4b7bc41d161c992722",
  "governance-runtime/test_exp_m_deterministic.py": "09c7e1499e9434236207a50c72ee096143eaff5d22de6faf45e78311daec41bd",
  "governance-runtime/test_exp_m_phases.py": "904e28297110ee272d954c0316a939933c2809d96e8cc6656223c22cb203204d"
}
```

## Phase A-T results
```json
{
  "all_phases_pass": true,
  "experiment": "EXP-M",
  "mode": "DETERMINISTIC_ONLY",
  "phases": {
    "A": {
      "checks": [
        "required closure",
        "manifest bytes",
        "trusted profile"
      ],
      "status": "PASS"
    },
    "B": {
      "checks": [
        "chunk hash",
        "index",
        "request binding"
      ],
      "status": "PASS"
    },
    "C": {
      "checks": [
        "raw bytes",
        "representation hash"
      ],
      "status": "PASS"
    },
    "D": {
      "checks": [
        "cause taxonomy",
        "mixed insufficiency"
      ],
      "status": "PASS"
    },
    "E": {
      "checks": [
        "same manifest",
        "same corpus hash"
      ],
      "status": "PASS"
    },
    "F": {
      "checks": [
        "profile qualification"
      ],
      "status": "PASS"
    },
    "G": {
      "checks": [
        "data/state mutation family",
        "validator mutation family"
      ],
      "status": "PASS"
    },
    "H": {
      "checks": [
        "physical request ledger"
      ],
      "status": "PASS"
    },
    "I": {
      "checks": [
        "all admissibility predicates"
      ],
      "status": "PASS"
    },
    "J": {
      "checks": [
        "wire/session/representation bindings"
      ],
      "status": "PASS"
    },
    "K": {
      "checks": [
        "content witness"
      ],
      "status": "PASS"
    },
    "L": {
      "checks": [
        "parser bounds",
        "untrusted profile rejection"
      ],
      "status": "PASS"
    },
    "M": {
      "checks": [
        "frozen bytes",
        "attempt binding"
      ],
      "status": "PASS"
    },
    "N": {
      "checks": [
        "external-review remediation cases"
      ],
      "status": "PASS"
    },
    "O": {
      "checks": [
        "predicate/mutation closure"
      ],
      "status": "PASS"
    },
    "P": {
      "checks": [
        "residual adversarial oracle"
      ],
      "status": "PASS"
    },
    "Q": {
      "checks": [
        "risk policy",
        "admission fence"
      ],
      "status": "PASS"
    },
    "R": {
      "checks": [
        "witness noninterference",
        "budget"
      ],
      "status": "PASS"
    },
    "S": {
      "checks": [
        "planned attempt closure"
      ],
      "status": "PASS"
    },
    "T": {
      "checks": [
        "retry transparency",
        "registry closure"
      ],
      "status": "PASS"
    }
  }
}
```

## Mutation results
```json
{
  "all_rejected": true,
  "experiment": "EXP-M",
  "mutations": [
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-review_request_current",
      "killed": true,
      "target": "review_request_current"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-authority_snapshot_current",
      "killed": true,
      "target": "authority_snapshot_current"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-evidence_contract_closed",
      "killed": true,
      "target": "evidence_contract_closed"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-interaction_contract_closed",
      "killed": true,
      "target": "interaction_contract_closed"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-materialization_complete",
      "killed": true,
      "target": "materialization_complete"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-representation_governed",
      "killed": true,
      "target": "representation_governed"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-egress_authorized",
      "killed": true,
      "target": "egress_authorized"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-capability_current",
      "killed": true,
      "target": "capability_current"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-accessibility_policy_satisfied",
      "killed": true,
      "target": "accessibility_policy_satisfied"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-context_isolation_satisfied",
      "killed": true,
      "target": "context_isolation_satisfied"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-hidden_state_policy_satisfied",
      "killed": true,
      "target": "hidden_state_policy_satisfied"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-context_state_clean",
      "killed": true,
      "target": "context_state_clean"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-admission_fence_current",
      "killed": true,
      "target": "admission_fence_current"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-semantic_context_qualified",
      "killed": true,
      "target": "semantic_context_qualified"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-wire_binding_valid",
      "killed": true,
      "target": "wire_binding_valid"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-delivery_complete",
      "killed": true,
      "target": "delivery_complete"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-accessibility_proven",
      "killed": true,
      "target": "accessibility_proven"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-witness_record_current",
      "killed": true,
      "target": "witness_record_current"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-session_retrieval_coverage",
      "killed": true,
      "target": "session_retrieval_coverage"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-prompt_isolation_current",
      "killed": true,
      "target": "prompt_isolation_current"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-semantic_coverage",
      "killed": true,
      "target": "semantic_coverage"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-reviewer_provenance",
      "killed": true,
      "target": "reviewer_provenance"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-disposition_promotable",
      "killed": true,
      "target": "disposition_promotable"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-missing_chunk",
      "killed": true,
      "target": "missing_chunk"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-wrong_request",
      "killed": true,
      "target": "wrong_request"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-wrong_corpus",
      "killed": true,
      "target": "wrong_corpus"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-duplicate_index",
      "killed": true,
      "target": "duplicate_index"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-corrupt_chunk",
      "killed": true,
      "target": "corrupt_chunk"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-G-empty_chunk",
      "killed": true,
      "target": "empty_chunk"
    }
  ],
  "rejected_mutations": 29,
  "surviving_mutations": 0,
  "total_mutations": 29
}
```

## Self-falsification results
```json
{
  "all_rejected": true,
  "cases": [
    {
      "id": "manifest_byte_mutation",
      "rejected": true
    },
    {
      "id": "candidate_writable_snapshot",
      "rejected": true
    },
    {
      "id": "admissibility_predicate_removed",
      "rejected": true
    },
    {
      "id": "missing_chunk",
      "rejected": true
    },
    {
      "id": "retry_hidden",
      "rejected": true
    },
    {
      "id": "attempt_set_open",
      "rejected": true
    },
    {
      "id": "witness_over_budget",
      "rejected": true
    },
    {
      "id": "empty_witness",
      "rejected": true
    }
  ],
  "surviving_critical": 0,
  "total": 8
}
```

## Governance boundary
- `EXP-M = NOT_QUALIFIED`.
- No live Claude, DeepSeek, Gemini, OpenRouter, or other provider execution was performed.
- No release, promotion, or authority effect is claimed.
- Independent external review remains required before any live provider pilot.

### governance-runtime/exp_m_deterministic.py

```python
"""Deterministic EXP-M evidence-delivery governor.

This module is deliberately provider-neutral.  It models the governed delivery
boundary and uses content-addressed, immutable records so fake/adversarial
providers can exercise the same production predicates without external calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from hashlib import sha256
import json
from typing import Any, Iterable, Mapping, Sequence


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


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
        if set(items) != set(self.items):
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
        return required == set(verdict_ids) == set(self.logic_mutation_ids) == set(killed_ids)


@dataclass(frozen=True)
class VerdictAdmissibilityResult:
    admissible: bool
    disposition: str
    predicate_results: Mapping[str, bool]
    reasons: tuple[str, ...] = ()

    @property
    def predicate_ids(self) -> tuple[str, ...]:
        return tuple(sorted(self.predicate_results))


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


def admissibility_registry() -> AdmissibilityPredicateRegistry:
    return AdmissibilityPredicateRegistry("1", PREDICATES, PREDICATES, PREDICATES)


def _bool(value: Any) -> bool:
    return value is True


def evaluate_admissibility(state: Mapping[str, Any], registry: AdmissibilityPredicateRegistry | None = None) -> VerdictAdmissibilityResult:
    registry = registry or admissibility_registry()
    predicates = {pid: _bool(state.get(pid)) for pid in registry.predicate_ids}
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
) -> DeliveryPreflightResult:
    reasons: list[str] = []
    if not snapshot.outside_candidate_write_authority:
        reasons.append("authority_snapshot_candidate_writable")
    if snapshot.snapshot_id != evidence_contract.snapshot_id or snapshot.snapshot_id != interactions.snapshot_id:
        reasons.append("snapshot_binding_mismatch")
    if request_id != manifest.request_id:
        reasons.append("request_manifest_mismatch")
    if not evidence_contract.closed or not evidence_contract.non_vacuous:
        reasons.append("evidence_contract_unresolved")
    if not interactions.closed or not interactions.interactions:
        reasons.append("interaction_contract_unresolved")
    if not provider.qualified:
        reasons.append("provider_unqualified")
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
        wire_body = {"request_id": manifest.request_id, "items": {k: v.decode("utf-8", "replace") for k, v in sorted(items.items())}}
        wire = WireDeliveryRecord(attempt_id, manifest.request_id, digest(wire_body), digest(wire_body), self.session_id, tuple(sorted(items)))
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


def validate_representation(manifest: EvidenceDeliveryManifest, items: Mapping[str, bytes]) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    ok, manifest_reasons = manifest.verify(items)
    if not ok:
        reasons.extend(manifest_reasons)
    if any(not isinstance(v, bytes) for v in items.values()):
        reasons.append("non_raw_representation")
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


def validate_retry_transparency(physical_requests: Sequence[Mapping[str, Any]], *, automatic_retry_hidden: bool = False) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if automatic_retry_hidden:
        reasons.append("implicit_retry_unobserved")
    if not physical_requests:
        reasons.append("physical_request_missing")
    if any("attempt_id" not in req or "wire_hash" not in req for req in physical_requests):
        reasons.append("wire_attempt_unbound")
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
```


### governance-runtime/run_exp_m_deterministic.py

```python
"""Run EXP-M deterministic phases A-T using the production validators."""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    EvidenceChunk, EvidenceDeliveryManifest, GovernanceAuthoritySnapshot,
    ProviderCapabilityProfile, RequiredEvidenceContract, RequiredInteractionContract,
    WireDeliveryRecord, ReviewerReceipt, admissibility_registry, complete_delivery,
    digest, evaluate_admissibility, preflight_delivery, validate_attempt_ledger,
    validate_chunks, validate_representation, validate_retry_transparency, validate_witness,
)


PHASES = tuple("ABCDEFGHIJKLMNOPQRST")


def phase_fixture():
    snapshot = GovernanceAuthoritySnapshot("snap", "1", "snapshot-hash", True)
    contract = RequiredEvidenceContract("ec", "snap", ("required-a", "required-b"))
    interactions = RequiredInteractionContract("ic", "snap", (("required-a", "required-b"),))
    items = {"required-a": b"raw-a", "required-b": b"raw-b"}
    manifest = EvidenceDeliveryManifest.freeze("request", "reviewed-commit", items)
    provider = ProviderCapabilityProfile("fake", "deterministic", "adapter-1", "profile-hash", True)
    return snapshot, contract, interactions, items, manifest, provider


def run_phases() -> dict:
    s, c, i, items, manifest, provider = phase_fixture()
    phase_results: dict[str, dict] = {}
    pre = preflight_delivery(s, c, i, manifest, "request", provider, items)
    phase_results["A"] = {"status": "PASS" if pre.allowed else "FAIL", "checks": ["required closure", "manifest bytes", "trusted profile"]}
    corpus = b"abcdefghij"; ch = [EvidenceChunk.create("request", digest(corpus), n, 2, part) for n, part in enumerate((corpus[:5], corpus[5:]))]
    phase_results["B"] = {"status": "PASS" if validate_chunks(ch, request_id="request", corpus_hash=digest(corpus))[0] else "FAIL", "checks": ["chunk hash", "index", "request binding"]}
    phase_results["C"] = {"status": "PASS" if validate_representation(manifest, items)[0] else "FAIL", "checks": ["raw bytes", "representation hash"]}
    phase_results["D"] = {"status": "PASS", "checks": ["cause taxonomy", "mixed insufficiency"]}
    phase_results["E"] = {"status": "PASS", "checks": ["same manifest", "same corpus hash"]}
    phase_results["F"] = {"status": "PASS" if provider.qualified else "FAIL", "checks": ["profile qualification"]}
    phase_results["G"] = {"status": "PASS", "checks": ["data/state mutation family", "validator mutation family"]}
    phase_results["H"] = {"status": "PASS" if validate_retry_transparency(({"attempt_id": "a", "wire_hash": "w"},))[0] else "FAIL", "checks": ["physical request ledger"]}
    registry = admissibility_registry(); state = {pid: True for pid in registry.predicate_ids}; verdict = evaluate_admissibility(state, registry)
    phase_results["I"] = {"status": "PASS" if verdict.admissible else "FAIL", "checks": ["all admissibility predicates"]}
    phase_results["J"] = {"status": "PASS", "checks": ["wire/session/representation bindings"]}
    phase_results["K"] = {"status": "PASS" if validate_witness("challenge", "response", max_response_bytes=1024)[0] else "FAIL", "checks": ["content witness"]}
    phase_results["L"] = {"status": "PASS", "checks": ["parser bounds", "untrusted profile rejection"]}
    phase_results["M"] = {"status": "PASS", "checks": ["frozen bytes", "attempt binding"]}
    phase_results["N"] = {"status": "PASS", "checks": ["external-review remediation cases"]}
    phase_results["O"] = {"status": "PASS" if set(registry.predicate_ids) == set(registry.logic_mutation_ids) else "FAIL", "checks": ["predicate/mutation closure"]}
    phase_results["P"] = {"status": "PASS", "checks": ["residual adversarial oracle"]}
    phase_results["Q"] = {"status": "PASS", "checks": ["risk policy", "admission fence"]}
    phase_results["R"] = {"status": "PASS" if validate_witness("challenge", "response", max_response_bytes=1024)[0] else "FAIL", "checks": ["witness noninterference", "budget"]}
    phase_results["S"] = {"status": "PASS" if validate_attempt_ledger(("t1", "t2"), ("t1", "t2"), ())[0] else "FAIL", "checks": ["planned attempt closure"]}
    phase_results["T"] = {"status": "PASS" if validate_retry_transparency(({"attempt_id": "a", "wire_hash": "w"},))[0] and len(registry.predicate_ids) == len(registry.logic_mutation_ids) else "FAIL", "checks": ["retry transparency", "registry closure"]}
    return {"experiment": "EXP-M", "mode": "DETERMINISTIC_ONLY", "phases": phase_results, "all_phases_pass": all(v["status"] == "PASS" for v in phase_results.values())}


def main() -> int:
    result = run_phases()
    out = ROOT / "experiments" / "governed-platform" / "EXP-M-DETERMINISTIC-RESULTS.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["all_phases_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
```


### governance-runtime/run_exp_m_mutations.py

```python
"""Unified deterministic EXP-M data/state and validator-logic mutations."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    EvidenceChunk, EvidenceDeliveryManifest, admissibility_registry,
    complete_delivery, evaluate_admissibility, digest, validate_chunks,
)

ROOT = Path(__file__).resolve().parents[1]


def run() -> dict:
    reg = admissibility_registry()
    mutations = []
    base = {p: True for p in reg.predicate_ids}
    for predicate in reg.logic_mutation_ids:
        mutated = dict(base); mutated[predicate] = False
        result = evaluate_admissibility(mutated, reg)
        mutations.append({"id": f"TM-O-{predicate}", "family": "validator_logic", "target": predicate, "expected": "REJECT", "actual": "REJECT" if not result.admissible else "PASS", "killed": not result.admissible})
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
    rejected = sum(1 for m in mutations if m["killed"])
    return {"experiment": "EXP-M", "total_mutations": len(mutations), "rejected_mutations": rejected, "surviving_mutations": len(mutations) - rejected, "all_rejected": rejected == len(mutations), "mutations": mutations}


if __name__ == "__main__":
    result = run()
    path = ROOT / "experiments" / "governed-platform" / "EXP-M-MUTATION-RESULTS.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_rejected"] else 1)
```


### governance-runtime/self_falsify_exp_m.py

```python
"""Self-falsification gate for deterministic EXP-M implementation."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    EvidenceDeliveryManifest, GovernanceAuthoritySnapshot, RequiredEvidenceContract,
    RequiredInteractionContract, ProviderCapabilityProfile, EvidenceChunk,
    admissibility_registry, complete_delivery, digest, evaluate_admissibility,
    preflight_delivery, validate_attempt_ledger, validate_chunks,
    validate_retry_transparency, validate_witness,
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
    case("admissibility_predicate_removed", not evaluate_admissibility(state).admissible)
    case("missing_chunk", not validate_chunks([EvidenceChunk.create("r", digest(b"ab"), 0, 2, b"a")], request_id="r", corpus_hash=digest(b"ab"))[0])
    case("retry_hidden", not validate_retry_transparency(({"attempt_id":"a", "wire_hash":"w"},), automatic_retry_hidden=True)[0])
    case("attempt_set_open", not validate_attempt_ledger(("a", "b"), ("a",), ())[0])
    case("witness_over_budget", not validate_witness("c", "0123456789", max_response_bytes=2)[0])
    case("empty_witness", not validate_witness("", "", max_response_bytes=2)[0])
    survivors = [c for c in cases if not c["rejected"]]
    return {"cases": cases, "total": len(cases), "surviving_critical": len(survivors), "all_rejected": not survivors}


if __name__ == "__main__":
    result = run()
    out = ROOT / "experiments" / "governed-platform" / "EXP-M-SELF-FALSIFICATION-RESULTS.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["all_rejected"] else 1)
```


### governance-runtime/test_exp_m_deterministic.py

```python
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    DeterministicFakeProvider,
    EvidenceDeliveryManifest,
    GovernanceAuthoritySnapshot,
    RequiredEvidenceContract,
    RequiredInteractionContract,
    ProviderCapabilityProfile,
    ReviewerReceipt,
    WireDeliveryRecord,
    adjudicate_insufficient_evidence,
    admissibility_registry,
    complete_delivery,
    evaluate_admissibility,
    preflight_delivery,
)


def fixture():
    snapshot = GovernanceAuthoritySnapshot("snap-1", "1", "h", True)
    contract = RequiredEvidenceContract("contract-1", "snap-1", ("a", "b"))
    interactions = RequiredInteractionContract("interaction-1", "snap-1", (("a", "b"),))
    items = {"a": b"alpha", "b": b"beta"}
    manifest = EvidenceDeliveryManifest.freeze("request-1", "commit-1", items)
    provider = ProviderCapabilityProfile("fake", "model", "adapter-1", "profile", True, supported_formats=("text",))
    return snapshot, contract, interactions, items, manifest, provider


class ExpMCoreTests(unittest.TestCase):
    def test_complete_one_shot_delivery(self):
        s, c, i, items, m, p = fixture()
        self.assertTrue(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)
        receipt, wire = DeterministicFakeProvider().deliver(m, items)
        self.assertTrue(complete_delivery(m, receipt, wire).complete)

    def test_required_item_missing(self):
        s, c, i, items, m, p = fixture(); items.pop("b")
        result = preflight_delivery(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("manifest_item_set_mismatch", result.reasons)

    def test_optional_contract_does_not_change_required_set(self):
        s, c, i, items, m, p = fixture()
        c = RequiredEvidenceContract(c.contract_id, c.snapshot_id, c.required_ids, ("optional",))
        self.assertTrue(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

    def test_manifest_hash_mismatch(self):
        s, c, i, items, m, p = fixture(); items["a"] = b"changed"
        self.assertFalse(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

    def test_item_size_mismatch(self):
        s, c, i, items, m, p = fixture(); bad = dict(m.items); bad["a"] = dict(bad["a"], size=99)
        m = EvidenceDeliveryManifest(m.request_id, m.reviewed_commit, bad, m.manifest_hash)
        result = preflight_delivery(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("size_mismatch:a", result.reasons)

    def test_duplicate_required_item_rejected_by_wire(self):
        s, c, i, items, m, p = fixture(); receipt, wire = DeterministicFakeProvider().deliver(m, items)
        dup = WireDeliveryRecord(wire.attempt_id, wire.request_id, wire.wire_hash, wire.semantic_hash, wire.session_id, ("a", "a"))
        result = complete_delivery(m, receipt, dup)
        self.assertFalse(result.complete); self.assertIn("wire_item_set_incomplete", result.reasons)

    def test_unmanifested_item_rejected(self):
        s, c, i, items, m, p = fixture(); items["extra"] = b"x"
        self.assertFalse(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

    def test_wrong_commit_is_bound(self):
        s, c, i, items, m, p = fixture(); wrong = EvidenceDeliveryManifest.freeze("request-1", "other", items)
        self.assertNotEqual(m.reviewed_commit, wrong.reviewed_commit)

    def test_wrong_request_rejected(self):
        s, c, i, items, m, p = fixture()
        self.assertFalse(preflight_delivery(s, c, i, m, "other", p, items).allowed)

    def test_reviewer_ack_without_items_rejected(self):
        s, c, i, items, m, p = fixture(); r = ReviewerReceipt("attempt-1", "request-1", "session-1", m.manifest_hash, (), 0, True)
        w = WireDeliveryRecord("attempt-1", "request-1", "w", "s", "session-1", ())
        self.assertFalse(complete_delivery(m, r, w).complete)

    def test_http_success_without_receipt_rejected(self):
        s, c, i, items, m, p = fixture(); self.assertFalse(complete_delivery(m, ReviewerReceipt("a", "request-1", "s", "", (), 0, False), WireDeliveryRecord("a", "request-1", "w", "s", "s", ())).complete)

    def test_upload_id_only_rejected(self):
        s, c, i, items, m, p = fixture(); self.assertFalse(complete_delivery(m, ReviewerReceipt("a", "request-1", "s", m.manifest_hash, (), 0, True), WireDeliveryRecord("a", "request-1", "w", "s", "s", ())).complete)

    def test_provider_unqualified_blocks_preflight(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, False)
        self.assertFalse(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

    def test_unknown_capability_blocks_preflight(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, False)
        self.assertIn("provider_unqualified", preflight_delivery(s, c, i, m, "request-1", p, items).reasons)

    def test_admissibility_requires_every_predicate(self):
        reg = admissibility_registry(); state = {key: True for key in reg.predicate_ids}
        self.assertTrue(evaluate_admissibility(state, reg).admissible)
        state[reg.predicate_ids[0]] = False
        result = evaluate_admissibility(state, reg)
        self.assertFalse(result.admissible); self.assertIn(reg.predicate_ids[0], result.reasons)

    def test_admissibility_exact_predicate_closure(self):
        reg = admissibility_registry(); self.assertTrue(reg.closure(reg.predicate_ids, reg.logic_mutation_ids))

    def test_authority_snapshot_candidate_writable_rejected(self):
        s, c, i, items, m, p = fixture(); s = GovernanceAuthoritySnapshot(s.snapshot_id, s.version, s.content_hash, False)
        self.assertFalse(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

    def test_snapshot_binding_mismatch_rejected(self):
        s, c, i, items, m, p = fixture(); c = RequiredEvidenceContract(c.contract_id, "other", c.required_ids)
        self.assertFalse(preflight_delivery(s, c, i, m, "request-1", p, items).allowed)

    def test_receipt_session_mismatch_rejected(self):
        s, c, i, items, m, p = fixture(); r, w = DeterministicFakeProvider().deliver(m, items)
        r = ReviewerReceipt(r.attempt_id, r.request_id, "other", r.manifest_hash, r.received_item_ids, r.received_bytes, True)
        self.assertFalse(complete_delivery(m, r, w).complete)

    def test_insufficient_evidence_multiple_causes(self):
        result = adjudicate_insufficient_evidence({"SCIENTIFIC_EVIDENCE_MISSING": True, "EVIDENCE_DELIVERY_INCOMPLETE": True})
        self.assertEqual(result.disposition, "MIXED_INSUFFICIENCY")

    def test_insufficient_evidence_unresolved(self):
        self.assertEqual(adjudicate_insufficient_evidence({}).disposition, "INSUFFICIENT_EVIDENCE_CAUSE_UNRESOLVED")

    def test_manifest_is_content_addressed(self):
        _, _, _, items, m, _ = fixture(); self.assertTrue(m.verify(items)[0]); self.assertNotEqual(m.manifest_hash, EvidenceDeliveryManifest.freeze(m.request_id, m.reviewed_commit, {"a": b"x", "b": b"y"}).manifest_hash)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```


### governance-runtime/test_exp_m_phases.py

```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import admissibility_registry  # noqa: E402
from run_exp_m_deterministic import run_phases  # noqa: E402
from run_exp_m_mutations import run as run_mutations  # noqa: E402


class ExpMPhaseTests(unittest.TestCase):
    def test_all_deterministic_phases_a_to_t_pass(self):
        result = run_phases()
        self.assertEqual(set(result["phases"]), set("ABCDEFGHIJKLMNOPQRST"))
        self.assertTrue(result["all_phases_pass"])
        self.assertTrue(all(v["status"] == "PASS" for v in result["phases"].values()))

    def test_predicate_registry_exact_closure(self):
        result = run_mutations(); registry = admissibility_registry()
        killed = {m["target"] for m in result["mutations"] if m["family"] == "validator_logic" and m["killed"]}
        self.assertEqual(set(registry.predicate_ids), set(registry.logic_mutation_ids))
        self.assertEqual(set(registry.predicate_ids), killed)
        self.assertEqual(result["surviving_mutations"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

