"""Table-driven adversarial tests for the shared SG-1 review parser."""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from r8_v15_r1_review_contract_parser import parse_review_contract  # noqa: E402


def doc(h="Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO"):
    return f"""A. OVERALL_DISPOSITION\nBOUNDED_PASS\nB. IDENTITY\nproposal\nC. CRITICAL_FINDINGS\nNONE.\nD. HIGH_FINDINGS\nNONE.\nE. MEDIUM_LOW_FINDINGS\nNone.\nF. ASSESSMENT\npass\nG. BOUNDARY\nLOCAL\nH. FINAL_GATE\n{h}\n"""


def rejects(text):
    try:
        parse_review_contract(text)
    except ValueError:
        return
    raise AssertionError("malformed review accepted")


def main():
    parse_review_contract(doc())
    parse_review_contract(doc("- Stage2 SG-1 may be explicitly activated by user: nOnE".replace("nOnE", "YES.") + "\n- Broader Stage2 semantic authority granted: no."))
    parse_review_contract(doc().replace("NONE.", "nOnE", 1).replace("NONE.", "None", 1).replace("\n", "\r\n"))
    for bad in (
        doc().replace("A. OVERALL_DISPOSITION", "A. OVERALL_DISPOSITION\nA. DUPLICATE", 1),
        doc().replace("C. CRITICAL_FINDINGS", "C. CRITICAL_FINDINGS\nC. DUPLICATE", 1),
        doc().replace("D. HIGH_FINDINGS", "D. HIGH_FINDINGS\nD. DUPLICATE", 1),
        doc().replace("H. FINAL_GATE", "H. FINAL_GATE\nH. DUPLICATE", 1),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nC. CRITICAL_FINDINGS\nCRITICAL: hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\n- HIGH FINDING: hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\n- HIGH FINDING: hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nCRITICAL — hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nHIGH - hidden"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nStage2 SG-1 may be explicitly activated by user: NO\nBroader Stage2 semantic authority granted: NO"),
        doc("Stage2 SG-1 may be explicitly activated by user: YES\nBroader Stage2 semantic authority granted: NO\nBroader Stage2 semantic authority granted: YES"),
        doc() + "\nA. EXTRA\ntext",
        doc().replace("B. IDENTITY", "D. REORDERED"),
    ):
        rejects(bad)
    root = Path("governance-r8")
    for name in ("R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt", "R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-003.txt", "R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-004.txt"):
        parse_review_contract((root / name).read_text(encoding="utf-8"))
    print("R8_REVIEW_CONTRACT_PARSER_TESTS_PASS cases=14")


if __name__ == "__main__":
    main()
