from __future__ import annotations
import unittest
from v24_review_proof_audit import dg,build_audit_record,build_reviewer_safe_proof
def proof_bundle():
 catalog=[{"subject_id":"SUB-U","load_bearing":True,"source_kind":"AUTHORITATIVE_SUBJECT_CATALOG","evidence_digest":"s"*64,"candidate_self_derived":False}]
 return {"proof_manifest_state":"QUALIFIED","mandatory_fields":[{"field_id":"F-U","source_binding":"SRC-U","redaction_class":"VISIBLE"},{"field_id":"F-CRED","source_binding":"SRC-CRED","redaction_class":"SECRET_SAFE_IDENTITY_ONLY"}],"source_values":{"SRC-U":{"identity":"U-1","state":"CURRENT"},"SRC-CRED":{"identity":"cred-1","version":"v2","state":"CURRENT","qualification_result":"QUALIFIED","secret":"never expose"}},"clean_review_context":{"candidate_commit":"abc","review_scope":"V24-I10"},"completeness_subject_catalog":catalog,"completeness_subject_catalog_digest":dg(catalog),"completeness_subject_results":[{"subject_id":"SUB-U","classification":"COMPLETE_BY_INDEPENDENT_DERIVATION","evidence_refs":["ev-1"],"load_bearing":False}]}
def audit_bundle():
 failures=[{"failure_id":"FAIL-1","state":"PRESERVED","record_digest":"f"*64,"evidence_ref":"review/v24/failure-1.json"}]
 return {"candidate_commit":"abc","governance_generation_id":"GEN-V24","decision_digest":"d"*64,"application_record_digest":"a"*64,"admission_ledger_digest":"l"*64,"completeness_ledger_digest":"c"*64,"normative_catalog_digest":"n"*64,"endpoint_precedence_digest":"e"*64,"proof_view_digest":"p"*64,"historical_failures_preserved":True,"historical_failure_records":failures,"historical_failure_set_digest":dg(failures),"authority_effect":"NONE_EVIDENCE_ONLY"}
class ProofAuditTests(unittest.TestCase):
 def test_positive_proof_is_non_authoritative_and_secret_safe(self):
  r=build_reviewer_safe_proof(proof_bundle());self.assertEqual(r["state"],"REVIEWER_SAFE_PROOF_READY");self.assertEqual(r["problems"],[]);self.assertFalse(r["qualified"]);self.assertNotIn("secret",r["proof"]["mandatory_fields"]["F-CRED"])
 def test_missing_mandatory_field_visible(self):
  b=proof_bundle();b["source_values"].pop("SRC-U");self.assertIn("PROOF_MANDATORY_FIELD_NOT_PRESENT:F-U",build_reviewer_safe_proof(b)["problems"])
 def test_prior_review_finding_contamination_blocks_clean_context(self):
  b=proof_bundle();b["clean_review_context"]["prior_reviewer_findings"]=["x"];self.assertIn("CLEAN_REVIEW_CONTAMINATION:prior_reviewer_findings",build_reviewer_safe_proof(b)["problems"])
 def test_load_bearing_insufficient_evidence_blocks_even_if_caller_says_false(self):
  b=proof_bundle();b["completeness_subject_results"][0].update({"classification":"INSUFFICIENT_EVIDENCE","load_bearing":False});self.assertIn("LOAD_BEARING_COMPLETENESS_REVIEW_BLOCKING",build_reviewer_safe_proof(b)["problems"])
 def test_subject_catalog_cannot_be_self_derived(self):
  b=proof_bundle();b["completeness_subject_catalog"][0]["candidate_self_derived"]=True;b["completeness_subject_catalog_digest"]=dg(b["completeness_subject_catalog"]);self.assertIn("COMPLETENESS_SUBJECT_CATALOG_SELF_DERIVED_FORBIDDEN:SUB-U",build_reviewer_safe_proof(b)["problems"])
 def test_unknown_subject_cannot_create_non_load_bearing_escape(self):
  b=proof_bundle();b["completeness_subject_results"][0]["subject_id"]="UNKNOWN";self.assertIn("COMPLETENESS_REVIEW_SUBJECT_UNDERIVED:UNKNOWN",build_reviewer_safe_proof(b)["problems"])
 def test_unqualified_proof_manifest_blocks(self):
  b=proof_bundle();b["proof_manifest_state"]="COMPILED";self.assertIn("PROOF_VIEW_APPLICABILITY_INCOMPLETE",build_reviewer_safe_proof(b)["problems"])
 def test_audit_positive_non_authoritative(self):
  r=build_audit_record(audit_bundle());self.assertEqual(r["state"],"AUDIT_RECORD_READY");self.assertEqual(r["problems"],[]);self.assertFalse(r["qualified"]);self.assertTrue(r["record"]["historical_failures_preserved"])
 def test_audit_requires_application_binding(self):
  b=audit_bundle();b.pop("application_record_digest");self.assertIn("AUDIT_BINDING_REQUIRED:application_record_digest",build_audit_record(b)["problems"])
 def test_audit_boolean_cannot_substitute_for_history(self):
  b=audit_bundle();b["historical_failure_records"]=[];b["historical_failure_set_digest"]=dg([]);b["historical_failures_preserved"]=True;self.assertIn("AUDIT_HISTORICAL_FAILURE_RECORDS_REQUIRED",build_audit_record(b)["problems"])
 def test_audit_failure_history_digest_must_bind_records(self):
  b=audit_bundle();b["historical_failure_set_digest"]="bad";self.assertIn("AUDIT_HISTORICAL_FAILURE_SET_DIGEST_INVALID",build_audit_record(b)["problems"])
 def test_audit_cannot_grant_authority(self):
  b=audit_bundle();b["authority_effect"]="GRANT";self.assertIn("AUDIT_RECORD_CANNOT_GRANT_AUTHORITY",build_audit_record(b)["problems"])
if __name__=="__main__":unittest.main()
