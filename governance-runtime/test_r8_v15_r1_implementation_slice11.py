import importlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
BRANCH="implementation/r8-v15-r1-slice11-resolver-policy-local-2026-09-25"

sys.path.insert(0,str(HERE))
slice1=importlib.import_module("r8_v15_r1_frozen_schema_runtime")
try:
    policy=importlib.import_module("r8_v15_r1_resolver_policy_validator")
    IMPORT_ERROR=None
except Exception as exc:
    policy=None
    IMPORT_ERROR=exc

def require():
    if policy is None:
        raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return policy

def valid():
    return {
      "policy_version":"policy-v1",
      "resolver_algorithm_version":"resolver-alg-v1",
      "resolver_policy_id":"resolver-policy:1",
      "lineage_start_rule_digest":"opaque:lineage",
      "candidate_construction_rule_digest":"opaque:candidate",
      "specificity_rule_digest":"opaque:specificity",
      "lifecycle_error_precedence_digest":"opaque:lifecycle",
      "mapping_traversal_rule_digest":"opaque:mapping",
      "successor_traversal_rule_digest":"opaque:successor",
      "replacement_evaluation_rule_digest":"opaque:replacement",
      "any_validation_rule_digest":"opaque:any",
      "fallback_prohibition_rule_digest":"opaque:fallback",
      "forensic_replay_rule_digest":"opaque:replay",
      "conformance_suite_id":"suite:1",
      "resolver_policy_digest":"opaque:policy-digest",
      "conformance_vector_set_digest":"opaque:vector-set"
    }

class Slice11FrozenAcceptance(unittest.TestCase):
    def test_i11_01_fields_match_schema(self):
        m=require()
        schema=json.loads((SCHEMA_DIR/"runtime-contracts.schema.json").read_text())
        req=schema["$defs"]["ResolverPolicyContract"]["required"]
        self.assertEqual(set(req),set(m.RESOLVER_POLICY_FIELDS)); self.assertEqual(len(req),len(m.RESOLVER_POLICY_FIELDS))
    def test_i11_02_missing_rejects(self):
        m=require(); x=valid(); x.pop("policy_version")
        with self.assertRaises(m.ResolverPolicyError) as cm: m.validate_resolver_policy_contract(x)
        self.assertEqual(cm.exception.code,"RESOLVER_POLICY_FIELD_SET_INVALID")
    def test_i11_03_extra_rejects(self):
        m=require(); x=valid(); x["extra"]="x"
        with self.assertRaises(m.ResolverPolicyError) as cm: m.validate_resolver_policy_contract(x)
        self.assertEqual(cm.exception.code,"RESOLVER_POLICY_FIELD_SET_INVALID")
    def test_i11_04_non_string_rejects(self):
        m=require(); x=valid(); x["policy_version"]=1
        with self.assertRaises(m.ResolverPolicyError) as cm: m.validate_resolver_policy_contract(x)
        self.assertEqual(cm.exception.code,"RESOLVER_POLICY_STRING_INVALID")
    def test_i11_05_empty_rejects(self):
        m=require(); x=valid(); x["resolver_policy_digest"]=""
        with self.assertRaises(m.ResolverPolicyError) as cm: m.validate_resolver_policy_contract(x)
        self.assertEqual(cm.exception.code,"RESOLVER_POLICY_STRING_INVALID")
    def test_i11_06_non_nfc_rejects(self):
        m=require(); x=valid(); x["resolver_algorithm_version"]="e\u0301"
        with self.assertRaises(m.ResolverPolicyError) as cm: m.validate_resolver_policy_contract(x)
        self.assertEqual(cm.exception.code,"RESOLVER_POLICY_GCP_STRING_INVALID")
    def test_i11_07_noncharacter_rejects(self):
        m=require(); x=valid(); x["specificity_rule_digest"]="\ufdd0"
        with self.assertRaises(m.ResolverPolicyError) as cm: m.validate_resolver_policy_contract(x)
        self.assertEqual(cm.exception.code,"RESOLVER_POLICY_GCP_STRING_INVALID")
    def test_i11_08_opaque_non_sha_digests_pass(self):
        m=require(); x=valid(); x["resolver_policy_digest"]="not-a-sha"
        self.assertTrue(m.validate_resolver_policy_contract(x)["locally_valid"])
    def test_i11_09_policy_version_opaque(self):
        m=require(); x=valid(); x["policy_version"]="opaque version id"
        self.assertTrue(m.validate_resolver_policy_contract(x)["locally_valid"])
    def test_i11_10_algorithm_version_opaque(self):
        m=require(); x=valid(); x["resolver_algorithm_version"]="opaque resolver alg"
        self.assertTrue(m.validate_resolver_policy_contract(x)["locally_valid"])
    def test_i11_11_suite_id_opaque(self):
        m=require(); x=valid(); x["conformance_suite_id"]="opaque suite"
        self.assertTrue(m.validate_resolver_policy_contract(x)["locally_valid"])
    def test_i11_12_policy_digest_unverified(self):
        r=require().validate_resolver_policy_contract(valid())
        self.assertFalse(r["resolver_policy_digest_verified"])
    def test_i11_13_vector_set_digest_unverified(self):
        r=require().validate_resolver_policy_contract(valid())
        self.assertFalse(r["conformance_vector_set_digest_verified"])
    def test_i11_14_non_authority_metadata(self):
        r=require().validate_resolver_policy_contract(valid())
        self.assertEqual(r["authority_effect"],"NONE")
        for k in ("policy_current","policy_active","policy_authorized","resolver_authorized","runtime_qualified","release_authorized","deployment_authorized","production_authorized","policy_authority_granted","terminal_authority"):
            self.assertFalse(r[k],k)
    def test_i11_15_failure_does_not_poison(self):
        m=require(); bad=valid(); bad["policy_version"]=""
        with self.assertRaises(m.ResolverPolicyError): m.validate_resolver_policy_contract(bad)
        self.assertEqual(m.validate_resolver_policy_contract(valid()),m.validate_resolver_policy_contract(valid()))
    def test_i11_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--",
          "schemas/governance-r8/v15-r1",
          "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
          "governance-runtime/r8_v15_r1_state_roots.py",
          "governance-runtime/r8_v15_r1_stc_validator.py",
          "governance-runtime/r8_v15_r1_preseal_validator.py",
          "governance-runtime/r8_v15_r1_timeproof_validator.py",
          "governance-runtime/r8_v15_r1_seal_validator.py",
          "governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True)
        self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice11.yml").read_text()
        for p in (BRANCH,"governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE11-PREREGISTRATION.md","governance-runtime/r8_v15_r1_resolver_policy_validator.py","governance-runtime/test_r8_v15_r1_implementation_slice11.py","governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE11-MARKER.json",".github/workflows/r8-v15-r1-implementation-slice11.yml","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/test_r8_v15_r1_implementation_slice7.py"):
            self.assertIn(p,wf)

if __name__=="__main__": unittest.main(verbosity=2)
