import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "schemas/governance-r8/v15-r1/runtime-contracts.schema.json"
GCP = ROOT / "schemas/governance-r8/v15-r1/gcp-rvm-2.json"
SOURCE_MAP = ROOT / "schemas/governance-r8/v15-r1/schema-provenance-source-map.json"
TRACE = ROOT / "schemas/governance-r8/v15-r1/schema-freeze-traceability.json"
SPM = ROOT / "schemas/governance-r8/v15-r1/schema-provenance-manifest-candidate.json"
SEMANTIC_CORRECTION = ROOT / "governance-r8/R8-V15-R1-GCP-P05-SEMANTIC-CORRECTION.json"


class R8V15R1SFV45R3RepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
        cls.defs = cls.runtime["$defs"]
        cls.gcp = json.loads(GCP.read_text(encoding="utf-8"))
        cls.source_map = json.loads(SOURCE_MAP.read_text(encoding="utf-8"))
        cls.trace = json.loads(TRACE.read_text(encoding="utf-8"))

    def test_las_root_uses_flat_frozen_members(self):
        las = self.defs["LASAuthorityStateRoot"]
        required = set(las["required"])
        expected = {
            "semantic_state_sequence",
            "committed_log_prefix_digest",
            "stream_head_map_root",
            "idempotency_ledger_root",
            "authority_state_machine_root",
            "revocation_stream_head",
            "nonce_ledger_head",
            "effect_stream_head",
            "csm5_registry_head",
            "aim4_descriptor_head",
            "any_scope_permission_head",
            "aim_scope_policy_head",
            "resolver_policy_head",
            "resolver_implementation_registry_head",
            "guard_registry_head",
            "configuration_generation",
            "prior_certificate_chain_digest",
            "state_root_digest",
        }
        self.assertEqual(required, expected)
        self.assertNotIn("semantic_heads", las["properties"])
        self.assertNotIn("configuration_head", las["properties"])

    def test_semantic_heads_are_only_named_semantic_registry_heads(self):
        heads = self.defs["SemanticHeads"]
        expected = {
            "csm5_registry_head",
            "aim4_descriptor_head",
            "any_scope_permission_head",
            "aim_scope_policy_head",
            "resolver_policy_head",
            "resolver_implementation_registry_head",
            "guard_registry_head",
        }
        self.assertEqual(set(heads["required"]), expected)
        self.assertEqual(set(heads["properties"]), expected)

    def test_stc_binds_barrier_and_exact_system_root(self):
        stc = self.defs["StateTransferCertificate"]
        self.assertIn("barrier_certificate_digest", stc["required"])
        self.assertIn("las_authority_state_root", stc["properties"])
        self.assertIn("ggs_genesis_state_root", stc["properties"])
        self.assertNotIn("semantic_heads", stc["required"])
        invariants = "\n".join(stc["x-validator-invariants"])
        self.assertIn("ROTATION_PREPARE", invariants)
        self.assertIn("STC_COMMIT", invariants)
        self.assertIn("required iff", invariants)

    def test_ggs_root_exact_base_formula_and_conditional_semantics(self):
        ggs = self.defs["GGSGenesisStateRoot"]
        base = {
            "B",
            "committed_log_prefix_digest_B",
            "constitution_namespace_root_B",
            "bootstrap_authorization_root_B",
            "idempotency_ledger_root_B",
            "configuration_generation",
            "prior_certificate_chain_digest_B",
            "state_root_digest",
        }
        self.assertEqual(set(ggs["required"]), base)
        self.assertIn("semantic_bundle_digest", ggs["properties"])
        self.assertIn("semantic_heads", ggs["properties"])
        invariants = "\n".join(ggs["x-validator-invariants"])
        self.assertIn("R8V12-I023", invariants)

    def test_csm_uses_resolver_policy_ref_not_embedded_policy(self):
        csm = self.defs["CurrentSemanticModelBundle"]
        self.assertIn("resolver_policy_ref", csm["required"])
        self.assertIn("resolver_policy_ref", csm["properties"])
        self.assertNotIn("resolver_policy", csm["properties"])

    def test_rcs_suite_identity_is_machine_readable_and_evidence_bound(self):
        suite = self.defs["ResolverConformanceSuite1"]
        expected = {
            "suite_id",
            "suite_version",
            "vector_manifest_digest",
            "vector_generator_implementation_digest",
            "generator_runtime_manifest_digest",
            "input_corpus_digest",
            "expected_result_manifest_digest",
            "execution_harness_digest",
            "required_resolver_runtime_identity_digest",
            "required_resolver_workload_identity_digest",
            "result_schema_digest",
            "suite_digest",
        }
        self.assertEqual(set(suite["required"]), expected)
        evidence = self.defs["ResolverConformanceEvidence"]
        self.assertIn("rcs_suite", evidence["required"])
        self.assertIn("rcs_suite_digest", evidence["required"])

    def test_dps_effect_class_is_conditionally_omitted_not_required_null(self):
        dps = self.defs["DecisionPresealContext"]
        self.assertIn("effect_class", dps["properties"])
        self.assertNotIn("effect_class", dps["required"])
        self.assertEqual(dps["properties"]["effect_class"], {"$ref": "#/$defs/CanonicalId"})
        self.assertIn("present iff", "\n".join(dps["x-validator-invariants"]))

    def test_t0_successor_drops_untraced_bootstrap_authorization_digest(self):
        t0 = self.defs["T0SuccessorManifest"]
        self.assertNotIn("bootstrap_authorization_digest", t0["properties"])
        self.assertNotIn("bootstrap_authorization_digest", t0["required"])

    def test_gcp_p05_matches_accepted_semantic_successor(self):
        p05 = next(v for v in self.gcp["canonical_vectors"] if v["vector_id"] == "GCP-RVM2-P05")
        expected = '{"max":9223372036854775807,"min":-9223372036854775808}'
        self.assertEqual(p05["expected_canonical_utf8"], expected)
        self.assertEqual(
            hashlib.sha256(expected.encode("utf-8")).hexdigest(),
            "161a1dcda7bae00f28f0ba32675f218fd4977065d2aa0439cf451c6d066dbbfb",
        )
        self.assertEqual(
            p05["expected_sha256"],
            "161a1dcda7bae00f28f0ba32675f218fd4977065d2aa0439cf451c6d066dbbfb",
        )
        self.assertIn("R8-V15-R1-GCP-P05-SEMANTIC-CORRECTION", p05["source_rules"])

    def test_semantic_successor_and_provenance_are_rebound(self):
        self.assertEqual(
            self.source_map["semantic_candidate_commit"],
            "1fa49fa4adfa6aa47fae68c0f1938083eeb1497f",
        )
        self.assertEqual(
            self.trace["semantic_candidate_commit"],
            "1fa49fa4adfa6aa47fae68c0f1938083eeb1497f",
        )
        refs = self.source_map["named_source_refs"]
        self.assertIn("SRC-GCP-P05-CORRECTION", refs)
        self.assertIn("SRC-V14", refs)
        self.assertNotIn("SRC-SPG-V2R1-EXTENSION", refs)
        self.assertNotIn("SRC-SPG-V2R1-VERIFY", refs)

    def test_successor_specific_qualification_is_reopened_and_spm_absent(self):
        self.assertFalse(SPM.exists())
        self.assertEqual(self.trace["status"], "SCHEMA_FREEZE_CANDIDATE_R3_NON_AUTHORITATIVE")
        expected = {
            "SFV-17","SFV-20","SFV-26","SFV-27","SFV-29","SFV-30","SFV-31",
            "SFV-33","SFV-35","SFV-36","SFV-37","SFV-44","SFV-45"
        }
        self.assertEqual(set(self.trace["final_freeze_blockers"]), expected)

    def test_semantic_correction_record_is_present(self):
        record = json.loads(SEMANTIC_CORRECTION.read_text(encoding="utf-8"))
        self.assertEqual(
            record["corrected_vector"]["sha256"],
            "161a1dcda7bae00f28f0ba32675f218fd4977065d2aa0439cf451c6d066dbbfb",
        )
        self.assertFalse(record["scope"]["other_semantics_changed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
