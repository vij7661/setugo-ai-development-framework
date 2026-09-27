"""Exact executable-step contract for the active Q18 invariant workflow."""
from pathlib import Path
WORKFLOW=Path(".github/workflows/r8-v15-r1-post-sg1-integration-invariant-gate.yml")
CONTRACT={
 "Verify exact candidate invariants":"python3 tools/verify_r8_v15_r1_post_sg1_integration_invariants.py",
 "Stage1 exact regression guard before successor matrix":'python3 tools/verify_r8_v15_r1_ig1_successor3_exact_candidate.py "$RUNNER_TEMP/q18-stage1-before"',
 "Review parser adversarial tests":"python3 tools/test_r8_v15_r1_review_contract_parser.py",
 "Independent A-J parser adversarial tests":"python3 tools/test_r8_v15_r1_independent_review_parser.py",
 "Activation parser validation":"python3 tools/validate_r8_v15_r1_stage2_sg1_activation_gate_parser.py",
 "Review preflight exact-artifact tests":"python3 tools/test_r8_v15_r1_stage2_sg1_review_preflight.py",
 "Semantic inventory tests":"python3 tools/test_r8_v15_r1_stage2_semantic_gap_inventory.py",
 "Reviewer evidence delivery and solution-contract tests":"python3 governance-runtime/test_reviewer_evidence_delivery.py",
 "Platform review materialization v2 tests":"python3 governance-runtime/test_platform_candidate_review_v2_materialization.py",
 "Platform review request-integrity tests":"python3 governance-runtime/test_platform_candidate_review_request_integrity.py",
 "Real-path reviewer delivery integration tests":"python3 governance-runtime/test_platform_candidate_review_delivery_integration.py",
 "External freeze-attestation v2 tests":"python3 governance-runtime/test_freeze_attestation.py",
 "Candidate-bound execution-evidence tests":"python3 governance-runtime/test_candidate_execution_evidence.py",
 "Governed evidence receipt tests":"python3 governance-runtime/test_governed_evidence_receipt.py",
 "GitHub ref and ingestion adapter tests":"python3 governance-runtime/test_github_evidence_ingestion.py",
 "Evidence data-only staging tests":"python3 governance-runtime/test_stage_evidence_data.py",
 "Review merge identity-gate tests":"python3 governance-runtime/test_q15_review_merge_gate.py",
 "Manual review ingestion gate tests":"python3 governance-runtime/test_manual_review_ingestion.py",
 "Real provider single-attempt contract tests":"python3 governance-runtime/test_platform_candidate_review_retry_contract.py",
 "Provider API request contract preservation tests":"python3 governance-runtime/test_provider_api_request_contract.py",
 "Runtime safe-read tests":"python3 governance-runtime/test_r8_v15_r1_runtime_toctou_hardening.py",
 "Evidence integrity tests":"python3 tools/test_r8_evidence_bundle_integrity.py",
 "Queue tests":"python3 tools/test_r8_work_queue.py",
 "Historical lifecycle interpretation tests":"python3 tools/test_candidate_lifecycle_interpretation.py",
 "Pinned governance action lint":"python3 tools/verify_pinned_governance_actions.py",
 "Pinned governance action adversarial tests":"python3 tools/test_verify_pinned_governance_actions.py",
 "Q18 ingestion workflow structural self-check":"python3 tools/verify_q17_ingestion_workflows.py",
 "Q18 ingestion workflow adversarial tests":"python3 tools/test_verify_q17_ingestion_workflows.py",
 "Verify invariant workflow test completeness":"python3 tools/verify_q16_invariant_workflow.py",
 "Invariant workflow self-check adversarial tests":"python3 tools/test_verify_q16_invariant_workflow.py",
 "Stage1 exact regression guard after successor matrix":'python3 tools/verify_r8_v15_r1_ig1_successor3_exact_candidate.py "$RUNNER_TEMP/q18-stage1-after"',
 "Verify worktree clean":'test -z "$(git status --porcelain=v1)"',
}
REQUIRED=tuple(CONTRACT.values())
def steps(text):
 lines=text.replace("\r\n","\n").splitlines();result={};current=None;i=0
 while i<len(lines):
  stripped=lines[i].strip()
  if stripped.startswith("- name:"):current=stripped.split(":",1)[1].strip();result[current]={}
  elif current and stripped.startswith("continue-on-error:"):result[current]["continue-on-error"]=stripped.split(":",1)[1].strip()
  elif current and stripped.startswith("if:"):result[current]["if"]=stripped.split(":",1)[1].strip()
  elif current and stripped.startswith("run:"):
   tail=stripped[4:].strip()
   if tail in {"|","|-",">",">-"}:
    indent=len(lines[i])-len(lines[i].lstrip());body=[];i+=1
    while i<len(lines) and (not lines[i].strip() or len(lines[i])-len(lines[i].lstrip())>indent):
     if lines[i].strip() and not lines[i].strip().startswith("#"):body.append(lines[i].strip())
     i+=1
    result[current]["run"]="\n".join(body).strip();continue
   result[current]["run"]=tail
  i+=1
 return result
def verify(text):
 inventory=steps(text)
 for name,command in CONTRACT.items():
  step=inventory.get(name)
  if not step or step.get("run")!=command:raise ValueError(f"exact governed step missing or altered: {name}")
  if step.get("continue-on-error") not in (None,"false"):raise ValueError(f"continue-on-error forbidden: {name}")
  if "if" in step:raise ValueError(f"conditional skip forbidden: {name}")
  if any(token in step["run"] for token in ("|| true","set +e","\n","echo ","printf ","<<","exit 0")):raise ValueError(f"weakened governed command: {name}")
 if 'PYTHONDONTWRITEBYTECODE: "1"' not in text or 'AUTHORITY_EFFECT: "NONE"' not in text:raise ValueError("workflow governance environment missing")
def executable_run_text(text):return "\n".join(v.get("run","") for v in steps(text).values())
def main():verify(WORKFLOW.read_text(encoding="utf-8"));print(f"Q18_INVARIANT_WORKFLOW_SELF_CHECK_PASS required={len(CONTRACT)}")
if __name__=="__main__":main()
