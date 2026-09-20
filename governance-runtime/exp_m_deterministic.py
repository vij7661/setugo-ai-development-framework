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
import hmac
import threading
import posixpath
import zipfile
import math
from datetime import datetime, timezone
from typing import Any, Iterable, Mapping, Sequence
from pathlib import Path
from exp_m_predicate_registry import PLATFORM_PREDICATE_REGISTRY, required_predicate_ids
from exp_m_mutation_catalog import MUTATION_CATALOG, mutation_target_ids


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
class FinalContextInteractionEvidence:
    request_id: str
    session_id: str
    context_hash: str
    member_ids: tuple[str, ...]
    interactions: tuple[tuple[str, ...], ...]
    derived: bool = True
    assembly_receipt_hash: str = ""
    builder_identity: str = "trusted-final-context-builder"


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
    schedule_seed: str = ""
    scheduled_days: tuple[str, ...] = ()
    scheduled_time_blocks: tuple[str, ...] = ()
    production_envelope_hash: str = ""


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
    independence_status: str = "STATISTICAL_INDEPENDENCE_UNPROVEN"


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
    assembly_member_ids: tuple[str, ...] = ()


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
    channel_observations: tuple[Mapping[str, Any], ...] = ()
    observer_id: str = "platform-context-observer"

    def __post_init__(self) -> None:
        if not self.observation_hash:
            object.__setattr__(self, "observation_hash", digest({"channels": tuple(self.observable_channels), "state_hash": self.state_hash, "clean": self.clean, "sentinel_passed": self.sentinel_passed, "channel_observations": tuple(self.channel_observations), "observer_id": self.observer_id}))


@dataclass(frozen=True)
class AdmissionFenceRecord:
    fence_id: str
    version: str
    current: bool
    issued_at: str | None = None
    state_hash: str = ""
    authority_snapshot_id: str = "platform-protected-resource"
    authority_snapshot_hash: str = "protected-resource-v1"
    issuer_id: str = "platform-fence-observer"
    attestation_hash: str = "fence-attestation-v1"

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
    authority_id: str = "platform-prompt-authority"
    authority_digest: str = "prompt-authority-v1"
    record_version: str = "1"
    generation: int = 1
    revoked: bool = False

    def __post_init__(self) -> None:
        if not self.record_hash:
            object.__setattr__(self, "record_hash", digest({"record_id": self.record_id, "provider_id": self.provider_id, "mode": self.mode, "current": self.current, "expires_at": self.expires_at, "authority_id": self.authority_id, "authority_digest": self.authority_digest, "record_version": self.record_version, "generation": self.generation, "revoked": self.revoked}))


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
    authority_id: str = "platform-witness-authority"
    authority_digest: str = "witness-authority-v1"
    record_version: str = "1"
    generation: int = 1
    revoked: bool = False

    def __post_init__(self) -> None:
        if not self.record_hash:
            object.__setattr__(self, "record_hash", digest({"record_id": self.record_id, "provider_id": self.provider_id, "mode": self.mode, "max_response_bytes": self.max_response_bytes, "current": self.current, "prompt_isolation_mode": self.prompt_isolation_mode, "expires_at": self.expires_at, "authority_id": self.authority_id, "authority_digest": self.authority_digest, "record_version": self.record_version, "generation": self.generation, "revoked": self.revoked}))


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
    utc_day: str = ""
    time_block: str = ""


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
            conn.execute("INSERT OR IGNORE INTO protected_state(id,generation,state_hash) VALUES(1,1,'')")

    def seed_protected_state(self, generation: int, state_hash: str) -> None:
        """Test/bootstrap helper; authority code owns the initial protected state."""
        with sqlite3.connect(self._db, timeout=5, isolation_level="IMMEDIATE") as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("UPDATE protected_state SET generation=?, state_hash=? WHERE id=1", (generation, state_hash))
            conn.commit()

    def commit_with_verdict(
        self,
        attempt_id: str,
        generation: int,
        disposition: str,
        *,
        expected_state_hash: str,
        expected_evidence_token: str,
        recompute_token_fn: Any | None = None,
        verdict_payload: Mapping[str, Any] | None = None,
        next_state_hash: str | None = None,
    ) -> AdmissionCheckpoint:
        """Atomically bind terminal CAS to the just-validated evidence verdict."""
        if disposition not in ("VOID", "COMMITTED"):
            return AdmissionCheckpoint(attempt_id, generation, "VOID", False, True, ("invalid_terminal_state",))
        with sqlite3.connect(self._db, timeout=5, isolation_level="IMMEDIATE") as conn:
            conn.execute("BEGIN IMMEDIATE")
            protected = conn.execute("SELECT generation,state_hash FROM protected_state WHERE id=1").fetchone()
            current = conn.execute("SELECT generation, disposition FROM admissions WHERE attempt_id=?", (attempt_id,)).fetchone()
            if current is not None:
                conn.commit()
                return AdmissionCheckpoint(attempt_id, int(current[0]), str(current[1]), False, current[1] == "VOID", ("terminal_state",))
            if protected is None or int(protected[0]) != generation or str(protected[1]) != expected_state_hash:
                conn.execute("INSERT INTO admissions(attempt_id,generation,disposition) VALUES(?,?,?)", (attempt_id, generation, "VOID"))
                conn.commit()
                return AdmissionCheckpoint(attempt_id, generation, "VOID", False, True, ("protected_state_identity_missing_or_drifted",))
            if recompute_token_fn is not None:
                recomputed = str(recompute_token_fn())
            elif verdict_payload is not None:
                recomputed = digest(verdict_payload)
            else:
                recomputed = ""
            if not expected_evidence_token or not hmac.compare_digest(recomputed, expected_evidence_token):
                conn.execute("INSERT INTO admissions(attempt_id,generation,disposition) VALUES(?,?,?)", (attempt_id, generation, "VOID"))
                conn.commit()
                return AdmissionCheckpoint(attempt_id, generation, "VOID", False, True, ("evidence_token_mismatch",))
            conn.execute("INSERT INTO admissions(attempt_id,generation,disposition) VALUES(?,?,?)", (attempt_id, generation, disposition))
            if disposition == "COMMITTED":
                conn.execute("UPDATE protected_state SET generation=?, state_hash=? WHERE id=1", (generation + 1, next_state_hash or str(generation + 1)))
            conn.commit()
        return AdmissionCheckpoint(attempt_id, generation, disposition, disposition == "COMMITTED", disposition == "VOID", ())

    def compare_and_set(self, attempt_id: str, generation: int, disposition: str, *, expected_state_hash: str | None = None, next_state_hash: str | None = None) -> AdmissionCheckpoint:
        if disposition not in ("VOID", "COMMITTED"):
            return AdmissionCheckpoint(attempt_id, generation, "VOID", False, True, ("invalid_terminal_state",))
        with sqlite3.connect(self._db, timeout=5, isolation_level="IMMEDIATE") as conn:
            conn.execute("BEGIN IMMEDIATE")
            protected = conn.execute("SELECT generation,state_hash FROM protected_state WHERE id=1").fetchone()
            if expected_state_hash is None or protected is None or protected[1] != expected_state_hash or int(protected[0]) != generation:
                current = conn.execute("SELECT generation, disposition FROM admissions WHERE attempt_id=?", (attempt_id,)).fetchone()
                if current is None:
                    conn.execute("INSERT INTO admissions(attempt_id,generation,disposition) VALUES(?,?,?)", (attempt_id, generation, "VOID"))
                conn.commit()
                return AdmissionCheckpoint(attempt_id, generation, "VOID", False, True, ("protected_state_identity_missing_or_drifted",))
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
    role_scope: str = "EXP-M-REVIEW"
    issuer_id: str = "platform-review-authority"
    authority_digest: str = "review-authority-v1"
    candidate_identity: str = "EXP-M"
    expires_at: str | None = "2099-01-01T00:00:00Z"
    generation: int = 1
    revoked: bool = False

    def __post_init__(self) -> None:
        if not self.record_hash:
            object.__setattr__(self, "record_hash", digest({"reviewer_id": self.reviewer_id, "policy_hash": self.policy_hash, "trusted": self.trusted, "authorization_source": self.authorization_source, "role_scope": self.role_scope, "issuer_id": self.issuer_id, "authority_digest": self.authority_digest, "candidate_identity": self.candidate_identity, "expires_at": self.expires_at, "generation": self.generation, "revoked": self.revoked}))
    

@dataclass(frozen=True)
class SemanticCoverageRecord:
    coverage_id: str
    context_id: str
    complete: bool
    source_hash: str = ""
    coverage_hash: str = ""
    context_hash: str = ""
    evidence_ids: tuple[str, ...] = ()
    algorithm_version: str = "coverage-v1"
    required_contract_hash: str = ""


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
    fixture_target_map: tuple[tuple[str, str], ...] = ()

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
        catalog_map = dict(self.fixture_target_map)
        if catalog_map and (set(catalog_map) != set(self.fixture_ids) or set(catalog_map.values()) != required):
            return False
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
    reviewed_tree: str = ""
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
    expected_prompt_authority_id: str = "platform-prompt-authority"
    expected_prompt_authority_digest: str = "prompt-authority-v1"
    expected_witness_authority_id: str = "platform-witness-authority"
    expected_witness_authority_digest: str = "witness-authority-v1"
    expected_reviewer_issuer_id: str = "platform-review-authority"
    expected_reviewer_authority_digest: str = "review-authority-v1"
    expected_reviewer_role_scope: str = "EXP-M-REVIEW"
    expected_authority_generation: int = 1
    expected_fence_authority_id: str = "platform-protected-resource"
    expected_fence_authority_hash: str = "protected-resource-v1"
    expected_fence_issuer_id: str = "platform-fence-observer"
    expected_fence_attestation: str = "fence-attestation-v1"
    expected_semantic_algorithm: str = "coverage-v1"
    expectation_manifest_hash: str = ""


@dataclass(frozen=True)
class EvidenceBundle:
    """Immutable evidence-bearing bundle consumed by the production verdict."""
    evidence: Mapping[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        return self.evidence.get(key, default)


def admissibility_registry() -> AdmissibilityPredicateRegistry:
    # Production consumes the platform registry; mutation/fixture catalogs are
    # independently maintained and imported only as data, never generated from
    # this dispatch map.
    from exp_m_review_fixtures import FIXTURE_CATALOG
    return AdmissibilityPredicateRegistry("3", required_predicate_ids(), mutation_target_ids(), tuple(item["fixture_id"] for item in FIXTURE_CATALOG), tuple((item["fixture_id"], item["target_predicate_id"]) for item in FIXTURE_CATALOG))


def _predicate_validators(context: PredicateContext, authority: Any | None = None) -> dict[str, Any]:
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
            expected_authority_id=context.expected_prompt_authority_id,
            expected_authority_digest=context.expected_prompt_authority_digest,
            expected_generation=context.expected_authority_generation,
        )[0]

    def capability_valid(state: Mapping[str, Any]) -> bool:
        profile, plan, record = state.get("capability_profile"), state.get("qualification_plan"), state.get("capability_record")
        if not isinstance(profile, ProviderCapabilityProfile) or not isinstance(plan, ProviderQualificationExecutionPlan) or not isinstance(record, ProviderCapabilityQualificationRecord):
            return False
        return validate_capability(profile, plan, record, now=str(state.get("now", "2099-01-01T00:00:00Z")), expected_provider=context.expected_provider, expected_model=context.expected_model, expected_operating_point=context.expected_operating_point, expected_profile_hash=context.expected_profile_hash, required_format="text", required_context_bytes=context.max_context_bytes, authority=authority)[0]

    def context_isolation_valid(state: Mapping[str, Any]) -> bool:
        record = state.get("context_isolation_verdict")
        if not isinstance(record, ContextIsolationVerdict):
            return False
        return record.policy is not None and record.policy.policy_id and record.policy.basis in ("COMPLETE_READABLE_FENCED_STATE", "DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY") and record.transition_class == context.expected_transition_class

    def accessibility_policy_valid(state: Mapping[str, Any]) -> bool:
        policy = state.get("accessibility_policy_record")
        if not isinstance(policy, ProviderAccessibilityRiskPolicy):
            return False
        if policy.transition_class != context.expected_transition_class or policy.residual_risk_allowed or policy.proof_mode not in ("inline", "inline-deterministic"):
            return False
        return bool(policy.proof_mode and policy.deterministic_required)

    def semantic_context_valid(state: Mapping[str, Any]) -> bool:
        record = state.get("semantic_context")
        if not isinstance(record, SemanticContextQualificationRecord):
            return False
        if record.context_id != context.final_context_id or record.context_hash != context.final_context_hash or record.source_hash != context.reviewed_commit:
            return False
        if record.context_bytes and digest(record.context_bytes) != record.context_hash:
            return False
        expected_receipt = digest({"context_id": record.context_id, "source_hash": record.source_hash, "members": tuple(record.assembly_member_ids), "assembly": "trusted-final-context-v1"})
        return bool(record.context_bytes or record.qualification_receipt_hash == expected_receipt)

    def wire_valid(state: Mapping[str, Any]) -> bool:
        manifest, materialized, wire, receipt, returned = state.get("manifest"), state.get("materialization"), state.get("wire"), state.get("receipt"), state.get("returned_items")
        if not isinstance(manifest, EvidenceDeliveryManifest) or not isinstance(materialized, MaterializationResult) or not isinstance(wire, WireDeliveryRecord) or not isinstance(receipt, ReviewerReceipt) or not isinstance(returned, Mapping) or any(not isinstance(v, bytes) for v in returned.values()):
            return False
        return validate_wire_delivery(manifest, materialized, wire, receipt, returned, expected_commit=context.reviewed_commit, expected_semantic_hash=context.expected_semantic_hash or None, authority=authority)[0]

    def delivery_valid(state: Mapping[str, Any]) -> bool:
        if isinstance(state.get("delivery"), DeliveryCompletenessResult) and not state["delivery"].complete:
            return False
        manifest, materialized, wire, receipt, returned = state.get("manifest"), state.get("materialization"), state.get("wire"), state.get("receipt"), state.get("returned_items")
        if not isinstance(manifest, EvidenceDeliveryManifest) or not isinstance(materialized, MaterializationResult) or not isinstance(wire, WireDeliveryRecord) or not isinstance(receipt, ReviewerReceipt) or not isinstance(returned, Mapping) or any(not isinstance(v, bytes) for v in returned.values()):
            return False
        # receipt.complete is only a consistency assertion; byte/wire/commit/semantic
        # completeness is recomputed by the authoritative delivery validator.
        return receipt.complete and validate_wire_delivery(
            manifest, materialized, wire, receipt, returned,
            expected_commit=context.reviewed_commit,
            expected_semantic_hash=context.expected_semantic_hash or None,
            authority=authority,
        )[0]

    def disposition_valid(state: Mapping[str, Any]) -> bool:
        results = state.get("__governor_predicate_results__")
        if not isinstance(results, Mapping) or not results:
            return False
        derived = "PASS" if all(bool(v) for v in results.values()) else "CHANGES_REQUIRED"
        caller = state.get("disposition")
        if caller is not None and caller != derived:
            return False
        return derived in context.promotable_dispositions

    def accessibility_proof_valid(state: Mapping[str, Any]) -> bool:
        proof, challenge = state.get("accessibility"), state.get("witness_challenge")
        if not isinstance(proof, AccessibilityProofRecord) or not isinstance(challenge, WitnessChallengeEvidence):
            return False
        if proof.final_context_id != context.final_context_id or proof.challenge_id != challenge.challenge_id:
            return False
        expected_proof = digest({"challenge": challenge, "context_id": context.final_context_id, "provider": context.expected_provider, "policy": context.expected_transition_class})
        return proof.evidence_hash == digest(challenge) and proof.proof_hash == expected_proof and proof.provider_id == context.expected_provider and proof.proof_mode == "inline-deterministic"

    def witness_valid(state: Mapping[str, Any]) -> bool:
        record, challenge = state.get("witness"), state.get("witness_challenge")
        if not isinstance(record, WitnessProtocolQualificationRecord) or not isinstance(challenge, WitnessChallengeEvidence):
            return False
        if context.expected_witness_answer_hash and challenge.expected_answer_hash != context.expected_witness_answer_hash:
            return False
        return validate_witness_qualification(record, provider_id=context.witness_provider, mode=context.witness_mode, prompt_mode=context.witness_prompt_mode, now=str(state.get("now", "2025-01-01T00:00:00Z")), response=str(state.get("witness_response", "")), challenge=str(state.get("witness_challenge_text", "")), final_context_bytes=challenge.final_context_bytes_before, max_final_context_bytes=context.max_context_bytes, expected_answer_hash=context.expected_witness_answer_hash, challenge_record=challenge, expected_authority_id=context.expected_witness_authority_id, expected_authority_digest=context.expected_witness_authority_digest, expected_generation=context.expected_authority_generation)[0] and challenge.final_context_bytes_after == challenge.final_context_bytes_before + challenge.response_length

    def semantic_coverage_valid(state: Mapping[str, Any]) -> bool:
        coverage = state.get("semantic_coverage")
        contract = state.get("evidence_contract")
        interactions = state.get("interaction_contract")
        required_hash = digest({"required": getattr(contract, "required_ids", ()), "optional": getattr(contract, "optional_ids", ()), "interactions": getattr(interactions, "interactions", ())})
        coverage_hash = digest({"algorithm": "coverage-v1", "required": getattr(contract, "required_ids", ()), "interactions": getattr(interactions, "interactions", ()), "evidence_ids": tuple(sorted(getattr(state.get("manifest"), "items", {}))), "source_hash": context.reviewed_commit, "context_hash": context.final_context_hash})
        return isinstance(coverage, SemanticCoverageRecord) and coverage.context_id == context.final_context_id and coverage.context_hash == context.final_context_hash and coverage.source_hash == context.reviewed_commit and coverage.algorithm_version == "coverage-v1" and coverage.required_contract_hash == required_hash and coverage.coverage_hash == coverage_hash and bool(coverage.evidence_ids)

    def reviewer_valid(state: Mapping[str, Any]) -> bool:
        reviewer = state.get("reviewer")
        return (isinstance(reviewer, ReviewerProvenanceRecord) and reviewer.policy_hash == context.expected_reviewer_policy_hash
                and bool(reviewer.authorization_source) and reviewer.authorization_source != "caller"
                and reviewer.trusted and reviewer.issuer_id == context.expected_reviewer_issuer_id
                and reviewer.authority_digest == context.expected_reviewer_authority_digest
                and reviewer.role_scope == context.expected_reviewer_role_scope
                and reviewer.candidate_identity == "EXP-M" and not reviewer.revoked
                and reviewer.generation == context.expected_authority_generation
                and reviewer.record_hash == digest({"reviewer_id": reviewer.reviewer_id, "policy_hash": reviewer.policy_hash, "trusted": reviewer.trusted, "authorization_source": reviewer.authorization_source, "role_scope": reviewer.role_scope, "issuer_id": reviewer.issuer_id, "authority_digest": reviewer.authority_digest, "candidate_identity": reviewer.candidate_identity, "expires_at": reviewer.expires_at, "generation": reviewer.generation, "revoked": reviewer.revoked}))

    return {
        "review_request_current": lambda s: isinstance(s.get("review_request"), Mapping) and s["review_request"].get("current") is True and s["review_request"].get("request_id") == context.request_id,
        "authority_snapshot_current": lambda s: isinstance(s.get("authority_snapshot"), GovernanceAuthoritySnapshot) and s["authority_snapshot"].outside_candidate_write_authority and s["authority_snapshot"].snapshot_id == context.authority_snapshot_id and s["authority_snapshot"].content_hash == context.authority_snapshot_hash and s["authority_snapshot"].version == context.authority_version,
        "evidence_contract_closed": lambda s: isinstance(s.get("evidence_contract"), RequiredEvidenceContract) and s["evidence_contract"].closed and s["evidence_contract"].non_vacuous,
        "interaction_contract_closed": lambda s: isinstance(s.get("interaction_contract"), RequiredInteractionContract) and s["interaction_contract"].closed and bool(s["interaction_contract"].interactions) and isinstance(s.get("final_context_interactions"), FinalContextInteractionEvidence) and s["final_context_interactions"].derived and s["final_context_interactions"].builder_identity == "trusted-final-context-builder" and s["final_context_interactions"].assembly_receipt_hash == digest({"context_id": context.final_context_id, "source_hash": context.reviewed_commit, "members": tuple(s["final_context_interactions"].member_ids), "assembly": "trusted-final-context-v1"}) and {tuple(x) for x in s["final_context_interactions"].interactions} == {tuple(x) for x in s["interaction_contract"].interactions},
        "materialization_complete": lambda s: isinstance(s.get("materialization"), MaterializationResult) and s["materialization"].success,
        "representation_governed": lambda s: isinstance(s.get("representation"), RepresentationRecord) and isinstance(s.get("manifest"), EvidenceDeliveryManifest) and isinstance(s.get("materialization"), MaterializationResult) and validate_representation(s["manifest"], s["materialization"].entries, s["representation"])[0],
        "egress_authorized": egress_valid,
        "capability_current": capability_valid,
        "accessibility_policy_satisfied": accessibility_policy_valid,
        "context_isolation_satisfied": context_isolation_valid,
        "hidden_state_policy_satisfied": lambda s: isinstance(s.get("context_isolation_verdict"), ContextIsolationVerdict) and s["context_isolation_verdict"].policy is not None and not s["context_isolation_verdict"].policy.hidden_state_allowed and s["context_isolation_verdict"].transition_class == context.expected_transition_class,
        "context_state_clean": lambda s: isinstance(s.get("context_isolation_verdict"), ContextIsolationVerdict) and s["context_isolation_verdict"].evidence is not None and validate_context_state(s["context_isolation_verdict"].evidence, required_channels=s["context_isolation_verdict"].required_channels, expected_observation_hash=context.expected_context_state_hash if len(context.expected_context_state_hash) == 64 else None)[0],
        "admission_fence_current": lambda s: isinstance(s.get("context_isolation_verdict"), ContextIsolationVerdict) and s["context_isolation_verdict"].fence is not None and validate_fence(s["context_isolation_verdict"].fence, context.expected_fence_version, expected_authority_id=context.expected_fence_authority_id, expected_authority_hash=context.expected_fence_authority_hash, expected_issuer_id=context.expected_fence_issuer_id, expected_attestation=context.expected_fence_attestation)[0] and (not context.expected_fence_state_hash or s["context_isolation_verdict"].fence.state_hash == context.expected_fence_state_hash),
        "semantic_context_qualified": semantic_context_valid,
        "wire_binding_valid": wire_valid,
        "delivery_complete": delivery_valid,
        "accessibility_proven": accessibility_proof_valid,
        "witness_record_current": witness_valid,
        "session_retrieval_coverage": lambda s: isinstance(s.get("retrieval"), RetrievalEvidenceRecord) and validate_retrieval(s["retrieval"], expected_request=context.request_id, expected_attempt=context.attempt_id, expected_session=context.session_id, expected_source=context.retrieval_source, expected_version=context.retrieval_version, expected_context_id=context.final_context_id, expected_context_hash=context.final_context_hash, authority=authority)[0],
        "prompt_isolation_current": prompt_valid,
        "semantic_coverage": semantic_coverage_valid,
        "reviewer_provenance": reviewer_valid,
        "disposition_promotable": disposition_valid,
    }


def evaluate_admissibility(bundle: EvidenceBundle, context: PredicateContext, registry: AdmissibilityPredicateRegistry | None = None, *, authority: Any | None = None) -> VerdictAdmissibilityResult:
    from exp_m_expectation_authority import authority_context_valid
    if not authority_context_valid(authority, context):
        return VerdictAdmissibilityResult(False, "INADMISSIBLE", {}, ("expectation_authority_invalid",))
    registry = registry or admissibility_registry()
    validators = _predicate_validators(context, authority)
    state = bundle.evidence
    predicates = {pid: bool(validators[pid](state)) for pid in registry.predicate_ids if pid != "disposition_promotable"}
    if "disposition_promotable" in registry.predicate_ids:
        disposition_state = dict(state)
        disposition_state["__governor_predicate_results__"] = dict(predicates)
        predicates["disposition_promotable"] = bool(validators["disposition_promotable"](disposition_state))
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
    observed_context: FinalContextInteractionEvidence | None = None,
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
    if observed_context is None or not observed_context.derived or observed_context.request_id != request_id or set(observed_context.member_ids) != set(items) or {tuple(x) for x in observed_context.interactions} != {tuple(x) for x in derived_interactions}:
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
        isolated, isolation_reasons = validate_context_isolation(context_policy, context_evidence, fence, transition_class=risk_policy.transition_class, expected_transition_class=expected_transition_class, expected_fence_version=expected_fence_version, required_channels=("memory", "config"))
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
        expected_transform_hash = digest({"transform_id": record.transform_id, "version": record.transform_version, "registry": QUALIFIED_TRANSFORMS.get(record.transform_id, "")})
        if record.transform_id not in QUALIFIED_TRANSFORMS or not record.transform_version or record.transform_hash != expected_transform_hash or record.registry_version != QUALIFIED_TRANSFORMS[record.transform_id]:
            reasons.append("representation_transform_unqualified")
        if record.source_hash != manifest.manifest_hash or record.representation_hash != digest({k: sha256(v).hexdigest() for k, v in sorted(items.items())}):
            reasons.append("representation_record_mismatch")
        if not record.parameters_hash or not record.coverage_hash or record.parameters_hash != digest({"parameters": "raw"}) or record.coverage_hash != digest({"coverage": "raw", "source": manifest.manifest_hash}):
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
    if state.observation_hash and state.observation_hash != digest({"channels": tuple(state.observable_channels), "state_hash": state.state_hash, "clean": state.clean, "sentinel_passed": state.sentinel_passed, "channel_observations": tuple(state.channel_observations), "observer_id": state.observer_id}):
        reasons.append("context_observation_hash_mismatch")
    if expected_observation_hash is not None and state.observation_hash != expected_observation_hash:
        reasons.append("context_expected_observation_mismatch")
    if not state.observation_hash:
        reasons.append("provider_context_observation_unbound")
    observations = {str(row.get("channel")): row for row in state.channel_observations if isinstance(row, Mapping)}
    if not observations:
        reasons.append("context_channel_observations_missing")
    for channel in required_channels:
        row = observations.get(str(channel))
        if row is None:
            reasons.append(f"context_structured_channel_missing:{channel}")
            continue
        if row.get("observer_id") != state.observer_id or not row.get("generation"):
            reasons.append(f"context_structured_observer_invalid:{channel}")
        if row.get("readable") is not True and row.get("fenced") is not True:
            reasons.append(f"context_channel_not_readable_or_fenced:{channel}")
        if row.get("observed_hash") != row.get("expected_hash") and row.get("fenced") is not True:
            reasons.append(f"context_channel_value_mismatch:{channel}")
    return not reasons, tuple(reasons)


def validate_fence(fence: AdmissionFenceRecord, expected_version: str, *, expected_authority_id: str = "platform-protected-resource", expected_authority_hash: str = "protected-resource-v1", expected_issuer_id: str = "platform-fence-observer", expected_attestation: str = "fence-attestation-v1") -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if fence.version != expected_version:
        reasons.append("admission_fence_version_mismatch")
    if not fence.fence_id or (fence.state_hash and not isinstance(fence.state_hash, str)):
        reasons.append("admission_fence_unbound")
    if fence.authority_snapshot_id != expected_authority_id or fence.authority_snapshot_hash != expected_authority_hash or fence.issuer_id != expected_issuer_id or fence.attestation_hash != expected_attestation:
        reasons.append("admission_fence_external_authority_mismatch")
    if not fence.current:
        reasons.append("admission_fence_not_current")
    if fence.state_hash != digest({"fence_id": fence.fence_id, "version": fence.version, "current": True}):
        reasons.append("admission_fence_state_mismatch")
        reasons.append("admission_fence_stale")
    return not reasons, tuple(reasons)


def validate_egress(egress: Mapping[str, Any], expected_version: str) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if egress.get("authorized") is not True or egress.get("version") != expected_version:
        reasons.append("egress_revoked_or_drifted")
    return not reasons, tuple(reasons)


def validate_prompt_isolation(record: PromptIsolationQualificationRecord, *, provider_id: str, mode: str, now: str, expected_authority_id: str | None = None, expected_authority_digest: str | None = None, expected_generation: int | None = None) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if record.provider_id != provider_id or record.mode != mode or not record.record_id:
        reasons.append("prompt_isolation_binding")
    if record.record_hash != digest({"record_id": record.record_id, "provider_id": record.provider_id, "mode": record.mode, "current": True, "expires_at": record.expires_at, "authority_id": record.authority_id, "authority_digest": record.authority_digest, "record_version": record.record_version, "generation": record.generation, "revoked": record.revoked}):
        reasons.append("prompt_isolation_record_not_currently_bound")
    if not record.current or record.revoked or record.generation < 1 or not record.authority_id or not record.authority_digest:
        reasons.append("prompt_isolation_authority_provenance")
    if expected_authority_id is not None and record.authority_id != expected_authority_id:
        reasons.append("prompt_isolation_authority_mismatch")
    if expected_authority_digest is not None and record.authority_digest != expected_authority_digest:
        reasons.append("prompt_isolation_authority_digest_mismatch")
    if expected_generation is not None and record.generation != expected_generation:
        reasons.append("prompt_isolation_generation_mismatch")
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
    def walk_archive(blob: bytes, prefix: str, depth: int) -> None:
        nonlocal total
        if depth > max_recursion_depth:
            reasons.append(f"archive_recursion:{prefix}")
            return
        try:
            with zipfile.ZipFile(__import__("io").BytesIO(blob)) as archive:
                for member in archive.infolist():
                    raw_member = member.filename
                    nested = posixpath.normpath(posixpath.join(prefix, raw_member))
                    if not safe_archive_member(raw_member) or not safe_archive_member(nested):
                        reasons.append(f"nested_archive_escape:{raw_member}")
                        continue
                    compressed_size = int(member.compress_size or 0)
                    declared_size = int(member.file_size or 0)
                    if declared_size > max_member_bytes:
                        reasons.append(f"member_size_limit:{nested}")
                        continue
                    if compressed_size == 0 and declared_size > 0 or compressed_size > 0 and declared_size / compressed_size > max_ratio:
                        reasons.append(f"member_ratio_limit:{nested}")
                        continue
                    nested_data = archive.read(member)
                    if len(nested_data) > max_member_bytes:
                        reasons.append(f"member_size_limit:{nested}")
                        continue
                    mode = (member.external_attr >> 16) & 0o170000
                    if mode == 0o120000:
                        try:
                            target = nested_data.decode("utf-8")
                            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(nested), target))
                            if not safe_archive_member(target) or not safe_archive_member(resolved):
                                reasons.append(f"nested_symlink_escape:{nested}")
                        except UnicodeDecodeError:
                            reasons.append(f"symlink_target_invalid:{nested}")
                        continue
                    if nested in seen:
                        reasons.append(f"duplicate_normalized_member:{nested}")
                        continue
                    seen.add(nested)
                    total += len(nested_data)
                    if zipfile.is_zipfile(__import__("io").BytesIO(nested_data)):
                        walk_archive(nested_data, nested, depth + 1)
                    else:
                        clean[nested] = nested_data
                    if total > max_total_bytes:
                        reasons.append("materialization_size_limit")
        except (zipfile.BadZipFile, OSError):
            reasons.append(f"archive_parse_failed:{prefix}")
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
        is_archive_bytes = zipfile.is_zipfile(__import__("io").BytesIO(value)) if isinstance(value, bytes) else False
        if entry.kind == "archive" or is_archive_bytes:
            walk_archive(value, posixpath.dirname(name), entry.recursion_depth + 1)
            continue
        if len(value) > max_member_bytes:
            reasons.append(f"member_size_limit:{name}")
        total += len(value)
        clean[name] = value
    if total > max_total_bytes:
        reasons.append("materialization_size_limit")
    representation_hash = digest({k: sha256(v).hexdigest() for k, v in sorted(clean.items())})
    return MaterializationResult(not reasons, clean, representation_hash, source_hash, transform_id, tuple(reasons))


def validate_capability(profile: ProviderCapabilityProfile, plan: ProviderQualificationExecutionPlan, record: ProviderCapabilityQualificationRecord, *, now: str, expected_provider: str, expected_model: str, expected_operating_point: str, expected_profile_hash: str, required_format: str, required_context_bytes: int, authority: Any | None = None) -> tuple[bool, tuple[str, ...]]:
    """Compute capability currentness from bound records and frozen authority."""
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

    # For non-production deterministic profiles, the plan and record are
    # compared to an authority-owned qualification ledger when an authority is
    # supplied by the production admission path.
    if authority is not None and plan.qualification_profile != "R5_PRODUCTION":
        try:
            entry = authority.qualification_entry(plan.plan_id)
        except ValueError as exc:
            reasons.append(str(exc))
        else:
            expected_plan = entry.get("plan") or {}
            expected_record = entry.get("record") or {}
            plan_checks = {
                "plan_id": plan.plan_id,
                "provider_id": plan.provider_id,
                "operating_point": plan.operating_point,
                "trial_ids": list(plan.trial_ids),
                "confirmation_ids": list(plan.confirmation_ids),
                "qualification_profile": plan.qualification_profile,
                "schedule_seed": plan.schedule_seed,
                "scheduled_days": list(plan.scheduled_days),
                "scheduled_time_blocks": list(plan.scheduled_time_blocks),
                "production_envelope_hash": plan.production_envelope_hash,
            }
            if any(expected_plan.get(k) != v for k, v in plan_checks.items()):
                reasons.append("qualification_authority_plan_mismatch")
            record_checks = {
                "plan_id": record.plan_id,
                "profile_hash": record.profile_hash,
                "statistical_qualified": record.statistical_qualified,
                "all_trials_closed": record.all_trials_closed,
                "hard_failures": record.hard_failures,
                "operating_point": record.operating_point,
                "planned_attempt_ids": list(record.planned_attempt_ids),
                "closed_attempt_ids": list(record.closed_attempt_ids),
                "provider_id": record.provider_id,
                "model_id": record.model_id,
                "protocol_version": record.protocol_version,
                "independence_status": record.independence_status,
            }
            if any(expected_record.get(k) != v for k, v in record_checks.items()):
                reasons.append("qualification_authority_record_mismatch")
            expected_attempts = expected_record.get("attempt_records") or []
            actual_attempts = [
                {
                    "attempt_id": a.attempt_id,
                    "planned_root_id": a.planned_root_id,
                    "parent_attempt_id": a.parent_attempt_id,
                    "kind": a.kind,
                    "request_id": a.request_id,
                    "session_id": a.session_id,
                    "wire_hash": a.wire_hash,
                    "outcome": a.outcome,
                    "provider_request_id": a.provider_request_id,
                    "request_hash": a.request_hash,
                    "utc_day": a.utc_day,
                    "time_block": a.time_block,
                } for a in record.attempt_records
            ]
            if expected_attempts != actual_attempts:
                reasons.append("qualification_authority_attempt_mismatch")

    attempts = list(record.attempt_records)
    physical_failures = sum(1 for a in attempts if getattr(a, "kind", "FIRST") == "FIRST" and getattr(a, "outcome", "") not in ("OK", "SUCCESS", "PASS"))
    if record.hard_failures != physical_failures:
        reasons.append("hard_failure_count_not_derived")
    if physical_failures != 0:
        reasons.append("qualification_not_statistically_valid")

    if plan.qualification_profile == "R5_PRODUCTION":
        protocol = None
        if authority is None:
            reasons.append("r5_protocol_unavailable")
        else:
            try:
                protocol = authority.load_r5_protocol()
            except ValueError:
                reasons.append("r5_protocol_unavailable")
        if protocol is not None:
            confirmation_min = int(protocol.get("n_min", 0))
            if len(plan.confirmation_ids) < confirmation_min or len(plan.trial_ids) == 0:
                reasons.append("production_confirmation_plan_too_small")
            if not attempts:
                reasons.append("production_attempts_missing")
            expected_population_order = tuple(plan.trial_ids) + tuple(plan.confirmation_ids)
            expected_population = set(expected_population_order)
            first_attempts = [a for a in attempts if getattr(a, "kind", "FIRST") == "FIRST"]
            if len(attempts) != len(expected_population) or {getattr(a, "planned_root_id", "") for a in first_attempts} != expected_population:
                reasons.append("production_population_mismatch")
            if any(getattr(a, "kind", "FIRST") != "FIRST" for a in attempts):
                reasons.append("production_hidden_retry_or_replacement")
            successes = len(attempts) - physical_failures
            n = len(attempts)
            if n:
                confidence = float(protocol.get("confidence_level", 0.0))
                threshold = float(protocol.get("lower_bound_threshold", 1.0))
                if physical_failures or successes != n or protocol.get("success_requirement") != "ZERO_FIRST_ATTEMPT_FAILURES":
                    reasons.append("production_statistical_lower_bound_below_threshold")
                else:
                    alpha = 1.0 - confidence
                    if not (0.0 < alpha < 1.0):
                        reasons.append("production_statistical_protocol_invalid")
                    else:
                        lower = math.pow(alpha, 1.0 / n)
                        if lower < threshold:
                            reasons.append("production_statistical_lower_bound_below_threshold")
            if record.protocol_version != str(protocol.get("protocol_id", "")):
                reasons.append("production_protocol_version_mismatch")
            sched = protocol.get("schedule_requirements") or {}
            days = tuple(plan.scheduled_days)
            blocks = tuple(plan.scheduled_time_blocks)
            if len(set(days)) < int(sched.get("min_distinct_days", 0)) or len(set(blocks)) < int(sched.get("min_distinct_time_blocks", 0)):
                reasons.append("production_schedule_diversity_insufficient")
            if bool(sched.get("require_exact_plan_coverage")) and attempts:
                used_days = {getattr(a, "utc_day", "") for a in first_attempts}
                used_blocks = {getattr(a, "time_block", "") for a in first_attempts}
                if used_days != set(days) or used_blocks != set(blocks):
                    reasons.append("production_schedule_attempt_coverage_mismatch")
            if sched.get("assignment_rule") == "ROUND_ROBIN_DECLARED_ORDER" and days and blocks and attempts:
                by_root = {getattr(a, "planned_root_id", ""): a for a in first_attempts}
                for index, root_id in enumerate(expected_population_order):
                    a = by_root.get(root_id)
                    if a is None:
                        continue
                    if a.utc_day != days[index % len(days)] or a.time_block != blocks[index % len(blocks)]:
                        reasons.append("production_schedule_distribution_mismatch")
                        break
            if protocol.get("retry_policy") == "NO_RETRY_OR_REPLACEMENT" and any(getattr(a, "kind", "FIRST") != "FIRST" for a in attempts):
                reasons.append("production_retry_policy_violation")
        if getattr(record, "independence_status", "STATISTICAL_INDEPENDENCE_UNPROVEN") != "STATISTICAL_INDEPENDENCE_UNPROVEN":
            reasons.append("production_independence_status_unexpected")

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
    return not reasons, tuple(dict.fromkeys(reasons))

def validate_context_isolation(policy: ProviderContextIsolationPolicy, evidence: ProviderContextStateEvidence, fence: AdmissionFenceRecord, *, transition_class: str, required_channels: Sequence[str], expected_transition_class: str | None = None, expected_fence_version: str | None = None, expected_observation_hash: str | None = None, expected_fence_state_hash: str | None = None, expected_fence_authority_id: str = "platform-protected-resource", expected_fence_authority_hash: str = "protected-resource-v1", expected_fence_issuer_id: str = "platform-fence-observer", expected_fence_attestation: str = "fence-attestation-v1") -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not policy.policy_id or policy.basis not in ("COMPLETE_READABLE_FENCED_STATE", "DEDICATED_PLATFORM_ACCOUNT_STATELESS_BOUNDARY"):
        reasons.append("context_policy_invalid")
    if expected_transition_class is None or expected_fence_version is None:
        reasons.append("external_context_expectations_missing")
    elif transition_class != expected_transition_class:
        reasons.append("context_transition_class_mismatch")
    if transition_class == "HIGHEST" and policy.hidden_state_allowed:
        reasons.append("hidden_state_residual_disallowed")
    clean, clean_reasons = validate_context_state(evidence, required_channels=required_channels, expected_observation_hash=expected_observation_hash)
    if not clean:
        reasons.extend(clean_reasons)
    fence_ok, fence_reasons = validate_fence(fence, expected_fence_version or "", expected_authority_id=expected_fence_authority_id, expected_authority_hash=expected_fence_authority_hash, expected_issuer_id=expected_fence_issuer_id, expected_attestation=expected_fence_attestation)
    if not fence_ok:
        reasons.extend(fence_reasons)
    if expected_fence_state_hash and fence.state_hash != expected_fence_state_hash:
        reasons.append("admission_fence_expected_state_mismatch")
    return not reasons, tuple(reasons)


def validate_retrieval(record: RetrievalEvidenceRecord, *, expected_request: str, expected_attempt: str, expected_session: str, expected_source: str, expected_version: str, expected_context_id: str, expected_context_hash: str, authority: Any | None = None) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if record.request_id != expected_request or record.attempt_id != expected_attempt or record.session_id != expected_session:
        reasons.append("retrieval_identity_mismatch")
    if record.source_id != expected_source or record.source_version != expected_version:
        reasons.append("retrieval_source_mismatch")
    raw = b""
    if authority is None:
        reasons.append("retrieval_authority_missing")
    else:
        try:
            raw = authority.resolve_retrieval_bytes(record.source_id, record.source_version, record.start, record.end)
        except ValueError as exc:
            reasons.append(str(exc))
    if raw:
        if record.end - record.start != len(raw) or record.returned_length != len(raw) or record.returned_sha256 != sha256(raw).hexdigest():
            reasons.append("retrieval_bytes_mismatch")
    elif record.end != record.start:
        reasons.append("retrieval_bytes_mismatch")
    if not record.tool_result_id:
        reasons.append("retrieval_tool_result_missing")
    if record.final_context_id != expected_context_id or record.final_context_hash != expected_context_hash:
        reasons.append("retrieval_final_context_unbound")
    return not reasons, tuple(dict.fromkeys(reasons))

def validate_witness_qualification(record: WitnessProtocolQualificationRecord, *, provider_id: str, mode: str, prompt_mode: str, now: str, response: str, challenge: str, final_context_bytes: int, max_final_context_bytes: int, expected_answer_hash: str | None = None, challenge_record: WitnessChallengeEvidence | None = None, expected_authority_id: str | None = None, expected_authority_digest: str | None = None, expected_generation: int | None = None) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if record.provider_id != provider_id or record.mode != mode or record.prompt_isolation_mode != prompt_mode or not record.record_id:
        reasons.append("witness_record_binding")
    if record.record_hash != digest({"record_id": record.record_id, "provider_id": record.provider_id, "mode": record.mode, "max_response_bytes": record.max_response_bytes, "current": True, "prompt_isolation_mode": record.prompt_isolation_mode, "expires_at": record.expires_at, "authority_id": record.authority_id, "authority_digest": record.authority_digest, "record_version": record.record_version, "generation": record.generation, "revoked": record.revoked}):
        reasons.append("witness_record_not_currently_bound")
    if not record.current or record.revoked or record.generation < 1 or not record.authority_id or not record.authority_digest:
        reasons.append("witness_authority_provenance")
    if expected_authority_id is not None and record.authority_id != expected_authority_id:
        reasons.append("witness_authority_mismatch")
    if expected_authority_digest is not None and record.authority_digest != expected_authority_digest:
        reasons.append("witness_authority_digest_mismatch")
    if expected_generation is not None and record.generation != expected_generation:
        reasons.append("witness_generation_mismatch")
    if record.expires_at is not None and record.expires_at <= now:
        reasons.append("witness_record_expired")
    if not challenge or not response or len(response.encode()) > record.max_response_bytes:
        reasons.append("witness_response_invalid")
    if expected_answer_hash is not None and digest(response) != expected_answer_hash:
        reasons.append("witness_answer_mismatch")
    if challenge_record is not None:
        if challenge_record.expected_answer_hash != expected_answer_hash or challenge_record.response_hash != digest(response):
            reasons.append("witness_challenge_response_binding")
        if challenge_record.semantics_class != "EXTRACTION_ACCESSIBILITY":
            reasons.append("witness_semantic_output")
    if final_context_bytes + len(response.encode()) > max_final_context_bytes:
        reasons.append("witness_context_eviction")
    if any(word in challenge.lower() for word in ("summarize", "judge", "evaluate", "defect")):
        reasons.append("witness_semantic_prompt")
    return not reasons, tuple(reasons)


def validate_wire_delivery(manifest: EvidenceDeliveryManifest, materialized: MaterializationResult, wire: WireDeliveryRecord, receipt: ReviewerReceipt, returned_items: Mapping[str, bytes], *, expected_commit: str, expected_semantic_hash: str | None = None, authority: Any | None = None) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    completion = complete_delivery(manifest, receipt, wire)
    if not completion.complete:
        reasons.extend(completion.reasons)
    raw_ok, raw_reasons = manifest.verify(returned_items)
    if not raw_ok:
        reasons.extend(raw_reasons)
    if authority is None:
        reasons.append("delivery_authority_missing")
    else:
        try:
            authority_commit = authority.resolve_reviewed_commit()
            if manifest.reviewed_commit != authority_commit or expected_commit != authority_commit:
                reasons.append("authority_reviewed_commit_mismatch")
            expected_delivery = authority.expected_delivery(manifest.request_id)
            if str(expected_delivery.get("reviewed_commit", "")) != authority_commit:
                reasons.append("authority_delivery_commit_mismatch")
            if str(expected_delivery.get("manifest_hash", "")) != manifest.manifest_hash:
                reasons.append("authority_manifest_hash_mismatch")
        except ValueError as exc:
            reasons.append(str(exc))
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
    return not reasons, tuple(dict.fromkeys(reasons))

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
    return AdmissionCheckpoint(attempt_id, expected.generation, "VOID", False, True, ("persistent_ledger_required",))


def admit_review_attempt_with_evidence(bundle: EvidenceBundle, context: PredicateContext, current: Mapping[str, Any], expected: AttemptState, *, attempt_id: str, expected_generation: int, registry: AdmissibilityPredicateRegistry | None = None, ledger: PersistentAdmissionLedger | None = None, authority: Any | None = None) -> AdmissionCheckpoint:
    """Final admission path: revalidate evidence then bind that verdict inside CAS."""
    if ledger is None:
        return AdmissionCheckpoint(attempt_id, expected.generation, "VOID", False, True, ("persistent_ledger_required",))
    verdict = evaluate_admissibility(bundle, context, registry, authority=authority)
    if not verdict.admissible:
        checkpoint = ledger.compare_and_set(attempt_id, expected.generation, "VOID", expected_state_hash=current.get("state_hash"))
        return AdmissionCheckpoint(attempt_id, expected.generation, "VOID", False, True, tuple(verdict.reasons) + tuple(checkpoint.reasons))
    token_payload = {
        "evidence": bundle.evidence,
        "context": context,
        "predicates": verdict.predicate_results,
        "generation": current.get("generation"),
        "state_hash": current.get("state_hash"),
    }
    expected_evidence_token = digest(token_payload)
    def recompute_token() -> str:
        return digest({
            "evidence": bundle.evidence,
            "context": context,
            "predicates": verdict.predicate_results,
            "generation": current.get("generation"),
            "state_hash": current.get("state_hash"),
        })
    return ledger.commit_with_verdict(
        attempt_id,
        expected_generation,
        "COMMITTED",
        expected_state_hash=str(current.get("state_hash", "")),
        expected_evidence_token=expected_evidence_token,
        recompute_token_fn=recompute_token,
        next_state_hash=str(current.get("next_state_hash", expected_generation + 1)),
    )

