import importlib, sys, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
mod=importlib.import_module("r8_v15_r1_stable_scope_value_validator")

class Slice20Successor1PatternRepair(unittest.TestCase):
    def test_r20_01_leading_ecma_line_terminators_reject(self):
        for bad in ("\nvalue","\rvalue","\u2028value","\u2029value"):
            with self.subTest(bad=repr(bad)):
                with self.assertRaises(mod.StableScopeValueError) as cm:
                    mod.validate_stable_scope_value(bad)
                self.assertEqual(cm.exception.code,"STABLE_SCOPE_PATTERN_INVALID")

    def test_r20_02_later_line_terminators_remain_pattern_matches(self):
        for good in ("x\n","x\r","x\u2028","x\u2029","x\ny"):
            with self.subTest(good=repr(good)):
                self.assertTrue(mod.validate_stable_scope_value(good)["locally_valid"])

    def test_r20_03_exact_any_only_is_excluded_by_negative_lookahead(self):
        with self.assertRaises(mod.StableScopeValueError) as cm:
            mod.validate_stable_scope_value("ANY")
        self.assertEqual(cm.exception.code,"STABLE_SCOPE_ANY_FORBIDDEN")
        for good in ("ANY\n","ANY\r","ANY\u2028","ANY\u2029","ANYTHING"):
            with self.subTest(good=repr(good)):
                self.assertTrue(mod.validate_stable_scope_value(good)["locally_valid"])

    def test_r20_04_repair_remains_non_authoritative(self):
        r=mod.validate_stable_scope_value("x")
        self.assertEqual(r["authority_effect"],"NONE")
        for k in ("scope_permission_verified","scope_current","semantic_selected","constitutional_authorized","runtime_qualified","evidence_promotion_authorized","policy_authority_granted","terminal_authority"):
            self.assertFalse(r[k],k)

if __name__=="__main__": unittest.main(verbosity=2)
