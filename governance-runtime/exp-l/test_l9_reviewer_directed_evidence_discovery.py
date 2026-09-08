from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path("governance-runtime/review-trust-kernel/evidence_discovery_broker_v1.py")


def load_module(repo_root):
    spec = importlib.util.spec_from_file_location("evidence_discovery_broker_v1", repo_root / MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EvidenceDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.m = load_module(cls.repo_root)

    def req(self, **extra):
        kwargs=dict(review_id="REV-1",candidate_sha="c"*40,base_sha="b"*40,query_type="READ_FILE",path="docs/current.md",reason="resolve contradiction",allowed_prefixes=["docs","governance-runtime"])
        kwargs.update(extra)
        return self.m.build_discovery_request(**kwargs)

    def test_l9_01_read_request_is_deterministic(self):
        a=self.req(); b=self.req(); self.assertEqual(a,b); self.assertEqual(a["request_sha256"],b["request_sha256"])

    def test_l9_02_write_query_rejected(self):
        with self.assertRaises(ValueError): self.req(query_type="WRITE_FILE")

    def test_l9_03_parent_traversal_rejected(self):
        with self.assertRaises(ValueError): self.req(path="../secret.txt")

    def test_l9_04_outside_allowlist_rejected(self):
        with self.assertRaises(ValueError): self.req(path="secrets/key.txt")

    def test_l9_05_response_is_candidate_and_base_bound(self):
        q=self.req(); r=self.m.materialize_response(q,content="x",source_ref="repo:docs/current.md@"+q["candidate_sha"])
        self.assertEqual(r["candidate_sha"],q["candidate_sha"]); self.assertEqual(r["base_sha"],q["base_sha"])

    def test_l9_06_response_is_hashed(self):
        q=self.req(); r=self.m.materialize_response(q,content="abc",source_ref="repo:docs/current.md@c")
        self.assertTrue(r["content_sha256"]); self.assertTrue(r["response_sha256"])

    def test_l9_07_missing_mandatory_discovery_blocks_promotion(self):
        q=self.req(); r=self.m.materialize_response(q,found=False)
        a=self.m.adjudicate_discovery(mandatory_request_hashes=[q["request_sha256"]],responses=[r],reviewer_disposition="PASS")
        self.assertFalse(a["promotable"]); self.assertEqual(a["unresolved_request_hashes"],[q["request_sha256"]])

    def test_l9_08_absent_response_blocks_promotion(self):
        q=self.req(); a=self.m.adjudicate_discovery(mandatory_request_hashes=[q["request_sha256"]],responses=[],reviewer_disposition="PASS")
        self.assertFalse(a["promotable"])

    def test_l9_09_resolved_mandatory_discovery_allows_pass(self):
        q=self.req(); r=self.m.materialize_response(q,content="authoritative",source_ref="repo:docs/current.md@c")
        a=self.m.adjudicate_discovery(mandatory_request_hashes=[q["request_sha256"]],responses=[r],reviewer_disposition="PASS")
        self.assertTrue(a["promotable"])

    def test_l9_10_nonpass_never_promotes_even_if_discovery_resolved(self):
        q=self.req(); r=self.m.materialize_response(q,content="authoritative",source_ref="repo:docs/current.md@c")
        a=self.m.adjudicate_discovery(mandatory_request_hashes=[q["request_sha256"]],responses=[r],reviewer_disposition="CHANGES_REQUIRED")
        self.assertFalse(a["promotable"])

    def test_l9_11_decision_is_byte_stable(self):
        q=self.req(); r=self.m.materialize_response(q,content="authoritative",source_ref="repo:docs/current.md@c")
        a=self.m.adjudicate_discovery(mandatory_request_hashes=[q["request_sha256"]],responses=[r],reviewer_disposition="PASS")
        b=self.m.adjudicate_discovery(mandatory_request_hashes=[q["request_sha256"]],responses=[r],reviewer_disposition="PASS")
        self.assertEqual(a,b); self.assertEqual(a["decision_sha256"],b["decision_sha256"])

    def test_l9_12_request_explicitly_read_only(self):
        self.assertTrue(self.req()["read_only"])


if __name__ == "__main__": unittest.main(verbosity=2)
