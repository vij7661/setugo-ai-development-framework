from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

STRATEGIES = {"R1_ONLY", "ALWAYS_THREE", "CONDITIONAL"}


@dataclass(frozen=True)
class EfficiencyCase:
    case_id: str
    strategy: str
    false_green: bool
    true_material_defects_found: int
    reviewer_calls: int
    prompt_tokens: int
    completion_tokens: int
    cost_microunits: int
    latency_ms: int
    price_version: str

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def validate_case(case: EfficiencyCase) -> None:
    if not case.case_id:
        raise ValueError("case_id required")
    if case.strategy not in STRATEGIES:
        raise ValueError("invalid strategy")
    for name in (
        "true_material_defects_found",
        "reviewer_calls",
        "prompt_tokens",
        "completion_tokens",
        "cost_microunits",
        "latency_ms",
    ):
        value = getattr(case, name)
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be non-negative integer")
    if not case.price_version:
        raise ValueError("price_version required")


def summarize(cases: Iterable[EfficiencyCase]) -> dict[str, dict[str, float | int | str]]:
    grouped: dict[str, list[EfficiencyCase]] = {s: [] for s in STRATEGIES}
    price_versions: set[str] = set()
    for case in cases:
        validate_case(case)
        grouped[case.strategy].append(case)
        price_versions.add(case.price_version)

    if len(price_versions) > 1:
        raise ValueError("mixed price versions cannot support direct monetary comparison")

    result: dict[str, dict[str, float | int | str]] = {}
    for strategy, rows in grouped.items():
        if not rows:
            continue
        n = len(rows)
        result[strategy] = {
            "case_count": n,
            "false_green_rate": sum(1 for r in rows if r.false_green) / n,
            "true_material_defects_found": sum(r.true_material_defects_found for r in rows),
            "avg_reviewer_calls": sum(r.reviewer_calls for r in rows) / n,
            "avg_tokens": sum(r.total_tokens for r in rows) / n,
            "avg_cost_microunits": sum(r.cost_microunits for r in rows) / n,
            "avg_latency_ms": sum(r.latency_ms for r in rows) / n,
            "price_version": rows[0].price_version,
        }
    return result


def compare_conditional(summary: dict[str, dict[str, float | int | str]]) -> dict[str, float | bool]:
    if "CONDITIONAL" not in summary or "R1_ONLY" not in summary or "ALWAYS_THREE" not in summary:
        raise ValueError("all three strategies required for comparison")

    cond = summary["CONDITIONAL"]
    r1 = summary["R1_ONLY"]
    all3 = summary["ALWAYS_THREE"]

    cond_fg = float(cond["false_green_rate"])
    r1_fg = float(r1["false_green_rate"])
    all3_fg = float(all3["false_green_rate"])
    safety_floor = min(r1_fg, all3_fg)

    extra_defects = int(cond["true_material_defects_found"]) - int(r1["true_material_defects_found"])
    extra_cost = float(cond["avg_cost_microunits"]) - float(r1["avg_cost_microunits"])
    cost_per_extra_defect = extra_cost / extra_defects if extra_defects > 0 else float("inf")

    return {
        "conditional_cheaper_than_always_three": float(cond["avg_cost_microunits"]) < float(all3["avg_cost_microunits"]),
        "conditional_uses_fewer_tokens_than_always_three": float(cond["avg_tokens"]) < float(all3["avg_tokens"]),
        "conditional_not_worse_than_best_observed_false_green": cond_fg <= safety_floor,
        "conditional_false_efficiency": (
            float(cond["avg_cost_microunits"]) < float(all3["avg_cost_microunits"])
            and cond_fg > safety_floor
        ),
        "cost_per_additional_true_defect_microunits": cost_per_extra_defect,
    }
