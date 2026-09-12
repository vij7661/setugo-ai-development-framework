from __future__ import annotations

import copy
import unittest

from v24_authority_universe import FUNCTIONAL_CATCH_ALL, validate_authority_universe_bundle


GEN = "GEN-V24-CONSTRUCTION"


def valid_bundle():
    return {
        "governance_generation_id": GEN,
        "authority_universe_contract": {
            "supported_authority_classes": [FUNCTIONAL_CATCH_ALL, "STATE_WRITE", "EXTERNAL_EFFECT"],
            "unknown_class_behavior": "FAIL_CLOSED_AUTHORITY_ADMISSION_REQUIRED",
        },
        "control_planes": [
            {"control_plane_id": "CP-DEPLOY", "class": "DEPLOYMENT"},
            {"control_plane_id": "CP-CRED", "class": "CREDENTIAL"},
        ],
        "authority_sinks": [
            {
                "sink_id": "SINK-STATE",
                "effect_classes": ["STATE_WRITE"],
                "admitted_writer_ids": ["gateway"],
                "required_control_plane_ids": ["CP-DEPLOY", "CP-CRED"],
                "unadmitted_writer_behavior": "DENY",
                "generation_id": GEN,
            }
        ],
        "consequential_effectors": [
            {
                "effector_id": "EFF-GW",
                "sink_id": "SINK-STATE",
                "authority_classes": ["STATE_WRITE"],
                "generation_id": GEN,
            }
        ],
        "effect_paths": [
            {
                "path_id": "PATH-GW-STATE",
                "source_component_id": "gateway",
                "sink_id": "SINK-STATE",
                "functional_effects": ["CREATE_AUTHORITY_STATE"],
                "admitted_authority_classes": ["STATE_WRITE"],
                "control_plane_ids": ["CP-DEPLOY", "CP-CRED"],
                "guard_ids": ["GUARD-AUTHORITY"],
                "material_authority_effect": True,
                "runtime_observed": True,
                "generation_id": GEN,
            }
        ],
        "dependency_edges": [
            {
                "source_id": "gateway",
                "target_id": "SINK-STATE",
                "edge_type": "AUTHORITY_EFFECT",
                "predicate_id": "PRED-STATE-WRITE",
                "material": True,
            }
        ],
        "completeness_required_subjects": [
            {"subject_id": "SUB-SINKS", "subject_kind": "AUTHORITY_SINK_REGISTRY"},
            {"subject_id": "SUB-EFFECTORS", "subject_kind": "CONSEQUENTIAL_EFFECTOR_REGISTRY"},
            {"subject_id": "SUB-GRAPH", "subject_kind": "AUTHORITY_DEPENDENCY_GRAPH"},
            {"subject_id": "SUB-PATHS", "subject_kind": "AUTHORITY_EFFECT_PATH_SET"},
            {"subject_id": "SUB-PLANES", "subject_kind": "CONTROL_PLANE_SET"},
        ],
        "independent_universe_projection": {
            "derivation_authority_id": "IUDA-CONSTRUCTION-STUB",
            "source_kind": "INDEPENDENT_EVIDENCE_INPUT",
            "source_evidence_digest": "e" * 64,
            "material_path_ids": ["PATH-GW-STATE"],
            "sink_ids": ["SINK-STATE"],
            "control_plane_ids": ["CP-DEPLOY", "CP-CRED"],
        },
    }


class AuthorityUniverseTests(unittest.TestCase):
    def assertProblem(self, mutate, expected):
        bundle = valid_bundle()
        mutate(bundle)
        result = validate_authority_universe_bundle(bundle)
        self.assertIn(expected, result["problems"])
        self.assertFalse(result["qualified"])

    def test_positive_construction_valid_but_non_authoritative(self):
        result = validate_authority_universe_bundle(valid_bundle())
        self.assertEqual(result["state"], "AUTHORITY_UNIVERSE_CONSTRUCTION_VALID")
        self.assertEqual(result["problems"], [])
        self.assertFalse(result["qualified"])
        self.assertEqual(result["authority_effect"], "NONE_EVIDENCE_ONLY")

    def test_functional_catchall_is_mandatory(self):
        self.assertProblem(
            lambda b: b["authority_universe_contract"]["supported_authority_classes"].remove(FUNCTIONAL_CATCH_ALL),
            "FUNCTIONAL_CATCH_ALL_MISSING",
        )

    def test_unknown_class_must_fail_closed(self):
        self.assertProblem(
            lambda b: b["authority_universe_contract"].__setitem__("unknown_class_behavior", "ALLOW_UNKNOWN"),
            "UNKNOWN_CLASS_FAIL_CLOSED_REQUIRED",
        )

    def test_projected_unknown_path_blocks(self):
        self.assertProblem(
            lambda b: b["independent_universe_projection"]["material_path_ids"].append("PATH-HIDDEN-DIRECT-DB"),
            "PROJECTED_MATERIAL_PATH_UNRESOLVED:PATH-HIDDEN-DIRECT-DB",
        )

    def test_observed_path_missing_from_independent_projection_blocks(self):
        self.assertProblem(
            lambda b: b["independent_universe_projection"].__setitem__("material_path_ids", []),
            "OBSERVED_PATH_ABSENT_FROM_INDEPENDENT_PROJECTION:PATH-GW-STATE",
        )

    def test_self_derived_projection_blocks(self):
        self.assertProblem(
            lambda b: b["independent_universe_projection"].__setitem__("source_kind", "CANDIDATE_SELF_DERIVED"),
            "INDEPENDENT_PROJECTION_SELF_DERIVED",
        )

    def test_missing_graph_edge_blocks(self):
        self.assertProblem(
            lambda b: b.__setitem__("dependency_edges", []),
            "GRAPH_MATERIAL_EDGE_MISSING:gateway:SINK-STATE:AUTHORITY_EFFECT",
        )

    def test_unknown_control_plane_blocks(self):
        self.assertProblem(
            lambda b: b["effect_paths"][0]["control_plane_ids"].append("CP-CLOUD-ROOT"),
            "PATH_CONTROL_PLANE_UNKNOWN:PATH-GW-STATE:CP-CLOUD-ROOT",
        )

    def test_sink_must_deny_unadmitted_writer(self):
        self.assertProblem(
            lambda b: b["authority_sinks"][0].__setitem__("unadmitted_writer_behavior", "LOG_ONLY"),
            "SINK_UNADMITTED_WRITER_NOT_DENY:SINK-STATE",
        )

    def test_functionally_material_path_requires_admission(self):
        self.assertProblem(
            lambda b: b["effect_paths"][0].__setitem__("admitted_authority_classes", []),
            "PATH_AUTHORITY_ADMISSION_REQUIRED:PATH-GW-STATE",
        )

    def test_new_omission_sensitive_registry_requires_completeness_subject(self):
        self.assertProblem(
            lambda b: b.__setitem__(
                "completeness_required_subjects",
                [x for x in b["completeness_required_subjects"] if x["subject_kind"] != "CONTROL_PLANE_SET"],
            ),
            "COMPLETENESS_REQUIRED_SUBJECT_MISSING:CONTROL_PLANE_SET",
        )

    def test_generation_mismatch_blocks(self):
        self.assertProblem(
            lambda b: b["effect_paths"][0].__setitem__("generation_id", "OLD-GEN"),
            "PATH_GENERATION_MISMATCH:PATH-GW-STATE",
        )


if __name__ == "__main__":
    unittest.main()
