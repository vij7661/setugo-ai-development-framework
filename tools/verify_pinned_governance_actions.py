"""Require immutable full-SHA third-party actions in governance workflows."""
import re
from pathlib import Path
WORKFLOWS=(Path(".github/workflows/governance-candidate-platform-review.yml"),Path(".github/workflows/governance-evidence-receipt-ingestion.yml"),Path(".github/workflows/governance-manual-review-ingestion.yml"))
PIN=re.compile(r"^[0-9a-f]{40}$")
def _value(line):
    match=re.match(r"^\s*-?\s*uses\s*:\s*(.*?)\s*$",line)
    if not match:return None
    value=match.group(1);quote=None;out=[]
    for char in value:
        if char in "\"'" and (quote is None or quote==char):quote=None if quote else char
        if char=="#" and quote is None:break
        out.append(char)
    value="".join(out).strip()
    if len(value)>=2 and value[0]==value[-1] and value[0] in "\"'":value=value[1:-1].strip()
    return value
def verify(text):
    uses=[value for line in text.splitlines() if (value:=_value(line)) is not None]
    if not uses:raise ValueError("governance workflow has no actions")
    for value in uses:
        if value.startswith("./"):
            if not re.fullmatch(r"\./[A-Za-z0-9._/-]+",value) or ".." in value.split("/"):raise ValueError(f"unsafe local action: {value}")
            continue
        if value.startswith("docker://"):
            if not re.fullmatch(r"docker://[^\s@]+@sha256:[0-9a-f]{64}",value):raise ValueError(f"mutable Docker action reference: {value}")
            continue
        if "@" not in value or not PIN.fullmatch(value.rsplit("@",1)[1]):raise ValueError(f"mutable action reference: {value}")
def main():
    for path in WORKFLOWS:verify(path.read_text(encoding="utf-8"))
    print(f"PINNED_GOVERNANCE_ACTIONS_PASS workflows={len(WORKFLOWS)}")
if __name__=="__main__":main()
