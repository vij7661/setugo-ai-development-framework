"""Build one self-contained independent-review packet from one exact frozen candidate."""
from __future__ import annotations
import argparse, hashlib, subprocess
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
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--job", required=True)
    args=ap.parse_args()

    root=args.candidate_root.resolve()
    assert git(root,"rev-parse","HEAD")==args.head
    assert git(root,"rev-parse","HEAD^{tree}")==args.tree

    changed=git(root,"diff","--name-only",f"{args.base}..{args.head}").splitlines()
    diff=subprocess.check_output(
        ["git","-C",str(root),"diff","--no-ext-diff","--unified=80",f"{args.base}..{args.head}"],
        text=True,
    )

    parts=[
        "R8 v15-r1 — FROZEN POST-SG1 SINGLE-CANDIDATE INDEPENDENT REVIEW\n\n",
        "USE ONLY THIS PACKET.\n",
        "Do not use prior conversation history, GitHub access, external APIs, model recollection, or prior packet conclusions.\n\n",
        "This review intentionally replaces the earlier multi-PR packet process.\n",
        "There is ONE candidate under review.\n\n",
        "EXACT FROZEN CANDIDATE\n",
        f"baseline: {args.base}\n",
        f"candidate commit: {args.head}\n",
        f"candidate tree: {args.tree}\n",
        "frozen branch: frozen/r8-v15-r1-post-sg1-integration-candidate-2026-09-26\n",
        f"packet-generation workflow run: {args.run_id}\n",
        f"packet-generation job: {args.job}\n",
        "authority_effect: NONE\n",
        "fallback-to-3: ACTIVE\n",
        "six-slice cadence restored: NO\n\n",
        "PROCESS CHANGE\n",
        "- #42/#43/#44/#46/#50 are no longer reviewed as separately moving heads.\n",
        "- Their implementation changes are composed into this one tree.\n",
        "- #44 is the single runtime winner for the #44/#46 overlap.\n",
        "- #46 consumes the runtime in this exact tree.\n",
        "- historical review packet/report artifacts were excluded from candidate implementation composition.\n",
        "- all evidence below is regenerated from this exact candidate SHA.\n\n",
        f"CHANGED FILE COUNT: {len(changed)}\n",
        "CHANGED FILES\n",
    ]

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
            parts.append(data.decode("utf-8"))
        except UnicodeDecodeError:
            parts.append("<NON-UTF8 FILE OMITTED FROM TEXT; HASH/IDENTITY ABOVE>\n")
        if not parts[-1].endswith("\n"):
            parts.append("\n")
        parts.append(f"----- END FILE {p} -----\n")

    parts.extend(["\n===== COMPLETE BASELINE-TO-CANDIDATE DIFF =====\n",diff,"\n===== END DIFF =====\n"])
    parts.append("\n===== EXACT TEST / INVARIANT LOGS =====\n")
    for lp in sorted(args.log_dir.glob("*.txt")):
        parts.append(f"\n----- BEGIN LOG {lp.name} -----\n")
        text=lp.read_text(encoding="utf-8", errors="replace")
        parts.append(text)
        if not text.endswith("\n"):
            parts.append("\n")
        parts.append(f"----- END LOG {lp.name} -----\n")

    parts.append("""
===== INDEPENDENT REVIEW INSTRUCTIONS =====

Review this ONE exact frozen candidate only.

DO NOT STOP AFTER THE FIRST FINDING.
Enumerate ALL Critical, High, Medium, and Low findings.

For every finding provide:
1. Finding ID
2. Severity
3. Exact file/function/contract
4. Concrete failure/false-green/omission path
5. Why current invariant/test is insufficient
6. Narrow recommended solution
7. Exact tests to add/change
8. Whether it invalidates candidate freeze
9. Merge-blocking YES/NO
10. Classification: code / evidence / runtime / policy

Explicitly test whether the old loop classes are closed:
- stale #44/#46 runtime composition;
- parser punctuation/hidden-finding variants;
- parser/hash double-read;
- unbound CI preflight identity;
- partial semantic-inventory verification;
- non-exact evidence lineage;
- queue/provenance ambiguity;
- hand-copied/stale test counts;
- packet identity drift.

Return ONLY sections A-J:

A. OVERALL_DISPOSITION
Exactly one: BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE

B. EXACT_CANDIDATE_IDENTITY
Repeat baseline, candidate commit/tree, changed-file count, packet workflow run/job.

C. CRITICAL_FINDINGS
Use NONE. if none.

D. HIGH_FINDINGS
Use NONE. if none.

E. MEDIUM_FINDINGS
Use NONE. if none.

F. LOW_FINDINGS
Use NONE. if none.

G. INVARIANT_ASSESSMENT
Assess each load-bearing invariant and whether the packet/test evidence proves it.

H. INTEGRATION_ASSESSMENT
Assess composition as ONE tree, especially #44/#46 and exact evidence binding.

I. REMEDIATION_PLAN
For every finding, give smallest safe fix + exact regression test. If none, state NONE.

J. FINAL_GATE
State:
- Frozen candidate eligible for bounded merge consideration: YES or NO.
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
