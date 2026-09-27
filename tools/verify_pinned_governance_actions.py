"""Require immutable full-SHA third-party actions in governance workflows."""
import re
from pathlib import Path
WORKFLOWS=(Path(".github/workflows/governance-candidate-platform-review.yml"),Path(".github/workflows/governance-evidence-receipt-ingestion.yml"),Path(".github/workflows/governance-manual-review-ingestion.yml"))
PIN=re.compile(r"^[0-9a-f]{40}$")
def verify(text):
    uses=[]
    for line in text.splitlines():
        match=re.match(r"^\s*-?\s*uses:\s*(\S+)\s*$",line)
        if match:uses.append(match.group(1))
    if not uses:raise ValueError("governance workflow has no actions")
    for value in uses:
        if value.startswith("./"):continue
        if "@" not in value or not PIN.fullmatch(value.rsplit("@",1)[1]):raise ValueError(f"mutable action reference: {value}")
def main():
    for path in WORKFLOWS:verify(path.read_text(encoding="utf-8"))
    print(f"PINNED_GOVERNANCE_ACTIONS_PASS workflows={len(WORKFLOWS)}")
if __name__=="__main__":main()
