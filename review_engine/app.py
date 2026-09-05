from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from .configuration import ReviewEngineConfiguration, build_provider_registry, build_qualification_registry
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
        self.engine = ReviewEngine(
            self.providers.invoke,
            session_store=self.sessions,
            qualification_registry=self.qualifications,
        )

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
        result.update(
            {
                "request_id": request.request_id,
                "platform_facts": request.platform_facts,
                "assurance_mode": self.configuration.assurance_mode,
                "action_authorized": False,
                "human_action_approval_required": bool(request.platform_facts.get("human_approval_required")),
                "session_chain_valid": self.sessions.validate_chain(request.request_id),
                "truth_contract_version": TVC_VERSION,
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
        return {
            "status": "ok",
            "assurance_mode": self.configuration.assurance_mode,
            "reviewers": reviewers,
            "memory_backend": "sqlite-single-node",
            "evidence_backend": "sqlite-hash-linked-single-node",
            "action_execution_enabled": False,
            "truth_contract_version": TVC_VERSION,
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
