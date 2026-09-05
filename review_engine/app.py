from __future__ import annotations

from dataclasses import asdict

from .configuration import ReviewEngineConfiguration, build_provider_registry, build_qualification_registry
from .orchestrator import ReviewEngine
from .request_boundary import build_request
from .session_store import SQLiteSessionStore
from .sqlite_memory import SQLiteMemoryStore


class ReviewEngineApp:
    """Application service used by CLI, HTTP API and future UI."""

    def __init__(
        self,
        configuration: ReviewEngineConfiguration,
        *,
        memory_db: str,
        sessions_db: str,
        provider_registry=None,
    ) -> None:
        self.configuration = configuration
        self.providers = provider_registry or build_provider_registry(configuration)
        self.qualifications = build_qualification_registry(configuration)
        self.memory = SQLiteMemoryStore(memory_db)
        self.sessions = SQLiteSessionStore(sessions_db)
        self.engine = ReviewEngine(
            self.providers.invoke,
            session_store=self.sessions,
            qualification_registry=self.qualifications,
        )

    def review(self, payload: dict) -> dict:
        request = build_request(payload)
        decision = self.engine.run(
            request,
            r1=self.configuration.reviewer("R1"),
            r2=self.configuration.reviewer("R2"),
            r3=self.configuration.reviewer("R3"),
            memory=self.memory,
        )
        result = asdict(decision)
        result.update({
            "request_id": request.request_id,
            "platform_facts": request.platform_facts,
            "assurance_mode": self.configuration.assurance_mode,
            "action_authorized": False,
            "human_action_approval_required": bool(request.platform_facts.get("human_approval_required")),
            "session_chain_valid": self.sessions.validate_chain(request.request_id),
        })
        return result

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
        }

    def session_summaries(self, *, limit: int = 100) -> list[dict]:
        return [asdict(summary) for summary in self.sessions.list_sessions(limit=limit)]

    def session_events(self, session_id: str) -> list[dict]:
        return [asdict(event) for event in self.sessions.events(session_id)]

    def current_memory(self) -> list[dict]:
        return [asdict(record) for record in self.memory.reviewer_visible()]
