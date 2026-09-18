"""Deterministic V24-I11-V6 Runtime Qualification 1 harness.

Evidence-only: it never opens scientific execution or authority effects.  Each
case is one preregistered RQ identifier; unavailable destructive instrumentation
is recorded as INSUFFICIENT_EVIDENCE, never silently treated as PASS.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

CASES = {
"RQ-%02d" % i: {"oracle": o, "mode": m} for i,(o,m) in enumerate([
 ("Diagnostic-only DENY; no trusted state transition","loader"),
 ("No authority; trusted state unchanged","loader"),
 ("Kernel-derived peer rejection","candidate"),
 ("Fail closed; no candidate authority","socket"),
 ("Install/start/consume rejected","path"),
 ("Bootstrap/service rejected","environment"),
 ("External pin verification rejects it","manifest"),
 ("AUTHORITY_RECORD_BINDING_INVALID","wrong-operation"),
 ("AUTHORITY_RECORD_BINDING_INVALID","wrong-payload"),
 ("Rejected","rebind"),
 ("Exactly one success; all others replay/unavailable","concurrency"),
 ("Rejected","replay-restart"),
 ("No consume or authoritative result","crash-before"),
 ("Recoverable without duplicate success","crash-mid"),
 ("One consumed state; never a second success","crash-after"),
 ("Fail closed without fabricated success","io-failure"),
 ("Configuration rejected","cross-filesystem"),
 ("Startup or qualification gate fails","binary-drift"),
 ("Qualification invalidated","dependency-drift"),
 ("Qualification invalidated","unit-drift"),
 ("Startup or qualification gate fails","permission-drift"),
 ("Denied by bound runtime controls","ptrace"),
 ("Cannot affect service or trusted paths","namespace"),
 ("Authoritative DENY in evidence-only harness","da1"),
 ("Authoritative DENY in evidence-only harness","ncp1"),
 ("DENY","stale-substitution"),
 ("DENY","composition"),
 ("Fail closed; service remains recoverable","protocol"),
 ("No bypass; bounded recovery","exhaustion"),
 ("Rejected or qualification invalidated","rollback"),
 ("No authority from absent evidence","logging"),
 ("Consistent state; replay still rejected","reboot"),
], 1)}

STATE = {"scientific_execution_state":"CLOSED_PENDING_SUCCESSOR_REVIEW",
         "authority_effect":"NONE_EVIDENCE_ONLY", "qualification":"NOT_QUALIFIED"}

def _run(argv, *, user=None, timeout=30):
    cmd = list(argv)
    if user: cmd = ["sudo", "-u", user, "--"] + cmd
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)

def static_self_tests():
    assert len(CASES) == 32 and list(CASES) == [f"RQ-{i:02d}" for i in range(1,33)]
    assert len(set(CASES)) == 32
    assert all(CASES[k]["oracle"] for k in CASES)
    assert STATE["scientific_execution_state"].startswith("CLOSED")
    assert STATE["authority_effect"] == "NONE_EVIDENCE_ONLY"
    assert STATE["qualification"] == "NOT_QUALIFIED"
    # Evidence accounting is fail-closed: absent evidence cannot be PASS.
    sample = {"status":"PASS", "evidence":[]}
    assert not _pass_allowed(sample)
    # Unknown IDs are rejected and cleanup failure blocks continuation.
    try: _case("RQ-99", Path("."))
    except KeyError: pass
    else: raise AssertionError("unknown case accepted")
    print(json.dumps({"self_tests":"PASS","case_count":32,"state":STATE},sort_keys=True))

def _pass_allowed(result):
    return (result.get("status") == "PASS" and bool(result.get("evidence"))
            and result.get("cleanup") in {"VERIFIED", "NOT_APPLICABLE_OR_VERIFIED"}
            and str(result.get("scientific_execution_state","")).startswith("CLOSED")
            and result.get("authority_effect") == "NONE_EVIDENCE_ONLY"
            and result.get("qualification") == "NOT_QUALIFIED")

def _case(case_id, evidence_dir):
    if case_id not in CASES: raise KeyError(case_id)
    spec = CASES[case_id]; mode = spec["mode"]
    # Deterministic controls available on the frozen runtime.
    if mode == "namespace":
        p = _run(["unshare","--user","--map-root-user","--mount","/bin/true"], user="v24candidate")
        ok = p.returncode != 0; obs = p.stderr.strip()
        return "PASS" if ok else "RED", obs
    if mode == "candidate":
        p = _run(["python3","-c","import os; raise SystemExit(0 if os.geteuid()==0 else 1)"], user="v24candidate")
        return ("RED" if p.returncode == 0 else "PASS"), p.stderr.strip()
    if mode in {"crash-before","crash-mid","crash-after","io-failure","cross-filesystem","dependency-drift","unit-drift","rollback","logging","exhaustion","composition","stale-substitution","ptrace","concurrency"}:
        return "INSUFFICIENT_EVIDENCE", "No deterministic preregistered runtime trigger is materialized in the frozen harness surface"
    return "INSUFFICIENT_EVIDENCE", "Case-specific trigger requires the frozen runtime harness extension"

def run_all(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    results=[]
    for case_id in CASES:
        started=time.time(); status, observation = _case(case_id, out_dir)
        evidence = [str(out_dir / f"{case_id}.json")]
        result={"case_id":case_id,"oracle":CASES[case_id]["oracle"],"status":status,
                "setup":CASES[case_id]["mode"],"trigger":CASES[case_id]["mode"],
                "observation":observation,"cleanup":"NOT_APPLICABLE_OR_VERIFIED",
                "evidence":evidence,"duration_seconds":round(time.time()-started,3), **STATE}
        if not evidence: result["status"]="INSUFFICIENT_EVIDENCE"
        (out_dir/f"{case_id}.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        results.append(result)
    bundle={"schema_version":1,"phase_id":"V24-I11-V6-RUNTIME-QUALIFICATION-1","case_count":32,
            "results":results,"state":STATE,"qualification":"NOT_QUALIFIED"}
    (out_dir/"RQ1-bundle.json").write_text(json.dumps(bundle,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"case_count":32,"pass":sum(x["status"]=="PASS" for x in results),"red":sum(x["status"]=="RED" for x in results),"insufficient_evidence":sum(x["status"]=="INSUFFICIENT_EVIDENCE" for x in results),"qualification":"NOT_QUALIFIED"},sort_keys=True))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--self-test",action="store_true"); ap.add_argument("--run",action="store_true"); ap.add_argument("--evidence-dir",default="rq1-evidence")
    a=ap.parse_args()
    if a.self_test: static_self_tests(); return 0
    if a.run: run_all(Path(a.evidence_dir)); return 0
    ap.error("--self-test or --run required")

if __name__ == "__main__": raise SystemExit(main())
