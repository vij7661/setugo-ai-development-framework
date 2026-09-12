from __future__ import annotations

import unittest
from v24_effective_control import validate_effective_control_bundle

GEN = "GEN-V24"


def valid_bundle():
    return {
        "governance_generation_id": GEN,
        "mandatory_source_classes": ["DEPLOYMENT_ADMIN", "CREDENTIAL_ADMIN"],
        "control_sources": [
            {"source_id":"SRC-DEPLOY","source_class":"DEPLOYMENT_ADMIN","control_domain_id":"D-DEPLOY","independent_derivation_evidence_digest":"a"*64,"generation_id":GEN},
            {"source_id":"SRC-CRED","source_class":"CREDENTIAL_ADMIN","control_domain_id":"D-CRED","independent_derivation_evidence_digest":"b"*64,"generation_id":GEN},
        ],
        "required_relationship_queries": [
            {"subject_id":"SINK-A","source_id":"SRC-DEPLOY"},
            {"subject_id":"SINK-A","source_id":"SRC-CRED"},
        ],
        "relationships": [
            {"relationship_id":"REL-1","subject_id":"SINK-A","source_id":"SRC-DEPLOY","status":"CONTROL_PRESENT","generation_id":GEN},
            {"relationship_id":"REL-2","subject_id":"SINK-A","source_id":"SRC-CRED","status":"NO_RELATIONSHIP_EVIDENCE_FOR_BOUND_SCOPE","negative_evidence_digest":"c"*64,"generation_id":GEN},
        ],
        "effective_control_closure": {
            "control_edges": [["SRC-DEPLOY","SINK-A"]],
            "root_threshold_capable_control_sets": [["SRC-DEPLOY"],["SRC-CRED"]],
        },
        "capability_inventory": [
            {"capability_id":"CAP-A","owner_control_domain_id":"D-OWNER","generation_id":GEN}
        ],
        "capability_attestations": [
            {"attestation_id":"ATT-A","capability_id":"CAP-A","independent_attestor_id":"ATTESTOR-X","attestor_control_domain_id":"D-ATTEST","measured_deployment_digest":"d"*64,"measured_configuration_digest":"e"*64,"state":"CURRENT","generation_id":GEN}
        ],
        "deployment_observations": [
            {"observation_id":"OBS-A","capability_id":"CAP-A","deployment_digest":"d"*64,"configuration_digest":"e"*64,"generation_id":GEN}
        ],
    }


class EffectiveControlTests(unittest.TestCase):
    def assertProblem(self, mutate, expected):
        b = valid_bundle(); mutate(b)
        r = validate_effective_control_bundle(b)
        self.assertIn(expected, r["problems"]); self.assertFalse(r["qualified"])

    def test_positive_construction_non_authoritative(self):
        r=validate_effective_control_bundle(valid_bundle())
        self.assertEqual(r["state"],"EFFECTIVE_CONTROL_CONSTRUCTION_VALID"); self.assertEqual(r["problems"],[]); self.assertFalse(r["qualified"])

    def test_mandatory_source_class_missing(self):
        self.assertProblem(lambda b: b["control_sources"].pop(), "MANDATORY_SOURCE_CLASS_MISSING:CREDENTIAL_ADMIN")

    def test_silence_is_not_negative_evidence(self):
        self.assertProblem(lambda b: b["relationships"].pop(), "RELATIONSHIP_QUERY_UNANSWERED:SINK-A:SRC-CRED")

    def test_negative_relationship_requires_evidence(self):
        self.assertProblem(lambda b: b["relationships"][1].pop("negative_evidence_digest"), "RELATIONSHIP_NEGATIVE_EVIDENCE_REQUIRED:REL-2")

    def test_control_edge_cannot_disappear(self):
        self.assertProblem(lambda b: b["effective_control_closure"].__setitem__("control_edges",[]), "EFFECTIVE_CONTROL_EDGE_OMITTED:SRC-DEPLOY:SINK-A")

    def test_threshold_control_sets_required(self):
        self.assertProblem(lambda b: b["effective_control_closure"].__setitem__("root_threshold_capable_control_sets",[]), "ROOT_THRESHOLD_CAPABLE_CONTROL_SETS_REQUIRED")

    def test_attestor_must_be_independent(self):
        self.assertProblem(lambda b: b["capability_attestations"][0].__setitem__("attestor_control_domain_id","D-OWNER"), "CAPABILITY_ATTESTOR_NOT_INDEPENDENT:CAP-A")

    def test_deployment_drift_invalidates_attestation(self):
        self.assertProblem(lambda b: b["deployment_observations"][0].__setitem__("configuration_digest","f"*64), "CAPABILITY_ATTESTATION_STALE_DRIFT:CAP-A")

    def test_capability_attestation_required(self):
        self.assertProblem(lambda b: b.__setitem__("capability_attestations",[]), "CAPABILITY_ATTESTATION_MISSING:CAP-A")

    def test_deployment_observation_required(self):
        self.assertProblem(lambda b: b.__setitem__("deployment_observations",[]), "CAPABILITY_DEPLOYMENT_OBSERVATION_MISSING:CAP-A")

if __name__ == "__main__": unittest.main()
