"""Build a self-contained review packet for exact frozen successor2."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git","-C",str(root),*args], text=True).strip()

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate-root", type=Path, required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--tree", required=True)
    ap.add_argument("--log-dir", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--packet-run-id", required=True)
    ap.add_argument("--packet-job", required=True)
    ap.add_argument("--linux-run-id", required=True)
    ap.add_argument("--linux-job-id", required=True)
    args=ap.parse_args()

    root=args.candidate_root.resolve()
    assert git(root,"rev-parse","HEAD")==args.head
    assert git(root,"rev-parse","HEAD^{tree}")==args.tree
    changed=git(root,"diff","--name-only",f"{args.base}..{args.head}").splitlines()
    diff=subprocess.check_output(["git","-C",str(root),"diff","--no-ext-diff","--unified=80",f"{args.base}..{args.head}"], text=True)

    parts=[]
    parts.append("R8 v15-r1 — POST-SG1 FROZEN SUCCESSOR2 INDEPENDENT REVIEW\n\n")
    parts.append("USE ONLY THIS PACKET.\n")
    parts.append("Do not use prior conversation history, GitHub access, external APIs, model recollection, or prior packet conclusions.\n\n")
    parts.append("REVIEW ONE IMMUTABLE SUCCESSOR CANDIDATE ONLY.\n\n")
    parts.append("EXACT IDENTITY\n")
    parts.append(f"baseline: {args.base}\n")
    parts.append(f"frozen successor commit: {args.head}\n")
    parts.append(f"frozen successor tree: {args.tree}\n")
    parts.append("frozen branch: frozen/r8-v15-r1-post-sg1-integration-successor2-2026-09-26\n")
    parts.append(f"changed-file count: {len(changed)}\n")
    parts.append(f"packet-generation run: {args.packet_run_id}\n")
    parts.append(f"packet-generation job: {args.packet_job}\n")
    parts.append(f"exact Linux evidence run: {args.linux_run_id}\n")
    parts.append(f"exact Linux evidence job: {args.linux_job_id}\n")
    parts.append("authority_effect: NONE\n")
    parts.append("fallback-to-3: ACTIVE\n")
    parts.append("six-slice cadence restored: NO\n\n")

    parts.append("HISTORY / SUCCESSOR LINEAGE\n")
    parts.append("- original frozen convergence candidate: ca1ae48be3d01025b7811d50d8482db30d15e4e9 / db50bcbead24390cc147278dd371188e54a3166d — invalidated by independent review.\n")
    parts.append("- frozen successor1: b73f2eb2fd44f97a53f3b39307fd92175330325d / 99fad2453dc849598e95497c1f0d6edf8cf34b36 — superseded after exact Linux evidence exposed checkout-dependent invariant/preflight harness assumptions and direct file_digest traversal acceptance.\n")
    parts.append("- successor2 Linux evidence failed runs preserved: 36244306503, 36244426865, 36244545343.\n")
    parts.append("- successor2 exact successful Linux evidence run: 36244614589, job 108411369154.\n")
    parts.append("- no failed evidence attempt was deleted or rewritten.\n\n")

    parts.append("PRIOR FINDING DISPOSITION\n")
    parts.append("- F-01 FIXED: multiline hidden Critical/High declaration bypass closed by first-alphabetic-token line rule.\n")
    parts.append("- F-02 FIXED: exact C/D headings reject heading-line injection.\n")
    parts.append("- F-03 FIXED: numeric/common bullet/decoration prefixes before Critical/High are rejected; ordinary prose remains allowed.\n")
    parts.append("- F-04 FIXED: validator workflow calls use supported args; exact identity stays on preflight.\n")
    parts.append("- F-05 DOCUMENTED_SCOPE: semantic-gap inventory remains HISTORICAL_STAGE1_BOUND_EVIDENCE for candidate 4984f06a4420b76ad1ad475751aebda04a2d2c5c/base 751162ee42c603cb6c84ee12021d16bab6fa626b and is not claimed regenerated from successor2.\n")
    parts.append("- F-06 FIXED: Git blob lookup failure is controlled fail-closed ValueError.\n")
    parts.append("- F-07 FIXED: exact evidence schema and archive format are strict expected identities.\n")
    parts.append("- F-08 FIXED: manual records required only when task state semantically requires them; optional records still validate.\n")
    parts.append("- F-09 REPRODUCED_ON_LINUX_AND_FIXED: direct parent traversal alias was accepted by file_digest; successor2 rejects lexical '..' before descriptor read. Path('.') is canonicalized by pathlib before the API and is treated identically to the canonical path.\n")
    parts.append("- F-10 FIXED: activation review read is explicitly UTF-8.\n")
    parts.append("- F-11 FIXED: read_confined_file captures absolute root/path once and uses captured root for descriptor open.\n")
    parts.append("- Linux harness portability fixes are successor-only test/evidence repairs; temporary fixtures use temporary directories instead of assuming repository scratch directories exist.\n\n")

    parts.append("EVIDENCE-SCOPE DISTINCTION\n")
    parts.append("- HISTORICAL_STAGE1_BOUND_EVIDENCE: semantic inventory/SG-1 closure evidence remains bound to Stage1 candidate 4984f06a... and is preserved as historical evidence.\n")
    parts.append("- CURRENT_FROZEN_SUCCESSOR2_EVIDENCE: invariant/parser/preflight/runtime/evidence/queue execution below runs against exact successor2 commit/tree.\n")
    parts.append("- This packet does NOT claim every historical artifact was regenerated from successor2.\n\n")

    parts.append("CHANGED FILES WITH EXACT IDENTITIES\n")
    for p in changed:
        blob=git(root,"rev-parse",f"{args.head}:{p}")
        data=(root/p).read_bytes()
        parts.append(f"- {p} | blob {blob} | sha256 {hashlib.sha256(data).hexdigest()} | bytes {len(data)}\n")

    parts.append("\n===== EXACT CHANGED FILE CONTENTS =====\n")
    for p in changed:
        blob=git(root,"rev-parse",f"{args.head}:{p}")
        data=(root/p).read_bytes()
        raw=hashlib.sha256(data).hexdigest()
        parts.append(f"\n----- BEGIN FILE {p} | blob {blob} | sha256 {raw} -----\n")
        try:
            txt=data.decode("utf-8")
        except UnicodeDecodeError:
            txt="<NON-UTF8 FILE; IDENTITY/HASH ABOVE>\n"
        parts.append(txt)
        if not txt.endswith("\n"):
            parts.append("\n")
        parts.append(f"----- END FILE {p} -----\n")

    parts.extend(["\n===== COMPLETE BASELINE-TO-SUCCESSOR2 DIFF =====\n",diff,"\n===== END DIFF =====\n"])

    parts.append("\n===== EXACT PACKET-GENERATION TEST LOGS =====\n")
    for lp in sorted(args.log_dir.glob("*.txt")):
        parts.append(f"\n----- BEGIN LOG {lp.name} -----\n")
        txt=lp.read_text(encoding="utf-8", errors="replace")
        parts.append(txt)
        if not txt.endswith("\n"):
            parts.append("\n")
        parts.append(f"----- END LOG {lp.name} -----\n")

    parts.append("""
===== INDEPENDENT REVIEW CONTRACT =====

Review ONE exact frozen successor2 only.

DO NOT STOP AFTER THE FIRST FINDING.
Enumerate ALL Critical, High, Medium, and Low findings.

Do not treat prior fixes as proven merely because they are labeled FIXED above.
Re-falsify the implementation and the invariant/evidence machinery from the exact contents in this packet.

Pay special attention to the defect families that caused the prior loop:
- cross-branch/stale runtime composition;
- parser hidden-finding grammar, multiline markers, heading injection, arbitrary prefix decoration;
- parser/hash double reads and exact-artifact binding;
- workflow CLI compatibility;
- historical-vs-current evidence identity;
- complete semantic-inventory verification;
- direct path traversal / descriptor confinement;
- exact evidence lineage/schema/archive binding;
- queue state/manual/provenance semantics;
- checkout-independent tests and evidence;
- packet identity drift or hand-copied claims.

For every finding provide:
1. Finding ID
2. Severity
3. Exact file/function/contract
4. Concrete failure / false-green / omission path
5. Why the current invariant/test is insufficient
6. Narrow recommended solution
7. Exact regression test to add/change
8. Whether the finding invalidates the successor2 freeze
9. Merge-blocking YES/NO
10. Classification: code / evidence / runtime / policy

Return ONLY sections A-J:

A. OVERALL_DISPOSITION
Exactly one: BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE

B. EXACT_CANDIDATE_IDENTITY
Repeat baseline, frozen successor commit/tree, changed-file count, packet run/job, Linux evidence run/job.

C. CRITICAL_FINDINGS
Use NONE. if none.

D. HIGH_FINDINGS
Use NONE. if none.

E. MEDIUM_FINDINGS
Use NONE. if none.

F. LOW_FINDINGS
Use NONE. if none.

G. INVARIANT_ASSESSMENT
Assess every load-bearing invariant and whether exact evidence supports it.

H. INTEGRATION_AND_EVIDENCE_ASSESSMENT
Assess one-tree composition, historical-vs-current evidence separation, exact Linux evidence, and packet completeness.

I. REMEDIATION_PLAN
For every finding give the smallest safe fix and exact regression. If no findings, state NONE.

J. FINAL_GATE
State exactly:
- Frozen successor2 eligible for bounded merge consideration: YES or NO.
- Broader Stage2 semantic authority granted: NO.
- Runtime qualification granted: NO.
- Release/deployment/production authority granted: NO.
- Automatic six-slice cadence restoration: NO.
- Fallback-to-3 remains ACTIVE.
""")

    packet="".join(parts)
    args.out.write_text(packet, encoding="utf-8", newline="\n")
    raw=args.out.read_bytes()
    print(str(args.out))
    print("packet_sha256="+hashlib.sha256(raw).hexdigest())
    print("packet_bytes="+str(len(raw)))
    print("packet_lines="+str(packet.count("\n")+1))

if __name__=="__main__":
    main()
