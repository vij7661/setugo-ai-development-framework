"""Structural self-check for Q17 post-freeze ingestion workflows."""
from pathlib import Path
from verify_q16_invariant_workflow import executable_run_text
import re
REQUIRED={
 Path(".github/workflows/governance-evidence-receipt-ingestion.yml"):("trusted/governance-runtime/stage_evidence_data.py","trusted/governance-runtime/github_evidence_ingestion.py"),
 Path(".github/workflows/governance-manual-review-ingestion.yml"):("trusted/governance-runtime/trusted_receipt_fetch.py","trusted/governance-runtime/stage_evidence_data.py","trusted/governance-runtime/manual_review_ingestion.py"),
}
def verify(path,text):
    executable=executable_run_text(text)
    missing=[item for item in REQUIRED[path] if item not in executable]
    if missing:raise ValueError(f"load-bearing ingestion command missing: {missing}")
    if "workflow_dispatch" not in text or "AUTHORITY_EFFECT: NONE" not in text:raise ValueError("manual evidence-only boundary missing")
    if 'ref: "${{ env.TRUSTED_VERIFIER_COMMIT }}"' not in text or 'TRUSTED_VERIFIER_COMMIT:' not in text or 'TRUSTED_VERIFIER_TREE:' not in text or "path: trusted" not in text or "path: evidence-ref" not in text:raise ValueError("trusted code and evidence data checkouts not separated")
    if 'ref: "${{ github.sha }}"' in text:raise ValueError("mutable workflow head used as verifier root")
    if not re.search(r"TRUSTED_VERIFIER_COMMIT:\s*[0-9a-f]{40}",text) or not re.search(r"TRUSTED_VERIFIER_TREE:\s*[0-9a-f]{40}",text):raise ValueError("trusted verifier root must be exact SHA/tree")
    if any(token in text for token in ("python3 evidence-ref/","bash evidence-ref/","evidence-ref/.github/","evidence-ref/governance-runtime")):raise ValueError("evidence ref may not supply executable code")
    if any(token in executable for token in ("gh pr merge","git merge","git push")):raise ValueError("ingestion workflow may not mutate merge state")
    if path.name=="governance-manual-review-ingestion.yml":
        if "actions: read" not in text or 'env: {GITHUB_TOKEN: "${{ github.token }}"}' not in text: raise ValueError("manual ingestion requires read-only Actions token")
        if "actions: write" in text or "contents: write" in text: raise ValueError("manual ingestion write permission forbidden")
        if "receipt_workflow_file" in text or "receipt_workflow_identity" in text: raise ValueError("producer identity may not be caller-selected")
        if "fetch_committed_review.py" not in executable or "--committed-review staged/committed-review.txt" not in executable: raise ValueError("committed review must come from trusted GitHub fetch")
def main():
    for path in REQUIRED:verify(path,path.read_text(encoding="utf-8"))
    print("Q17_INGESTION_WORKFLOW_SELF_CHECK_PASS")
if __name__=="__main__":main()
