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


def disposition_for(candidate, value, evidence=D4):
    r={
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
        r["successor_control_id"]="CTRL-SUCCESSOR"
    return r


def qualified_disposition_bundle(text=TEXT):
    p=projection(text)
    ds=[]
    # Treat one generic body block as normative; all other structural candidates are explicitly dispositioned.
    normative_done=False
    for c in p["candidates"]:
        if c["kind"]=="BODY_BLOCK" and "must deny" in c["exact_text"] and not normative_done:
            ds.append(disposition_for(c,MATERIAL_NORMATIVE));normative_done=True
        elif c["kind"]=="HEADING":
            ds.append(disposition_for(c,REFERENCE_ONLY))
        else:
            ds.append(disposition_for(c,PROVEN_NON_NORMATIVE))
    b={
        "projection":p,
        "parser_descriptor":parser_descriptor(),
        "expected_artifact_sha256":p["artifact_sha256"],
        "expected_artifact_git_blob_sha1":p["artifact_git_blob_sha1"],
        "disposition_authority_set":authority_set(),
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
