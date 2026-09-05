from __future__ import annotations

from dataclasses import dataclass
from math import log
from typing import Iterable


@dataclass(frozen=True)
class SemanticProbePolicy:
    max_normalized_entropy: float
    max_refusal_ratio: float
    policy_version: str
    min_samples: int = 3


@dataclass(frozen=True)
class SemanticProbeResult:
    status: str
    normalized_entropy: float | None
    refusal_ratio: float
    semantic_cluster_count: int
    sample_count: int
    reasons: tuple[str, ...]
    policy_version: str


_VALID_STATUSES = {"STABLE", "UNCERTAIN", "REFUSAL_DOMINANT", "INSUFFICIENT"}


def _validate_policy(policy: SemanticProbePolicy) -> None:
    if not policy.policy_version:
        raise ValueError("semantic probe policy_version is required")
    if not 0.0 <= policy.max_normalized_entropy <= 1.0:
        raise ValueError("max_normalized_entropy must be in [0, 1]")
    if not 0.0 <= policy.max_refusal_ratio <= 1.0:
        raise ValueError("max_refusal_ratio must be in [0, 1]")
    if not isinstance(policy.min_samples, int) or policy.min_samples < 2:
        raise ValueError("min_samples must be an integer >= 2")


def analyze_semantic_samples(
    cluster_ids: Iterable[str],
    refusal_flags: Iterable[bool],
    policy: SemanticProbePolicy,
) -> SemanticProbeResult:
    """Analyze pre-clustered black-box generations.

    `cluster_ids` represent context-sensitive semantic equivalence classes produced
    by a separately governed clustering step. This function deliberately does not
    infer semantic equivalence from lexical similarity. Insufficient sampling is
    not reported as stability and must route toward additional review.
    """

    _validate_policy(policy)
    clusters = list(cluster_ids)
    refusals = list(refusal_flags)
    if not clusters:
        raise ValueError("at least one semantic sample is required")
    if len(clusters) != len(refusals):
        raise ValueError("cluster_ids and refusal_flags must have equal length")
    if any(not isinstance(c, str) or not c.strip() for c in clusters):
        raise ValueError("every semantic cluster id must be a non-empty string")
    if any(not isinstance(r, bool) for r in refusals):
        raise ValueError("every refusal flag must be boolean")

    n = len(clusters)
    refusal_ratio = sum(refusals) / n

    counts: dict[str, int] = {}
    for cid, refused in zip(clusters, refusals):
        if refused:
            continue
        counts[cid] = counts.get(cid, 0) + 1

    if n < policy.min_samples:
        return SemanticProbeResult(
            status="INSUFFICIENT",
            normalized_entropy=None,
            refusal_ratio=refusal_ratio,
            semantic_cluster_count=len(counts),
            sample_count=n,
            reasons=("valid semantic sample count is below policy minimum",),
            policy_version=policy.policy_version,
        )

    non_refusal_n = sum(counts.values())
    if non_refusal_n <= 1 or len(counts) <= 1:
        normalized_entropy = 0.0
    else:
        probs = [count / non_refusal_n for count in counts.values()]
        entropy = -sum(p * log(p) for p in probs)
        max_entropy = log(len(counts))
        normalized_entropy = 0.0 if max_entropy == 0 else entropy / max_entropy

    reasons: list[str] = []
    if refusal_ratio > policy.max_refusal_ratio:
        status = "REFUSAL_DOMINANT"
        reasons.append("refusal ratio exceeds policy threshold")
    elif normalized_entropy > policy.max_normalized_entropy:
        status = "UNCERTAIN"
        reasons.append("semantic entropy exceeds policy threshold")
    else:
        status = "STABLE"
        reasons.append("semantic probe remains within policy thresholds")

    assert status in _VALID_STATUSES
    return SemanticProbeResult(
        status=status,
        normalized_entropy=normalized_entropy,
        refusal_ratio=refusal_ratio,
        semantic_cluster_count=len(counts),
        sample_count=n,
        reasons=tuple(reasons),
        policy_version=policy.policy_version,
    )
