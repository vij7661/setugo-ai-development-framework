"""EXP-O Pilot 23: isolated checkpoint authority with durable monotonic issuance."""
from __future__ import annotations
import hashlib,hmac,json,os,sqlite3,subprocess,sys,time
from pathlib import Path
from typing import Any,Mapping

VERSION="exp-o-pilot23-v1"

def _canon(v:Any)->bytes:return json.dumps(v,sort_keys=True,separators=(",",":")).encode()
def _dig(v:Any)->str:return hashlib.sha256(_canon(v)).hexdigest()
def checkpoint_statement(*,witness_id:str,key_id:str,store_identity:str,history_root:str,max_generation:int,checkpoint_generation:int)->dict[str,Any]:
    return {"version":VERSION,"witness_id":witness_id,"key_id":key_id,"store_identity":store_identity,"history_root":history_root,"max_generation":int(max_generation),"checkpoint_generation":int(checkpoint_generation)}
def checkpoint_digest(s:Mapping[str,Any])->str:return _dig(dict(s))
def _tag(s:Mapping[str,Any],key:bytes)->str:return hmac.new(key,_canon(dict(s)),hashlib.sha256).hexdigest()
def init_authority_store(path:str|Path)->None:
    Path(path).parent.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(str(path),isolation_level=None); c.execute("PRAGMA journal_mode=WAL");c.execute("PRAGMA synchronous=FULL")
    c.execute("CREATE TABLE IF NOT EXISTS issued(witness_id TEXT NOT NULL,store_identity TEXT NOT NULL,checkpoint_generation INTEGER NOT NULL,checkpoint_digest TEXT NOT NULL,auth_tag TEXT NOT NULL,PRIMARY KEY(witness_id,store_identity,checkpoint_generation))")
    c.execute("CREATE TABLE IF NOT EXISTS maxima(witness_id TEXT NOT NULL,store_identity TEXT NOT NULL,max_checkpoint_generation INTEGER NOT NULL,PRIMARY KEY(witness_id,store_identity))");c.close()

def _issue(path:str|Path,s:Mapping[str,Any],key:bytes)->dict[str,Any]:
    g=int(s["checkpoint_generation"]); wid=str(s["witness_id"]); sid=str(s["store_identity"]); d=checkpoint_digest(s); c=sqlite3.connect(str(path),isolation_level=None);c.row_factory=sqlite3.Row
    try:
        c.execute("BEGIN IMMEDIATE"); m=c.execute("SELECT max_checkpoint_generation FROM maxima WHERE witness_id=? AND store_identity=?",(wid,sid)).fetchone(); maximum=int(m[0]) if m else -1
        row=c.execute("SELECT checkpoint_digest,auth_tag FROM issued WHERE witness_id=? AND store_identity=? AND checkpoint_generation=?",(wid,sid,g)).fetchone()
        if g<maximum:c.execute("ROLLBACK");return {"ok":False,"reason":"CHECKPOINT_GENERATION_ROLLBACK","maximum":maximum}
        if row:
            if not hmac.compare_digest(str(row[0]),d):c.execute("ROLLBACK");return {"ok":False,"reason":"CHECKPOINT_SAME_GENERATION_EQUIVOCATION"}
            c.execute("COMMIT");return {"ok":True,"replay":True,"statement":dict(s),"checkpoint_digest":d,"auth_tag":str(row[1])}
        t=_tag(s,key);c.execute("INSERT INTO issued VALUES(?,?,?,?,?)",(wid,sid,g,d,t))
        if m:c.execute("UPDATE maxima SET max_checkpoint_generation=? WHERE witness_id=? AND store_identity=?",(g,wid,sid))
        else:c.execute("INSERT INTO maxima VALUES(?,?,?)",(wid,sid,g))
        c.execute("COMMIT");return {"ok":True,"replay":False,"statement":dict(s),"checkpoint_digest":d,"auth_tag":t}
    except BaseException:
        try:c.execute("ROLLBACK")
        except Exception:pass
        raise
    finally:c.close()

def _verify(record:Mapping[str,Any],key:bytes,*,minimum_generation:int,expected_witness_id:str,expected_store_identity:str,expected_key_id:str)->dict[str,Any]:
    try:s=dict(record["statement"]);t=str(record["auth_tag"]);d=str(record["checkpoint_digest"])
    except Exception:return {"ok":False,"reason":"CHECKPOINT_MALFORMED"}
    if checkpoint_digest(s)!=d:return {"ok":False,"reason":"CHECKPOINT_DIGEST_MISMATCH"}
    if not hmac.compare_digest(_tag(s,key),t):return {"ok":False,"reason":"CHECKPOINT_AUTH_FAILED"}
    if s.get("version")!=VERSION:return {"ok":False,"reason":"CHECKPOINT_VERSION_MISMATCH"}
    if str(s.get("witness_id"))!=expected_witness_id or str(s.get("store_identity"))!=expected_store_identity or str(s.get("key_id"))!=expected_key_id:return {"ok":False,"reason":"CHECKPOINT_SCOPE_MISMATCH"}
    if int(s.get("checkpoint_generation",-1))<int(minimum_generation):return {"ok":False,"reason":"CHECKPOINT_ROLLBACK"}
    return {"ok":True,"checkpoint_digest":d,"statement":s}

def _verification_token(v:Mapping[str,Any],verification_key:bytes)->dict[str,Any]:
    body={"version":VERSION,"checkpoint_digest":v["checkpoint_digest"],"witness_id":v["statement"]["witness_id"],"store_identity":v["statement"]["store_identity"],"history_root":v["statement"]["history_root"],"max_generation":v["statement"]["max_generation"],"checkpoint_generation":v["statement"]["checkpoint_generation"],"issued_at_ms":int(time.time()*1000)}
    return {**body,"verification_tag":hmac.new(verification_key,_canon(body),hashlib.sha256).hexdigest()}
def verify_token(token:Mapping[str,Any],verification_key:bytes,*,checkpoint_digest_expected:str,witness_id:str,store_identity:str,history_root:str,minimum_checkpoint_generation:int)->dict[str,Any]:
    try:tag=str(token["verification_tag"]);body={k:token[k] for k in ("version","checkpoint_digest","witness_id","store_identity","history_root","max_generation","checkpoint_generation","issued_at_ms")}
    except Exception:return {"ok":False,"reason":"VERIFICATION_TOKEN_MALFORMED"}
    if not hmac.compare_digest(tag,hmac.new(verification_key,_canon(body),hashlib.sha256).hexdigest()):return {"ok":False,"reason":"VERIFICATION_TOKEN_AUTH_FAILED"}
    if body["checkpoint_digest"]!=checkpoint_digest_expected or body["witness_id"]!=witness_id or body["store_identity"]!=store_identity or body["history_root"]!=history_root:return {"ok":False,"reason":"VERIFICATION_TOKEN_BINDING_MISMATCH"}
    if int(body["checkpoint_generation"])<int(minimum_checkpoint_generation):return {"ok":False,"reason":"VERIFICATION_TOKEN_ROLLBACK"}
    return {"ok":True,"body":body}

class CheckpointAuthorityProcess:
    def __init__(self,*,store:str|Path,checkpoint_key:bytes,verification_key:bytes):
        self.store=str(store);init_authority_store(self.store);env=dict(os.environ);env["EXP_O_CHECKPOINT_KEY_HEX"]=checkpoint_key.hex();env["EXP_O_VERIFY_TOKEN_KEY_HEX"]=verification_key.hex();self.argv=[sys.executable,str(Path(__file__).resolve()),"--worker",self.store]
        self.proc=subprocess.Popen(self.argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,env=env);r=json.loads(self.proc.stdout.readline());self.pid=int(r["pid"])
    def call(self,req:Mapping[str,Any])->dict[str,Any]:
        if self.proc.poll() is not None:return {"ok":False,"reason":"CHECKPOINT_AUTHORITY_UNAVAILABLE"}
        self.proc.stdin.write(json.dumps(dict(req),sort_keys=True)+"\n");self.proc.stdin.flush();line=self.proc.stdout.readline();return json.loads(line) if line else {"ok":False,"reason":"CHECKPOINT_AUTHORITY_RESPONSE_LOST"}
    def issue(self,s:Mapping[str,Any],*,crash_after_commit:bool=False)->dict[str,Any]:return self.call({"op":"issue","statement":dict(s),"crash_after_commit":crash_after_commit})
    def verify(self,record:Mapping[str,Any],*,minimum_generation:int,expected_witness_id:str,expected_store_identity:str,expected_key_id:str)->dict[str,Any]:return self.call({"op":"verify","record":dict(record),"minimum_generation":minimum_generation,"expected_witness_id":expected_witness_id,"expected_store_identity":expected_store_identity,"expected_key_id":expected_key_id})
    def stop(self,kill:bool=False):
        if self.proc.poll() is None:
            if kill:self.proc.kill()
            else:
                try:self.proc.stdin.write('{"op":"stop"}\n');self.proc.stdin.flush()
                except Exception:self.proc.terminate()
            try:self.proc.wait(timeout=4)
            except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait(timeout=4)
        for x in (self.proc.stdin,self.proc.stdout,self.proc.stderr):
            try:x.close() if x else None
            except Exception:pass

def _main(store:str)->int:
    ck=bytes.fromhex(os.environ.get("EXP_O_CHECKPOINT_KEY_HEX",""));vk=bytes.fromhex(os.environ.get("EXP_O_VERIFY_TOKEN_KEY_HEX",""));init_authority_store(store);print(json.dumps({"ready":True,"pid":os.getpid()}),flush=True)
    for line in sys.stdin:
        q=json.loads(line);op=q.get("op")
        if op=="stop":return 0
        if op=="issue":
            r=_issue(store,q["statement"],ck)
            if q.get("crash_after_commit") and r.get("ok"):os._exit(93)
            print(json.dumps(r,sort_keys=True),flush=True)
        elif op=="verify":
            v=_verify(q["record"],ck,minimum_generation=int(q["minimum_generation"]),expected_witness_id=q["expected_witness_id"],expected_store_identity=q["expected_store_identity"],expected_key_id=q["expected_key_id"])
            if v.get("ok"):v["verification_token"]=_verification_token(v,vk)
            print(json.dumps(v,sort_keys=True),flush=True)
        else:print(json.dumps({"ok":False,"reason":"OP_INVALID"}),flush=True)
    return 0
if __name__=="__main__" and len(sys.argv)==3 and sys.argv[1]=="--worker":raise SystemExit(_main(sys.argv[2]))
