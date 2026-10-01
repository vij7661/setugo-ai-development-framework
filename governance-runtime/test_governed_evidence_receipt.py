from __future__ import annotations
import copy,io,json,unittest,zipfile
from unittest.mock import Mock
from candidate_execution_evidence import build_statement
from governed_evidence_receipt import git_blob_sha1,ingest_verified_receipt,sha256_bytes
B="b"*40;C="c"*40;T="d"*40;REF="frozen/q18";REPO="vij7661/setugo-ai-development-framework";VC="e"*40;VT="f"*40;ER="evidence/q17"
def raw(v):return (json.dumps(v,sort_keys=True)+"\n").encode()
def archive(members):
 out=io.BytesIO()
 with zipfile.ZipFile(out,"w") as z:
  for name,value in members:z.writestr(name,value)
 return out.getvalue()
def fixtures():
 payloads={"linux":b"linux evidence tar","packet":b"immutable packet"};statements={};archives={};rows={}
 meta={"linux":("11","12","13",".github/workflows/linux.yml","linux-validation","linux-statement.json","Q18-LINUX-EVIDENCE.tar","LINUX_VALIDATION","SUCCESS"),"packet":("21","22","23",".github/workflows/packet.yml","packet-generation","packet-statement.json","review-packet.tar","REVIEW_PACKET","GENERATED")}
 for name,(run,job,artifact,wf,wid,sp,pp,kind,conclusion) in meta.items():
  statement=build_statement(kind=kind,run_id=run,job_id=job,workflow_identity=wid,baseline_commit=B,candidate_commit=C,candidate_tree=T,changed_file_count=88,conclusion=conclusion,artifact_digest="sha256:"+sha256_bytes(payloads[name]));sr=raw(statement);ar=archive([(sp,sr),(pp,payloads[name])]);statements[name]=statement;archives[name]=ar
  rows[name]={"run_id":run,"job_id":job,"workflow_file":wf,"workflow_identity":wid,"artifact_id":artifact,"archive_digest":"sha256:"+sha256_bytes(ar),"archive_raw_sha256":"sha256:"+sha256_bytes(ar),"payload_member_path":pp,"payload_member_sha256":"sha256:"+sha256_bytes(payloads[name]),"payload_member_bytes":len(payloads[name]),"statement_member_path":sp,"statement_raw_sha256":"sha256:"+sha256_bytes(sr),"statement_internal_sha256":"sha256:"+statement["statement_sha256"]}
 freeze={"schema":"r8-external-freeze-attestation/v2","candidate_commit":C,"candidate_tree":T,"frozen_ref":REF,"linux_validation_statement":statements["linux"],"review_packet_statement":statements["packet"],"authority_effect":"NONE","fallback_to_3":"ACTIVE","six_slice_cadence":"NOT_RESTORED","attestation_state":"FROZEN_VERIFIED"};fr=raw(freeze);review=b"review bytes\n"
 receipt={"schema":"r8-governed-evidence-receipt/v2","repository":REPO,"candidate":{"baseline":B,"commit":C,"tree":T,"changed_file_count":88,"frozen_ref":REF},**rows,"freeze_attestation":{"raw_sha256":sha256_bytes(fr),"git_blob":git_blob_sha1(fr)},"independent_review":{"original_upload_raw_sha256":sha256_bytes(review),"committed_review_sha256":sha256_bytes(review),"git_blob":git_blob_sha1(review)},"review_source":{"repository":REPO,"revision":"a"*40,"path":"review.txt"},"trusted_code":{"verifier_commit":VC,"verifier_tree":VT,"evidence_ref":ER},"authority_effect":"NONE"}
 return receipt,{"freeze_attestation":fr,"independent_review":review},archives
def api_for(receipt,archives):
 api=Mock();api.resolve_ref.return_value=C
 api.run.side_effect=[{"id":11,"workflow_file":receipt["linux"]["workflow_file"],"conclusion":"success"},{"id":21,"workflow_file":receipt["packet"]["workflow_file"],"conclusion":"success"}]
 api.job.side_effect=[{"id":12,"run_id":11,"workflow_identity":receipt["linux"]["workflow_identity"],"conclusion":"success"},{"id":22,"run_id":21,"workflow_identity":receipt["packet"]["workflow_identity"],"conclusion":"success"}]
 api.artifact.side_effect=[{"id":13,"run_id":11,"digest":receipt["linux"]["archive_digest"],"archive_download_url":"u1"},{"id":23,"run_id":21,"digest":receipt["packet"]["archive_digest"],"archive_download_url":"u2"}]
 api.download_artifact.side_effect=[archives["linux"],archives["packet"]];api.git_blob.side_effect=[receipt["freeze_attestation"]["git_blob"],receipt["independent_review"]["git_blob"]];api.git_blob_bytes.return_value=b"review bytes\n";return api
LOC={"freeze_attestation":{"revision":"e","path":"freeze.json"},"independent_review":{"revision":"a"*40,"path":"review.txt"}}
def ingest(receipt,blobs,archives):return ingest_verified_receipt(receipt,api_for(receipt,archives),blobs,artifact_locations=LOC,trusted_verifier_commit=VC,trusted_verifier_tree=VT,evidence_ref=ER)
class Tests(unittest.TestCase):
 def test_v2_binds_run_job_archive_statement_and_member(self):
  receipt,blobs,archives=fixtures();self.assertEqual(ingest(receipt,blobs,archives),receipt)
 def test_cross_identity_and_archive_member_confusion_fail(self):
  for mutation in ("run_id","job_id","workflow_identity","payload_member_sha256","archive_digest"):
   receipt,blobs,archives=fixtures();receipt["linux"][mutation]="99" if mutation.endswith("id") else "sha256:"+"9"*64 if "digest" in mutation or "sha256" in mutation else "wrong"
   with self.assertRaises(ValueError):ingest(receipt,blobs,archives)
 def test_traversal_backslash_and_duplicate_members_fail(self):
  for member in ("../linux-statement.json","dir\\linux-statement.json"):
   receipt,blobs,archives=fixtures();archives["linux"]=archive([(member,b"x"),(receipt["linux"]["payload_member_path"],b"x")]);receipt["linux"]["archive_digest"]=receipt["linux"]["archive_raw_sha256"]="sha256:"+sha256_bytes(archives["linux"])
   with self.assertRaises(ValueError):ingest(receipt,blobs,archives)
  receipt,blobs,archives=fixtures();out=io.BytesIO()
  with zipfile.ZipFile(out,"w") as z:
   z.writestr(receipt["linux"]["statement_member_path"],b"x");z.writestr(receipt["linux"]["statement_member_path"],b"y");z.writestr(receipt["linux"]["payload_member_path"],b"z")
  archives["linux"]=out.getvalue();receipt["linux"]["archive_digest"]=receipt["linux"]["archive_raw_sha256"]="sha256:"+sha256_bytes(archives["linux"])
  with self.assertRaises(ValueError):ingest(receipt,blobs,archives)
 def test_v1_and_trusted_code_substitution_fail(self):
  receipt,blobs,archives=fixtures();old=copy.deepcopy(receipt);old["schema"]="r8-governed-evidence-receipt/v1"
  with self.assertRaises(ValueError):ingest(old,blobs,archives)
  with self.assertRaises(ValueError):ingest_verified_receipt(receipt,api_for(receipt,archives),blobs,artifact_locations=LOC,trusted_verifier_commit="0"*40,trusted_verifier_tree=VT,evidence_ref=ER)
 def test_three_review_provenance_identities_are_distinct_and_load_bearing(self):
  receipt,blobs,archives=fixtures()
  for field in ("committed_review_sha256","git_blob"):
   bad=copy.deepcopy(receipt);bad["independent_review"][field]="0"*len(bad["independent_review"][field])
   with self.assertRaises(ValueError):ingest(bad,blobs,archives)
  bad=copy.deepcopy(blobs);bad["independent_review"]=b"different original bytes"
  with self.assertRaises(ValueError):ingest(receipt,bad,archives)
if __name__=="__main__":unittest.main()
