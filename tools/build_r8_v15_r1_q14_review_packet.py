"""Build a self-contained independent-review packet for exact frozen Q14."""
from __future__ import annotations

import argparse
import hashlib
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

    parts: list[str] = []
    parts.append("R8 v15-r1 — Q14 FROZEN PERMANENT-INVARIANT CANDIDATE — INDEPENDENT REVIEW\n\n")
    parts.append("USE ONLY THIS PACKET AS THE REVIEW MATERIAL.\n")
    parts.append("Do not use prior conversation history, proposer confidence, model recollection, or prior PASS labels as evidence.\n")
    parts.append("Review ONE immutable frozen candidate only.\n\n")

    parts.append("===== EXACT CANDIDATE IDENTITY =====\n")
    parts.append(f"baseline: {args.base}\n")
    parts.append(f"frozen Q14 commit: {args.head}\n")
    parts.append(f"frozen Q14 tree: {args.tree}\n")
    parts.append("frozen branch: frozen/r8-v15-r1-q14-permanent-invariants-2026-09-27\n")
    parts.append(f"changed-file count from baseline: {len(changed)}\n")
    parts.append(f"packet-generation run: {args.packet_run_id}\n")
    parts.append(f"packet-generation job: {args.packet_job_id}\n")
    parts.append(f"exact Linux validation run: {args.linux_run_id}\n")
    parts.append(f"exact Linux validation job: {args.linux_job_id}\n")
    parts.append("authority_effect: NONE\n")
    parts.append("fallback-to-3: ACTIVE\n")
    parts.append("six-slice cadence restored: NO\n\n")

    parts.append("===== LINEAGE / WHY Q14 EXISTS =====\n")
    parts.append("- SG-1 bounded closure baseline: 7cd2787d85b189a4161f271ee131e42bd961140a.\n")
    parts.append("- Earlier post-SG1 candidates were preserved; defects were not rewritten away.\n")
    parts.append("- Frozen successor2 a9bf0a4fbdb3e382183bb285b521de935451fe9c was independently reviewed and returned CHANGES_REQUIRED.\n")
    parts.append("- Q14 was created after a root-cause review concluded that repeated example-by-example repairs must be replaced by permanent defect-family invariants.\n")
    parts.append("- Q14 adds/repairs reviewer grammar, controlled authority declarations, workflow command contracts, semantic/evidence identity, queue completeness, filesystem confinement, deterministic review packaging, cross-component equality, provider API request preservation, reviewer evidence delivery, and reviewer-solution adjudication.\n")
    parts.append("- No external provider API call is evidence of Q14 correctness.\n\n")

    parts.append("===== SUCCESSOR2 REVIEW FINDINGS THAT Q14 MUST STRUCTURALLY CLOSE =====\n")
    parts.append("- C-01: non-C/D heading-line hidden Critical/High bypass.\n")
    parts.append("- C-02: contradictory activation/authority declarations embedded in heading/prose.\n")
    parts.append("- H-01: Review003/Review004 validator shell continuation made --review a separate command.\n")
    parts.append("- M-01: exact changed-file count was printed but not asserted.\n")
    parts.append("- M-02: Q10 integration task was absent from machine-readable queue ledger.\n")
    parts.append("- L-01: CRITICAL_FINDING / HIGH_FINDING underscore forms were not directly covered.\n")
    parts.append("- L-02: direct public-helper lexical parent traversal regression was missing.\n\n")

    parts.append("===== Q14 PERMANENT-INVARIANT FAMILIES =====\n")
    for line in [
        "1. Review grammar must be structural, not a list of punctuation examples.",
        "2. Controlled activation/authority declarations have one semantic owner; duplicate/contradictory/embedded declarations fail closed.",
        "3. Workflow commands must be executable exactly as written and CLI-compatible.",
        "4. Semantic verification recomputes canonical results; self-hash alone is insufficient.",
        "5. Evidence identity binds the complete applicable tuple: schema/archive/run/job/workflow/head/inputs/digests/activation evidence/authority effect.",
        "6. Every governed Q-task is represented in the machine-readable ledger or governed exemption.",
        "7. Filesystem confinement uses one fixed caller root with descriptor-safe traversal and direct helper regressions.",
        "8. Review packets are deterministic projections of one immutable SHA/tree; counts/digests/test results are derived.",
        "9. Cross-component load-bearing dependencies must be equal in the one reviewed tree.",
        "10. Governance-only remediation preserves provider-facing API request semantics.",
        "11. Mandatory reviewer evidence must actually be delivered completely.",
        "12. Reviewer defects include proposed remediation/regressions, but reviewer solutions remain advisory until implementer adjudication.",
    ]:
        parts.append(f"- {line}\n")
    parts.append("\n")

    parts.append("===== PROVIDER API REQUEST PRESERVATION CONTRACT =====\n")
    parts.append("- Change classes: CONTROL_PLANE_ONLY, EVIDENCE_ONLY, API_ADMISSION_EFFECT, API_REQUEST_SCHEMA_CHANGE, API_EXECUTION_BEHAVIOR_CHANGE.\n")
    parts.append("- Q14 did not authorize API_REQUEST_SCHEMA_CHANGE or API_EXECUTION_BEHAVIOR_CHANGE.\n")
    parts.append("- Same admitted logical request must retain the same canonical provider-request fingerprint for governance-only changes.\n")
    parts.append("- Governance metadata must not silently leak into provider-facing model/API requests.\n")
    parts.append("- Secret values must not enter fingerprints/evidence.\n\n")

    parts.append("===== REVIEWER EVIDENCE DELIVERY MODES =====\n")
    parts.append("- AUTHENTICATED_GITHUB_MCP_READ_ONLY: exact repo + immutable commit + exact object/path; read-only tools; no credential exposure; accessed objects recorded.\n")
    parts.append("- PROVIDER_URL_CONTEXT: only when provider proves URL fetch/context; immutable commit-addressed URLs; fetched content identity must be recorded.\n")
    parts.append("- PLATFORM_MATERIALIZED_CONTENT: platform fetches exact objects, verifies identity, and sends exact file/content/chunks.\n")
    parts.append("- URL_ONLY: locator only; NEVER sufficient evidence that the reviewer received/reviewed content.\n")
    parts.append("- Missing/truncated/digest-mismatched/partial mandatory delivery is non-promotable.\n\n")

    parts.append("===== REVIEWER SOLUTION / IMPLEMENTER ADJUDICATION CONTRACT =====\n")
    parts.append("For each defect, reviewer output should include finding id, severity, location, failure path, evidence, impact, narrow remediation, exact regression/falsification test, candidate-invalidated flag, blocking flag.\n")
    parts.append("Reviewer solutions are advisory, not authority. Supported implementer adjudications:\n")
    for state in [
        "ACCEPTED_AS_PROPOSED",
        "ACCEPTED_NARROWED",
        "ACCEPTED_WITH_ALTERNATIVE_SOLUTION",
        "REJECTED_NOT_REPRODUCED",
        "REJECTED_UNSAFE_OR_OUT_OF_SCOPE",
        "DEFERRED_REQUIRES_EVIDENCE",
    ]:
        parts.append(f"- {state}\n")
    parts.append("\n")

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
        "\n===== COMPLETE BASELINE-TO-Q14 DIFF =====\n",
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

Review the ONE exact frozen Q14 candidate identified above.

DO NOT STOP AFTER THE FIRST FINDING.
Enumerate ALL Critical, High, Medium, and Low findings.

Do not accept any claim merely because this packet labels it a permanent invariant or because a test is green.
Re-falsify the implementation from the exact file contents, diff, and logs.

Pay particular attention to:
- whether review parsing is truly structural or still an enumerable regex/example patch set;
- whether harmless formatting is separated from authority semantics without allowing contradictory/embedded declarations;
- whether workflow command validation proves the actual shell/CLI command, not textual presence;
- whether semantic/evidence identity is complete and replay-resistant;
- whether queue completeness can drift when a new Q-task is added;
- whether public and internal filesystem helpers share the same fixed-root confinement contract;
- whether deterministic packet generation has any hand-entered identity/count fields capable of drift;
- whether provider request fingerprinting protects the actual adapter-facing request rather than a disconnected synthetic object;
- whether API request preservation accidentally blocks legitimate provider-specific schemas or misses provider-execution semantics;
- whether reviewer evidence delivery helpers are actually integrated with review request construction;
- whether AUTHENTICATED_GITHUB_MCP_READ_ONLY can prove exact immutable objects consumed and cannot expose write tools/credentials;
- whether PROVIDER_URL_CONTEXT can falsely count a URL as delivered without proof of fetch/content identity;
- whether PLATFORM_MATERIALIZED_CONTENT and chunk verification prove full bytes and exact candidate/version;
- whether URL_ONLY can accidentally satisfy review completeness;
- whether reviewer proposed solutions can leak into authority or auto-implementation;
- whether the implementer adjudication record preserves the original finding and reviewer proposal;
- whether any new governance rule causes a false-negative/false-positive path that is itself material;
- whether the Q14 changes alter actual provider-facing request behavior despite claiming governance-only scope.

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
Repeat baseline, frozen Q14 commit/tree, changed-file count, packet run/job, Linux validation run/job.

C. CRITICAL_FINDINGS
Use NONE. if none.

D. HIGH_FINDINGS
Use NONE. if none.

E. MEDIUM_FINDINGS
Use NONE. if none.

F. LOW_FINDINGS
Use NONE. if none.

G. PERMANENT_INVARIANT_ASSESSMENT
Assess all 12 invariant families separately.

H. API_AND_REVIEWER_DELIVERY_ASSESSMENT
Assess provider API request preservation plus all four reviewer evidence-delivery modes and whether they are actually enforced/integrated.

I. REMEDIATION_PLAN
For every finding provide the proposed solution and exact regression/falsification test. If no findings, state NONE.
Explicitly state that proposed solutions are advisory and require implementer adjudication.

J. FINAL_GATE
State exactly:
- Frozen Q14 candidate eligible for bounded merge consideration: YES or NO.
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
