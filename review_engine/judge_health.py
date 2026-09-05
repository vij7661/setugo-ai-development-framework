from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
from math import floor
from typing import Iterable


@dataclass(frozen=True)
class JudgeIdentityBinding:
    """Platform-retained identity for judge-health telemetry.

    The ID is derived from configured/qualified routing identity rather than a
    model self-reported name. Runtime cryptographic provider attestation remains
    a separate integration boundary.
    """

    provider: str
    model: str
    sku: str
    deployment_path: str
    role: str
    foundation_lineage: str
    qualification_ref: str
    qualification_epoch: int

    def validate(self) -> None:
        for field in (
            "provider",
            "model",
            "sku",
            "deployment_path",
            "role",
            "foundation_lineage",
            "qualification_ref",
        ):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"judge identity {field} required")
        if self.qualification_epoch < 1:
            raise ValueError("judge identity qualification_epoch must be >= 1")

    @property
    def judge_id(self) -> str:
        self.validate()
        payload = json.dumps(
            {
                "provider": self.provider,
                "model": self.model,
                "sku": self.sku,
                "deployment_path": self.deployment_path,
                "role": self.role,
                "foundation_lineage": self.foundation_lineage,
                "qualification_ref": self.qualification_ref,
                "qualification_epoch": self.qualification_epoch,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return "judge:" + sha256(payload.encode("utf-8")).hexdigest()

    @property
    def runtime_path(self) -> tuple[str, str, str, str]:
        return (self.provider, self.model, self.sku, self.deployment_path)


@dataclass(frozen=True)
class JudgeObservation:
    """One platform-retained judge decision on a comparable evaluation item."""

    task_id: str
    judge_id: str
    label: str
    dimension: str = "GENERAL"
    identity: JudgeIdentityBinding | None = None

    @classmethod
    def bound(
        cls,
        task_id: str,
        identity: JudgeIdentityBinding,
        label: str,
        dimension: str = "GENERAL",
    ) -> "JudgeObservation":
        identity.validate()
        return cls(task_id, identity.judge_id, label, dimension, identity)

    def validate(self, *, require_bound_identity: bool = False) -> None:
        for name in ("task_id", "judge_id", "label", "dimension"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"judge observation {name} required")
        if self.identity is None:
            if require_bound_identity:
                raise ValueError("judge observation requires platform-bound identity")
            return
        self.identity.validate()
        if self.judge_id != self.identity.judge_id:
            raise ValueError("judge_id does not match platform-bound judge identity")


@dataclass(frozen=True)
class PairwiseJudgeAssessment:
    dimension: str
    judge_a: str
    judge_b: str
    shared_tasks: int
    disagreements: int
    disagreement_rate: float
    max_disagreements_if_both_meet_target: int
    alarm: bool
    identity_correlation: str = "UNBOUND_IDENTITY"


@dataclass(frozen=True)
class JudgeHealthReport:
    status: str
    minimum_accuracy_target: float
    minimum_shared_tasks: int
    pair_assessments: tuple[PairwiseJudgeAssessment, ...]
    alarm_pairs: tuple[tuple[str, str, str], ...]
    identity_warnings: tuple[tuple[str, str, str], ...] = ()
    no_alarm_establishes_correctness: bool = False
    can_identify_faulty_judge: bool = False
    bound_identity_required: bool = True
    method: str = "PAIRWISE_LOGICAL_DISAGREEMENT_BOUND_V1"


class JudgeHealthMonitor:
    """Conservative no-ground-truth logical-consistency alarm.

    For two judges evaluated on the same Q single-label tasks, if each is at
    least accuracy `a` against the same unknown answer key, their number of
    disagreements cannot exceed 2*(1-a)*Q. Exceeding that bound proves that both
    cannot simultaneously satisfy the target.

    It cannot prove correctness or identify the faulty judge. Bound identity
    prevents arbitrary aliases/self-reported model names from being treated as
    independent monitored judges. Same exact deployment paths are not counted as
    a distinct pair; same foundation lineage remains analyzable but is warned as
    correlated identity evidence.
    """

    def __init__(
        self,
        *,
        minimum_accuracy_target: float,
        minimum_shared_tasks: int = 20,
        require_bound_identity: bool = True,
    ) -> None:
        if not 0.5 <= minimum_accuracy_target <= 1.0:
            raise ValueError("minimum_accuracy_target must be between 0.5 and 1.0")
        if minimum_shared_tasks < 1:
            raise ValueError("minimum_shared_tasks must be >= 1")
        self.minimum_accuracy_target = float(minimum_accuracy_target)
        self.minimum_shared_tasks = int(minimum_shared_tasks)
        self.require_bound_identity = bool(require_bound_identity)

    def _normalize(
        self,
        observations: Iterable[JudgeObservation],
    ) -> tuple[dict[tuple[str, str, str], str], dict[str, JudgeIdentityBinding]]:
        normalized: dict[tuple[str, str, str], str] = {}
        identities: dict[str, JudgeIdentityBinding] = {}
        for observation in observations:
            observation.validate(require_bound_identity=self.require_bound_identity)
            key = (
                observation.dimension.strip(),
                observation.task_id.strip(),
                observation.judge_id.strip(),
            )
            label = observation.label.strip()
            existing = normalized.get(key)
            if existing is not None and existing != label:
                raise ValueError(
                    "conflicting retained judge observations for the same dimension/task/judge"
                )
            normalized[key] = label
            if observation.identity is not None:
                previous = identities.get(observation.judge_id)
                if previous is not None and previous != observation.identity:
                    raise ValueError("conflicting platform-bound identity for judge_id")
                identities[observation.judge_id] = observation.identity
        return normalized, identities

    @staticmethod
    def _identity_correlation(
        identity_a: JudgeIdentityBinding | None,
        identity_b: JudgeIdentityBinding | None,
    ) -> str:
        if identity_a is None or identity_b is None:
            return "UNBOUND_IDENTITY"
        if identity_a.runtime_path == identity_b.runtime_path:
            return "SAME_DEPLOYMENT_PATH"
        if identity_a.foundation_lineage == identity_b.foundation_lineage:
            return "SAME_FOUNDATION_LINEAGE"
        return "DISTINCT_DECLARED_LINEAGE"

    def evaluate(self, observations: Iterable[JudgeObservation]) -> JudgeHealthReport:
        normalized, identities = self._normalize(observations)
        by_dimension: dict[str, dict[str, dict[str, str]]] = {}
        for (dimension, task_id, judge_id), label in normalized.items():
            by_dimension.setdefault(dimension, {}).setdefault(judge_id, {})[task_id] = label

        assessments: list[PairwiseJudgeAssessment] = []
        alarm_pairs: list[tuple[str, str, str]] = []
        identity_warnings: list[tuple[str, str, str]] = []

        for dimension in sorted(by_dimension):
            judge_map = by_dimension[dimension]
            for judge_a, judge_b in combinations(sorted(judge_map), 2):
                correlation = self._identity_correlation(
                    identities.get(judge_a), identities.get(judge_b)
                )
                if correlation == "SAME_DEPLOYMENT_PATH":
                    identity_warnings.append((dimension, judge_a, "same deployment path as " + judge_b))
                    # Aliasing one runtime path as two judges must not create
                    # ensemble-health evidence.
                    continue
                if correlation == "SAME_FOUNDATION_LINEAGE":
                    identity_warnings.append((dimension, judge_a, "same foundation lineage as " + judge_b))
                elif correlation == "UNBOUND_IDENTITY":
                    identity_warnings.append((dimension, judge_a, "unbound identity pair with " + judge_b))

                tasks_a = judge_map[judge_a]
                tasks_b = judge_map[judge_b]
                shared = sorted(set(tasks_a).intersection(tasks_b))
                q = len(shared)
                if q < self.minimum_shared_tasks:
                    continue
                disagreements = sum(1 for task_id in shared if tasks_a[task_id] != tasks_b[task_id])
                allowed = floor((2.0 * (1.0 - self.minimum_accuracy_target) * q) + 1e-12)
                alarm = disagreements > allowed
                assessment = PairwiseJudgeAssessment(
                    dimension=dimension,
                    judge_a=judge_a,
                    judge_b=judge_b,
                    shared_tasks=q,
                    disagreements=disagreements,
                    disagreement_rate=disagreements / q,
                    max_disagreements_if_both_meet_target=allowed,
                    alarm=alarm,
                    identity_correlation=correlation,
                )
                assessments.append(assessment)
                if alarm:
                    alarm_pairs.append((dimension, judge_a, judge_b))

        if not assessments:
            status = "INSUFFICIENT_DATA"
        elif alarm_pairs:
            status = "LOGICALLY_INCONSISTENT_WITH_QUALIFICATION_TARGET"
        else:
            status = "NO_LOGICAL_ALARM"

        return JudgeHealthReport(
            status=status,
            minimum_accuracy_target=self.minimum_accuracy_target,
            minimum_shared_tasks=self.minimum_shared_tasks,
            pair_assessments=tuple(assessments),
            alarm_pairs=tuple(alarm_pairs),
            identity_warnings=tuple(identity_warnings),
            bound_identity_required=self.require_bound_identity,
        )
