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
    "governance-runtime/test_q15_review_merge_gate.py",
    "tools/verify_q16_invariant_workflow.py",
    "tools/test_verify_q16_invariant_workflow.py",
    "git status --porcelain=v1",
)

def verify(text: str) -> None:
    missing = [item for item in REQUIRED if text.count(item) != 1]
    if missing: raise ValueError(f"Q16 invariant workflow coverage missing/duplicated: {missing}")
    if "PYTHONDONTWRITEBYTECODE: \"1\"" not in text: raise ValueError("bytecode suppression missing")
    if 'AUTHORITY_EFFECT: "NONE"' not in text: raise ValueError("workflow authority effect must remain NONE")

def main():
    verify(WORKFLOW.read_text(encoding="utf-8")); print(f"Q16_INVARIANT_WORKFLOW_SELF_CHECK_PASS required={len(REQUIRED)}")

if __name__ == "__main__": main()
