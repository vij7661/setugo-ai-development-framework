"""Fail closed if the committed Q16 invariant workflow loses required coverage."""
from pathlib import Path

WORKFLOW = Path(".github/workflows/r8-v15-r1-post-sg1-integration-invariant-gate.yml")
REQUIRED = (
    "tools/verify_r8_v15_r1_post_sg1_integration_invariants.py",
    "tools/test_r8_v15_r1_review_contract_parser.py",
    "tools/test_r8_v15_r1_independent_review_parser.py",
    "tools/test_r8_v15_r1_stage2_sg1_review_preflight.py",
    "tools/validate_r8_v15_r1_stage2_sg1_activation_gate_parser.py",
    "tools/test_r8_v15_r1_stage2_semantic_gap_inventory.py",
    "governance-runtime/test_r8_v15_r1_runtime_toctou_hardening.py",
    "tools/test_r8_evidence_bundle_integrity.py",
    "tools/test_r8_work_queue.py",
    "governance-runtime/test_provider_api_request_contract.py",
    "governance-runtime/test_reviewer_evidence_delivery.py",
    "governance-runtime/test_platform_candidate_review_v2_materialization.py",
    "governance-runtime/test_platform_candidate_review_request_integrity.py",
    "governance-runtime/test_platform_candidate_review_delivery_integration.py",
    "governance-runtime/test_freeze_attestation.py",
    "governance-runtime/test_candidate_execution_evidence.py",
    "governance-runtime/test_governed_evidence_receipt.py",
    "governance-runtime/test_q15_review_merge_gate.py",
    "governance-runtime/test_manual_review_ingestion.py",
    "governance-runtime/test_platform_candidate_review_retry_contract.py",
    "tools/test_candidate_lifecycle_interpretation.py",
    "tools/verify_pinned_governance_actions.py",
    "tools/test_verify_pinned_governance_actions.py",
    "tools/verify_q17_ingestion_workflows.py",
    "tools/test_verify_q17_ingestion_workflows.py",
    "tools/verify_r8_v15_r1_ig1_successor3_exact_candidate.py",
    "tools/verify_q16_invariant_workflow.py",
    "tools/test_verify_q16_invariant_workflow.py",
    "git status --porcelain=v1",
)

def verify(text: str) -> None:
    executable = executable_run_text(text)
    missing = [item for item in REQUIRED if executable.count(item) != (2 if item.endswith("verify_r8_v15_r1_ig1_successor3_exact_candidate.py") else 1)]
    if missing: raise ValueError(f"Q16 invariant workflow coverage missing/duplicated: {missing}")
    if "PYTHONDONTWRITEBYTECODE: \"1\"" not in text: raise ValueError("bytecode suppression missing")
    if 'AUTHORITY_EFFECT: "NONE"' not in text: raise ValueError("workflow authority effect must remain NONE")

def executable_run_text(text: str) -> str:
    """Extract only YAML run scalar content; comments and other fields are inert."""
    lines=text.replace("\r\n","\n").splitlines(); blocks=[]; index=0
    while index < len(lines):
        line=lines[index]; stripped=line.lstrip(); indent=len(line)-len(stripped)
        if not stripped.startswith("run:"):
            index+=1;continue
        tail=stripped[4:].strip()
        if tail and tail not in {"|",">","|-",">-"} and not tail.startswith("#"):
            blocks.append(tail)
        index+=1
        if tail in {"|",">","|-",">-"}:
            body=[]
            while index < len(lines):
                child=lines[index]; child_stripped=child.lstrip(); child_indent=len(child)-len(child_stripped)
                if child_stripped and child_indent <= indent:break
                if child_stripped and not child_stripped.startswith("#"):body.append(child_stripped)
                index+=1
            blocks.append("\n".join(body))
    return "\n".join(blocks)

def main():
    verify(WORKFLOW.read_text(encoding="utf-8")); print(f"Q16_INVARIANT_WORKFLOW_SELF_CHECK_PASS required={len(REQUIRED)}")

if __name__ == "__main__": main()
