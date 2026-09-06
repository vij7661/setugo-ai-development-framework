"""EXP-O Pilot 23 witness path: no checkpoint minting key; exact oracle-decision binding."""
from __future__ import annotations
import json,os,subprocess,sys
from pathlib import Path
from typing import Any,Mapping
from checkpoint_authority_process_exp_o import checkpoint_digest
from process_witness_store_integrity_exp_o import _commit_signature, init_store, verify_store

class OracleWitnessProcess:
    def __init__(self,*,witness_id:str,key_id:str,signing_key:bytes,store:str|Path,store_identity:str):
        self.witness_id=witness_id;self.key_id=key_id;self.store=str(store);self.store_identity=store_identity
        if not Path(self.store).exists():init_store(self.store,store_identity=store_identity)
        env=dict(os.environ);env["EXP_O_WITNESS_KEY_HEX"]=signing_key.hex();env.pop("EXP_O_CHECKPOINT_KEY_HEX",None);env.pop("EXP_O_WITNESS_CHECKPOINT_KEY_HEX",None)
        self.argv=[sys.executable,str(Path(__file__).resolve()),"--worker",witness_id,key_id,self.store,store_identity]
        self.proc=subprocess.Popen(self.argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,env=env)
        r=json.loads(self.proc.stdout.readline());self.pid=int(r["pid"]);self.env_keys=list(r.get("env_keys",[]))
    def sign(self,statement:Mapping[str,Any],*,checkpoint_record:Mapping[str,Any],verification_decision:Mapping[str,Any],minimum_checkpoint_generation:int)->dict[str,Any]:
        if self.proc.poll() is not None:return {"approved":False,"reason":"WITNESS_UNAVAILABLE"}
        q={"op":"sign","statement":dict(statement),"checkpoint_record":dict(checkpoint_record),"verification_decision":dict(verification_decision),"minimum_checkpoint_generation":int(minimum_checkpoint_generation)}
        self.proc.stdin.write(json.dumps(q,sort_keys=True)+"\n");self.proc.stdin.flush();line=self.proc.stdout.readline();return json.loads(line) if line else {"approved":False,"reason":"WITNESS_RESPONSE_LOST"}
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

def _decision_ok(store:str,store_identity:str,witness_id:str,record:Mapping[str,Any],decision:Mapping[str,Any],minimum:int)->tuple[bool,str]:
    local=verify_store(store,expected_store_identity=store_identity)
    if not local.get("ok"):return False,str(local.get("reason"))
    if not decision.get("ok"):return False,"CHECKPOINT_NOT_VERIFIED"
    try:
        rd=checkpoint_digest(record["statement"])
        if str(record.get("checkpoint_digest"))!=rd:return False,"CHECKPOINT_RECORD_DIGEST_MISMATCH"
        if str(decision.get("checkpoint_digest"))!=rd:return False,"ORACLE_DECISION_CHECKPOINT_MISMATCH"
        token=decision["verification_token"]
        if str(token.get("checkpoint_digest"))!=rd or str(token.get("witness_id"))!=witness_id or str(token.get("store_identity"))!=store_identity:return False,"ORACLE_DECISION_SCOPE_MISMATCH"
        if str(token.get("history_root"))!=str(local["history_root"]):return False,"ORACLE_DECISION_HISTORY_MISMATCH"
        if int(token.get("checkpoint_generation",-1))<int(minimum):return False,"ORACLE_DECISION_ROLLBACK"
        if int(record["statement"].get("max_generation",-2))!=int(local["max_generation"]):return False,"CHECKPOINT_LOCAL_MAX_MISMATCH"
        if str(record["statement"].get("history_root"))!=str(local["history_root"]):return False,"CHECKPOINT_LOCAL_HISTORY_MISMATCH"
    except Exception:return False,"ORACLE_DECISION_MALFORMED"
    return True,"OK"

def _main(wid:str,kid:str,store:str,sid:str)->int:
    key=bytes.fromhex(os.environ.get("EXP_O_WITNESS_KEY_HEX",""));
    if not Path(store).exists():init_store(store,store_identity=sid)
    forbidden=[k for k in os.environ if "CHECKPOINT_KEY" in k or "WITNESS_CHECKPOINT" in k]
    print(json.dumps({"ready":True,"pid":os.getpid(),"env_keys":forbidden}),flush=True)
    for line in sys.stdin:
        q=json.loads(line)
        if q.get("op")=="stop":return 0
        if q.get("op")!="sign":print(json.dumps({"approved":False,"reason":"OP_INVALID"}),flush=True);continue
        ok,reason=_decision_ok(store,sid,wid,q.get("checkpoint_record",{}),q.get("verification_decision",{}),int(q.get("minimum_checkpoint_generation",0)))
        if not ok:print(json.dumps({"approved":False,"reason":reason,"witness_id":wid}),flush=True);continue
        r=_commit_signature(store,witness_id=wid,key_id=kid,key=key,store_identity=sid,statement=q["statement"]);print(json.dumps(r,sort_keys=True),flush=True)
    return 0
if __name__=="__main__" and len(sys.argv)==6 and sys.argv[1]=="--worker":raise SystemExit(_main(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5]))
