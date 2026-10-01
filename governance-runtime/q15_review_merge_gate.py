"""Q15 review/merge evidence gate. This module grants no merge authority."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from freeze_attestation import load_and_verify  # noqa: E402
from governed_evidence_receipt import git_blob_sha1,git_text_blob_sha1,sha256_bytes, verify_receipt_files,verify_receipt_v2_structure,verify_trusted_code_binding  # noqa: E402
from trusted_receipt_fetch import TRUSTED_RECEIPT_WORKFLOW_FILE,TRUSTED_RECEIPT_JOB_IDENTITY  # noqa: E402
from r8_v15_r1_independent_review_parser import (  # noqa: E402
    eligible_for_bounded_merge,
    parse_independent_review_file,
)


def review_merge_evidence_eligible(*, review_path: Path, freeze_attestation_path: Path, linux_statement_path: Path, review_packet_statement_path: Path, packet_payload_path: Path, governed_receipt_path: Path, expected_receipt_sha256: str, expected_identity: dict, trusted_receipt_proof_path: Path|None = None, committed_review_path: Path|None = None, trusted_verifier_commit: str|None = None, trusted_verifier_tree: str|None = None, root: Path = ROOT) -> bool:
    receipt_raw=governed_receipt_path.read_bytes()
    if sha256_bytes(receipt_raw) != expected_receipt_sha256: return False
    receipt=json.loads(receipt_raw.decode("utf-8"))
    if receipt.get("schema")=="r8-governed-evidence-receipt/v2":
        if not verify_receipt_v2_structure(receipt): return False
        if not trusted_receipt_proof_path or not trusted_receipt_proof_path.is_file() or not committed_review_path or not committed_review_path.is_file() or not trusted_verifier_commit or not trusted_verifier_tree: return False
        proof=json.loads(trusted_receipt_proof_path.read_text(encoding="utf-8"))
        required=("schema","source","receipt_sha256","repository","run_id","job_id","workflow_file","workflow_identity","artifact_id","archive_digest","member","producer_head_sha","verifier_commit","verifier_tree")
        if proof.get("schema")!="r8-trusted-receipt-proof/v2" or any(not proof.get(k) for k in required): return False
        if proof.get("source")!="GITHUB_ACTIONS_ARTIFACT_DOWNLOAD" or proof.get("receipt_sha256")!=expected_receipt_sha256 or proof.get("repository")!=receipt.get("repository"): return False
        if proof.get("workflow_file")!=TRUSTED_RECEIPT_WORKFLOW_FILE or proof.get("workflow_identity")!=TRUSTED_RECEIPT_JOB_IDENTITY or proof.get("producer_head_sha")!=trusted_verifier_commit: return False
        if proof.get("run_id")!=str(proof["run_id"]) or proof.get("job_id")!=str(proof["job_id"]) or proof.get("artifact_id")!=str(proof["artifact_id"]): return False
        if not proof.get("archive_digest","").startswith("sha256:") or len(proof["archive_digest"])!=71 or proof.get("member")!="governed-evidence-receipt.json": return False
        if not verify_trusted_code_binding(receipt,expected_commit=trusted_verifier_commit,expected_tree=trusted_verifier_tree) or proof.get("verifier_commit")!=trusted_verifier_commit or proof.get("verifier_tree")!=trusted_verifier_tree: return False
        committed=committed_review_path.read_bytes()
        if receipt["independent_review"]["committed_review_sha256"]!=sha256_bytes(committed) or receipt["independent_review"]["git_blob"]!=git_blob_sha1(committed): return False
        if "review_source" in receipt and receipt["review_source"].get("repository")!=receipt.get("repository"): return False
        review_raw=review_path.read_bytes();freeze_raw=freeze_attestation_path.read_bytes()
        if "review_source" not in receipt and receipt["independent_review"]["original_upload_raw_sha256"]!=sha256_bytes(review_raw): return False
        if receipt["freeze_attestation"]!={"raw_sha256":sha256_bytes(freeze_raw),"git_blob":git_text_blob_sha1(freeze_raw)}: return False
    elif not verify_receipt_files(receipt,linux_statement_path=linux_statement_path,packet_statement_path=review_packet_statement_path,freeze_attestation_path=freeze_attestation_path,review_path=review_path,packet_payload_path=packet_payload_path): return False
    authoritative_review = committed_review_path if receipt.get("schema")=="r8-governed-evidence-receipt/v2" and "review_source" in receipt else review_path
    parsed = parse_independent_review_file(authoritative_review, candidate_label=expected_identity["candidate_label"])
    attestation = load_and_verify(freeze_attestation_path, root=root, require_v2=True)
    packet_statement = attestation["review_packet_statement"] if receipt.get("schema")=="r8-governed-evidence-receipt/v2" else json.loads(review_packet_statement_path.read_text(encoding="utf-8"))
    identity = parsed["identity"]
    exact_fields = ("baseline", "candidate_commit", "candidate_tree", "changed_file_count", "packet_run_job", "linux_run_job")
    for field in exact_fields:
        left,right=identity.get(field),expected_identity.get(field)
        if field.endswith("run_job"):
            if tuple(left or ()) != tuple(right or ()): return False
        elif left != right: return False
    rc=receipt["candidate"]
    if (rc["baseline"],rc["commit"],rc["tree"],rc["changed_file_count"],rc["frozen_ref"]) != (expected_identity["baseline"],expected_identity["candidate_commit"],expected_identity["candidate_tree"],expected_identity["changed_file_count"],expected_identity["frozen_ref"]): return False
    if attestation.get("candidate_commit") != expected_identity["candidate_commit"] or attestation.get("candidate_tree") != expected_identity["candidate_tree"]: return False
    linux, packet = attestation["linux_validation_statement"], attestation["review_packet_statement"]
    for statement in (linux, packet):
        if statement.get("baseline_commit") != expected_identity["baseline"] or statement.get("changed_file_count") != expected_identity["changed_file_count"]: return False
    if packet_statement != packet: return False
    if (linux["run_id"], linux["job_id"]) != tuple(expected_identity["linux_run_job"]): return False
    if (packet["run_id"], packet["job_id"]) != tuple(expected_identity["packet_run_job"]): return False
    return eligible_for_bounded_merge(parsed, freeze_verified=True)
