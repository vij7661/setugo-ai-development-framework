"""Build a self-contained independent-review packet for exact frozen Q15."""
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
    ap.add_argument("--freeze-attestation", type=Path, required=True)
    ap.add_argument("--log-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--packet-run-id", required=True)
    ap.add_argument("--packet-job-id", required=True)
    ap.add_argument("--linux-run-id", required=True)
    ap.add_argument("--linux-job-id", required=True)
    args = ap.parse_args()

    root = args.candidate_root.resolve()
    assert git(root, "rev-parse", "HEAD") == args.head
    assert git(root, "rev-parse", "HEAD^{tree}") == args.tree

    changed = git(root, "diff", "--name-only", f"{args.base}..{args.head}").splitlines()
    diff = subprocess.check_output(
        ["git", "-C", str(root), "diff", "--no-ext-diff", "--unified=80", f"{args.base}..{args.head}"],
        text=True,
    )
    attestation = json.loads(args.freeze_attestation.read_text(encoding="utf-8"))
    assert attestation["candidate_commit"] == args.head
    assert attestation["candidate_tree"] == args.tree
    assert attestation["linux_validation"]["run_id"] == args.linux_run_id
    assert attestation["linux_validation"]["job_id"] == args.linux_job_id
    assert attestation["review_packet"]["run_id"] == args.packet_run_id
    assert attestation["review_packet"]["job_id"] == args.packet_job_id

    parts: list[str] = []
    parts.append("R8 v15-r1 — Q15 FROZEN REVIEW-REMEDIATION SUCCESSOR — INDEPENDENT REVIEW\n\n")
    parts.append("USE ONLY THIS PACKET AS THE REVIEW MATERIAL.\n")
    parts.append("Do not use prior conversation history, proposer confidence, model recollection, or prior PASS labels as evidence.\n")
    parts.append("Review ONE immutable frozen candidate only.\n")
    parts.append("Do not stop after the first finding. Enumerate ALL Critical, High, Medium, and Low findings.\n\n")

    parts.append("===== EXACT CANDIDATE IDENTITY =====\n")
    parts.append(f"baseline: {args.base}\n")
    parts.append(f"frozen Q15 commit: {args.head}\n")
    parts.append(f"frozen Q15 tree: {args.tree}\n")
    parts.append("frozen branch: frozen/r8-v15-r1-q15-review-remediation-successor-2026-09-27\n")
    parts.append(f"changed-file count from baseline: {len(changed)}\n")
    parts.append(f"packet-generation run: {args.packet_run_id}\n")
    parts.append(f"packet-generation job: {args.packet_job_id}\n")
    parts.append(f"exact Linux validation run: {args.linux_run_id}\n")
    parts.append(f"exact Linux validation job: {args.linux_job_id}\n")
    parts.append("authority_effect: NONE\n")
    parts.append("fallback-to-3: ACTIVE\n")
    parts.append("six-slice cadence restored: NO\n\n")

    parts.append("===== EXTERNAL FREEZE ATTESTATION =====\n")
    parts.append(args.freeze_attestation.read_text(encoding="utf-8"))
    if not parts[-1].endswith("\n"):
        parts.append("\n")
    parts.append("===== END EXTERNAL FREEZE ATTESTATION =====\n\n")

    parts.append("===== LINEAGE / WHY Q15 EXISTS =====\n")
    parts.append("- SG-1 bounded closure baseline: 7cd2787d85b189a4161f271ee131e42bd961140a.\n")
    parts.append("- Frozen Q14 predecessor: 01ec3651c9c0764e69944cd5718b07e4d30623b4 / a61f1b0686c65719a83e0b065f5ac632f88cba96.\n")
    parts.append("- Q14 independent review 001 disposition: CHANGES_REQUIRED; Critical NONE; High F-01/F-02/F-03; Medium F-04/F-05/F-06; Low F-07.\n")
    parts.append("- Q15 is the single successor implementing governed adjudications for all F-01..F-07.\n")
    parts.append("- Q14 frozen history is preserved; Q15 does not rewrite the predecessor.\n")
    parts.append("- No external provider/model API call was used as test evidence.\n\n")

    parts.append("===== Q15 ADJUDICATED REPAIR FAMILIES =====\n")
    for line in [
        "F-01 ACCEPTED_NARROWED: reviewer evidence delivery integrated into the actual governed review path before provider invocation.",
        "F-02 ACCEPTED_WITH_ALTERNATIVE_SOLUTION: legacy A-H SG1 activation parser preserved; separate structural A-J independent-review parser/gate added.",
        "F-03 ACCEPTED_WITH_ALTERNATIVE_SOLUTION: external non-self-referential freeze attestation binds exact candidate/ref/Linux/packet evidence.",
        "F-04 ACCEPTED_NARROWED: recursive structured governance-metadata rejection without scanning ordinary natural-language message text.",
        "F-05 ACCEPTED_WITH_ALTERNATIVE_SOLUTION: authentication secrets excluded from adapter semantic projection by construction.",
        "F-06 ACCEPTED_NARROWED: queue preserves implementation branch and separately binds exact frozen/reviewed candidate identity.",
        "F-07 ACCEPTED_AS_PROPOSED: PROVIDER_URL_CONTEXT requires fetched-content SHA-256 and byte count for mandatory evidence.",
    ]:
        parts.append(f"- {line}\n")
    parts.append("\n")

    parts.append("===== PRESERVED PRE-FREEZE LINUX HISTORY =====\n")
    parts.append("- 36270975410 / 108484736168: first exact Linux run; stale changed-file count 37 vs 53 detected.\n")
    parts.append("- 36271088620 / 108485055943: exhaustive run; stale count plus evidence-harness cwd/cache defects observed.\n")
    parts.append("- 36271206089 / 108485381693: corrected harness; only real candidate defect remained stale 37 vs 53 count.\n")
    parts.append(f"- {args.linux_run_id} / {args.linux_job_id}: repaired exact candidate; complete Linux matrix PASS, zero failures.\n\n")

    parts.append("===== API REQUEST PRESERVATION BOUNDARY =====\n")
    parts.append("- Authorized change classes are governance/control/evidence/admission only.\n")
    parts.append("- No API_REQUEST_SCHEMA_CHANGE is authorized.\n")
    parts.append("- No API_EXECUTION_BEHAVIOR_CHANGE is authorized.\n")
    parts.append("- Same admitted logical request must preserve adapter-facing semantic request identity.\n")
    parts.append("- Provider endpoint, HTTP method, model, prompt/messages, provider parameters, timeout, retry, streaming and response semantics must not silently change.\n")
    parts.append("- Authentication secrets must remain outside semantic fingerprints and persisted evidence.\n\n")

    parts.append("===== EXACT CHANGED FILE IDENTITIES =====\n")
    for p in changed:
        blob = git(root, "rev-parse", f"{args.head}:{p}")
        data = (root / p).read_bytes()
        parts.append(
            f"- {p} | blob {blob} | sha256 {hashlib.sha256(data).hexdigest()} | bytes {len(data)}\n"
        )

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
        "\n===== COMPLETE BASELINE-TO-Q15 DIFF =====\n",
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

Review the ONE exact frozen Q15 candidate identified above.

DO NOT STOP AFTER THE FIRST FINDING.
Enumerate ALL Critical, High, Medium, and Low findings.

Do not accept a claim merely because a test is green, a prior reviewer proposed it, or the packet calls it closed.
Re-falsify the implementation from the exact file contents, diff, freeze attestation, and logs.

Pay particular attention to:
- whether F-01 is truly enforced on the real provider review request/materialization path before invocation;
- whether access-manifest/corpus/request/candidate binding can be spoofed, omitted, or partially satisfied;
- whether URL_ONLY is incapable of satisfying mandatory review evidence;
- whether PROVIDER_URL_CONTEXT proves fetched-content identity rather than only locator identity;
- whether AUTHENTICATED_GITHUB_MCP_READ_ONLY and PLATFORM_MATERIALIZED_CONTENT enforce complete exact mandatory subjects;
- whether the A-J parser accepts negative dispositions as valid evidence without treating them as merge PASS;
- whether legacy A-H SG1 activation semantics were accidentally weakened;
- whether A-J severity parsing can be bypassed with headings, punctuation, Unicode, malformed numbering, duplicate IDs, or prose placement;
- whether the external freeze attestation is non-self-referential and actually verifies frozen ref -> exact commit/tree;
- whether the attestation's Linux and packet run/job fields are exact and whether a stale/cross-candidate attestation can be replayed;
- whether queue identity can drift from frozen identity/attestation;
- whether nested structured governance metadata can still leak into provider-facing request semantics;
- whether ordinary user/system natural-language content remains valid;
- whether the adapter-facing semantic request projection really matches the actual Gemini transport payload/endpoint/model/timeout/retry semantics;
- whether authentication secrets can affect semantic fingerprints or persisted evidence;
- whether governance-only Q15 changes accidentally alter real provider request schema or execution behavior;
- whether changed-file accounting can go stale again or can be made self-referential/hand-entered;
- whether the review/merge evidence gate can be bypassed with a valid negative review, malformed final gate, missing freeze evidence, or stale review.

For EVERY finding provide:
1. Finding ID
2. Severity: CRITICAL / HIGH / MEDIUM / LOW
3. Exact file/function/contract
4. Concrete failure / false-green / omission path
5. Evidence from this packet
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
Repeat baseline, frozen Q15 commit/tree, changed-file count, packet run/job, Linux validation run/job.

C. CRITICAL_FINDINGS
Use NONE. if none.

D. HIGH_FINDINGS
Use NONE. if none.

E. MEDIUM_FINDINGS
Use NONE. if none.

F. LOW_FINDINGS
Use NONE. if none.

G. PERMANENT_INVARIANT_ASSESSMENT
Assess each Q15 repair family F-01..F-07 and the preserved Q14 invariant families materially affected by Q15.

H. API_AND_REVIEWER_DELIVERY_ASSESSMENT
Assess actual adapter-facing request preservation and all reviewer evidence-delivery modes as integrated in the real review path.

I. REMEDIATION_PLAN
For every finding provide the proposed solution and exact regression/falsification test. If no findings, state NONE.
Explicitly state that reviewer solutions are advisory and require implementer adjudication.

J. FINAL_GATE
State exactly:
- Frozen Q15 candidate eligible for bounded merge consideration: YES or NO.
- Broader Stage2 semantic authority granted: NO.
- Runtime qualification granted: NO.
- Release/deployment/production authority granted: NO.
- Automatic six-slice cadence restoration: NO.
- Fallback-to-3 remains ACTIVE.
""")

    packet = "".join(parts)
    args.out.write_text(packet, encoding="utf-8", newline="\n")
    raw = args.out.read_bytes()
    print(str(args.out))
    print("packet_sha256=" + hashlib.sha256(raw).hexdigest())
    print("packet_bytes=" + str(len(raw)))
    print("packet_lines=" + str(packet.count("\n") + 1))
    print("changed_file_count=" + str(len(changed)))


if __name__ == "__main__":
    main()
