"""EXP-I Pilot 14: root-key rotation and compromised-root containment."""
from __future__ import annotations
import hashlib, hmac, json, os, sqlite3, subprocess, sys
from pathlib import Path
from typing import Any, Mapping
from exp_i_asymmetric_checkpoint_signer import _canon, _digest, _ed25519_sign, _ed25519_verify, _ensure_ed25519_keypair
from exp_i_registry_root_isolation import fp

ROOT_VERSION="exp-i-pilot14-root-trust-v1"
REGISTRY_VERSION="exp-i-pilot14-registry-v1"

def _root_record_body(epoch:int, transition_id:str, prior_root_id:str|None, active_root_id:str, public_pem:str, activation_registry_epoch:int, pred:str)->dict[str,Any]:
    return {"schema_version":ROOT_VERSION,"root_epoch":epoch,"transition_id":transition_id,"prior_root_id":prior_root_id,"prior_status_after":None if prior_root_id is None else "REVOKED","active_root_id":active_root_id,"active_public_key_pem":public_pem,"active_public_key_fingerprint":fp(public_pem),"activation_registry_epoch":activation_registry_epoch,"predecessor_root_record_digest":pred}

class RootMinimumAuthority:
    def __init__(self,path:str|Path):
        self.path=str(path); c=sqlite3.connect(self.path); c.execute("CREATE TABLE IF NOT EXISTS minimum(id INTEGER PRIMARY KEY CHECK(id=1), root_epoch INTEGER NOT NULL, record_digest TEXT NOT NULL)"); c.commit(); c.close()
    def advance(self,epoch:int,digest:str):
        c=sqlite3.connect(self.path,isolation_level=None)
        try:
            c.execute("BEGIN IMMEDIATE"); r=c.execute("SELECT root_epoch,record_digest FROM minimum WHERE id=1").fetchone()
            if r and epoch<int(r[0]): raise PermissionError("ROOT_MINIMUM_ROLLBACK_DENIED")
            if r and epoch==int(r[0]) and digest!=r[1]: raise PermissionError("ROOT_MINIMUM_REBIND_DENIED")
            if not r:c.execute("INSERT INTO minimum VALUES(1,?,?)",(epoch,digest))
            elif epoch>int(r[0]):c.execute("UPDATE minimum SET root_epoch=?,record_digest=? WHERE id=1",(epoch,digest))
            c.execute("COMMIT")
        finally:c.close()
    def current(self):
        c=sqlite3.connect(self.path); r=c.execute("SELECT root_epoch,record_digest FROM minimum WHERE id=1").fetchone(); c.close()
        if not r: raise PermissionError("ROOT_MINIMUM_UNSET")
        return int(r[0]),str(r[1])

class PlatformRootTrustAuthority:
    def __init__(self,path:str|Path,auth_key_path:str|Path):
        self.path=str(path); self.auth_key_path=str(auth_key_path); Path(self.auth_key_path).parent.mkdir(parents=True,exist_ok=True)
        if not Path(self.auth_key_path).exists(): Path(self.auth_key_path).write_bytes(os.urandom(32))
        c=sqlite3.connect(self.path); c.execute("CREATE TABLE IF NOT EXISTS root_records(root_epoch INTEGER PRIMARY KEY,transition_id TEXT UNIQUE NOT NULL,record_json TEXT NOT NULL,record_digest TEXT UNIQUE NOT NULL,record_auth TEXT NOT NULL)"); c.commit(); c.close()
    def _auth(self,body:Mapping[str,Any])->str:return hmac.new(Path(self.auth_key_path).read_bytes(),_canon(body),hashlib.sha256).hexdigest()
    def bootstrap(self,*,transition_id:str,root_id:str,public_key_pem:str,activation_registry_epoch:int=0): return self._transition(transition_id,None,root_id,public_key_pem,activation_registry_epoch)
    def rotate(self,*,transition_id:str,expected_prior_root_id:str,next_root_id:str,next_public_key_pem:str,activation_registry_epoch:int): return self._transition(transition_id,expected_prior_root_id,next_root_id,next_public_key_pem,activation_registry_epoch)
    def _transition(self,tid,expected_prior,next_id,next_pem,activation_registry_epoch):
        c=sqlite3.connect(self.path,timeout=10,isolation_level=None)
        try:
            c.execute("BEGIN IMMEDIATE"); rows=c.execute("SELECT root_epoch,transition_id,record_json,record_digest,record_auth FROM root_records ORDER BY root_epoch").fetchall()
            for er,et,j,d,a in rows:
                if et==tid:
                    old=json.loads(j)
                    if old["active_root_id"]!=next_id or old["active_public_key_pem"]!=next_pem or old["prior_root_id"]!=expected_prior: raise PermissionError("ROOT_TRANSITION_REBIND_DENIED")
                    c.execute("COMMIT"); return {"record":old,"record_digest":d,"record_auth":a}
            last=rows[-1] if rows else None; epoch=1 if not last else int(last[0])+1; prior=None if not last else json.loads(last[2])["active_root_id"]
            if prior!=expected_prior: raise PermissionError("ROOT_PRIOR_MISMATCH")
            pred="GENESIS" if not last else str(last[3])
            body=_root_record_body(epoch,tid,prior,next_id,next_pem,activation_registry_epoch,pred); auth=self._auth(body); digest=_digest({"record":body,"auth":auth})
            c.execute("INSERT INTO root_records VALUES(?,?,?,?,?)",(epoch,tid,json.dumps(body,sort_keys=True),digest,auth)); c.execute("COMMIT")
            return {"record":body,"record_digest":digest,"record_auth":auth}
        finally:c.close()
    def history(self,minimum:RootMinimumAuthority|None=None):
        c=sqlite3.connect(self.path); rows=c.execute("SELECT root_epoch,record_json,record_digest,record_auth FROM root_records ORDER BY root_epoch").fetchall(); c.close()
        if not rows: raise PermissionError("ROOT_TRUST_EMPTY")
        pred="GENESIS"; out=[]
        for expected,(er,j,d,a) in enumerate(rows,1):
            b=json.loads(j)
            if int(er)!=expected or int(b.get("root_epoch",-1))!=expected: raise PermissionError("ROOT_EPOCH_CHAIN_INVALID")
            if b.get("schema_version")!=ROOT_VERSION or b.get("predecessor_root_record_digest")!=pred: raise PermissionError("ROOT_PREDECESSOR_INVALID")
            if fp(str(b.get("active_public_key_pem","")))!=b.get("active_public_key_fingerprint"): raise PermissionError("ROOT_FINGERPRINT_INVALID")
            if not hmac.compare_digest(self._auth(b),str(a)): raise PermissionError("ROOT_RECORD_AUTH_INVALID")
            if _digest({"record":b,"auth":a})!=str(d): raise PermissionError("ROOT_RECORD_DIGEST_INVALID")
            pred=str(d); out.append({"record":b,"record_digest":str(d),"record_auth":str(a)})
        if minimum:
            me,md=minimum.current()
            if len(out)<me: raise PermissionError("ROOT_BELOW_MINIMUM")
            if out[me-1]["record_digest"]!=md: raise PermissionError("ROOT_MINIMUM_DIGEST_MISMATCH")
        return out
    def current(self,minimum:RootMinimumAuthority|None=None):return self.history(minimum)[-1]


def _init_signer_store(path:str):
    c=sqlite3.connect(path); c.execute("CREATE TABLE IF NOT EXISTS issuance(transition_id TEXT PRIMARY KEY,body_digest TEXT NOT NULL,signature TEXT NOT NULL)"); c.commit(); c.close()

def _worker(root_id,store,priv,pub,root_db,root_auth,minimum_db):
    _ensure_ed25519_keypair(priv,pub); _init_signer_store(store); public=Path(pub).read_text(); print(json.dumps({"ready":True,"root_id":root_id,"public_key_pem":public}),flush=True)
    for line in sys.stdin:
        try:
            req=json.loads(line); body=req["body"]; minimum=RootMinimumAuthority(minimum_db); trust=PlatformRootTrustAuthority(root_db,root_auth); cur=trust.current(minimum)["record"]
            if cur["active_root_id"]!=root_id or cur["active_public_key_fingerprint"]!=fp(public): raise PermissionError("ROOT_NOT_CURRENTLY_ELIGIBLE")
            if int(body.get("root_epoch",-1))!=int(cur["root_epoch"]) or body.get("root_record_digest")!=trust.current(minimum)["record_digest"]: raise PermissionError("ROOT_BINDING_STALE")
            tid=str(body["transition_id"]); bd=_digest(body); c=sqlite3.connect(store,isolation_level=None)
            try:
                c.execute("BEGIN IMMEDIATE"); old=c.execute("SELECT body_digest,signature FROM issuance WHERE transition_id=?",(tid,)).fetchone()
                if old:
                    if old[0]!=bd: raise PermissionError("TRANSITION_REBIND_DENIED")
                    sig=old[1]; c.execute("COMMIT")
                else:
                    sig=_ed25519_sign(priv,_canon(body)); c.execute("INSERT INTO issuance VALUES(?,?,?)",(tid,bd,sig)); c.execute("COMMIT")
                print(json.dumps({"ok":True,"signature":sig}),flush=True)
            finally:c.close()
        except Exception as exc: print(json.dumps({"ok":False,"reason":str(exc)}),flush=True)

class RotatingRootSigner:
    def __init__(self,directory:str|Path,root_id:str,root_trust:PlatformRootTrustAuthority,minimum:RootMinimumAuthority):
        d=Path(directory); d.mkdir(parents=True,exist_ok=True); self.root_id=root_id; self.root_trust=root_trust; self.minimum=minimum; self._store=str(d/"state.db"); self._priv=str(d/"private.pem"); self._pub=str(d/"public.pem"); self.proc=None; _ensure_ed25519_keypair(self._priv,self._pub); self.public_key_pem=Path(self._pub).read_text(); self.start()
    def start(self):
        if self.proc and self.proc.poll() is None:return
        self.proc=subprocess.Popen([sys.executable,__file__,"--worker",self.root_id,self._store,self._priv,self._pub,self.root_trust.path,self.root_trust.auth_key_path,self.minimum.path],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
        ready=json.loads(self.proc.stdout.readline());
        if not ready.get("ready"): raise RuntimeError("ROOT_START_FAILED")
    def stop(self,kill=False):
        if self.proc and self.proc.poll() is None:self.proc.kill() if kill else self.proc.terminate(); self.proc.wait(timeout=5)
    def sign(self,body:Mapping[str,Any]):
        if not self.proc or self.proc.poll() is not None:return {"ok":False,"reason":"ROOT_UNAVAILABLE"}
        self.proc.stdin.write(json.dumps({"body":dict(body)},sort_keys=True)+"\n"); self.proc.stdin.flush(); line=self.proc.stdout.readline(); return json.loads(line) if line else {"ok":False,"reason":"ROOT_RESPONSE_LOST"}

class RootRotatingRegistry:
    def __init__(self,path:str|Path,root_trust:PlatformRootTrustAuthority,minimum:RootMinimumAuthority,signers:Mapping[str,RotatingRootSigner]):
        self.path=str(path); self.root_trust=root_trust; self.minimum=minimum; self.signers=dict(signers); c=sqlite3.connect(self.path); c.execute("CREATE TABLE IF NOT EXISTS trust_events(trust_epoch INTEGER PRIMARY KEY,transition_id TEXT UNIQUE NOT NULL,event_json TEXT NOT NULL,event_digest TEXT UNIQUE NOT NULL,signature TEXT NOT NULL)"); c.commit(); c.close()
    def transition(self,*,transition_id:str,key_id:str,public_key_pem:str,activation_generation:int,root_id:str|None=None):
        c=sqlite3.connect(self.path,timeout=10,isolation_level=None)
        try:
            c.execute("BEGIN IMMEDIATE"); rows=c.execute("SELECT trust_epoch,transition_id,event_json,event_digest,signature FROM trust_events ORDER BY trust_epoch").fetchall()
            for er,tid,j,d,s in rows:
                if tid==transition_id:
                    e=json.loads(j)
                    if e["active_key_id"]!=key_id or e["active_public_key_pem"]!=public_key_pem or int(e["activation_generation"])!=activation_generation or (root_id is not None and e["signer_root_id"]!=root_id): raise PermissionError("TRANSITION_REBIND_DENIED")
                    c.execute("COMMIT"); return {"event":e,"event_digest":d,"signature":s}
            current_root=self.root_trust.current(self.minimum); rr=current_root["record"]; rid=root_id or rr["active_root_id"]
            if rid!=rr["active_root_id"]: raise PermissionError("ROOT_NOT_CURRENTLY_ELIGIBLE")
            signer=self.signers[rid]; last=rows[-1] if rows else None; epoch=1 if not last else int(last[0])+1; pred="GENESIS" if not last else str(last[3]); prior=None if not last else json.loads(last[2])["active_key_id"]
            if activation_generation!=epoch: raise PermissionError("ACTIVATION_GENERATION_NOT_EXACT_NEXT")
            body={"registry_version":REGISTRY_VERSION,"transition_id":transition_id,"trust_epoch":epoch,"prior_key_id":prior,"active_key_id":key_id,"active_public_key_pem":public_key_pem,"active_public_key_fingerprint":fp(public_key_pem),"activation_generation":activation_generation,"predecessor_event_digest":pred,"signer_root_id":rid,"root_epoch":rr["root_epoch"],"root_record_digest":current_root["record_digest"]}
            signed=signer.sign(body)
            if not signed.get("ok"): raise PermissionError(signed.get("reason","ROOT_SIGN_FAILED"))
            sig=signed["signature"]; d=_digest({"event":body,"signature":sig}); c.execute("INSERT INTO trust_events VALUES(?,?,?,?,?)",(epoch,transition_id,json.dumps(body,sort_keys=True),d,sig)); c.execute("COMMIT"); return {"event":body,"event_digest":d,"signature":sig}
        finally:c.close()

class RotatingRegistryReader:
    def __init__(self,registry_db:str|Path,root_trust:PlatformRootTrustAuthority,minimum:RootMinimumAuthority):self.registry_db=str(registry_db); self.root_trust=root_trust; self.minimum=minimum
    def history(self):
        roots=self.root_trust.history(self.minimum); by_epoch={x["record"]["root_epoch"]:x for x in roots}; c=sqlite3.connect(self.registry_db); rows=c.execute("SELECT trust_epoch,event_json,event_digest,signature FROM trust_events ORDER BY trust_epoch").fetchall(); c.close(); pred="GENESIS"; out=[]
        for expected,(er,j,d,s) in enumerate(rows,1):
            e=json.loads(j)
            if int(er)!=expected or int(e["trust_epoch"])!=expected or e["predecessor_event_digest"]!=pred: raise PermissionError("TRUST_CHAIN_INVALID")
            rr=by_epoch.get(int(e["root_epoch"]));
            if not rr or rr["record_digest"]!=e["root_record_digest"] or rr["record"]["active_root_id"]!=e["signer_root_id"]: raise PermissionError("ROOT_BINDING_INVALID")
            pub=rr["record"]["active_public_key_pem"]
            if not _ed25519_verify(pub,_canon(e),str(s)): raise PermissionError("ROOT_SIGNATURE_INVALID")
            if _digest({"event":e,"signature":s})!=str(d): raise PermissionError("TRUST_EVENT_DIGEST_INVALID")
            pred=str(d); out.append({"event":e,"event_digest":str(d),"signature":str(s)})
        if not out: raise PermissionError("REGISTRY_EMPTY")
        return out
    def current(self):return self.history()[-1]

if __name__=="__main__" and len(sys.argv)>1 and sys.argv[1]=="--worker": _worker(*sys.argv[2:9])
