"""Read-only GitHub evidence ingestion entry point for governed receipts."""
from __future__ import annotations
import argparse,json,os,re,base64
from pathlib import Path
from urllib.request import Request,urlopen
from governed_evidence_receipt import canonical_bytes,ingest_verified_receipt

def canonical_governed_ref(value:str,*,allow_tags:bool=False)->str:
    if not isinstance(value,str) or not value or value.strip()!=value or "\\" in value:
        raise ValueError("malformed governed ref")
    if value.startswith("refs/"): value=value[5:]
    if value.startswith("heads/"): result=value
    elif value.startswith("tags/"):
        if not allow_tags: raise ValueError("tag refs are not allowed")
        result=value
    elif value.startswith("frozen/"): result="heads/"+value
    else: raise ValueError("ambiguous governed ref namespace")
    parts=result.split("/")
    if any(not p or p in {".",".."} or not re.fullmatch(r"[A-Za-z0-9._-]+",p) for p in parts):
        raise ValueError("malformed governed ref")
    return result

class GitHubREST:
    def __init__(self,token):self.token=token
    def _get(self,url):
        req=Request(url,headers={"Authorization":f"Bearer {self.token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"setugo-governed-evidence-ingestion/1.0"},method="GET")
        with urlopen(req,timeout=60) as r:return json.loads(r.read().decode())
    def _get_bytes(self,url):
        req=Request(url,headers={"Authorization":f"Bearer {self.token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"setugo-governed-evidence-ingestion/2.0"},method="GET")
        with urlopen(req,timeout=60) as r:return r.read()
    def resolve_ref(self,repository,ref,*,allow_tags=False):
        canonical=canonical_governed_ref(ref,allow_tags=allow_tags)
        return self._get(f"https://api.github.com/repos/{repository}/git/ref/{canonical}")["object"]["sha"]
    def run(self,repository,run_id):
        v=self._get(f"https://api.github.com/repos/{repository}/actions/runs/{run_id}");return {"id":v["id"],"workflow_file":v["path"],"head_sha":v.get("head_sha"),"repository":repository,"conclusion":v["conclusion"]}
    def job(self,repository,job_id):
        v=self._get(f"https://api.github.com/repos/{repository}/actions/jobs/{job_id}");return {"id":v["id"],"run_id":v["run_id"],"workflow_identity":v["name"],"conclusion":v["conclusion"]}
    def artifact(self,repository,artifact_id):
        v=self._get(f"https://api.github.com/repos/{repository}/actions/artifacts/{artifact_id}");return {"id":v["id"],"run_id":v["workflow_run"]["id"],"digest":v["digest"],"archive_download_url":v["archive_download_url"]}
    def download_artifact(self,repository,artifact_id,download_url):
        expected=f"https://api.github.com/repos/{repository}/actions/artifacts/{artifact_id}/zip"
        if download_url != expected: raise ValueError("artifact download URL mismatch")
        return self._get_bytes(download_url)
    def git_blob(self,repository,revision,path):return self._get(f"https://api.github.com/repos/{repository}/contents/{path}?ref={revision}")["sha"]
    def git_blob_bytes(self,repository,revision,path):
        value=self._get(f"https://api.github.com/repos/{repository}/contents/{path}?ref={revision}")
        if value.get("encoding")!="base64":raise ValueError("Git content is not base64")
        return base64.b64decode(value["content"],validate=True)

    def committed_review(self, repository, revision, path):
        """Read review bytes and Git identity through the trusted GitHub API."""
        if not isinstance(revision,str) or not re.fullmatch(r"[0-9a-f]{40}",revision): raise ValueError("review revision must be an immutable commit")
        if not isinstance(path,str) or not path or path.startswith("/") or "\\" in path or any(p in {"",".",".."} for p in path.split("/")): raise ValueError("unsafe review path")
        raw=self.git_blob_bytes(repository,revision,path)
        return raw,self.git_blob(repository,revision,path)

def main():
    p=argparse.ArgumentParser();p.add_argument("--spec",required=True);p.add_argument("--artifact-locations",required=True);p.add_argument("--trusted-verifier-commit",required=True);p.add_argument("--trusted-verifier-tree",required=True);p.add_argument("--evidence-ref",required=True);p.add_argument("--output",required=True);a=p.parse_args()
    token=os.environ.get("GITHUB_TOKEN","");
    if not token:raise RuntimeError("GITHUB_TOKEN required")
    base=Path(a.spec).resolve().parent
    spec=json.loads(Path(a.spec).read_text(encoding="utf-8"));locations=json.loads(Path(a.artifact_locations).read_text(encoding="utf-8"));blobs={"freeze_attestation":(base/"freeze-attestation.json").read_bytes(),"independent_review":(base/"independent-review.txt").read_bytes()}
    receipt=ingest_verified_receipt(spec,GitHubREST(token),blobs,artifact_locations=locations,trusted_verifier_commit=a.trusted_verifier_commit,trusted_verifier_tree=a.trusted_verifier_tree,evidence_ref=a.evidence_ref);Path(a.output).write_bytes(canonical_bytes(receipt))
if __name__=="__main__":main()
