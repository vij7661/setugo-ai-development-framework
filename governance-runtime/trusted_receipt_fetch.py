"""Trusted, read-only retrieval of the receipt produced by the GitHub verifier workflow."""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from github_evidence_ingestion import GitHubREST
from governed_evidence_receipt import _safe_archive,sha256_bytes,verify_receipt_v2_structure,verify_trusted_code_binding
TRUSTED_RECEIPT_WORKFLOW_FILE=".github/workflows/governance-evidence-receipt-ingestion.yml"
TRUSTED_RECEIPT_JOB_IDENTITY="receipt-only"
def fetch(*,api,repository,artifact_id,run_id,job_id,archive_digest,verifier_commit,verifier_tree,expected_producer_head=None,workflow_file=TRUSTED_RECEIPT_WORKFLOW_FILE,workflow_identity=TRUSTED_RECEIPT_JOB_IDENTITY,member="governed-evidence-receipt.json"):
    run=api.run(repository,str(run_id));job=api.job(repository,str(job_id));artifact=api.artifact(repository,str(artifact_id))
    expected_head=expected_producer_head or verifier_commit
    if str(run.get("id"))!=str(run_id) or run.get("repository")!=repository or run.get("workflow_file")!=TRUSTED_RECEIPT_WORKFLOW_FILE or run.get("head_sha")!=expected_head or run.get("conclusion")!="success":raise ValueError("trusted receipt producer run mismatch")
    if str(job.get("id"))!=str(job_id) or str(job.get("run_id"))!=str(run_id) or job.get("workflow_identity")!=workflow_identity or job.get("conclusion")!="success":raise ValueError("trusted receipt job mismatch")
    if str(artifact.get("id"))!=str(artifact_id) or str(artifact.get("run_id"))!=str(run_id) or artifact.get("digest")!=archive_digest:raise ValueError("trusted receipt artifact mismatch")
    archive=api.download_artifact(repository,str(artifact_id),artifact.get("archive_download_url"))
    if "sha256:"+sha256_bytes(archive)!=archive_digest:raise ValueError("trusted receipt archive digest mismatch")
    members=_safe_archive(archive,{member});raw=members[member];receipt=json.loads(raw.decode("utf-8"))
    if not verify_receipt_v2_structure(receipt) or not verify_trusted_code_binding(receipt,expected_commit=verifier_commit,expected_tree=verifier_tree):raise ValueError("trusted receipt verifier binding mismatch")
    return raw,{"schema":"r8-trusted-receipt-proof/v2","source":"GITHUB_ACTIONS_ARTIFACT_DOWNLOAD","repository":repository,"run_id":str(run_id),"job_id":str(job_id),"producer_head_sha":expected_head,"workflow_file":TRUSTED_RECEIPT_WORKFLOW_FILE,"workflow_identity":TRUSTED_RECEIPT_JOB_IDENTITY,"artifact_id":str(artifact_id),"archive_digest":archive_digest,"member":member,"receipt_sha256":sha256_bytes(raw),"verifier_commit":verifier_commit,"verifier_tree":verifier_tree}
def main():
    p=argparse.ArgumentParser()
    for name in ("repository","artifact-id","run-id","job-id","archive-digest","verifier-commit","verifier-tree","output","proof-output"):p.add_argument("--"+name,required=True)
    p.add_argument("--expected-producer-head",required=False)
    p.add_argument("--member",default="governed-evidence-receipt.json");a=p.parse_args();token=os.environ.get("GITHUB_TOKEN")
    if not token:raise RuntimeError("GITHUB_TOKEN required")
    raw,proof=fetch(api=GitHubREST(token),repository=a.repository,artifact_id=a.artifact_id,run_id=a.run_id,job_id=a.job_id,archive_digest=a.archive_digest,verifier_commit=a.verifier_commit,verifier_tree=a.verifier_tree,expected_producer_head=a.expected_producer_head,member=a.member)
    Path(a.output).write_bytes(raw);Path(a.proof_output).write_text(json.dumps(proof,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
if __name__=="__main__":main()
