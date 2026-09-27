"""Read-only GitHub evidence ingestion entry point for governed receipts."""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from urllib.request import Request,urlopen
from governed_evidence_receipt import canonical_bytes,ingest_verified_receipt

class GitHubREST:
    def __init__(self,token):self.token=token
    def _get(self,url):
        req=Request(url,headers={"Authorization":f"Bearer {self.token}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"setugo-governed-evidence-ingestion/1.0"},method="GET")
        with urlopen(req,timeout=60) as r:return json.loads(r.read().decode())
    def resolve_ref(self,repository,ref):return self._get(f"https://api.github.com/repos/{repository}/git/ref/{ref.replace('refs/','',1)}")["object"]["sha"]
    def run(self,repository,run_id):
        v=self._get(f"https://api.github.com/repos/{repository}/actions/runs/{run_id}");return {"id":v["id"],"workflow_identity":f"{v['path']}/{v.get('name','')}","conclusion":v["conclusion"]}
    def job(self,repository,job_id):
        v=self._get(f"https://api.github.com/repos/{repository}/actions/jobs/{job_id}");return {"id":v["id"],"run_id":v["run_id"],"conclusion":v["conclusion"]}
    def artifact(self,repository,artifact_id):
        v=self._get(f"https://api.github.com/repos/{repository}/actions/artifacts/{artifact_id}");return {"id":v["id"],"run_id":v["workflow_run"]["id"],"digest":v["digest"]}
    def git_blob(self,repository,revision,path):return self._get(f"https://api.github.com/repos/{repository}/contents/{path}?ref={revision}")["sha"]

def main():
    p=argparse.ArgumentParser();p.add_argument("--spec",required=True);p.add_argument("--blob-map",required=True);p.add_argument("--artifact-locations",required=True);p.add_argument("--output",required=True);a=p.parse_args()
    token=os.environ.get("GITHUB_TOKEN","");
    if not token:raise RuntimeError("GITHUB_TOKEN required")
    spec=json.loads(Path(a.spec).read_text(encoding="utf-8"));mapping=json.loads(Path(a.blob_map).read_text(encoding="utf-8"));locations=json.loads(Path(a.artifact_locations).read_text(encoding="utf-8"));blobs={k:Path(v).read_bytes() for k,v in mapping.items()}
    receipt=ingest_verified_receipt(spec,GitHubREST(token),blobs,artifact_locations=locations);Path(a.output).write_bytes(canonical_bytes(receipt))
if __name__=="__main__":main()
