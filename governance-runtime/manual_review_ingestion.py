"""Governed manual independent-review ingestion; evidence only, never merge."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from q15_review_merge_gate import review_merge_evidence_eligible

def ingest(*,review_path,freeze_attestation_path,linux_statement_path,packet_statement_path,packet_payload_path,receipt_path,receipt_sha256,expected_identity,root=Path(".")):
    eligible=review_merge_evidence_eligible(review_path=review_path,freeze_attestation_path=freeze_attestation_path,linux_statement_path=linux_statement_path,review_packet_statement_path=packet_statement_path,packet_payload_path=packet_payload_path,governed_receipt_path=receipt_path,expected_receipt_sha256=receipt_sha256,expected_identity=expected_identity,root=root)
    return {"schema":"r8-manual-review-eligibility/v1","candidate_commit":expected_identity["candidate_commit"],"candidate_tree":expected_identity["candidate_tree"],"review_evidence_eligible":eligible,"authority_effect":"NONE","automatic_merge":False,"runtime_authority":False,"release_authority":False,"deployment_authority":False,"production_authority":False}

def main():
    p=argparse.ArgumentParser()
    for name in ("review","freeze-attestation","linux-statement","packet-statement","packet-payload","receipt","receipt-sha256","expected-identity","output"):p.add_argument("--"+name,required=True)
    a=p.parse_args(); identity=json.loads(Path(a.expected_identity).read_text(encoding="utf-8"))
    result=ingest(review_path=Path(a.review),freeze_attestation_path=Path(a.freeze_attestation),linux_statement_path=Path(a.linux_statement),packet_statement_path=Path(a.packet_statement),packet_payload_path=Path(a.packet_payload),receipt_path=Path(a.receipt),receipt_sha256=a.receipt_sha256,expected_identity=identity)
    Path(a.output).write_text(json.dumps(result,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8")
if __name__=="__main__":main()
