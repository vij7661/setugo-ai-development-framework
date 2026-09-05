import json
import tempfile
import unittest
from pathlib import Path

from build_exp_l_semantic_bundle import build_bundle


def write_result(root: Path, name: str, *, provider="p", status="PASS", eligible=True, diagnosis=None, findings=None):
    data = {
        "provider": provider,
        "mechanism_version": "model-x",
        "status": status,
        "evidence_eligible": eligible,
        "diagnosis": diagnosis,
        "findings": findings or [],
        "input_tokens": 10,
        "output_tokens": 5,
        "latency_ms": 100,
        "runtime_metadata": {"sampling_temperature": 1.0},
    }
    p = root / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


class ExpLSemanticBundleTests(unittest.TestCase):
    def test_single_valid_sample_is_insufficient_not_stable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = [
                write_result(root, "a.json", diagnosis={"primary_failure_class": "TEST DEFECT"}),
                write_result(root, "b.json", status="ERROR", eligible=False),
            ]
            b = build_bundle("C", paths, "sha", 1)
            p = b["providers"][0]
            self.assertEqual("INSUFFICIENT", p["sample_sufficiency"])
            self.assertIsNone(p["normalized_semantic_entropy"])
            self.assertFalse(p["stable_single_cluster"])

    def test_finding_class_is_used_when_diagnosis_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = write_result(root, "a.json", findings=[{"failure_class": "TEST DEFECT", "summary": "x"}])
            b = build_bundle("C", [path], "sha", 1)
            self.assertEqual("TEST DEFECT", b["samples"][0]["semantic_proxy_label"])

    def test_clean_structured_review_is_distinct_no_material_defect_cluster(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = write_result(root, "a.json", diagnosis=None, findings=[])
            b = build_bundle("C", [path], "sha", 1)
            self.assertEqual("NO_MATERIAL_DEFECT", b["samples"][0]["semantic_proxy_label"])

    def test_three_consistent_valid_samples_can_report_single_cluster_stability(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = [write_result(root, f"{i}.json", findings=[{"failure_class": "TEST DEFECT", "summary": "x"}]) for i in range(3)]
            b = build_bundle("C", paths, "sha", 1)
            p = b["providers"][0]
            self.assertEqual("SUFFICIENT", p["sample_sufficiency"])
            self.assertTrue(p["stable_single_cluster"])
            self.assertEqual(0.0, p["normalized_semantic_entropy"])

    def test_materially_different_classified_conclusions_have_nonzero_entropy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = [
                write_result(root, "a.json", findings=[]),
                write_result(root, "b.json", findings=[{"failure_class": "TEST DEFECT", "summary": "x"}]),
                write_result(root, "c.json", findings=[{"failure_class": "TEST DEFECT", "summary": "x"}]),
                write_result(root, "d.json", findings=[{"failure_class": "TEST DEFECT", "summary": "x"}]),
            ]
            b = build_bundle("C", paths, "sha", 1)
            p = b["providers"][0]
            self.assertGreater(p["normalized_semantic_entropy"], 0.0)
            self.assertFalse(p["stable_single_cluster"])


if __name__ == "__main__":
    unittest.main()
