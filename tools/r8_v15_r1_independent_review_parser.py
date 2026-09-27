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
FINAL_FIELDS_AFTER_CANDIDATE = (
    "Broader Stage2 semantic authority granted",
    "Runtime qualification granted",
    "Release/deployment/production authority granted",
    "Automatic six-slice cadence restoration",
)
FINDING_ID_TOKEN = r"[A-Z][A-Z0-9_-]*-[0-9]+"
SHA40 = r"[0-9a-f]{40}"
FINDING_CLASSIFICATIONS = frozenset({"api-contract", "code", "evidence", "governance-rule", "packaging", "runtime"})


def _none(body: str) -> bool:
    return re.fullmatch(r"(?is)\s*NONE\.?\s*", body) is not None


def _validate_findings(body: str, severity: str, *, allow_legacy_annotations: bool = False) -> list[str]:
    if _none(body):
        return []
    matches = list(re.finditer(rf"(?m)^\*\*({FINDING_ID_TOKEN})(?: [^*\r\n]+)?\*\*\s*$", body))
    if not matches or body[:matches[0].start()].strip():
        raise ValueError(f"malformed {severity} findings")
    ids = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        block = body[match.end():end].strip()
        rows = {}
        order = []
        for line in block.splitlines():
            parsed = re.fullmatch(r"\s*(\d+)\.\s+(.+?)\s*", line)
            if not parsed or int(parsed.group(1)) in rows:
                raise ValueError(f"malformed finding {match.group(1)}")
            number = int(parsed.group(1)); order.append(number); rows[number] = parsed.group(2)
        if order != list(range(2, 12)) or rows[2] != severity:
            raise ValueError(f"malformed finding {match.group(1)}")
        if not re.fullmatch(r"Candidate invalidated:\s*(YES|NO)", rows[9], re.I):
            raise ValueError(f"malformed finding {match.group(1)}")
        blocking_pattern = r"Merge/promotion blocking:\s*(YES|NO)(?:\s*\(.+\))?" if allow_legacy_annotations else r"Merge/promotion blocking:\s*(YES|NO)"
        if not re.fullmatch(blocking_pattern, rows[10], re.I):
            raise ValueError(f"malformed finding {match.group(1)}")
        classification = re.fullmatch(r"Classification:\s*(.+)", rows[11], re.I)
        if not classification:
            raise ValueError(f"malformed finding {match.group(1)}")
        classes = {item.strip().lower() for item in classification.group(1).split("/")}
        if not classes or not classes <= FINDING_CLASSIFICATIONS:
            raise ValueError(f"malformed finding {match.group(1)}")
        prefix_severity = {"C": "CRITICAL", "H": "HIGH", "M": "MEDIUM", "L": "LOW"}
        prefix = match.group(1).split("-", 1)[0]
        if prefix in prefix_severity and prefix_severity[prefix] != severity:
            raise ValueError(f"finding id/severity mismatch: {match.group(1)}")
        ids.append(match.group(1))
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate finding id")
    return ids


def _parse_identity(body: str, candidate_label: str) -> dict:
    patterns = (
        ("baseline", rf"- baseline:\s*({SHA40})"),
        ("candidate_commit", rf"- frozen {re.escape(candidate_label)} commit:\s*({SHA40})"),
        ("candidate_tree", rf"- frozen {re.escape(candidate_label)} tree:\s*({SHA40})"),
        ("changed_file_count", r"- changed-file count from baseline:\s*([0-9]+)"),
        ("packet_run_job", r"- packet-generation run/job:\s*([0-9]+)\s*/\s*([0-9]+)"),
        ("linux_run_job", r"- exact Linux validation run/job:\s*([0-9]+)\s*/\s*([0-9]+)"),
    )
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if len(lines) != len(patterns):
        raise ValueError("candidate identity must contain exactly six fields")
    identity = {"candidate_label": candidate_label}
    for line, (name, pattern) in zip(lines, patterns):
        match = re.fullmatch(pattern, line)
        if not match:
            raise ValueError(f"invalid candidate identity field: {name}")
        value = match.groups()
        identity[name] = int(value[0]) if name == "changed_file_count" else (value if len(value) == 2 else value[0])
    return identity


def parse_independent_review(text: str, *, candidate_label: str, allow_legacy_finding_annotations: bool = False) -> dict:
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
    identity = _parse_identity(sections["B"], candidate_label)
    findings = {}
    seen = set()
    for letter, severity in zip("CDEF", SEVERITIES):
        findings[severity] = _validate_findings(sections[letter], severity, allow_legacy_annotations=allow_legacy_finding_annotations)
        if seen.intersection(findings[severity]):
            raise ValueError("finding id repeated across severities")
        seen.update(findings[severity])
    lines = [line.strip() for line in sections["J"].splitlines() if line.strip()]
    if len(lines) != 6:
        raise ValueError("final gate must contain exactly six fields")
    values = {}
    final_fields = (f"Frozen {candidate_label} candidate eligible for bounded merge consideration",) + FINAL_FIELDS_AFTER_CANDIDATE
    for expected, line in zip(final_fields, lines[:5]):
        match = re.fullmatch(rf"- {re.escape(expected)}:\s*(YES|NO)\.?", line)
        if not match:
            raise ValueError("invalid final gate field")
        values[expected] = match.group(1)
    if not re.fullmatch(r"- Fallback-to-3 remains ACTIVE\.?", lines[5]):
        raise ValueError("invalid fallback final gate field")
    return {"disposition": disposition, "sections": sections, "identity": identity, "findings": findings, "final_gate": values, "candidate_gate_field": final_fields[0]}


def eligible_for_bounded_merge(parsed: dict, *, freeze_verified: bool = False) -> bool:
    return (
        freeze_verified
        and
        parsed.get("disposition") == "BOUNDED_PASS"
        and not any(parsed.get("findings", {}).values())
        and parsed.get("final_gate", {}).get(parsed.get("candidate_gate_field")) == "YES"
        and all(parsed.get("final_gate", {}).get(field) == "NO" for field in FINAL_FIELDS_AFTER_CANDIDATE)
    )


def parse_independent_review_file(path: Path, *, candidate_label: str, allow_legacy_finding_annotations: bool = False) -> dict:
    try:
        return parse_independent_review(path.read_text(encoding="utf-8"), candidate_label=candidate_label, allow_legacy_finding_annotations=allow_legacy_finding_annotations)
    except UnicodeDecodeError as exc:
        raise ValueError("review is not valid UTF-8") from exc
