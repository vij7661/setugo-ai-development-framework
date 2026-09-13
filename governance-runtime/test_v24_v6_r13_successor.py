from __future__ import annotations

import unittest

from v24_v6_governance_foundation import digest
from v24_v6_r13_successor import REQUIRED_ORACLE_CHECKS, validate_external_oracle_evidence_bundle

COMMIT="1"*40; TREE="2"*40; ENV="3"*64; INTERPRETER="4"*64; ORACLE="5"*40; OBSERVER="6"*40


def record(check_id: str) -> dict:
    r={
        "check_id":check_id,
        "challenge_digest":"7"*64,
        "request_digest":"8"*64,
        "observation_digest":"9"*64,
        "assertion_digest":"a"*64,
        "candidate_commit":COMMIT,
        "candidate_tree":TREE,
        "environment_digest":ENV,
        "interpreter_contract_digest":INTERPRETER,
        "oracle_git_blob_sha1":ORACLE,
        "observer_git_blob_sha1":OBSERVER,
        "run_id":"run-1",
        "round_id":"round-1",
        "candidate_process_role":"UNTRUSTED_OBSERVATION_ONLY",
        "oracle_decision_origin":"TRUSTED_EXTERNAL_ORACLE",
        "oracle_control_domain":"R13-EXTERNAL-ORACLE",
        "candidate_control_domain":"R13-CANDIDATE",
        "oracle_terminal_result":"PASS",
    }
    r["record_digest"]=digest(r)
    return r


def bundle() -> dict:
    rows=[record(x) for x in sorted(REQUIRED_ORACLE_CHECKS)]
    return {
        "schema_version":1,
        "authority_origin":"EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant":False,
        "candidate_side_unittest_role":"NON_AUTHORITATIVE_DIAGNOSTIC_ONLY",
        "candidate_commit":COMMIT,
        "candidate_tree":TREE,
        "environment_digest":ENV,
        "interpreter_contract_digest":INTERPRETER,
        "oracle_git_blob_sha1":ORACLE,
        "observer_git_blob_sha1":OBSERVER,
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


class R13ExternalOracleEvidenceTests(unittest.TestCase):
    def test_complete_external_oracle_bundle_binds_but_never_qualifies(self):
        r=validate_external_oracle_evidence_bundle(bundle())
        self.assertTrue(r["valid"],r["problems"]); self.assertFalse(r["qualified"])
        self.assertEqual(r["bound_check_count"],6)

    def test_candidate_unittest_cannot_be_authoritative(self):
        b=bundle(); b["candidate_side_unittest_role"]="QUALIFICATION_AUTHORITY"
        r=validate_external_oracle_evidence_bundle(b)
        self.assertIn("R13_CANDIDATE_UNITTEST_ROLE_INVALID",r["problems"])

    def test_candidate_pass_field_is_forbidden(self):
        b=bundle(); b["records"][0]["candidate_reported_pass"]=True; reseal(b)
        r=validate_external_oracle_evidence_bundle(b)
        self.assertTrue(any("CANDIDATE_PASS_FIELD_FORBIDDEN" in x for x in r["problems"]))

    def test_candidate_cannot_be_oracle_control_domain(self):
        b=bundle(); b["records"][0]["oracle_control_domain"]=b["records"][0]["candidate_control_domain"]; reseal(b)
        r=validate_external_oracle_evidence_bundle(b)
        self.assertTrue(any("ORACLE_NOT_INDEPENDENT" in x for x in r["problems"]))

    def test_name_only_record_is_rejected(self):
        b=bundle(); b["records"]=[{"check_id":x} for x in sorted(REQUIRED_ORACLE_CHECKS)]; b["evidence_set_digest"]=digest({"record_digests":[]})
        r=validate_external_oracle_evidence_bundle(b)
        self.assertFalse(r["valid"]); self.assertTrue(any("DIGEST_INVALID" in x for x in r["problems"]))

    def test_missing_check_fails_closed(self):
        b=bundle(); removed=b["records"].pop()["check_id"]; b["evidence_set_digest"]=digest({"record_digests":sorted(x["record_digest"] for x in b["records"])})
        r=validate_external_oracle_evidence_bundle(b)
        self.assertIn(f"R13_ORACLE_CHECK_MISSING:{removed}",r["problems"])

    def test_stale_candidate_binding_fails(self):
        b=bundle(); b["records"][0]["candidate_commit"]="f"*40; reseal(b)
        r=validate_external_oracle_evidence_bundle(b)
        self.assertTrue(any("COMMIT_MISMATCH" in x for x in r["problems"]))

    def test_candidate_decision_origin_fails(self):
        b=bundle(); b["records"][0]["oracle_decision_origin"]="CANDIDATE_PROCESS"; reseal(b)
        r=validate_external_oracle_evidence_bundle(b)
        self.assertTrue(any("DECISION_ORIGIN_INVALID" in x for x in r["problems"]))


if __name__=="__main__": unittest.main()
