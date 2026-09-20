"""Deterministic EXP-M evidence-delivery governor.

This module is deliberately provider-neutral.  It models the governed delivery
boundary and uses content-addressed, immutable records so fake/adversarial
providers can exercise the same production predicates without external calls.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict, is_dataclass
from hashlib import sha256
import json
import sqlite3
import threading
import posixpath
import zipfile
from datetime import datetime, timezone
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
    qualification_profile: str = "TEST_PROFILE"


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
    protocol_version: str = "R5-CP-1"


@dataclass(frozen=True)
class ContextIsolationVerdict:
    policy: ProviderContextIsolationPolicy | None
    evidence: ProviderContextStateEvidence | None
    fence: AdmissionFenceRecord | None
    transition_class: str
    required_channels: tuple[str, ...]


@dataclass(frozen=True)
class AccessibilityPolicyEvidence:
    policy_version: str
    proof_mode: str
    deterministic_required: bool
    satisfied_by: str


@dataclass(frozen=True)
class SemanticContextQualificationRecord:
    context_id: str
    context_hash: str
    qualified: bool
    source_hash: str
    context_bytes: bytes = b""
    qualification_receipt_hash: str = ""


@dataclass(frozen=True)
class WitnessChallengeEvidence:
    challenge_id: str
    source_slice_id: str
    source_slice_hash: str
    expected_answer_hash: str
    provider_id: str
    mode: str
    prompt_isolation_mode: str
    response_hash: str
    response_length: int
    final_context_id: str
    final_context_bytes_before: int
    final_context_bytes_after: int
    semantics_class: str = "EXTRACTION_ACCESSIBILITY"


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
    observation_hash: str = ""

    def __post_init__(self) -> None:
        if not self.observation_hash:
            object.__setattr__(self, "observation_hash", digest({"channels": tuple(self.observable_channels), "state_hash": self.state_hash, "clean": self.clean, "sentinel_passed": self.sentinel_passed}))


@dataclass(frozen=True)
class AdmissionFenceRecord:
    fence_id: str
    version: str
    current: bool
    issued_at: str | None = None
    state_hash: str = ""

    def __post_init__(self) -> None:
        if not self.state_hash:
            object.__setattr__(self, "state_hash", digest({"fence_id": self.fence_id, "version": self.version, "current": self.current}))


@dataclass(frozen=True)
class PromptIsolationQualificationRecord:
    record_id: str
    provider_id: str
    mode: str
    current: bool
    expires_at: str | None = None
    issued_at: str | None = None
    record_hash: str = ""

    def __post_init__(self) -> None:
        if not self.record_hash:
            object.__setattr__(self, "record_hash", digest({"record_id": self.record_id, "provider_id": self.provider_id, "mode": self.mode, "current": self.current, "expires_at": self.expires_at}))


@dataclass(frozen=True)
class WitnessProtocolQualificationRecord:
    record_id: str
    provider_id: str
    mode: str
    max_response_bytes: int
    current: bool
    prompt_isolation_mode: str = ""
    expires_at: str | None = None
    issued_at: str | None = None
    record_hash: str = ""

    def __post_init__(self) -> None:
        if not self.record_hash:
            object.__setattr__(self, "record_hash", digest({"record_id": self.record_id, "provider_id": self.provider_id, "mode": self.mode, "max_response_bytes": self.max_response_bytes, "current": self.current, "prompt_isolation_mode": self.prompt_isolation_mode, "expires_at": self.expires_at}))


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
    provider_request_id: str = ""
    request_hash: str = ""


@dataclass(frozen=True)
class AdmissionCheckpoint:
    attempt_id: str
    generation: int
    disposition: str
    committed: bool
    void: bool
    reasons: tuple[str, ...] = ()


class PersistentAdmissionLedger:
    """Transactional persistent ledger; terminal states survive restart and races."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._db = self.path.with_suffix(self.path.suffix + ".sqlite")
        with sqlite3.connect(self._db, timeout=5, isolation_level=None) as conn:
            conn.execute("PRAGMA journal_mode=DELETE")
            conn.execute("CREATE TABLE IF NOT EXISTS admissions (attempt_id TEXT PRIMARY KEY, generation INTEGER NOT NULL, disposition TEXT NOT NULL)")
            conn.execute("CREATE TABLE IF NOT EXISTS protected_state (id INTEGER PRIMARY KEY CHECK(id=1), generation INTEGER NOT NULL, state_hash TEXT NOT NULL)")
            conn.execute("INSERT OR IGNORE INTO protected_state(id,generation,state_hash) VALUES(1,0,'')")

    def compare_and_set(self, attempt_id: str, generation: int, disposition: str, *, expected_state_hash: str | None = None, next_state_hash: str | None = None) -> AdmissionCheckpoint:
        if disposition not in ("VOID", "COMMITTED"):
            return AdmissionCheckpoint(attempt_id, generation, "VOID", False, True, ("invalid_terminal_state",))
        with sqlite3.connect(self._db, timeout=5, isolation_level="IMMEDIATE") as conn:
            conn.execute("BEGIN IMMEDIATE")
            protected = conn.execute("SELECT generation,state_hash FROM protected_state WHERE id=1").fetchone()
            if expected_state_hash is not None and (protected is None or protected[1] != expected_state_hash or int(protected[0]) != generation):
                conn.rollback()
                return AdmissionCheckpoint(attempt_id, generation, "VOID", False, True, ("protected_state_generation_drift",))
            current = conn.execute("SELECT generation, disposition FROM admissions WHERE attempt_id=?", (attempt_id,)).fetchone()
            if current is not None:
                conn.commit()
                return AdmissionCheckpoint(attempt_id, int(current[0]), str(current[1]), False, current[1] == "VOID", ("terminal_state",))
            conn.execute("INSERT INTO admissions(attempt_id,generation,disposition) VALUES(?,?,?)", (attempt_id, generation, disposition))
            if disposition == "COMMITTED":
                conn.execute("UPDATE protected_state SET generation=?, state_hash=? WHERE id=1", (generation + 1, next_state_hash or str(generation + 1)))
            conn.commit()
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
    proof_mode: str = ""
    policy_version: str = ""
    evidence_hash: str = ""
    proof_hash: str = ""
    issued_at: str | None = None


@dataclass(frozen=True)
class ReviewerProvenanceRecord:
    reviewer_id: str
    policy_hash: str
    trusted: bool
    authorization_source: str = ""
    record_hash: str = ""
    issued_at: str | None = None


@dataclass(frozen=True)
class SemanticCoverageRecord:
    coverage_id: str
    context_id: str
    complete: bool
    source_hash: str = ""
    coverage_hash: str = ""
    context_hash: str = ""
    evidence_ids: tuple[str, ...] = ()


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

    def closure(self, verdict_ids: Iterable[str], killed_ids: Iterable[str], *, declared_mutations: Iterable[str] | None = None, executed_mutations: Iterable[str] | None = None, declared_fixtures: Iterable[str] | None = None, executed_fixtures: Iterable[str] | None = None, killed_mutations: Iterable[str] | None = None, executed_fixture_targets: Iterable[str] | None = None) -> bool:
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
        verdict = targets(verdict_ids)
        killed = targets(killed_ids)
        if any(value is None for value in (declared_mutations, executed_mutations, declared_fixtures, executed_fixtures, killed_mutations, executed_fixture_targets)):
            return False
        mutation_declared = set(declared_mutations)
        mutation_executed = set(executed_mutations)
        mutation_killed = set(killed_mutations)
        fixture_declared = set(declared_fixtures)
        fixture_executed = set(executed_fixtures)
        fixture_targets = set(executed_fixture_targets)
        return (required == verdict and required == killed and
                mutation_declared == required and mutation_executed == mutation_declared and mutation_killed == required and
                fixture_declared == set(self.fixture_ids) and fixture_executed == fixture_declared and fixture_targets == required)


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
    expected_semantic_hash: str = ""
    expected_transition_class: str = "LOWER"
    expected_fence_version: str = "1"
    expected_witness_answer_hash: str = digest("answer")
    expected_challenge_id: str = ""
    expected_reviewer_policy_hash: str = "policy"
    expected_context_state_hash: str = "state"
    expected_fence_state_hash: str = ""
    expected_qualification_profile: str = "TEST_PROFILE"


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
        expected_semantic_hash=str(state.get("expected_semantic_hash", "")),
        expected_transition_class=str(state.get("expected_transition_class", state.get("transition_class", "LOWER"))),
        expected_fence_version=str(state.get("expected_fence_version", "1")),
        expected_witness_answer_hash=str(state.get("expected_witness_answer_hash", digest(state.get("witness_expected_answer", "answer")))),
        expected_challenge_id=str(state.get("expected_challenge_id", "challenge")),
        expected_reviewer_policy_hash=str(state.get("expected_reviewer_policy_hash", "policy")),
        expected_context_state_hash=str(state.get("expected_context_state_hash", digest({"channels": ("memory", "config"), "state_hash": "state", "clean": True, "sentinel_passed": True}))),
        expected_fence_state_hash=str(state.get("expected_fence_state_hash", digest({"fence_id": "fence", "version": "1", "current": True}))),
        expected_qualification_profile=str(state.get("expected_qualification_profile", "TEST_PROFILE")),
    )


def bundle_from_state(state: Mapping[str, Any]) -> EvidenceBundle:
    """Test-only fixture adapter. Production callers construct typed bundles directly."""
    out = dict(state)
    if "review_request" not in state or not isinstance(state.get("review_request"), Mapping):
        return EvidenceBundle(out)
    request_id, attempt_id, session_id = str(state.get("expected_request_id", "r")), str(state.get("expected_attempt_id", "a")), str(state.get("expected_session_id", "s"))
    if "interaction_contract" in state and "observed_interactions" not in out and isinstance(state.get("interaction_contract"), RequiredInteractionContract):
        # Test adapter records an observed delivery trace; production callers
        # must populate this from the delivered context, not the contract.
        out["observed_interactions"] = tuple(state["interaction_contract"].interactions)
    reviewed_commit = str(state.get("expected_reviewed_commit", "commit"))
    profile = ProviderCapabilityProfile("fake", "deterministic", "adapter", "profile-hash", True, supported_formats=("text",), max_context_bytes=1_000_000)
    plan = ProviderQualificationExecutionPlan("plan", "fake", "default", ("a1",), ("a1",))
    record = ProviderCapabilityQualificationRecord("plan", "profile-hash", True, True, 0, "default", ("a1",), ("a1",), "fake", "deterministic", attempt_records=(PhysicalAttemptRecord("a1", "a1", None, "FIRST", request_id, session_id, "wire-a1", "OK"),))
    out.setdefault("capability_profile", profile); out.setdefault("qualification_plan", plan); out.setdefault("capability_record", record)
    if not isinstance(out.get("capability_profile"), ProviderCapabilityProfile): out["capability_profile"] = profile
    if not isinstance(out.get("qualification_plan"), ProviderQualificationExecutionPlan): out["qualification_plan"] = plan
    if not isinstance(out.get("capability_record"), ProviderCapabilityQualificationRecord): out["capability_record"] = record
    if isinstance(state.get("capability"), Mapping) and state["capability"].get("validated") is not True: out["capability_record"] = ProviderCapabilityQualificationRecord("bad", "bad", False, False)
    isolation = ContextIsolationVerdict(ProviderContextIsolationPolicy("policy", "COMPLETE_READABLE_FENCED_STATE"), ProviderContextStateEvidence(True, ("memory", "config"), True, "state"), AdmissionFenceRecord("fence", "1", True), "LOWER", ("memory", "config"))
    if ((isinstance(state.get("context_state"), Mapping) and not state["context_state"].get("clean", False)) or (isinstance(state.get("context_isolation"), Mapping) and not state["context_isolation"].get("satisfied", False)) or (isinstance(state.get("hidden_state_policy"), Mapping) and not state["hidden_state_policy"].get("satisfied", False))): isolation = ContextIsolationVerdict(isolation.policy, ProviderContextStateEvidence(False, tuple(state.get("context_state", {}).get("observable_channels", ())) if isinstance(state.get("context_state"), Mapping) else (), False, str(state.get("context_state", {}).get("state_hash", "")) if isinstance(state.get("context_state"), Mapping) else ""), isolation.fence, "LOWER", isolation.required_channels)
    if isinstance(state.get("fence"), Mapping) and not state["fence"].get("current", False): isolation = ContextIsolationVerdict(isolation.policy, isolation.evidence, AdmissionFenceRecord("fence", str(state["fence"].get("version", "")), False), "LOWER", isolation.required_channels)
    out["context_isolation_verdict"] = isolation
    if isinstance(state.get("accessibility_policy"), Mapping) and state["accessibility_policy"].get("satisfied") is False:
        out["accessibility_policy_record"] = ProviderAccessibilityRiskPolicy("LOWER", "invalid", True, False)
    elif not isinstance(out.get("accessibility_policy_record"), ProviderAccessibilityRiskPolicy): out["accessibility_policy_record"] = ProviderAccessibilityRiskPolicy("LOWER", "inline-deterministic", True, False)
    challenge = WitnessChallengeEvidence("challenge", "slice", "slice-hash", digest("answer"), "fake", "inline", "prompt", digest("answer"), len("answer"), "ctx", 10, 16)
    out.setdefault("witness_challenge", challenge); out.setdefault("witness_expected_answer", "answer"); out.setdefault("witness_response", "answer"); out.setdefault("witness_challenge_text", "extract token")
    if isinstance(state.get("witness"), Mapping) and state["witness"].get("validated") is False:
        out["witness"] = WitnessProtocolQualificationRecord("w", "fake", "inline", 100, False, "prompt", "2000-01-01T00:00:00Z")
    else:
        out.setdefault("witness", WitnessProtocolQualificationRecord("w", "fake", "inline", 100, True, "prompt", "2099-01-01T00:00:00Z"))
    if isinstance(state.get("prompt_isolation"), Mapping) and state["prompt_isolation"].get("current") is False:
        out["prompt_isolation"] = PromptIsolationQualificationRecord("prompt", "fake", "inline", False, "2000-01-01T00:00:00Z")
    if isinstance(state.get("semantic_context"), Mapping) and state["semantic_context"].get("qualified") is False:
        out["semantic_context"] = SemanticContextQualificationRecord("ctx", "wrong", False, "")
    elif not isinstance(out.get("semantic_context"), SemanticContextQualificationRecord): out["semantic_context"] = SemanticContextQualificationRecord("ctx", "ctx-h", True, reviewed_commit)
    if isinstance(state.get("semantic_coverage"), Mapping) and state["semantic_coverage"].get("complete") is False:
        out["semantic_coverage"] = SemanticCoverageRecord("cov", "ctx", False, "", "", "wrong")
    elif not isinstance(out.get("semantic_coverage"), SemanticCoverageRecord) or not out["semantic_coverage"].source_hash:
        out["semantic_coverage"] = SemanticCoverageRecord("cov", "ctx", True, reviewed_commit, "coverage-h", "ctx-h")
    raw_items = {"a": b"a"}; manifest = EvidenceDeliveryManifest.freeze(request_id, reviewed_commit, raw_items); materialized = materialize_entries(raw_items, source_hash=reviewed_commit)
    provider = DeterministicFakeProvider(); receipt, wire = provider.deliver(manifest, raw_items)
    out["manifest"] = manifest
    if not (isinstance(state.get("materialization"), MaterializationResult) and not state["materialization"].success): out["materialization"] = materialized
    out.setdefault("returned_items", raw_items); out["receipt"] = receipt
    if isinstance(state.get("wire"), Mapping) and state["wire"].get("valid") is False: out["wire"] = None
    else: out["wire"] = wire
    if isinstance(state.get("delivery"), Mapping) and (state["delivery"].get("complete") is False or state["delivery"].get("computed_complete") is False):
        out["returned_items"] = {"a": b"changed"}
    if isinstance(state.get("accessibility"), Mapping) and state["accessibility"].get("proven") is False:
        out["accessibility"] = AccessibilityProofRecord("proof", "challenge", "fake", "inline-deterministic", "ctx", False, "inline-deterministic", "LOWER", "")
    elif not isinstance(out.get("accessibility"), AccessibilityProofRecord) or not out["accessibility"].evidence_hash:
        out["accessibility"] = AccessibilityProofRecord("proof", "challenge", "fake", "inline", "ctx", True, "inline-deterministic", "LOWER", digest(challenge))
    if isinstance(state.get("reviewer"), Mapping) and state["reviewer"].get("trusted") is False:
        out["reviewer"] = ReviewerProvenanceRecord("reviewer", "", False, "")
    elif not isinstance(out.get("reviewer"), ReviewerProvenanceRecord) or not out["reviewer"].authorization_source:
        out["reviewer"] = ReviewerProvenanceRecord("reviewer", "policy", True, "trusted-review-artifact")
    return EvidenceBundle(out)


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
# Independent, review-owned catalogs.  These are intentionally declared in a
# separate block rather than generated from the production validator map.
INDEPENDENT_MUTATION_CATALOG = (
    {"id": "negative:review_request_current", "target": "review_request_current"},
    {"id": "negative:authority_snapshot_current", "target": "authority_snapshot_current"},
    {"id": "negative:evidence_contract_closed", "target": "evidence_contract_closed"},
    {"id": "negative:interaction_contract_closed", "target": "interaction_contract_closed"},
    {"id": "negative:materialization_complete", "target": "materialization_complete"},
    {"id": "negative:representation_governed", "target": "representation_governed"},
    {"id": "negative:egress_authorized", "target": "egress_authorized"},
    {"id": "negative:capability_current", "target": "capability_current"},
    {"id": "negative:accessibility_policy_satisfied", "target": "accessibility_policy_satisfied"},
    {"id": "negative:context_isolation_satisfied", "target": "context_isolation_satisfied"},
    {"id": "negative:hidden_state_policy_satisfied", "target": "hidden_state_policy_satisfied"},
    {"id": "negative:context_state_clean", "target": "context_state_clean"},
    {"id": "negative:admission_fence_current", "target": "admission_fence_current"},
    {"id": "negative:semantic_context_qualified", "target": "semantic_context_qualified"},
    {"id": "negative:wire_binding_valid", "target": "wire_binding_valid"},
    {"id": "negative:delivery_complete", "target": "delivery_complete"},
    {"id": "negative:accessibility_proven", "target": "accessibility_proven"},
    {"id": "negative:witness_record_current", "target": "witness_record_current"},
    {"id": "negative:session_retrieval_coverage", "target": "session_retrieval_coverage"},
    {"id": "negative:prompt_isolation_current", "target": "prompt_isolation_current"},
    {"id": "negative:semantic_coverage", "target": "semantic_coverage"},
    {"id": "negative:reviewer_provenance", "target": "reviewer_provenance"},
    {"id": "negative:disposition_promotable", "target": "disposition_promotable"},
)
# Review-owned negative fixtures are independently declared.  They are not
# aliases of the mutation catalog and each names its immutable constructor and
# rejection expectation.
INDEPENDENT_FIXTURE_CATALOG = (
    {"fixture_id": "negative:review_request_current", "target_predicate_id": "review_request_current", "constructor": "fixture_review_request_not_current", "expected_rejection": "review_request_current"},
    {"fixture_id": "negative:authority_snapshot_current", "target_predicate_id": "authority_snapshot_current", "constructor": "fixture_candidate_writable_snapshot", "expected_rejection": "authority_snapshot_current"},
    {"fixture_id": "negative:evidence_contract_closed", "target_predicate_id": "evidence_contract_closed", "constructor": "fixture_open_evidence_contract", "expected_rejection": "evidence_contract_closed"},
    {"fixture_id": "negative:interaction_contract_closed", "target_predicate_id": "interaction_contract_closed", "constructor": "fixture_open_interaction_contract", "expected_rejection": "interaction_contract_closed"},
    {"fixture_id": "negative:materialization_complete", "target_predicate_id": "materialization_complete", "constructor": "fixture_failed_materialization", "expected_rejection": "materialization_complete"},
    {"fixture_id": "negative:representation_governed", "target_predicate_id": "representation_governed", "constructor": "fixture_unqualified_representation", "expected_rejection": "representation_governed"},
    {"fixture_id": "negative:egress_authorized", "target_predicate_id": "egress_authorized", "constructor": "fixture_revoked_egress", "expected_rejection": "egress_authorized"},
    {"fixture_id": "negative:capability_current", "target_predicate_id": "capability_current", "constructor": "fixture_expired_capability", "expected_rejection": "capability_current"},
    {"fixture_id": "negative:accessibility_policy_satisfied", "target_predicate_id": "accessibility_policy_satisfied", "constructor": "fixture_wrong_accessibility_policy", "expected_rejection": "accessibility_policy_satisfied"},
    {"fixture_id": "negative:context_isolation_satisfied", "target_predicate_id": "context_isolation_satisfied", "constructor": "fixture_dirty_context", "expected_rejection": "context_isolation_satisfied"},
    {"fixture_id": "negative:hidden_state_policy_satisfied", "target_predicate_id": "hidden_state_policy_satisfied", "constructor": "fixture_hidden_state", "expected_rejection": "hidden_state_policy_satisfied"},
    {"fixture_id": "negative:context_state_clean", "target_predicate_id": "context_state_clean", "constructor": "fixture_dirty_context_state", "expected_rejection": "context_state_clean"},
    {"fixture_id": "negative:admission_fence_current", "target_predicate_id": "admission_fence_current", "constructor": "fixture_stale_fence", "expected_rejection": "admission_fence_current"},
    {"fixture_id": "negative:semantic_context_qualified", "target_predicate_id": "semantic_context_qualified", "constructor": "fixture_wrong_context_hash", "expected_rejection": "semantic_context_qualified"},
    {"fixture_id": "negative:wire_binding_valid", "target_predicate_id": "wire_binding_valid", "constructor": "fixture_wrong_wire", "expected_rejection": "wire_binding_valid"},
    {"fixture_id": "negative:delivery_complete", "target_predicate_id": "delivery_complete", "constructor": "fixture_incomplete_delivery", "expected_rejection": "delivery_complete"},
    {"fixture_id": "negative:accessibility_proven", "target_predicate_id": "accessibility_proven", "constructor": "fixture_wrong_accessibility_evidence", "expected_rejection": "accessibility_proven"},
    {"fixture_id": "negative:witness_record_current", "target_predicate_id": "witness_record_current", "constructor": "fixture_expired_witness", "expected_rejection": "witness_record_current"},
    {"fixture_id": "negative:session_retrieval_coverage", "target_predicate_id": "session_retrieval_coverage", "constructor": "fixture_wrong_retrieval_session", "expected_rejection": "session_retrieval_coverage"},
    {"fixture_id": "negative:prompt_isolation_current", "target_predicate_id": "prompt_isolation_current", "constructor": "fixture_expired_prompt_isolation", "expected_rejection": "prompt_isolation_current"},
    {"fixture_id": "negative:semantic_coverage", "target_predicate_id": "semantic_coverage", "constructor": "fixture_incomplete_semantic_coverage", "expected_rejection": "semantic_coverage"},
    {"fixture_id": "negative:reviewer_provenance", "target_predicate_id": "reviewer_provenance", "constructor": "fixture_untrusted_reviewer", "expected_rejection": "reviewer_provenance"},
    {"fixture_id": "negative:disposition_promotable", "target_predicate_id": "disposition_promotable", "constructor": "fixture_non_promotable_disposition", "expected_rejection": "disposition_promotable"},
)
FIXTURE_IDS = tuple(item["fixture_id"] for item in INDEPENDENT_FIXTURE_CATALOG)


def admissibility_registry() -> AdmissibilityPredicateRegistry:
    return AdmissibilityPredicateRegistry("2", tuple(d["id"] for d in PREDICATE_DEFINITIONS), tuple(item["target"] for item in INDEPENDENT_MUTATION_CATALOG), FIXTURE_IDS)


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

    def capability_valid(state: Mapping[str, Any]) -> bool:
        profile, plan, record = state.get("capability_profile"), state.get("qualification_plan"), state.get("capability_record")
        if not isinstance(profile, ProviderCapabilityProfile) or not isinstance(plan, ProviderQualificationExecutionPlan) or not isinstance(record, ProviderCapabilityQualificationRecord):
            return False
        return validate_capability(profile, plan, record, now=str(state.get("now", "2099-01-01T00:00:00Z")), expected_provider=context.expected_provider, expected_model=context.expected_model, expected_operating_point=context.expected_operating_point, expected_profile_hash=context.expected_profile_hash, required_format="text", required_context_bytes=context.max_context_bytes)[0]

    def context_isolation_valid(state: Mapping[str, Any]) -> bool:
        record = state.get("context_isolation_verdict")
        if not isinstance(record, ContextIsolationVerdict):
            return False
        return validate_context_isolation(record.policy, record.evidence, record.fence, transition_class=record.transition_class, required_channels=record.required_channels, expected_observation_hash=context.expected_context_state_hash if context.expected_context_state_hash and len(context.expected_context_state_hash) == 64 else None, expected_fence_state_hash=context.expected_fence_state_hash)[0]

    def accessibility_policy_valid(state: Mapping[str, Any]) -> bool:
        policy, proof = state.get("accessibility_policy_record"), state.get("accessibility")
        if not isinstance(policy, ProviderAccessibilityRiskPolicy) or not isinstance(proof, AccessibilityProofRecord):
            return False
        if proof.proof_mode != policy.proof_mode or proof.policy_version != policy.transition_class or not proof.evidence_hash:
            return False
        if policy.deterministic_required and proof.proof_mode != "inline-deterministic":
            return False
        return bool(proof.proof_id and proof.challenge_id and proof.provider_id == context.expected_provider and proof.proof_mode == policy.proof_mode and proof.evidence_hash)

    def semantic_context_valid(state: Mapping[str, Any]) -> bool:
        record = state.get("semantic_context")
        if not isinstance(record, SemanticContextQualificationRecord):
            return False
        if record.context_id != context.final_context_id or record.context_hash != context.final_context_hash or record.source_hash != context.reviewed_commit:
            return False
        if record.context_bytes and digest(record.context_bytes) != record.context_hash:
            return False
        return bool(record.qualification_receipt_hash or record.source_hash)

    def wire_valid(state: Mapping[str, Any]) -> bool:
        manifest, materialized, wire, receipt, returned = state.get("manifest"), state.get("materialization"), state.get("wire"), state.get("receipt"), state.get("returned_items")
        if not isinstance(manifest, EvidenceDeliveryManifest) or not isinstance(materialized, MaterializationResult) or not isinstance(wire, WireDeliveryRecord) or not isinstance(receipt, ReviewerReceipt) or not isinstance(returned, Mapping) or any(not isinstance(v, bytes) for v in returned.values()):
            return False
        return validate_wire_delivery(manifest, materialized, wire, receipt, returned, expected_commit=context.reviewed_commit, expected_semantic_hash=context.expected_semantic_hash or None)[0]

    def delivery_valid(state: Mapping[str, Any]) -> bool:
        return wire_valid(state)

    def accessibility_proof_valid(state: Mapping[str, Any]) -> bool:
        proof, challenge = state.get("accessibility"), state.get("witness_challenge")
        if not isinstance(proof, AccessibilityProofRecord) or not isinstance(challenge, WitnessChallengeEvidence):
            return False
        if proof.final_context_id != context.final_context_id or proof.challenge_id != challenge.challenge_id:
            return False
        return proof.evidence_hash == digest(challenge) and proof.provider_id == context.expected_provider

    def witness_valid(state: Mapping[str, Any]) -> bool:
        record, challenge = state.get("witness"), state.get("witness_challenge")
        if not isinstance(record, WitnessProtocolQualificationRecord) or not isinstance(challenge, WitnessChallengeEvidence):
            return False
        if context.expected_witness_answer_hash and challenge.expected_answer_hash != context.expected_witness_answer_hash:
            return False
        return validate_witness_qualification(record, provider_id=context.witness_provider, mode=context.witness_mode, prompt_mode=context.witness_prompt_mode, now=str(state.get("now", "2025-01-01T00:00:00Z")), response=str(state.get("witness_response", "")), challenge=str(state.get("witness_challenge_text", "")), final_context_bytes=challenge.final_context_bytes_before, max_final_context_bytes=context.max_context_bytes)[0] and challenge.final_context_bytes_after == challenge.final_context_bytes_before + challenge.response_length

    def semantic_coverage_valid(state: Mapping[str, Any]) -> bool:
        coverage = state.get("semantic_coverage")
        return isinstance(coverage, SemanticCoverageRecord) and coverage.context_id == context.final_context_id and (coverage.context_hash or context.final_context_hash) == context.final_context_hash and coverage.source_hash == context.reviewed_commit and bool(coverage.coverage_hash) and bool(coverage.evidence_ids or coverage.coverage_hash)

    def reviewer_valid(state: Mapping[str, Any]) -> bool:
        reviewer = state.get("reviewer")
        return isinstance(reviewer, ReviewerProvenanceRecord) and reviewer.policy_hash == context.expected_reviewer_policy_hash and bool(reviewer.authorization_source) and reviewer.authorization_source != "caller"

    return {
        "review_request_current": lambda s: isinstance(s.get("review_request"), Mapping) and s["review_request"].get("current") is True and s["review_request"].get("request_id") == context.request_id,
        "authority_snapshot_current": lambda s: isinstance(s.get("authority_snapshot"), GovernanceAuthoritySnapshot) and s["authority_snapshot"].outside_candidate_write_authority and s["authority_snapshot"].snapshot_id == context.authority_snapshot_id and s["authority_snapshot"].content_hash == context.authority_snapshot_hash and s["authority_snapshot"].version == context.authority_version,
        "evidence_contract_closed": lambda s: isinstance(s.get("evidence_contract"), RequiredEvidenceContract) and s["evidence_contract"].closed and s["evidence_contract"].non_vacuous,
        "interaction_contract_closed": lambda s: isinstance(s.get("interaction_contract"), RequiredInteractionContract) and s["interaction_contract"].closed and bool(s["interaction_contract"].interactions) and s.get("observed_interactions") is not None and {tuple(x) for x in s.get("observed_interactions", ())} == {tuple(x) for x in s["interaction_contract"].interactions},
        "materialization_complete": lambda s: isinstance(s.get("materialization"), MaterializationResult) and s["materialization"].success,
        "representation_governed": lambda s: isinstance(s.get("representation"), RepresentationRecord) and s["representation"].transform_id in QUALIFIED_TRANSFORMS and s["representation"].registry_version == QUALIFIED_TRANSFORMS[s["representation"].transform_id] and bool(s["representation"].source_hash) and bool(s["representation"].representation_hash) and bool(s["representation"].parameters_hash) and bool(s["representation"].coverage_hash),
        "egress_authorized": egress_valid,
        "capability_current": capability_valid,
        "accessibility_policy_satisfied": accessibility_policy_valid,
        "context_isolation_satisfied": context_isolation_valid,
        "hidden_state_policy_satisfied": context_isolation_valid,
        "context_state_clean": context_isolation_valid,
        "admission_fence_current": context_isolation_valid,
        "semantic_context_qualified": semantic_context_valid,
        "wire_binding_valid": wire_valid,
        "delivery_complete": delivery_valid,
        "accessibility_proven": accessibility_proof_valid,
        "witness_record_current": witness_valid,
        "session_retrieval_coverage": lambda s: isinstance(s.get("retrieval"), RetrievalEvidenceRecord) and validate_retrieval(s["retrieval"], s.get("retrieval_bytes", b""), expected_request=context.request_id, expected_attempt=context.attempt_id, expected_session=context.session_id, expected_source=context.retrieval_source, expected_version=context.retrieval_version, expected_context_id=context.final_context_id, expected_context_hash=context.final_context_hash)[0],
        "prompt_isolation_current": prompt_valid,
        "semantic_coverage": semantic_coverage_valid,
        "reviewer_provenance": reviewer_valid,
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
    allowed_ids = set(evidence_contract.required_ids) | set(evidence_contract.optional_ids)
    manifest_ids = set(manifest.items)
    if (not evidence_contract.closed or not evidence_contract.non_vacuous or not evidence_contract.required_ids
            or len(evidence_contract.required_ids) != len(set(evidence_contract.required_ids))
            or len(evidence_contract.optional_ids) != len(set(evidence_contract.optional_ids))
            or not set(evidence_contract.required_ids).issubset(manifest_ids)
            or not manifest_ids.issubset(allowed_ids)):
        reasons.append("evidence_contract_unresolved")
    if not interactions.closed or not interactions.interactions or any(not set(interaction).issubset(manifest.items) for interaction in interactions.interactions):
        reasons.append("interaction_contract_unresolved")
    derived_interactions = tuple(tuple(interaction) for interaction in interactions.interactions if all(item_id in items for item_id in interaction))
    if tuple(derived_interactions) != tuple(interactions.interactions):
        reasons.append("interaction_observation_missing_from_delivered_context")
    if observed_interactions is None or {tuple(x) for x in observed_interactions} != {tuple(x) for x in derived_interactions}:
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
    # receipt.complete is a diagnostic consistency bit only; completeness is
    # recomputed from the manifest, returned bytes, receipt and wire identity.
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
    if any(item not in set(dispatched_ids) for item in retried_ids):
        reasons.append("retry_not_dispatched")
    if any(item not in set(dispatched_ids) for item in failed_ids):
        reasons.append("failed_attempt_not_dispatched")
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
    if len({r.attempt_id for r in records}) != len(records) or len({r.wire_hash for r in records}) != len(records):
        reasons.append("physical_attempt_or_wire_duplicate")
    provider_ids = [r.provider_request_id for r in records if r.provider_request_id]
    if len(provider_ids) != len(set(provider_ids)):
        reasons.append("provider_request_id_duplicate")
    if any(r.kind == "RETRY" and not r.parent_attempt_id for r in records):
        reasons.append("retry_parent_missing")
    if any(r.kind == "FIRST" and not r.planned_root_id for r in records):
        reasons.append("first_attempt_root_missing")
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


def validate_context_state(state: ProviderContextStateEvidence, *, required_channels: Sequence[str], expected_observation_hash: str | None = None) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    # clean/sentinel_passed are diagnostic cache fields; the observed channel
    # set and a content-bound state hash are authoritative.
    if not state.observable_channels:
        reasons.append("provider_context_not_observed")
    if not set(required_channels).issubset(state.observable_channels):
        reasons.append("context_channel_unobserved")
    if not state.state_hash:
        reasons.append("context_state_unbound")
    if state.observation_hash and state.observation_hash != digest({"channels": tuple(state.observable_channels), "state_hash": state.state_hash, "clean": state.clean, "sentinel_passed": state.sentinel_passed}):
        reasons.append("context_observation_hash_mismatch")
    if expected_observation_hash is not None and state.observation_hash != expected_observation_hash:
        reasons.append("context_expected_observation_mismatch")
    if not state.observation_hash:
        reasons.append("provider_context_observation_unbound")
    return not reasons, tuple(reasons)


def validate_fence(fence: AdmissionFenceRecord, expected_version: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if fence.version != expected_version:
        reasons.append("admission_fence_version_mismatch")
    if not fence.fence_id or (fence.state_hash and not isinstance(fence.state_hash, str)):
        reasons.append("admission_fence_unbound")
    if fence.state_hash != digest({"fence_id": fence.fence_id, "version": fence.version, "current": True}):
        reasons.append("admission_fence_state_mismatch")
        reasons.append("admission_fence_stale")
    return not reasons, tuple(reasons)


def validate_egress(egress: Mapping[str, Any], expected_version: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if egress.get("authorized") is not True or egress.get("version") != expected_version:
        reasons.append("egress_revoked_or_drifted")
    return not reasons, tuple(reasons)


def validate_prompt_isolation(record: PromptIsolationQualificationRecord, *, provider_id: str, mode: str, now: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if record.provider_id != provider_id or record.mode != mode or not record.record_id:
        reasons.append("prompt_isolation_binding")
    if record.record_hash != digest({"record_id": record.record_id, "provider_id": record.provider_id, "mode": record.mode, "current": True, "expires_at": record.expires_at}):
        reasons.append("prompt_isolation_record_not_currently_bound")
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
        if not safe_archive_member(entry.raw_name):
            reasons.append(f"unsafe_member:{entry.raw_name}")
            continue
        name = posixpath.normpath(entry.raw_name)
        if name != entry.raw_name or not safe_archive_member(name) or (entry.normalized_path and entry.normalized_path != name):
            reasons.append(f"normalized_path_mismatch:{entry.raw_name}")
            continue
        value = entry.data
        if name in seen:
            reasons.append(f"duplicate_normalized_member:{name}")
            continue
        seen.add(name)
        if entry.kind not in ("file", "symlink", "archive"):
            reasons.append(f"unsupported_member_kind:{name}")
        if entry.kind == "symlink" and (not entry.link_target or not safe_archive_member(posixpath.normpath(posixpath.join(posixpath.dirname(name), entry.link_target)))):
            reasons.append(f"symlink_escape:{name}")
        if entry.recursion_depth > max_recursion_depth:
            reasons.append(f"archive_recursion:{name}")
        if entry.compressed_size and len(value) > entry.compressed_size * max_ratio:
            reasons.append(f"decompression_ratio:{name}")
        if entry.kind == "file" and entry.uncompressed_size not in (0, len(value)):
            reasons.append(f"uncompressed_size_metadata_mismatch:{name}")
        if entry.kind == "file" and entry.compressed_size not in (0, len(value)):
            reasons.append(f"compressed_size_metadata_mismatch:{name}")
        if not isinstance(value, bytes):
            reasons.append(f"non_bytes:{name}")
            continue
        if entry.kind == "archive":
            try:
                with zipfile.ZipFile(__import__("io").BytesIO(value)) as archive:
                    for member in archive.infolist():
                        nested = posixpath.normpath(posixpath.join(posixpath.dirname(name), member.filename))
                        if not safe_archive_member(member.filename) or not safe_archive_member(nested):
                            reasons.append(f"nested_archive_escape:{member.filename}")
                            continue
                        nested_data = archive.read(member)
                        if len(nested_data) > max_member_bytes:
                            reasons.append(f"member_size_limit:{nested}")
                        if nested in seen:
                            reasons.append(f"duplicate_normalized_member:{nested}")
                        seen.add(nested)
                        clean[nested] = nested_data
                        total += len(nested_data)
            except (zipfile.BadZipFile, OSError):
                reasons.append(f"archive_parse_failed:{name}")
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
    attempts = list(record.attempt_records)
    physical_failures = sum(1 for a in attempts if getattr(a, "kind", "FIRST") == "FIRST" and getattr(a, "outcome", "") not in ("OK", "SUCCESS", "PASS"))
    if record.hard_failures != physical_failures:
        reasons.append("hard_failure_count_not_derived")
    if physical_failures != 0:
        reasons.append("qualification_not_statistically_valid")
    if plan.qualification_profile == "R5_PRODUCTION":
        if len(plan.trial_ids) < 2 or len(plan.confirmation_ids) < 1:
            reasons.append("production_confirmation_plan_too_small")
        if not attempts:
            reasons.append("production_attempts_missing")
    expected_roots = set(plan.trial_ids) | set(plan.confirmation_ids)
    if not record.planned_attempt_ids or not record.closed_attempt_ids or set(record.planned_attempt_ids) != expected_roots or set(record.closed_attempt_ids) != expected_roots:
        reasons.append("qualification_attempt_closure")
    if attempts:
        roots = [a for a in attempts if getattr(a, "kind", "FIRST") == "FIRST"]
        if {getattr(a, "planned_root_id", "") for a in roots} != expected_roots or len(roots) != len(set(getattr(a, "planned_root_id", "") for a in roots)):
            reasons.append("qualification_attempt_records_incomplete")
        if any(getattr(a, "kind", "") == "RETRY" and (getattr(a, "parent_attempt_id", None) is None or not any(getattr(p, "attempt_id", None) == getattr(a, "parent_attempt_id", None) and getattr(p, "outcome", "") == "FAILED" for p in attempts)) for a in attempts):
            reasons.append("qualification_retry_lineage_invalid")
    if profile.expires_at is not None and profile.expires_at <= now:
        reasons.append("profile_expired")
    return not reasons, tuple(reasons)


def validate_context_isolation(policy: ProviderContextIsolationPolicy, evidence: ProviderContextStateEvidence, fence: AdmissionFenceRecord, *, transition_class: str, required_channels: Sequence[str], expected_observation_hash: str | None = None, expected_fence_state_hash: str | None = None) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not policy.policy_id or policy.basis not in ("COMPLETE_READABLE_FENCED_STATE", "DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY"):
        reasons.append("context_policy_invalid")
    if transition_class == "HIGHEST" and policy.hidden_state_allowed:
        reasons.append("hidden_state_residual_disallowed")
    clean, clean_reasons = validate_context_state(evidence, required_channels=required_channels, expected_observation_hash=expected_observation_hash)
    if not clean:
        reasons.extend(clean_reasons)
    fence_ok, fence_reasons = validate_fence(fence, fence.version)
    if not fence_ok:
        reasons.extend(fence_reasons)
    if expected_fence_state_hash and fence.state_hash != expected_fence_state_hash:
        reasons.append("admission_fence_expected_state_mismatch")
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
    if record.provider_id != provider_id or record.mode != mode or record.prompt_isolation_mode != prompt_mode or not record.record_id:
        reasons.append("witness_record_binding")
    if record.record_hash != digest({"record_id": record.record_id, "provider_id": record.provider_id, "mode": record.mode, "max_response_bytes": record.max_response_bytes, "current": True, "prompt_isolation_mode": record.prompt_isolation_mode, "expires_at": record.expires_at}):
        reasons.append("witness_record_not_currently_bound")
    if record.expires_at is not None and record.expires_at <= now:
        reasons.append("witness_record_expired")
    if not challenge or not response or len(response.encode()) > record.max_response_bytes:
        reasons.append("witness_response_invalid")
    if final_context_bytes + len(response.encode()) > max_final_context_bytes:
        reasons.append("witness_context_eviction")
    if any(word in challenge.lower() for word in ("summarize", "judge", "evaluate", "defect")):
        reasons.append("witness_semantic_prompt")
    return not reasons, tuple(reasons)


def validate_wire_delivery(manifest: EvidenceDeliveryManifest, materialized: MaterializationResult, wire: WireDeliveryRecord, receipt: ReviewerReceipt, returned_items: Mapping[str, bytes], *, expected_commit: str, expected_semantic_hash: str | None) -> tuple[bool, tuple[str, ...]]:
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
    if expected_semantic_hash is not None and wire.semantic_hash != expected_semantic_hash:
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
        checkpoint = ledger.compare_and_set(attempt_id, expected.generation, "VOID", expected_state_hash=current.get("state_hash")) if ledger else AdmissionCheckpoint(attempt_id, expected.generation, "VOID", False, True, tuple(reasons))
        return AdmissionCheckpoint(checkpoint.attempt_id, checkpoint.generation, checkpoint.disposition, False, True, tuple(reasons) + tuple(checkpoint.reasons))
    if ledger:
        checkpoint = ledger.compare_and_set(attempt_id, expected.generation, "COMMITTED", expected_state_hash=current.get("state_hash"), next_state_hash=str(current.get("next_state_hash", expected.generation + 1)))
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
