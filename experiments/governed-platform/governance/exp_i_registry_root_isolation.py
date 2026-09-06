"""EXP-I Pilot 13: isolated trust-registry root and monotonic trusted minimum."""
from __future__ import annotations
import hashlib, json, os, sqlite3, subprocess, sys, tempfile
from pathlib import Path
from typing import Any, Mapping
from exp_i_asymmetric_checkpoint_signer import _canon, _digest, _ed25519_sign, _ed25519_verify, _ensure_ed25519_keypair

REGISTRY_VERSION = "exp-i-pilot13-registry-v1"
ROOT_ID = "PILOT13-ROOT-1"

def fp(pem: str) -> str:
    return hashlib.sha256(pem.encode()).hexdigest()

def _init_root_store(path: str) -> None:
    con=sqlite3.connect(path)
    try:
        con.execute("CREATE TABLE IF NOT EXISTS root_issuance(transition_id TEXT PRIMARY KEY, trust_epoch INTEGER UNIQUE NOT NULL, body_digest TEXT NOT NULL, signature TEXT NOT NULL)")
        con.commit()
    finally: con.close()

def _root_worker(store: str, private_path: str, public_path: str) -> None:
    _ensure_ed25519_keypair(private_path, public_path); _init_root_store(store)
    public=Path(public_path).read_text(); print(json.dumps({"ready":True,"root_id":ROOT_ID,"public_key_pem":public}), flush=True)
    for line in sys.stdin:
        try:
            req=json.loads(line); op=req.get("op")
            if op=="sign":
                body=req["body"]; tid=str(body["transition_id"]); epoch=int(body["trust_epoch"]); bd=_digest(body)
                con=sqlite3.connect(store, timeout=10, isolation_level=None)
                try:
                    con.execute("BEGIN IMMEDIATE")
                    old=con.execute("SELECT trust_epoch,body_digest,signature FROM root_issuance WHERE transition_id=?",(tid,)).fetchone()
                    if old:
                        if int(old[0])!=epoch or old[1]!=bd: raise PermissionError("TRANSITION_REBIND_DENIED")
                        sig=old[2]; con.execute("COMMIT")
                    else:
                        last=con.execute("SELECT COALESCE(MAX(trust_epoch),0) FROM root_issuance").fetchone()[0]
                        if epoch!=int(last)+1: raise PermissionError("ROOT_EPOCH_NOT_EXACT_NEXT")
                        sig=_ed25519_sign(private_path,_canon(body))
                        con.execute("INSERT INTO root_issuance VALUES(?,?,?,?)",(tid,epoch,bd,sig)); con.execute("COMMIT")
                    print(json.dumps({"ok":True,"signature":sig}),flush=True)
                finally: con.close()
            else: print(json.dumps({"ok":False,"reason":"OPERATION_NOT_ALLOWED"}),flush=True)
        except Exception as exc: print(json.dumps({"ok":False,"reason":str(exc)}),flush=True)

class IsolatedRootAuthority:
    def __init__(self, directory: str|Path):
        d=Path(directory); d.mkdir(parents=True,exist_ok=True)
        self._store=str(d/"root-state.db"); self._private=str(d/"root-private.pem"); self._public=str(d/"root-public.pem"); self.proc=None; self.start()
    def start(self):
        if self.proc and self.proc.poll() is None: return
        self.proc=subprocess.Popen([sys.executable,__file__,"--root-worker",self._store,self._private,self._public],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True,bufsize=1)
        ready=json.loads(self.proc.stdout.readline());
        if not ready.get("ready"): raise RuntimeError("ROOT_START_FAILED")
        self.root_id=ready["root_id"]; self.public_key_pem=ready["public_key_pem"]
    def stop(self, kill=False):
        if self.proc and self.proc.poll() is None:
            self.proc.kill() if kill else self.proc.terminate(); self.proc.wait(timeout=5)
    def sign(self, body: Mapping[str,Any]) -> dict[str,Any]:
        if not self.proc or self.proc.poll() is not None: return {"ok":False,"reason":"ROOT_UNAVAILABLE"}
        self.proc.stdin.write(json.dumps({"op":"sign","body":dict(body)},sort_keys=True)+"\n"); self.proc.stdin.flush(); line=self.proc.stdout.readline()
        return json.loads(line) if line else {"ok":False,"reason":"ROOT_RESPONSE_LOST"}

class TrustedMinimumAuthority:
    def __init__(self,path:str|Path):
        self.path=str(path); con=sqlite3.connect(self.path); con.execute("CREATE TABLE IF NOT EXISTS minimum(id INTEGER PRIMARY KEY CHECK(id=1), trust_epoch INTEGER NOT NULL, event_digest TEXT NOT NULL)"); con.commit(); con.close()
    def advance(self,epoch:int,digest:str):
        con=sqlite3.connect(self.path,isolation_level=None)
        try:
            con.execute("BEGIN IMMEDIATE"); row=con.execute("SELECT trust_epoch,event_digest FROM minimum WHERE id=1").fetchone()
            if row and epoch<int(row[0]): raise PermissionError("MINIMUM_ROLLBACK_DENIED")
            if row and epoch==int(row[0]) and digest!=row[1]: raise PermissionError("MINIMUM_DIGEST_REBIND_DENIED")
            if not row: con.execute("INSERT INTO minimum VALUES(1,?,?)",(epoch,digest))
            elif epoch>int(row[0]): con.execute("UPDATE minimum SET trust_epoch=?,event_digest=? WHERE id=1",(epoch,digest))
            con.execute("COMMIT")
        finally: con.close()
    def current(self):
        con=sqlite3.connect(self.path); row=con.execute("SELECT trust_epoch,event_digest FROM minimum WHERE id=1").fetchone(); con.close();
        if not row: raise PermissionError("MINIMUM_UNSET")
        return int(row[0]),str(row[1])

class RootSignedRegistry:
    def __init__(self,path:str|Path,root:IsolatedRootAuthority):
        self.path=str(path); self.root=root; con=sqlite3.connect(self.path); con.execute("CREATE TABLE IF NOT EXISTS trust_events(trust_epoch INTEGER PRIMARY KEY,event_json TEXT NOT NULL,event_digest TEXT NOT NULL UNIQUE,signature TEXT NOT NULL)"); con.commit(); con.close()
    def transition(self,*,transition_id:str,key_id:str,public_key_pem:str,activation_generation:int):
        con=sqlite3.connect(self.path,timeout=10,isolation_level=None)
        try:
            con.execute("BEGIN IMMEDIATE"); last=con.execute("SELECT trust_epoch,event_json,event_digest FROM trust_events ORDER BY trust_epoch DESC LIMIT 1").fetchone()
            epoch=1 if not last else int(last[0])+1; pred="GENESIS" if not last else str(last[2]); prior=None if not last else json.loads(last[1])["active_key_id"]
            body={"registry_version":REGISTRY_VERSION,"transition_id":transition_id,"trust_epoch":epoch,"event_type":"BOOTSTRAP" if epoch==1 else "ROTATE_REVOKE","prior_key_id":prior,"prior_status_after":None if epoch==1 else "REVOKED","active_key_id":key_id,"active_public_key_pem":public_key_pem,"active_public_key_fingerprint":fp(public_key_pem),"activation_generation":activation_generation,"predecessor_event_digest":pred,"signer_root_id":self.root.root_id}
            signed=self.root.sign(body)
            if not signed.get("ok"): raise PermissionError(signed.get("reason","ROOT_SIGN_FAILED"))
            sig=signed["signature"]; digest=_digest({"event":body,"signature":sig})
            existing=con.execute("SELECT event_json,event_digest,signature FROM trust_events WHERE trust_epoch=?",(epoch,)).fetchone()
            if existing:
                if json.loads(existing[0])!=body: raise PermissionError("REGISTRY_EPOCH_CONFLICT")
                con.execute("COMMIT"); return {"event":body,"event_digest":existing[1],"signature":existing[2]}
            con.execute("INSERT INTO trust_events VALUES(?,?,?,?)",(epoch,json.dumps(body,sort_keys=True),digest,sig)); con.execute("COMMIT")
            return {"event":body,"event_digest":digest,"signature":sig}
        finally: con.close()

class PinnedRegistryReader:
    def __init__(self,path:str|Path,*,pinned_root_id:str,pinned_root_public_key_pem:str,minimum:TrustedMinimumAuthority):
        self.path=str(path); self.pinned_root_id=pinned_root_id; self.pinned_root_public_key_pem=pinned_root_public_key_pem; self.minimum=minimum
    def history(self):
        con=sqlite3.connect(self.path); rows=con.execute("SELECT trust_epoch,event_json,event_digest,signature FROM trust_events ORDER BY trust_epoch").fetchall(); con.close()
        if not rows: raise PermissionError("REGISTRY_EMPTY")
        pred="GENESIS"; seen=set(); out=[]
        for expected,(epoch,j,d,sig) in enumerate(rows,1):
            e=json.loads(j)
            if int(epoch)!=expected or int(e.get("trust_epoch",-1))!=expected: raise PermissionError("TRUST_EPOCH_CHAIN_INVALID")
            if e.get("registry_version")!=REGISTRY_VERSION or e.get("predecessor_event_digest")!=pred: raise PermissionError("TRUST_PREDECESSOR_INVALID")
            if e.get("signer_root_id")!=self.pinned_root_id: raise PermissionError("ROOT_ID_MISMATCH")
            if fp(str(e.get("active_public_key_pem","")))!=e.get("active_public_key_fingerprint"): raise PermissionError("TRUST_FINGERPRINT_INVALID")
            if e.get("active_key_id") in seen: raise PermissionError("TRUST_KEY_ID_REUSE")
            if not _ed25519_verify(self.pinned_root_public_key_pem,_canon(e),str(sig)): raise PermissionError("ROOT_SIGNATURE_INVALID")
            if _digest({"event":e,"signature":sig})!=str(d): raise PermissionError("TRUST_EVENT_DIGEST_INVALID")
            seen.add(e["active_key_id"]); pred=str(d); out.append({"event":e,"event_digest":str(d),"signature":str(sig)})
        min_epoch,min_digest=self.minimum.current()
        if len(out)<min_epoch: raise PermissionError("TRUST_BELOW_MINIMUM")
        if out[min_epoch-1]["event_digest"]!=min_digest: raise PermissionError("TRUST_MINIMUM_DIGEST_MISMATCH")
        return out
    def current(self): return self.history()[-1]

if __name__=="__main__" and len(sys.argv)>1 and sys.argv[1]=="--root-worker":
    _root_worker(sys.argv[2],sys.argv[3],sys.argv[4])
