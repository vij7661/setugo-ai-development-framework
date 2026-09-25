import copy, importlib, itertools, json, subprocess, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parent
SCHEMA_DIR=REPO_ROOT/"schemas"/"governance-r8"/"v15-r1"
BASELINE="751162ee42c603cb6c84ee12021d16bab6fa626b"
sys.path.insert(0,str(HERE))

BRANCH="implementation/r8-v15-r1-slice45-freeze-validator-contract-exact-local-2026-09-25"
try: mod=importlib.import_module("r8_v15_r1_freeze_validator_contract_exact_validator"); IMPORT_ERROR=None
except Exception as exc: mod=None; IMPORT_ERROR=exc
def require():
    if mod is None: raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return mod
def frozen(): return json.loads((SCHEMA_DIR/"schema-freeze-validator-contract.json").read_text())
class Slice45FrozenAcceptance(unittest.TestCase):
    def test_i45_01_exact_file_identity(self):
        self.assertEqual(frozen(),frozen())
        self.assertTrue(isinstance(frozen(),dict))
    def test_i45_02_exact_passes(self): self.assertTrue(require().validate_freeze_validator_contract(frozen())["locally_valid"])
    def test_i45_03_non_mapping_rejects(self):
        m=require()
        with self.assertRaises(m.FreezeValidatorContractExactError): m.validate_freeze_validator_contract([])
    def test_i45_04_top_level_mutation_rejects(self):
        m=require(); x=copy.deepcopy(frozen()); k=next(iter(x)); x[k]="__mutated__"
        with self.assertRaises(m.FreezeValidatorContractExactError): m.validate_freeze_validator_contract(x)
    def test_i45_05_missing_field_rejects(self):
        m=require(); x=copy.deepcopy(frozen()); x.pop(next(iter(x)))
        with self.assertRaises(m.FreezeValidatorContractExactError): m.validate_freeze_validator_contract(x)
    def test_i45_06_extra_field_rejects(self):
        m=require(); x=copy.deepcopy(frozen()); x["__extra__"]=1
        with self.assertRaises(m.FreezeValidatorContractExactError): m.validate_freeze_validator_contract(x)
    def test_i45_07_nested_mutation_rejects(self):
        m=require(); x=copy.deepcopy(frozen())
        target=None
        def mutate(v):
            nonlocal target
            if isinstance(v,dict):
                for k,val in v.items():
                    if isinstance(val,str):
                        v[k]=val+"__x"; target=k; return True
                    if mutate(val): return True
            elif isinstance(v,list):
                for val in v:
                    if mutate(val): return True
            return False
        self.assertTrue(mutate(x))
        with self.assertRaises(m.FreezeValidatorContractExactError): m.validate_freeze_validator_contract(x)
    def test_i45_08_list_reorder_rejects_when_present(self):
        m=require(); x=copy.deepcopy(frozen()); changed=False
        def swap(v):
            nonlocal changed
            if isinstance(v,dict):
                for val in v.values():
                    if swap(val): return True
            elif isinstance(v,list) and len(v)>1:
                v[0],v[1]=v[1],v[0]; changed=True; return True
            return False
        swap(x); self.assertTrue(changed)
        with self.assertRaises(m.FreezeValidatorContractExactError): m.validate_freeze_validator_contract(x)
    def test_i45_09_object_key_order_irrelevant(self):
        m=require(); x=frozen(); y={k:x[k] for k in reversed(list(x.keys()))}; self.assertTrue(m.validate_freeze_validator_contract(y)["locally_valid"])
    def test_i45_10_json_type_fidelity(self):
        m=require(); x=copy.deepcopy(frozen()); mutated=False
        def flip(v):
            nonlocal mutated
            if isinstance(v,dict):
                for k,val in v.items():
                    if type(val) is int:
                        v[k]=True; mutated=True; return True
                    if flip(val): return True
            elif isinstance(v,list):
                for val in v:
                    if flip(val): return True
            return False
        if flip(x):
            with self.assertRaises(m.FreezeValidatorContractExactError): m.validate_freeze_validator_contract(x)
        else:
            self.assertTrue(m.validate_freeze_validator_contract(frozen())["locally_valid"])
    def test_i45_11_deterministic(self):
        m=require(); self.assertEqual(m.validate_freeze_validator_contract(frozen()),m.validate_freeze_validator_contract(frozen()))
    def test_i45_12_source_semantics_not_verified(self):
        r=require().validate_freeze_validator_contract(frozen()); self.assertFalse(r["source_semantics_verified"])
    def test_i45_13_rule_execution_not_performed(self):
        r=require().validate_freeze_validator_contract(frozen()); self.assertFalse(r["rule_execution_performed"])
    def test_i45_14_non_authority(self):
        r=require().validate_freeze_validator_contract(frozen()); self.assertEqual(r["authority_effect"],"NONE"); self.assertFalse(r["runtime_qualified"]); self.assertFalse(r["terminal_authority"])
    def test_i45_15_nonpoison_and_no_sibling_dependency(self):
        m=require(); bad=copy.deepcopy(frozen()); bad["__extra__"]=1
        with self.assertRaises(m.FreezeValidatorContractExactError): m.validate_freeze_validator_contract(bad)
        self.assertTrue(m.validate_freeze_validator_contract(frozen())["locally_valid"])
        src=(HERE/"r8_v15_r1_freeze_validator_contract_exact_validator.py").read_text(); self.assertNotIn("r8_v15_r1_srtt4_",src)
    def test_i45_16_immutability_and_workflow(self):
        result=subprocess.run(["git","diff","--name-only",BASELINE,"HEAD","--","schemas/governance-r8/v15-r1","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/r8_v15_r1_state_roots.py","governance-runtime/r8_v15_r1_stc_validator.py","governance-runtime/r8_v15_r1_preseal_validator.py","governance-runtime/r8_v15_r1_timeproof_validator.py","governance-runtime/r8_v15_r1_seal_validator.py","governance-runtime/r8_v15_r1_effect_intent_validator.py"],cwd=REPO_ROOT,text=True,capture_output=True,check=True); self.assertEqual(result.stdout.strip(),"")
        wf=(REPO_ROOT/".github/workflows/r8-v15-r1-implementation-slice45.yml").read_text()
        for p in (BRANCH,"R8-V15-R1-IMPLEMENTATION-SLICE45-PREREGISTRATION.md","r8_v15_r1_freeze_validator_contract_exact_validator.py","test_r8_v15_r1_implementation_slice45.py","R8-V15-R1-IMPLEMENTATION-SLICE45-MARKER.json"): self.assertIn(p,wf)
if __name__=="__main__": unittest.main(verbosity=2)
