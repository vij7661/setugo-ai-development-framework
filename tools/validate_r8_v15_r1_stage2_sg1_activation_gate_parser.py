"""Offline deterministic validation of the SG-1 activation review parser contract."""
from __future__ import annotations

import re
import argparse
from pathlib import Path


WORKFLOW = Path(".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml")
REVIEW_002 = Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt")


def clean_none_section(text: str) -> bool:
    return re.fullmatch(r"(?i:none\.?)", text.strip()) is not None


def parse_review_contract(text: str) -> dict:
    headings=list(re.finditer(r"(?m)^([A-H])\.\s+[^\r\n]*$", text))
    if len(headings) != 8 or [m.group(1) for m in headings] != list("ABCDEFGH"):
        raise ValueError("review must contain exactly one ordered A-H section")
    sections={}
    for index, match in enumerate(headings):
        end=headings[index+1].start() if index+1 < len(headings) else len(text)
        sections[match.group(1)]=text[match.end():end].strip()
    if sections["A"] != "BOUNDED_PASS":
        raise ValueError("disposition")
    if not clean_none_section(sections["C"]):
        raise ValueError("critical")
    if not clean_none_section(sections["D"]):
        raise ValueError("high")
    if len(re.findall(r"(?mi)^Stage2 SG-1 may be explicitly activated by user:\s*YES\.?\s*$", sections["H"])) != 1:
        raise ValueError("activation")
    if re.search(r"(?mi)^Stage2 SG-1 may be explicitly activated by user:\s*NO\.?\s*$", text):
        raise ValueError("contradictory activation")
    if len(re.findall(r"(?mi)^Broader Stage2 semantic authority granted:\s*NO\.?\s*$", sections["H"])) != 1:
        raise ValueError("authority")
    if re.search(r"(?mi)^Broader Stage2 semantic authority granted:\s*YES\.?\s*$", text):
        raise ValueError("broader authority")
    outside_cd=text[:headings[2].start()] + text[headings[4].start():]
    if re.search(r"(?mi)^(?:CRITICAL|HIGH)\s*:", outside_cd):
        raise ValueError("finding outside section")
    return sections


def review(disposition="BOUNDED_PASS", c="NONE.", d="NONE.", h_extra=""):
    return f"""A. OVERALL_DISPOSITION\n{disposition}\nB. EXACT_SG1_PROPOSAL_IDENTITY\nidentity\nC. CRITICAL_FINDINGS\n{c}\nD. HIGH_FINDINGS\n{d}\nE. MEDIUM_LOW_FINDINGS\nNone.\nF. SG1_PROTOCOL_ASSESSMENT\nassessment\nG. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY\nboundary\nH. FINAL_GATE\nStage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\n{h_extra}"""


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--review", type=Path)
    args=parser.parse_args()
    source = WORKFLOW.read_text(encoding="utf-8")
    assert 'EXPECTED_REVIEW_PATH="governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-003.txt"' in source
    assert 're.fullmatch(r"(?i:none\\.?)", text.strip())' in source
    assert "review must contain exactly one ordered A-H section" in source

    accepted = ["None", "None.", "NONE", "NONE.", "nOnE", "nOnE."]
    rejected = ["NONE..", "NO FINDINGS", "0", "PASS", "", "None. extra"]
    for value in accepted:
        assert clean_none_section(value), value
    for value in rejected:
        assert not clean_none_section(value), value
    accepted_document = review()
    parse_review_contract(accepted_document)
    punctuated_document = accepted_document.replace("activated by user: YES\n", "activated by user: YES.\n").replace("authority granted: NO\n", "authority granted: NO.\n")
    parse_review_contract(punctuated_document)
    parse_review_contract(REVIEW_002.read_text(encoding="utf-8"))
    if args.review:
        parse_review_contract(args.review.read_text(encoding="utf-8"))
    rejected_documents = [
        accepted_document.replace("A. OVERALL_DISPOSITION", "A. OVERALL_DISPOSITION\nA. DUPLICATE", 1),
        accepted_document.replace("C. CRITICAL_FINDINGS", "C. CRITICAL_FINDINGS\nC. DUPLICATE", 1),
        accepted_document.replace("D. HIGH_FINDINGS", "D. HIGH_FINDINGS\nD. DUPLICATE", 1),
        accepted_document.replace("H. FINAL_GATE", "H. FINAL_GATE\nH. DUPLICATE", 1),
        review(h_extra="C. CRITICAL_FINDINGS\nCRITICAL: hidden fatal issue"),
        review(h_extra="D. HIGH_FINDINGS\nHIGH: hidden high issue"),
        review(h_extra="Stage2 SG-1 may be explicitly activated by user: NO"),
        review(h_extra="Broader Stage2 semantic authority granted: YES"),
        accepted_document.replace("A. OVERALL_DISPOSITION", "A. OVERALL_DISPOSITION\nA. OVERALL_DISPOSITION", 1),
        accepted_document.replace("H. FINAL_GATE", "H. FINAL_GATE\nH. FINAL_GATE", 1),
        accepted_document.replace("activated by user: YES", "activated by user: YES..", 1),
        accepted_document.replace("authority granted: NO", "authority granted: NO..", 1),
        accepted_document + "\nA. EXTRA_SECTION\ntext",
        accepted_document.replace("B. EXACT_SG1_PROPOSAL_IDENTITY", "D. REORDERED\ntext", 1),
    ]
    for malformed in rejected_documents:
        try:
            parse_review_contract(malformed)
        except ValueError:
            continue
        raise AssertionError("malformed review accepted")
    print("SG1_ACTIVATION_GATE_REVIEW_PARSER_VALIDATION_PASS")


if __name__ == "__main__":
    main()
