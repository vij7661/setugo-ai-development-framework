from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import threading
import time
import unittest

from runtime_process_exp_o import FileTrustedClock, read_gateway_effect_count
from runtime_slice_exp_o import AuthorityKernel, LocalEnforcementPoint
from semantic_permit_registry_exp_o import DurableSemanticBoundLocalEnforcementPoint, DurableSemanticPermitRegistry, REGISTRY_BINDING_FIELDS
from semantic_trusted_lease_exp_o import TrustedLeaseSemanticBoundLocalEnforcementPoint, TrustedSemanticLeaseRegistry
from semantic_trusted_lease_process_exp_o import TrustedLeaseSemanticGatewayProcessHarness
from semantic_verification_binding_exp_o import SemanticVerificationAuthority, digest


class ExpOPilot12TrustedLeaseSplitBrainTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="exp-o-p12-lease-")
        root = Path(self.tmp.name)
        self.effects_db = root / "effects.sqlite"
        self.registry_db = root / "semantic-and-trusted-lease.sqlite"
        self.clock_path = root / "clock.txt"
        self.clock_path.write_text("100000", encoding="utf-8")
        self.kernel_key=b"p12-kernel"; self.inner_key=b"p12-inner"; self.semantic_key=b"p12-semantic"; self.outer_key=b"p12-outer"; self.registry_key=b"p12-registry"; self.lease_key=b"p12-lease"
        self.kernel=AuthorityKernel(self.kernel_key)
        base_lep=LocalEnforcementPoint(self.kernel,self.inner_key)
        self.verifier=SemanticVerificationAuthority(self.semantic_key,verifier_id="p12-independent-verifier")
        self.p10=DurableSemanticPermitRegistry(self.registry_db,self.registry_key)
        p10_lep=DurableSemanticBoundLocalEnforcementPoint(base_lep,semantic_verification_key=self.verifier.verification_key,outer_permit_signing_key=self.outer_key,registry=self.p10)
        self.clock=FileTrustedClock(self.clock_path)
        self.leases=TrustedSemanticLeaseRegistry(self.registry_db,self.lease_key,self.p10,self.clock)
        self.bound_lep=TrustedLeaseSemanticBoundLocalEnforcementPoint(p10_lep,self.leases)
        self.capability=self.kernel.issue_capability(subject_id="worker",subject_key_thumbprint="worker-key",issued_at_ms=90000,expires_at_ms=120000,freshness_class="WORKSPACE_MUTATION",allowed_actions=["WRITE"],allowed_resources=["src/app.py"],effect_contract_id="contract-v1",base_sha="base-v1")
        self.contract={"effect_contract_id":"contract-v1","base_sha":"base-v1","allowed_action_classes":["WRITE"],"allowed_resources":["src/app.py"],"forbidden_resources":["prod/**",".github/**","secrets/**"],"max_changed_files":1,"destructive_effect_allowed":False,"semantic_correspondence_required":True}
        self.a={"change_intent":"Apply independently verified correction A","rationale":"A"}
        self.b={"change_intent":"Apply independently verified correction B","rationale":"B"}
        self.harnesses=[]

    def tearDown(self)->None:
        for h in self.harnesses: h.stop()
        self.tmp.cleanup()

    def set_clock(self,value:int)->None: self.clock_path.write_text(str(value),encoding="utf-8")
    def effect_for(self,candidate:dict)->dict:
        return {"action_class":"WRITE","target_resources":["src/app.py"],"changed_files":["src/app.py"],"base_sha":"base-v1","effect_contract_id":"contract-v1","destructive_effect":False,"provenance_trust_classes":["REMOTE_MODEL_PROPOSAL"],"semantic_payload_digest":digest(candidate)}
    def issue(self,candidate:dict,*,key:str,effect:dict|None=None):
        e=copy.deepcopy(effect if effect is not None else self.effect_for(candidate)); evidence=self.verifier.verify_candidate(candidate_payload=candidate,effect=e)
        auth=self.bound_lep.authorize(self.capability,candidate_payload=candidate,semantic_verification=evidence,worker_id="worker",worker_key_thumbprint="worker-key",effect_contract=self.contract,effect=e,idempotency_key=key,now_ms=100000,origin_available=True,online_authority_confirmed=False)
        self.assertTrue(auth.get("authorized"),auth); return auth,e
    def harness(self,name:str)->TrustedLeaseSemanticGatewayProcessHarness:
        root=Path(self.tmp.name); h=TrustedLeaseSemanticGatewayProcessHarness(effects_db_path=self.effects_db,registry_db_path=self.registry_db,lease_db_path=self.registry_db,ready_path=root/f"ready-{name}.json",clock_path=self.clock_path,outer_permit_key=self.outer_key,registry_key=self.registry_key,lease_key=self.lease_key,inner_permit_key=self.inner_key,enable_test_faults=True); h.start(); self.harnesses.append(h); return h
    def execute(self,h,auth,candidate,effect,key,*,fault=None):
        return h.client(timeout_s=1.5).execute(permit=auth["permit"],candidate_payload=candidate,worker_id="worker",worker_key_thumbprint="worker-key",effect=effect,idempotency_key=key,fault_mode=fault)
    def bound_id(self,auth): return str(auth["permit"]["payload"]["bound_permit_id"])
    def expected(self,auth): return {f:auth["permit"]["payload"].get(f) for f in REGISTRY_BINDING_FIELDS if f!="bound_permit_id"}
    def hold_owner(self,key="held"):
        auth,e=self.issue(self.a,key=key); a=self.harness("a-"+key); box={}
        def run(): box["result"]=self.execute(a,auth,self.a,e,key,fault="HOLD_AFTER_RESOLVE")
        t=threading.Thread(target=run,daemon=True); t.start(); bid=self.bound_id(auth); deadline=time.monotonic()+2
        while time.monotonic()<deadline:
            s=self.leases.inspect(bid)
            if s.get("state")=="IN_FLIGHT": return auth,e,bid,a,t,box,s
            time.sleep(.01)
        self.fail("owner did not become IN_FLIGHT")
    def release(self,h,t,box): h.client().release_test_hold(); t.join(timeout=3); self.assertFalse(t.is_alive()); return box.get("result")

    def test_p12_01_first_owner_receives_trusted_lease_deadline(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-01"); self.assertEqual(s["lease_epoch"],1); self.assertEqual(s["lease_expires_at_ms"],101000); self.assertEqual(s["lease_owner_gateway_instance_id"],a.info["gateway_instance_id"]); self.release(a,t,box)

    def test_p12_02_different_live_gateway_before_expiry_cannot_take_over(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-02"); b=self.harness("b-p12-02"); self.set_clock(100999); r=self.execute(b,auth,self.a,e,"p12-02"); self.assertFalse(r["authorized"]); self.assertEqual(r["reason"],"TRUSTED_LEASE_LIVE_OWNER_UNEXPIRED"); self.release(a,t,box)

    def test_p12_03_failed_preexpiry_takeover_does_not_mutate_fence(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-03"); before=self.leases.inspect(bid); b=self.harness("b-p12-03"); self.set_clock(100999); self.execute(b,auth,self.a,e,"p12-03"); after=self.leases.inspect(bid); self.assertEqual((after["lease_owner_gateway_instance_id"],after["lease_epoch"],after["lease_expires_at_ms"]),(before["lease_owner_gateway_instance_id"],before["lease_epoch"],before["lease_expires_at_ms"])); self.assertEqual(read_gateway_effect_count(self.effects_db),0); self.release(a,t,box)

    def test_p12_04_current_owner_renews_without_epoch_change(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-04"); self.set_clock(100500); r=a.client().renew(bid,1); self.assertTrue(r["renewed"]); self.assertEqual(r["lease_epoch"],1); self.assertEqual(r["lease_expires_at_ms"],101500); self.release(a,t,box)

    def test_p12_05_non_owner_cannot_renew(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-05"); b=self.harness("b-p12-05"); r=b.client().renew(bid,1); self.assertFalse(r["renewed"]); self.assertEqual(r["reason"],"TRUSTED_LEASE_RENEW_STALE_OWNER"); self.release(a,t,box)

    def test_p12_06_untrusted_time_claim_cannot_force_expiry(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-06"); b=self.harness("b-p12-06"); self.set_clock(100100); r=b.client().renew(bid,1,claimed_now_ms=999999999); self.assertFalse(r["renewed"]); x=self.execute(b,auth,self.a,e,"p12-06"); self.assertEqual(x["reason"],"TRUSTED_LEASE_LIVE_OWNER_UNEXPIRED"); self.release(a,t,box)

    def test_p12_07_exact_expiry_boundary_is_deterministic(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-07"); b=self.harness("b-p12-07"); self.set_clock(100999); pre=self.execute(b,auth,self.a,e,"p12-07"); self.assertEqual(pre["reason"],"TRUSTED_LEASE_LIVE_OWNER_UNEXPIRED"); self.set_clock(101000); at=self.leases.resolve_for_gateway(bid,gateway_instance_id=b.info["gateway_instance_id"],expected_bindings=self.expected(auth)); self.assertTrue(at["resolved"]); self.assertEqual(at["disposition"],"TRUSTED_EXPIRY_TAKEOVER"); self.assertEqual(at["lease_epoch"],2); a.stop(); t.join(timeout=2)

    def test_p12_08_postexpiry_takeover_advances_epoch_and_expiry(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-08"); b=self.harness("b-p12-08"); self.set_clock(101000); r=self.leases.resolve_for_gateway(bid,gateway_instance_id=b.info["gateway_instance_id"],expected_bindings=self.expected(auth)); self.assertTrue(r["resolved"]); self.assertEqual(r["lease_epoch"],2); self.assertEqual(r["lease_expires_at_ms"],102000); a.stop(); t.join(timeout=2)

    def test_p12_09_old_owner_cannot_finalize_after_takeover(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-09"); old=a.info["gateway_instance_id"]; b=self.harness("b-p12-09"); self.set_clock(101000); self.leases.resolve_for_gateway(bid,gateway_instance_id=b.info["gateway_instance_id"],expected_bindings=self.expected(auth)); r=self.leases.finalize_both(bid,gateway_instance_id=old,lease_epoch=1,authoritative_result_digest="stale"); self.assertFalse(r["finalized"]); self.assertEqual(r["reason"],"TRUSTED_LEASE_STALE_OWNER"); a.stop(); t.join(timeout=2)

    def test_p12_10_old_owner_cannot_renew_after_takeover(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-10"); old=a.info["gateway_instance_id"]; b=self.harness("b-p12-10"); self.set_clock(101000); self.leases.resolve_for_gateway(bid,gateway_instance_id=b.info["gateway_instance_id"],expected_bindings=self.expected(auth)); r=self.leases.renew(bid,gateway_instance_id=old,lease_epoch=1); self.assertFalse(r["renewed"]); self.assertEqual(r["reason"],"TRUSTED_LEASE_RENEW_STALE_OWNER"); a.stop(); t.join(timeout=2)

    def test_p12_11_changed_candidate_cannot_use_expired_takeover(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-11"); b=self.harness("b-p12-11"); self.set_clock(101000); eb=self.effect_for(self.b); r=self.execute(b,auth,self.b,eb,"p12-11"); self.assertFalse(r["authorized"]); self.assertIn("semantic_payload_digest",r["reason"]); self.assertEqual(self.leases.inspect(bid)["lease_epoch"],1); a.stop(); t.join(timeout=2)

    def test_p12_12_changed_effect_or_idempotency_cannot_use_takeover(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-12"); b=self.harness("b-p12-12"); self.set_clock(101000); mutated=copy.deepcopy(e); mutated["provenance_trust_classes"]=["REMOTE_MODEL_PROPOSAL","UNTRUSTED_TOOL_CONTENT"]; r1=self.execute(b,auth,self.a,mutated,"p12-12"); self.assertFalse(r1["authorized"]); r2=self.execute(b,auth,self.a,e,"p12-12-other"); self.assertFalse(r2["authorized"]); self.assertEqual(self.leases.inspect(bid)["lease_epoch"],1); a.stop(); t.join(timeout=2)

    def test_p12_13_two_live_gateways_racing_at_expiry_yield_one_owner(self):
        auth,e,bid,a,t,box,s=self.hold_owner("p12-13"); b=self.harness("b-p12-13"); c=self.harness("c-p12-13"); self.set_clock(101000); outcomes=[]; lock=threading.Lock()
        def claim(h):
            r=self.leases.resolve_for_gateway(bid,gateway_instance_id=h.info["gateway_instance_id"],expected_bindings=self.expected(auth));
            with lock: outcomes.append(r)
        tb=threading.Thread(target=claim,args=(b,)); tc=threading.Thread(target=claim,args=(c,)); tb.start(); tc.start(); tb.join(); tc.join(); winners=[r for r in outcomes if r.get("resolved")]; self.assertEqual(len(winners),1); self.assertEqual(winners[0]["lease_epoch"],2); self.assertEqual(self.leases.inspect(bid)["lease_epoch"],2); a.stop(); t.join(timeout=2)

    def test_p12_14_posteffect_crash_reconciles_without_duplicate(self):
        auth,e=self.issue(self.a,key="p12-14"); a=self.harness("a-p12-14"); unknown=self.execute(a,auth,self.a,e,"p12-14",fault="CRASH_AFTER_GATEWAY_BEFORE_FINALIZE"); self.assertFalse(unknown["transport_complete"]); bid=self.bound_id(auth); self.assertEqual(read_gateway_effect_count(self.effects_db),1); self.set_clock(101000); b=self.harness("b-p12-14"); r=self.execute(b,auth,self.a,e,"p12-14"); self.assertTrue(r["authorized"]); self.assertEqual(read_gateway_effect_count(self.effects_db),1); self.assertEqual(self.leases.inspect(bid)["state"],"CONSUMED")

    def test_p12_15_consumed_permit_cannot_revive_after_expiry(self):
        auth,e=self.issue(self.a,key="p12-15"); a=self.harness("a-p12-15"); first=self.execute(a,auth,self.a,e,"p12-15"); self.assertTrue(first["authorized"]); self.set_clock(999999); b=self.harness("b-p12-15"); second=self.execute(b,auth,self.a,e,"p12-15"); self.assertFalse(second["authorized"]); self.assertEqual(second["reason"],"SEMANTIC_BOUND_PERMIT_CONSUMED"); self.assertEqual(read_gateway_effect_count(self.effects_db),1)

    def test_p12_16_fresh_clean_permit_remains_live(self):
        auth,e=self.issue(self.a,key="p12-16"); a=self.harness("a-p12-16"); r=self.execute(a,auth,self.a,e,"p12-16"); self.assertTrue(r["authorized"]); self.assertEqual(r["decision"],"EXECUTED"); self.assertEqual(read_gateway_effect_count(self.effects_db),1)


if __name__ == "__main__": unittest.main()
