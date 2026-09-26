"""Single fail-closed parser for the bounded R8 v15-r1 A-H review contract."""
from __future__ import annotations

import re
from pathlib import Path


def clean_none_section(text: str) -> bool:
    return re.fullmatch(r"(?i:none\.?)", text.strip()) is not None


STRUCTURED_FINDING = re.compile(
    r"(?mi)^[ \t]*(?:[-*][ \t]+)?(?:CRITICAL|HIGH)(?:[ \t]+FINDING)?"
    r"(?:[ \t]*(?::|[-\u2013\u2014])[ \t]*|[ \t]{2,})(?=\S).+$"
)


def parse_review_contract(text: str) -> dict[str, str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    headings = list(re.finditer(r"(?m)^([A-H])\.\s+[^\r\n]*$", text))
    if len(headings) != 8 or [m.group(1) for m in headings] != list("ABCDEFGH"):
        raise ValueError("review must contain exactly one ordered A-H section")
    sections: dict[str, str] = {}
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[match.group(1)] = text[match.end():end].strip()
    if sections["A"] != "BOUNDED_PASS":
        raise ValueError("disposition")
    if not clean_none_section(sections["C"]):
        raise ValueError("critical")
    if not clean_none_section(sections["D"]):
        raise ValueError("high")
    if len(re.findall(r"(?mi)^\s*(?:-\s*)?Stage2 SG-1 may be explicitly activated by user:\s*YES\.?\s*$", sections["H"])) != 1:
        raise ValueError("activation")
    if re.search(r"(?mi)^\s*(?:-\s*)?Stage2 SG-1 may be explicitly activated by user:\s*NO\.?\s*$", text):
        raise ValueError("contradictory activation")
    if len(re.findall(r"(?mi)^\s*(?:-\s*)?Broader Stage2 semantic authority granted:\s*NO\.?\s*$", sections["H"])) != 1:
        raise ValueError("authority")
    if re.search(r"(?mi)^\s*(?:-\s*)?Broader Stage2 semantic authority granted:\s*YES\.?\s*$", text):
        raise ValueError("broader authority")
    outside_cd = text[:headings[2].start()] + text[headings[4].start():]
    if STRUCTURED_FINDING.search(outside_cd):
        raise ValueError("finding outside section")
    return sections


def parse_review_file(path: Path) -> dict[str, str]:
    try:
        return parse_review_contract(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError("review is not valid UTF-8") from exc
