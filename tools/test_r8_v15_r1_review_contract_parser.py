"""Table-driven adversarial tests for the shared SG-1 review parser."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from r8_v15_r1_review_contract_parser import parse_review_contract  # noqa: E402


def doc(h="Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO"):
    return f"""A. OVERALL_DISPOSITION
BOUNDED_PASS
B. IDENTITY
proposal
C. CRITICAL_FINDINGS
NONE.
D. HIGH_FINDINGS
NONE.
E. MEDIUM_LOW_FINDINGS
None.
F. ASSESSMENT
pass
G. BOUNDARY
LOCAL
H. FINAL_GATE
{h}
"""


def rejects(text):
    try:
        parse_review_contract(text)
    except ValueError:
        return
    raise AssertionError("malformed review accepted")


def main():
    accepted = [
        doc(),
        doc("- Stage2 SG-1 may be explicitly activated by user: YES.\n- Broader Stage2 semantic authority granted: no."),
        doc().replace("NONE.", "nOnE", 1).replace("NONE.", "None", 1).replace("\n", "\r\n"),
        doc().replace(
            "E. MEDIUM_LOW_FINDINGS\nNone.",
            "E. MEDIUM_LOW_FINDINGS\nThe parser rejects CRITICAL: labels at structured line starts.",
        ),
    ]
    for case in accepted:
        parse_review_contract(case)

    bad_cases = (
        doc().replace("A. OVERALL_DISPOSITION", "A. OVERALL_DISPOSITION\nA. DUPLICATE", 1),
        doc().replace("C. CRITICAL_FINDINGS", "C. CRITICAL_FINDINGS\nC. DUPLICATE", 1),
        doc().replace("D. HIGH_FINDINGS", "D. HIGH_FINDINGS\nD. DUPLICATE", 1),
        doc().replace("H. FINAL_GATE", "H. FINAL_GATE\nH. DUPLICATE", 1),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nC. CRITICAL_FINDINGS\nCRITICAL: hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\n- HIGH FINDING: hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nCRITICAL — hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nHIGH - hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nCRITICAL:\nhidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nHIGH:\nhidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\n1. CRITICAL: hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\n1) HIGH hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\n• HIGH: hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\n[ ] HIGH hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\n> CRITICAL hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\n*** CRITICAL hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nCRITICAL_FINDING: hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nHIGH_FINDING: hidden"),
        doc().replace("C. CRITICAL_FINDINGS", "C. CRITICAL_FINDINGS CRITICAL: hidden"),
        doc().replace("D. HIGH_FINDINGS", "D. HIGH_FINDINGS HIGH: hidden"),
        doc().replace("A. OVERALL_DISPOSITION", "A. OVERALL_DISPOSITION CRITICAL: hidden"),
        doc().replace("B. IDENTITY", "B. IDENTITY HIGH: hidden"),
        doc().replace("E. MEDIUM_LOW_FINDINGS", "E. MEDIUM_LOW_FINDINGS CRITICAL: hidden"),
        doc().replace("F. ASSESSMENT", "F. ASSESSMENT HIGH: hidden"),
        doc().replace("G. BOUNDARY", "G. BOUNDARY CRITICAL: hidden"),
        doc().replace("H. FINAL_GATE", "H. FINAL_GATE HIGH: hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nStage2 SG-1 may be explicitly activated by user: NO\nBroader Stage2 semantic authority granted: NO"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nBroader Stage2 semantic authority granted: YES"),
        doc().replace("H. FINAL_GATE", "H. FINAL_GATE Stage2 SG-1 may be explicitly activated by user: NO"),
        doc().replace("H. FINAL_GATE", "H. FINAL_GATE Broader Stage2 semantic authority granted: YES"),
        doc().replace(
            "E. MEDIUM_LOW_FINDINGS\nNone.",
            "E. MEDIUM_LOW_FINDINGS\nNote: Stage2 SG-1 may be explicitly activated by user: NO",
        ),
        doc().replace(
            "E. MEDIUM_LOW_FINDINGS\nNone.",
            "E. MEDIUM_LOW_FINDINGS\nHowever, Broader Stage2 semantic authority granted: YES",
        ),
        doc() + "\nA. EXTRA\ntext",
        doc().replace("B. IDENTITY", "D. REORDERED"),
    )
    for bad in bad_cases:
        rejects(bad)

    root = Path("governance-r8")
    historical = (
        "R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt",
        "R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-003.txt",
        "R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-004.txt",
    )
    for name in historical:
        parse_review_contract((root / name).read_text(encoding="utf-8"))

    print(
        "R8_REVIEW_CONTRACT_PARSER_TESTS_PASS "
        f"accepted={len(accepted)} rejected={len(bad_cases)} historical={len(historical)}"
    )


if __name__ == "__main__":
    main()
