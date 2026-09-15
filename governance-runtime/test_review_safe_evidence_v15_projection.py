from __future__ import annotations

import unittest

from review_safe_evidence_v15 import canonical_hash
from review_safe_evidence_v15_projection import (
    projection_construction_frontier,
    validate_disclosure_catalog,
    validate_disclosure_completeness_certificate,
    validate_obligation_graph,
    validate_obligation_record,
    validate_projection_record,
)


def seal(r, field):
    r[field] = canonical_hash({k: v for k, v in r.items() if k != field})
    return r


def independence(a="D-COMP", b="D-VER", result="INDEPENDENT", shared=None):
    return seal({
        "schema_version": 1,
        "proof_id": f"IP-{a}-{b}",
        "subject_a": a,
        "subject_b": b,
        "generation_id": "GEN-1",
        "ancestry_graph_digest": "1" * 64,
        "shared_load_bearing_ancestors": list(shared or []),
        "declared_residual_roots": ["R1", "R2"],
        "result": result,
        "proof_digest": "",
    }, "proof_digest")


def obligation(oid="O1", dim="D1", evidence_id="E1"):
    return seal({
        "schema_version": 1,
        "obligation_id": oid,
        "dimension_id": dim,
        "proposition_id": f"P-{oid}",
        "generation_id": "GEN-1",
        "materiality_authority_id": "MAT-1",
        "materiality_control_domain_id": "D-MAT",
        "currentness_rule": "GENERATION_CURRENT",
        "currentness_state": "CURRENT",
        "candidate_controlled": False,
        "required_evidence_ids": [evidence_id],
        "load_bearing_fields": ["identity", "status"],
        "non_load_bearing_fields": ["comment", "debug"],
        "load_bearing_relations": ["source_binding"],
        "semantic_contract": {
            "cardinality": "EXACT_RECORD",
            "ordering": "PRESERVE_SOURCE_ORDER",
            "units": "NO_CONVERSION",
            "qualifiers": "PRESERVE_LOAD_BEARING",
            "provenance": "PRESERVE_SOURCE_BINDING",
        },
        "record_digest": "",
    }, "record_digest")


def graph(obligations=None, dimensions=None):
    obligations = list(obligations or [obligation()])
    dimensions = list(dimensions or ["D1"])
    return seal({
        "schema_version": 1,
        "graph_id": "G1",
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "mandatory_dimensions": dimensions,
        "obligations": obligations,
        "graph_digest": "",
    }, "graph_digest")


def raw(evidence_id="E1"):
    content = {
        "identity": "OBJ-1",
        "status": "CURRENT",
        "comment": "diagnostic text",
        "debug": "trace text",
    }
    relations = {"source_binding": "SRC-1", "diagnostic_relation": "D-1"}
    return {
        "evidence_id": evidence_id,
        "content": content,
        "relations": relations,
        "content_digest": canonical_hash(content),
        "relations_digest": canonical_hash(relations),
    }


def projection(*, mode="STRUCTURED_REDACTION", omitted=None, content=None, relations=None,
               raw_access=True, recomputed=True):
    source = raw()
    omitted = ["comment"] if omitted is None else list(omitted)
    if content is None:
        content = {k: v for k, v in source["content"].items() if k not in omitted}
    if relations is None:
        relations = dict(source["relations"])
    r = {
        "schema_version": 1,
        "projection_id": "PR-1",
        "obligation_id": "O1",
        "raw_evidence_id": "E1",
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "compiler_id": "COMP-1",
        "compiler_control_domain_id": "D-COMP",
        "verifier_id": "VER-1",
        "verifier_control_domain_id": "D-VER",
        "obligation_graph_digest": "g" * 64,
        "mode": mode,
        "candidate_controlled": False,
        "raw_access_attested": raw_access,
        "materiality_recomputed": recomputed,
        "omitted_fields": omitted,
        "projected_content": content,
        "projected_relations": relations,
        "projected_content_digest": canonical_hash(content),
        "projected_relations_digest": canonical_hash(relations),
        "projection_digest": "",
    }
    return seal(r, "projection_digest")


def projection_result(record=None, source=None, obl=None, proof=None):
    return validate_projection_record(
        record or projection(), raw=source or raw(), obligation=obl or obligation(),
        verifier_independence_proof=proof or independence())


def catalog(state="COMPLETE_REVIEWABLE_VIEW", projection_ids=None):
    projection_ids = list(projection_ids or ["PR-1"])
    return seal({
        "schema_version": 1,
        "catalog_id": "DC-1",
        "candidate_id": "C1",
        "snapshot_id": "S1",
        "generation_id": "GEN-1",
        "views": [{
            "view_id": "VIEW-O1-MIN",
            "obligation_id": "O1",
            "minimum_view": True,
            "presealed": True,
            "state": state,
            "projection_ids": projection_ids,
        }],
        "catalog_digest": "",
    }, "catalog_digest")


class ObligationTests(unittest.TestCase):
    def test_valid_obligation(self):
        self.assertTrue(validate_obligation_record(obligation())["valid"])

    def test_candidate_controlled_materiality_rejected(self):
        r = obligation()
        r["candidate_controlled"] = True
        seal(r, "record_digest")
        self.assertIn("OBLIGATION_CANDIDATE_CONTROL_FORBIDDEN", validate_obligation_record(r)["problems"])

    def test_load_and_nonload_overlap_rejected(self):
        r = obligation()
        r["non_load_bearing_fields"].append("identity")
        seal(r, "record_digest")
        self.assertIn("OBLIGATION_FIELD_MATERIALITY_OVERLAP", validate_obligation_record(r)["problems"])

    def test_graph_requires_every_mandatory_dimension(self):
        g = graph(dimensions=["D1", "D2"])
        self.assertIn("OBLIGATION_GRAPH_DIMENSION_UNCOVERED:D2", validate_obligation_graph(g)["problems"])

    def test_graph_positive(self):
        out = validate_obligation_graph(graph())
        self.assertTrue(out["valid"], out["problems"])


class ProjectionTests(unittest.TestCase):
    def test_structured_redaction_of_nonload_field_passes(self):
        out = projection_result()
        self.assertTrue(out["valid"], out["problems"])
        self.assertTrue(out["reviewable"])

    def test_load_bearing_field_omission_rejected(self):
        r = projection(omitted=["identity"])
        out = projection_result(record=r)
        self.assertTrue(any("PROJECTION_LOAD_OR_UNKNOWN_FIELD_OMISSION_FORBIDDEN:identity" in x for x in out["problems"]))
        self.assertTrue(any("PROJECTION_LOAD_BEARING_FIELD_OMITTED:identity" in x for x in out["problems"]))

    def test_retained_value_change_rejected(self):
        c = dict(raw()["content"])
        c.pop("comment")
        c["status"] = "STALE"
        r = projection(content=c)
        out = projection_result(record=r)
        self.assertIn("PROJECTION_LOAD_BEARING_FIELD_CHANGED:status", out["problems"])

    def test_generated_field_rejected(self):
        c = dict(raw()["content"])
        c.pop("comment")
        c["generated_summary"] = "looks fine"
        r = projection(content=c)
        out = projection_result(record=r)
        self.assertIn("PROJECTION_GENERATED_FIELD_FORBIDDEN:generated_summary", out["problems"])

    def test_load_bearing_relation_omission_rejected(self):
        rel = {"diagnostic_relation": "D-1"}
        r = projection(relations=rel)
        out = projection_result(record=r)
        self.assertIn("PROJECTION_LOAD_BEARING_RELATION_OMITTED:source_binding", out["problems"])

    def test_no_raw_access_rejected(self):
        out = projection_result(record=projection(raw_access=False))
        self.assertIn("PROJECTION_VERIFIER_RAW_ACCESS_REQUIRED", out["problems"])

    def test_no_materiality_recompute_rejected(self):
        out = projection_result(record=projection(recomputed=False))
        self.assertIn("PROJECTION_MATERIALITY_RECOMPUTE_REQUIRED", out["problems"])

    def test_unproven_compiler_verifier_independence_rejected(self):
        out = projection_result(proof=independence(result="INDEPENDENCE_UNPROVEN"))
        self.assertIn("PROJECTION_VERIFIER_INDEPENDENCE_REQUIRED", out["problems"])

    def test_exact_projection_must_match_all_content(self):
        r = projection(mode="EXACT", omitted=[], content=raw()["content"], relations=raw()["relations"])
        self.assertTrue(projection_result(record=r)["valid"])
        bad = dict(raw()["content"])
        bad["status"] = "STALE"
        r2 = projection(mode="EXACT", omitted=[], content=bad, relations=raw()["relations"])
        self.assertIn("PROJECTION_EXACT_CONTENT_MISMATCH", projection_result(record=r2)["problems"])


class DisclosureTests(unittest.TestCase):
    def test_complete_minimum_view_is_review_ready(self):
        pr = projection_result()
        out = validate_disclosure_catalog(catalog(), obligations=[obligation()], projections={"PR-1": pr})
        self.assertTrue(out["valid"], out["problems"])
        self.assertTrue(out["review_ready"])

    def test_missing_minimum_view_blocks(self):
        c = catalog()
        c["views"] = []
        seal(c, "catalog_digest")
        out = validate_disclosure_catalog(c, obligations=[obligation()], projections={"PR-1": projection_result()})
        self.assertIn("DISCLOSURE_MINIMUM_VIEW_COUNT_INVALID:O1:0", out["problems"])
        self.assertFalse(out["review_ready"])

    def test_invalid_projection_blocks_view(self):
        bad = projection_result(record=projection(raw_access=False))
        out = validate_disclosure_catalog(catalog(), obligations=[obligation()], projections={"PR-1": bad})
        self.assertIn("DISCLOSURE_VIEW_PROJECTION_INVALID:VIEW-O1-MIN:PR-1", out["problems"])

    def test_insufficient_minimum_view_is_valid_but_not_review_ready(self):
        pr = projection_result()
        out = validate_disclosure_catalog(
            catalog(state="INSUFFICIENT_TO_ASSESS"), obligations=[obligation()], projections={"PR-1": pr})
        self.assertTrue(out["valid"], out["problems"])
        self.assertFalse(out["review_ready"])
        self.assertEqual(out["insufficient_obligations"], ["O1"])

    def test_disclosure_certificate_must_match_catalog_state(self):
        pr = projection_result()
        c = catalog(state="INSUFFICIENT_TO_ASSESS")
        cr = validate_disclosure_catalog(c, obligations=[obligation()], projections={"PR-1": pr})
        cert = seal({
            "schema_version": 1,
            "certificate_id": "CERT-1",
            "candidate_id": "C1",
            "snapshot_id": "S1",
            "generation_id": "GEN-1",
            "verifier_id": "DISC-V",
            "verifier_control_domain_id": "D-DISC",
            "verifier_independence_result": "INDEPENDENT",
            "catalog_digest": c["catalog_digest"],
            "bound_catalog_digest": c["catalog_digest"],
            "obligation_states": {"O1": "COMPLETE_REVIEWABLE_VIEW"},
            "certificate_digest": "",
        }, "certificate_digest")
        out = validate_disclosure_completeness_certificate(
            cert, catalog_result=cr, expected_obligation_ids=["O1"])
        self.assertIn("DISCLOSURE_CERTIFICATE_STATE_MISMATCH:O1:INSUFFICIENT_TO_ASSESS", out["problems"])
        self.assertFalse(out["review_ready"])

    def test_complete_certificate_is_review_ready(self):
        pr = projection_result()
        c = catalog()
        cr = validate_disclosure_catalog(c, obligations=[obligation()], projections={"PR-1": pr})
        cert = seal({
            "schema_version": 1,
            "certificate_id": "CERT-1",
            "candidate_id": "C1",
            "snapshot_id": "S1",
            "generation_id": "GEN-1",
            "verifier_id": "DISC-V",
            "verifier_control_domain_id": "D-DISC",
            "verifier_independence_result": "INDEPENDENT",
            "catalog_digest": c["catalog_digest"],
            "bound_catalog_digest": c["catalog_digest"],
            "obligation_states": {"O1": "COMPLETE_REVIEWABLE_VIEW"},
            "certificate_digest": "",
        }, "certificate_digest")
        out = validate_disclosure_completeness_certificate(
            cert, catalog_result=cr, expected_obligation_ids=["O1"])
        self.assertTrue(out["valid"], out["problems"])
        self.assertTrue(out["review_ready"])

    def test_frontier_non_authoritative(self):
        f = projection_construction_frontier()
        self.assertFalse(f["qualified"])
        self.assertEqual(f["authority_effect"], "NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()
