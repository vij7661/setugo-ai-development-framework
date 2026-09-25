import importlib, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
mod=importlib.import_module("r8_v15_r1_canonical_scope_tuple_validator")

FIELDS=("trust_domain_id","constitution_id","root_namespace","tenant_id","organization_id","project_id","experiment_or_release_id","object_class","action_class")
def valid(v="scope:1"): return {k:v for k in FIELDS}

class Slice22Successor1PatternRepair(unittest.TestCase):
    def test_r22_01_every_field_rejects_leading_ecma_line_terminators(self):
        for field in FIELDS:
            for bad in ("\nvalue","\rvalue","\u2028value","\u2029value"):
                x=valid(); x[field]=bad
                with self.subTest(field=field,bad=repr(bad)):
                    with self.assertRaises(mod.CanonicalScopeTupleError) as cm:
                        mod.validate_canonical_scope_tuple(x)
                    self.assertEqual(cm.exception.code,"CANONICAL_SCOPE_COMPONENT_PATTERN_INVALID")

    def test_r22_02_later_line_terminators_remain_component_pattern_matches(self):
        for good in ("x\n","x\r","x\u2028","x\u2029","x\ny"):
            x=valid(); x["tenant_id"]=good
            with self.subTest(good=repr(good)):
                self.assertTrue(mod.validate_canonical_scope_tuple(x)["locally_valid"])

    def test_r22_03_any_sentinel_and_any_plus_terminator_follow_frozen_scopecomponent(self):
        self.assertTrue(mod.validate_canonical_scope_tuple(valid("ANY"))["locally_valid"])
        for good in ("ANY\n","ANY\r","ANY\u2028","ANY\u2029","ANYTHING"):
            x=valid(); x["tenant_id"]=good
            with self.subTest(good=repr(good)):
                self.assertTrue(mod.validate_canonical_scope_tuple(x)["locally_valid"])

    def test_r22_04_repair_remains_non_authoritative(self):
        r=mod.validate_canonical_scope_tuple(valid())
        self.assertEqual(r["authority_effect"],"NONE")
        for k in ("any_permission_verified","scope_current","scope_match_verified","scope_relation_verified","semantic_selected","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","policy_authority_granted","terminal_authority"):
            self.assertFalse(r[k],k)

if __name__=="__main__": unittest.main(verbosity=2)
