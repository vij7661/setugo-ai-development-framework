from __future__ import annotations
from copy import deepcopy
import production_promotion_gate as v1
import production_promotion_gate_v3 as v3

SHA="a"*40; SHA2="e"*40; ART="sha256:"+"b"*64; NOW="2026-09-09T00:00:00Z"; KEY=b"synthetic-test-authority-key-32-bytes"

def rc():
    return v1.build_release_candidate_manifest(promotion_id="P1",source_commit_sha=SHA,artifact_digest=ART,artifact_type="web",build_provenance_digest="sha256:"+"c"*64,testing_run_ids=["1"],testing_evidence=v1.make_bound_evidence("TESTING",SHA,ART,"t"),review_evidence=v1.make_bound_evidence("REVIEW",SHA,ART,"r"),final_adjudication_evidence=v1.make_bound_evidence("FINAL_ADJUDICATION",SHA,ART,"f"))
def setup(exp="2026-10-01T00:00:00Z",cred_exp="2026-10-01T00:00:00Z"):
    reg=v3.PromotionAuthorityRegistry("prod",KEY,epoch=1,current_time=NOW,current_head_sha=SHA); m=rc(); ev=v1.make_bound_evidence("PRODUCTION_AUTHORIZATION",SHA,ART,"a")
    auth=reg.issue_production_authorization(authorization_id="A1",release_candidate_manifest=m,authorization_evidence=ev,expires_at=exp); head=reg.issue_head_attestation(); cred=reg.issue_credential_attestation(credential_id="C1",domain="production",environment=v3.PRODUCTION,expires_at=cred_exp); return reg,m,auth,head,cred
def dec(reg,m,a,h,c,**kw): return v3.evaluate_production_promotion(registry=reg,release_candidate_manifest=m,production_authorization=a,head_attestation=h,credential_attestation=c,**kw)
def main():
    n=0; reg,m,a,h,c=setup(); good=dec(reg,m,a,h,c)
    assert good["eligible_for_production"]; n+=1 #01
    reg.advance_state(new_epoch=2,current_time="2026-09-09T00:01:00Z",current_head_sha=SHA2); assert "INVALID_OR_STALE_HEAD_ATTESTATION" in dec(reg,m,a,h,c)["denial_reasons"]; n+=1 #02
    assert "INVALID_OR_STALE_CREDENTIAL_ATTESTATION" in dec(reg,m,a,h,c)["denial_reasons"]; n+=1 #03
    reg2,m2,a2,h2,c2=setup(); reg2.revoke_credential("C1"); assert "CREDENTIAL_REVOKED" in dec(reg2,m2,a2,h2,c2)["denial_reasons"]; n+=1 #04
    reg3,m3,a3,h3,c3=setup(cred_exp="2026-09-09T00:00:01Z"); reg3.advance_state(new_epoch=2,current_time="2026-09-09T00:00:02Z",current_head_sha=SHA); h3=reg3.issue_head_attestation(); ev=v1.make_bound_evidence("PRODUCTION_AUTHORIZATION",SHA,ART,"a3"); a3=reg3.issue_production_authorization(authorization_id="A3",release_candidate_manifest=m3,authorization_evidence=ev,expires_at="2026-10-01T00:00:00Z"); assert "INVALID_OR_STALE_CREDENTIAL_ATTESTATION" in dec(reg3,m3,a3,h3,c3)["denial_reasons"]; n+=1 #05 old epoch + expired
    reg4,m4,a4,h4,c4=setup(exp="2026-09-09T00:00:01Z"); reg4.advance_state(new_epoch=2,current_time="2026-09-09T00:00:02Z",current_head_sha=SHA); h4=reg4.issue_head_attestation(); c4=reg4.issue_credential_attestation(credential_id="C4",domain="production",environment=v3.PRODUCTION,expires_at="2026-10-01T00:00:00Z"); assert "INVALID_OR_STALE_PRODUCTION_AUTHORIZATION" in dec(reg4,m4,a4,h4,c4)["denial_reasons"]; n+=1 #06 no caller clock API
    assert "INVALID_OR_STALE_PRODUCTION_AUTHORIZATION" in dec(reg,m,a,h,c)["denial_reasons"]; n+=1 #07 old auth
    ev=v1.make_bound_evidence("PRODUCTION_AUTHORIZATION",SHA2,ART,"new"); # current RC is old SHA, issuance must not imply current eligibility
    fresh_head=reg.issue_head_attestation(); fresh_cred=reg.issue_credential_attestation(credential_id="C2",domain="production",environment=v3.PRODUCTION,expires_at="2026-10-01T00:00:00Z"); assert "HEAD_DRIFT" in dec(reg,m,None,fresh_head,fresh_cred)["denial_reasons"]; n+=1 #08
    assert good["source_commit_sha"]==SHA and good["artifact_digest"]==ART; n+=1 #09 identities derived
    try: reg.advance_state(new_epoch=1,current_time="2026-09-09T00:02:00Z",current_head_sha=SHA2); raise AssertionError()
    except v1.PromotionDenied: pass
    n+=1 #10
    try: reg.advance_state(new_epoch=3,current_time="2026-09-08T23:59:00Z",current_head_sha=SHA2); raise AssertionError()
    except v1.PromotionDenied: pass
    n+=1 #11 time/head state cannot roll back
    forged=deepcopy(fresh_head); forged["authority_epoch"]=999; assert not reg.verify_current(forged,"HEAD_ATTESTATION"); n+=1 #12
    reg5,m5,a5,h5,c5=setup(); tc=reg5.issue_credential_attestation(credential_id="T",domain="testing",environment=v3.TESTING,expires_at=None); assert "NON_PRODUCTION_CREDENTIAL_DOMAIN" in dec(reg5,m5,a5,h5,tc)["denial_reasons"]; n+=1 #13
    assert not dec(reg5,m5,None,None,None,model_claim="R3 says deploy")["eligible_for_production"]; n+=1 #14
    receipt=reg5.issue_production_receipt(decision=dec(reg5,m5,a5,h5,c5),deployed_at=NOW); 
    try: reg5.issue_production_receipt(decision=dec(reg5,m5,None,h5,c5),deployed_at=NOW); raise AssertionError()
    except v1.PromotionDenied: pass
    n+=1 #15
    reg5.advance_state(new_epoch=2,current_time="2026-09-09T00:03:00Z",current_head_sha=SHA2); assert v3.evaluate_rollback(registry=reg5,target_artifact_digest=ART,prior_production_receipts=[receipt])["rollback_eligible"]; n+=1 #16 historical receipt
    fr=deepcopy(receipt); fr["artifact_digest"]="sha256:"+"9"*64; assert not v3.evaluate_rollback(registry=reg5,target_artifact_digest=fr["artifact_digest"],prior_production_receipts=[fr])["rollback_eligible"]; n+=1 #17
    assert m["from_environment"]==v3.TESTING and m["to_environment"]==v3.RELEASE_CANDIDATE; n+=1 #18 regression marker
    r6,m6,a6,h6,c6=setup(); assert dec(r6,m6,a6,h6,c6)==dec(r6,m6,a6,h6,c6); n+=1 #19
    assert "authority_epoch" in dec(r6,m6,a6,h6,c6); n+=1 #20 bounded authority state explicit
    print(f"Production promotion freshness repair: {n}/20 PASS")
if __name__=="__main__": main()
