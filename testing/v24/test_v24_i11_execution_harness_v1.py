"""Construction tests only; no WDPC scientific case is executed."""
import unittest
from v24_i11_execution_harness_v1 import (
    CASE_SPECS, EXACT_FIXTURE_BRANCHES, ExecutionScheduler, ResultLedger,
    ScientificCaseResult, assert_execution_frontier, validate_fixture_branch,
    validate_profile_negative,
)

D="a"*64

GOOD={
"O-AGG":{"authority_transition_state":"DENIED","effect_before":0,"effect_after":0},
"O-CONTROL":{"downstream_guarded_decision_before":0,"downstream_guarded_decision_after":0,"material_effect_before":0,"material_effect_after":0},
"O-ENDPOINT":{"table_active":False,"dispatch_before":0,"dispatch_after":0,"material_effect_before":0,"material_effect_after":0},
"O-NORMATIVE":{"authority_derived_from_target":False,"decision_dispatch_before":0,"decision_dispatch_after":0,"material_effect_before":0,"material_effect_after":0},
"O-PROOF":{"proof_state":"FAIL","consuming_authority_decision_before":0,"consuming_authority_decision_after":0,"material_effect_before":0,"material_effect_after":0},
"O-UNIVERSE":{"unqualified_path_reached_sink":False,"sink_effect_before":0,"sink_effect_after":0},
"O-MIGRATION":{"predecessor_read_accepted":False,"successor_activated":False,"material_effect_before":0,"material_effect_after":0},
"O-APPLICATION":{"valid_applied_state":False,"sink_effect_before":0,"sink_effect_after":0},
"O-APPLY":{"worker_invocation_before":0,"worker_invocation_after":0,"application_record_count_before":0,"application_record_count_after":0,"material_effect_before":0,"material_effect_after":0},
"O-HISTORY":{"historical_decision_digest_before":D,"historical_decision_digest_after":D,"historical_result_before":"IE","historical_result_after":"IE","retroactively_upgraded":False,"material_effect_before":0,"material_effect_after":0},
"O-BOOTSTRAP":{"completeness_current_record_count_before":1,"completeness_current_record_count_after":1,"generation_activated":False,"material_effect_before":0,"material_effect_after":0},
"O-PERIMETER":{"closed_world_authority_path_qualified":False,"material_write_count_before":0,"material_write_count_after":0,"material_effect_before":0,"material_effect_after":0},
}
BAD={
"O-AGG":{**GOOD["O-AGG"],"authority_transition_state":"SUCCESS"},
"O-CONTROL":{**GOOD["O-CONTROL"],"downstream_guarded_decision_after":1},
"O-ENDPOINT":{**GOOD["O-ENDPOINT"],"table_active":True},
"O-NORMATIVE":{**GOOD["O-NORMATIVE"],"authority_derived_from_target":True},
"O-PROOF":{**GOOD["O-PROOF"],"proof_state":"PASS"},
"O-UNIVERSE":{**GOOD["O-UNIVERSE"],"unqualified_path_reached_sink":True},
"O-MIGRATION":{**GOOD["O-MIGRATION"],"predecessor_read_accepted":True},
"O-APPLICATION":{**GOOD["O-APPLICATION"],"valid_applied_state":True},
"O-APPLY":{**GOOD["O-APPLY"],"worker_invocation_after":1},
"O-HISTORY":{**GOOD["O-HISTORY"],"historical_result_after":"VALID"},
"O-BOOTSTRAP":{**GOOD["O-BOOTSTRAP"],"generation_activated":True},
"O-PERIMETER":{**GOOD["O-PERIMETER"],"closed_world_authority_path_qualified":True},
}

class ExecutionHarnessConstructionTests(unittest.TestCase):
    def test_76_specs_and_blocked_cases(self):
        self.assertEqual(set(CASE_SPECS),{f"WDPC-{i}" for i in range(431,507)})
        self.assertEqual(CASE_SPECS["WDPC-469"]["status"],"BLOCKED_BY_I1_SEMANTIC_QUALIFICATION")
        self.assertEqual(CASE_SPECS["WDPC-495"]["status"],"BLOCKED_BY_I1_SEMANTIC_QUALIFICATION")

    def test_all_negative_profiles_are_enforced(self):
        for cid,s in CASE_SPECS.items():
            if s["case_type"]=="NEG":
                self.assertIn(s["profile_id"],GOOD,cid)
                self.assertEqual(validate_profile_negative(s["profile_id"],GOOD[s["profile_id"]]),[],cid)

    def test_each_profile_rejects_a_load_bearing_violation(self):
        for profile,o in BAD.items():
            self.assertTrue(validate_profile_negative(profile,o),profile)

    def test_exact_fixture_branches_fail_closed(self):
        for cid,branch in EXACT_FIXTURE_BRANCHES.items():
            self.assertEqual(validate_fixture_branch(cid,branch),[])
            self.assertTrue(validate_fixture_branch(cid,"WRONG"))

    def test_missing_profile_fields_are_harness_failure_evidence(self):
        self.assertTrue(validate_profile_negative("O-AGG",{}))

    def test_evidence_lock_collision(self):
        s=ExecutionScheduler()
        s.acquire("WDPC-449","w1")
        with self.assertRaisesRegex(ValueError,"EVIDENCE_LOCK_CONFLICT"):
            s.acquire("WDPC-477","w2")
        s.release("WDPC-449","PASS")

    def test_external_snapshot_identity_required(self):
        with self.assertRaisesRegex(ValueError,"EXTERNAL_EVIDENCE_SNAPSHOT_ID_REQUIRED"):
            ExecutionScheduler().acquire("WDPC-449")

    def test_positive_waits_for_same_profile_negatives(self):
        with self.assertRaisesRegex(ValueError,"POSITIVE_BEFORE_NEGATIVE_RESOLUTION"):
            ExecutionScheduler().acquire("WDPC-461")

    def test_result_ledger_is_append_only(self):
        l=ResultLedger()
        r1=ScientificCaseResult("WDPC-431","WDPC-431:"+"1"*16,"FAIL_CODE_DEFECT","O-AGG",D,None)
        d1=l.append(r1)
        r2=ScientificCaseResult("WDPC-432","WDPC-432:"+"2"*16,"PASS","O-CONTROL",D,d1)
        l.append(r2)
        with self.assertRaisesRegex(ValueError,"DUPLICATE_RUN_ID"): l.append(r2)

    def test_frontier_is_not_execution(self):
        s=assert_execution_frontier()
        self.assertEqual(s["execution_harness_profile_invariant_gate"],"CONSTRUCTION_READY")
        self.assertEqual(s["wdpc_execution_status"],"NOT_EXECUTED")

if __name__=="__main__":
    unittest.main()
