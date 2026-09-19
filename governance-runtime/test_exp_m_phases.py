import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exp_m_deterministic import (  # noqa: E402
    admissibility_registry, GovernanceAuthoritySnapshot, RequiredEvidenceContract,
    RequiredInteractionContract, MaterializationResult, AccessibilityProofRecord,
    WireDeliveryRecord, DeliveryCompletenessResult, WitnessProtocolQualificationRecord,
    RetrievalEvidenceRecord, SemanticCoverageRecord, ReviewerProvenanceRecord,
    RepresentationRecord,
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
            "representation": RepresentationRecord("raw-v1", "1", "transform", "registry-exp-m-r1", "src", "rep", "params", "coverage"),
            "egress": {"authorized": True, "version": "1"},
            "capability": {"validated": True}, "accessibility_policy": {"satisfied": True, "risk_policy_version": "r1"}, "accessibility": AccessibilityProofRecord("proof", "ch", "fake", "inline", "ctx", True),
            "context_isolation": {"satisfied": True, "transition_class": "LOWER"}, "hidden_state_policy": {"satisfied": True},
            "context_state": {"clean": True, "sentinel_passed": True, "state_hash": "state"}, "fence": {"current": True, "version": "1"},
            "semantic_context": {"qualified": True, "context_hash": "ctx-h"}, "wire": WireDeliveryRecord("a", "r", "w", "s", "s", ("a",)), "delivery": DeliveryCompletenessResult(True),
            "witness": WitnessProtocolQualificationRecord("w", "fake", "inline", 100, True, "prompt", "2099-01-01T00:00:00Z"), "retrieval": RetrievalEvidenceRecord("r", "a", "s", "file", "v", 0, 1, "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", 1, "tool", 1, "ctx", "ctx-h"), "retrieval_bytes": b"a", "prompt_isolation": {"current": True},
            "semantic_coverage": SemanticCoverageRecord("cov", "ctx", True), "reviewer": ReviewerProvenanceRecord("reviewer", "policy", True),
            "disposition": "PASS", "disposition_promotable": True,
        }
        mod = __import__("exp_m_deterministic")
        self.assertTrue(mod.evaluate_admissibility(mod.bundle_from_state(state), mod.context_from_state(state), reg).admissible)


if __name__ == "__main__":
    unittest.main(verbosity=2)
