"""Fetch the authoritative committed review through trusted GitHub read APIs."""
from __future__ import annotations
import argparse,json,os,re
from pathlib import Path
from github_evidence_ingestion import GitHubREST

def fetch(*,api,repository,revision,path,receipt):
    review=receipt.get("independent_review",{})
    source=receipt.get("review_source",{})
    expected_repo=source.get("repository",receipt.get("repository"))
    if expected_repo!=repository or source.get("revision")!=revision or source.get("path")!=path:
        raise ValueError("committed review source is not receipt-bound")
    if not re.fullmatch(r"[0-9a-f]{40}",revision) or path.startswith("/") or "\\" in path or any(p in {"",".",".."} for p in path.split("/")):
        raise ValueError("unsafe committed review identity")
    raw,blob=api.committed_review(repository,revision,path)
    import hashlib
    if hashlib.sha256(raw).hexdigest()!=review.get("committed_review_sha256") or blob!=review.get("git_blob"):
        raise ValueError("committed review bytes/blob mismatch")
    return raw

def main():
    p=argparse.ArgumentParser()
    for name in ("repository","revision","path","receipt","output"):p.add_argument("--"+name,required=True)
    a=p.parse_args(); token=os.environ.get("GITHUB_TOKEN")
    if not token: raise RuntimeError("GITHUB_TOKEN required")
    receipt=json.loads(Path(a.receipt).read_text(encoding="utf-8"))
    Path(a.output).write_bytes(fetch(api=GitHubREST(token),repository=a.repository,revision=a.revision,path=a.path,receipt=receipt))
if __name__=="__main__":main()
