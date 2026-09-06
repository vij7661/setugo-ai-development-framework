"""EXP-O Pilot 12 process harness/client for trusted lease semantic permits."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any
from urllib import request as urlrequest

from semantic_process_exp_o import SemanticLoopbackClient


class TrustedLeaseSemanticLoopbackClient(SemanticLoopbackClient):
    def release_test_hold(self) -> dict[str, Any]:
        req=urlrequest.Request(self.base_url+"/test/release-hold",data=b"{}",headers={"Content-Type":"application/json"},method="POST")
        with urlrequest.urlopen(req,timeout=self.timeout_s) as response: return json.loads(response.read().decode("utf-8"))
    def renew(self,bound_permit_id:str,lease_epoch:int,**extra:Any)->dict[str,Any]:
        body={"bound_permit_id":bound_permit_id,"lease_epoch":lease_epoch,**extra}
        req=urlrequest.Request(self.base_url+"/renew",data=json.dumps(body).encode("utf-8"),headers={"Content-Type":"application/json"},method="POST")
        with urlrequest.urlopen(req,timeout=self.timeout_s) as response: return json.loads(response.read().decode("utf-8"))


class TrustedLeaseSemanticGatewayProcessHarness:
    def __init__(self,*,effects_db_path:str|Path,registry_db_path:str|Path,lease_db_path:str|Path,ready_path:str|Path,clock_path:str|Path,outer_permit_key:bytes,registry_key:bytes,lease_key:bytes,inner_permit_key:bytes,enable_test_faults:bool=True)->None:
        self.effects_db_path=Path(effects_db_path); self.registry_db_path=Path(registry_db_path); self.lease_db_path=Path(lease_db_path); self.ready_path=Path(ready_path); self.clock_path=Path(clock_path)
        self.outer_permit_key=bytes(outer_permit_key); self.registry_key=bytes(registry_key); self.lease_key=bytes(lease_key); self.inner_permit_key=bytes(inner_permit_key); self.enable_test_faults=bool(enable_test_faults)
        self.process:subprocess.Popen[bytes]|None=None; self.info:dict[str,Any]|None=None
    @property
    def script_path(self)->Path: return Path(__file__).with_name("mcp_semantic_trusted_lease_gateway_process_exp_o.py")
    def start(self,*,timeout_s:float=5.0)->dict[str,Any]:
        if self.process is not None and self.process.poll() is None: raise RuntimeError("trusted lease gateway process already running")
        self.ready_path.unlink(missing_ok=True); env=os.environ.copy(); env.pop("EXP_O_SEMANTIC_VERIFIER_SIGNING_KEY_HEX",None); env.pop("EXP_O_AUTHORITY_KERNEL_SIGNING_KEY_HEX",None)
        env["EXP_O_OUTER_PERMIT_KEY_HEX"]=self.outer_permit_key.hex(); env["EXP_O_SEMANTIC_REGISTRY_KEY_HEX"]=self.registry_key.hex(); env["EXP_O_TRUSTED_LEASE_KEY_HEX"]=self.lease_key.hex(); env["EXP_O_INNER_PERMIT_KEY_HEX"]=self.inner_permit_key.hex()
        args=[sys.executable,str(self.script_path),"--effects-db",str(self.effects_db_path),"--registry-db",str(self.registry_db_path),"--lease-db",str(self.lease_db_path),"--ready-file",str(self.ready_path),"--clock-file",str(self.clock_path)]
        if self.enable_test_faults: args.append("--enable-test-faults")
        self.process=subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,env=env); deadline=time.monotonic()+timeout_s
        while time.monotonic()<deadline:
            if self.process.poll() is not None:
                code=self.process.returncode; self.process=None; raise RuntimeError(f"trusted lease semantic gateway exited early with {code}")
            if self.ready_path.exists(): self.info=json.loads(self.ready_path.read_text(encoding="utf-8")); return dict(self.info)
            time.sleep(0.02)
        self.stop(); raise TimeoutError("trusted lease semantic gateway did not become ready")
    @property
    def base_url(self)->str:
        if not self.info: raise RuntimeError("trusted lease gateway not started")
        return f"http://127.0.0.1:{int(self.info['port'])}"
    def client(self,*,timeout_s:float=2.0)->TrustedLeaseSemanticLoopbackClient: return TrustedLeaseSemanticLoopbackClient(self.base_url,timeout_s=timeout_s)
    def stop(self)->None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try: self.process.wait(timeout=2.0)
            except subprocess.TimeoutExpired: self.process.kill(); self.process.wait(timeout=2.0)
        self.process=None; self.info=None
    def restart(self,*,timeout_s:float=5.0)->dict[str,Any]: self.stop(); return self.start(timeout_s=timeout_s)
