from __future__ import annotations

import re
from dataclasses import dataclass

from .models import ReviewFinding


# Platform-owned safety budget. Reviewers may identify correction targets but
# cannot enlarge this capability. A future policy service may replace this
# centralized MVP constant; it must not become a model/user supplied parameter.
MAX_AUTOMATIC_EDITABLE_FRACTION = 0.80


class CorrectionScopeError(ValueError):
    """A material correction target cannot be bound to a safe automatic text scope."""


@dataclass(frozen=True)
class ScopedCorrectionAssessment:
    admissible: bool
    reason: str

    def as_dict(self) -> dict:
        return {"admissible": self.admissible, "reason": self.reason}


@dataclass(frozen=True)
class ScopedCorrectionPlan:
    """Platform-derived capability for replacing only exact localized claims.

    The plan is deliberately conservative. A model/reviewer finding does not gain
    arbitrary rewrite authority merely by naming a broad scope. Automatic
    correction is permitted only when every material target names one claim scope
    and supplies a unique exact text anchor in the frozen artifact. All text
    outside those anchors becomes immutable for this correction attempt.
    """

    original: str
    editable_ranges: tuple[tuple[int, int], ...]
    target_finding_ids: tuple[str, ...]
    anchors: tuple[str, ...]

    @property
    def editable_chars(self) -> int:
        return sum(end - start for start, end in self.editable_ranges)

    @property
    def editable_fraction(self) -> float:
        return self.editable_chars / len(self.original)

    def immutable_segments(self) -> tuple[str, ...]:
        segments: list[str] = []
        cursor = 0
        for start, end in self.editable_ranges:
            segments.append(self.original[cursor:start])
            cursor = end
        segments.append(self.original[cursor:])
        return tuple(segments)

    def as_dict(self) -> dict:
        return {
            "mode": "EXACT_CLAIM_ANCHOR_REPLACEMENT_V1",
            "target_finding_ids": list(self.target_finding_ids),
            "editable_ranges": [
                {"start": start, "end": end}
                for start, end in self.editable_ranges
            ],
            "anchors": list(self.anchors),
            "editable_chars": self.editable_chars,
            "artifact_chars": len(self.original),
            "editable_fraction": self.editable_fraction,
            "max_automatic_editable_fraction": MAX_AUTOMATIC_EDITABLE_FRACTION,
            "unaffected_content_must_be_preserved_exactly": True,
        }

    def assess(self, revised: str) -> ScopedCorrectionAssessment:
        if not isinstance(revised, str):
            return ScopedCorrectionAssessment(False, "revised artifact must be text")
        if revised == self.original:
            return ScopedCorrectionAssessment(False, "material review finding produced no artifact revision")

        # A revised artifact is admissible iff it can be constructed from the
        # frozen original by replacing only the editable ranges. The immutable
        # segments therefore have to survive verbatim, in order, with exact
        # prefix/suffix binding. Regex expresses that language directly while
        # escaping every immutable segment so model text cannot influence syntax.
        segments = self.immutable_segments()
        pattern_parts: list[str] = ["\\A", re.escape(segments[0])]
        for segment in segments[1:]:
            pattern_parts.extend([".*?", re.escape(segment)])
        pattern_parts.append("\\Z")
        pattern = "".join(pattern_parts)
        if re.match(pattern, revised, flags=re.DOTALL) is None:
            return ScopedCorrectionAssessment(
                False,
                "revision changed content outside the platform-authorized correction scope",
            )
        return ScopedCorrectionAssessment(True, "revision preserved all content outside authorized claim anchors")


def build_scoped_correction_plan(
    original: str,
    findings: tuple[ReviewFinding, ...],
) -> ScopedCorrectionPlan:
    if not isinstance(original, str) or not original:
        raise CorrectionScopeError("frozen artifact text required for scoped correction")
    if not findings:
        raise CorrectionScopeError("at least one material correction target is required")

    bound: list[tuple[int, int, str, str]] = []
    for finding in findings:
        finding.validate()
        scopes = finding.affected_scope
        if len(scopes) != 1 or not scopes[0].startswith("claim:"):
            raise CorrectionScopeError(
                f"finding {finding.finding_id} is not bound to one machine-localizable claim scope"
            )
        anchor = finding.first_invalid_claim
        if not isinstance(anchor, str) or not anchor:
            raise CorrectionScopeError(
                f"finding {finding.finding_id} lacks an exact first_invalid_claim anchor"
            )

        first = original.find(anchor)
        if first < 0:
            raise CorrectionScopeError(
                f"finding {finding.finding_id} anchor is absent from the frozen artifact"
            )
        if original.find(anchor, first + 1) >= 0:
            raise CorrectionScopeError(
                f"finding {finding.finding_id} anchor is ambiguous in the frozen artifact"
            )
        bound.append((first, first + len(anchor), finding.finding_id, anchor))

    bound.sort(key=lambda item: (item[0], item[1], item[2]))
    ranges: list[tuple[int, int]] = []
    anchors: list[str] = []
    finding_ids: list[str] = []
    for start, end, finding_id, anchor in bound:
        if ranges and start < ranges[-1][1]:
            if (start, end) == ranges[-1]:
                # Multiple retained findings may independently identify the same
                # exact claim. That does not enlarge the capability.
                finding_ids.append(finding_id)
                continue
            raise CorrectionScopeError("material correction anchors overlap and cannot be isolated safely")
        ranges.append((start, end))
        anchors.append(anchor)
        finding_ids.append(finding_id)

    editable_chars = sum(end - start for start, end in ranges)
    if editable_chars >= len(original):
        raise CorrectionScopeError(
            "automatic correction would authorize the entire artifact; human review is required"
        )
    editable_fraction = editable_chars / len(original)
    if editable_fraction > MAX_AUTOMATIC_EDITABLE_FRACTION:
        raise CorrectionScopeError(
            "automatic correction is not localized: editable scope exceeds the platform correction budget"
        )

    return ScopedCorrectionPlan(
        original=original,
        editable_ranges=tuple(ranges),
        target_finding_ids=tuple(finding_ids),
        anchors=tuple(anchors),
    )
