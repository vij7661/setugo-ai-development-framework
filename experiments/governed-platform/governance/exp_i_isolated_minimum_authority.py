"""EXP-I Pilot 16: isolated trusted-minimum advancement authority."""
from __future__ import annotations
import hashlib, json, os, sqlite3, subprocess, sys, threading
from pathlib import Path
from typing import Any

from exp_i_asymmetric_checkpoint_signer import _canon, _digest, _ensure_ed25519_keypair, _ed25519_sign, _ed25519_verify
from exp_i_registry_root_isolation import fp
from exp_i_root_rotation import PlatformRootTrustAuthority, RootMinimumAuthority


def _permit_body(recovery_id:str,current_epoch:int,current_digest:str,target:dict[str,Any])->dict[str,Any]:
    r=target['record']
    return {
        'recovery_id':recovery_id,
        'current_minimum_epoch':int(current_epoch),
        'current_minimum_digest':current_digest,
        'target_root_epoch':int(r['root_epoch']),
        'target_root_record_digest':target['record_digest'],
        'target_root_id':r['active_root_id'],
        'target_public_key_fingerprint':r['active_public_key_fingerprint'],
        'predecessor_root_record_digest':r['predecessor_root_record_digest'],
        'transition_id':r['transition_id'],
        'activation_registry_epoch':int(r['activation_registry_epoch']),
    }


class RecoveryAuthorizationAuthority:
    """Platform-owned permit signer. Private key is not passed to minimum worker."""
    def __init__(self, private_path:str|Path, public_path:str|Path):
        self.private_path=str(private_path); self.public_path=str(public_path)
        _ensure_ed25519_keypair(self.private_path,self.public_path)
    @property
    def public_key_pem(self)->str: return Path(self.public_path).read_text()
    def issue(self,recovery_id:str,current_epoch:int,current_digest:str,target:dict[str,Any])->dict[str,Any]:
        body=_permit_body(recovery_id,current_epoch,current_digest,target)
        return {'permit':body,'signature':_ed25519_sign(self.private_path,_canon(body))}


def _ensure_min_schema(path:str)->None:
    c=sqlite3.connect(path)
    try:
        c.execute('CREATE TABLE IF NOT EXISTS minimum(id INTEGER PRIMARY KEY CHECK(id=1),root_epoch INTEGER NOT NULL,record_digest TEXT NOT NULL)')
        c.execute('CREATE TABLE IF NOT EXISTS recovery_ledger(recovery_id TEXT PRIMARY KEY,permit_digest TEXT NOT NULL,target_epoch INTEGER NOT NULL,target_digest TEXT NOT NULL)')
        c.commit()
    finally:c.close()


def _worker(root_db:str,root_auth:str,min_db:str,recovery_public_pem:str)->None:
    _ensure_min_schema(min_db)
    for line in sys.stdin:
        try:
            req=json.loads(line); op=req.get('op')
            if op=='ping': out={'ok':True,'pid':os.getpid()}
            elif op=='read':
                c=sqlite3.connect(min_db); row=c.execute('SELECT root_epoch,record_digest FROM minimum WHERE id=1').fetchone(); c.close()
                out={'ok':True,'minimum':None if row is None else [int(row[0]),str(row[1])],'pid':os.getpid()}
            elif op=='advance': out=_advance(root_db,root_auth,min_db,recovery_public_pem,req.get('authorization'))
            else: out={'ok':False,'reason':'UNKNOWN_OPERATION'}
        except Exception as e: out={'ok':False,'reason':f'{type(e).__name__}:{e}'}
        print(json.dumps(out,sort_keys=True),flush=True)


def _advance(root_db:str,root_auth:str,min_db:str,recovery_public_pem:str,authorization:Any)->dict[str,Any]:
    if not isinstance(authorization,dict): return {'ok':False,'reason':'RECOVERY_AUTHORIZATION_REQUIRED'}
    body=authorization.get('permit'); sig=authorization.get('signature')
    if not isinstance(body,dict) or not isinstance(sig,str) or not _ed25519_verify(recovery_public_pem,_canon(body),sig):
        return {'ok':False,'reason':'RECOVERY_AUTHORIZATION_INVALID'}
    trust=PlatformRootTrustAuthority(root_db,root_auth)
    history=trust.history(None)
    target=None
    for item in history:
        if int(item['record']['root_epoch'])==int(body.get('target_root_epoch',-1)):
            target=item; break
    if target is None:return {'ok':False,'reason':'TARGET_ROOT_NOT_FOUND'}
    exact=_permit_body(body.get('recovery_id',''),int(body.get('current_minimum_epoch',-1)),str(body.get('current_minimum_digest','')),target)
    if exact!=body:return {'ok':False,'reason':'RECOVERY_BINDING_MISMATCH'}
    c=sqlite3.connect(min_db,timeout=10,isolation_level=None)
    try:
        c.execute('BEGIN IMMEDIATE')
        row=c.execute('SELECT root_epoch,record_digest FROM minimum WHERE id=1').fetchone()
        if row is None:
            c.execute('ROLLBACK'); return {'ok':False,'reason':'MINIMUM_NOT_BOOTSTRAPPED'}
        ce,cd=int(row[0]),str(row[1]); pd=_digest({'permit':body,'signature':sig})
        prior=c.execute('SELECT permit_digest,target_epoch,target_digest FROM recovery_ledger WHERE recovery_id=?',(body['recovery_id'],)).fetchone()
        if prior:
            if (str(prior[0]),int(prior[1]),str(prior[2]))!=(pd,int(body['target_root_epoch']),str(body['target_root_record_digest'])):
                c.execute('ROLLBACK'); return {'ok':False,'reason':'RECOVERY_ID_REBIND_DENIED'}
            if ce==int(body['target_root_epoch']) and cd==body['target_root_record_digest']:
                c.execute('COMMIT'); return {'ok':True,'replay':True,'minimum':[ce,cd]}
        if ce!=int(body['current_minimum_epoch']) or cd!=body['current_minimum_digest']:
            c.execute('ROLLBACK'); return {'ok':False,'reason':'CURRENT_MINIMUM_BINDING_MISMATCH'}
        te=int(body['target_root_epoch']); td=str(body['target_root_record_digest'])
        if te!=ce+1:
            c.execute('ROLLBACK'); return {'ok':False,'reason':'TARGET_EPOCH_NOT_CONTIGUOUS'}
        if body['predecessor_root_record_digest']!=cd:
            c.execute('ROLLBACK'); return {'ok':False,'reason':'PREDECESSOR_MISMATCH'}
        c.execute('INSERT INTO recovery_ledger VALUES(?,?,?,?)',(body['recovery_id'],pd,te,td))
        c.execute('UPDATE minimum SET root_epoch=?,record_digest=? WHERE id=1',(te,td)); c.execute('COMMIT')
        return {'ok':True,'replay':False,'minimum':[te,td]}
    finally:c.close()


class MinimumAuthorityProcess:
    def __init__(self,root_db:str|Path,root_auth:str|Path,min_db:str|Path,recovery_public_pem:str):
        self.root_db=str(root_db); self.root_auth=str(root_auth); self.min_db=str(min_db); self.recovery_public_pem=recovery_public_pem
        _ensure_min_schema(self.min_db); self.proc=None; self._lock=threading.Lock(); self.start()
    def start(self):
        if self.proc and self.proc.poll() is None:return
        self.proc=subprocess.Popen([sys.executable,__file__,'--worker',self.root_db,self.root_auth,self.min_db],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,env={**os.environ,'EXP_I_RECOVERY_PUBLIC_PEM':self.recovery_public_pem})
    def stop(self,kill=False):
        if not self.proc:return
        if self.proc.poll() is None:
            (self.proc.kill() if kill else self.proc.terminate()); self.proc.wait(timeout=5)
        for h in (self.proc.stdin,self.proc.stdout,self.proc.stderr):
            if h:
                try:h.close()
                except Exception:pass
    def request(self,payload:dict[str,Any])->dict[str,Any]:
        if not self.proc or self.proc.poll() is not None:return {'ok':False,'reason':'MINIMUM_AUTHORITY_UNAVAILABLE'}
        with self._lock:
            self.proc.stdin.write(json.dumps(payload,sort_keys=True)+'\n'); self.proc.stdin.flush(); line=self.proc.stdout.readline()
        return json.loads(line) if line else {'ok':False,'reason':'MINIMUM_AUTHORITY_UNAVAILABLE'}
    def advance(self,authorization:dict[str,Any]|None):return self.request({'op':'advance','authorization':authorization})
    def read(self):return self.request({'op':'read'})


if __name__=='__main__':
    if len(sys.argv)>=5 and sys.argv[1]=='--worker': _worker(sys.argv[2],sys.argv[3],sys.argv[4],os.environ['EXP_I_RECOVERY_PUBLIC_PEM'])
    else: raise SystemExit('WORKER_MODE_REQUIRED')
