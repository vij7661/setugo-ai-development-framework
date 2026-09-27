"""Build the immutable Q16 review payload before packet statement/attestation wrapping."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-root", type=Path, required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--linux-statement", type=Path, required=True)
    ap.add_argument("--log-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    root = args.candidate_root.resolve()
    assert git(root, "rev-parse", "HEAD") == args.head
    assert git(root, "rev-parse", "HEAD^{tree}") == args.tree

    changed = git(root, "diff", "--name-only", f"{args.base}..{args.head}").splitlines()
    linux = json.loads(args.linux_statement.read_text(encoding="utf-8"))
    assert linux["candidate_commit"] == args.head
    assert linux["candidate_tree"] == args.tree
    assert linux["baseline_commit"] == args.base
    assert linux["changed_file_count"] == len(changed)

    diff = subprocess.check_output(
        ["git", "-C", str(root), "diff", "--no-ext-diff", "--unified=80", f"{args.base}..{args.head}"],
        text=True,
    )

    parts: list[str] = []
    parts.append("R8 v15-r1 — Q16 FROZEN REVIEW-REMEDIATION SUCCESSOR — INDEPENDENT REVIEW PAYLOAD\n\n")
    parts.append("This payload is later wrapped with a candidate-bound REVIEW_PACKET execution statement and an external freeze-attestation v2.\n")
    parts.append("USE ONLY THE FINAL Q16 REVIEW BUNDLE AS REVIEW MATERIAL.\n")
    parts.append("Do not rely on prior conversation history, proposer confidence, model recollection, or prior PASS labels.\n")
    parts.append("Review ONE immutable frozen Q16 candidate only.\n")
    parts.append("DO NOT STOP AFTER THE FIRST FINDING. Enumerate ALL Critical, High, Medium, and Low findings.\n\n")

    parts.append("===== EXACT CANDIDATE IDENTITY =====\n")
    parts.append(f"baseline: {args.base}\n")
    parts.append(f"frozen Q16 commit: {args.head}\n")
    parts.append(f"frozen Q16 tree: {args.tree}\n")
    parts.append("frozen branch: frozen/r8-v15-r1-q16-q15-review-successor-2026-09-27\n")
    parts.append(f"changed-file count from baseline: {len(changed)}\n")
    parts.append(f"exact Linux validation run/job: {linux['run_id']} / {linux['job_id']}\n")
    parts.append(f"Linux statement SHA256: {linux['statement_sha256']}\n")
    parts.append(f"Linux evidence artifact digest: {linux['artifact_digest']}\n")
    parts.append("authority_effect: NONE\n")
    parts.append("fallback-to-3: ACTIVE\n")
    parts.append("six-slice cadence restored: NO\n\n")

    parts.append("===== CANDIDATE-BOUND LINUX EXECUTION STATEMENT =====\n")
    parts.append(args.linux_statement.read_text(encoding="utf-8"))
    if not parts[-1].endswith("\n"):
        parts.append("\n")
    parts.append("===== END LINUX EXECUTION STATEMENT =====\n\n")

    parts.append("===== LINEAGE / WHY Q16 EXISTS =====\n")
    parts.append("- SG-1 closure baseline: 7cd2787d85b189a4161f271ee131e42bd961140a.\n")
    parts.append("- Frozen Q15 predecessor: 8ce8226818407924d81cee98a2800fc64d1797b1 / a571f49f66f0543ac2f12bdf5b39db99d537a02c.\n")
    parts.append("- Q15 independent review 001 disposition: CHANGES_REQUIRED.\n")
    parts.append("- Reviewer C-01 and M-04 were rejected because mutating an immutable candidate to record a later freeze would recreate self-reference.\n")
    parts.append("- H-01/H-02/H-03/H-04, M-01/M-02/M-03, L-01/L-02 were accepted/narrowed/alternatively repaired.\n")
    parts.append("- Implementer-discovered I-01 HIGH repaired the A-J parser so the exact Q15 review grammar and candidate label can be ingested.\n")
    parts.append("- Q16 retains candidate-local PRE_FREEZE_READY construction state; post-freeze state is external lifecycle evidence.\n")
    parts.append("- No external provider/model API call is used as test evidence.\n\n")

    parts.append("===== Q16 REPAIR FAMILIES TO RE-FALSIFY =====\n")
    for line in [
        "Review B-section identity is structurally parsed and bound to expected candidate, Linux statement, packet statement, and freeze attestation.",
        "Actual Gemini wire endpoint/payload/timeout/retry semantics are derived from or exactly validated against one canonical semantic projection.",
        "Freeze-attestation v2 binds candidate-bound Linux and review-packet execution statements; stale/cross-candidate replay must fail.",
        "Committed successor invariant CI runs the full governed test inventory and self-checks that required commands cannot silently disappear.",
        "Structured provider/reviewer metadata keys are trim/case/hyphen normalized; governance and secret/auth keys are rejected recursively.",
        "Natural-language user/system message content remains opaque and may mention governance/security words.",
        "The platform materialized review path accepts only PLATFORM_MATERIALIZED_CONTENT; claimed delivery mode must match actual integration.",
        "Logical subject IDs are separate from exact repository path/object/blob identity and content digest/bytes.",
        "Authenticated MCP and URL-context modes have mode-specific complete identity requirements.",
        "Generic A-J parser accepts bounded structural finding IDs such as C-01/H-01/M-01/L-01 and parameterizes the candidate label.",
        "Candidate-local construction state and external post-freeze lifecycle state are deliberately separated to avoid self-reference.",
    ]:
        parts.append(f"- {line}\n")
    parts.append("\n")

    parts.append("===== API REQUEST PRESERVATION BOUNDARY =====\n")
    parts.append("- No API_REQUEST_SCHEMA_CHANGE is authorized.\n")
    parts.append("- No API_EXECUTION_BEHAVIOR_CHANGE is authorized.\n")
    parts.append("- Same admitted logical request must preserve the pre-Q16 Gemini wire request semantics.\n")
    parts.append("- Endpoint, HTTP method, model, prompt, payload, generation parameters, timeout, retry, streaming, and response interpretation must not silently drift.\n")
    parts.append("- Authentication secrets must remain transport-only, outside semantic fingerprints and persisted evidence.\n\n")

    parts.append("===== EXACT CHANGED FILE IDENTITIES =====\n")
    for p in changed:
        blob = git(root, "rev-parse", f"{args.head}:{p}")
        data = (root / p).read_bytes()
        parts.append(f"- {p} | blob {blob} | sha256 {hashlib.sha256(data).hexdigest()} | bytes {len(data)}\n")

    parts.append("\n===== EXACT CHANGED FILE CONTENTS =====\n")
    for p in changed:
        blob = git(root, "rev-parse", f"{args.head}:{p}")
        data = (root / p).read_bytes()
        raw = hashlib.sha256(data).hexdigest()
        parts.append(f"\n----- BEGIN FILE {p} | blob {blob} | sha256 {raw} -----\n")
        try:
            txt = data.decode("utf-8")
        except UnicodeDecodeError:
            txt = "<NON-UTF8 FILE; IDENTITY/HASH ABOVE>\n"
        parts.append(txt)
        if not txt.endswith("\n"):
            parts.append("\n")
        parts.append(f"----- END FILE {p} -----\n")

    parts.extend([
        "\n===== COMPLETE BASELINE-TO-Q16 DIFF =====\n",
        diff,
        "\n===== END DIFF =====\n",
    ])

    parts.append("\n===== EXACT PACKET-GENERATION TEST LOGS =====\n")
    for lp in sorted(args.log_dir.glob("*.txt")):
        parts.append(f"\n----- BEGIN LOG {lp.name} -----\n")
        txt = lp.read_text(encoding="utf-8", errors="replace")
        parts.append(txt)
        if not txt.endswith("\n"):
            parts.append("\n")
        parts.append(f"----- END LOG {lp.name} -----\n")

    parts.append(r"""
===== INDEPENDENT REVIEW CONTRACT =====

The FINAL REVIEW BUNDLE places the packet execution statement and external freeze-attestation v2 before this payload.
Treat those external records as the post-freeze lifecycle evidence; do NOT require this immutable candidate to rewrite itself after freeze.

Review the ONE exact frozen Q16 candidate identified above.
DO NOT STOP AFTER THE FIRST FINDING.
Enumerate ALL Critical, High, Medium, and Low findings.

Re-falsify, in particular:
- review section-B candidate identity binding across review, expected identity, Linux statement, packet statement, and v2 freeze attestation;
- parser compatibility with the exact A-J contract, non-F finding IDs, candidate labels, negative dispositions, malformed headings, Unicode/punctuation, duplicate IDs, and severity mismatches;
- candidate-local PRE_FREEZE_READY vs external FROZEN lifecycle separation, without demanding self-referential in-tree post-freeze mutation;
- v2 execution-statement digest integrity and stale/cross-candidate run/job replay;
- whether the actual Gemini wire request is genuinely derived from/validated against the semantic projection rather than a parallel unused helper;
- whether endpoint, payload, generation configuration, timeout, retry, streaming or response semantics can drift undetected;
- recursive secret/governance key normalization and whether ordinary natural-language prompt text remains valid;
- real reviewer-delivery mode truthfulness and exact source path/object/blob identity;
- whether matching bytes from the wrong source can satisfy delivery;
- invariant-workflow completeness and whether the self-check can be trivially bypassed;
- queue/lifecycle logic for accidental self-reference or false freeze claims;
- any repair-induced defect not explicitly anticipated above.

For EVERY finding provide:
1. Finding ID
2. Severity: CRITICAL / HIGH / MEDIUM / LOW
3. Exact file/function/contract
4. Concrete failure / false-green / omission path
5. Evidence from this bundle
6. Why current invariant/test is insufficient
7. Narrowest safe proposed remediation
8. Exact regression/falsification test
9. Candidate invalidated: YES/NO
10. Merge/promotion blocking: YES/NO
11. Classification: code / evidence / runtime / API-contract / packaging / governance-rule

Return ONLY sections A-J:

A. OVERALL_DISPOSITION
Exactly one: BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE

B. EXACT_CANDIDATE_IDENTITY
Repeat baseline, frozen Q16 commit/tree, changed-file count, packet run/job, Linux validation run/job.

C. CRITICAL_FINDINGS
Use NONE. if none.

D. HIGH_FINDINGS
Use NONE. if none.

E. MEDIUM_FINDINGS
Use NONE. if none.

F. LOW_FINDINGS
Use NONE. if none.

G. PERMANENT_INVARIANT_ASSESSMENT
Assess all Q16 repair families separately, including lifecycle-state separation.

H. API_AND_REVIEWER_DELIVERY_ASSESSMENT
Assess actual Gemini wire-request preservation and all reviewer delivery modes as integrated/enforced.

I. REMEDIATION_PLAN
For every finding provide the proposed solution and exact regression/falsification test. Reviewer proposals remain advisory and require implementer adjudication.

J. FINAL_GATE
State exactly:
- Frozen Q16 candidate eligible for bounded merge consideration: YES or NO.
- Broader Stage2 semantic authority granted: NO.
- Runtime qualification granted: NO.
- Release/deployment/production authority granted: NO.
- Automatic six-slice cadence restoration: NO.
- Fallback-to-3 remains ACTIVE.
""")

    payload = "".join(parts)
    args.out.write_text(payload, encoding="utf-8", newline="\n")
    raw = args.out.read_bytes()
    print("payload_sha256=" + hashlib.sha256(raw).hexdigest())
    print("payload_bytes=" + str(len(raw)))
    print("payload_lines=" + str(payload.count("\n") + 1))
    print("changed_file_count=" + str(len(changed)))


if __name__ == "__main__":
    main()
