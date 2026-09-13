from __future__ import annotations

import unittest

from v24_v6_governance_foundation import CURRENT, QUALIFIED, INSUFFICIENT_EVIDENCE, digest
from v24_v6_normative_clause_projection import (
    MATERIAL_NORMATIVE,
    PROVEN_NON_NORMATIVE,
    REFERENCE_ONLY,
    SUPERSEDED,
    construction_frontier,
    enumerate_markdown_structural_candidates,
    qualify_normative_dispositions,
    validate_catalog_candidate_coverage,
)

D1="1"*64;D2="2"*64;D3="3"*64;D4="4"*64;D5="5"*64;D6="6"*64



def seal(record, field):
    material=dict(record); material.pop(field,None); record[field]=digest(material); return record


def currentness(source_id, source_digest):
    r={
        "currentness_rule_id":"CUR-1", "source_object_id":source_id,
        "source_version_or_sequence":"1", "source_digest":source_digest,
        "observed_at_sequence":1, "verifier_qualification_digest":D6,
        "result":CURRENT, "binding_digest":"",
    }
    return seal(r,"binding_digest")


def qualification(subject_id, subject_digest, subject_kind):
    r={
        "qualification_id":f"Q-{subject_id}", "subject_object_id":subject_id,
        "subject_content_digest":subject_digest, "subject_kind":subject_kind,
        "subject_owner_id":f"OWNER-{subject_id}", "qualification_authority_id":"QUAL-AUTH",
        "authority_member_ids":["QA-1"], "authority_control_domain_ids":["QUAL-DOMAIN"],
        "independence_qualification_digests":[D4], "evidence_record_digests":[D5],
        "evidence_class_ids":["EVIDENCE-1"], "verifier_mechanism_id":"QUAL-VERIFIER",
        "verifier_mechanism_qualification_digest":D6,
        "currentness_bindings":[currentness(subject_id,subject_digest)],
        "result":QUALIFIED, "proof_digest":D5, "qualification_digest":"",
    }
    return seal(r,"qualification_digest")

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


def parser_descriptor():
    subject_id="MD-STRUCTURAL-V1"
    subject_digest=digest({"parser_profile_id":subject_id,"implementation_content_digest":D1,"rule_digest":D2})
    q=qualification(subject_id,subject_digest,"NORMATIVE_STRUCTURAL_PARSER")
    return {
        "parser_profile_id":subject_id,
        "implementation_content_digest":D1,
        "rule_digest":D2,
        "qualification_state":QUALIFIED,
        "qualification_digest":q["qualification_digest"],
        "qualification_record":q,
        "independence_state":QUALIFIED,
        "currentness_result":CURRENT,
    }


def authority_set():
    authority={
        "authority_set_id":"NORMATIVE-DISPOSITION-AUTHORITY",
        "currentness_result":CURRENT,
        "independence_state":QUALIFIED,
        "threshold":2,
        "member_ids":["REV-A","REV-B"],
        "member_control_domain_ids":["DOMAIN-A","DOMAIN-B"],
    }
    subject_digest=digest({
        "authority_set_id":authority["authority_set_id"],
        "threshold":authority["threshold"],
        "member_ids":sorted(authority["member_ids"]),
        "member_control_domain_ids":sorted(authority["member_control_domain_ids"]),
    })
    q=qualification(authority["authority_set_id"],subject_digest,"NORMATIVE_DISPOSITION_AUTHORITY_SET")
    authority.update({"qualification_state":QUALIFIED,"qualification_digest":q["qualification_digest"],"qualification_record":q})
    return authority


def disposition_for(candidate, value, authority_qualification_digest, evidence=D4):
    r={
        "candidate_clause_id":candidate["candidate_clause_id"],
        "artifact_sha256":candidate["artifact_sha256"],
        "candidate_span_digest":candidate["exact_text_sha256"],
        "authority_set_qualification_digest":authority_qualification_digest,
        "approver_ids":["REV-A","REV-B"],
        "approver_control_domain_ids":["DOMAIN-A","DOMAIN-B"],
        "evidence_digests":[evidence],
        "currentness_result":CURRENT,
        "disposition":value,
    }
    if value==SUPERSEDED:
        r["successor_control_id"]="CTRL-SUCCESSOR"
    return r


def qualified_disposition_bundle(text=TEXT):
    p=projection(text)
    auth=authority_set()
    ds=[]
    # Treat one generic body block as normative; all other structural candidates are explicitly dispositioned.
    normative_done=False
    for c in p["candidates"]:
        if c["kind"]=="BODY_BLOCK" and "must deny" in c["exact_text"] and not normative_done:
            ds.append(disposition_for(c,MATERIAL_NORMATIVE,auth["qualification_digest"]));normative_done=True
        elif c["kind"]=="HEADING":
            ds.append(disposition_for(c,REFERENCE_ONLY,auth["qualification_digest"]))
        else:
            ds.append(disposition_for(c,PROVEN_NON_NORMATIVE,auth["qualification_digest"]))
    b={
        "projection":p,
        "parser_descriptor":parser_descriptor(),
        "expected_artifact_sha256":p["artifact_sha256"],
        "expected_artifact_git_blob_sha1":p["artifact_git_blob_sha1"],
        "disposition_authority_set":auth,
        "artifact_owner_control_domain_id":"ARTIFACT-OWNER",
        "catalog_owner_control_domain_id":"CATALOG-OWNER",
        "dispositions":ds,
    }
    return b


class R5NormativeProjectionTests(unittest.TestCase):
    def test_frontier_non_authoritative(self):
        r=construction_frontier();self.assertFalse(r["qualified"]);self.assertEqual(r["authority_effect"],"NONE_EVIDENCE_ONLY")

    def test_structural_projection_is_deterministic(self):
        a=projection();b=projection();self.assertTrue(a["qualified"],a["problems"]);self.assertEqual(a["projection_digest"],b["projection_digest"]);self.assertEqual(a["candidate_set_digest"],b["candidate_set_digest"])

    def test_new_generic_prose_becomes_new_structural_candidate(self):
        a=projection()
        changed=TEXT.replace("Supporting explanation only.\n\n","Supporting explanation only.\n\nAn additional requirement applies to all authoritative decisions.\n\n")
        b=projection(changed)
        self.assertGreater(len(b["candidates"]),len(a["candidates"]))
        self.assertNotEqual(a["candidate_set_digest"],b["candidate_set_digest"])

    def test_projection_does_not_use_catalog_locator_input(self):
        p=projection();self.assertNotIn("required_clause_locators",p);self.assertTrue(any(c["kind"]=="BODY_BLOCK" for c in p["candidates"]))

    def test_exact_artifact_sha_binding_required(self):
        b=qualified_disposition_bundle();b["expected_artifact_sha256"]=D5
        r=qualify_normative_dispositions(b);self.assertIn("NORMATIVE_ARTIFACT_SHA256_BINDING_MISMATCH",r["problems"])

    def test_parser_must_be_qualified_independent_current(self):
        b=qualified_disposition_bundle();b["parser_descriptor"]["independence_state"]="CONFLICT"
        r=qualify_normative_dispositions(b);self.assertIn("NORMATIVE_PARSER_NOT_INDEPENDENT",r["problems"])


    def test_parser_requires_bound_qualification_digest(self):
        b=qualified_disposition_bundle(); b["parser_descriptor"]["qualification_digest"]=None
        r=qualify_normative_dispositions(b); self.assertTrue(any("NORMATIVE_PARSER_QUALIFICATION_DIGEST_INVALID" in x for x in r["problems"]))

    def test_authority_set_requires_valid_governed_qualification_record(self):
        b=qualified_disposition_bundle(); b["disposition_authority_set"]["qualification_digest"]=None
        for d in b["dispositions"]: d["authority_set_qualification_digest"]=None
        r=qualify_normative_dispositions(b)
        self.assertFalse(r["qualified"]); self.assertTrue(any("AUTHORITY_SET_QUALIFICATION_DIGEST_INVALID" in x for x in r["problems"]))

    def test_authority_set_qualification_subject_binding_cannot_be_substituted(self):
        b=qualified_disposition_bundle(); q=b["disposition_authority_set"]["qualification_record"]
        q["subject_object_id"]="OTHER-AUTHORITY"; seal(q,"qualification_digest")
        b["disposition_authority_set"]["qualification_digest"]=q["qualification_digest"]
        for d in b["dispositions"]: d["authority_set_qualification_digest"]=q["qualification_digest"]
        r=qualify_normative_dispositions(b)
        self.assertTrue(any("QUALIFICATION_SUBJECT_ID_MISMATCH" in x for x in r["problems"]))

    def test_every_candidate_requires_disposition(self):
        b=qualified_disposition_bundle();missing=b["dispositions"].pop()["candidate_clause_id"]
        r=qualify_normative_dispositions(b);self.assertIn(f"NORMATIVE_DISPOSITION_MISSING:{missing}",r["problems"])

    def test_insufficient_evidence_disposition_blocks(self):
        b=qualified_disposition_bundle();b["dispositions"][0]["disposition"]=INSUFFICIENT_EVIDENCE
        r=qualify_normative_dispositions(b);self.assertTrue(any("INSUFFICIENT_EVIDENCE" in x for x in r["problems"]))

    def test_owner_control_domain_cannot_be_disposition_authority(self):
        b=qualified_disposition_bundle();b["disposition_authority_set"]["member_control_domain_ids"][0]="ARTIFACT-OWNER"
        r=qualify_normative_dispositions(b);self.assertIn("NORMATIVE_DISPOSITION_OWNER_CONTROL_DOMAIN_CONFLICT",r["problems"])

    def test_threshold_requires_distinct_approvers_and_domains(self):
        b=qualified_disposition_bundle();b["dispositions"][0]["approver_ids"]=["REV-A"]
        r=qualify_normative_dispositions(b);self.assertTrue(any("THRESHOLD_NOT_MET" in x for x in r["problems"]))

    def test_material_candidate_requires_exact_catalog_descriptor(self):
        b=qualified_disposition_bundle();q=qualify_normative_dispositions(b);self.assertTrue(q["qualified"],q["problems"])
        p=b["projection"];mid=q["material_candidate_ids"][0];candidate=next(c for c in p["candidates"] if c["candidate_clause_id"]==mid)
        c={"disposition_qualification_state":QUALIFIED,"material_candidate_ids":q["material_candidate_ids"],"artifact_sha256":p["artifact_sha256"],"artifact_git_blob_sha1":p["artifact_git_blob_sha1"],"catalog_descriptors":[{"control_id":"CTRL-A","candidate_clause_id":mid,"artifact_sha256":p["artifact_sha256"],"normative_artifact_blob_sha":p["artifact_git_blob_sha1"],"candidate_span_digest":candidate["exact_text_sha256"]}]}
        r=validate_catalog_candidate_coverage(c);self.assertTrue(r["qualified"],r["problems"])

    def test_material_candidate_missing_descriptor_blocks(self):
        b=qualified_disposition_bundle();q=qualify_normative_dispositions(b);p=b["projection"]
        r=validate_catalog_candidate_coverage({"disposition_qualification_state":QUALIFIED,"material_candidate_ids":q["material_candidate_ids"],"artifact_sha256":p["artifact_sha256"],"artifact_git_blob_sha1":p["artifact_git_blob_sha1"],"catalog_descriptors":[]})
        self.assertFalse(r["qualified"]);self.assertTrue(any("NORMATIVE_MATERIAL_CANDIDATE_UNMAPPED" in x for x in r["problems"]))

    def test_non_material_candidate_must_not_receive_normative_descriptor(self):
        b=qualified_disposition_bundle();q=qualify_normative_dispositions(b);p=b["projection"]
        nonmaterial=next(c for c in p["candidates"] if c["candidate_clause_id"] not in q["material_candidate_ids"])
        r=validate_catalog_candidate_coverage({"disposition_qualification_state":QUALIFIED,"material_candidate_ids":q["material_candidate_ids"],"artifact_sha256":p["artifact_sha256"],"artifact_git_blob_sha1":p["artifact_git_blob_sha1"],"catalog_descriptors":[{"control_id":"BAD","candidate_clause_id":nonmaterial["candidate_clause_id"],"artifact_sha256":p["artifact_sha256"],"normative_artifact_blob_sha":p["artifact_git_blob_sha1"],"candidate_span_digest":nonmaterial["exact_text_sha256"]}]})
        self.assertTrue(any("NORMATIVE_DESCRIPTOR_TARGETS_NON_MATERIAL_CANDIDATE" in x for x in r["problems"]))

    def test_catalog_artifact_blob_mismatch_blocks(self):
        b=qualified_disposition_bundle();q=qualify_normative_dispositions(b);p=b["projection"];mid=q["material_candidate_ids"][0];candidate=next(c for c in p["candidates"] if c["candidate_clause_id"]==mid)
        r=validate_catalog_candidate_coverage({"disposition_qualification_state":QUALIFIED,"material_candidate_ids":[mid],"artifact_sha256":p["artifact_sha256"],"artifact_git_blob_sha1":p["artifact_git_blob_sha1"],"catalog_descriptors":[{"control_id":"CTRL-A","candidate_clause_id":mid,"artifact_sha256":p["artifact_sha256"],"normative_artifact_blob_sha":"0"*40,"candidate_span_digest":candidate["exact_text_sha256"]}]})
        self.assertIn("NORMATIVE_CATALOG_ARTIFACT_BLOB_BINDING_MISMATCH:CTRL-A",r["problems"])

    def test_changed_candidate_span_invalidates_old_disposition(self):
        b=qualified_disposition_bundle();old=b["dispositions"][0]
        changed=TEXT+"\nAdditional structural unit.\n"
        p=projection(changed)
        b2={**b,"projection":p,"expected_artifact_sha256":p["artifact_sha256"],"expected_artifact_git_blob_sha1":p["artifact_git_blob_sha1"],"dispositions":b["dispositions"]}
        r=qualify_normative_dispositions(b2);self.assertFalse(r["qualified"]);self.assertTrue(any("UNKNOWN_CANDIDATE" in x or "MISSING" in x for x in r["problems"]))

if __name__=="__main__":unittest.main()
