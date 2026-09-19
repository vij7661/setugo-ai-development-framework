#!/usr/bin/env python3
"""Offline structured-proof mutation suite; no runtime interaction."""
import copy, json
from v24_v6_rq1_rq16_harness import evaluate_arm
from test_v24_v6_rq1_rq16_harness import good

def main():
    mutations=[]
    specs=[
      ("wrong_target",lambda e:e.update(target_record_id="other")),
      ("wrong_path",lambda e:e["fault_proof"].update(target_path="/run/v24-v6-authority/private/records/other.record")),
      ("wrong_syscall",lambda e:e["fault_proof"].update(target_syscall="rename")),
      ("wrong_errno",lambda e:e["fault_proof"].update(observed_errno="EROFS")),
      ("missing_activation",lambda e:e["fault_proof"].update(activation_evidence={})),
      ("missing_operation",lambda e:e["fault_proof"].update(operation_evidence={})),
      ("observer_missing",lambda e:e["observations"].pop("restored")),
      ("cleanup_unverified",lambda e:e["cleanup_proof"].update(independently_verified=False)),
      ("duplicate_consume",lambda e:e["lifecycle"].update(duplicate_authoritative_consume=True)),
      ("both_directories",lambda e:e["lifecycle"].update(target_in_consumed=True)),
      ("rq17_split",lambda e:e.update(rq17_contamination=True)),
      ("authoritative_success",lambda e:e.update(authoritative_success=True)),
      ("invalid_transition",lambda e:e.update(invalid_transition=True)),
    ]
    for name,mut in specs:
        e=copy.deepcopy(good()); mut(e); actual,reasons=evaluate_arm("ENOSPC",e)
        mutations.append({"mutation_id":name,"case":"ENOSPC","path":name,"expected_result":"REJECT","actual_result":actual,"reasons":reasons,"rejected":actual!="PASS"})
    out={"total":len(mutations),"rejected":sum(x["rejected"] for x in mutations),"survived":sum(not x["rejected"] for x in mutations),"all_rejected":all(x["rejected"] for x in mutations),"mutations":mutations,"RQ16_EXECUTED":False}
    print(json.dumps(out,indent=2,sort_keys=True)); return 0 if out["all_rejected"] else 2
if __name__=="__main__": raise SystemExit(main())
