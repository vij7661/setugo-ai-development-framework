import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    admissibility_registry, GovernanceAuthoritySnapshot, RequiredEvidenceContract,
    RequiredInteractionContract, MaterializationResult,
)
from run_exp_m_deterministic import run_phases  # noqa: E402
from run_exp_m_mutations import run as run_mutations  # noqa: E402


class ExpMPhaseTests(unittest.TestCase):
    def test_all_deterministic_phases_a_to_t_pass(self):
        result = run_phases()
        self.assertEqual(set(result["phases"]), set("ABCDEFGHIJKLMNOPQRST"))
        self.assertTrue(result["all_phases_pass"])
        self.assertTrue(all(v["status"] == "PASS" for v in result["phases"].values()))
        self.assertGreater(result["phases"]["G"]["mutation_total"], 0)

    def test_predicate_registry_exact_closure(self):
        result = run_mutations(); registry = admissibility_registry()
        killed = {m["target"] for m in result["mutations"] if m["family"] == "validator_logic" and m["killed"]}
        self.assertEqual(set(registry.predicate_ids), set(registry.logic_mutation_ids))
        self.assertEqual(set(registry.predicate_ids), killed)
        self.assertEqual(result["surviving_mutations"], 0)
        self.assertTrue(all(m.get("negative_control") in (None, "REJECT") for m in result["mutations"]))

    def test_structured_admissibility_fixture_is_positive(self):
        reg = admissibility_registry()
        state = {
            "review_request": {"current": True, "request_id": "r"},
            "authority_snapshot": GovernanceAuthoritySnapshot("s", "1", "h", True),
            "evidence_contract": RequiredEvidenceContract("e", "s", ("a",)),
            "interaction_contract": RequiredInteractionContract("i", "s", (("a",),)),
            "materialization": MaterializationResult(True, {"a": b"a"}, "rep", "src", "raw-v1"),
            "representation": {"governed": True, "transform_id": "raw-v1"},
            "egress": {"authorized": True, "version": "1"},
            "capability_current": True, "accessibility_policy": {"satisfied": True}, "accessibility": {"satisfied": True, "proven": True},
            "context_isolation": {"satisfied": True}, "hidden_state_policy": {"satisfied": True},
            "context_state": {"clean": True, "sentinel_passed": True}, "fence": {"current": True, "version": "1"},
            "semantic_context": {"qualified": True}, "wire": {"valid": True}, "delivery": {"complete": True},
            "witness": {"current": True}, "retrieval": {"complete": True}, "prompt_isolation": {"current": True},
            "semantic_coverage": {"complete": True}, "reviewer": {"trusted": True},
            "disposition": "PASS", "disposition_promotable": True,
        }
        self.assertTrue(__import__("exp_m_deterministic").evaluate_admissibility(state, reg).admissible)


if __name__ == "__main__":
    unittest.main(verbosity=2)
