"""Governed manual independent-review ingestion; evidence only, never merge."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from q15_review_merge_gate import review_merge_evidence_eligible
from governed_evidence_receipt import sha256_bytes,verify_receipt_v2_structure,verify_trusted_code_binding

def validate_trusted_receipt(receipt_path:Path, proof_path:Path, expected_sha256:str, verifier_commit:str, verifier_tree:str)->dict:
    raw=receipt_path.read_bytes()
    if sha256_bytes(raw)!=expected_sha256 or not proof_path.is_file():raise ValueError("trusted receipt bytes are not externally bound")
    receipt=json.loads(raw.decode("utf-8"));proof=json.loads(proof_path.read_text(encoding="utf-8"))
    if proof.get("schema")!="r8-trusted-receipt-proof/v1" or proof.get("source")!="GITHUB_ACTIONS_ARTIFACT_DOWNLOAD" or proof.get("receipt_sha256")!=expected_sha256:raise ValueError("trusted receipt proof malformed")
    if not verify_receipt_v2_structure(receipt) or not verify_trusted_code_binding(receipt,expected_commit=verifier_commit,expected_tree=verifier_tree):raise ValueError("trusted receipt verifier root mismatch")
    for key in ("repository","run_id","job_id","workflow_file","workflow_identity","artifact_id","archive_digest","member","verifier_commit","verifier_tree"):
        if not proof.get(key):raise ValueError("trusted receipt proof incomplete")
    if proof["verifier_commit"]!=verifier_commit or proof["verifier_tree"]!=verifier_tree:raise ValueError("trusted receipt verifier root mismatch")
    return receipt

def ingest(*,review_path,freeze_attestation_path,linux_statement_path,packet_statement_path,packet_payload_path,receipt_path,receipt_sha256,expected_identity=None,candidate_label=None,trusted_receipt_proof_path=None,committed_review_path=None,trusted_verifier_commit=None,trusted_verifier_tree=None,root=Path(".")):
    if Path(receipt_path).is_file():
        if not trusted_receipt_proof_path or not trusted_verifier_commit or not trusted_verifier_tree: raise ValueError("trusted receipt proof and verifier binding required")
        receipt=validate_trusted_receipt(Path(receipt_path),Path(trusted_receipt_proof_path),receipt_sha256,trusted_verifier_commit,trusted_verifier_tree)
        expected_identity={"baseline":receipt["candidate"]["baseline"],"candidate_commit":receipt["candidate"]["commit"],"candidate_tree":receipt["candidate"]["tree"],"changed_file_count":receipt["candidate"]["changed_file_count"],"frozen_ref":receipt["candidate"]["frozen_ref"],"packet_run_job":[receipt["packet"]["run_id"],receipt["packet"]["job_id"]],"linux_run_job":[receipt["linux"]["run_id"],receipt["linux"]["job_id"]],"candidate_label":candidate_label or ""}
    eligible=review_merge_evidence_eligible(review_path=review_path,freeze_attestation_path=freeze_attestation_path,linux_statement_path=linux_statement_path,review_packet_statement_path=packet_statement_path,packet_payload_path=packet_payload_path,governed_receipt_path=receipt_path,expected_receipt_sha256=receipt_sha256,expected_identity=expected_identity, trusted_receipt_proof_path=trusted_receipt_proof_path, committed_review_path=committed_review_path, trusted_verifier_commit=trusted_verifier_commit, trusted_verifier_tree=trusted_verifier_tree,root=root)
    return {"schema":"r8-manual-review-eligibility/v1","candidate_commit":expected_identity["candidate_commit"],"candidate_tree":expected_identity["candidate_tree"],"review_evidence_eligible":eligible,"authority_effect":"NONE","automatic_merge":False,"runtime_authority":False,"release_authority":False,"deployment_authority":False,"production_authority":False}

def main():
    p=argparse.ArgumentParser()
    for name in ("review","freeze-attestation","linux-statement","packet-statement","packet-payload","receipt","receipt-sha256","output"):p.add_argument("--"+name,required=True)
    p.add_argument("--expected-identity");p.add_argument("--candidate-label");p.add_argument("--trusted-receipt-proof");p.add_argument("--committed-review");p.add_argument("--trusted-verifier-commit");p.add_argument("--trusted-verifier-tree")
    a=p.parse_args(); identity=json.loads(Path(a.expected_identity).read_text(encoding="utf-8")) if a.expected_identity else None
    result=ingest(review_path=Path(a.review),freeze_attestation_path=Path(a.freeze_attestation),linux_statement_path=Path(a.linux_statement),packet_statement_path=Path(a.packet_statement),packet_payload_path=Path(a.packet_payload),receipt_path=Path(a.receipt),receipt_sha256=a.receipt_sha256,expected_identity=identity,candidate_label=a.candidate_label,trusted_receipt_proof_path=Path(a.trusted_receipt_proof) if a.trusted_receipt_proof else None,committed_review_path=Path(a.committed_review) if a.committed_review else None,trusted_verifier_commit=a.trusted_verifier_commit,trusted_verifier_tree=a.trusted_verifier_tree)
    Path(a.output).write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
if __name__=="__main__":main()
