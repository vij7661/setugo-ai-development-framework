"""Structural self-check for Q17 post-freeze ingestion workflows."""
from pathlib import Path
from verify_q16_invariant_workflow import executable_run_text
REQUIRED={
 Path(".github/workflows/governance-evidence-receipt-ingestion.yml"):("governance-runtime/github_evidence_ingestion.py",),
 Path(".github/workflows/governance-manual-review-ingestion.yml"):("governance-runtime/manual_review_ingestion.py",),
}
def verify(path,text):
    executable=executable_run_text(text)
    missing=[item for item in REQUIRED[path] if item not in executable]
    if missing:raise ValueError(f"load-bearing ingestion command missing: {missing}")
    if "workflow_dispatch" not in text or "AUTHORITY_EFFECT: NONE" not in text:raise ValueError("manual evidence-only boundary missing")
    if any(token in executable for token in ("gh pr merge","git merge","git push")):raise ValueError("ingestion workflow may not mutate merge state")
def main():
    for path in REQUIRED:verify(path,path.read_text(encoding="utf-8"))
    print("Q17_INGESTION_WORKFLOW_SELF_CHECK_PASS")
if __name__=="__main__":main()
