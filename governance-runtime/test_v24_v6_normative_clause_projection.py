from __future__ import annotations

import copy
import unittest

from v24_v6_governance_foundation import CURRENT, QUALIFIED, INSUFFICIENT_EVIDENCE
from v24_v6_normative_clause_projection import (
    MATERIAL_NORMATIVE,
    PROVEN_NON_NORMATIVE,
    REFERENCE_ONLY,
    SUPERSEDED,
    canonical_authority_set_content_digest,
    canonical_catalog_control_binding_digest,
    canonical_disposition_content_digest,
    canonical_parser_content_digest,
    construction_frontier,
    enumerate_markdown_structural_candidates,
    qualify_normative_dispositions,
    validate_catalog_candidate_coverage,
)
from v24_v6_test_proof_context import build_test_proof_context

D1="1"*64;D2="2"*64;D3="3"*64;D4="4"*64;D5="5"*64;D6="6"*64
PARSER_ID="NORMATIVE-PARSER-1";PROJECTION_ID="NORMATIVE-PROJECTION-1"
AUTHORITY_ID="NORMATIVE-DISPOSITION-AUTHORITY-1";DISPOSITION_SET_ID="NORMATIVE-DISPOSITION-SET-1"

TEXT=(
    "# Standard\n\n"
    "Introductory context.\n\n"
    "## Control A\n\n"
    "A system must deny an unqualified request.\n\n"
    "Supporting explanation only.\n\n"
    "## Control B\n\n"
    "A second control applies.\n"
)


def projection(text=TEXT):
    return enumerate_markdown_structural_candidates(
        artifact_bytes=text.encode("utf-8"),
        artifact_path="standards/example.md",
        parser_profile_id="MD-STRUCTURAL-V1",
    )


# Legacy opaque-label fixtures intentionally retained for the permanent R5 RED.
def parser_descriptor():
    return {
        "parser_profile_id":"MD-STRUCTURAL-V1",
        "implementation_content_digest":D1,
        "rule_digest":D2,
        "qualification_state":QUALIFIED,
        "independence_state":QUALIFIED,
        "currentness_result":CURRENT,
    }


def authority_set():
    return {
        "qualification_state":QUALIFIED,
        "qualification_digest":D3,
        "currentness_result":CURRENT,
        "independence_state":QUALIFIED,
        "threshold":2,
        "member_ids":["REV-A","REV-B"],
        "member_control_domain_ids":["DOMAIN-A","DOMAIN-B"],
    }


def disposition_for(candidate,value,evidence=D4):
    record={
        "candidate_clause_id":candidate["candidate_clause_id"],
        "artifact_sha256":candidate["artifact_sha256"],
        "candidate_span_digest":candidate["exact_text_sha256"],
        "authority_set_qualification_digest":D3,
        "approver_ids":["REV-A","REV-B"],
        "approver_control_domain_ids":["DOMAIN-A","DOMAIN-B"],
        "evidence_digests":[evidence],
        "currentness_result":CURRENT,
        "disposition":value,
    }
    if value==SUPERSEDED:
        record["successor_control_id"]="CTRL-SUCCESSOR"
    return record


def qualified_disposition_bundle(text=TEXT):
    p=projection(text);records=[];normative_done=False
    for candidate in p["candidates"]:
        if candidate["kind"]=="BODY_BLOCK" and "must deny" in candidate["exact_text"] and not normative_done:
            records.append(disposition_for(candidate,MATERIAL_NORMATIVE));normative_done=True
        elif candidate["kind"]=="HEADING":
            records.append(disposition_for(candidate,REFERENCE_ONLY))
        else:
            records.append(disposition_for(candidate,PROVEN_NON_NORMATIVE))
    return {
        "projection":p,
        "parser_descriptor":parser_descriptor(),
        "expected_artifact_sha256":p["artifact_sha256"],
        "expected_artifact_git_blob_sha1":p["artifact_git_blob_sha1"],
        "disposition_authority_set":authority_set(),
        "artifact_owner_control_domain_id":"ARTIFACT-OWNER",
        "catalog_owner_control_domain_id":"CATALOG-OWNER",
        "dispositions":records,
    }


def _parser_base():
    parser={
        "parser_id":PARSER_ID,
        "parser_profile_id":"MD-STRUCTURAL-V1",
        "implementation_content_digest":D1,
        "rule_digest":D2,
        "qualification_state":QUALIFIED,
        "independence_state":QUALIFIED,
        "currentness_result":CURRENT,
    }
    parser["parser_content_digest"]=canonical_parser_content_digest(parser)
    return parser


def _authority_base():
    authority={
        "authority_set_id":AUTHORITY_ID,
        "qualification_state":QUALIFIED,
        "currentness_result":CURRENT,
        "independence_state":QUALIFIED,
        "threshold":2,
        "member_ids":["REV-A","REV-B"],
        "member_control_domain_ids":["DOMAIN-A","DOMAIN-B"],
    }
    authority["authority_set_content_digest"]=canonical_authority_set_content_digest(authority)
    return authority


def _value_for(candidate):
    if candidate["kind"]=="BODY_BLOCK" and "must deny" in candidate["exact_text"]:
        return MATERIAL_NORMATIVE
    if candidate["kind"]=="HEADING":
        return REFERENCE_ONLY
    return PROVEN_NON_NORMATIVE


def _draft_disposition(candidate,index,authority_q):
    record={
        "disposition_record_id":f"DISPOSITION-{index}",
        "candidate_clause_id":candidate["candidate_clause_id"],
        "artifact_sha256":candidate["artifact_sha256"],
        "candidate_span_digest":candidate["exact_text_sha256"],
        "authority_set_id":AUTHORITY_ID,
        "authority_set_qualification_digest":authority_q,
        "approver_ids":["REV-A","REV-B"],
        "approver_control_domain_ids":["DOMAIN-A","DOMAIN-B"],
        "evidence_digests":[D4],
        "currentness_result":CURRENT,
        "disposition":_value_for(candidate),
    }
    record["disposition_content_digest"]=canonical_disposition_content_digest(record)
    return record


def proof_closed_disposition_fixture(text=TEXT):
    p=projection(text);parser=_parser_base();authority=_authority_base()
    primitive={
        "parser_q":{"kind":"QUALIFICATION","subject_id":PARSER_ID,"content_digest":parser["parser_content_digest"]},
        "parser_i":{"kind":"INDEPENDENCE","subject_identity_id":PARSER_ID},
        "parser_c":{"kind":"CURRENTNESS","source_id":PARSER_ID,"source_digest":parser["parser_content_digest"]},
        "projection_q":{"kind":"QUALIFICATION","subject_id":PROJECTION_ID,"content_digest":p["projection_digest"]},
        "authority_q":{"kind":"QUALIFICATION","subject_id":AUTHORITY_ID,"content_digest":authority["authority_set_content_digest"]},
        "authority_i":{"kind":"INDEPENDENCE","subject_identity_id":AUTHORITY_ID},
        "authority_c":{"kind":"CURRENTNESS","source_id":AUTHORITY_ID,"source_digest":authority["authority_set_content_digest"]},
    }
    _,_,refs1=build_test_proof_context(primitive)
    drafts=[_draft_disposition(candidate,index,refs1["authority_q"]) for index,candidate in enumerate(p["candidates"],1)]
    specs=dict(primitive)
    for index,record in enumerate(drafts,1):
        specs[f"disp_{index}_q"]={"kind":"QUALIFICATION","subject_id":record["disposition_record_id"],"content_digest":record["disposition_content_digest"]}
        specs[f"disp_{index}_c"]={"kind":"CURRENTNESS","source_id":record["disposition_record_id"],"source_digest":record["disposition_content_digest"]}
    context,boundary,refs=build_test_proof_context(specs)
    parser.update({
        "qualification_digest":refs["parser_q"],
        "independence_qualification_digest":refs["parser_i"],
        "currentness_binding_digest":refs["parser_c"],
    })
    authority.update({
        "qualification_digest":refs["authority_q"],
        "independence_qualification_digest":refs["authority_i"],
        "currentness_binding_digest":refs["authority_c"],
    })
    records=[]
    for index,record in enumerate(drafts,1):
        item=dict(record)
        item["authority_set_qualification_digest"]=refs["authority_q"]
        item["disposition_content_digest"]=canonical_disposition_content_digest(item)
        item["disposition_qualification_digest"]=refs[f"disp_{index}_q"]
        item["currentness_binding_digest"]=refs[f"disp_{index}_c"]
        records.append(item)
    bundle={
        "projection":p,
        "projection_id":PROJECTION_ID,
        "projection_qualification_digest":refs["projection_q"],
        "parser_descriptor":parser,
        "expected_artifact_sha256":p["artifact_sha256"],
        "expected_artifact_git_blob_sha1":p["artifact_git_blob_sha1"],
        "disposition_authority_set":authority,
        "artifact_owner_control_domain_id":"ARTIFACT-OWNER",
        "catalog_owner_control_domain_id":"CATALOG-OWNER",
        "dispositions":records,
    }
    return bundle,context,boundary,specs


def disposition_result(text=TEXT):
    bundle,context,boundary,specs=proof_closed_disposition_fixture(text)
    result=qualify_normative_dispositions(bundle,proof_context=context,trusted_boundary=boundary)
    return bundle,context,boundary,specs,result


def coverage_fixture(descriptors=None):
    bundle,_,_,specs,result=disposition_result()
    assert result["qualified"],result["problems"]
    extended=dict(specs)
    extended["disposition_set_q"]={"kind":"QUALIFICATION","subject_id":DISPOSITION_SET_ID,"content_digest":result["disposition_digest"]}
    if descriptors is None:
        mid=result["material_candidate_ids"][0]
        span=next(x["candidate_span_digest"] for x in result["disposition_binding_material"]["candidate_span_digests"] if x["candidate_clause_id"]==mid)
        descriptors=[{
            "control_id":"CTRL-A",
            "candidate_clause_id":mid,
            "artifact_sha256":result["disposition_binding_material"]["artifact_sha256"],
            "normative_artifact_blob_sha":result["disposition_binding_material"]["artifact_git_blob_sha1"],
            "candidate_span_digest":span,
        }]
    descriptors=[dict(d) for d in descriptors]
    for index,descriptor in enumerate(descriptors,1):
        descriptor.setdefault("control_binding_id",f"CLAUSE-CONTROL-BINDING-{index}")
        descriptor["control_binding_content_digest"]=canonical_catalog_control_binding_digest(descriptor)
        extended[f"control_binding_{index}_q"]={"kind":"QUALIFICATION","subject_id":descriptor["control_binding_id"],"content_digest":descriptor["control_binding_content_digest"]}
    context,boundary,refs=build_test_proof_context(extended)
    # Earlier proof refs remain deterministic when binding proofs are appended.
    result=qualify_normative_dispositions(bundle,proof_context=context,trusted_boundary=boundary)
    assert result["qualified"],result["problems"]
    for index,descriptor in enumerate(descriptors,1):
        descriptor["control_binding_qualification_digest"]=refs[f"control_binding_{index}_q"]
        descriptor["control_binding_qualification_state"]=QUALIFIED
    coverage={
        "disposition_set_id":DISPOSITION_SET_ID,
        "disposition_digest":result["disposition_digest"],
        "disposition_qualification_digest":refs["disposition_set_q"],
        "disposition_qualification_state":QUALIFIED,
        "disposition_binding_material":result["disposition_binding_material"],
        "material_candidate_ids":result["material_candidate_ids"],
        "artifact_sha256":result["disposition_binding_material"]["artifact_sha256"],
        "artifact_git_blob_sha1":result["disposition_binding_material"]["artifact_git_blob_sha1"],
        "catalog_descriptors":descriptors,
    }
    return coverage,context,boundary,result


class R5NormativeProjectionTests(unittest.TestCase):
    def test_frontier_non_authoritative(self):
        r=construction_frontier();self.assertFalse(r["qualified"]);self.assertEqual(r["authority_effect"],"NONE_EVIDENCE_ONLY")

    def test_structural_projection_is_deterministic(self):
        a=projection();b=projection();self.assertTrue(a["qualified"],a["problems"]);self.assertEqual(a["projection_digest"],b["projection_digest"]);self.assertEqual(a["candidate_set_digest"],b["candidate_set_digest"])

    def test_new_generic_prose_becomes_new_structural_candidate(self):
        a=projection();changed=TEXT.replace("Supporting explanation only.\n\n","Supporting explanation only.\n\nAn additional requirement applies to all authoritative decisions.\n\n");b=projection(changed)
        self.assertGreater(len(b["candidates"]),len(a["candidates"]));self.assertNotEqual(a["candidate_set_digest"],b["candidate_set_digest"])

    def test_projection_does_not_use_catalog_locator_input(self):
        p=projection();self.assertNotIn("required_clause_locators",p);self.assertTrue(any(c["kind"]=="BODY_BLOCK" for c in p["candidates"]))

    def test_proof_closed_normative_dispositions_qualify(self):
        _,_,_,_,result=disposition_result();self.assertTrue(result["qualified"],result["problems"]);self.assertEqual(len(result["material_candidate_ids"]),1)

    def test_exact_artifact_sha_binding_required(self):
        b,c,t,_=proof_closed_disposition_fixture();b["expected_artifact_sha256"]=D5
        r=qualify_normative_dispositions(b,proof_context=c,trusted_boundary=t);self.assertIn("NORMATIVE_ARTIFACT_SHA256_BINDING_MISMATCH",r["problems"])

    def test_parser_must_be_qualified_independent_current(self):
        b,c,t,_=proof_closed_disposition_fixture();b["parser_descriptor"]["independence_state"]="CONFLICT"
        r=qualify_normative_dispositions(b,proof_context=c,trusted_boundary=t);self.assertIn("NORMATIVE_PARSER_NOT_INDEPENDENT",r["problems"])

    def test_parser_proof_subject_mismatch_blocks(self):
        b,c,t,_=proof_closed_disposition_fixture();b["parser_descriptor"]["parser_id"]="OTHER-PARSER"
        r=qualify_normative_dispositions(b,proof_context=c,trusted_boundary=t);self.assertTrue(any("NORMATIVE_PARSER_PROOF" in x and "SUBJECT_ID_MISMATCH" in x for x in r["problems"]))

    def test_projection_candidate_tamper_blocks(self):
        b,c,t,_=proof_closed_disposition_fixture();b["projection"]["candidates"][0]["exact_text"]="tampered\n"
        r=qualify_normative_dispositions(b,proof_context=c,trusted_boundary=t);self.assertTrue(any("CANDIDATE_TEXT_DIGEST_MISMATCH" in x for x in r["problems"]))

    def test_every_candidate_requires_disposition(self):
        b,c,t,_=proof_closed_disposition_fixture();missing=b["dispositions"].pop()["candidate_clause_id"]
        r=qualify_normative_dispositions(b,proof_context=c,trusted_boundary=t);self.assertIn(f"NORMATIVE_DISPOSITION_MISSING:{missing}",r["problems"])

    def test_insufficient_evidence_disposition_blocks(self):
        b,c,t,_=proof_closed_disposition_fixture();b["dispositions"][0]["disposition"]=INSUFFICIENT_EVIDENCE
        r=qualify_normative_dispositions(b,proof_context=c,trusted_boundary=t);self.assertTrue(any("INSUFFICIENT_EVIDENCE" in x for x in r["problems"]))

    def test_owner_control_domain_cannot_be_disposition_authority(self):
        b,c,t,_=proof_closed_disposition_fixture();b["disposition_authority_set"]["member_control_domain_ids"][0]="ARTIFACT-OWNER"
        r=qualify_normative_dispositions(b,proof_context=c,trusted_boundary=t);self.assertIn("NORMATIVE_DISPOSITION_OWNER_CONTROL_DOMAIN_CONFLICT",r["problems"])

    def test_threshold_requires_exact_member_domain_pairs(self):
        b,c,t,_=proof_closed_disposition_fixture();b["dispositions"][0]["approver_control_domain_ids"]=["DOMAIN-B","DOMAIN-A"]
        r=qualify_normative_dispositions(b,proof_context=c,trusted_boundary=t);cid=b["dispositions"][0]["candidate_clause_id"];self.assertIn(f"NORMATIVE_DISPOSITION_APPROVER_NOT_IN_AUTHORITY_SET:{cid}",r["problems"])

    def test_material_candidate_requires_exact_catalog_descriptor(self):
        coverage,c,t,_=coverage_fixture();r=validate_catalog_candidate_coverage(coverage,proof_context=c,trusted_boundary=t);self.assertTrue(r["qualified"],r["problems"])

    def test_catalog_coverage_requires_qualified_disposition_set(self):
        coverage,_,_,_=coverage_fixture();r=validate_catalog_candidate_coverage(coverage);self.assertFalse(r["qualified"]);self.assertTrue(any("NORMATIVE_DISPOSITION_SET_PROOF" in x or "TRUSTED_PROOF_BOUNDARY_REQUIRED" in x for x in r["problems"]))

    def test_material_candidate_missing_descriptor_blocks(self):
        coverage,c,t,_=coverage_fixture([]);r=validate_catalog_candidate_coverage(coverage,proof_context=c,trusted_boundary=t);self.assertFalse(r["qualified"]);self.assertTrue(any("NORMATIVE_MATERIAL_CANDIDATE_UNMAPPED" in x for x in r["problems"]))

    def test_non_material_candidate_must_not_receive_normative_descriptor(self):
        coverage,c,t,result=coverage_fixture();nonmaterial=next(x["candidate_clause_id"] for x in result["disposition_binding_material"]["candidate_span_digests"] if x["candidate_clause_id"] not in result["material_candidate_ids"]);span=next(x["candidate_span_digest"] for x in result["disposition_binding_material"]["candidate_span_digests"] if x["candidate_clause_id"]==nonmaterial)
        coverage["catalog_descriptors"]=[{"control_id":"BAD","candidate_clause_id":nonmaterial,"artifact_sha256":coverage["artifact_sha256"],"normative_artifact_blob_sha":coverage["artifact_git_blob_sha1"],"candidate_span_digest":span}]
        r=validate_catalog_candidate_coverage(coverage,proof_context=c,trusted_boundary=t);self.assertTrue(any("NORMATIVE_DESCRIPTOR_TARGETS_NON_MATERIAL_CANDIDATE" in x for x in r["problems"]))

    def test_catalog_artifact_blob_mismatch_blocks(self):
        coverage,c,t,_=coverage_fixture();coverage["catalog_descriptors"][0]["normative_artifact_blob_sha"]="0"*40
        r=validate_catalog_candidate_coverage(coverage,proof_context=c,trusted_boundary=t);self.assertIn("NORMATIVE_CATALOG_ARTIFACT_BLOB_BINDING_MISMATCH:CTRL-A",r["problems"])

    def test_catalog_span_substitution_blocks(self):
        coverage,c,t,_=coverage_fixture();coverage["catalog_descriptors"][0]["candidate_span_digest"]=D6
        r=validate_catalog_candidate_coverage(coverage,proof_context=c,trusted_boundary=t);self.assertIn("NORMATIVE_CATALOG_SPAN_BINDING_MISMATCH:CTRL-A",r["problems"])

    def test_material_candidate_list_cannot_override_bound_disposition_result(self):
        coverage,c,t,_=coverage_fixture();coverage["material_candidate_ids"]=[]
        r=validate_catalog_candidate_coverage(coverage,proof_context=c,trusted_boundary=t);self.assertIn("NORMATIVE_MATERIAL_CANDIDATE_SET_BINDING_MISMATCH",r["problems"])

    def test_changed_candidate_span_invalidates_old_projection_and_dispositions(self):
        b,c,t,_=proof_closed_disposition_fixture();changed=TEXT+"\nAdditional structural unit.\n";p=projection(changed);b["projection"]=p;b["expected_artifact_sha256"]=p["artifact_sha256"];b["expected_artifact_git_blob_sha1"]=p["artifact_git_blob_sha1"]
        r=qualify_normative_dispositions(b,proof_context=c,trusted_boundary=t);self.assertFalse(r["qualified"]);self.assertTrue(any("NORMATIVE_PROJECTION_PROOF" in x or "UNKNOWN_CANDIDATE" in x or "MISSING" in x for x in r["problems"]))


if __name__=="__main__":unittest.main()
