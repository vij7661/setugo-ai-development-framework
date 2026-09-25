"""Offline deterministic validation of the SG-1 activation review parser contract."""
from __future__ import annotations

import re
from pathlib import Path


WORKFLOW = Path(".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml")


def clean_none_section(text: str) -> bool:
    return re.fullmatch(r"(?i:none\.?)", text.strip()) is not None


def main() -> None:
    source = WORKFLOW.read_text(encoding="utf-8")
    assert 'EXPECTED_REVIEW_PATH="governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt"' in source
    assert 're.fullmatch(r"(?i:none\\.?)", text.strip())' in source

    accepted = ["None", "None.", "NONE", "NONE.", "nOnE", "nOnE."]
    rejected = ["NONE..", "NO FINDINGS", "0", "PASS", "", "None. extra"]
    for value in accepted:
        assert clean_none_section(value), value
    for value in rejected:
        assert not clean_none_section(value), value
    print("SG1_ACTIVATION_GATE_REVIEW_PARSER_VALIDATION_PASS")


if __name__ == "__main__":
    main()
