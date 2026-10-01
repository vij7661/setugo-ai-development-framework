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
 "Trusted receipt artifact-binding tests":"python3 governance-runtime/test_trusted_receipt_fetch.py",
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
EXPECTED_TOP=("name","on","permissions","env","jobs")
EXPECTED_BRANCHES=("integration/r8-v15-r1-post-sg1-convergence-2026-09-26","codex/r8-v15-r1-q16-q15-review-successor-2026-09-27","codex/r8-v15-r1-q17-q16-review-successor-2026-09-27","codex/r8-v15-r1-q18-q17-review-successor-2026-09-27")
SYNTAX_STEP="Syntax-check changed Python without writing bytecode"
SYNTAX_RUN_BODY='''set -euo pipefail
python3 - <<'PY'
import ast
from pathlib import Path
files = [
    "tools/r8_v15_r1_review_contract_parser.py",
    "tools/preflight_r8_v15_r1_stage2_sg1_review.py",
    "tools/r8_v15_r1_stage2_semantic_gap_inventory.py",
    "tools/r8_evidence_bundle_integrity.py",
    "tools/r8_work_queue.py",
    "tools/r8_v15_r1_independent_review_parser.py",
    "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
    "governance-runtime/candidate_execution_evidence.py",
    "governance-runtime/freeze_attestation.py",
    "governance-runtime/provider_api_request_contract.py",
    "governance-runtime/reviewer_evidence_delivery.py",
    "governance-runtime/q15_review_merge_gate.py",
    "governance-runtime/governed_evidence_receipt.py",
    "governance-runtime/github_evidence_ingestion.py",
    "governance-runtime/trusted_receipt_fetch.py",
    "governance-runtime/manual_review_ingestion.py",
    "governance-runtime/stage_evidence_data.py",
    "governance-runtime/trusted_receipt_fetch.py",
]
for name in files:
    ast.parse(Path(name).read_text(encoding="utf-8"), filename=name)
print(f"AST_SYNTAX_PASS files={len(files)}")
PY'''
SYNTAX_RUN_BODY="\n".join(line.strip() for line in SYNTAX_RUN_BODY.splitlines()).strip()

def structural_contract(text):
    """Validate the intentionally small, canonical workflow subset."""
    lines=text.replace("\r\n","\n").splitlines()
    if any("\t" in line for line in lines): raise ValueError("tabs are unsupported")
    # This is deliberately a closed contract, not a YAML best-effort parser.
    # Any execution-affecting mapping outside the reviewed shape is rejected.
    if __import__('re').search(r"(?m)^    (?:defaults|container|services|working-directory|continue-on-error|if|env):", text):
        # timeout-minutes is checked below at the one permitted job field.
        allowed_timeout = "    timeout-minutes: 30"
        residual = text.replace(allowed_timeout, "")
        if __import__('re').search(r"(?m)^    (?:defaults|container|services|working-directory|continue-on-error|if|env):", residual):
            raise ValueError("unsupported execution control")
    if __import__('re').search(r"\\(?:x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8}|N|L|P|0|a|b|t|n|r)|(^|\s)[&*][A-Za-z0-9_-]+|(^|\s)![A-Za-z]",text,__import__('re').M): raise ValueError("unsupported YAML representation")
    top=[line.strip().split(":",1)[0] for line in lines if line and not line.startswith(" ") and not line.startswith("#") and ":" in line]
    if tuple(top[:5])!=EXPECTED_TOP or set(top)!=set(EXPECTED_TOP): raise ValueError("workflow top-level structure changed")
    if "  workflow_dispatch:" not in lines or "  push:" not in lines: raise ValueError("workflow triggers changed")
    on_end=lines.index("permissions:") if "permissions:" in lines else 0
    branches=[line.strip()[2:] for line in lines[:on_end] if line.startswith("      - ")]
    if tuple(branches)!=EXPECTED_BRANCHES: raise ValueError("workflow push branches changed")
    if "permissions:" not in lines or "  contents: read" not in lines: raise ValueError("workflow permissions changed")
    if any(line.startswith("  ") and line.strip().startswith("actions:") for line in lines): raise ValueError("unexpected workflow permission")
    if "env:" not in lines: raise ValueError("workflow env structure changed")
    if "  PYTHONDONTWRITEBYTECODE: \"1\"" not in lines or "  AUTHORITY_EFFECT: \"NONE\"" not in lines: raise ValueError("workflow env values changed")
    jobs_start=lines.index("jobs:") if "jobs:" in lines else 0
    job_names=[line.strip() for line in lines[jobs_start:] if line.startswith("  ") and not line.startswith("    ") and line.strip().endswith(":")]
    job_headers=[line.strip().split(":",1)[0] for line in lines[jobs_start:] if line.startswith("    ") and not line.startswith("      ") and ":" in line]
    if job_names != ["invariant-gate:"] or job_headers != ["runs-on","timeout-minutes","steps"]: raise ValueError("job structure changed")
    if "    runs-on: ubuntu-24.04" not in lines or "    timeout-minutes: 30" not in lines: raise ValueError("job execution contract changed")
    steps_start=next((i for i,line in enumerate(lines[jobs_start:],jobs_start) if line.strip()=="steps:"),None)
    if steps_start is None: raise ValueError("steps missing")
    step_lines=[line.strip() for line in lines[steps_start+1:] if line.startswith("      - ")]
    if not step_lines or step_lines[0] != "- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1": raise ValueError("checkout step changed")
    names=[v.split(":",1)[1].strip() for v in step_lines[1:] if v.startswith("- name:")]
    expected_names=list(CONTRACT)
    expected_names.insert(expected_names.index("Stage1 exact regression guard after successor matrix"),"Syntax-check changed Python without writing bytecode")
    if names != expected_names: raise ValueError("step inventory/order changed")
    if len(step_lines) != len(expected_names)+1 or any(not v.startswith(("- name:","- uses:")) for v in step_lines): raise ValueError("unnamed or extra step")
    if any(v.startswith("- name:") and not v.split(":",1)[1].strip() for v in step_lines): raise ValueError("unnamed step")
    if any(v.startswith("- name:") for v in step_lines[1:]) and len(names)!=len(set(names)): raise ValueError("duplicate step name")
    if "        with:" not in lines or "          fetch-depth: 0" not in lines or "          persist-credentials: false" not in lines: raise ValueError("checkout options changed")
    with_start=lines.index("        with:")
    with_keys=[]
    with_values={}
    for line in lines[with_start+1:]:
        if line.startswith("      - "):
            break
        if line.startswith("          ") and not line.startswith("            ") and ":" in line:
            key,value=line.strip().split(":",1)
            with_keys.append(key);with_values[key]=value.strip()
    if with_keys != ["fetch-depth","persist-credentials"] or with_values != {"fetch-depth":"0","persist-credentials":"false"}:
        raise ValueError("checkout input contract changed")
    current="__checkout";seen={}
    for line in lines:
        if line.startswith("      - name:"):
            current=line.split(":",1)[1].strip();seen.setdefault(current,[])
        elif line.startswith("        ") and not line.startswith("          ") and ":" in line:
            seen.setdefault(current,[]).append(line.strip().split(":",1)[0])
    if seen.get("__checkout") != ["with"]: raise ValueError("checkout fields changed")
    for name,fields in seen.items():
        if name=="__checkout": continue
        allowed=["shell","run"] if name in {SYNTAX_STEP,"Verify worktree clean"} else ["run"]
        if fields != allowed: raise ValueError(f"step fields changed: {name}")
    return True
def steps(text):
 lines=text.replace("\r\n","\n").splitlines();result={};current=None;i=0
 while i<len(lines):
  stripped=lines[i].strip()
  if stripped.startswith("- name:"):current=stripped.split(":",1)[1].strip();result[current]={}
  elif current and stripped.startswith("continue-on-error:"):result[current]["continue-on-error"]=stripped.split(":",1)[1].strip()
  elif current and stripped.startswith("if:"):result[current]["if"]=stripped.split(":",1)[1].strip()
  elif current and stripped.startswith("shell:"):result[current]["shell"]=stripped.split(":",1)[1].strip().strip("\"'")
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
 structural_contract(text)
 if __import__('re').search(r"(?:^|[,{]|\n)\s*['\"](?:name|shell|run|if|continue-on-error)['\"]\s*:",text,__import__('re').M) or __import__('re').search(r"(^|\s)[&*][A-Za-z0-9_-]+",text) or __import__('re').search(r"\\(?:x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4})",text) or __import__('re').search(r"(^|\s)![A-Za-z]",text,__import__('re').M):raise ValueError("unsupported quoted/aliased workflow mapping")
 inventory=steps(text)
 for name,command in CONTRACT.items():
  step=inventory.get(name)
  if not step or step.get("run")!=command:raise ValueError(f"exact governed step missing or altered: {name}")
  if step.get("continue-on-error") not in (None,"false"):raise ValueError(f"continue-on-error forbidden: {name}")
  if "if" in step:raise ValueError(f"conditional skip forbidden: {name}")
  if step.get("shell") not in (None,"bash"):raise ValueError(f"unapproved shell semantics: {name}")
  if any(token in step["run"] for token in ("|| true","set +e","\n","echo ","printf ","<<","exit 0")):raise ValueError(f"weakened governed command: {name}")
 syntax=inventory.get(SYNTAX_STEP)
 if not syntax or syntax.get("shell")!="bash" or syntax.get("run")!=SYNTAX_RUN_BODY: raise ValueError("syntax step command contract changed")
 clean=inventory.get("Verify worktree clean")
 if not clean or clean.get("shell")!="bash" or clean.get("run")!='test -z "$(git status --porcelain=v1)"': raise ValueError("clean-worktree step contract changed")
 if 'PYTHONDONTWRITEBYTECODE: "1"' not in text or 'AUTHORITY_EFFECT: "NONE"' not in text:raise ValueError("workflow governance environment missing")
def executable_run_text(text):return "\n".join(v.get("run","") for v in steps(text).values())
def main():verify(WORKFLOW.read_text(encoding="utf-8"));print(f"Q18_INVARIANT_WORKFLOW_SELF_CHECK_PASS required={len(CONTRACT)}")
if __name__=="__main__":main()
