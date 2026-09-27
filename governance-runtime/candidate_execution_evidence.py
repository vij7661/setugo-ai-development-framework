"""Build candidate-bound Linux/packet evidence statements without granting authority."""
from __future__ import annotations
import argparse, json, re, subprocess
from pathlib import Path
from freeze_attestation import canonical_sha256, verify_execution_statement

KINDS={"LINUX_VALIDATION":"SUCCESS","REVIEW_PACKET":"GENERATED"}
def build_statement(*,kind,run_id,job_id,workflow_identity,baseline_commit,candidate_commit,candidate_tree,changed_file_count,conclusion,artifact_digest):
    value={"schema":"r8-candidate-execution-evidence/v1","kind":kind,"run_id":str(run_id),"job_id":str(job_id),"workflow_identity":workflow_identity,"baseline_commit":baseline_commit,"candidate_commit":candidate_commit,"candidate_tree":candidate_tree,"changed_file_count":changed_file_count,"conclusion":conclusion,"artifact_digest":artifact_digest}
    value["statement_sha256"]=canonical_sha256(value)
    if kind not in KINDS or conclusion != KINDS[kind] or not verify_execution_statement(value,kind=kind,commit=candidate_commit,tree=candidate_tree): raise ValueError("invalid candidate execution statement")
    return value
def verify_git_identity(root,baseline,c,t,changed_file_count):
    subprocess.check_call(["git","rev-parse","--verify",f"{baseline}^{{commit}}"],cwd=root,stdout=subprocess.DEVNULL)
    got=subprocess.check_output(["git","rev-parse",f"{c}^{{tree}}"],cwd=root,text=True).strip()
    if got != t: raise ValueError("candidate commit/tree mismatch")
    changed=subprocess.check_output(["git","diff","--name-only",f"{baseline}..{c}"],cwd=root,text=True).splitlines()
    if len(changed) != changed_file_count: raise ValueError("candidate changed-file count mismatch")
def main():
    p=argparse.ArgumentParser(); p.add_argument("--kind",choices=sorted(KINDS),required=True); p.add_argument("--run-id",required=True); p.add_argument("--job-id",required=True); p.add_argument("--workflow-identity",required=True); p.add_argument("--baseline-commit",required=True); p.add_argument("--candidate-commit",required=True); p.add_argument("--candidate-tree",required=True); p.add_argument("--changed-file-count",type=int,required=True); p.add_argument("--conclusion",required=True); p.add_argument("--artifact-digest",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    verify_git_identity(Path("."),a.baseline_commit,a.candidate_commit,a.candidate_tree,a.changed_file_count)
    v=build_statement(kind=a.kind,run_id=a.run_id,job_id=a.job_id,workflow_identity=a.workflow_identity,baseline_commit=a.baseline_commit,candidate_commit=a.candidate_commit,candidate_tree=a.candidate_tree,changed_file_count=a.changed_file_count,conclusion=a.conclusion,artifact_digest=a.artifact_digest)
    Path(a.output).write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")
if __name__=="__main__": main()
