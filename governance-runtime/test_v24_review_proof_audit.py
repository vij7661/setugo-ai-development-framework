from __future__ import annotations
import unittest
from v24_review_proof_audit import build_audit_record,build_reviewer_safe_proof

def proof_bundle():
 return {"proof_manifest_state":"QUALIFIED","mandatory_fields":[{"field_id":"F-U","source_binding":"SRC-U","redaction_class":"VISIBLE"},{"field_id":"F-CRED","source_binding":"SRC-CRED","redaction_class":"SECRET_SAFE_IDENTITY_ONLY"}],"source_values":{"SRC-U":{"identity":"U-1","state":"CURRENT"},"SRC-CRED":{"identity":"cred-1","version":"v2","state":"CURRENT","qualification_result":"QUALIFIED","secret":"never expose"}},"clean_review_context":{"candidate_commit":"abc","review_scope":"V24-I10"},"completeness_subject_results":[{"subject_id":"SUB-U","classification":"COMPLETE_BY_INDEPENDENT_DERIVATION","evidence_refs":["ev-1"],"load_bearing":True}]}
def audit_bundle():
 return {"candidate_commit":"abc","governance_generation_id":"GEN-V24","decision_digest":"d"*64,"application_record_digest":"a"*64,"admission_ledger_digest":"l"*64,"completeness_ledger_digest":"c"*64,"normative_catalog_digest":"n"*64,"endpoint_precedence_digest":"e"*64,"proof_view_digest":"p"*64,"historical_failures_preserved":True,"authority_effect":"NONE_EVIDENCE_ONLY"}
class ProofAuditTests(unittest.TestCase):
 def test_positive_proof_is_non_authoritative_and_secret_safe(self):
  r=build_reviewer_safe_proof(proof_bundle());self.assertEqual(r["state"],"REVIEWER_SAFE_PROOF_READY");self.assertEqual(r["problems"],[]);self.assertFalse(r["qualified"]);self.assertNotIn("secret",r["proof"]["mandatory_fields"]["F-CRED"])
 def test_missing_mandatory_field_visible(self):
  b=proof_bundle();b["source_values"].pop("SRC-U");self.assertIn("PROOF_MANDATORY_FIELD_NOT_PRESENT:F-U",build_reviewer_safe_proof(b)["problems"])
 def test_prior_review_finding_contamination_blocks_clean_context(self):
  b=proof_bundle();b["clean_review_context"]["prior_reviewer_findings"]=["x"];self.assertIn("CLEAN_REVIEW_CONTAMINATION:prior_reviewer_findings",build_reviewer_safe_proof(b)["problems"])
 def test_load_bearing_insufficient_evidence_blocks(self):
  b=proof_bundle();b["completeness_subject_results"][0]["classification"]="INSUFFICIENT_EVIDENCE";self.assertIn("LOAD_BEARING_COMPLETENESS_REVIEW_BLOCKING",build_reviewer_safe_proof(b)["problems"])
 def test_unqualified_proof_manifest_blocks(self):
  b=proof_bundle();b["proof_manifest_state"]="COMPILED";self.assertIn("PROOF_VIEW_APPLICABILITY_INCOMPLETE",build_reviewer_safe_proof(b)["problems"])
 def test_audit_positive_non_authoritative(self):
  r=build_audit_record(audit_bundle());self.assertEqual(r["state"],"AUDIT_RECORD_READY");self.assertEqual(r["problems"],[]);self.assertFalse(r["qualified"])
 def test_audit_requires_application_binding(self):
  b=audit_bundle();b.pop("application_record_digest");self.assertIn("AUDIT_BINDING_REQUIRED:application_record_digest",build_audit_record(b)["problems"])
 def test_audit_preserves_failure_history(self):
  b=audit_bundle();b["historical_failures_preserved"]=False;self.assertIn("AUDIT_HISTORICAL_FAILURE_PRESERVATION_REQUIRED",build_audit_record(b)["problems"])
 def test_audit_cannot_grant_authority(self):
  b=audit_bundle();b["authority_effect"]="GRANT";self.assertIn("AUDIT_RECORD_CANNOT_GRANT_AUTHORITY",build_audit_record(b)["problems"])
if __name__=="__main__":unittest.main()
