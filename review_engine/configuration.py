from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .anthropic_provider import AnthropicEndpoint, AnthropicProvider
from .gemini_provider import GeminiEndpoint, GeminiProvider
from .models import ReviewerConfig
from .providers import OpenAICompatibleEndpoint, OpenAICompatibleProvider, ProviderRegistry
from .qualification import QualificationRecord, QualificationRegistry


TOP_LEVEL_FIELDS = frozenset({"providers", "reviewers", "qualifications"})
REVIEWER_ROLES = frozenset({"R1", "R2", "R3"})
REVIEWER_FIELDS = frozenset({
    "provider",
    "model",
    "sku",
    "deployment_path",
    "api_key_env",
    "foundation_lineage",
    "qualification_ref",
    "enabled",
})
QUALIFICATION_FIELDS = frozenset({
    "qualification_ref",
    "provider",
    "model",
    "sku",
    "deployment_path",
    "role",
    "status",
    "qualification_epoch",
    "foundation_lineage",
    "max_risk",
    "task_types",
    "provider_binding_fingerprint",
})
PROVIDER_FIELDS = {
    "openai_compatible": frozenset({
        "adapter",
        "base_url",
        "timeout_seconds",
        "max_attempts",
        "initial_backoff_seconds",
        "max_backoff_seconds",
        "temperature",
    }),
    "anthropic": frozenset({
        "adapter",
        "base_url",
        "anthropic_version",
        "timeout_seconds",
        "max_attempts",
        "max_tokens",
        "temperature",
        "initial_backoff_seconds",
        "max_backoff_seconds",
    }),
    "gemini": frozenset({
        "adapter",
        "base_url",
        "timeout_seconds",
        "max_attempts",
        "temperature",
        "max_output_tokens",
        "initial_backoff_seconds",
        "max_backoff_seconds",
    }),
}
FORBIDDEN_CREDENTIAL_FIELD_NAMES = frozenset({
    "apikey",
    "token",
    "secret",
    "authorization",
    "accesstoken",
    "bearertoken",
    "authtoken",
    "clientsecret",
    "secretkey",
    "password",
    "passwd",
    "privatekey",
    "credential",
    "credentials",
})


@dataclass(frozen=True)
class ReviewEngineConfiguration:
    reviewers: dict[str, ReviewerConfig]
    provider_specs: dict[str, dict[str, Any]]
    qualification_records: tuple[QualificationRecord, ...] = ()

    def reviewer(self, role: str) -> ReviewerConfig | None:
        return self.reviewers.get(role)

    @property
    def assurance_mode(self) -> str:
        return "GOVERNED" if self.qualification_records else "EXPERIMENTAL_UNQUALIFIED"


def _normalized_field_name(value: object) -> str:
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def _reject_secret_material(node: Any, path: str = "root") -> None:
    """Reject credential-shaped configuration fields at any nesting depth.

    The configuration contract carries secret *references* such as api_key_env,
    never raw credentials. Normalization catches common spelling variants such as
    apiKey, api-key, client_secret and bearer-token without matching legitimate
    reference names like api_key_env.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if _normalized_field_name(key) in FORBIDDEN_CREDENTIAL_FIELD_NAMES:
                raise ValueError(f"raw credential field forbidden in configuration: {path}.{key}")
            _reject_secret_material(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            _reject_secret_material(value, f"{path}[{index}]")


def _reject_unknown_fields(node: dict, *, path: str, allowed: frozenset[str]) -> None:
    unknown = sorted(str(key) for key in node if key not in allowed)
    if unknown:
        raise ValueError(f"unsupported configuration field(s) at {path}: {', '.join(unknown)}")


def _effective_provider_binding(spec: dict[str, Any]) -> dict[str, Any]:
    """Return the canonical provider execution configuration used for qualification binding.

    Fingerprinting is intentionally separate from transport admission. It binds
    the configured value exactly enough to detect later substitution, while the
    provider adapter remains the authority that rejects insecure/invalid remote
    endpoints during registry construction. This preserves fail-closed transport
    tests without turning fingerprint calculation into a second transport gate.
    """
    adapter_type = spec.get("adapter")
    if adapter_type == "openai_compatible":
        return {
            "adapter": adapter_type,
            "base_url": str(spec.get("base_url", "")).strip(),
            "timeout_seconds": int(spec.get("timeout_seconds", 120)),
            "max_attempts": int(spec.get("max_attempts", 3)),
            "initial_backoff_seconds": float(spec.get("initial_backoff_seconds", 1.0)),
            "max_backoff_seconds": float(spec.get("max_backoff_seconds", 10.0)),
            "temperature": float(spec.get("temperature", 0.0)),
        }
    if adapter_type == "anthropic":
        return {
            "adapter": adapter_type,
            "base_url": str(spec.get("base_url", "https://api.anthropic.com/v1")).strip(),
            "anthropic_version": str(spec.get("anthropic_version", "2023-06-01")),
            "timeout_seconds": int(spec.get("timeout_seconds", 120)),
            "max_attempts": int(spec.get("max_attempts", 3)),
            "max_tokens": int(spec.get("max_tokens", 4096)),
            "temperature": float(spec.get("temperature", 0.0)),
            "initial_backoff_seconds": float(spec.get("initial_backoff_seconds", 1.0)),
            "max_backoff_seconds": float(spec.get("max_backoff_seconds", 10.0)),
        }
    if adapter_type == "gemini":
        return {
            "adapter": adapter_type,
            "base_url": str(spec.get("base_url", "https://generativelanguage.googleapis.com/v1beta")).strip(),
            "timeout_seconds": int(spec.get("timeout_seconds", 120)),
            "max_attempts": int(spec.get("max_attempts", 3)),
            "temperature": float(spec.get("temperature", 0.0)),
            "max_output_tokens": int(spec.get("max_output_tokens", 4096)),
            "initial_backoff_seconds": float(spec.get("initial_backoff_seconds", 1.0)),
            "max_backoff_seconds": float(spec.get("max_backoff_seconds", 10.0)),
        }
    raise ValueError(f"unsupported provider adapter: {adapter_type!r}")


def provider_binding_fingerprint(spec: dict[str, Any]) -> str:
    """Bind retained reviewer qualification to the exact configured provider route."""
    canonical = json.dumps(
        _effective_provider_binding(spec),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_configuration(path: str | Path) -> ReviewEngineConfiguration:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("configuration root must be an object")
    _reject_secret_material(data)
    _reject_unknown_fields(data, path="root", allowed=TOP_LEVEL_FIELDS)

    provider_specs = data.get("providers")
    reviewer_specs = data.get("reviewers")
    if not isinstance(provider_specs, dict) or not isinstance(reviewer_specs, dict):
        raise ValueError("configuration requires providers and reviewers objects")

    _reject_unknown_fields(reviewer_specs, path="root.reviewers", allowed=REVIEWER_ROLES)

    validated_provider_specs: dict[str, dict[str, Any]] = {}
    for provider_id, spec in provider_specs.items():
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("provider identifier must be a non-empty string")
        if not isinstance(spec, dict):
            raise ValueError(f"provider {provider_id} must be an object")
        adapter_type = spec.get("adapter")
        allowed_fields = PROVIDER_FIELDS.get(adapter_type)
        if allowed_fields is None:
            raise ValueError(f"unsupported provider adapter: {adapter_type!r}")
        _reject_unknown_fields(spec, path=f"root.providers.{provider_id}", allowed=allowed_fields)
        validated_provider_specs[provider_id] = dict(spec)

    reviewers: dict[str, ReviewerConfig] = {}
    for role in ("R1", "R2", "R3"):
        spec = reviewer_specs.get(role)
        if spec is None:
            continue
        if not isinstance(spec, dict):
            raise ValueError(f"reviewer {role} must be an object")
        _reject_unknown_fields(spec, path=f"root.reviewers.{role}", allowed=REVIEWER_FIELDS)
        provider_id = str(spec.get("provider", ""))
        if provider_id not in validated_provider_specs:
            raise ValueError(f"reviewer {role} references unknown provider {provider_id}")
        config = ReviewerConfig(
            role=role,
            provider=provider_id,
            model=str(spec.get("model", "")),
            sku=str(spec.get("sku", "default")),
            deployment_path=str(spec.get("deployment_path", "api")),
            api_key_env=str(spec.get("api_key_env", "")),
            foundation_lineage=str(spec.get("foundation_lineage", "")),
            qualification_ref=spec.get("qualification_ref"),
            enabled=bool(spec.get("enabled", True)),
            provider_binding_fingerprint=provider_binding_fingerprint(validated_provider_specs[provider_id]),
        )
        config.validate()
        reviewers[role] = config
    if "R1" not in reviewers:
        raise ValueError("R1 reviewer configuration is required")

    records: list[QualificationRecord] = []
    raw_records = data.get("qualifications", [])
    if not isinstance(raw_records, list):
        raise ValueError("qualifications must be a list")
    for index, item in enumerate(raw_records):
        if not isinstance(item, dict):
            raise ValueError("qualification record must be an object")
        _reject_unknown_fields(item, path=f"root.qualifications[{index}]", allowed=QUALIFICATION_FIELDS)
        task_types = item.get("task_types", ["*"])
        if not isinstance(task_types, list):
            raise ValueError("qualification task_types must be a list")
        raw_provider_binding = item.get("provider_binding_fingerprint")
        record = QualificationRecord(
            qualification_ref=str(item.get("qualification_ref", "")),
            provider=str(item.get("provider", "")),
            model=str(item.get("model", "")),
            sku=str(item.get("sku", "default")),
            deployment_path=str(item.get("deployment_path", "api")),
            role=str(item.get("role", "")),
            status=str(item.get("status", "UNQUALIFIED")),
            qualification_epoch=int(item.get("qualification_epoch", 1)),
            foundation_lineage=str(item.get("foundation_lineage", "")),
            max_risk=str(item.get("max_risk", "LOW")),
            task_types=tuple(str(v) for v in task_types),
            provider_binding_fingerprint=(
                str(raw_provider_binding) if raw_provider_binding is not None else None
            ),
        )
        record.validate()
        records.append(record)
    QualificationRegistry(tuple(records))
    return ReviewEngineConfiguration(
        reviewers=reviewers,
        provider_specs=validated_provider_specs,
        qualification_records=tuple(records),
    )


def build_provider_registry(configuration: ReviewEngineConfiguration) -> ProviderRegistry:
    registry = ProviderRegistry()
    for provider_id, spec in configuration.provider_specs.items():
        if not isinstance(spec, dict):
            raise ValueError(f"provider {provider_id} must be an object")
        adapter_type = spec.get("adapter")
        if adapter_type == "openai_compatible":
            adapter = OpenAICompatibleProvider(
                OpenAICompatibleEndpoint(
                    base_url=str(spec.get("base_url", "")),
                    timeout_seconds=int(spec.get("timeout_seconds", 120)),
                    max_attempts=int(spec.get("max_attempts", 3)),
                    initial_backoff_seconds=float(spec.get("initial_backoff_seconds", 1.0)),
                    max_backoff_seconds=float(spec.get("max_backoff_seconds", 10.0)),
                    temperature=float(spec.get("temperature", 0.0)),
                )
            )
        elif adapter_type == "anthropic":
            adapter = AnthropicProvider(
                AnthropicEndpoint(
                    base_url=str(spec.get("base_url", "https://api.anthropic.com/v1")),
                    anthropic_version=str(spec.get("anthropic_version", "2023-06-01")),
                    timeout_seconds=int(spec.get("timeout_seconds", 120)),
                    max_attempts=int(spec.get("max_attempts", 3)),
                    max_tokens=int(spec.get("max_tokens", 4096)),
                    temperature=float(spec.get("temperature", 0.0)),
                    initial_backoff_seconds=float(spec.get("initial_backoff_seconds", 1.0)),
                    max_backoff_seconds=float(spec.get("max_backoff_seconds", 10.0)),
                )
            )
        elif adapter_type == "gemini":
            adapter = GeminiProvider(
                GeminiEndpoint(
                    base_url=str(spec.get("base_url", "https://generativelanguage.googleapis.com/v1beta")),
                    timeout_seconds=int(spec.get("timeout_seconds", 120)),
                    max_attempts=int(spec.get("max_attempts", 3)),
                    temperature=float(spec.get("temperature", 0.0)),
                    max_output_tokens=int(spec.get("max_output_tokens", 4096)),
                    initial_backoff_seconds=float(spec.get("initial_backoff_seconds", 1.0)),
                    max_backoff_seconds=float(spec.get("max_backoff_seconds", 10.0)),
                )
            )
        else:
            raise ValueError(f"unsupported provider adapter: {adapter_type!r}")
        registry.register(provider_id, adapter)
    return registry


def build_qualification_registry(configuration: ReviewEngineConfiguration) -> QualificationRegistry | None:
    if not configuration.qualification_records:
        return None
    for record in configuration.qualification_records:
        if not record.provider_binding_fingerprint:
            raise ValueError(
                f"qualification {record.qualification_ref} requires provider binding fingerprint"
            )
        provider_spec = configuration.provider_specs.get(record.provider)
        if provider_spec is None:
            raise ValueError(
                f"qualification {record.qualification_ref} references unknown provider {record.provider}"
            )
        current_binding = provider_binding_fingerprint(provider_spec)
        if record.provider_binding_fingerprint != current_binding:
            raise ValueError(
                f"qualification {record.qualification_ref} provider binding fingerprint mismatch"
            )
    return QualificationRegistry(configuration.qualification_records)
