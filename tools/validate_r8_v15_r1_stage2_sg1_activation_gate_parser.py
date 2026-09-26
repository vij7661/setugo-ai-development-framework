"""Offline deterministic validation of the SG-1 activation review parser contract."""
from __future__ import annotations

import argparse
from pathlib import Path
from r8_v15_r1_review_contract_parser import clean_none_section, parse_review_contract


WORKFLOW = Path(".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml")
REVIEW_002 = Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt")
REVIEW_003 = Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-003.txt")
REVIEW_004 = Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-004.txt")


def review(disposition="BOUNDED_PASS", c="NONE.", d="NONE.", h_extra=""):
    return f"""A. OVERALL_DISPOSITION\n{disposition}\nB. EXACT_SG1_PROPOSAL_IDENTITY\nidentity\nC. CRITICAL_FINDINGS\n{c}\nD. HIGH_FINDINGS\n{d}\nE. MEDIUM_LOW_FINDINGS\nNone.\nF. SG1_PROTOCOL_ASSESSMENT\nassessment\nG. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY\nboundary\nH. FINAL_GATE\nStage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\n{h_extra}"""


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--review", type=Path)
    args=parser.parse_args()
    source = WORKFLOW.read_text(encoding="utf-8")
    assert 'from r8_v15_r1_review_contract_parser import parse_review_contract' in source
    assert Path("tools/r8_v15_r1_review_contract_parser.py").exists()

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
    parse_review_contract(REVIEW_003.read_text(encoding="utf-8"))
    parse_review_contract(REVIEW_004.read_text(encoding="utf-8"))
    bullet_document = accepted_document.replace("Stage2 SG-1 may be explicitly activated by user: YES", "- Stage2 SG-1 may be explicitly activated by user: YES.").replace("Broader Stage2 semantic authority granted: NO", "- Broader Stage2 semantic authority granted: NO.")
    parse_review_contract(bullet_document)
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
        review(h_extra="- Stage2 SG-1 may be explicitly activated by user: NO."),
        review(h_extra="- Broader Stage2 semantic authority granted: YES."),
        review(h_extra="- HIGH FINDING: hidden high issue"),
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
