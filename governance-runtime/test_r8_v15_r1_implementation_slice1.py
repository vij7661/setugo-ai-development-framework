import hashlib
import importlib
import json
import shutil
import socket
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))

FROZEN_CANDIDATE = "f93ca26975ecb64f0da13779889c75b36140cdfc"
FROZEN_SPM_SHA256 = "84c484121c4c8dd0592bcd7e4c070d8a3ab7f17215f4c3d2b31863fb6dbf6797"
FROZEN_SEMANTIC = "1fa49fa4adfa6aa47fae68c0f1938083eeb1497f"
SCHEMA_DIR = REPO_ROOT / "schemas" / "governance-r8" / "v15-r1"

try:
    runtime = importlib.import_module("r8_v15_r1_frozen_schema_runtime")
    IMPORT_ERROR = None
except Exception as exc:  # expected RED before mechanism implementation
    runtime = None
    IMPORT_ERROR = exc


def require_runtime():
    if runtime is None:
        raise AssertionError(f"MECHANISM_ABSENT: {IMPORT_ERROR!r}")
    return runtime


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Slice1FrozenAcceptance(unittest.TestCase):
    maxDiff = None

    def make_schema_fixture(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        dest = root / "schemas" / "governance-r8" / "v15-r1"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(SCHEMA_DIR, dest)
        return td, root, dest

    def test_i1_01_exact_frozen_tree_loads(self):
        m = require_runtime()
        bundle = m.FrozenSchemaRuntime(REPO_ROOT, candidate_sha=FROZEN_CANDIDATE).load()
        self.assertEqual(bundle["candidate_sha"], FROZEN_CANDIDATE)
        self.assertEqual(bundle["spm_sha256"], FROZEN_SPM_SHA256)
        self.assertEqual(bundle["semantic_candidate_sha"], FROZEN_SEMANTIC)
        self.assertEqual(bundle["authority_effect"], "NONE")
        self.assertFalse(bundle["runtime_qualified"])

    def test_i1_02_candidate_identity_mismatch_fails(self):
        m = require_runtime()
        with self.assertRaises(m.FrozenSchemaError) as cm:
            m.FrozenSchemaRuntime(REPO_ROOT, candidate_sha="0" * 40).load()
        self.assertEqual(cm.exception.code, "CANDIDATE_IDENTITY_MISMATCH")

    def test_i1_03_spm_digest_mismatch_or_missing_fails(self):
        m = require_runtime()
        td, root, schema = self.make_schema_fixture()
        self.addCleanup(td.cleanup)
        spm = schema / "schema-provenance-manifest-candidate.json"
        spm.write_bytes(spm.read_bytes() + b"\n")
        with self.assertRaises(m.FrozenSchemaError) as cm:
            m.FrozenSchemaRuntime(root, candidate_sha=FROZEN_CANDIDATE).load()
        self.assertEqual(cm.exception.code, "SPM_DIGEST_MISMATCH")

        td2, root2, schema2 = self.make_schema_fixture()
        self.addCleanup(td2.cleanup)
        (schema2 / "schema-provenance-manifest-candidate.json").unlink()
        with self.assertRaises(m.FrozenSchemaError) as cm2:
            m.FrozenSchemaRuntime(root2, candidate_sha=FROZEN_CANDIDATE).load()
        self.assertEqual(cm2.exception.code, "REQUIRED_ARTIFACT_MISSING")

    def test_i1_04_covered_artifact_tamper_fails_before_bundle_return(self):
        m = require_runtime()
        td, root, schema = self.make_schema_fixture()
        self.addCleanup(td.cleanup)
        target = schema / "runtime-contracts.schema.json"
        target.write_bytes(target.read_bytes() + b"\n")
        with self.assertRaises(m.FrozenSchemaError) as cm:
            m.FrozenSchemaRuntime(root, candidate_sha=FROZEN_CANDIDATE).load()
        self.assertEqual(cm.exception.code, "ARTIFACT_DIGEST_MISMATCH")
        self.assertIn("runtime-contracts.schema.json", str(cm.exception))

    def test_i1_05_spm_coverage_must_be_empty(self):
        m = require_runtime()
        spm = load_json(SCHEMA_DIR / "schema-provenance-manifest-candidate.json")
        spm["coverage"]["uncovered_semantic_elements"] = ["/synthetic"]
        with self.assertRaises(m.FrozenSchemaError) as cm:
            m.validate_spm_document(spm)
        self.assertEqual(cm.exception.code, "SPM_COVERAGE_INCOMPLETE")

    def test_i1_06_generator_binding_mismatch_fails(self):
        m = require_runtime()
        spm = load_json(SCHEMA_DIR / "schema-provenance-manifest-candidate.json")
        spm["generator"]["generator_id"] = "ATTACKER"
        with self.assertRaises(m.FrozenSchemaError) as cm:
            m.validate_spm_document(spm)
        self.assertEqual(cm.exception.code, "GENERATOR_BINDING_MISMATCH")

    def test_i1_07_gcp_key_ordering_is_deterministic_and_nfc_aware(self):
        m = require_runtime()
        got = m.canonicalize_json_text('{"min":1,"max":2}', schema_context="object")
        self.assertEqual(got, b'{"max":2,"min":1}')
        got2 = m.canonicalize_json_text('{"b":1,"a":2}', schema_context="object")
        self.assertEqual(got2, b'{"a":2,"b":1}')

    def test_i1_08_signed_int64_bounds(self):
        m = require_runtime()
        self.assertEqual(m.canonicalize_json_text("-9223372036854775808", schema_context="integer_range"),
                         b"-9223372036854775808")
        self.assertEqual(m.canonicalize_json_text("9223372036854775807", schema_context="integer_range"),
                         b"9223372036854775807")
        for text in ("-9223372036854775809", "9223372036854775808"):
            with self.assertRaises(m.GCPError) as cm:
                m.canonicalize_json_text(text, schema_context="integer_range")
            self.assertEqual(cm.exception.code, "GCP_REJECT_OUT_OF_INT64")

    def test_i1_09_p05_exact_bytes_and_digest(self):
        m = require_runtime()
        gcp = load_json(SCHEMA_DIR / "gcp-rvm-2.json")
        p05 = next(v for v in gcp["canonical_vectors"] if v["vector_id"] == "GCP-RVM2-P05")
        canonical = m.canonicalize_json_text(p05["input_representation"], schema_context=p05["schema_context"])
        self.assertEqual(canonical.decode("utf-8"), p05["expected_canonical_utf8"])
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), p05["expected_sha256"])
        self.assertEqual(
            p05["expected_sha256"],
            "161a1dcda7bae00f28f0ba32675f218fd4977065d2aa0439cf451c6d066dbbfb",
        )

    def test_i1_10_all_positive_gcp_vectors_recompute(self):
        m = require_runtime()
        gcp = load_json(SCHEMA_DIR / "gcp-rvm-2.json")
        observed = m.recompute_positive_vectors(gcp)
        self.assertEqual(set(observed), {v["vector_id"] for v in gcp["canonical_vectors"]})
        for v in gcp["canonical_vectors"]:
            self.assertEqual(observed[v["vector_id"]]["canonical_utf8"], v["expected_canonical_utf8"])
            self.assertEqual(observed[v["vector_id"]]["sha256"], v["expected_sha256"])

    def test_i1_11_duplicate_and_nfc_collision_reject(self):
        m = require_runtime()
        cases = [
            ('{"a":1,"a":2}', "object_parse", "GCP_REJECT_DUPLICATE_KEY"),
            ('{"é":1,"e\\u0301":2}', "object_key_NFC_collision", "GCP_REJECT_NFC_KEY_COLLISION"),
        ]
        for text, context, code in cases:
            with self.subTest(code=code):
                with self.assertRaises(m.GCPError) as cm:
                    m.canonicalize_json_text(text, schema_context=context)
                self.assertEqual(cm.exception.code, code)

    def test_i1_12_unicode_and_frozen_rejection_vectors_reject_with_exact_codes(self):
        m = require_runtime()
        gcp = load_json(SCHEMA_DIR / "gcp-rvm-2.json")
        for v in gcp["rejection_vectors"]:
            with self.subTest(vector=v["vector_id"]):
                with self.assertRaises(m.GCPError) as cm:
                    m.canonicalize_json_text(v["input_representation"], schema_context=v["schema_context"])
                self.assertEqual(cm.exception.code, v["expected_rejection_code"])

    def test_i1_13_missing_required_core_artifact_fails_closed(self):
        m = require_runtime()
        required = [
            "runtime-contracts.schema.json",
            "gcp-rvm-2.json",
            "schema-freeze-validator-contract.json",
            "schema-freeze-traceability.json",
            "schema-provenance-source-map.json",
        ]
        for name in required:
            with self.subTest(name=name):
                td, root, schema = self.make_schema_fixture()
                try:
                    (schema / name).unlink()
                    with self.assertRaises(m.FrozenSchemaError) as cm:
                        m.FrozenSchemaRuntime(root, candidate_sha=FROZEN_CANDIDATE).load()
                    self.assertEqual(cm.exception.code, "REQUIRED_ARTIFACT_MISSING")
                finally:
                    td.cleanup()

    def test_i1_14_loader_is_read_only_and_network_free(self):
        m = require_runtime()
        before = {p.relative_to(REPO_ROOT).as_posix(): sha256_file(p)
                  for p in SCHEMA_DIR.rglob("*") if p.is_file()}
        with mock.patch.object(socket, "socket", side_effect=AssertionError("network forbidden")):
            bundle = m.FrozenSchemaRuntime(REPO_ROOT, candidate_sha=FROZEN_CANDIDATE).load()
            self.assertEqual(bundle["authority_effect"], "NONE")
        after = {p.relative_to(REPO_ROOT).as_posix(): sha256_file(p)
                 for p in SCHEMA_DIR.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_i1_15_claim_boundary_is_non_authoritative(self):
        m = require_runtime()
        bundle = m.FrozenSchemaRuntime(REPO_ROOT, candidate_sha=FROZEN_CANDIDATE).load()
        self.assertEqual(bundle["authority_effect"], "NONE")
        self.assertFalse(bundle["runtime_qualified"])
        self.assertFalse(bundle["release_authorized"])
        self.assertFalse(bundle["deployment_authorized"])
        self.assertFalse(bundle["production_authorized"])
        self.assertFalse(bundle["terminal_authority"])

    def test_i1_16_failure_does_not_poison_fresh_valid_load(self):
        m = require_runtime()
        with self.assertRaises(m.GCPError):
            m.canonicalize_json_text("9223372036854775808", schema_context="integer_range")
        with self.assertRaises(m.FrozenSchemaError):
            m.FrozenSchemaRuntime(REPO_ROOT, candidate_sha="f" * 40).load()

        canonical = m.canonicalize_json_text('{"b":1,"a":2}', schema_context="object")
        self.assertEqual(canonical, b'{"a":2,"b":1}')
        bundle = m.FrozenSchemaRuntime(REPO_ROOT, candidate_sha=FROZEN_CANDIDATE).load()
        self.assertEqual(bundle["spm_sha256"], FROZEN_SPM_SHA256)


if __name__ == "__main__":
    unittest.main()
