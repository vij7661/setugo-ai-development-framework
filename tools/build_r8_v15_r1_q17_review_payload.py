"""Build immutable Q17 independent-review payload."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path

def git(root,*args):
    return subprocess.check_output(["git","-C",str(root),*args],text=True).strip()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate-root",type=Path,required=True)
    ap.add_argument("--base",required=True)
    ap.add_argument("--head",required=True)
    ap.add_argument("--tree",required=True)
    ap.add_argument("--linux-statement",type=Path,required=True)
    ap.add_argument("--log-dir",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    root=a.candidate_root.resolve()
    assert git(root,"rev-parse","HEAD")==a.head
    assert git(root,"rev-parse","HEAD^{tree}")==a.tree
    changed=git(root,"diff","--name-only",f"{a.base}..{a.head}").splitlines()
    linux=json.loads(a.linux_statement.read_text(encoding="utf-8"))
    assert linux["candidate_commit"]==a.head and linux["candidate_tree"]==a.tree
    assert linux["baseline_commit"]==a.base and linux["changed_file_count"]==len(changed)
    diff=subprocess.check_output(["git","-C",str(root),"diff","--no-ext-diff","--unified=80",f"{a.base}..{a.head}"],text=True)

    p=[]
    p.append("R8 v15-r1 — Q17 FROZEN REVIEW-REMEDIATION SUCCESSOR — INDEPENDENT REVIEW PAYLOAD\n\n")
    p.append("USE ONLY THE FINAL Q17 REVIEW BUNDLE AS REVIEW MATERIAL.\n")
    p.append("Review ONE immutable frozen Q17 candidate. Do not rely on prior conversation history or proposer confidence.\n")
    p.append("DO NOT STOP AFTER THE FIRST FINDING. Enumerate ALL Critical, High, Medium, and Low findings.\n\n")
    p.append("===== EXACT CANDIDATE IDENTITY =====\n")
    p.append(f"baseline: {a.base}\n")
    p.append(f"frozen Q17 commit: {a.head}\n")
    p.append(f"frozen Q17 tree: {a.tree}\n")
    p.append("frozen branch: frozen/r8-v15-r1-q17-q16-review-successor-2026-09-27\n")
    p.append(f"changed-file count from baseline: {len(changed)}\n")
    p.append(f"exact Linux validation run/job: {linux['run_id']} / {linux['job_id']}\n")
    p.append(f"Linux statement SHA256: {linux['statement_sha256']}\n")
    p.append(f"Linux evidence payload digest: {linux['artifact_digest']}\n")
    p.append("authority_effect: NONE\nfallback-to-3: ACTIVE\nsix-slice cadence restored: NO\n\n")
    p.append("===== CANDIDATE-BOUND LINUX EXECUTION STATEMENT =====\n")
    p.append(a.linux_statement.read_text(encoding="utf-8"))
    if not p[-1].endswith("\n"): p.append("\n")
    p.append("===== END LINUX EXECUTION STATEMENT =====\n\n")
    p.append("===== Q17 LINEAGE =====\n")
    p.append("- SG-1 closure baseline: 7cd2787d85b189a4161f271ee131e42bd961140a.\n")
    p.append("- Frozen Q16 predecessor: 66b720bd33eb200428c64c31c50e8c5a1ce5cec1 / 78061fdbc0340f3025a056612836cf9b2df1a412.\n")
    p.append("- Q16 independent review 001 disposition: CHANGES_REQUIRED; Critical NONE; High H-01..H-04; Medium M-01..M-05; Low L-01..L-05.\n")
    p.append("- H-01 was adjudicated REJECTED_NOT_REPRODUCED because Q16 already failed closed on unsupported retry policy; Q17 adds direct real-path regression without adding retries.\n")
    p.append("- H-02/H-03/H-04, M-01..M-05, L-02/L-03 were accepted or narrowed; L-01/L-04/L-05 use safer alternative solutions.\n")
    p.append("- Q17 remains candidate-local PRE_FREEZE_READY; later freeze/review facts are external lifecycle evidence.\n")
    p.append("- Governed evidence receipt generation intentionally occurs only after a manual independent review exists; inspect the receipt/ingestion code as candidate behavior, not as pre-existing proof of itself.\n\n")
    p.append("===== Q17 REPAIR FAMILIES TO RE-FALSIFY =====\n")
    for line in [
      "Unsupported retry policies fail before provider transport; admitted Gemini behavior remains exactly one attempt.",
      "Governed evidence receipt verifies GitHub run/job/artifact/ref/blob associations through read-only APIs and exact digests.",
      "Exact independent-review bytes/hash/blob are bound before review parsing or merge-evidence eligibility.",
      "Invariant-workflow self-check inspects executable run blocks; comments cannot satisfy required commands.",
      "retry_policy receives the same normalized recursive governance/secret-key checks as other structured provider fields.",
      "Materialized review path requires mandatory coverage true, successful result status, exact provider identity and repository before provider invocation.",
      "Validated access manifest is persisted and its digest/mode/provider/repository/request/candidate identity are bound into execution evidence.",
      "URL and authenticated-MCP delivery modes bind logical subject separately from repository, commit, path, object/blob identity, digest and bytes.",
      "Manual independent-review ingestion is a real workflow path invoking the load-bearing review/merge evidence gate but cannot merge or grant authority.",
      "A-J parser enforces exact finding row order and controlled rows 9-11.",
      "Governance workflows pin third-party actions to immutable SHAs.",
      "Historical construction records are point-in-time evidence; later lifecycle interpretation comes from external structured evidence.",
      "Queue/external lifecycle discoverability does not mutate frozen predecessors."
    ]: p.append(f"- {line}\n")
    p.append("\n===== API REQUEST PRESERVATION BOUNDARY =====\n")
    p.append("- No API_REQUEST_SCHEMA_CHANGE is authorized.\n- No API_EXECUTION_BEHAVIOR_CHANGE is authorized.\n")
    p.append("- Same admitted logical request must preserve endpoint/method/model/prompt/payload/parameters/timeout/single-attempt retry/streaming/response behavior.\n")
    p.append("- Authentication remains transport-only and outside semantic fingerprints/evidence.\n\n")
    p.append("===== EXACT CHANGED FILE IDENTITIES =====\n")
    for f in changed:
        data=(root/f).read_bytes(); blob=git(root,"rev-parse",f"{a.head}:{f}")
        p.append(f"- {f} | blob {blob} | sha256 {hashlib.sha256(data).hexdigest()} | bytes {len(data)}\n")
    p.append("\n===== EXACT CHANGED FILE CONTENTS =====\n")
    for f in changed:
        data=(root/f).read_bytes(); blob=git(root,"rev-parse",f"{a.head}:{f}"); raw=hashlib.sha256(data).hexdigest()
        p.append(f"\n----- BEGIN FILE {f} | blob {blob} | sha256 {raw} -----\n")
        try: txt=data.decode("utf-8")
        except UnicodeDecodeError: txt="<NON-UTF8 FILE; IDENTITY/HASH ABOVE>\n"
        p.append(txt); p.append("" if txt.endswith("\n") else "\n"); p.append(f"----- END FILE {f} -----\n")
    p.extend(["\n===== COMPLETE BASELINE-TO-Q17 DIFF =====\n",diff,"\n===== END DIFF =====\n"])
    p.append("\n===== EXACT PACKET-GENERATION TEST LOGS =====\n")
    for lp in sorted(a.log_dir.glob("*.txt")):
        p.append(f"\n----- BEGIN LOG {lp.name} -----\n")
        txt=lp.read_text(encoding="utf-8",errors="replace"); p.append(txt); p.append("" if txt.endswith("\n") else "\n")
        p.append(f"----- END LOG {lp.name} -----\n")
    p.append(r"""
===== INDEPENDENT REVIEW CONTRACT =====

The FINAL REVIEW BUNDLE places the packet execution statement and external freeze-attestation v2 before this payload.
Candidate-local PRE_FREEZE_READY is construction-time state, not evidence that later external freeze/review did not occur.

Review the ONE exact frozen Q17 candidate identified above.
DO NOT STOP AFTER THE FIRST FINDING.
Enumerate ALL Critical, High, Medium, and Low findings.

Re-falsify in particular:
- whether unsupported retry-policy mutation really fails before urlopen and admitted behavior is exactly one attempt;
- whether governed evidence receipt verification truly anchors run/job/artifact/ref/blob associations to GitHub read-only evidence rather than trusting attacker-controlled receipt fields;
- whether artifact digest comparison proves the exact downloaded artifact bytes and cannot confuse ZIP digest with contained-file digest;
- whether exact review artifact raw hash/Git blob is load-bearing before parse/eligibility;
- whether manual-review ingestion actually invokes the gate on a real workflow path and remains evidence-only;
- whether workflow self-checks inspect executable YAML semantics rather than text that may live in comments or unrelated blocks;
- whether retry_policy and all structured provider subtrees receive normalized recursive forbidden-key checks while natural-language message content remains opaque;
- whether manifest truthfulness fields are bound to exact expected provider/repository/status/coverage before provider invocation;
- whether admitted access-manifest bytes/hash are persisted and bound to the execution envelope;
- whether URL/MCP exact source path/object/blob identity can be substituted while keeping matching bytes;
- whether A-J rows 2..11, YES/NO rows, and classification enums are enforced without rejecting valid historical evidence unexpectedly;
- whether pinned action verification can be bypassed with YAML aliases/composite/local references or whitespace;
- whether construction-time lifecycle prose can accidentally override later external lifecycle evidence;
- whether queue/external lifecycle pointers introduce self-reference or stale evidence;
- whether any new receipt/ingestion workflow creates write/merge/authority capability despite claims of evidence-only behavior;
- whether any Q17 repair introduces API request or execution behavior drift.

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
Repeat baseline, frozen Q17 commit/tree, changed-file count, packet run/job, Linux validation run/job.

C. CRITICAL_FINDINGS
Use NONE. if none.

D. HIGH_FINDINGS
Use NONE. if none.

E. MEDIUM_FINDINGS
Use NONE. if none.

F. LOW_FINDINGS
Use NONE. if none.

G. PERMANENT_INVARIANT_ASSESSMENT
Assess every Q17 repair family separately.

H. API_AND_REVIEWER_DELIVERY_ASSESSMENT
Assess actual Gemini request preservation, reviewer delivery, receipt/ingestion design, and authority boundaries.

I. REMEDIATION_PLAN
For every finding provide proposed remediation and exact regression/falsification test. Reviewer proposals remain advisory until implementer adjudication.

J. FINAL_GATE
State exactly:
- Frozen Q17 candidate eligible for bounded merge consideration: YES or NO.
- Broader Stage2 semantic authority granted: NO.
- Runtime qualification granted: NO.
- Release/deployment/production authority granted: NO.
- Automatic six-slice cadence restoration: NO.
- Fallback-to-3 remains ACTIVE.
""")
    payload="".join(p)
    a.out.write_text(payload,encoding="utf-8",newline="\n")
    raw=a.out.read_bytes()
    print("payload_sha256="+hashlib.sha256(raw).hexdigest())
    print("payload_bytes="+str(len(raw)))
    print("payload_lines="+str(payload.count("\n")+1))
    print("changed_file_count="+str(len(changed)))
if __name__=="__main__": main()
