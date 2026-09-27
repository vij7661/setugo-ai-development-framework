from __future__ import annotations
import copy, json, tempfile, unittest
from pathlib import Path
from unittest.mock import Mock
from candidate_execution_evidence import build_statement
from freeze_attestation import canonical_sha256
from governed_evidence_receipt import git_blob_sha1, ingest_verified_receipt, sha256_bytes, verify_receipt_files

B="b"*40; C="c"*40; T="d"*40; REF="frozen/q16"; REPO="vij7661/setugo-ai-development-framework"
def raw(v): return (json.dumps(v,sort_keys=True)+"\n").encode()
def fixtures():
    linux=build_statement(kind="LINUX_VALIDATION",run_id="11",job_id="12",workflow_identity="linux.yml/job",baseline_commit=B,candidate_commit=C,candidate_tree=T,changed_file_count=61,conclusion="SUCCESS",artifact_digest="sha256:"+"1"*64)
    packet=build_statement(kind="REVIEW_PACKET",run_id="21",job_id="22",workflow_identity="packet.yml/job",baseline_commit=B,candidate_commit=C,candidate_tree=T,changed_file_count=61,conclusion="GENERATED",artifact_digest="sha256:"+"2"*64)
    freeze={"schema":"r8-external-freeze-attestation/v2","candidate_commit":C,"candidate_tree":T,"frozen_ref":REF,"linux_validation_statement":linux,"review_packet_statement":packet,"authority_effect":"NONE","fallback_to_3":"ACTIVE","six_slice_cadence":"NOT_RESTORED","attestation_state":"FROZEN_VERIFIED"}
    review=b"exact independent review bytes\n"; payload=b"packet payload"; la=b"linux artifact"; pa=b"packet artifact"
    blobs={"linux_artifact":la,"packet_artifact":pa,"linux_statement":raw(linux),"packet_statement":raw(packet),"packet_payload":payload,"freeze_attestation":raw(freeze),"independent_review":review}
    receipt={"schema":"r8-governed-evidence-receipt/v1","repository":REPO,"candidate":{"baseline":B,"commit":C,"tree":T,"changed_file_count":61,"frozen_ref":REF},"linux":{"run_id":"11","job_id":"12","workflow_identity":"linux.yml/job","artifact_id":"13","artifact_digest":"sha256:"+sha256_bytes(la),"statement_raw_sha256":"sha256:"+sha256_bytes(raw(linux)),"statement_internal_sha256":"sha256:"+linux["statement_sha256"]},"packet":{"run_id":"21","job_id":"22","workflow_identity":"packet.yml/job","artifact_id":"23","artifact_digest":"sha256:"+sha256_bytes(pa),"payload_sha256":"sha256:"+sha256_bytes(payload),"statement_raw_sha256":"sha256:"+sha256_bytes(raw(packet)),"statement_internal_sha256":"sha256:"+packet["statement_sha256"]},"freeze_attestation":{"raw_sha256":sha256_bytes(raw(freeze)),"git_blob":git_blob_sha1(raw(freeze))},"independent_review":{"raw_sha256":sha256_bytes(review),"git_blob":git_blob_sha1(review)},"authority_effect":"NONE"}
    return receipt,linux,packet,freeze,review,payload,blobs

class Tests(unittest.TestCase):
    def test_mocked_github_associations_anchor_receipt(self):
        receipt,*_,blobs=fixtures(); api=Mock(); api.resolve_ref.return_value=C
        api.run.side_effect=[{"id":11,"workflow_identity":"linux.yml/job","conclusion":"success"},{"id":21,"workflow_identity":"packet.yml/job","conclusion":"success"}]
        api.job.side_effect=[{"id":12,"run_id":11,"workflow_identity":"linux.yml/job","conclusion":"success"},{"id":22,"run_id":21,"workflow_identity":"packet.yml/job","conclusion":"success"}]
        api.artifact.side_effect=[{"id":13,"run_id":11,"digest":receipt["linux"]["artifact_digest"]},{"id":23,"run_id":21,"digest":receipt["packet"]["artifact_digest"]}]
        api.git_blob.side_effect=[receipt["freeze_attestation"]["git_blob"],receipt["independent_review"]["git_blob"]]
        self.assertEqual(ingest_verified_receipt(receipt,api,blobs,artifact_locations={"freeze_attestation":{"revision":"evidence","path":"freeze.json"},"independent_review":{"revision":"review","path":"review.txt"}}),receipt)
        bad=copy.deepcopy(receipt); bad["linux"]["run_id"]="99"
        api.run.side_effect=None; api.run.return_value={"id":11,"workflow_identity":"linux.yml/job","conclusion":"success"}; api.job.side_effect=None; api.job.return_value={"id":12,"run_id":11,"workflow_identity":"linux.yml/job","conclusion":"success"}; api.artifact.side_effect=None; api.artifact.return_value={"id":13,"run_id":11,"digest":receipt["linux"]["artifact_digest"]}
        with self.assertRaises(ValueError): ingest_verified_receipt(bad,api,blobs,artifact_locations={"freeze_attestation":{"revision":"e","path":"f"},"independent_review":{"revision":"r","path":"i"}})

    def test_exact_review_bytes_and_all_bound_files(self):
        receipt,linux,packet,freeze,review,payload,_=fixtures()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); paths=[]
            for name,data in (("linux",raw(linux)),("packet",raw(packet)),("freeze",raw(freeze)),("review",review),("payload",payload)):
                p=root/name; p.write_bytes(data); paths.append(p)
            self.assertTrue(verify_receipt_files(receipt,linux_statement_path=paths[0],packet_statement_path=paths[1],freeze_attestation_path=paths[2],review_path=paths[3],packet_payload_path=paths[4]))
            paths[3].write_bytes(review+b"different")
            self.assertFalse(verify_receipt_files(receipt,linux_statement_path=paths[0],packet_statement_path=paths[1],freeze_attestation_path=paths[2],review_path=paths[3],packet_payload_path=paths[4]))

if __name__=="__main__": unittest.main()
