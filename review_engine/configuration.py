from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import ReviewerConfig
from .providers import OpenAICompatibleEndpoint, OpenAICompatibleProvider, ProviderRegistry


@dataclass(frozen=True)
class ReviewEngineConfiguration:
    reviewers: dict[str, ReviewerConfig]
    provider_specs: dict[str, dict[str, Any]]

    def reviewer(self, role: str) -> ReviewerConfig | None:
        return self.reviewers.get(role)


def _reject_secret_material(node: Any, path: str = "root") -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            lower = str(key).lower()
            if lower in {"api_key", "apikey", "token", "secret", "authorization"}:
                raise ValueError(f"raw credential field forbidden in configuration: {path}.{key}")
            _reject_secret_material(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _reject_secret_material(value, f"{path}[{index}]")


def load_configuration(path: str | Path) -> ReviewEngineConfiguration:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("configuration root must be an object")
    _reject_secret_material(data)

    provider_specs = data.get("providers")
    reviewer_specs = data.get("reviewers")
    if not isinstance(provider_specs, dict) or not isinstance(reviewer_specs, dict):
        raise ValueError("configuration requires providers and reviewers objects")

    reviewers: dict[str, ReviewerConfig] = {}
    for role in ("R1", "R2", "R3"):
        spec = reviewer_specs.get(role)
        if spec is None:
            continue
        if not isinstance(spec, dict):
            raise ValueError(f"reviewer {role} must be an object")
        config = ReviewerConfig(
            role=role,
            provider=str(spec.get("provider", "")),
            model=str(spec.get("model", "")),
            sku=str(spec.get("sku", "default")),
            deployment_path=str(spec.get("deployment_path", "api")),
            api_key_env=str(spec.get("api_key_env", "")),
            foundation_lineage=str(spec.get("foundation_lineage", "")),
            qualification_ref=spec.get("qualification_ref"),
            enabled=bool(spec.get("enabled", True)),
        )
        config.validate()
        if config.provider not in provider_specs:
            raise ValueError(f"reviewer {role} references unknown provider {config.provider}")
        reviewers[role] = config

    if "R1" not in reviewers:
        raise ValueError("R1 reviewer configuration is required")
    return ReviewEngineConfiguration(reviewers=reviewers, provider_specs=provider_specs)


def build_provider_registry(configuration: ReviewEngineConfiguration) -> ProviderRegistry:
    registry = ProviderRegistry()
    for provider_id, spec in configuration.provider_specs.items():
        if not isinstance(spec, dict):
            raise ValueError(f"provider {provider_id} must be an object")
        adapter_type = spec.get("adapter")
        if adapter_type != "openai_compatible":
            raise ValueError(f"unsupported provider adapter for MVP: {adapter_type!r}")
        endpoint = OpenAICompatibleEndpoint(
            base_url=str(spec.get("base_url", "")),
            timeout_seconds=int(spec.get("timeout_seconds", 120)),
            max_attempts=int(spec.get("max_attempts", 3)),
            initial_backoff_seconds=float(spec.get("initial_backoff_seconds", 1.0)),
            max_backoff_seconds=float(spec.get("max_backoff_seconds", 10.0)),
            temperature=float(spec.get("temperature", 0.0)),
        )
        registry.register(provider_id, OpenAICompatibleProvider(endpoint))
    return registry
