from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import floor
from typing import Iterable


@dataclass(frozen=True)
class JudgeObservation:
    """One platform-retained judge decision on a comparable evaluation item.

    `judge_id` should identify the qualified deployment/model path being
    monitored, not a self-reported runtime model label.
    """

    task_id: str
    judge_id: str
    label: str
    dimension: str = "GENERAL"

    def validate(self) -> None:
        for name in ("task_id", "judge_id", "label", "dimension"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"judge observation {name} required")


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


@dataclass(frozen=True)
class JudgeHealthReport:
    status: str
    minimum_accuracy_target: float
    minimum_shared_tasks: int
    pair_assessments: tuple[PairwiseJudgeAssessment, ...]
    alarm_pairs: tuple[tuple[str, str, str], ...]
    no_alarm_establishes_correctness: bool = False
    can_identify_faulty_judge: bool = False
    method: str = "PAIRWISE_LOGICAL_DISAGREEMENT_BOUND_V1"


class JudgeHealthMonitor:
    """Conservative no-ground-truth logical-consistency alarm.

    For two judges evaluated on the same Q single-label tasks, if each is at
    least accuracy `a` against the same unknown answer key, their number of
    disagreements cannot exceed 2*(1-a)*Q. Every disagreement implies at least
    one of the two is wrong, so exceeding that bound proves that both cannot
    simultaneously satisfy the target.

    This is intentionally a sound subset of richer no-knowledge/LP approaches.
    It cannot prove correctness, cannot identify which judge is wrong, and
    assumes observations are authentic and tasks share a single-label ground
    truth even though that ground truth is unknown.
    """

    def __init__(self, *, minimum_accuracy_target: float, minimum_shared_tasks: int = 20) -> None:
        if not 0.5 <= minimum_accuracy_target <= 1.0:
            raise ValueError("minimum_accuracy_target must be between 0.5 and 1.0")
        if minimum_shared_tasks < 1:
            raise ValueError("minimum_shared_tasks must be >= 1")
        self.minimum_accuracy_target = float(minimum_accuracy_target)
        self.minimum_shared_tasks = int(minimum_shared_tasks)

    @staticmethod
    def _normalize(observations: Iterable[JudgeObservation]) -> dict[tuple[str, str, str], str]:
        normalized: dict[tuple[str, str, str], str] = {}
        for observation in observations:
            observation.validate()
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
        return normalized

    def evaluate(self, observations: Iterable[JudgeObservation]) -> JudgeHealthReport:
        normalized = self._normalize(observations)
        by_dimension: dict[str, dict[str, dict[str, str]]] = {}
        for (dimension, task_id, judge_id), label in normalized.items():
            by_dimension.setdefault(dimension, {}).setdefault(judge_id, {})[task_id] = label

        assessments: list[PairwiseJudgeAssessment] = []
        alarm_pairs: list[tuple[str, str, str]] = []

        for dimension in sorted(by_dimension):
            judge_map = by_dimension[dimension]
            for judge_a, judge_b in combinations(sorted(judge_map), 2):
                tasks_a = judge_map[judge_a]
                tasks_b = judge_map[judge_b]
                shared = sorted(set(tasks_a).intersection(tasks_b))
                q = len(shared)
                if q < self.minimum_shared_tasks:
                    continue
                disagreements = sum(1 for task_id in shared if tasks_a[task_id] != tasks_b[task_id])
                # Floating epsilon avoids floor artifacts such as 1.999999999.
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
                )
                assessments.append(assessment)
                if alarm:
                    alarm_pairs.append((dimension, judge_a, judge_b))

        if not assessments:
            status = "INSUFFICIENT_DATA"
        elif alarm_pairs:
            status = "LOGICALLY_INCONSISTENT_WITH_QUALIFICATION_TARGET"
        else:
            # Deliberately not called HEALTHY/ALIGNED. Agreement cannot establish
            # correctness when the answer key is unknown.
            status = "NO_LOGICAL_ALARM"

        return JudgeHealthReport(
            status=status,
            minimum_accuracy_target=self.minimum_accuracy_target,
            minimum_shared_tasks=self.minimum_shared_tasks,
            pair_assessments=tuple(assessments),
            alarm_pairs=tuple(alarm_pairs),
        )
