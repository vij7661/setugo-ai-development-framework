import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "schemas/governance-r8/v15-r1/schema-freeze-traceability.json"
SOURCE_MAP = ROOT / "schemas/governance-r8/v15-r1/schema-provenance-source-map.json"
SPM_CANDIDATE = ROOT / "schemas/governance-r8/v15-r1/schema-provenance-manifest-candidate.json"


class R8V15R1QualificationLifecycleInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trace = json.loads(TRACE.read_text(encoding="utf-8"))
        cls.source_map = json.loads(SOURCE_MAP.read_text(encoding="utf-8"))
        cls.by_id = {x["rule_id"]: x for x in cls.trace["freeze_process_mappings"]}

    def test_candidate_is_in_a_lawful_pre_materialization_state(self):
        status = self.trace["status"]
        self.assertIn(
            status,
            {
                "SCHEMA_FREEZE_CANDIDATE_V4_NON_AUTHORITATIVE",
                "QUALIFIED_EVIDENCE_REBIND_PRECOMMIT_NON_AUTHORITATIVE",
            },
        )
        self.assertFalse(SPM_CANDIDATE.exists())

    def test_prequalification_or_fixed_point_gate_state_is_consistent(self):
        status = self.trace["status"]
        refs = self.source_map["named_source_refs"]
        routes = {x["match_prefix"]: x for x in self.source_map["source_ref_routes"]}

        if status == "SCHEMA_FREEZE_CANDIDATE_V4_NON_AUTHORITATIVE":
            self.assertEqual(
                self.trace["final_freeze_blockers"],
                ["SFV-35", "SFV-36", "SFV-44", "SFV-45"],
            )
            self.assertIn("REGENERATION_REQUIRED", self.by_id["SFG-001"]["status"])
            self.assertTrue(
                "REBIND_REQUIRED" in self.by_id["SFG-002"]["status"]
                or "REBIND_COMPLETE" in self.by_id["SFG-002"]["status"]
                or "REGENERATION_REQUIRED" in self.by_id["SFG-002"]["status"]
            )
            self.assertIn("REQUALIFICATION_REQUIRED", self.by_id["SFG-003"]["status"])
            self.assertNotIn("SRC-SPG-V2R1-EXTENSION", refs)
            self.assertNotIn("SRC-SPG-V2R1-VERIFY", refs)
            self.assertNotIn("SPG-QUALIFICATION-V2-R1-2026-09-24", routes)
        else:
            self.assertEqual(self.trace["final_freeze_blockers"], ["SFV-45"])
            self.assertEqual(
                self.by_id["SFG-001"]["status"],
                "QUALIFIED_SPM_EVIDENCE_PRECOMMITTED_PENDING_EXACT_FINAL_REGENERATION",
            )
            self.assertEqual(
                self.by_id["SFG-002"]["status"],
                "QUALIFIED_SOURCE_AUTHORITY_PRECOMMITTED_PENDING_EXACT_FINAL_REGENERATION",
            )
            self.assertEqual(
                self.by_id["SFG-003"]["status"],
                "QUALIFIED_GENERATOR_EVIDENCE_PRECOMMITTED_PENDING_EXACT_FINAL_REGENERATION",
            )
            self.assertIn("SRC-SPG-V2R1-EXTENSION", refs)
            self.assertIn("SRC-SPG-V2R1-VERIFY", refs)
            self.assertIn("SPG-QUALIFICATION-V2-R1-2026-09-24", routes)

        self.assertEqual(
            self.by_id["SFG-007"]["status"],
            (
                "BLOCKED_PENDING_REPAIRED_EXACT_CANDIDATE_REVIEW"
                if status == "SCHEMA_FREEZE_CANDIDATE_V4_NON_AUTHORITATIVE"
                else "BLOCKED_PENDING_EXACT_QUALIFIED_CANDIDATE_REVIEW"
            ),
        )

    def test_base_generator_identity_runtime_qualification_sources_remain(self):
        refs = self.source_map["named_source_refs"]
        self.assertIn("SRC-SPG-ENROLLMENT", refs)
        self.assertIn("SRC-SPG-STAGEB-VERIFY", refs)
        routes = {x["match_prefix"]: x for x in self.source_map["source_ref_routes"]}
        self.assertEqual(
            routes["SPG-QUALIFICATION-2026-09-24"]["source_ref_ids"],
            ["SRC-SPG-ENROLLMENT", "SRC-SPG-STAGEB-VERIFY"],
        )

    def test_reviewed_semantic_basis_is_exact(self):
        self.assertEqual(
            self.trace["semantic_candidate_commit"],
            "1fa49fa4adfa6aa47fae68c0f1938083eeb1497f",
        )
        self.assertEqual(
            self.source_map["semantic_candidate_commit"],
            "1fa49fa4adfa6aa47fae68c0f1938083eeb1497f",
        )
        refs = self.source_map["named_source_refs"]
        self.assertEqual(
            refs["SRC-GCP-P05-CORRECTION"]["commit"],
            "1fa49fa4adfa6aa47fae68c0f1938083eeb1497f",
        )
        self.assertEqual(
            refs["SRC-GCP-P05-REVIEW"]["commit"],
            "c1d983ebd6eca0a78a41c946709bf246cf876f68",
        )
        self.assertEqual(
            refs["SRC-GCP-P05-ACCEPTANCE"]["commit"],
            "c1d983ebd6eca0a78a41c946709bf246cf876f68",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
