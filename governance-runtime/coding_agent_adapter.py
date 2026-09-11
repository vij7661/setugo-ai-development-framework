#!/usr/bin/env python3
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Callable, Iterable, Mapping, Sequence

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"(?i)\b(?:api[_-]?key|token|secret|password)\s*[=:]\s*[^\s,;]+"),
    re.compile(r"(?i)\bauthorization\s*:\s*bearer\s+[^\s,;]+"),
)

COMPLETION_STATES = frozenset({
    "COMPLETED", "FAILED", "BLOCKED", "REQUIREMENT_UNRESOLVED", "CANCELLED",
})
FAILURE_CLASSES = frozenset({
    "NONE", "CODE DEFECT", "FIXTURE-DATA DEFECT", "TEST DEFECT",
    "ENVIRONMENT-TOOLING DEFECT", "REQUIREMENT UNRESOLVED",
    "AGENT_ADAPTER_DEFECT", "SCOPE_VIOLATION",
})
GOVERNANCE_PREFIXES = (
    "governance-runtime/", "standards/", "experiments/governed-platform/adjudication/",
    "experiments/governed-platform/review-", ".github/workflows/",
)
TERMINAL_AUTHORITY_KEYS = frozenset({
    "merge_authorized", "release_authorized", "deploy_authorized", "promotion_authorized",
    "terminal_authority", "authority_granted",
})
REQUIRED_NATIVE_FIELDS = frozenset({
    "completion_state", "changed_artifacts", "commands_run", "test_results",
    "failure_classification", "execution_events",
})


class AdapterContractError(ValueError):
    pass


class ScopeViolation(AdapterContractError):
    pass


class TestIntegrityViolation(AdapterContractError):
    pass


class SecretContainmentViolation(AdapterContractError):
    pass


class AuthorityViolation(AdapterContractError):
    pass


class IdempotencyConflict(AdapterContractError):
    pass


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _hash(value: Any) -> str:
    return hashlib.sha256(_canon(value)).hexdigest()


def _path_matches(path: str, rule: str) -> bool:
    if not isinstance(path, str) or not isinstance(rule, str) or not path or not rule:
        return False
    if rule.endswith("/"):
        return path.startswith(rule)
    return path == rule or path.startswith(rule.rstrip("/") + "/")


def _contains_secret(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_contains_secret(k) or _contains_secret(v) for k, v in value.items())
    if isinstance(value, (list, tuple, set, frozenset)):
        return any(_contains_secret(v) for v in value)
    if not isinstance(value, str):
        return False
    return any(p.search(value) for p in SECRET_PATTERNS)


@dataclass(frozen=True)
class AgentDescriptor:
    adapter_id: str
    agent_id: str
    agent_family: str
    agent_version: str
    capabilities: frozenset[str]

    def __post_init__(self) -> None:
        for name in ("adapter_id", "agent_id", "agent_family", "agent_version"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise AdapterContractError(f"{name} is required")
        if not isinstance(self.capabilities, frozenset) or not self.capabilities:
            raise AdapterContractError("capabilities must be a non-empty frozenset")
        if any(not isinstance(x, str) or not x.strip() for x in self.capabilities):
            raise AdapterContractError("capabilities must contain non-empty strings")


@dataclass(frozen=True)
class GovernedCodingTask:
    task_id: str
    candidate_sha: str
    goal: str
    allowed_paths: tuple[str, ...]
    forbidden_paths: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    required_tests: tuple[str, ...]
    forbidden_changes: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    required_capabilities: frozenset[str]
    authorized_test_changes: tuple[str, ...] = ()
    authorized_governance_paths: tuple[str, ...] = ()
    allow_governance_mutation: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, str) or not self.task_id.strip():
            raise AdapterContractError("task_id is required")
        if not SHA40.fullmatch(str(self.candidate_sha)):
            raise AdapterContractError("candidate_sha must be an exact lowercase SHA40")
        if not isinstance(self.goal, str) or not self.goal.strip():
            raise AdapterContractError("goal is required")
        for name in ("allowed_paths", "acceptance_criteria", "required_tests", "stop_conditions"):
            value = getattr(self, name)
            if not isinstance(value, tuple) or not value or any(not isinstance(x, str) or not x for x in value):
                raise AdapterContractError(f"{name} must be a non-empty tuple of strings")
        for name in ("forbidden_paths", "forbidden_changes", "authorized_test_changes", "authorized_governance_paths"):
            value = getattr(self, name)
            if not isinstance(value, tuple) or any(not isinstance(x, str) or not x for x in value):
                raise AdapterContractError(f"{name} must be a tuple of strings")
        if not isinstance(self.required_capabilities, frozenset) or not self.required_capabilities:
            raise AdapterContractError("required_capabilities must be a non-empty frozenset")
        if not isinstance(self.allow_governance_mutation, bool):
            raise AdapterContractError("allow_governance_mutation must be boolean")

    def contract_view(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "candidate_sha": self.candidate_sha,
            "goal": self.goal,
            "allowed_paths": list(self.allowed_paths),
            "forbidden_paths": list(self.forbidden_paths),
            "acceptance_criteria": list(self.acceptance_criteria),
            "required_tests": list(self.required_tests),
            "forbidden_changes": list(self.forbidden_changes),
            "stop_conditions": list(self.stop_conditions),
            "required_capabilities": sorted(self.required_capabilities),
            "authorized_test_changes": list(self.authorized_test_changes),
            "authorized_governance_paths": list(self.authorized_governance_paths),
            "allow_governance_mutation": self.allow_governance_mutation,
        }


class CodingAgentAdapter(ABC):
    @property
    @abstractmethod
    def descriptor(self) -> AgentDescriptor:
        raise NotImplementedError

    @abstractmethod
    def execute(self, task: GovernedCodingTask) -> Mapping[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def normalize(self, task: GovernedCodingTask, native_result: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, CodingAgentAdapter] = {}

    def register(self, adapter: CodingAgentAdapter) -> None:
        if not isinstance(adapter, CodingAgentAdapter):
            raise AdapterContractError("adapter must implement CodingAgentAdapter")
        desc = adapter.descriptor
        if desc.adapter_id in self._adapters:
            raise AdapterContractError(f"duplicate adapter_id: {desc.adapter_id}")
        self._adapters[desc.adapter_id] = adapter

    def get(self, adapter_id: str) -> CodingAgentAdapter:
        try:
            return self._adapters[adapter_id]
        except KeyError as exc:
            raise AdapterContractError(f"unknown adapter_id: {adapter_id}") from exc

    def descriptors(self) -> list[AgentDescriptor]:
        return [self._adapters[k].descriptor for k in sorted(self._adapters)]


class InMemoryExecutionStore:
    def __init__(self) -> None:
        self._by_execution: dict[str, dict[str, Any]] = {}
        self._history: list[dict[str, Any]] = []

    @staticmethod
    def _material(record: Mapping[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in dict(record).items() if k != "result_hash"}

    def put(self, record: Mapping[str, Any]) -> dict[str, Any]:
        execution_id = str(record.get("execution_id", ""))
        if not execution_id:
            raise AdapterContractError("execution_id is required")
        material = self._material(record)
        computed = _hash(material)
        supplied = record.get("result_hash")
        if supplied is not None and supplied != computed:
            existing = self._by_execution.get(execution_id)
            if existing is not None:
                raise IdempotencyConflict("execution_id reused with conflicting content")
            raise AdapterContractError("result_hash does not match normalized result")
        normalized = dict(material)
        normalized["result_hash"] = computed
        existing = self._by_execution.get(execution_id)
        if existing is not None:
            if _hash(self._material(existing)) != computed:
                raise IdempotencyConflict("execution_id reused with conflicting content")
            return dict(existing)
        self._by_execution[execution_id] = normalized
        self._history.append(normalized)
        return dict(normalized)

    def get(self, execution_id: str) -> dict[str, Any] | None:
        value = self._by_execution.get(execution_id)
        return None if value is None else dict(value)

    def history_for_task(self, task_id: str) -> list[dict[str, Any]]:
        return [dict(x) for x in self._history if x.get("task_id") == task_id]


class JsonlExecutionStore(InMemoryExecutionStore):
    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self.path = Path(path)
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                record = json.loads(line)
                super().put(record)

    def put(self, record: Mapping[str, Any]) -> dict[str, Any]:
        execution_id = str(record.get("execution_id", ""))
        before = self.get(execution_id) if execution_id else None
        saved = super().put(record)
        if before is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(saved, sort_keys=True, separators=(",", ":")) + "\n")
        return saved


class CodingAgentExecutionGateway:
    def __init__(self, registry: AdapterRegistry, *, store: InMemoryExecutionStore | None = None,
                 reviewer_dispatch: Callable[..., Any] | None = None, phase: str = "TESTING") -> None:
        self.registry = registry
        self.store = store or InMemoryExecutionStore()
        self.reviewer_dispatch = reviewer_dispatch
        self.phase = str(phase).upper()
        if self.phase not in {"TESTING", "RELEASE", "PRODUCTION"}:
            raise AdapterContractError(f"unsupported phase: {phase}")

    @classmethod
    def from_adapters(cls, adapters: Iterable[CodingAgentAdapter], **kwargs: Any) -> "CodingAgentExecutionGateway":
        registry = AdapterRegistry()
        for adapter in adapters:
            registry.register(adapter)
        return cls(registry, **kwargs)

    def _validate_capabilities(self, adapter: CodingAgentAdapter, task: GovernedCodingTask) -> None:
        missing = task.required_capabilities - adapter.descriptor.capabilities
        if missing:
            raise AdapterContractError(f"adapter lacks required capabilities: {sorted(missing)}")

    def _validate_native_pre_normalization(self, native: Mapping[str, Any], task: GovernedCodingTask) -> None:
        if not isinstance(native, Mapping):
            raise AdapterContractError("adapter native result must be a mapping")
        candidate = native.get("candidate_sha")
        if candidate is not None and candidate != task.candidate_sha:
            raise AdapterContractError("native result candidate_sha does not match governed task")
        if _contains_secret(native):
            raise SecretContainmentViolation("raw secret-like material detected in agent result")
        authority = native.get("authority_effect")
        if authority not in (None, "", "NONE"):
            raise AuthorityViolation("agent attempted to assert authority")
        for key in TERMINAL_AUTHORITY_KEYS:
            if native.get(key) not in (None, False, "", "NONE"):
                raise AuthorityViolation(f"agent attempted terminal authority via {key}")

    def _normalize(self, adapter: CodingAgentAdapter, task: GovernedCodingTask,
                   native: Mapping[str, Any], execution_id: str) -> dict[str, Any]:
        missing = REQUIRED_NATIVE_FIELDS - set(native.keys())
        if missing:
            raise AdapterContractError(f"native result missing required fields: {sorted(missing)}")
        raw = adapter.normalize(task, native)
        if not isinstance(raw, Mapping):
            raise AdapterContractError("adapter normalize() must return a mapping")
        out = dict(raw)
        out.update({
            "schema_version": 1,
            "execution_id": execution_id,
            "task_id": task.task_id,
            "candidate_sha": task.candidate_sha,
            "adapter_id": adapter.descriptor.adapter_id,
            "agent_id": adapter.descriptor.agent_id,
            "agent_family": adapter.descriptor.agent_family,
            "agent_version": adapter.descriptor.agent_version,
            "task_contract_hash": _hash(task.contract_view()),
            "authority_effect": "NONE",
            "review_effect": "MANUAL_REVIEW_IF_REQUESTED" if self.phase == "TESTING" else "SEPARATE_PHASE_REVIEW_POLICY",
            "phase": self.phase,
        })
        required_normalized = {
            "completion_state", "changed_artifacts", "commands_run", "test_results",
            "failure_classification", "execution_events",
        }
        missing_normalized = required_normalized - set(out.keys())
        if missing_normalized:
            raise AdapterContractError(f"normalized result missing fields: {sorted(missing_normalized)}")
        if out["completion_state"] not in COMPLETION_STATES:
            raise AdapterContractError("invalid completion_state")
        if out["failure_classification"] not in FAILURE_CLASSES:
            raise AdapterContractError("invalid failure_classification")
        if out["completion_state"] == "REQUIREMENT_UNRESOLVED" and out["failure_classification"] != "REQUIREMENT UNRESOLVED":
            raise AdapterContractError("REQUIREMENT_UNRESOLVED must preserve requirement failure classification")
        for key in ("changed_artifacts", "commands_run", "test_results", "execution_events"):
            if not isinstance(out[key], list):
                raise AdapterContractError(f"{key} must be normalized as a list")
        if any(not isinstance(path, str) or not path for path in out["changed_artifacts"]):
            raise AdapterContractError("changed_artifacts must contain non-empty paths")
        if _contains_secret(out):
            raise SecretContainmentViolation("raw secret-like material detected after normalization")
        return out

    def _validate_scope_and_test_integrity(self, task: GovernedCodingTask, out: dict[str, Any]) -> None:
        material_test_change = False
        for path in out["changed_artifacts"]:
            if not any(_path_matches(path, allowed) for allowed in task.allowed_paths):
                raise ScopeViolation(f"changed artifact outside allowed scope: {path}")
            if any(_path_matches(path, denied) for denied in task.forbidden_paths):
                raise ScopeViolation(f"changed artifact is forbidden: {path}")
            if any(_path_matches(path, denied) for denied in task.forbidden_changes):
                raise ScopeViolation(f"explicit forbidden change detected: {path}")
            governance_path = any(_path_matches(path, prefix) for prefix in GOVERNANCE_PREFIXES)
            if governance_path:
                exact_authorized = path in task.authorized_governance_paths
                if not (task.allow_governance_mutation and exact_authorized):
                    raise ScopeViolation(f"governance mutation denied by default: {path}")
            if path in task.required_tests:
                if path not in task.authorized_test_changes:
                    raise TestIntegrityViolation(f"required test mutation is not authorized: {path}")
                material_test_change = True
        out["material_test_change_requires_adjudication"] = material_test_change

    def execute(self, adapter_id: str, task: GovernedCodingTask, *, execution_id: str) -> dict[str, Any]:
        if not isinstance(task, GovernedCodingTask):
            raise AdapterContractError("task must be GovernedCodingTask")
        if not isinstance(execution_id, str) or not execution_id.strip():
            raise AdapterContractError("execution_id is required")
        adapter = self.registry.get(adapter_id)
        self._validate_capabilities(adapter, task)
        native = adapter.execute(task)
        self._validate_native_pre_normalization(native, task)
        out = self._normalize(adapter, task, native, execution_id)
        self._validate_scope_and_test_integrity(task, out)
        saved = self.store.put(out)
        # Coding-agent execution is never a reviewer dispatch side effect. Review is a separate governed action.
        return saved

    def ingest_result(self, result: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(result, Mapping):
            raise AdapterContractError("result must be a mapping")
        if result.get("authority_effect") != "NONE":
            raise AuthorityViolation("ingested result cannot carry authority")
        if _contains_secret(result):
            raise SecretContainmentViolation("raw secret-like material detected in ingested result")
        return self.store.put(result)
