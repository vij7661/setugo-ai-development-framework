"""Structural A-J independent-review evidence parser (not an activation parser)."""
from __future__ import annotations

import re
from pathlib import Path

HEADINGS = (
    "A. OVERALL_DISPOSITION",
    "B. EXACT_CANDIDATE_IDENTITY",
    "C. CRITICAL_FINDINGS",
    "D. HIGH_FINDINGS",
    "E. MEDIUM_FINDINGS",
    "F. LOW_FINDINGS",
    "G. PERMANENT_INVARIANT_ASSESSMENT",
    "H. API_AND_REVIEWER_DELIVERY_ASSESSMENT",
    "I. REMEDIATION_PLAN",
    "J. FINAL_GATE",
)
DISPOSITIONS = frozenset({"BOUNDED_PASS", "CHANGES_REQUIRED", "INSUFFICIENT_EVIDENCE"})
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
FINAL_FIELDS = (
    "Frozen Q14 candidate eligible for bounded merge consideration",
    "Broader Stage2 semantic authority granted",
    "Runtime qualification granted",
    "Release/deployment/production authority granted",
    "Automatic six-slice cadence restoration",
)
FINDING_ID = re.compile(r"\*\*F-[0-9]+\*\*\s*$")


def _none(body: str) -> bool:
    return re.fullmatch(r"(?is)\s*NONE\.?\s*", body) is not None


def _validate_findings(body: str, severity: str) -> list[str]:
    if _none(body):
        return []
    matches = list(re.finditer(r"(?m)^\*\*(F-[0-9]+)(?: [^*\r\n]+)?\*\*\s*$", body))
    if not matches or body[:matches[0].start()].strip():
        raise ValueError(f"malformed {severity} findings")
    ids = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        block = body[match.end():end].strip()
        rows = {}
        for line in block.splitlines():
            parsed = re.fullmatch(r"\s*(\d+)\.\s+(.+?)\s*", line)
            if not parsed or int(parsed.group(1)) in rows:
                raise ValueError(f"malformed finding {match.group(1)}")
            rows[int(parsed.group(1))] = parsed.group(2)
        if set(rows) != set(range(2, 12)) or rows[2] != severity:
            raise ValueError(f"malformed finding {match.group(1)}")
        ids.append(match.group(1))
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate finding id")
    return ids


def parse_independent_review(text: str) -> dict:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    headings = list(re.finditer(r"(?m)^([A-J])\. [^\n]+$", normalized))
    if len(headings) != 10 or [m.group(0) for m in headings] != list(HEADINGS):
        raise ValueError("review must contain exactly one ordered A-J contract")
    sections = {}
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(normalized)
        sections[match.group(1)] = normalized[match.end():end].strip()
    disposition = sections["A"]
    if disposition not in DISPOSITIONS:
        raise ValueError("invalid disposition")
    if not sections["B"] or not sections["G"] or not sections["H"] or not sections["I"]:
        raise ValueError("required review section is empty")
    findings = {}
    seen = set()
    for letter, severity in zip("CDEF", SEVERITIES):
        findings[severity] = _validate_findings(sections[letter], severity)
        if seen.intersection(findings[severity]):
            raise ValueError("finding id repeated across severities")
        seen.update(findings[severity])
    lines = [line.strip() for line in sections["J"].splitlines() if line.strip()]
    if len(lines) != 6:
        raise ValueError("final gate must contain exactly six fields")
    values = {}
    for expected, line in zip(FINAL_FIELDS, lines[:5]):
        match = re.fullmatch(rf"- {re.escape(expected)}:\s*(YES|NO)", line)
        if not match:
            raise ValueError("invalid final gate field")
        values[expected] = match.group(1)
    if lines[5] != "- Fallback-to-3 remains ACTIVE":
        raise ValueError("invalid fallback final gate field")
    return {"disposition": disposition, "sections": sections, "findings": findings, "final_gate": values}


def eligible_for_bounded_merge(parsed: dict, *, freeze_verified: bool = False) -> bool:
    return (
        freeze_verified
        and
        parsed.get("disposition") == "BOUNDED_PASS"
        and not any(parsed.get("findings", {}).values())
        and parsed.get("final_gate", {}).get(FINAL_FIELDS[0]) == "YES"
        and all(parsed.get("final_gate", {}).get(field) == "NO" for field in FINAL_FIELDS[1:])
    )


def parse_independent_review_file(path: Path) -> dict:
    try:
        return parse_independent_review(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError("review is not valid UTF-8") from exc
