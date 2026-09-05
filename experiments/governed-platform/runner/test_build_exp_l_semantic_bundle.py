import json
import tempfile
import unittest
from pathlib import Path

from build_exp_l_semantic_bundle import build_bundle


def write_result(root: Path, name: str, *, provider="p", status="PASS", eligible=True, diagnosis=None, findings=None, scope=None):
    data = {
        "provider": provider,
        "mechanism_version": "model-x",
        "status": status,
        "evidence_eligible": eligible,
        "diagnosis": diagnosis,
        "findings": findings or [],
        "authorized_scope": scope or [],
        "input_tokens": 10,
        "output_tokens": 5,
        "latency_ms": 100,
        "runtime_metadata": {"sampling_temperature": 1.0},
    }
    p = root / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


def finding(failure_class, *scope):
    return {"failure_class": failure_class, "summary": "x", "artifact_scope": list(scope)}


class ExpLSemanticBundleTests(unittest.TestCase):
    def test_single_valid_sample_is_insufficient_not_stable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = [
                write_result(root, "a.json", diagnosis={"primary_failure_class": "TEST DEFECT"}, scope=["TEST"]),
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
            path = write_result(root, "a.json", findings=[finding("TEST DEFECT", "assertion")], scope=["assertion"])
            b = build_bundle("C", [path], "sha", 1)
            self.assertEqual("FINDING=TEST DEFECT|SCOPE_CLASSES=TEST", b["samples"][0]["semantic_proxy_label"])

    def test_clean_structured_review_is_distinct_no_material_defect_cluster(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = write_result(root, "a.json", diagnosis=None, findings=[])
            b = build_bundle("C", [path], "sha", 1)
            self.assertEqual("NO_MATERIAL_DEFECT|SCOPE_CLASSES=NONE", b["samples"][0]["semantic_proxy_label"])

    def test_three_consistent_valid_samples_can_report_single_cluster_stability(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = [write_result(root, f"{i}.json", findings=[finding("TEST DEFECT", "assertion")], scope=["assertion"]) for i in range(3)]
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
                write_result(root, "b.json", findings=[finding("TEST DEFECT", "assertion")], scope=["assertion"]),
                write_result(root, "c.json", findings=[finding("TEST DEFECT", "assertion")], scope=["assertion"]),
                write_result(root, "d.json", findings=[finding("TEST DEFECT", "assertion")], scope=["assertion"]),
            ]
            b = build_bundle("C", paths, "sha", 1)
            p = b["providers"][0]
            self.assertGreater(p["normalized_semantic_entropy"], 0.0)
            self.assertFalse(p["stable_single_cluster"])

    def test_same_primary_different_contributor_is_materially_different(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = [
                write_result(
                    root,
                    "a.json",
                    diagnosis={"primary_failure_class": "CODE DEFECT", "contributors": ["FIXTURE-DATA DEFECT"]},
                    findings=[finding("CODE DEFECT", "svc"), finding("FIXTURE-DATA DEFECT", "fixture")],
                    scope=["svc", "fixture"],
                ),
                write_result(
                    root,
                    "b.json",
                    diagnosis={"primary_failure_class": "CODE DEFECT", "contributors": []},
                    findings=[finding("CODE DEFECT", "svc")],
                    scope=["svc"],
                ),
                write_result(
                    root,
                    "c.json",
                    diagnosis={"primary_failure_class": "CODE DEFECT", "contributors": ["FIXTURE-DATA DEFECT"]},
                    findings=[finding("CODE DEFECT", "svc"), finding("FIXTURE-DATA DEFECT", "fixture")],
                    scope=["svc", "fixture"],
                ),
            ]
            b = build_bundle("C", paths, "sha", 1)
            p = b["providers"][0]
            self.assertGreater(p["normalized_semantic_entropy"], 0.0)
            self.assertFalse(p["stable_single_cluster"])

    def test_same_failure_classes_different_semantic_scope_is_materially_different(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = [
                write_result(
                    root,
                    "a.json",
                    diagnosis={"primary_failure_class": "CODE DEFECT", "contributors": []},
                    findings=[finding("CODE DEFECT", "svc")],
                    scope=["svc"],
                ),
                write_result(
                    root,
                    "b.json",
                    diagnosis={"primary_failure_class": "CODE DEFECT", "contributors": ["TEST DEFECT"]},
                    findings=[finding("CODE DEFECT", "svc"), finding("TEST DEFECT", "assertion")],
                    scope=["svc", "assertion"],
                ),
                write_result(
                    root,
                    "c.json",
                    diagnosis={"primary_failure_class": "CODE DEFECT", "contributors": []},
                    findings=[finding("CODE DEFECT", "svc")],
                    scope=["svc"],
                ),
            ]
            b = build_bundle("C", paths, "sha", 1)
            self.assertGreater(b["providers"][0]["normalized_semantic_entropy"], 0.0)

    def test_lexical_scope_variants_same_artifact_class_do_not_manufacture_entropy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = [
                write_result(root, "a.json", diagnosis={"primary_failure_class": "CODE DEFECT"}, findings=[finding("CODE DEFECT", "payment creation logic")], scope=["payment creation logic"]),
                write_result(root, "b.json", diagnosis={"primary_failure_class": "CODE DEFECT"}, findings=[finding("CODE DEFECT", "production payment creation logic")], scope=["production payment creation logic"]),
                write_result(root, "c.json", diagnosis={"primary_failure_class": "CODE DEFECT"}, findings=[finding("CODE DEFECT", "idempotency persistence mechanism")], scope=["idempotency persistence mechanism"]),
            ]
            b = build_bundle("C", paths, "sha", 1)
            p = b["providers"][0]
            self.assertTrue(p["stable_single_cluster"])
            self.assertEqual(0.0, p["normalized_semantic_entropy"])
            self.assertEqual(0, p["samples_with_unmapped_authorized_scope"])

    def test_unmapped_authorized_scope_is_retained_as_material_marker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = write_result(
                root,
                "a.json",
                diagnosis={"primary_failure_class": "CODE DEFECT"},
                findings=[finding("CODE DEFECT", "known service")],
                scope=["known service", "mystery admin override"],
            )
            b = build_bundle("C", [path], "sha", 1)
            sample = b["samples"][0]
            self.assertIn("UNMAPPED_SCOPE", sample["semantic_proxy_label"])
            self.assertEqual(1, sample["unmapped_authorized_scope_count"])

    def test_contributor_explanation_suffix_normalizes_to_canonical_class(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = [
                write_result(root, "a.json", diagnosis={"primary_failure_class": "FIXTURE-DATA DEFECT", "contributors": ["CODE DEFECT"]}, findings=[finding("FIXTURE-DATA DEFECT", "fixture"), finding("CODE DEFECT", "svc")], scope=["fixture", "svc"]),
                write_result(root, "b.json", diagnosis={"primary_failure_class": "FIXTURE-DATA DEFECT", "contributors": ["CODE DEFECT: late idempotency"]}, findings=[finding("FIXTURE-DATA DEFECT", "fixture2"), finding("CODE DEFECT", "svc2")], scope=["fixture2", "svc2"]),
                write_result(root, "c.json", diagnosis={"primary_failure_class": "FIXTURE-DATA DEFECT", "contributors": ["CODE DEFECT - retry bug"]}, findings=[finding("FIXTURE-DATA DEFECT", "fixture3"), finding("CODE DEFECT", "svc3")], scope=["fixture3", "svc3"]),
            ]
            b = build_bundle("C", paths, "sha", 1)
            self.assertTrue(b["providers"][0]["stable_single_cluster"])


if __name__ == "__main__":
    unittest.main()
