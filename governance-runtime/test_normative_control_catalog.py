from __future__ import annotations

import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from normative_control_catalog import git_blob_sha_bytes, validate_normative_catalog


def clause_sha(text: str, heading: str) -> str:
    lines = text.splitlines(keepends=True)
    start = next(i for i, line in enumerate(lines) if line.rstrip("\r\n") == heading)
    level = len(heading) - len(heading.lstrip("#"))
    end = len(lines)
    for i in range(start + 1, len(lines)):
        stripped = lines[i].lstrip()
        if stripped.startswith("#"):
            prefix = len(stripped) - len(stripped.lstrip("#"))
            if prefix <= level and len(stripped) > prefix and stripped[prefix] == " ":
                end = i
                break
    value = "".join(lines[start:end]).rstrip("\r\n") + "\n"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class NormativeControlCatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "standards").mkdir()

        self.current_text = "# Current\n\n## P24-16 — Catalog\n\nCurrent rule.\n\n## P24-17 — Endpoint\n\nEndpoint rule.\n"
        self.legacy_text = "# Legacy\n\n## §1 Scope\n\nLegacy active rule.\n\n## §2 Old path\n\nSuperseded rule.\n"
        self.reference_text = "# Notes\n\nInformational only.\n"

        (self.root / "standards/current.md").write_text(self.current_text, encoding="utf-8")
        (self.root / "standards/legacy.md").write_text(self.legacy_text, encoding="utf-8")
        (self.root / "standards/reference.md").write_text(self.reference_text, encoding="utf-8")

        current_blob = git_blob_sha_bytes(self.current_text.encode())
        legacy_blob = git_blob_sha_bytes(self.legacy_text.encode())
        ref_blob = git_blob_sha_bytes(self.reference_text.encode())

        self.manifest = {
            "schema_version": 1,
            "governance_generation": "V24",
            "artifacts": [
                {
                    "path": "standards/current.md",
                    "blob_sha": current_blob,
                    "classification": "AUTHORITATIVE_DESCRIPTOR_REQUIRED",
                    "required_clause_locators": [
                        {
                            "locator_id": "P24-16",
                            "heading": "## P24-16 — Catalog",
                            "clause_sha256": clause_sha(self.current_text, "## P24-16 — Catalog"),
                        },
                        {
                            "locator_id": "P24-17",
                            "heading": "## P24-17 — Endpoint",
                            "clause_sha256": clause_sha(self.current_text, "## P24-17 — Endpoint"),
                        },
                    ],
                },
                {
                    "path": "standards/legacy.md",
                    "blob_sha": legacy_blob,
                    "classification": "NONAUTHORITATIVE_REFERENCE",
                    "required_clause_locators": [],
                },
                {
                    "path": "standards/reference.md",
                    "blob_sha": ref_blob,
                    "classification": "NONAUTHORITATIVE_REFERENCE",
                    "required_clause_locators": [],
                },
            ],
        }
        self.catalog = {
            "schema_version": 1,
            "governance_generation": "V24",
            "descriptors": [
                self._descriptor(
                    "P24-16",
                    "P24-16",
                    "## P24-16 — Catalog",
                    clause_sha(self.current_text, "## P24-16 — Catalog"),
                ),
                self._descriptor(
                    "P24-17",
                    "P24-17",
                    "## P24-17 — Endpoint",
                    clause_sha(self.current_text, "## P24-17 — Endpoint"),
                ),
            ],
        }
        self.legacy = {
            "schema_version": 1,
            "governance_generation": "V24",
            "legacy_clause_inventory": [
                {"artifact_path": "standards/legacy.md", "locator_id": "V5-S1"},
                {"artifact_path": "standards/legacy.md", "locator_id": "V5-S2"},
            ],
            "records": [
                {
                    "artifact_path": "standards/legacy.md",
                    "locator_id": "V5-S1",
                    "status": "ACTIVE_MAPPED",
                    "target_control_id": "P24-16",
                },
                {
                    "artifact_path": "standards/legacy.md",
                    "locator_id": "V5-S2",
                    "status": "SUPERSEDED",
                    "target_control_id": None,
                },
            ],
        }

    def tearDown(self):
        self.tmp.cleanup()

    def _descriptor(self, control_id, locator_id, heading, digest):
        return {
            "control_id": control_id,
            "normative_artifact_path": "standards/current.md",
            "normative_artifact_blob_sha": git_blob_sha_bytes(self.current_text.encode()),
            "clause_locator": {"locator_id": locator_id, "heading": heading},
            "clause_sha256": digest,
            "inherited_predecessor_control_ids": [],
            "authority_bearing_predicate_ids": [],
            "phase_severity_endpoint_mappings": [],
            "applicability_rules": [{"type": "ALWAYS"}],
            "required_proof_fields": [],
            "protected_mutation_strength_class": "ROOT_GOVERNED_NON_WEAKENING",
            "effective_generation": "V24",
            "effective_sequence": 1,
        }

    def validate(self, manifest=None, catalog=None, legacy=None):
        return validate_normative_catalog(
            repo_root=self.root,
            artifact_manifest=manifest or self.manifest,
            control_catalog=catalog or self.catalog,
            legacy_qualification=legacy or self.legacy,
        )

    def test_positive_closed_world_bundle_qualifies(self):
        result = self.validate()
        self.assertTrue(result["qualified"], result["problems"])
        self.assertEqual("NORMATIVE_CONTROL_CATALOG_QUALIFIED", result["state"])
        self.assertEqual(2, result["descriptor_count"])
        self.assertEqual(2, result["legacy_record_count"])

    def test_missing_descriptor_blocks(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["descriptors"].pop()
        result = self.validate(catalog=catalog)
        self.assertFalse(result["qualified"])
        self.assertTrue(any(x.startswith("CATALOG_REQUIRED_LOCATOR_UNMAPPED") for x in result["problems"]))

    def test_descriptor_cannot_target_reference_artifact(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["artifacts"][0]["classification"] = "NONAUTHORITATIVE_REFERENCE"
        manifest["artifacts"][0]["required_clause_locators"] = []
        result = self.validate(manifest=manifest)
        self.assertFalse(result["qualified"])
        self.assertTrue(any(x.startswith("DESCRIPTOR_TARGETS_NONAUTHORITATIVE_ARTIFACT") for x in result["problems"]))

    def test_blob_mismatch_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["artifacts"][0]["blob_sha"] = "0" * 40
        result = self.validate(manifest=manifest)
        self.assertFalse(result["qualified"])
        self.assertIn("MANIFEST_BLOB_MISMATCH:standards/current.md", result["problems"])

    def test_duplicate_control_id_blocks(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["descriptors"].append(copy.deepcopy(catalog["descriptors"][0]))
        result = self.validate(catalog=catalog)
        self.assertFalse(result["qualified"])
        self.assertIn("DESCRIPTOR_CONTROL_ID_DUPLICATE:P24-16", result["problems"])

    def test_clause_digest_mismatch_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["artifacts"][0]["required_clause_locators"][0]["clause_sha256"] = "0" * 64
        result = self.validate(manifest=manifest)
        self.assertFalse(result["qualified"])
        self.assertTrue(any("CLAUSE_SHA_MISMATCH" in x for x in result["problems"]))

    def test_legacy_inventory_must_be_fully_qualified(self):
        legacy = copy.deepcopy(self.legacy)
        legacy["records"].pop()
        result = self.validate(legacy=legacy)
        self.assertFalse(result["qualified"])
        self.assertIn("LEGACY_INVENTORY_UNQUALIFIED:standards/legacy.md:V5-S2", result["problems"])

    def test_active_legacy_mapping_must_target_known_descriptor(self):
        legacy = copy.deepcopy(self.legacy)
        legacy["records"][0]["target_control_id"] = "UNKNOWN"
        result = self.validate(legacy=legacy)
        self.assertFalse(result["qualified"])
        self.assertIn("LEGACY_ACTIVE_TARGET_INVALID:standards/legacy.md:V5-S1", result["problems"])

    def test_superseded_legacy_clause_may_not_claim_target(self):
        legacy = copy.deepcopy(self.legacy)
        legacy["records"][1]["target_control_id"] = "P24-17"
        result = self.validate(legacy=legacy)
        self.assertFalse(result["qualified"])
        self.assertIn("LEGACY_NONACTIVE_TARGET_PRESENT:standards/legacy.md:V5-S2", result["problems"])

    def test_reference_artifact_may_not_declare_normative_locator(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["artifacts"][2]["required_clause_locators"] = [
            {"locator_id": "X", "heading": "## X", "clause_sha256": "0" * 64}
        ]
        result = self.validate(manifest=manifest)
        self.assertFalse(result["qualified"])
        self.assertIn("REFERENCE_ARTIFACT_HAS_NORMATIVE_LOCATORS:standards/reference.md", result["problems"])

    def test_path_traversal_blocks(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["artifacts"][0]["path"] = "../escape.md"
        result = self.validate(manifest=manifest)
        self.assertFalse(result["qualified"])
        self.assertIn("MANIFEST_ARTIFACT_PATH_INVALID", result["problems"])

    def test_generation_mismatch_blocks(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["governance_generation"] = "V25"
        result = self.validate(catalog=catalog)
        self.assertFalse(result["qualified"])
        self.assertIn("CATALOG_GENERATION_MISMATCH", result["problems"])


if __name__ == "__main__":
    unittest.main()
