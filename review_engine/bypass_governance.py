from __future__ import annotations

import re
from collections.abc import Callable
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
SHA40_RE = re.compile(r"[0-9a-f]{40}")
PLACEHOLDER_WORDS = frozenset({"todo", "tbd", "placeholder", "fake", "unknown", "example"})
EvidenceVerifier = Callable[[str], bool]


def _reject_placeholder(value: str, field_name: str) -> None:
    lowered = value.lower()
    if any(word in lowered for word in PLACEHOLDER_WORDS):
        raise ValueError(f"{field_name} cannot be placeholder evidence")


def _validate_evidence_ref(field_name: str, value: str | None) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty evidence reference")
    _reject_placeholder(value, field_name)

    if field_name == "first_failure_ref":
        if not re.fullmatch(r"github-actions:\d+/job/\d+@[0-9a-f]{40}", value):
            raise ValueError("first_failure_ref must bind workflow run, job and exact commit")
        return
    if field_name == "repair_ref":
        if not re.fullmatch(r"commit:[0-9a-f]{40}:.+", value):
            raise ValueError("repair_ref must bind an exact commit and production path")
        return
    if field_name == "regression_ref":
        if not re.fullmatch(r".+@[0-9a-f]{40}", value):
            raise ValueError("regression_ref must bind a regression artifact to an exact commit")
        return
    if field_name == "full_suite_ref":
        if "SUCCESS" not in value or not SHA40_RE.search(value) or not re.search(r"\d{5,}", value):
            raise ValueError("full_suite_ref must identify successful CI and an exact commit")
        return
    if field_name == "independent_review_ref":
        if not re.fullmatch(r"platform-review:[A-Za-z0-9._-]+@[0-9a-f]{40}", value):
            raise ValueError("independent_review_ref must bind a platform review to the exact candidate")
        return
    raise ValueError(f"unknown evidence-reference field: {field_name}")


@dataclass(frozen=True)
class BypassRecord:
    """Evidence-bearing lifecycle for one discovered governance bypass.

    This is process state, never an exception that permits the bypass. A bypass
    remains non-closed until the required evidence references exist. Authority-
    bearing production code must not contain a debug/test/legacy escape route
    that makes the bypass admissible.

    Reference-shape validation prevents placeholder strings from advancing the
    lifecycle. For authority-bearing findings, reaching INDEPENDENTLY_REVIEWED or
    CLOSED additionally requires a platform-supplied evidence resolver callback;
    the record never treats its own strings as proof that referenced evidence
    actually exists.
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

        for field_name in (
            "first_failure_ref",
            "repair_ref",
            "regression_ref",
            "full_suite_ref",
            "independent_review_ref",
        ):
            _validate_evidence_ref(field_name, getattr(self, field_name))

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

    def _verify_authority_evidence(self, evidence_verifier: EvidenceVerifier | None) -> None:
        if not self.independent_review_required:
            return
        if evidence_verifier is None:
            raise ValueError("platform evidence verifier required for authority-bound bypass review/closure")
        refs = (
            self.first_failure_ref,
            self.repair_ref,
            self.regression_ref,
            self.full_suite_ref,
            self.independent_review_ref,
        )
        for ref in refs:
            if not ref or not evidence_verifier(ref):
                raise ValueError(f"platform evidence verifier rejected reference: {ref!r}")

    def advance(
        self,
        next_status: str,
        *,
        evidence_verifier: EvidenceVerifier | None = None,
        **evidence: str | bool | None,
    ) -> "BypassRecord":
        """Advance exactly one lifecycle edge; skipping or reopening is forbidden."""
        if next_status not in BYPASS_STATUSES:
            raise ValueError("invalid bypass status")
        current_index = BYPASS_STATUSES.index(self.status)
        next_index = BYPASS_STATUSES.index(next_status)
        if next_index != current_index + 1:
            raise ValueError("bypass lifecycle transitions must advance exactly one stage")
        updated = replace(self, status=next_status, **evidence)
        updated.validate()
        if next_status in {"INDEPENDENTLY_REVIEWED", "CLOSED"}:
            updated._verify_authority_evidence(evidence_verifier)
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
