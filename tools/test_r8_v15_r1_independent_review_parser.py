from __future__ import annotations

import copy
from pathlib import Path

from r8_v15_r1_independent_review_parser import eligible_for_bounded_merge, parse_independent_review


def clean(disposition="BOUNDED_PASS", label="Q14"):
    return f"""A. OVERALL_DISPOSITION
{disposition}
B. EXACT_CANDIDATE_IDENTITY
- baseline: {'b'*40}
- frozen {label} commit: {'a'*40}
- frozen {label} tree: {'c'*40}
- changed-file count from baseline: 53
- packet-generation run/job: 11 / 12
- exact Linux validation run/job: 13 / 14
C. CRITICAL_FINDINGS
NONE.
D. HIGH_FINDINGS
NONE.
E. MEDIUM_FINDINGS
NONE.
F. LOW_FINDINGS
NONE.
G. PERMANENT_INVARIANT_ASSESSMENT
All tested.
H. API_AND_REVIEWER_DELIVERY_ASSESSMENT
Preserved.
I. REMEDIATION_PLAN
None.
J. FINAL_GATE
- Frozen {label} candidate eligible for bounded merge consideration: YES
- Broader Stage2 semantic authority granted: NO
- Runtime qualification granted: NO
- Release/deployment/production authority granted: NO
- Automatic six-slice cadence restoration: NO
- Fallback-to-3 remains ACTIVE
"""


def reject(text, label="Q14"):
    try:
        parse_independent_review(text, candidate_label=label)
    except ValueError:
        return
    raise AssertionError("malformed A-J review accepted")


def main():
    parsed = parse_independent_review(clean(), candidate_label="Q14")
    assert not eligible_for_bounded_merge(parsed)
    assert eligible_for_bounded_merge(parsed, freeze_verified=True)
    for disposition in ("CHANGES_REQUIRED", "INSUFFICIENT_EVIDENCE"):
        negative = parse_independent_review(clean(disposition), candidate_label="Q14")
        assert negative["disposition"] == disposition
        assert not eligible_for_bounded_merge(negative)
    preserved = parse_independent_review(Path("governance-r8/R8-V15-R1-Q14-INDEPENDENT-REVIEW-001.txt").read_text(encoding="utf-8"), candidate_label="Q14", allow_legacy_finding_annotations=True)
    assert preserved["disposition"] == "CHANGES_REQUIRED"
    assert not eligible_for_bounded_merge(preserved)
    q15 = parse_independent_review(Path("governance-r8/R8-V15-R1-Q15-INDEPENDENT-REVIEW-001.txt").read_text(encoding="utf-8"), candidate_label="Q15")
    assert q15["disposition"] == "CHANGES_REQUIRED"
    assert q15["identity"]["candidate_commit"] == "8ce8226818407924d81cee98a2800fc64d1797b1"
    q16 = parse_independent_review(Path("governance-r8/R8-V15-R1-Q16-INDEPENDENT-REVIEW-001.txt").read_text(encoding="utf-8"), candidate_label="Q16")
    assert q16["disposition"] == "CHANGES_REQUIRED"
    base = clean()
    finding = """**F-09**
2. HIGH
3. location
4. failure
5. evidence
6. impact
7. repair
8. regression
9. Candidate invalidated: NO
10. Merge/promotion blocking: YES
11. Classification: code
"""
    with_finding = base.replace("D. HIGH_FINDINGS\nNONE.", "D. HIGH_FINDINGS\n" + finding)
    assert parse_independent_review(with_finding, candidate_label="Q14")["findings"]["HIGH"] == ["F-09"]
    cases = [
        base.replace("B. EXACT_CANDIDATE_IDENTITY", "A. DUPLICATE", 1),
        base.replace("D. HIGH_FINDINGS", "C. CRITICAL_FINDINGS", 1),
        base.replace("E. MEDIUM_FINDINGS\nNONE.\nF. LOW_FINDINGS", "F. LOW_FINDINGS\nNONE.\nE. MEDIUM_FINDINGS"),
        base.replace("F. LOW_FINDINGS\nNONE.\n", ""),
        base + "\nJ. FINAL_GATE\ntext",
        with_finding.replace("2. HIGH", "2. MEDIUM"),
        with_finding.replace("11. Classification: code", ""),
        base.replace("Fallback-to-3 remains ACTIVE", "Fallback-to-3 remains INACTIVE"),
        base.replace("Runtime qualification granted: NO", "Runtime qualification: NO"),
        base.replace("Frozen Q14 candidate", "Frozen Q15 candidate"),
        with_finding.replace("F-09", "bad id"),
        with_finding.replace("**F-09**", "**F-09**\n**F-09**"),
        with_finding.replace("**F-09**", "**H-09**").replace("2. HIGH", "2. MEDIUM"),
        base.replace("frozen Q14 commit", "frozen Q15 commit"),
        with_finding.replace("8. regression\n9. Candidate", "9. Candidate\n8. regression"),
        with_finding.replace("Candidate invalidated: NO", "Candidate invalidated: MAYBE"),
        with_finding.replace("Merge/promotion blocking: YES", "Merge/promotion blocking: MAYBE"),
        with_finding.replace("Classification: code", "Classification: unknown-class"),
    ]
    for case in cases:
        reject(case)
    print(f"R8_AJ_INDEPENDENT_REVIEW_PARSER_PASS rejected={len(cases)}")


if __name__ == "__main__":
    main()
