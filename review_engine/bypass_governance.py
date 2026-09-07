from __future__ import annotations

from dataclasses import dataclass, replace


BYPASS_STATUSES = (
    "DISCOVERED",
    "PRESERVED",
    "MECHANISM_REPAIRED",
    "REGRESSION_FROZEN",
    "FULL_SUITE_GREEN",
    "INDEPENDENTLY_REVIEWED",
    "CLOSED",
)


@dataclass(frozen=True)
class BypassRecord:
    """Evidence-bearing lifecycle for one discovered governance bypass.

    This is process state, never an exception that permits the bypass. A bypass
    remains non-closed until the required evidence references exist. Authority-
    bearing production code must not contain a debug/test/legacy escape route
    that makes the bypass admissible.
    """

    bypass_id: str
    invariant: str
    status: str = "DISCOVERED"
    independent_review_required: bool = True
    first_failure_ref: str | None = None
    repair_ref: str | None = None
    regression_ref: str | None = None
    full_suite_ref: str | None = None
    independent_review_ref: str | None = None

    def validate(self) -> None:
        if not self.bypass_id.strip():
            raise ValueError("bypass_id required")
        if not self.invariant.strip():
            raise ValueError("bypass invariant required")
        if self.status not in BYPASS_STATUSES:
            raise ValueError("invalid bypass status")

        reached = BYPASS_STATUSES.index(self.status)
        required_by_stage = (
            ("PRESERVED", "first_failure_ref"),
            ("MECHANISM_REPAIRED", "repair_ref"),
            ("REGRESSION_FROZEN", "regression_ref"),
            ("FULL_SUITE_GREEN", "full_suite_ref"),
        )
        for stage, field_name in required_by_stage:
            if reached >= BYPASS_STATUSES.index(stage) and not getattr(self, field_name):
                raise ValueError(f"{field_name} required at status {self.status}")

        if reached >= BYPASS_STATUSES.index("INDEPENDENTLY_REVIEWED"):
            if self.independent_review_required and not self.independent_review_ref:
                raise ValueError("independent_review_ref required before independent-review status")

        if self.status == "CLOSED":
            if not self.full_suite_ref:
                raise ValueError("closed bypass requires full-suite evidence")
            if self.independent_review_required and not self.independent_review_ref:
                raise ValueError("closed bypass requires independent review evidence")

    def advance(self, next_status: str, **evidence: str | bool | None) -> "BypassRecord":
        """Advance exactly one lifecycle edge; skipping or reopening is forbidden."""
        if next_status not in BYPASS_STATUSES:
            raise ValueError("invalid bypass status")
        current_index = BYPASS_STATUSES.index(self.status)
        next_index = BYPASS_STATUSES.index(next_status)
        if next_index != current_index + 1:
            raise ValueError("bypass lifecycle transitions must advance exactly one stage")
        updated = replace(self, status=next_status, **evidence)
        updated.validate()
        return updated


def assert_no_bypass_exception(*, requested: bool, reason: str = "") -> None:
    """Hard fail for any attempted debug/test/legacy authority bypass.

    Callers may use this guard when wiring configuration surfaces. It deliberately
    provides no override token: if a production authority path asks to bypass a
    governance invariant, construction must fail rather than continue.
    """
    if requested:
        detail = f": {reason}" if reason else ""
        raise ValueError(f"governance bypass exceptions are forbidden{detail}")
