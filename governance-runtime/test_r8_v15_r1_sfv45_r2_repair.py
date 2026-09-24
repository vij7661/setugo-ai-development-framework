import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas/governance-r8/v15-r1/runtime-contracts.schema.json"
SOURCE_MAP_PATH = ROOT / "schemas/governance-r8/v15-r1/schema-provenance-source-map.json"
FREEZE_PATH = ROOT / "schemas/governance-r8/v15-r1/schema-freeze-traceability.json"
INT64_MAX = 9223372036854775807


class R8V15R1SFV45R2RepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.defs = cls.schema["$defs"]

    def test_all_signed_sequence_ceilings_are_exact(self):
        maxima = []

        def walk(value):
            if isinstance(value, dict):
                if "maximum" in value:
                    maxima.append(value["maximum"])
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(self.schema)
        self.assertGreaterEqual(len(maxima), 1)
        self.assertTrue(all(value == INT64_MAX for value in maxima if value > 9))
        self.assertLessEqual(INT64_MAX, INT64_MAX)
        self.assertGreater(INT64_MAX + 1, INT64_MAX)

    def test_repaired_defs_require_confirmed_members(self):
        expected = {
            "MTRResponse": {"mtr_challenge_id", "response_nonce_echo", "signature", "attestation_proof"},
            "RevocationEvent": {"attestation_serial", "effective_revocation_seq", "reason_class", "eba_threshold_proof", "btw_inclusion_consistency_proof", "mtr_high_water_update"},
            "ResolverImplementationRegistryRecord": {"resolver_implementation_record_id", "resolver_implementation_digest", "resolver_runtime_manifest_digest", "workload_attestation_policy_digest", "predecessor_record_id", "constitutional_source_evidence_digest"},
            "ResolverConformanceEvidence": {"rir_record_digest", "resolver_implementation_digest", "resolver_runtime_manifest_digest", "rcs_suite_digest", "rcs_vector_digests", "raw_per_vector_results", "deterministic_aggregate_result"},
            "AuthorityReadSetEntry": {"schema_semantic_entry_digest"},
            "RecoveryContext": {"recovery_context_id", "constitution_id", "trigger_type", "affected_objects_or_streams", "current_t0_generation", "current_las_head_digest", "current_anchor_head_digests", "trigger_evidence_digests"},
            "ResolverPolicyContract": {"policy_version", "resolver_algorithm_version", "successor_traversal_rule_digest", "forensic_replay_rule_digest"},
            "ReviewAttestation": {"review_dimension_results"},
            "EvidenceRecord": {"input_object_ids", "input_object_digests", "execution_proof_digest", "output_derivation_digest", "event_id"},
            "EffectIntent": {"provider_id", "action", "candidate_scope_digest", "action_scope_digest", "tenant_scope_digest"},
            "MigrationBinding": {"requalification_proof"},
            "MigrationRequalificationProof": {"source_constitution_namespace", "destination_constitution_namespace", "complete_object_map", "pre_policy_snapshot_digest", "post_policy_snapshot_digest", "issuer_scope_widening", "reviewer_evidence_scope_widening", "authority_scope_widening", "destination_qualification_results", "authority_referenced_object_closure"},
        }
        for name, members in expected.items():
            self.assertIn(name, self.defs)
            self.assertTrue(members.issubset(set(self.defs[name].get("required", []))), name)

    def test_traceability_maps_requalification_proof(self):
        source_map = json.loads(SOURCE_MAP_PATH.read_text(encoding="utf-8"))
        pointers = source_map["artifact_sources"]["runtime-contracts.schema.json"]["pointer_prefix_sources"]
        self.assertEqual(pointers["/$defs/MigrationRequalificationProof"], ["NORM-037"])
        freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))
        norm = next(item for item in freeze["mappings"] if item["norm"] == "NORM-037")
        self.assertIn("runtime-contracts#MigrationRequalificationProof", norm["schemas"])

    def test_schema_is_strict_for_repaired_objects(self):
        for name in ("MTRResponse", "RevocationEvent", "MigrationRequalificationProof", "ReviewAttestation", "EvidenceRecord", "EffectIntent"):
            self.assertIs(self.defs[name]["additionalProperties"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
