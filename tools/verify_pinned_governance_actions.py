"""Structural, scope-complete immutable-action verifier for governed workflows."""
import re
from pathlib import Path
PIN=re.compile(r"^[0-9a-f]{40}$")
GOVERNED_WORKFLOW_NAMES=("governance-candidate-platform-review.yml","governance-evidence-receipt-ingestion.yml","governance-manual-review-ingestion.yml","governance-review-request-integrity.yml","r8-v15-r1-post-sg1-integration-invariant-gate.yml")
WORKFLOWS=tuple(Path(".github/workflows")/name for name in GOVERNED_WORKFLOW_NAMES)
def _strip_comment(value):
    quote=None;out=[]
    for char in value:
        if char in "\"'" and (quote is None or quote==char):quote=None if quote else char
        if char=="#" and quote is None:break
        out.append(char)
    value="".join(out).strip()
    if len(value)>=2 and value[0]==value[-1] and value[0] in "\"'":value=value[1:-1].strip()
    return value
def uses_nodes(text):
    """Find YAML mapping keys in block and flow style without trusting formatting."""
    # This verifier intentionally accepts only the governed YAML subset. Quoted
    # mapping keys, aliases and anchors are rejected rather than ignored.
    if re.search(r"(?:^|[,{]|\n)\s*['\"](?:uses|shell|run|if|continue-on-error)['\"]\s*:",text,re.M) or re.search(r"(^|\s)[&*][A-Za-z0-9_-]+",text):
        raise ValueError("unsupported quoted/aliased YAML mapping")
    found=[]
    for line in text.replace("\r\n","\n").splitlines():
        quote=None;i=0
        while i<len(line)-5:
            if line[i] in "\"'" and (quote is None or quote==line[i]):quote=None if quote else line[i];i+=1;continue
            if quote is None and (i==0 or not (line[i-1].isalnum() or line[i-1] in "_-")) and line[i:i+5]=="uses:":
                j=i+5;start=j
                while j<len(line) and line[j].isspace():j+=1
                start=j;quote2=None
                while j<len(line):
                    ch=line[j]
                    if ch in "\"'" and (quote2 is None or quote2==ch):quote2=None if quote2 else ch
                    if quote2 is None and ch in ",}":break
                    j+=1
                value=_strip_comment(line[start:j])
                if value:found.append(value)
                i=j;continue
            i+=1
    return found
def verify(text):
    uses=uses_nodes(text)
    if not uses:raise ValueError("governed workflow has no actions")
    for value in uses:
        if value.startswith("./"):
            if not re.fullmatch(r"\./[A-Za-z0-9._/-]+",value) or any(part in {"..",""} for part in value[2:].split("/")):raise ValueError(f"unsafe local action: {value}")
        elif value.startswith("docker://"):
            if not re.fullmatch(r"docker://[^\s@]+@sha256:[0-9a-f]{64}",value):raise ValueError(f"mutable Docker action reference: {value}")
        elif "@" not in value or not PIN.fullmatch(value.rsplit("@",1)[1]):raise ValueError(f"mutable action reference: {value}")
def verify_inventory(paths=WORKFLOWS):
    expected={Path(".github/workflows")/name for name in GOVERNED_WORKFLOW_NAMES}
    actual=set(paths)
    discovered=set(Path(".github/workflows").glob("governance-*.yml")) | {Path(".github/workflows/r8-v15-r1-post-sg1-integration-invariant-gate.yml")}
    if discovered!=expected:raise ValueError(f"governed workflow inventory mismatch missing={discovered-expected} extra={expected-discovered}")
    if actual!=expected:raise ValueError(f"governed workflow inventory mismatch missing={expected-actual} extra={actual-expected}")
    for path in paths:
        if not path.is_file():raise ValueError(f"governed workflow missing: {path}")
        verify(path.read_text(encoding="utf-8"))
def main():verify_inventory();print(f"PINNED_GOVERNANCE_ACTIONS_PASS workflows={len(WORKFLOWS)}")
if __name__=="__main__":main()
