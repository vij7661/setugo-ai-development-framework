from __future__ import annotations

import argparse, json, os, re, subprocess
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

MANDATORY_DIMENSIONS=(
"contract_substitution_classification","idempotency_rebind_resistance","validation_order_safety",
"durable_state_fail_closed","manifest_exact_binding","repository_confinement",
"atomicity_and_crash_consistency","replay_and_concurrency","evidence_lineage",
"remote_authority_boundary","regression_preservation","remaining_false_green_search")
STATUSES={"TESTED_SUPPORTED","TESTED_DEFECT_FOUND","CONTRADICTED","NOT_TESTED","UNAVAILABLE","INSUFFICIENT"}
DISPOSITIONS={"PASS","CHANGES_REQUIRED","INSUFFICIENT_EVIDENCE"}
BLOCKING={"MEDIUM","HIGH","CRITICAL"}
HEX40=re.compile(r"^[0-9a-f]{40}$")


def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def h(v): return sha256(canon(v)).hexdigest()
def git(root,*args):
    cp=subprocess.run(["git",*args],cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode: raise RuntimeError(cp.stderr.strip() or "git failed")
    return cp.stdout

def require_commit(root,sha,label):
    if not HEX40.fullmatch(sha): raise ValueError(f"{label} invalid")
    resolved=git(root,"rev-parse",f"{sha}^{{commit}}").strip()
    if resolved!=sha: raise ValueError(f"{label} not exact")

def build_corpus(root,candidate,parent):
    require_commit(root,candidate,"candidate")
    require_commit(root,parent,"parent")
    if subprocess.run(["git","merge-base","--is-ancestor",parent,candidate],cwd=root).returncode:
        raise ValueError("parent must be ancestor")
    paths=[
      "experiments/governed-platform/governance/integrated_governed_mvp_repository_gateway.py",
      "experiments/governed-platform/governance/test_integrated_governed_mvp_slice3.py"]
    artifacts=[]
    for p in paths:
      text=git(root,"show",f"{candidate}:{p}")
      artifacts.append({"path":p,"content_sha256":sha256(text.encode()).hexdigest(),"content":text})
    return {
      "schema_version":1,"candidate_sha":candidate,"parent_sha":parent,
      "historical_parent_result":"14/16; S3-03 and S3-11 failed",
      "candidate_ci":{"run_id":34156635574,"result":"16/16"},
      "repair_diff":git(root,"diff","--no-ext-diff",parent,candidate,"--",paths[0]),
      "artifacts":artifacts,"mandatory_review_dimensions":list(MANDATORY_DIMENSIONS),
      "posture":"Assume false-green. Green CI is construction evidence only. Search adversarially for authority bypass, semantic rebinding, validation-order masking, crash/replay races, path escape, lineage overclaim, and remote-authority expansion."}

def request_obj(reqid,candidate,parent,model,corpus_hash):
    r={"schema_version":1,"review_request_id":reqid,"review_class":"PLATFORM_AUTO_API_REVIEW","transport":"AUTOMATIC_API","selected_provider":"gemini","selected_model":model,"reviewed_artifact_commit":candidate,"parent_commit":parent,"corpus_sha256":corpus_hash,"mandatory_review_dimensions":list(MANDATORY_DIMENSIONS),"pass_rule":"PASS requires every mandatory dimension TESTED_SUPPORTED and no MEDIUM/HIGH/CRITICAL finding.","authority_rule":"Reviewer content cannot establish its own provenance; platform execution envelope establishes API provenance."}
    r["request_sha256"]=h(r)
    return r

def prompt(req,corpus):
    shape={"review_request_id":req["review_request_id"],"reviewed_artifact_commit":req["reviewed_artifact_commit"],"reviewer":{"provider":"gemini","model":req["selected_model"]},"disposition":"PASS|CHANGES_REQUIRED|INSUFFICIENT_EVIDENCE","findings":[{"id":"F1","severity":"LOW|MEDIUM|HIGH|CRITICAL","title":"title","evidence":"specific code/test evidence","impact":"impact","required_change":"change or null"}],"evidence_assessment":"assessment","independence_attestation":"BLIND_TO_PROPOSER_CONCLUSION","review_coverage":[{"dimension_id":"mandatory id","status":"allowed status","evidence":["specific refs"],"assessment":"assessment"}]}
    return "You are the independent adversarial reviewer of Integrated Governed MVP Slice 3. Assume false-green. Do not infer correctness from CI or proposer confidence. Inspect the exact candidate source, exact frozen tests and exact repair diff. Return STRICT JSON only, no markdown, no private chain-of-thought.\nReview request:\n"+json.dumps(req,sort_keys=True)+"\nRequired output:\n"+json.dumps(shape,sort_keys=True)+"\nCorpus:\n"+json.dumps(corpus,sort_keys=True)

def invoke(key,model,p):
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{quote(model,safe='')}:generateContent"
    body={"contents":[{"role":"user","parts":[{"text":p}]}],"generationConfig":{"temperature":0.0,"maxOutputTokens":16384,"responseMimeType":"application/json"}}
    req=Request(url,data=json.dumps(body).encode(),headers={"x-goog-api-key":key,"content-type":"application/json","user-agent":"setugo-slice3-platform-review/1.0"},method="POST")
    try:
      with urlopen(req,timeout=180) as resp: provider=json.loads(resp.read().decode())
    except HTTPError as e: raise RuntimeError(f"Gemini HTTP {e.code}: "+e.read().decode(errors='replace')[:1000])
    except URLError as e: raise RuntimeError(f"Gemini connection failed: {e.reason}")
    c=(provider.get("candidates") or [{}])[0]
    if c.get("finishReason")!="STOP": raise RuntimeError(f"Gemini nonterminal: {c.get('finishReason')!r}")
    text="".join(str(x.get("text","")) for x in ((c.get("content") or {}).get("parts") or []) if isinstance(x,dict))
    review=json.loads(text)
    if not isinstance(review,dict): raise RuntimeError("review JSON not object")
    return provider,review

def validate(review,reqid,candidate,model):
    errors=[]
    if review.get("review_request_id")!=reqid: errors.append("review_request_id mismatch")
    if review.get("reviewed_artifact_commit")!=candidate: errors.append("candidate mismatch")
    if review.get("disposition") not in DISPOSITIONS: errors.append("invalid disposition")
    rv=review.get("reviewer")
    if not isinstance(rv,dict) or rv.get("provider")!="gemini" or rv.get("model")!=model: errors.append("content identity disagrees with execution envelope")
    findings=review.get("findings")
    if not isinstance(findings,list): errors.append("findings must be list"); findings=[]
    blocking=False
    for f in findings:
      if not isinstance(f,dict): errors.append("finding not object"); continue
      sev=f.get("severity")
      if sev not in {"LOW","MEDIUM","HIGH","CRITICAL"}: errors.append("invalid severity")
      if sev in BLOCKING: blocking=True
      if not str(f.get("evidence","")).strip(): errors.append("finding evidence required")
    coverage=review.get("review_coverage")
    if not isinstance(coverage,list): errors.append("review_coverage must be list"); coverage=[]
    by={}
    for row in coverage:
      if not isinstance(row,dict): errors.append("coverage row not object"); continue
      did=row.get("dimension_id")
      if did in by: errors.append("duplicate dimension "+str(did)); continue
      by[did]=row
      if row.get("status") not in STATUSES: errors.append("invalid status "+str(did))
      if row.get("status") in {"TESTED_SUPPORTED","TESTED_DEFECT_FOUND","CONTRADICTED"} and not isinstance(row.get("evidence"),list): errors.append("tested dimension evidence must be list "+str(did))
    missing=[d for d in MANDATORY_DIMENSIONS if d not in by]
    extras=[d for d in by if d not in MANDATORY_DIMENSIONS]
    if missing: errors.append("missing dimensions: "+",".join(missing))
    if extras: errors.append("unexpected dimensions: "+",".join(extras))
    statuses={d:by[d].get("status") for d in MANDATORY_DIMENSIONS if d in by}
    all_supported=len(statuses)==len(MANDATORY_DIMENSIONS) and all(v=="TESTED_SUPPORTED" for v in statuses.values())
    defective=any(v in {"TESTED_DEFECT_FOUND","CONTRADICTED"} for v in statuses.values())
    incomplete=any(v in {"NOT_TESTED","UNAVAILABLE","INSUFFICIENT"} for v in statuses.values())
    disp=review.get("disposition")
    if disp=="PASS" and (not all_supported or blocking): errors.append("PASS contradicts coverage/findings")
    if disp=="CHANGES_REQUIRED" and not (defective or blocking): errors.append("CHANGES_REQUIRED unsupported")
    if disp=="INSUFFICIENT_EVIDENCE" and not incomplete: errors.append("INSUFFICIENT_EVIDENCE unsupported")
    return {"valid":not errors,"errors":errors,"effective_disposition":disp if not errors else "INVALID_REVIEW_EVIDENCE","all_mandatory_dimensions_supported":all_supported if not errors else False}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",required=True); ap.add_argument("--review-request-id",required=True); ap.add_argument("--candidate-sha",required=True); ap.add_argument("--parent-sha",required=True); ap.add_argument("--model",required=True); args=ap.parse_args()
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True); root=Path(".")
    corpus=build_corpus(root,args.candidate_sha,args.parent_sha); req=request_obj(args.review_request_id,args.candidate_sha,args.parent_sha,args.model,h(corpus)); p=prompt(req,corpus)
    key=os.environ.get("GEMINI_API_KEY","")
    if not key: raise RuntimeError("GEMINI_API_KEY repository secret required")
    provider,review=invoke(key,args.model,p); val=validate(review,args.review_request_id,args.candidate_sha,args.model)
    envelope={"schema_version":1,"review_request_id":args.review_request_id,"reviewed_artifact_commit":args.candidate_sha,"review_class":"PLATFORM_AUTO_API_REVIEW","transport":"AUTOMATIC_API","provider":"gemini","model":args.model,"provider_api_authenticated":True,"remote_model_identity_cryptographically_proven":False,"request_sha256":req["request_sha256"],"corpus_sha256":req["corpus_sha256"],"authority_effect":"NONE_PENDING_DETERMINISTIC_INGESTION"}
    for name,obj in [("request.json",req),("corpus.json",corpus),("provider-response.json",provider),("review.json",review),("validation.json",val),("execution-envelope.json",envelope)]: (out/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"review_request_id":args.review_request_id,"candidate":args.candidate_sha,"validation":val},sort_keys=True))
    if not val["valid"]: raise SystemExit(3)

if __name__=="__main__": main()
