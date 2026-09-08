from __future__ import annotations

import argparse, json, os, re, subprocess
from hashlib import sha256
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from review_protocol import verify_review_request

HEX40=re.compile(r"^[0-9a-f]{40}$")
ALLOWED_STATUSES={"CONTRADICTED","INACCESSIBLE","INSUFFICIENT","NOT_TESTED","TESTED_DEFECT_FOUND","TESTED_SUPPORTED","UNAVAILABLE"}
ALLOWED_DISPOSITIONS={"PASS","BOUNDED_PASS","FAIL","NOT_TESTED","INSUFFICIENT_EVIDENCE","CHANGES_REQUIRED"}
BLOCKING={"MEDIUM","HIGH","CRITICAL"}

def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
def digest(v): return sha256(canon(v)).hexdigest()
def git(root,*args):
    cp=subprocess.run(["git",*args],cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",errors="strict")
    if cp.returncode: raise RuntimeError(cp.stderr.strip() or "git failed")
    return cp.stdout

def verify_request_integrity(request):
    ok, reason = verify_review_request(request)
    if not ok:
        raise ValueError(reason)
    return request

def require_commit(root,sha,label):
    if not HEX40.fullmatch(sha): raise ValueError(f"{label} invalid")
    if git(root,"rev-parse",f"{sha}^{{commit}}").strip()!=sha: raise ValueError(f"{label} not exact")

def build_corpus(root,request):
    candidate=request["artifact"]["commit"]
    require_commit(root,candidate,"candidate")
    evidence=[]
    for ref in request.get("evidence_refs",[]):
        if ref.get("type")!="file": continue
        path=ref.get("ref")
        if not isinstance(path,str) or not path: continue
        cp=subprocess.run(["git","show",f"{candidate}:{path}"],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if cp.returncode: raise RuntimeError(f"candidate evidence file unavailable: {path}")
        text=cp.stdout.decode("utf-8")
        evidence.append({"path":path,"bytes_utf8":len(cp.stdout),"sha256":sha256(cp.stdout).hexdigest(),"content":text})
    base=git(root,"merge-base","origin/main",candidate).strip()
    diff=git(root,"diff","--no-ext-diff",base,candidate,"--","governance-runtime",".github/workflows/live-conversation-governance.yml",".github/workflows/governance-candidate-platform-review.yml")
    return {"schema_version":1,"review_request":request,"base_commit":base,"candidate_commit":candidate,"candidate_diff":diff,"evidence_artifacts":evidence,"posture":"Assume false-green. Do not use proposer confidence or green CI as sufficient evidence. Search for authority bypass, provenance confusion, stale-memory promotion, review-waiver paths, provider/model substitution, semantic overclaim, mode/transport divergence, and missing deterministic enforcement."}

def build_prompt(request,corpus,model):
    dims=[d["id"] for d in request["required_review_dimensions"] if d.get("mandatory")]
    shape={"review_request_id":request["review_request_id"],"reviewed_artifact_commit":request["artifact"]["commit"],"reviewer":{"provider":"gemini","model":model},"disposition":"PASS|BOUNDED_PASS|FAIL|NOT_TESTED|INSUFFICIENT_EVIDENCE|CHANGES_REQUIRED","findings":[{"id":"F1","severity":"LOW|MEDIUM|HIGH|CRITICAL","title":"title","evidence":"specific file/function evidence","impact":"impact","required_change":"change or null"}],"evidence_assessment":"assessment","independence_attestation":"BLIND_TO_PROPOSER_CONCLUSION","review_coverage":[{"dimension_id":dims[0] if dims else "dimension","status":"TESTED_SUPPORTED|TESTED_DEFECT_FOUND|CONTRADICTED|NOT_TESTED|UNAVAILABLE|INACCESSIBLE|INSUFFICIENT","evidence":["specific refs"],"assessment":"assessment"}]}
    return "You are the independent adversarial reviewer for a material live-conversation-governance authority transition. Assume false-green. Inspect the exact candidate and supplied evidence. Return strict JSON only; no markdown and no private chain-of-thought. Every mandatory dimension must be present exactly once. PASS requires every mandatory dimension TESTED_SUPPORTED and no MEDIUM/HIGH/CRITICAL finding. Reviewer content cannot establish API provenance; the platform execution envelope does.\nREQUEST:\n"+json.dumps(request,sort_keys=True)+"\nOUTPUT SHAPE:\n"+json.dumps(shape,sort_keys=True)+"\nCORPUS:\n"+json.dumps(corpus,sort_keys=True)

def invoke(key,model,prompt):
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{quote(model,safe='')}:generateContent"
    payload={"contents":[{"role":"user","parts":[{"text":prompt}]}],"generationConfig":{"temperature":0.0,"maxOutputTokens":16384,"responseMimeType":"application/json"}}
    req=Request(url,data=json.dumps(payload).encode(),headers={"x-goog-api-key":key,"content-type":"application/json","user-agent":"setugo-governance-platform-review/1.0"},method="POST")
    try:
        with urlopen(req,timeout=180) as response: body=json.loads(response.read().decode("utf-8"))
    except HTTPError as exc: raise RuntimeError(f"Gemini HTTP {exc.code}: "+exc.read().decode("utf-8",errors="replace")[:1000]) from exc
    except URLError as exc: raise RuntimeError(f"Gemini connection failed: {exc.reason}") from exc
    c=(body.get("candidates") or [{}])[0]
    if c.get("finishReason")!="STOP": raise RuntimeError(f"Gemini nonterminal: {c.get('finishReason')!r}")
    text="".join(str(p.get("text","")) for p in ((c.get("content") or {}).get("parts") or []) if isinstance(p,dict))
    review=json.loads(text)
    if not isinstance(review,dict): raise RuntimeError("review JSON must be object")
    return body,review

def validate(review,request,model):
    errors=[]
    reqid=request["review_request_id"]; candidate=request["artifact"]["commit"]
    mandatory=[d["id"] for d in request["required_review_dimensions"] if d.get("mandatory")]
    if review.get("review_request_id")!=reqid: errors.append("review_request_id mismatch")
    if review.get("reviewed_artifact_commit")!=candidate: errors.append("reviewed_artifact_commit mismatch")
    disp=review.get("disposition")
    if disp not in ALLOWED_DISPOSITIONS: errors.append("invalid disposition")
    rv=review.get("reviewer")
    if not isinstance(rv,dict) or rv.get("provider")!="gemini" or rv.get("model")!=model: errors.append("reviewer content identity disagrees with execution envelope")
    findings=review.get("findings")
    if not isinstance(findings,list): errors.append("findings must be list"); findings=[]
    blocking=False
    for f in findings:
        if not isinstance(f,dict): errors.append("finding must be object"); continue
        sev=f.get("severity")
        if sev not in {"LOW","MEDIUM","HIGH","CRITICAL"}: errors.append("invalid finding severity")
        if sev in BLOCKING: blocking=True
        if not str(f.get("evidence","")).strip(): errors.append("finding evidence required")
    cov=review.get("review_coverage")
    if not isinstance(cov,list): errors.append("review_coverage must be list"); cov=[]
    by={}
    for row in cov:
        if not isinstance(row,dict): errors.append("coverage row must be object"); continue
        did=row.get("dimension_id")
        if did in by: errors.append(f"duplicate dimension {did}"); continue
        by[did]=row
        if row.get("status") not in ALLOWED_STATUSES: errors.append(f"invalid coverage status {did}")
        if row.get("status") in {"TESTED_SUPPORTED","TESTED_DEFECT_FOUND","CONTRADICTED"}:
            ev=row.get("evidence")
            if not isinstance(ev,list) or not any(str(x).strip() for x in ev): errors.append(f"tested dimension evidence required {did}")
    missing=[d for d in mandatory if d not in by]; extras=[d for d in by if d not in mandatory]
    if missing: errors.append("missing mandatory dimensions: "+",".join(missing))
    if extras: errors.append("unexpected dimensions: "+",".join(extras))
    statuses={d:by[d].get("status") for d in mandatory if d in by}
    all_supported=len(statuses)==len(mandatory) and all(v=="TESTED_SUPPORTED" for v in statuses.values())
    incomplete=any(v in {"NOT_TESTED","UNAVAILABLE","INACCESSIBLE","INSUFFICIENT"} for v in statuses.values())
    defective=any(v in {"TESTED_DEFECT_FOUND","CONTRADICTED"} for v in statuses.values())
    if disp=="PASS" and (not all_supported or blocking): errors.append("PASS contradicts coverage/findings")
    if disp=="BOUNDED_PASS" and (blocking or defective or incomplete): errors.append("BOUNDED_PASS contradicts mandatory coverage/findings")
    if disp in {"FAIL","CHANGES_REQUIRED"} and not (defective or blocking): errors.append("negative disposition lacks defect evidence")
    if disp in {"NOT_TESTED","INSUFFICIENT_EVIDENCE"} and not incomplete: errors.append("insufficient disposition lacks incomplete coverage")
    return {"valid":not errors,"errors":errors,"effective_disposition":disp if not errors else "INVALID_REVIEW_EVIDENCE","all_mandatory_dimensions_supported":all_supported if not errors else False}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--request",required=True); ap.add_argument("--output-dir",required=True); ap.add_argument("--model",required=True); args=ap.parse_args()
    request=json.loads(Path(args.request).read_text(encoding="utf-8")); verify_request_integrity(request); root=Path("."); out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    corpus=build_corpus(root,request); prompt=build_prompt(request,corpus,args.model); key=os.environ.get("GEMINI_API_KEY","")
    if not key: raise RuntimeError("GEMINI_API_KEY repository secret required")
    provider,review=invoke(key,args.model,prompt); validation=validate(review,request,args.model)
    envelope={"schema_version":1,"review_request_id":request["review_request_id"],"reviewed_artifact_commit":request["artifact"]["commit"],"review_class":"PLATFORM_AUTO_API_REVIEW","transport":"AUTOMATIC_API","provider":"gemini","model":args.model,"provider_api_authenticated":True,"remote_model_identity_cryptographically_proven":False,"request_hash":request.get("request_hash"),"corpus_sha256":digest(corpus),"authority_effect":"NONE_PENDING_DETERMINISTIC_INGESTION"}
    for n,o in [("corpus.json",corpus),("provider-response.json",provider),("review.json",review),("validation.json",validation),("execution-envelope.json",envelope)]: (out/n).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    if not validation["valid"]: raise SystemExit(3)
if __name__=="__main__": main()
