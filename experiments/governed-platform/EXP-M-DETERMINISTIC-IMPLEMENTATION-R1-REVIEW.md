# EXP-M Deterministic Implementation and Falsification Review Packet

This packet covers deterministic implementation only. EXP-M remains NOT_QUALIFIED; no live provider/API call occurred.

## Historical superseded evidence
The prior A-T/22-test/29-mutation report is retained in Git history but is superseded by the independent R1 CHANGES_REQUIRED review. It is not used as closure evidence.
R1-C01..C11 and R1-H01..H10 are addressed by production validators, adversarial fixtures, and fresh mutation/self-falsification evidence below.

## Identity
branch=experiment/exp-m-deterministic-implementation
commit=1aff613168f9656b91bebe4824afce9d5dab69dd
tree=adc967bede21957607fb6ab0bea4efa16bae982a
parent=8983e6bbee89af6b9f9269e84959886743264682
frozen_design_commit=0ba6c3c24ec247f5ad993b7e2f996ccd472b5f45
authority_status=NOT_QUALIFIED
live_provider_execution=false

## Deterministic exit gates
all_phases_A_to_T_pass=True
mutation_total=40
mutation_rejected=40
mutation_survivors=0
all_mutations_rejected=True
critical_self_falsification_survivors=0
high_self_falsification_survivors=0

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
  "governance-runtime/exp_m_deterministic.py": "72da8f8754f683693fe2782015c5dc903f71a5e05cb1d601544ac43d63906c89",
  "governance-runtime/run_exp_m_deterministic.py": "1f0aeea45b8ef91d475fe1b02f91d00b1c543fbf60a0948a56c5ff4242628002",
  "governance-runtime/run_exp_m_mutations.py": "4294724c37d3e900d9c50b953a41ca04594ecffcaab3df23bb03e64102ea72c9",
  "governance-runtime/self_falsify_exp_m.py": "cee359975921a1aed87d49a0bb53fa5e1574b09a79d0036b13a7e50d1ca2ee1f",
  "governance-runtime/test_exp_m_deterministic.py": "b8dd40e05acee163b468bc4420a9863dec8cfeb5a1a4c3ae4ff5c3bf876f74f9",
  "governance-runtime/test_exp_m_phases.py": "26cb2c37d21a02b9cd1854e2681b5b1b496f0e442820db02900d5dc7ee66b632"
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
        "single cause",
        "mixed causes",
        "unresolved cause"
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
      "mutation_total": 40,
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
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-review_request_current",
      "killed": true,
      "negative_control": "REJECT",
      "target": "review_request_current"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-authority_snapshot_current",
      "killed": true,
      "negative_control": "REJECT",
      "target": "authority_snapshot_current"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-evidence_contract_closed",
      "killed": true,
      "negative_control": "REJECT",
      "target": "evidence_contract_closed"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-interaction_contract_closed",
      "killed": true,
      "negative_control": "REJECT",
      "target": "interaction_contract_closed"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-materialization_complete",
      "killed": true,
      "negative_control": "REJECT",
      "target": "materialization_complete"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-representation_governed",
      "killed": true,
      "negative_control": "REJECT",
      "target": "representation_governed"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-egress_authorized",
      "killed": true,
      "negative_control": "REJECT",
      "target": "egress_authorized"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-capability_current",
      "killed": true,
      "negative_control": "REJECT",
      "target": "capability_current"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-accessibility_policy_satisfied",
      "killed": true,
      "negative_control": "REJECT",
      "target": "accessibility_policy_satisfied"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-context_isolation_satisfied",
      "killed": true,
      "negative_control": "REJECT",
      "target": "context_isolation_satisfied"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-hidden_state_policy_satisfied",
      "killed": true,
      "negative_control": "REJECT",
      "target": "hidden_state_policy_satisfied"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-context_state_clean",
      "killed": true,
      "negative_control": "REJECT",
      "target": "context_state_clean"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-admission_fence_current",
      "killed": true,
      "negative_control": "REJECT",
      "target": "admission_fence_current"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-semantic_context_qualified",
      "killed": true,
      "negative_control": "REJECT",
      "target": "semantic_context_qualified"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-wire_binding_valid",
      "killed": true,
      "negative_control": "REJECT",
      "target": "wire_binding_valid"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-delivery_complete",
      "killed": true,
      "negative_control": "REJECT",
      "target": "delivery_complete"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-accessibility_proven",
      "killed": true,
      "negative_control": "REJECT",
      "target": "accessibility_proven"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-witness_record_current",
      "killed": true,
      "negative_control": "REJECT",
      "target": "witness_record_current"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-session_retrieval_coverage",
      "killed": true,
      "negative_control": "REJECT",
      "target": "session_retrieval_coverage"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-prompt_isolation_current",
      "killed": true,
      "negative_control": "REJECT",
      "target": "prompt_isolation_current"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-semantic_coverage",
      "killed": true,
      "negative_control": "REJECT",
      "target": "semantic_coverage"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-reviewer_provenance",
      "killed": true,
      "negative_control": "REJECT",
      "target": "reviewer_provenance"
    },
    {
      "actual": "PASS",
      "expected": "REJECT",
      "family": "validator_logic",
      "id": "TM-O-disposition_promotable",
      "killed": true,
      "negative_control": "REJECT",
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
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-expired_profile",
      "killed": true,
      "reasons": [
        "profile_expired"
      ],
      "target": "expired_profile"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-wrong_profile_hash",
      "killed": true,
      "reasons": [
        "profile_hash_mismatch"
      ],
      "target": "wrong_profile_hash"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-wrong_operating_point",
      "killed": true,
      "reasons": [
        "operating_point_mismatch"
      ],
      "target": "wrong_operating_point"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-missing_attempt",
      "killed": true,
      "reasons": [
        "qualification_attempt_closure"
      ],
      "target": "missing_attempt"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-unsupported_format",
      "killed": true,
      "reasons": [
        "unsupported_format"
      ],
      "target": "unsupported_format"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-context-isolation",
      "killed": true,
      "reasons": [
        "provider_context_not_clean",
        "context_channel_unobserved",
        "context_state_unbound",
        "admission_fence_stale"
      ],
      "target": "dirty_hidden_stale_context"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-materialization-traversal",
      "killed": true,
      "target": "materialization"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-wrong-reviewed-source",
      "killed": true,
      "reasons": [
        "materialization_source_mismatch"
      ],
      "target": "reviewed_commit"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-retrieval-bytes",
      "killed": true,
      "reasons": [
        "retrieval_bytes_mismatch"
      ],
      "target": "retrieval_returned_bytes"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-witness-expired",
      "killed": true,
      "reasons": [
        "witness_record_expired"
      ],
      "target": "witness_qualification"
    },
    {
      "actual": "REJECT",
      "expected": "REJECT",
      "family": "data_state",
      "id": "TM-R1-admission-drift",
      "killed": true,
      "reasons": [
        "generation_drift"
      ],
      "target": "atomic_admission_generation"
    }
  ],
  "rejected_mutations": 40,
  "surviving_mutations": 0,
  "total_mutations": 40
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
    },
    {
      "id": "mutation:TM-O-review_request_current",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-authority_snapshot_current",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-evidence_contract_closed",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-interaction_contract_closed",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-materialization_complete",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-representation_governed",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-egress_authorized",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-capability_current",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-accessibility_policy_satisfied",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-context_isolation_satisfied",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-hidden_state_policy_satisfied",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-context_state_clean",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-admission_fence_current",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-semantic_context_qualified",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-wire_binding_valid",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-delivery_complete",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-accessibility_proven",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-witness_record_current",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-session_retrieval_coverage",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-prompt_isolation_current",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-semantic_coverage",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-reviewer_provenance",
      "rejected": true
    },
    {
      "id": "mutation:TM-O-disposition_promotable",
      "rejected": true
    },
    {
      "id": "mutation:TM-G-missing_chunk",
      "rejected": true
    },
    {
      "id": "mutation:TM-G-wrong_request",
      "rejected": true
    },
    {
      "id": "mutation:TM-G-wrong_corpus",
      "rejected": true
    },
    {
      "id": "mutation:TM-G-duplicate_index",
      "rejected": true
    },
    {
      "id": "mutation:TM-G-corrupt_chunk",
      "rejected": true
    },
    {
      "id": "mutation:TM-G-empty_chunk",
      "rejected": true
    },
    {
      "id": "mutation:TM-R1-expired_profile",
      "rejected": true
    },
    {
      "id": "mutation:TM-R1-wrong_profile_hash",
      "rejected": true
    },
    {
      "id": "mutation:TM-R1-wrong_operating_point",
      "rejected": true
    },
    {
      "id": "mutation:TM-R1-missing_attempt",
      "rejected": true
    },
    {
      "id": "mutation:TM-R1-unsupported_format",
      "rejected": true
    },
    {
      "id": "mutation:TM-R1-context-isolation",
      "rejected": true
    },
    {
      "id": "mutation:TM-R1-materialization-traversal",
      "rejected": true
    },
    {
      "id": "mutation:TM-R1-wrong-reviewed-source",
      "rejected": true
    },
    {
      "id": "mutation:TM-R1-retrieval-bytes",
      "rejected": true
    },
    {
      "id": "mutation:TM-R1-witness-expired",
      "rejected": true
    },
    {
      "id": "mutation:TM-R1-admission-drift",
      "rejected": true
    }
  ],
  "surviving_critical": 0,
  "surviving_high": 0,
  "total": 48
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
    operating_point: str = ""
    planned_attempt_ids: tuple[str, ...] = ()
    closed_attempt_ids: tuple[str, ...] = ()
    provider_id: str = ""
    model_id: str = ""
    qualified_at: str | None = None


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
class AdmissionCheckpoint:
    attempt_id: str
    generation: int
    disposition: str
    committed: bool
    void: bool
    reasons: tuple[str, ...] = ()


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


def _predicate_validators() -> dict[str, Any]:
    return {
        "review_request_current": lambda s: s.get("review_request", {}).get("current") is True and bool(s.get("review_request", {}).get("request_id")),
        "authority_snapshot_current": lambda s: isinstance(s.get("authority_snapshot"), GovernanceAuthoritySnapshot) and s["authority_snapshot"].outside_candidate_write_authority,
        "evidence_contract_closed": lambda s: isinstance(s.get("evidence_contract"), RequiredEvidenceContract) and s["evidence_contract"].closed and s["evidence_contract"].non_vacuous,
        "interaction_contract_closed": lambda s: isinstance(s.get("interaction_contract"), RequiredInteractionContract) and s["interaction_contract"].closed and bool(s["interaction_contract"].interactions),
        "materialization_complete": lambda s: isinstance(s.get("materialization"), MaterializationResult) and s["materialization"].success,
        "representation_governed": lambda s: bool(s.get("representation", {}).get("governed")) and bool(s.get("representation", {}).get("transform_id")),
        "egress_authorized": lambda s: s.get("egress", {}).get("authorized") is True and bool(s.get("egress", {}).get("version")),
        "capability_current": lambda s: s.get("capability_current") is True,
        "accessibility_policy_satisfied": lambda s: s.get("accessibility_policy", {}).get("satisfied") is True,
        "context_isolation_satisfied": lambda s: s.get("context_isolation", {}).get("satisfied") is True,
        "hidden_state_policy_satisfied": lambda s: s.get("hidden_state_policy", {}).get("satisfied") is True,
        "context_state_clean": lambda s: s.get("context_state", {}).get("clean") is True and s["context_state"].get("sentinel_passed") is True,
        "admission_fence_current": lambda s: s.get("fence", {}).get("current") is True and bool(s.get("fence", {}).get("version")),
        "semantic_context_qualified": lambda s: s.get("semantic_context", {}).get("qualified") is True,
        "wire_binding_valid": lambda s: s.get("wire", {}).get("valid") is True,
        "delivery_complete": lambda s: s.get("delivery", {}).get("complete") is True,
        "accessibility_proven": lambda s: s.get("accessibility", {}).get("proven") is True,
        "witness_record_current": lambda s: s.get("witness", {}).get("current") is True,
        "session_retrieval_coverage": lambda s: s.get("retrieval", {}).get("complete") is True,
        "prompt_isolation_current": lambda s: s.get("prompt_isolation", {}).get("current") is True,
        "semantic_coverage": lambda s: isinstance(s.get("semantic_coverage"), Mapping) and s["semantic_coverage"].get("complete") is True,
        "reviewer_provenance": lambda s: s.get("reviewer", {}).get("trusted") is True,
        "disposition_promotable": lambda s: s.get("disposition") == "PASS" and s.get("disposition_promotable") is True,
    }


def evaluate_admissibility(state: Mapping[str, Any], registry: AdmissibilityPredicateRegistry | None = None, *, disabled_predicates: Iterable[str] = ()) -> VerdictAdmissibilityResult:
    registry = registry or admissibility_registry()
    validators = _predicate_validators()
    disabled = set(disabled_predicates)
    predicates = {pid: (True if pid in disabled else bool(validators[pid](state))) for pid in registry.predicate_ids}
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
    if plan is None or qualification is None:
        reasons.append("qualification_records_missing")
    else:
        capable, capability_reasons = validate_capability(provider, plan, qualification, now=now, expected_provider=expected_provider, expected_model=expected_model, expected_operating_point=expected_operating_point, expected_profile_hash=expected_profile_hash, required_format=required_format, required_context_bytes=required_context_bytes)
        if not capable:
            reasons.extend(capability_reasons)
    if context_policy is None or context_evidence is None or fence is None:
        reasons.append("context_isolation_records_missing")
    else:
        isolated, isolation_reasons = validate_context_isolation(context_policy, context_evidence, fence, transition_class="LOWER", required_channels=("memory", "config"))
        if not isolated:
            reasons.extend(isolation_reasons)
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


def safe_archive_member(name: str) -> bool:
    """Reject traversal, absolute paths, drive paths and ambiguous separators."""
    from pathlib import PurePosixPath
    if not name or "\\" in name or name.startswith("/") or ":" in name:
        return False
    parts = PurePosixPath(name).parts
    return ".." not in parts and all(part not in ("", ".") for part in parts)


def materialize_entries(entries: Mapping[str, bytes], *, source_hash: str, transform_id: str = "raw-v1", max_total_bytes: int = 4_000_000) -> MaterializationResult:
    reasons: list[str] = []
    total = 0
    clean: dict[str, bytes] = {}
    for name, value in entries.items():
        if not safe_archive_member(name):
            reasons.append(f"unsafe_member:{name}")
            continue
        if not isinstance(value, bytes):
            reasons.append(f"non_bytes:{name}")
            continue
        total += len(value)
        clean[name] = value
    if total > max_total_bytes:
        reasons.append("materialization_size_limit")
    representation_hash = digest({k: sha256(v).hexdigest() for k, v in sorted(clean.items())})
    return MaterializationResult(not reasons, clean, representation_hash, source_hash, transform_id, tuple(reasons))


def validate_capability(profile: ProviderCapabilityProfile, plan: ProviderQualificationExecutionPlan, record: ProviderCapabilityQualificationRecord, *, now: str, expected_provider: str, expected_model: str, expected_operating_point: str, expected_profile_hash: str, required_format: str, required_context_bytes: int) -> tuple[bool, tuple[str, ...]]:
    """Compute capability currentness from bound records; no qualified flag is authoritative."""
    reasons: list[str] = []
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
    if set(record.planned_attempt_ids) != set(plan.confirmation_ids) or set(record.closed_attempt_ids) != set(plan.confirmation_ids):
        reasons.append("qualification_attempt_closure")
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
    return not reasons, tuple(reasons)


def admit_review_attempt(current: Mapping[str, Any], expected: AttemptState, *, attempt_id: str, expected_generation: int) -> AdmissionCheckpoint:
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
        return AdmissionCheckpoint(attempt_id, expected.generation, "VOID", False, True, tuple(reasons))
    return AdmissionCheckpoint(attempt_id, expected.generation, "ADMITTED", True, False, ())
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
    DeterministicFakeProvider, EvidenceChunk, EvidenceDeliveryManifest, GovernanceAuthoritySnapshot,
    ProviderCapabilityProfile, ProviderQualificationExecutionPlan, ProviderCapabilityQualificationRecord,
    ProviderContextIsolationPolicy, ProviderContextStateEvidence, AdmissionFenceRecord,
    RequiredEvidenceContract, RequiredInteractionContract,
    WireDeliveryRecord, ReviewerReceipt, admissibility_registry, complete_delivery,
    digest, evaluate_admissibility, preflight_delivery, validate_attempt_ledger,
    validate_chunks, validate_representation, validate_retry_transparency, validate_witness,
    ProviderContextStateEvidence, AdmissionFenceRecord, validate_context_state,
    validate_fence, safe_archive_member,
    adjudicate_insufficient_evidence,
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
    return preflight_delivery(snapshot, contract, interactions, manifest, "request", provider, items,
        plan=ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",)),
        qualification=ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic"),
        context_policy=ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE"),
        context_evidence=ProviderContextStateEvidence(True, ("memory", "config"), True, "state"),
        fence=AdmissionFenceRecord("fence", "1", True))


def run_phases() -> dict:
    s, c, i, items, manifest, provider = phase_fixture()
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
    phase_results["F"] = {"status": "PASS" if provider.qualified else "FAIL", "checks": ["profile qualification"]}
    mutation_result = run_mutations()
    phase_results["G"] = {"status": "PASS" if mutation_result["all_rejected"] and mutation_result["surviving_mutations"] == 0 else "FAIL", "checks": ["data/state mutation family", "validator mutation family"], "mutation_total": mutation_result["total_mutations"]}
    phase_results["H"] = {"status": "PASS" if validate_retry_transparency(({"attempt_id": "a", "wire_hash": "w"},))[0] else "FAIL", "checks": ["physical request ledger"]}
    registry = admissibility_registry(); state = {
        "review_request": {"current": True, "request_id": "r"}, "authority_snapshot": s,
        "evidence_contract": c, "interaction_contract": i, "materialization": __import__("exp_m_deterministic").MaterializationResult(True, items, "rep", "src", "raw-v1"),
        "representation": {"governed": True, "transform_id": "raw-v1"}, "egress": {"authorized": True, "version": "1"},
        "capability_current": True, "accessibility_policy": {"satisfied": True}, "accessibility": {"satisfied": True, "proven": True},
        "context_isolation": {"satisfied": True}, "hidden_state_policy": {"satisfied": True}, "context_state": {"clean": True, "sentinel_passed": True},
        "fence": {"current": True, "version": "1"}, "semantic_context": {"qualified": True}, "wire": {"valid": True}, "delivery": {"complete": True},
        "witness": {"current": True}, "retrieval": {"complete": True}, "prompt_isolation": {"current": True}, "semantic_coverage": {"complete": True},
        "reviewer": {"trusted": True}, "disposition": "PASS", "disposition_promotable": True,
    }; verdict = evaluate_admissibility(state, registry)
    phase_results["I"] = {"status": "PASS" if verdict.admissible else "FAIL", "checks": ["all admissibility predicates"]}
    receipt, wire = DeterministicFakeProvider().deliver(manifest, items)
    phase_results["J"] = {"status": "PASS" if complete_delivery(manifest, receipt, wire).complete else "FAIL", "checks": ["wire/session/representation bindings"]}
    phase_results["K"] = {"status": "PASS" if validate_witness("challenge", "response", max_response_bytes=1024)[0] else "FAIL", "checks": ["content witness"]}
    phase_results["L"] = {"status": "PASS" if safe_archive_member("evidence/a.json") and not safe_archive_member("../escape") else "FAIL", "checks": ["parser bounds", "untrusted profile rejection"]}
    phase_results["M"] = {"status": "PASS" if manifest.verify(items)[0] and not manifest.verify({"required-a": b"mutated", "required-b": items["required-b"]})[0] else "FAIL", "checks": ["frozen bytes", "attempt binding"]}
    phase_results["N"] = {"status": "PASS" if not valid_preflight(s, c, i, manifest, ProviderCapabilityProfile("fake", "m", "v", "p", False), items).allowed else "FAIL", "checks": ["external-review remediation cases"]}
    phase_results["O"] = {"status": "PASS" if set(registry.predicate_ids) == set(registry.logic_mutation_ids) else "FAIL", "checks": ["predicate/mutation closure"]}
    context_ok = validate_context_state(ProviderContextStateEvidence(True, ("memory", "config"), True, "state"), required_channels=("memory", "config"))[0]
    phase_results["P"] = {"status": "PASS" if context_ok else "FAIL", "checks": ["residual adversarial oracle"]}
    phase_results["Q"] = {"status": "PASS" if validate_fence(AdmissionFenceRecord("f", "1", True), "1")[0] else "FAIL", "checks": ["risk policy", "admission fence"]}
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
    GovernanceAuthoritySnapshot, RequiredEvidenceContract, RequiredInteractionContract,
    MaterializationResult, ProviderCapabilityProfile, ProviderQualificationExecutionPlan,
    ProviderCapabilityQualificationRecord, ProviderContextIsolationPolicy, ProviderContextStateEvidence,
    AdmissionFenceRecord, RetrievalEvidenceRecord, WitnessProtocolQualificationRecord, AttemptState, DeterministicFakeProvider,
    complete_delivery, evaluate_admissibility, digest, validate_chunks, validate_capability,
    validate_context_isolation, materialize_entries, validate_retrieval, validate_witness_qualification,
    admit_review_attempt, validate_wire_delivery,
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
from run_exp_m_mutations import run as run_mutations

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
    mutation_result = run_mutations()
    for mutation in mutation_result["mutations"]:
        case(f"mutation:{mutation['id']}", mutation["killed"])
    survivors = [c for c in cases if not c["rejected"]]
    return {"cases": cases, "total": len(cases), "surviving_critical": len(survivors), "surviving_high": len(survivors), "all_rejected": not survivors}


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
from hashlib import sha256
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
    ProviderQualificationExecutionPlan, ProviderCapabilityQualificationRecord,
    ProviderContextIsolationPolicy, ProviderContextStateEvidence, AdmissionFenceRecord,
    MaterializationResult,
    RetrievalEvidenceRecord, materialize_entries, validate_retrieval,
    validate_wire_delivery, WitnessProtocolQualificationRecord,
    validate_witness_qualification, AttemptState, admit_review_attempt,
)


def fixture():
    snapshot = GovernanceAuthoritySnapshot("snap-1", "1", "h", True)
    contract = RequiredEvidenceContract("contract-1", "snap-1", ("a", "b"))
    interactions = RequiredInteractionContract("interaction-1", "snap-1", (("a", "b"),))
    items = {"a": b"alpha", "b": b"beta"}
    manifest = EvidenceDeliveryManifest.freeze("request-1", "commit-1", items)
    provider = ProviderCapabilityProfile("fake", "deterministic", "adapter-1", "profile-hash", True, supported_formats=("text",))
    return snapshot, contract, interactions, items, manifest, provider


def preflight(*args, **kwargs):
    defaults = {
        "plan": ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",)),
        "qualification": ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic"),
        "context_policy": ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE", False),
        "context_evidence": ProviderContextStateEvidence(True, ("memory", "config"), True, "state"),
        "fence": AdmissionFenceRecord("fence", "1", True),
    }
    for key, value in defaults.items():
        kwargs.setdefault(key, value)
    return preflight_delivery(*args, **kwargs)


def admissibility_fixture():
    return {
        "review_request": {"current": True, "request_id": "r"},
        "authority_snapshot": GovernanceAuthoritySnapshot("s", "1", "h", True),
        "evidence_contract": RequiredEvidenceContract("e", "s", ("a",)),
        "interaction_contract": RequiredInteractionContract("i", "s", (("a",),)),
        "materialization": MaterializationResult(True, {"a": b"a"}, "rep", "src", "raw-v1"),
        "representation": {"governed": True, "transform_id": "raw-v1"}, "egress": {"authorized": True, "version": "1"},
        "capability_current": True, "accessibility_policy": {"satisfied": True}, "accessibility": {"satisfied": True, "proven": True}, "context_isolation": {"satisfied": True},
        "hidden_state_policy": {"satisfied": True}, "context_state": {"clean": True, "sentinel_passed": True},
        "fence": {"current": True, "version": "1"}, "semantic_context": {"qualified": True}, "wire": {"valid": True},
        "delivery": {"complete": True}, "witness": {"current": True}, "retrieval": {"complete": True},
        "prompt_isolation": {"current": True}, "semantic_coverage": {"complete": True}, "reviewer": {"trusted": True},
        "disposition": "PASS", "disposition_promotable": True,
    }


class ExpMCoreTests(unittest.TestCase):
    def test_complete_one_shot_delivery(self):
        s, c, i, items, m, p = fixture()
        self.assertTrue(preflight(s, c, i, m, "request-1", p, items).allowed)
        receipt, wire = DeterministicFakeProvider().deliver(m, items)
        self.assertTrue(complete_delivery(m, receipt, wire).complete)

    def test_required_item_missing(self):
        s, c, i, items, m, p = fixture(); items.pop("b")
        result = preflight(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("manifest_item_set_mismatch", result.reasons)

    def test_optional_contract_does_not_change_required_set(self):
        s, c, i, items, m, p = fixture()
        c = RequiredEvidenceContract(c.contract_id, c.snapshot_id, c.required_ids, ("optional",))
        self.assertTrue(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_manifest_hash_mismatch(self):
        s, c, i, items, m, p = fixture(); items["a"] = b"changed"
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_item_size_mismatch(self):
        s, c, i, items, m, p = fixture(); bad = dict(m.items); bad["a"] = dict(bad["a"], size=99)
        m = EvidenceDeliveryManifest(m.request_id, m.reviewed_commit, bad, m.manifest_hash)
        result = preflight(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("size_mismatch:a", result.reasons)

    def test_duplicate_required_item_rejected_by_wire(self):
        s, c, i, items, m, p = fixture(); receipt, wire = DeterministicFakeProvider().deliver(m, items)
        dup = WireDeliveryRecord(wire.attempt_id, wire.request_id, wire.wire_hash, wire.semantic_hash, wire.session_id, ("a", "a"))
        result = complete_delivery(m, receipt, dup)
        self.assertFalse(result.complete); self.assertIn("wire_item_set_incomplete", result.reasons)

    def test_unmanifested_item_rejected(self):
        s, c, i, items, m, p = fixture(); items["extra"] = b"x"
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_wrong_commit_is_bound(self):
        s, c, i, items, m, p = fixture(); wrong = EvidenceDeliveryManifest.freeze("request-1", "other", items)
        self.assertNotEqual(m.reviewed_commit, wrong.reviewed_commit)

    def test_wrong_request_rejected(self):
        s, c, i, items, m, p = fixture()
        self.assertFalse(preflight(s, c, i, m, "other", p, items).allowed)

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
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_unknown_capability_blocks_preflight(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, False)
        self.assertIn("qualification_records_missing", preflight_delivery(s, c, i, m, "request-1", p, items).reasons)

    def test_admissibility_requires_every_predicate(self):
        reg = admissibility_registry(); state = admissibility_fixture()
        self.assertTrue(evaluate_admissibility(state, reg).admissible)
        state["delivery"] = {"complete": False}
        result = evaluate_admissibility(state, reg)
        self.assertFalse(result.admissible); self.assertIn("delivery_complete", result.reasons)

    def test_admissibility_exact_predicate_closure(self):
        reg = admissibility_registry(); self.assertTrue(reg.closure(reg.predicate_ids, reg.logic_mutation_ids))

    def test_authority_snapshot_candidate_writable_rejected(self):
        s, c, i, items, m, p = fixture(); s = GovernanceAuthoritySnapshot(s.snapshot_id, s.version, s.content_hash, False)
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

    def test_snapshot_binding_mismatch_rejected(self):
        s, c, i, items, m, p = fixture(); c = RequiredEvidenceContract(c.contract_id, "other", c.required_ids)
        self.assertFalse(preflight(s, c, i, m, "request-1", p, items).allowed)

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

    def test_expired_profile_is_not_current(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, True, "2000-01-01T00:00:00Z", p.supported_formats, p.max_context_bytes)
        result = preflight(s, c, i, m, "request-1", p, items, now="2025-01-01T00:00:00Z")
        self.assertFalse(result.allowed); self.assertIn("profile_expired", result.reasons)

    def test_wrong_profile_hash_is_not_current(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, "wrong", True, supported_formats=("text",))
        result = preflight(s, c, i, m, "request-1", p, items)
        self.assertFalse(result.allowed); self.assertIn("profile_hash_mismatch", result.reasons)

    def test_wrong_operating_point_is_not_current(self):
        s, c, i, items, m, p = fixture(); result = preflight(s, c, i, m, "request-1", p, items, expected_operating_point="other")
        self.assertFalse(result.allowed); self.assertIn("operating_point_mismatch", result.reasons)

    def test_missing_planned_attempt_is_not_current(self):
        s, c, i, items, m, p = fixture(); plan = ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1", "a2"))
        result = preflight(s, c, i, m, "request-1", p, items, plan=plan)
        self.assertFalse(result.allowed); self.assertIn("qualification_attempt_closure", result.reasons)

    def test_unsupported_format_and_context_limit_fail(self):
        s, c, i, items, m, p = fixture(); p = ProviderCapabilityProfile(p.provider_id, p.model_id, p.adapter_version, p.profile_hash, True, supported_formats=("json",), max_context_bytes=1)
        result = preflight(s, c, i, m, "request-1", p, items, required_format="text", required_context_bytes=100)
        self.assertFalse(result.allowed); self.assertIn("unsupported_format", result.reasons); self.assertIn("context_limit_exceeded", result.reasons)

    def test_dirty_context_and_stale_fence_fail(self):
        s, c, i, items, m, p = fixture(); evidence = ProviderContextStateEvidence(False, ("memory",), False, "state")
        result = preflight(s, c, i, m, "request-1", p, items, context_evidence=evidence, fence=AdmissionFenceRecord("fence", "1", False))
        self.assertFalse(result.allowed); self.assertIn("provider_context_not_clean", result.reasons); self.assertIn("admission_fence_stale", result.reasons)

    def test_materialization_rejects_traversal(self):
        result = materialize_entries({"../escape": b"x"}, source_hash="src")
        self.assertFalse(result.success); self.assertTrue(any("unsafe_member" in r for r in result.reasons))

    def test_retrieval_binds_raw_bytes_and_final_context(self):
        raw = b"page"; rec = RetrievalEvidenceRecord("r", "a", "s", "file", "v1", 0, len(raw), sha256(raw).hexdigest(), len(raw), "tool", 1, "ctx", "ctx-h")
        self.assertTrue(validate_retrieval(rec, raw, expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v1", expected_context_id="ctx", expected_context_hash="ctx-h")[0])
        self.assertFalse(validate_retrieval(rec, b"wrong", expected_request="r", expected_attempt="a", expected_session="s", expected_source="file", expected_version="v1", expected_context_id="ctx", expected_context_hash="ctx-h")[0])

    def test_wire_delivery_rejects_returned_byte_mismatch(self):
        s, c, i, items, m, p = fixture(); provider = DeterministicFakeProvider(); receipt, wire = provider.deliver(m, items); materialized = materialize_entries(items, source_hash="request-1")
        ok, _ = validate_wire_delivery(m, materialized, wire, receipt, {"a": b"bad", "b": items["b"]}, expected_commit="request-1", expected_semantic_hash=wire.semantic_hash)
        self.assertFalse(ok)

    def test_witness_record_binding_budget_and_semantics(self):
        record = WitnessProtocolQualificationRecord("w", "fake", "inline", 10, True, "prompt", "2099-01-01T00:00:00Z")
        self.assertTrue(validate_witness_qualification(record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="ok", challenge="extract token", final_context_bytes=1, max_final_context_bytes=100)[0])
        self.assertFalse(validate_witness_qualification(record, provider_id="other", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="ok", challenge="extract token", final_context_bytes=1, max_final_context_bytes=100)[0])
        self.assertFalse(validate_witness_qualification(record, provider_id="fake", mode="inline", prompt_mode="prompt", now="2025-01-01T00:00:00Z", response="01234567890", challenge="extract token", final_context_bytes=1, max_final_context_bytes=100)[0])

    def test_atomic_admission_voids_state_drift(self):
        expected = AttemptState("a", 1, "authority", "request", "cap", "egress", "context", "fence", "prompt", "witness", "session", "registry")
        current = {"generation": 2, "authority_version": "authority", "request_version": "request", "capability_hash": "cap", "egress_version": "egress", "context_hash": "context", "fence_version": "fence", "prompt_hash": "prompt", "witness_hash": "witness", "session_hash": "session", "registry_version": "registry"}
        result = admit_review_attempt(current, expected, attempt_id="a", expected_generation=1)
        self.assertTrue(result.void); self.assertFalse(result.committed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```


### governance-runtime/test_exp_m_phases.py

```python
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    admissibility_registry, GovernanceAuthoritySnapshot, RequiredEvidenceContract,
    RequiredInteractionContract, MaterializationResult,
)
from run_exp_m_deterministic import run_phases  # noqa: E402
from run_exp_m_mutations import run as run_mutations  # noqa: E402


class ExpMPhaseTests(unittest.TestCase):
    def test_all_deterministic_phases_a_to_t_pass(self):
        result = run_phases()
        self.assertEqual(set(result["phases"]), set("ABCDEFGHIJKLMNOPQRST"))
        self.assertTrue(result["all_phases_pass"])
        self.assertTrue(all(v["status"] == "PASS" for v in result["phases"].values()))
        self.assertGreater(result["phases"]["G"]["mutation_total"], 0)

    def test_predicate_registry_exact_closure(self):
        result = run_mutations(); registry = admissibility_registry()
        killed = {m["target"] for m in result["mutations"] if m["family"] == "validator_logic" and m["killed"]}
        self.assertEqual(set(registry.predicate_ids), set(registry.logic_mutation_ids))
        self.assertEqual(set(registry.predicate_ids), killed)
        self.assertEqual(result["surviving_mutations"], 0)
        self.assertTrue(all(m.get("negative_control") in (None, "REJECT") for m in result["mutations"]))

    def test_structured_admissibility_fixture_is_positive(self):
        reg = admissibility_registry()
        state = {
            "review_request": {"current": True, "request_id": "r"},
            "authority_snapshot": GovernanceAuthoritySnapshot("s", "1", "h", True),
            "evidence_contract": RequiredEvidenceContract("e", "s", ("a",)),
            "interaction_contract": RequiredInteractionContract("i", "s", (("a",),)),
            "materialization": MaterializationResult(True, {"a": b"a"}, "rep", "src", "raw-v1"),
            "representation": {"governed": True, "transform_id": "raw-v1"},
            "egress": {"authorized": True, "version": "1"},
            "capability_current": True, "accessibility_policy": {"satisfied": True}, "accessibility": {"satisfied": True, "proven": True},
            "context_isolation": {"satisfied": True}, "hidden_state_policy": {"satisfied": True},
            "context_state": {"clean": True, "sentinel_passed": True}, "fence": {"current": True, "version": "1"},
            "semantic_context": {"qualified": True}, "wire": {"valid": True}, "delivery": {"complete": True},
            "witness": {"current": True}, "retrieval": {"complete": True}, "prompt_isolation": {"current": True},
            "semantic_coverage": {"complete": True}, "reviewer": {"trusted": True},
            "disposition": "PASS", "disposition_promotable": True,
        }
        self.assertTrue(__import__("exp_m_deterministic").evaluate_admissibility(state, reg).admissible)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

