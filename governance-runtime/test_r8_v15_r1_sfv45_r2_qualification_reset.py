import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "schemas/governance-r8/v15-r1/schema-freeze-traceability.json"
SOURCE_MAP = ROOT / "schemas/governance-r8/v15-r1/schema-provenance-source-map.json"
SPM_CANDIDATE = ROOT / "schemas/governance-r8/v15-r1/schema-provenance-manifest-candidate.json"


class R8V15R1QualificationResetInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trace = json.loads(TRACE.read_text(encoding="utf-8"))
        cls.source_map = json.loads(SOURCE_MAP.read_text(encoding="utf-8"))

    def test_repaired_candidate_reopens_exact_byte_qualification_gates(self):
        self.assertIn("SCHEMA_FREEZE_CANDIDATE", self.trace["status"])
        self.assertIn("NON_AUTHORITATIVE", self.trace["status"])
        blockers = set(self.trace["final_freeze_blockers"])
        self.assertTrue({"SFV-35", "SFV-36", "SFV-44", "SFV-45"}.issubset(blockers))

        by_id = {x["rule_id"]: x for x in self.trace["freeze_process_mappings"]}
        self.assertIn("REGENERATION_REQUIRED", by_id["SFG-001"]["status"])
        self.assertTrue(
            "REBIND_REQUIRED" in by_id["SFG-002"]["status"]
            or "REGENERATION_REQUIRED" in by_id["SFG-002"]["status"]
        )
        self.assertIn("REQUALIFICATION_REQUIRED", by_id["SFG-003"]["status"])
        self.assertEqual(
            by_id["SFG-007"]["status"],
            "BLOCKED_PENDING_REPAIRED_EXACT_CANDIDATE_REVIEW",
        )

    def test_predecessor_successor_output_evidence_does_not_transfer(self):
        refs = self.source_map["named_source_refs"]
        self.assertNotIn("SRC-SPG-V2R1-EXTENSION", refs)
        self.assertNotIn("SRC-SPG-V2R1-VERIFY", refs)
        routes = {x["match_prefix"]: x for x in self.source_map["source_ref_routes"]}
        self.assertNotIn("SPG-QUALIFICATION-V2-R1-2026-09-24", routes)

    def test_base_generator_identity_runtime_qualification_sources_remain(self):
        refs = self.source_map["named_source_refs"]
        self.assertIn("SRC-SPG-ENROLLMENT", refs)
        self.assertIn("SRC-SPG-STAGEB-VERIFY", refs)
        routes = {x["match_prefix"]: x for x in self.source_map["source_ref_routes"]}
        self.assertEqual(
            routes["SPG-QUALIFICATION-2026-09-24"]["source_ref_ids"],
            ["SRC-SPG-ENROLLMENT", "SRC-SPG-STAGEB-VERIFY"],
        )

    def test_traceability_provenance_contains_no_successor_specific_spg_pass(self):
        pps = self.source_map["artifact_sources"]["schema-freeze-traceability.json"]["pointer_prefix_sources"]
        flattened = {item for values in pps.values() for item in values}
        self.assertNotIn("SPG-QUALIFICATION-V2-R1-2026-09-24", flattened)

    def test_predecessor_materialized_spm_is_absent_before_fresh_generation(self):
        self.assertFalse(
            SPM_CANDIDATE.exists(),
            "predecessor-bound materialized SPM must not transfer into a fresh successor qualification run",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
