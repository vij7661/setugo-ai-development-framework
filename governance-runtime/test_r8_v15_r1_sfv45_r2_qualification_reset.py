import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "schemas/governance-r8/v15-r1/schema-freeze-traceability.json"
SOURCE_MAP = ROOT / "schemas/governance-r8/v15-r1/schema-provenance-source-map.json"


class R8V15R1SFV45R2QualificationResetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trace = json.loads(TRACE.read_text(encoding="utf-8"))
        cls.source_map = json.loads(SOURCE_MAP.read_text(encoding="utf-8"))

    def test_repaired_candidate_reopens_exact_byte_qualification_gates(self):
        self.assertEqual(
            self.trace["status"],
            "SCHEMA_FREEZE_CANDIDATE_V2_NON_AUTHORITATIVE",
        )
        self.assertEqual(
            self.trace["final_freeze_blockers"],
            ["SFV-35", "SFV-36", "SFV-44", "SFV-45"],
        )
        by_id = {x["rule_id"]: x for x in self.trace["freeze_process_mappings"]}
        self.assertEqual(by_id["SFG-001"]["status"], "SPM_REGENERATION_REQUIRED_AFTER_SCHEMA_REPAIR")
        self.assertEqual(by_id["SFG-002"]["status"], "SPM_REGENERATION_REQUIRED_AFTER_SCHEMA_REPAIR")
        self.assertEqual(by_id["SFG-003"]["status"], "REQUALIFICATION_REQUIRED_AFTER_SCHEMA_REPAIR")
        self.assertEqual(by_id["SFG-007"]["status"], "BLOCKED_PENDING_REPAIRED_EXACT_CANDIDATE_REVIEW")

    def test_predecessor_v2r1_output_evidence_does_not_transfer(self):
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

    def test_traceability_provenance_points_only_to_prequalification_sources(self):
        pps = self.source_map["artifact_sources"]["schema-freeze-traceability.json"]["pointer_prefix_sources"]
        self.assertEqual(
            pps["/freeze_process_mappings/2/status"],
            ["SPG-QUALIFICATION-2026-09-24"],
        )
        self.assertEqual(
            pps["/final_freeze_blockers"],
            [
                "R8-V15-R1-EXECUTABLE-SCHEMA-FREEZE-PREREGISTRATION-V2",
                "SPG-QUALIFICATION-2026-09-24",
            ],
        )
        self.assertEqual(
            pps["/note"],
            [
                "R8-V15-R1-EXECUTABLE-SCHEMA-FREEZE-PREREGISTRATION-V2",
                "SPG-QUALIFICATION-2026-09-24",
            ],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
