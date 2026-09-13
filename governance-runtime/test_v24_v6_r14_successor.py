from __future__ import annotations

import unittest

from v24_v6_governance_foundation import digest
from v24_v6_r14_successor import REQUIRED_R14_CHECKS, validate_native_observation_evidence_bundle

COMMIT="1"*40
TREE="2"*40
ENV="3"*64
INTERPRETER="4"*64
NATIVE_SOURCE="5"*40
NATIVE_BINARY="6"*64
COMPILER="7"*64
ORACLE="8"*40


def record(check_id: str) -> dict:
    row={
        "check_id":check_id,
        "challenge_digest":"9"*64,
        "request_digest":"a"*64,
        "observation_digest":"b"*64,
        "assertion_digest":"c"*64,
        "candidate_commit":COMMIT,
        "candidate_tree":TREE,
        "environment_digest":ENV,
        "interpreter_contract_digest":INTERPRETER,
        "native_observer_source_git_blob_sha1":NATIVE_SOURCE,
        "native_observer_binary_sha256":NATIVE_BINARY,
        "native_observer_compiler_digest":COMPILER,
        "oracle_git_blob_sha1":ORACLE,
        "run_id":"run-1",
        "round_id":"round-1",
        "candidate_process_role":"UNTRUSTED_EXECUTION_ONLY",
        "observation_transport":"NATIVE_PARENT_AUTHENTICATED_FRAME",
        "observation_authentication":"HMAC_SHA256_EPHEMERAL_NATIVE_PARENT",
        "native_parent_initializes_python":False,
        "trusted_parent_imports_candidate_python":False,
        "oracle_decision_origin":"TRUSTED_EXTERNAL_ORACLE",
        "oracle_control_domain":"R14-EXTERNAL-ORACLE",
        "candidate_control_domain":"R14-CANDIDATE",
        "oracle_terminal_result":"PASS",
        "r13_tailored_frame_regression":"REJECTED",
    }
    row["record_digest"]=digest(dict(row))
    return row


def bundle() -> dict:
    rows=[record(x) for x in sorted(REQUIRED_R14_CHECKS)]
    return {
        "schema_version":1,
        "authority_origin":"EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant":False,
        "candidate_side_unittest_role":"NON_AUTHORITATIVE_DIAGNOSTIC_ONLY",
        "native_parent_process_initializes_python":False,
        "candidate_python_executes_only_in_forked_child":True,
        "candidate_commit":COMMIT,
        "candidate_tree":TREE,
        "environment_digest":ENV,
        "interpreter_contract_digest":INTERPRETER,
        "native_observer_source_git_blob_sha1":NATIVE_SOURCE,
        "native_observer_binary_sha256":NATIVE_BINARY,
        "native_observer_compiler_digest":COMPILER,
        "oracle_git_blob_sha1":ORACLE,
        "records":rows,
        "evidence_set_digest":digest({"record_digests":sorted(x["record_digest"] for x in rows)}),
        "scientific_execution_state":"CLOSED_PENDING_SUCCESSOR_REVIEW",
        "authority_effect":"NONE_EVIDENCE_ONLY",
    }


def reseal(b: dict, index: int = 0) -> None:
    row=b["records"][index]
    material=dict(row); material.pop("record_digest",None)
    row["record_digest"]=digest(material)
    b["evidence_set_digest"]=digest({"record_digests":sorted(x["record_digest"] for x in b["records"])})


class R14NativeObservationEvidenceTests(unittest.TestCase):
    def test_complete_bundle_binds_but_never_qualifies(self):
        r=validate_native_observation_evidence_bundle(bundle())
        self.assertTrue(r["valid"],r["problems"])
        self.assertFalse(r["qualified"])
        self.assertEqual(r["bound_check_count"],6)

    def test_native_parent_must_not_initialize_python(self):
        b=bundle(); b["native_parent_process_initializes_python"]=True
        r=validate_native_observation_evidence_bundle(b)
        self.assertIn("R14_NATIVE_PARENT_PYTHON_INITIALIZATION_FORBIDDEN",r["problems"])

    def test_candidate_pass_field_is_forbidden(self):
        b=bundle(); b["records"][0]["candidate_reported_pass"]=True; reseal(b)
        r=validate_native_observation_evidence_bundle(b)
        self.assertTrue(any("CANDIDATE_PASS_FIELD_FORBIDDEN" in x for x in r["problems"]))

    def test_python_observation_transport_is_rejected(self):
        b=bundle(); b["records"][0]["observation_transport"]="PYTHON_JSON_STDOUT"; reseal(b)
        r=validate_native_observation_evidence_bundle(b)
        self.assertTrue(any("OBSERVATION_TRANSPORT_INVALID" in x for x in r["problems"]))

    def test_missing_r13_regression_rejection_fails(self):
        b=bundle(); b["records"][0]["r13_tailored_frame_regression"]="NOT_RUN"; reseal(b)
        r=validate_native_observation_evidence_bundle(b)
        self.assertTrue(any("R13_REGRESSION_NOT_REJECTED" in x for x in r["problems"]))

    def test_native_binary_substitution_fails(self):
        b=bundle(); b["records"][0]["native_observer_binary_sha256"]="f"*64; reseal(b)
        r=validate_native_observation_evidence_bundle(b)
        self.assertTrue(any("NATIVE_BINARY_MISMATCH" in x for x in r["problems"]))

    def test_oracle_and_candidate_domains_must_differ(self):
        b=bundle(); b["records"][0]["oracle_control_domain"]=b["records"][0]["candidate_control_domain"]; reseal(b)
        r=validate_native_observation_evidence_bundle(b)
        self.assertTrue(any("ORACLE_NOT_INDEPENDENT" in x for x in r["problems"]))

    def test_name_only_records_fail_closed(self):
        b=bundle(); b["records"]=[{"check_id":x} for x in sorted(REQUIRED_R14_CHECKS)]; b["evidence_set_digest"]=digest({"record_digests":[]})
        r=validate_native_observation_evidence_bundle(b)
        self.assertFalse(r["valid"])
        self.assertTrue(any("DIGEST_INVALID" in x for x in r["problems"]))


if __name__=="__main__":
    unittest.main()
