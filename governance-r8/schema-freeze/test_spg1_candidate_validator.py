import copy
import unittest

from spg1_candidate_validator import evaluate, enumerate_nodes


SOURCE = {
    "path": "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V8.md",
    "blob": "9990ae39ac4508a031860075c1178a94386c8aaa",
    "authoritative": True,
}


def plan_for(schema_body):
    nodes = enumerate_nodes(schema_body)
    return {
        "schema_version": 1,
        "semantic_candidate_commit": "c721b38cf8b00294797300b526596ce723a47ff8",
        "generator_binding": {
            "generator_id": "spg1-candidate",
            "executable_digest": "sha256:" + "1" * 64,
            "runtime_manifest_digest": "sha256:" + "2" * 64,
            "workload_attestation_digest": "sha256:" + "3" * 64,
            "signing_credential_id": "candidate-signing-credential",
            "generation_event_id": "SPG-EVENT-001",
        },
        "allowed_output_schema_classes": ["JSON_SCHEMA_2020_12"],
        "frozen_sources": [copy.deepcopy(SOURCE)],
        "artifact": {
            "artifact_id": "example.schema.json",
            "schema_class": "JSON_SCHEMA_2020_12",
            "schema_body": schema_body,
        },
        "provenance": [
            {
                "json_pointer": ptr,
                "semantic_purpose": "test semantics",
                "source_design_ids": ["R8V8-I020"],
                "sources": [{"path": SOURCE["path"], "blob": SOURCE["blob"]}],
                "reviewer_status": "NOT_REQUIRED_FOR_TEST",
            }
            for ptr in nodes
        ],
    }


class SPG1CandidateTests(unittest.TestCase):
    def test_p01_minimal_full_coverage(self):
        p = plan_for({"type": "object"})
        self.assertEqual(evaluate(p)["status"], "VALID_CANDIDATE_PLAN")

    def test_p02_nested_full_coverage(self):
        p = plan_for({
            "type": "object",
            "required": ["x"],
            "properties": {"x": {"type": "array", "items": {"type": "string"}}},
        })
        self.assertEqual(evaluate(p)["status"], "VALID_CANDIDATE_PLAN")

    def test_p03_multiple_authoritative_sources(self):
        p = plan_for({"type": "string"})
        second = {
            "path": "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V7.md",
            "blob": "4bffae9907735862946e97ff9c608abf960078a8",
            "authoritative": True,
        }
        p["frozen_sources"].append(second)
        p["provenance"][0]["sources"].append({"path": second["path"], "blob": second["blob"]})
        self.assertEqual(evaluate(p)["status"], "VALID_CANDIDATE_PLAN")

    def test_p04_deterministic(self):
        p = plan_for({"type": "boolean"})
        self.assertEqual(evaluate(p), evaluate(copy.deepcopy(p)))

    def test_n01_missing_provenance(self):
        p = plan_for({"type": "object", "properties": {"x": {"type": "string"}}})
        p["provenance"].pop()
        self.assertEqual(evaluate(p)["status"], "PROVENANCE_COVERAGE_MISSING")

    def test_n02_unknown_pointer(self):
        p = plan_for({"type": "string"})
        p["provenance"].append(copy.deepcopy(p["provenance"][0]))
        p["provenance"][-1]["json_pointer"] = "/does-not-exist"
        self.assertEqual(evaluate(p)["status"], "PROVENANCE_POINTER_UNKNOWN")

    def test_n03_duplicate_pointer(self):
        p = plan_for({"type": "string"})
        p["provenance"].append(copy.deepcopy(p["provenance"][0]))
        self.assertEqual(evaluate(p)["status"], "PROVENANCE_POINTER_DUPLICATE")

    def test_n04_unfrozen_source(self):
        p = plan_for({"type": "string"})
        p["provenance"][0]["sources"][0]["blob"] = "not-frozen"
        self.assertEqual(evaluate(p)["status"], "UNAUTHORIZED_SEMANTIC_SOURCE")

    def test_n05_nonauthoritative_only(self):
        p = plan_for({"type": "string"})
        p["frozen_sources"][0]["authoritative"] = False
        self.assertEqual(evaluate(p)["status"], "UNAUTHORIZED_SEMANTIC_SOURCE")

    def test_n06_candidate_mismatch(self):
        p = plan_for({"type": "string"})
        p["semantic_candidate_commit"] = "wrong"
        self.assertEqual(evaluate(p)["status"], "FROZEN_CANDIDATE_MISMATCH")

    def test_n07_schema_class(self):
        p = plan_for({"type": "string"})
        p["artifact"]["schema_class"] = "OTHER"
        self.assertEqual(evaluate(p)["status"], "OUTPUT_SCHEMA_CLASS_UNAUTHORIZED")

    def test_n08_runtime_manifest_missing(self):
        p = plan_for({"type": "string"})
        p["generator_binding"]["runtime_manifest_digest"] = ""
        self.assertEqual(evaluate(p)["status"], "GENERATOR_BINDING_INCOMPLETE")

    def test_n09_workload_attestation_missing(self):
        p = plan_for({"type": "string"})
        p["generator_binding"]["workload_attestation_digest"] = ""
        self.assertEqual(evaluate(p)["status"], "GENERATOR_BINDING_INCOMPLETE")

    def test_n10_signing_credential_missing(self):
        p = plan_for({"type": "string"})
        p["generator_binding"]["signing_credential_id"] = ""
        self.assertEqual(evaluate(p)["status"], "GENERATOR_BINDING_INCOMPLETE")

    def test_n11_unknown_plan_field(self):
        p = plan_for({"type": "string"})
        p["qualified"] = True
        self.assertEqual(evaluate(p)["status"], "PLAN_SCHEMA_INVALID")

    def test_n12_authority_claim_injection(self):
        p = plan_for({"type": "string"})
        p["authority_effect"] = "GRANTED"
        self.assertEqual(evaluate(p)["status"], "PLAN_SCHEMA_INVALID")


if __name__ == "__main__":
    unittest.main()
