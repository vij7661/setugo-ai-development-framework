import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas" / "governance-r8" / "v15-r1"
FROZEN_CANDIDATE = "f93ca26975ecb64f0da13779889c75b36140cdfc"
SEMANTIC = "1fa49fa4adfa6aa47fae68c0f1938083eeb1497f"
SPM_SHA256 = "84c484121c4c8dd0592bcd7e4c070d8a3ab7f17215f4c3d2b31863fb6dbf6797"
SOURCE_MAP_SHA256 = "6d35964bfaa0cccfdd09bb46128a5efe3197d146e90144d1ac61ebe08c0aeec5"
TRACE_SHA256 = "cbe0a8cd1c955145bab3f00973fee465af1901a9d24dfd6748790d11a0b602ac"
P05_SHA = "161a1dcda7bae00f28f0ba32675f218fd4977065d2aa0439cf451c6d066dbbfb"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class R8V15R1PostFreezeRegressionTests(unittest.TestCase):
    def test_exact_executable_schema_freeze_record(self):
        record = load(ROOT / "governance-r8" / "R8-V15-R1-EXECUTABLE-SCHEMA-FREEZE.json")
        self.assertEqual(record["status"], "EXECUTABLE_SCHEMA_FROZEN")
        self.assertEqual(record["exact_frozen_candidate_commit"], FROZEN_CANDIDATE)
        self.assertEqual(record["reviewed_semantic_commit"], SEMANTIC)
        self.assertEqual(record["final_spm_sha256"], SPM_SHA256)
        self.assertEqual(record["gate_evidence"]["sfv_45"], "PASS")
        self.assertEqual(record["gate_evidence"]["final_freeze_blockers"], [])
        self.assertFalse(record["claim_boundary"]["runtime_qualification_authorized"])
        self.assertFalse(record["claim_boundary"]["production_authorized"])

    def test_final_spm_is_present_and_exact(self):
        spm_path = SCHEMA_ROOT / "schema-provenance-manifest-candidate.json"
        self.assertTrue(spm_path.is_file())
        self.assertEqual(sha(spm_path), SPM_SHA256)
        spm = load(spm_path)
        self.assertEqual(spm["status"], "FINAL_FREEZE_ELIGIBLE")
        self.assertEqual(spm["semantic_candidate_commit"], SEMANTIC)
        self.assertEqual(spm["coverage"], {
            "uncovered_semantic_elements": [],
            "non_authoritative_only_sources": [],
            "conflicting_entries": [],
        })

    def test_source_map_and_traceability_exact_hashes(self):
        source_map_path = SCHEMA_ROOT / "schema-provenance-source-map.json"
        trace_path = SCHEMA_ROOT / "schema-freeze-traceability.json"
        self.assertEqual(sha(source_map_path), SOURCE_MAP_SHA256)
        self.assertEqual(sha(trace_path), TRACE_SHA256)
        source_map = load(source_map_path)
        trace = load(trace_path)
        self.assertEqual(source_map["semantic_candidate_commit"], SEMANTIC)
        self.assertEqual(trace["semantic_candidate_commit"], SEMANTIC)
        self.assertEqual(trace["final_freeze_blockers"], ["SFV-45"])

    def test_p05_semantic_correction_remains_exact(self):
        gcp = load(SCHEMA_ROOT / "gcp-rvm-2.json")
        p05 = next(x for x in gcp["canonical_vectors"] if x["vector_id"] == "GCP-RVM2-P05")
        self.assertEqual(
            p05["expected_canonical_utf8"],
            '{"max":9223372036854775807,"min":-9223372036854775808}',
        )
        self.assertEqual(p05["expected_sha256"], P05_SHA)

    def test_runtime_contract_repairs_remain_present(self):
        defs = load(SCHEMA_ROOT / "runtime-contracts.schema.json")["$defs"]
        las = defs["LASAuthorityStateRoot"]
        self.assertNotIn("semantic_heads", las["properties"])
        self.assertIn("state_root_digest", las["required"])
        stc = defs["StateTransferCertificate"]
        self.assertIn("rotation_prepare_certificate_digest", stc["required"])
        self.assertIn("semantic_state_binding_required", stc["required"])
        self.assertIn("GGSGenesisStateRoot", defs)
        csm = defs["CurrentSemanticModelBundle"]
        self.assertIn("resolver_policy_ref", csm["required"])
        self.assertNotIn("resolver_policy", csm["properties"])
        self.assertIn("ResolverConformanceSuite1", defs)
        self.assertIn("rcs_suite", defs["ResolverConformanceEvidence"]["required"])

    def test_final_independent_review_evidence_is_preserved(self):
        review = load(ROOT / "governance-r8" / "R8-V15-R1-SFV45-R3-FINAL-INDEPENDENT-REVIEW.json")
        self.assertEqual(review["exact_candidate_commit"], FROZEN_CANDIDATE)
        self.assertEqual(review["reviewer_disposition"], "PASS")
        self.assertEqual(review["sfv_45"], "PASS")
        self.assertEqual(review["adjudication"], "ACCEPTED")
        self.assertFalse(review["claim_boundary"]["runtime_qualification_authorized"])

    def test_implementation_branch_does_not_modify_frozen_schema_bytes(self):
        result = subprocess.run(
            ["git", "diff", "--name-only", FROZEN_CANDIDATE, "HEAD", "--", "schemas/governance-r8/v15-r1"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.stdout.strip(), "")

    def test_implementation_authorization_remains_bounded(self):
        auth = load(ROOT / "governance-r8" / "R8-V15-R1-IMPLEMENTATION-AUTHORIZATION.json")
        self.assertEqual(auth["status"], "IMPLEMENTATION_AUTHORIZED_BOUNDED_LOCAL_CONSTRUCTION")
        self.assertTrue(auth["grants"]["implementation_construction"])
        self.assertFalse(auth["grants"]["runtime_qualification"])
        self.assertFalse(auth["grants"]["release"])
        self.assertFalse(auth["grants"]["deployment"])
        self.assertFalse(auth["grants"]["production"])
        self.assertFalse(auth["grants"]["terminal_authority"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
