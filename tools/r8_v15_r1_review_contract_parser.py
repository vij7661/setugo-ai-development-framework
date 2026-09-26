"""Single fail-closed parser for the bounded R8 v15-r1 A-H review contract."""
from __future__ import annotations

import re
from pathlib import Path


def clean_none_section(text: str) -> bool:
    return re.fullmatch(r"(?i:none\.?)", text.strip()) is not None


# Outside C/D, reject a finding declaration whenever the first ASCII alphabetic
# token on a line is CRITICAL or HIGH. Prefix punctuation, bullets, numbering,
# blockquotes, checkboxes, and underscore-joined suffixes do not bypass this.
STRUCTURED_FINDING = re.compile(
    r"(?mi)^[^A-Za-z\r\n]*?(CRITICAL|HIGH)(?=[^A-Za-z]|$)"
)

ACTIVATION_PHRASE = "Stage2 SG-1 may be explicitly activated by user:"
AUTHORITY_PHRASE = "Broader Stage2 semantic authority granted:"

ACTIVATION_LINE = re.compile(
    r"(?i)^\s*(?:-\s*)?Stage2 SG-1 may be explicitly activated by user:\s*(YES|NO)\.?\s*$"
)
AUTHORITY_LINE = re.compile(
    r"(?i)^\s*(?:-\s*)?Broader Stage2 semantic authority granted:\s*(YES|NO)\.?\s*$"
)


def _controlled_declarations(text: str) -> tuple[list[str], list[str]]:
    """Return exact controlled declaration values; reject embedded/heading forms."""
    activation: list[str] = []
    authority: list[str] = []
    for line in text.splitlines():
        if re.search(re.escape(ACTIVATION_PHRASE), line, flags=re.IGNORECASE):
            match = ACTIVATION_LINE.fullmatch(line)
            if not match:
                raise ValueError("activation declaration placement")
            activation.append(match.group(1).upper())
        if re.search(re.escape(AUTHORITY_PHRASE), line, flags=re.IGNORECASE):
            match = AUTHORITY_LINE.fullmatch(line)
            if not match:
                raise ValueError("authority declaration placement")
            authority.append(match.group(1).upper())
    return activation, authority


def parse_review_contract(text: str) -> dict[str, str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    headings = list(re.finditer(r"(?m)^([A-H])\.\s+[^\r\n]*$", text))
    if len(headings) != 8 or [m.group(1) for m in headings] != list("ABCDEFGH"):
        raise ValueError("review must contain exactly one ordered A-H section")

    # C/D are load-bearing exact headings because their bodies must be clean NONE.
    if headings[2].group(0).strip() != "C. CRITICAL_FINDINGS":
        raise ValueError("critical heading")
    if headings[3].group(0).strip() != "D. HIGH_FINDINGS":
        raise ValueError("high heading")

    # No other heading may smuggle a Critical/High declaration.
    for index, match in enumerate(headings):
        if index in (2, 3):
            continue
        heading_line = match.group(0)
        if re.search(r"(?i)\b(?:CRITICAL|HIGH)(?=[^A-Za-z]|$)", heading_line):
            raise ValueError("finding embedded in heading")

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

    # Controlled activation/authority phrases are allowed only as exact standalone
    # declarations. Heading-line/prose embedding is fail-closed.
    activation, authority = _controlled_declarations(text)
    if activation != ["YES"]:
        raise ValueError("activation")
    if authority != ["NO"]:
        raise ValueError("authority")

    # Required declarations must actually live in H.
    if len(ACTIVATION_LINE.findall(sections["H"])) != 1:
        raise ValueError("activation section")
    if len(AUTHORITY_LINE.findall(sections["H"])) != 1:
        raise ValueError("authority section")

    outside_cd = text[:headings[2].start()] + text[headings[4].start():]
    if STRUCTURED_FINDING.search(outside_cd):
        raise ValueError("finding outside section")
    return sections


def parse_review_file(path: Path) -> dict[str, str]:
    try:
        return parse_review_contract(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError("review is not valid UTF-8") from exc
