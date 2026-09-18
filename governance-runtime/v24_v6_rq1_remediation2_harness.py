#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, shutil, signal, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "governance-runtime"
OBSERVER = RUNTIME / "v24_v6_rq1_observer.py"
PID = Path("/run/v24-v6-authority/service.pid")
CANDIDATE = "v24candidate"
STATE = {"scientific_execution_state":"CLOSED_PENDING_SUCCESSOR_REVIEW",
         "authority_effect":"NONE_EVIDENCE_ONLY","qualification":"NOT_QUALIFIED"}
CASES = {
 "RQ-01":("Diagnostic-only DENY; no trusted state transition","loader-interposition"),
 "RQ-02":("No authority; trusted state unchanged","fake-runtime-functions"),
 "RQ-03":("Kernel-derived peer rejection","root-control-peer"),
 "RQ-04":("Fail closed; no candidate authority","socket-replacement"),
 "RQ-08":("AUTHORITY_RECORD_BINDING_INVALID","keep-existing"),
 "RQ-09":("AUTHORITY_RECORD_BINDING_INVALID","keep-existing"),
 "RQ-10":("Rejected","keep-existing"),
 "RQ-22":("Denied by bound runtime controls","ptrace-service"),
 "RQ-23":("Cannot affect service or trusted paths","namespace-bind"),
 "RQ-24":("Authoritative DENY in evidence-only harness","da1"),
 "RQ-25":("Authoritative DENY in evidence-only harness","ncp1"),
 "RQ-28":("Fail closed; service remains recoverable","protocol-fuzz"),
}
RUNNABLE=[k for k,v in CASES.items() if v[1]!="keep-existing"]

def run(argv,*,user=None,timeout=20):
    cmd=list(argv)
    if user: cmd=["sudo","-u",user,"--"]+cmd
    return subprocess.run(cmd,text=True,capture_output=True,check=False,timeout=timeout)

def sha(path:Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def write_json(path:Path,obj):
    path.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n",encoding="utf-8")

def observe(path:Path):
    p=subprocess.run([sys.executable,str(OBSERVER)],text=True,capture_output=True,check=False,timeout=15)
    if p.returncode: raise RuntimeError(f"observer failed: {p.stderr}")
    path.write_text(p.stdout.strip()+"\n",encoding="utf-8")
    return json.loads(p.stdout)

def stable(before,after):
    for k in ["service","gate","unit"]:
        for f in ["sha256","uid","mode"]:
            if before.get(k,{}).get(f)!=after.get(k,{}).get(f): return False
    return True

def active():
    return subprocess.run(["systemctl","is-active","--quiet","v24-v6-trusted-authority.service"]).returncode==0

def candidate_uid():
    return int(run(["id","-u",CANDIDATE],timeout=5).stdout.strip())

def root_control_request():
    code=r'''import json,socket,struct
s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.settimeout(4)
s.connect("/run/v24-v6-authority/service.sock")
peer=struct.unpack("3i",s.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
hdr=("V24-V6-S9-CONSUME/1\\n"+"a"*64+"\\nresolve-governed\\n"+"b"*64+"\\nROOT-VERIFIER\\n"+"c"*64+"\\n1\\n1\\n0\\n").encode()
s.sendall(hdr+b"x"+b"y")
line=b""
while not line.endswith(b"\\n"): line+=s.recv(1)
n=int(line.strip()); body=b""
while len(body)<n: body+=s.recv(n-len(body))
print(json.dumps({"peer":peer,"response":json.loads(body)},sort_keys=True))'''
    return run(["python3","-c",code],user=CANDIDATE,timeout=10)

def case_01_02(cid,out):
    b=observe(out/f"{cid}.before.observer.json")
    test="test_v24_v6_successor9_consume_loader_red.Successor9ConsumeLoaderRed.test_candidate_loader_interposition_cannot_forge_authoritative_consume"
    p=run(["env",f"PYTHONPATH={RUNTIME}","python3","-m","unittest","-v",test],user=CANDIDATE,timeout=45)
    a=observe(out/f"{cid}.after.observer.json"); s=stable(b,a)
    return p.returncode==0 and s and active(),{"trigger":"direct frozen service launch under LD_PRELOAD fake geteuid/lstat/chmod/fopen/rename","rc":p.returncode,"stdout":p.stdout,"stderr":p.stderr,"state_stable":s,"service_active":active()}

def case_03(out):
    b=observe(out/"RQ-03.before.observer.json")
    if shutil.which("strace") is None: return False,{"harness_defect":"strace unavailable"}
    pid=int(PID.read_text().strip()); trace=out/"RQ-03.strace.txt"
    with trace.open("w",encoding="utf-8") as tf:
        st=subprocess.Popen(["strace","-f","-qq","-e","trace=getsockopt","-s","256","-p",str(pid)],stdout=tf,stderr=tf,text=True)
        time.sleep(.5); p=root_control_request(); time.sleep(.5); st.send_signal(signal.SIGINT)
        try: st.wait(timeout=3)
        except subprocess.TimeoutExpired: st.kill(); st.wait()
    a=observe(out/"RQ-03.after.observer.json"); tr=trace.read_text(errors="replace"); uid=candidate_uid()
    try: payload=json.loads(p.stdout.strip())
    except Exception: payload={}
    reason=((payload or {}).get("response") or {}).get("reason")
    peer=(f"uid={uid}" in tr and "SO_PEERCRED" in tr); rejected=reason in {"IPC_HEADER_INVALID","PEER_IDENTITY_REJECTED"}
    return p.returncode==0 and peer and rejected and stable(b,a),{"trigger":"candidate root-control protocol","candidate_uid":uid,"response_reason":reason,"so_peercred_observed":peer,"strace_sha256":sha(trace),"stdout":p.stdout,"stderr":p.stderr,"state_stable":stable(b,a)}

def case_04(out):
    b=observe(out/"RQ-04.before.observer.json")
    code=r'''import os,socket,json
p="/run/v24-v6-authority/service.sock"; o={}
try: os.unlink(p); o["unlink"]="UNEXPECTED_SUCCESS"
except Exception as e: o["unlink"]=type(e).__name__+":"+str(e)
s=socket.socket(socket.AF_UNIX)
try: s.bind(p); o["bind"]="UNEXPECTED_SUCCESS"
except Exception as e: o["bind"]=type(e).__name__+":"+str(e)
print(json.dumps(o,sort_keys=True))'''
    p=run(["python3","-c",code],user=CANDIDATE,timeout=10)
    r=run(["systemctl","restart","v24-v6-trusted-authority.service"],timeout=20); time.sleep(.5)
    a=observe(out/"RQ-04.after.observer.json")
    try: attack=json.loads(p.stdout.strip())
    except Exception: attack={}
    sm=a.get("socket",{}); denied="UNEXPECTED_SUCCESS" not in attack.values()
    trusted=sm.get("exists") and sm.get("uid")==0 and sm.get("is_socket")
    return p.returncode==0 and denied and r.returncode==0 and trusted and active(),{"trigger":"candidate unlink/bind replacement plus trusted restart","attack":attack,"restart_rc":r.returncode,"trusted_socket_restored":trusted,"service_active":active()}

def case_22(out):
    b=observe(out/"RQ-22.before.observer.json"); pid=int(PID.read_text().strip())
    code=r'''import ctypes,errno,json,sys
pid=int(sys.argv[1]); libc=ctypes.CDLL(None,use_errno=True); libc.ptrace.restype=ctypes.c_long
rc=libc.ptrace(16,pid,None,None); err=ctypes.get_errno()
if rc==0: libc.ptrace(17,pid,None,None)
print(json.dumps({"rc":rc,"errno":err},sort_keys=True)); raise SystemExit(0 if rc==-1 and err in (errno.EPERM,errno.EACCES) else 1)'''
    p=run(["python3","-c",code,str(pid)],user=CANDIDATE,timeout=10); a=observe(out/"RQ-22.after.observer.json")
    return p.returncode==0 and stable(b,a) and active(),{"trigger":"candidate PTRACE_ATTACH actual trusted service PID","service_pid":pid,"stdout":p.stdout,"stderr":p.stderr,"state_stable":stable(b,a)}

def case_23(out):
    b=observe(out/"RQ-23.before.observer.json"); target="/tmp/rq1-r23-bind"
    run(["rm","-rf",target]); run(["mkdir","-p",target])
    p=run(["unshare","--user","--map-root-user","--mount","--propagation","private","/bin/sh","-c",f"mount --bind /opt/v24-v6-trusted-runtime {target} && touch {target}/candidate-write"],user=CANDIDATE,timeout=10)
    a=observe(out/"RQ-23.after.observer.json")
    return p.returncode!=0 and stable(b,a) and active(),{"trigger":"candidate user/mount namespace bind attack","rc":p.returncode,"stdout":p.stdout,"stderr":p.stderr,"kernel_denied_attack_chain":p.returncode!=0,"state_stable":stable(b,a)}

def candidate_diag(mode,dest):
    code=r'''import json,sys
from v24_v6_successor9_trusted_control import _request
from v24_v6_trusted_service_client import request_service
r=_request(sys.argv[1]); x=request_service(r["operation"],context=r["context"],boundary=r["boundary"],payload=r["payload"],reference=r["reference"],expected_id=r["expected_id"],expected_digest=r["expected_digest"])
print(json.dumps(x,sort_keys=True))'''
    p=run(["env",f"PYTHONPATH={RUNTIME}","python3","-c",code,mode],user=CANDIDATE,timeout=30)
    if p.returncode==0: dest.write_text(p.stdout.strip()+"\n")
    return p

def trusted_consume(mode,diag):
    return run(["env",f"PYTHONPATH={RUNTIME}","python3",str(RUNTIME/"v24_v6_successor9_trusted_control.py"),mode,str(diag)],timeout=30)

def case_24_25(cid,out):
    mode="da1" if cid=="RQ-24" else "ncp1"; b=observe(out/f"{cid}.before.observer.json"); diag=out/f"{cid}.diagnostic.json"
    d=candidate_diag(mode,diag)
    if d.returncode: return False,{"harness_defect":"attacked diagnostic creation failed","stderr":d.stderr}
    c=trusted_consume(mode,diag); a=observe(out/f"{cid}.after.observer.json")
    try: x=json.loads(c.stdout.strip())
    except Exception: x={}
    exact=x.get("decision")=="DENY" and x.get("construction_authoritative") is True and x.get("service_authoritative") is True and x.get("record_state")=="CONSUMED"
    return c.returncode!=0 and exact and active(),{"trigger":f"{mode.upper()} attacked diagnostic then matching root-peer consume","diagnostic":json.loads(diag.read_text()),"consume_stdout":c.stdout,"consume_stderr":c.stderr,"authoritative_deny":exact,"service_hash_stable":b.get("service",{}).get("sha256")==a.get("service",{}).get("sha256")}

def protocol_variants():
    code=r'''import json,socket
P="/run/v24-v6-authority/service.sock"
def recv(s):
  try:
    line=b""
    while not line.endswith(b"\\n"):
      b=s.recv(1)
      if not b:return {"closed":True}
      line+=b
    n=int(line.strip()); body=b""
    while len(body)<n:
      b=s.recv(n-len(body))
      if not b:break
      body+=b
    return json.loads(body) if body else {"empty":True}
  except Exception as e:return {"exception":type(e).__name__+":"+str(e)}
def one(name,data):
  s=socket.socket(socket.AF_UNIX); s.settimeout(3); s.connect(P); s.sendall(data); s.shutdown(socket.SHUT_WR); r=recv(s); s.close(); return {"name":name,"response":r}
v=("V24-V6-S8/1\\nresolve-governed\\n"+"a"*64+"\\nX\\n"+"b"*64+"\\n10\\n10\\n0\\n").encode()
print(json.dumps([one("malformed_magic",b"BAD\\nx\\nx\\nx\\nx\\n0\\n0\\n0\\n"),one("oversized_header",b"A"*10000+b"\\n"),one("truncated_header",b"V24-V6-S8/1\\nresolve-governed\\n"),one("partial_body",v+b"abc")],sort_keys=True))'''
    return run(["python3","-c",code],user=CANDIDATE,timeout=20)

def case_28(out):
    b=observe(out/"RQ-28.before.observer.json"); p=protocol_variants(); a=observe(out/"RQ-28.after.observer.json")
    try: rows=json.loads(p.stdout.strip())
    except Exception: rows=[]
    reasons=[]
    for row in rows:
        r=row.get("response") or {}; reasons.append(r.get("reason") or r.get("exception") or ("closed" if r.get("closed") else "UNKNOWN"))
    expected=len(reasons)==4 and all(any(t in str(x) for t in ["MALFORMED","INVALID","TRUNCATED","closed","exception"]) for x in reasons)
    return p.returncode==0 and expected and active() and stable(b,a),{"trigger":"malformed/oversized/truncated/partial protocol variants","variants":rows,"reasons":reasons,"service_recoverable":active(),"state_stable":stable(b,a)}

IMPL={"RQ-01":case_01_02,"RQ-02":case_01_02,"RQ-03":lambda c,o:case_03(o),"RQ-04":lambda c,o:case_04(o),"RQ-22":lambda c,o:case_22(o),"RQ-23":lambda c,o:case_23(o),"RQ-24":case_24_25,"RQ-25":case_24_25,"RQ-28":lambda c,o:case_28(o)}

def execute(cid,out):
    oracle,mode=CASES[cid]; start=time.time()
    if cid in {"RQ-08","RQ-09","RQ-10"}: r={"case_id":cid,"oracle":oracle,"status":"KEEP_HISTORICAL_SUPPORTED_PASS","mode":mode,"observation":"Not rerun; prior independently reviewed evidence remains historical.",**STATE}
    elif cid not in IMPL: r={"case_id":cid,"oracle":oracle,"status":"HARNESS_DEFECT","mode":mode,"observation":"No exact trigger implemented.",**STATE}
    else:
        try:
            ok,d=IMPL[cid](cid,out); st="PASS" if ok else ("HARNESS_DEFECT" if "harness_defect" in d else "RED")
            r={"case_id":cid,"oracle":oracle,"status":st,"mode":mode,"detail":d,**STATE}
        except Exception as e:r={"case_id":cid,"oracle":oracle,"status":"HARNESS_DEFECT","mode":mode,"observation":f"{type(e).__name__}: {e}",**STATE}
    r["duration_seconds"]=round(time.time()-start,3); write_json(out/f"{cid}.result.json",r); return r

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--case",action="append",choices=sorted(CASES)); ap.add_argument("--safe-slice",action="store_true"); ap.add_argument("--evidence-dir",required=True); a=ap.parse_args()
    selected=a.case or (RUNNABLE if a.safe_slice else [])
    if not selected: ap.error("select --case or --safe-slice")
    out=Path(a.evidence_dir); out.mkdir(parents=True,exist_ok=True); rs=[execute(c,out) for c in selected]
    write_json(out/"RQ1-remediation2-targeted-bundle.json",{"schema_version":1,"phase_id":"V24-I11-V6-RUNTIME-QUALIFICATION-1","remediation":"2","results":rs,"state":STATE})
    counts={}
    for r in rs:counts[r["status"]]=counts.get(r["status"],0)+1
    print(json.dumps({"selected":selected,"counts":counts,**STATE},sort_keys=True))
    return 0 if all(r["status"] in {"PASS","KEEP_HISTORICAL_SUPPORTED_PASS"} for r in rs) else 2
if __name__=="__main__": raise SystemExit(main())
