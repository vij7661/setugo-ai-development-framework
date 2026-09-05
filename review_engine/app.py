from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from .claim_coverage import ClaimCoverageValidator
from .claim_coverage_guard import ClaimCoverageGuardedInvoker
from .configuration import ReviewEngineConfiguration, build_provider_registry, build_qualification_registry
from .evidence_correspondence import EvidenceCorrespondenceValidator
from .judge_health import JudgeHealthMonitor, JudgeObservation
from .orchestrator import ReviewEngine
from .request_boundary import PlatformExecutionEnvelope, build_request
from .session_store import SQLiteSessionStore
from .sqlite_memory import SQLiteMemoryStore
from .truth_contract import TVC_VERSION


class ReviewEngineApp:
    """Application service used by CLI, HTTP API and future UI."""

    def __init__(
        self,
        configuration: ReviewEngineConfiguration,
        *,
        memory_db: str,
        sessions_db: str,
        provider_registry=None,
        execution_envelope: PlatformExecutionEnvelope | None = None,
        evidence_validator: EvidenceCorrespondenceValidator | None = None,
        claim_coverage_validator: ClaimCoverageValidator | None = None,
    ) -> None:
        self.configuration = configuration
        self.providers = provider_registry or build_provider_registry(configuration)
        self.qualifications = build_qualification_registry(configuration)
        self.memory = SQLiteMemoryStore(memory_db)
        self.sessions = SQLiteSessionStore(sessions_db)
        # v0.1 is a review-only service. A future authenticated platform/tool
        # integration must inject its own trusted envelope here rather than
        # accepting governance-critical execution facts from request JSON.
        self.execution_envelope = execution_envelope or PlatformExecutionEnvelope()
        # Evidence correspondence and claim coverage are platform-owned. They are
        # constructor-injected and intentionally have no public HTTP write surface.
        self.evidence_validator = evidence_validator
        self.claim_coverage_validator = claim_coverage_validator

        # GOVERNED assurance must not treat a free verifier_id/qualification
        # label as evidence-verification authority, forget retained attestations,
        # or accept an evidence hash that has no exact platform-retained snapshot.
        if self.qualifications is not None and self.evidence_validator is not None:
            if not bool(getattr(self.evidence_validator, "qualified_verifier_assessment_enforced", False)):
                raise ValueError(
                    "GOVERNED assurance requires evidence correspondence with qualified verifier assessment"
                )
            if not bool(getattr(self.evidence_validator, "durable_attestation_state_enforced", False)):
                raise ValueError(
                    "GOVERNED assurance requires durable evidence correspondence attestation state"
                )
            if not bool(getattr(self.evidence_validator, "retained_snapshot_binding_enforced", False)):
                raise ValueError(
                    "GOVERNED assurance requires evidence correspondence bound to retained evidence snapshots"
                )
            if not bool(getattr(self.evidence_validator, "durable_snapshot_state_enforced", False)):
                raise ValueError(
                    "GOVERNED assurance requires durable retained evidence snapshot state"
                )

        # A governed reviewer configuration must not gain a stronger-looking
        # assurance label while using coverage evidence that bypasses extractor
        # qualification, accepts risk/task scope as free admission arguments,
        # forgets replay/inventory state after restart, or consumes work before
        # the corresponding inventory is durably retained.
        if self.qualifications is not None and self.claim_coverage_validator is not None:
            if not bool(getattr(self.claim_coverage_validator, "qualified_admission_enforced", False)):
                raise ValueError(
                    "GOVERNED assurance requires claim coverage with qualified extractor admission"
                )
            if not bool(getattr(self.claim_coverage_validator, "trusted_scope_binding_enforced", False)):
                raise ValueError(
                    "GOVERNED assurance requires claim coverage bound to platform-issued extraction scope"
                )
            if not bool(getattr(self.claim_coverage_validator, "durable_work_state_enforced", False)):
                raise ValueError(
                    "GOVERNED assurance requires durable extraction work replay protection"
                )
            if not bool(getattr(self.claim_coverage_validator, "durable_inventory_state_enforced", False)):
                raise ValueError(
                    "GOVERNED assurance requires durable retained claim coverage inventory state"
                )
            if not bool(getattr(self.claim_coverage_validator, "atomic_inventory_admission_enforced", False)):
                raise ValueError(
                    "GOVERNED assurance requires atomic claim coverage inventory admission and work consumption"
                )

        invoker = self.providers.invoke
        self.claim_coverage_guard = None
        if self.claim_coverage_validator is not None:
            self.claim_coverage_guard = ClaimCoverageGuardedInvoker(invoker, self.claim_coverage_validator)
            invoker = self.claim_coverage_guard
        self.engine = ReviewEngine(
            invoker,
            session_store=self.sessions,
            qualification_registry=self.qualifications,
            evidence_validator=self.evidence_validator,
        )

    def _coverage_durable_replay_protection(self) -> bool:
        return bool(
            getattr(self.claim_coverage_validator, "durable_work_state_enforced", False)
        ) if self.claim_coverage_validator is not None else False

    def _coverage_durable_inventory_state(self) -> bool:
        return bool(
            getattr(self.claim_coverage_validator, "durable_inventory_state_enforced", False)
        ) if self.claim_coverage_validator is not None else False

    def _coverage_atomic_inventory_admission(self) -> bool:
        return bool(
            getattr(self.claim_coverage_validator, "atomic_inventory_admission_enforced", False)
        ) if self.claim_coverage_validator is not None else False

    def _evidence_qualified_verifier(self) -> bool:
        return bool(
            getattr(self.evidence_validator, "qualified_verifier_assessment_enforced", False)
        ) if self.evidence_validator is not None else False

    def _evidence_durable_attestation_state(self) -> bool:
        return bool(
            getattr(self.evidence_validator, "durable_attestation_state_enforced", False)
        ) if self.evidence_validator is not None else False

    def _evidence_retained_snapshot_binding(self) -> bool:
        return bool(
            getattr(self.evidence_validator, "retained_snapshot_binding_enforced", False)
        ) if self.evidence_validator is not None else False

    def _evidence_durable_snapshot_state(self) -> bool:
        return bool(
            getattr(self.evidence_validator, "durable_snapshot_state_enforced", False)
        ) if self.evidence_validator is not None else False

    def review(self, payload: dict) -> dict:
        request = build_request(payload, platform_envelope=self.execution_envelope)
        decision = self.engine.run(
            request,
            r1=self.configuration.reviewer("R1"),
            r2=self.configuration.reviewer("R2"),
            r3=self.configuration.reviewer("R3"),
            memory=self.memory,
        )
        result = asdict(decision)
        durable_replay = self._coverage_durable_replay_protection()
        result.update(
            {
                "request_id": request.request_id,
                "platform_facts": request.platform_facts,
                "assurance_mode": self.configuration.assurance_mode,
                "action_authorized": False,
                "human_action_approval_required": bool(request.platform_facts.get("human_approval_required")),
                "session_chain_valid": self.sessions.validate_chain(request.request_id),
                "truth_contract_version": TVC_VERSION,
                "evidence_correspondence_validator_configured": self.evidence_validator is not None,
                "evidence_correspondence_qualified_verifier": self._evidence_qualified_verifier(),
                "evidence_correspondence_durable_attestation_state": self._evidence_durable_attestation_state(),
                "evidence_correspondence_retained_snapshot_binding": self._evidence_retained_snapshot_binding(),
                "evidence_correspondence_durable_snapshot_state": self._evidence_durable_snapshot_state(),
                "claim_coverage_validator_configured": self.claim_coverage_validator is not None,
                "claim_coverage_qualified_admission": bool(
                    getattr(self.claim_coverage_validator, "qualified_admission_enforced", False)
                ) if self.claim_coverage_validator is not None else False,
                "claim_coverage_trusted_scope_binding": bool(
                    getattr(self.claim_coverage_validator, "trusted_scope_binding_enforced", False)
                ) if self.claim_coverage_validator is not None else False,
                "claim_coverage_durable_work_state": durable_replay,
                "claim_coverage_durable_replay_protection": durable_replay,
                "claim_coverage_durable_inventory_state": self._coverage_durable_inventory_state(),
                "claim_coverage_atomic_inventory_admission": self._coverage_atomic_inventory_admission(),
            }
        )
        return result

    def judge_health(
        self,
        observations: Iterable[JudgeObservation],
        *,
        minimum_accuracy_target: float,
        minimum_shared_tasks: int = 20,
    ) -> dict:
        """Evaluate platform-retained judge telemetry without claiming correctness.

        This method intentionally has no public HTTP endpoint in the MVP. A
        future authenticated evaluation/telemetry pipeline should provide the
        observations so arbitrary callers cannot manufacture qualification
        health evidence.
        """
        monitor = JudgeHealthMonitor(
            minimum_accuracy_target=minimum_accuracy_target,
            minimum_shared_tasks=minimum_shared_tasks,
        )
        return asdict(monitor.evaluate(observations))

    def health(self) -> dict:
        reviewers = {}
        for role in ("R1", "R2", "R3"):
            cfg = self.configuration.reviewer(role)
            if cfg is not None:
                reviewers[role] = {
                    "provider": cfg.provider,
                    "model": cfg.model,
                    "sku": cfg.sku,
                    "deployment_path": cfg.deployment_path,
                    "enabled": cfg.enabled,
                    "qualification_ref": cfg.qualification_ref,
                }
        durable_replay = self._coverage_durable_replay_protection()
        return {
            "status": "ok",
            "assurance_mode": self.configuration.assurance_mode,
            "reviewers": reviewers,
            "memory_backend": "sqlite-single-node",
            "evidence_backend": "sqlite-hash-linked-single-node",
            "action_execution_enabled": False,
            "truth_contract_version": TVC_VERSION,
            "evidence_correspondence_validator": "CONFIGURED" if self.evidence_validator is not None else "UNCONFIGURED",
            "evidence_correspondence_qualified_verifier": self._evidence_qualified_verifier(),
            "evidence_correspondence_durable_attestation_state": self._evidence_durable_attestation_state(),
            "evidence_correspondence_retained_snapshot_binding": self._evidence_retained_snapshot_binding(),
            "evidence_correspondence_durable_snapshot_state": self._evidence_durable_snapshot_state(),
            "claim_coverage_validator": "CONFIGURED" if self.claim_coverage_validator is not None else "UNCONFIGURED",
            "claim_coverage_qualified_admission": bool(
                getattr(self.claim_coverage_validator, "qualified_admission_enforced", False)
            ) if self.claim_coverage_validator is not None else False,
            "claim_coverage_trusted_scope_binding": bool(
                getattr(self.claim_coverage_validator, "trusted_scope_binding_enforced", False)
            ) if self.claim_coverage_validator is not None else False,
            "claim_coverage_durable_work_state": durable_replay,
            "claim_coverage_durable_replay_protection": durable_replay,
            "claim_coverage_durable_inventory_state": self._coverage_durable_inventory_state(),
            "claim_coverage_atomic_inventory_admission": self._coverage_atomic_inventory_admission(),
            "judge_health_monitor": "PAIRWISE_LOGICAL_DISAGREEMENT_BOUND_V1",
            "execution_envelope": {
                "operation_class": self.execution_envelope.operation_class,
                "connected_tool_capabilities": list(self.execution_envelope.connected_tool_capabilities),
                "target_environment": self.execution_envelope.target_environment,
                "task_type": self.execution_envelope.task_type,
                "source": "trusted_application_boundary",
            },
        }

    def session_summaries(self, *, limit: int = 100) -> list[dict]:
        return [asdict(summary) for summary in self.sessions.list_sessions(limit=limit)]

    def session_events(self, session_id: str) -> list[dict]:
        return [asdict(event) for event in self.sessions.events(session_id)]

    def current_memory(self) -> list[dict]:
        return [asdict(record) for record in self.memory.reviewer_visible()]
