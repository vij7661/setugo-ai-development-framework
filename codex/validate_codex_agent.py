from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
SKILL = ROOT / "skills" / "codex-execution" / "SKILL.md"

REQUIRED_AGENTS = (
    "Codex is a governed implementation/execution agent",
    "exact current HEAD SHA",
    "repository/activity timestamps",
    "Do not resume from chat memory alone",
    "Goal",
    "Affected components",
    "Constraints",
    "Acceptance criteria",
    "Tests/validation",
    "Forbidden changes",
    "skills/failure-triage/SKILL.md",
    "REQUIREMENT UNRESOLVED",
    "A previously green SHA does not validate a different SHA",
    "PASS — MANUAL QA REQUIRED",
    "BLOCKED — REQUIREMENT DECISION REQUIRED",
    "Green CI is evidence. It is not merge/release/deploy/completion authority",
)

REQUIRED_SKILL = (
    "Codex is the implementation/execution layer",
    "repository/activity timestamps",
    "Do not rely on chat memory alone",
    "exact HEAD SHA",
    "six-field task contract",
    "Affected components",
    "Acceptance criteria",
    "Forbidden changes",
    "skills/failure-triage/SKILL.md",
    "REQUIREMENT UNRESOLVED",
    "Old green CI cannot validate a new head",
    "PASS — MANUAL QA REQUIRED",
    "BLOCKED — REQUIREMENT DECISION REQUIRED",
    "Codex must not self-authorize merge, release, deploy",
)

FORBIDDEN_AUTHORITY_PATTERNS = (
    r"\bCodex\s+(?:may|can|should|is authorized to)\s+merge\b",
    r"\bCodex\s+(?:may|can|should|is authorized to)\s+release\b",
    r"\bCodex\s+(?:may|can|should|is authorized to)\s+deploy\b",
    r"\bCodex\s+(?:may|can|should|is authorized to)\s+promote\s+to\s+production\b",
    r"\bCodex\s+(?:may|can|should|is authorized to)\s+declare\s+completion\b",
)


def _missing(text: str, required: tuple[str, ...]) -> list[str]:
    return [clause for clause in required if clause not in text]


def validate_texts(agents_text: str, skill_text: str) -> list[str]:
    errors: list[str] = []

    for clause in _missing(agents_text, REQUIRED_AGENTS):
        errors.append(f"AGENTS.md missing mandatory clause: {clause}")

    for clause in _missing(skill_text, REQUIRED_SKILL):
        errors.append(f"codex-execution skill missing mandatory clause: {clause}")

    combined = f"{agents_text}\n{skill_text}"
    for pattern in FORBIDDEN_AUTHORITY_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            errors.append(f"terminal authority grant detected: {pattern}")

    if "skills/failure-triage/SKILL.md" not in agents_text or "skills/failure-triage/SKILL.md" not in skill_text:
        errors.append("failure-triage must be referenced from both Codex governance surfaces")

    if "python codex/validate_codex_agent.py" not in agents_text:
        errors.append("AGENTS.md must require the deterministic Codex validator")

    return errors


def validate_repository(root: Path = ROOT) -> list[str]:
    agents = root / "AGENTS.md"
    skill = root / "skills" / "codex-execution" / "SKILL.md"

    missing_files = [str(path.relative_to(root)) for path in (agents, skill) if not path.is_file()]
    if missing_files:
        return [f"missing required file: {path}" for path in missing_files]

    return validate_texts(
        agents.read_text(encoding="utf-8"),
        skill.read_text(encoding="utf-8"),
    )


def main() -> int:
    errors = validate_repository()
    if errors:
        print("CODEX_GOVERNANCE_VALIDATION=FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("CODEX_GOVERNANCE_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
