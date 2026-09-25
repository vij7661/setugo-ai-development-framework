import importlib, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
mod=importlib.import_module("r8_v15_r1_scope_component_validator")

class Slice21Successor1PatternRepair(unittest.TestCase):
    def test_r21_01_leading_ecma_line_terminators_reject_stable_branch(self):
        for bad in ("\nvalue","\rvalue","\u2028value","\u2029value"):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(mod.ScopeComponentError) as cm:
                    mod.validate_scope_component(bad)
                self.assertEqual(cm.exception.code,"SCOPE_COMPONENT_PATTERN_INVALID")

    def test_r21_02_later_line_terminators_remain_stable_pattern_matches(self):
        for good in ("x\n","x\r","x\u2028","x\u2029","x\ny"):
            with self.subTest(good=repr(good)):
                r=mod.validate_scope_component(good)
                self.assertTrue(r["locally_valid"])
                self.assertEqual(r["component_kind"],"STABLE")

    def test_r21_03_exact_any_is_sentinel_but_any_plus_terminator_is_stable(self):
        self.assertEqual(mod.validate_scope_component("ANY")["component_kind"],"ANY")
        for good in ("ANY\n","ANY\r","ANY\u2028","ANY\u2029","ANYTHING"):
            with self.subTest(good=repr(good)):
                self.assertEqual(mod.validate_scope_component(good)["component_kind"],"STABLE")

    def test_r21_04_repair_remains_non_authoritative(self):
        r=mod.validate_scope_component("x")
        self.assertEqual(r["authority_effect"],"NONE")
        for k in ("any_permission_verified","scope_current","semantic_selected","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","policy_authority_granted","terminal_authority"):
            self.assertFalse(r[k],k)

if __name__=="__main__": unittest.main(verbosity=2)
