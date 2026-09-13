from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import v24_v6_external_execution_binding as r11


COMMIT = "1" * 40
TREE = "2" * 40


def _row(path: str, data: bytes, role: str) -> dict[str, str]:
    return {
        "path": path,
        "git_blob_sha1": r11.git_blob_sha(data),
        "raw_sha256": r11.raw_sha256(data),
        "role": role,
    }


def _pinset(rows: list[dict[str, str]], tests: list[str]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "authority_origin": "EXTERNAL_REVIEW_BRANCH",
        "candidate_self_grant": False,
        "candidate_commit": COMMIT,
        "candidate_tree": TREE,
        "interpreter_contract": {
            "isolated_mode": True,
            "safe_path": True,
            "ignore_environment": True,
            "no_site": True,
            "trusted_runner_outside_candidate_tree": True,
            "candidate_path_absent_at_interpreter_startup": True,
        },
        "admitted_python_files": rows,
        "executed_tests": tests,
    }


class ExternalExecutionBindingTests(unittest.TestCase):
    def _subject(self) -> tuple[tempfile.TemporaryDirectory[str], Path, dict[str, object]]:
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        g = root / "governance-runtime"
        g.mkdir(parents=True)
        prod = b"VALUE = 1\n"
        test = b"import unittest\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        self.assertEqual(1, 1)\n"
        (g / "v24_subject.py").write_bytes(prod)
        (g / "test_v24_subject.py").write_bytes(test)
        rows = [
            _row("governance-runtime/v24_subject.py", prod, "production"),
            _row("governance-runtime/test_v24_subject.py", test, "test"),
        ]
        return td, root, _pinset(rows, ["governance-runtime/test_v24_subject.py"])

    def test_valid_external_pinset_binds_exact_bytes(self) -> None:
        td, root, pinset = self._subject()
        with td:
            got = r11.validate_external_execution_pinset(
                repo_root=root,
                pinset=pinset,
                expected_candidate_commit=COMMIT,
                expected_candidate_tree=TREE,
            )
            self.assertTrue(got["valid"], got["problems"])
            self.assertEqual(2, got["bound_file_count"])
            self.assertEqual(1, got["executed_test_count"])
            self.assertFalse(got["qualified"])

    def test_candidate_self_grant_is_rejected(self) -> None:
        td, root, pinset = self._subject()
        with td:
            pinset["candidate_self_grant"] = True
            got = r11.validate_external_execution_pinset(repo_root=root, pinset=pinset)
            self.assertIn("EXTERNAL_PINSET_CANDIDATE_SELF_GRANT_FORBIDDEN", got["problems"])

    def test_wrong_authority_origin_is_rejected(self) -> None:
        td, root, pinset = self._subject()
        with td:
            pinset["authority_origin"] = "CANDIDATE_BRANCH"
            got = r11.validate_external_execution_pinset(repo_root=root, pinset=pinset)
            self.assertIn("EXTERNAL_PINSET_AUTHORITY_ORIGIN_INVALID", got["problems"])

    def test_same_path_different_test_bytes_is_rejected(self) -> None:
        td, root, pinset = self._subject()
        with td:
            path = root / "governance-runtime/test_v24_subject.py"
            path.write_text("raise SystemExit(0)\n", encoding="utf-8")
            got = r11.validate_external_execution_pinset(repo_root=root, pinset=pinset)
            self.assertIn(
                "EXTERNAL_PINSET_GIT_BLOB_MISMATCH:governance-runtime/test_v24_subject.py",
                got["problems"],
            )
            self.assertIn(
                "EXTERNAL_PINSET_RAW_SHA256_MISMATCH:governance-runtime/test_v24_subject.py",
                got["problems"],
            )

    def test_executed_test_must_be_pinned(self) -> None:
        td, root, pinset = self._subject()
        with td:
            pinset["executed_tests"] = ["governance-runtime/test_missing.py"]
            got = r11.validate_external_execution_pinset(repo_root=root, pinset=pinset)
            self.assertIn(
                "EXTERNAL_PINSET_EXECUTED_TEST_UNPINNED:governance-runtime/test_missing.py",
                got["problems"],
            )

    def test_executed_test_role_must_be_test(self) -> None:
        td, root, pinset = self._subject()
        with td:
            rows = pinset["admitted_python_files"]
            assert isinstance(rows, list)
            rows[1]["role"] = "dependency"
            got = r11.validate_external_execution_pinset(repo_root=root, pinset=pinset)
            self.assertIn(
                "EXTERNAL_PINSET_EXECUTED_TEST_ROLE_INVALID:governance-runtime/test_v24_subject.py",
                got["problems"],
            )

    def test_unittest_shadow_is_rejected_even_when_pinned(self) -> None:
        td, root, pinset = self._subject()
        with td:
            data = b"raise RuntimeError('shadow')\n"
            path = root / "governance-runtime/unittest.py"
            path.write_bytes(data)
            rows = pinset["admitted_python_files"]
            assert isinstance(rows, list)
            rows.append(_row("governance-runtime/unittest.py", data, "dependency"))
            got = r11.validate_external_execution_pinset(repo_root=root, pinset=pinset)
            self.assertIn(
                "EXTERNAL_PINSET_BOOTSTRAP_SHADOW_REJECTED:governance-runtime/unittest.py",
                got["problems"],
            )

    def test_sitecustomize_shadow_is_rejected(self) -> None:
        td, root, pinset = self._subject()
        with td:
            data = b"raise RuntimeError('startup')\n"
            path = root / "governance-runtime/sitecustomize.py"
            path.write_bytes(data)
            rows = pinset["admitted_python_files"]
            assert isinstance(rows, list)
            rows.append(_row("governance-runtime/sitecustomize.py", data, "dependency"))
            got = r11.validate_external_execution_pinset(repo_root=root, pinset=pinset)
            self.assertIn(
                "EXTERNAL_PINSET_BOOTSTRAP_SHADOW_REJECTED:governance-runtime/sitecustomize.py",
                got["problems"],
            )

    def test_usercustomize_shadow_is_rejected(self) -> None:
        td, root, pinset = self._subject()
        with td:
            data = b"raise RuntimeError('startup')\n"
            path = root / "governance-runtime/usercustomize.py"
            path.write_bytes(data)
            rows = pinset["admitted_python_files"]
            assert isinstance(rows, list)
            rows.append(_row("governance-runtime/usercustomize.py", data, "dependency"))
            got = r11.validate_external_execution_pinset(repo_root=root, pinset=pinset)
            self.assertIn(
                "EXTERNAL_PINSET_BOOTSTRAP_SHADOW_REJECTED:governance-runtime/usercustomize.py",
                got["problems"],
            )

    def test_stdlib_shadow_is_rejected(self) -> None:
        td, root, pinset = self._subject()
        with td:
            data = b"VALUE = 'shadow'\n"
            path = root / "governance-runtime/json.py"
            path.write_bytes(data)
            rows = pinset["admitted_python_files"]
            assert isinstance(rows, list)
            rows.append(_row("governance-runtime/json.py", data, "dependency"))
            got = r11.validate_external_execution_pinset(repo_root=root, pinset=pinset)
            self.assertIn(
                "EXTERNAL_PINSET_STDLIB_SHADOW_REJECTED:governance-runtime/json.py",
                got["problems"],
            )

    def test_candidate_identity_mismatch_is_rejected(self) -> None:
        td, root, pinset = self._subject()
        with td:
            got = r11.validate_external_execution_pinset(
                repo_root=root,
                pinset=pinset,
                expected_candidate_commit="3" * 40,
                expected_candidate_tree="4" * 40,
            )
            self.assertIn("EXTERNAL_PINSET_CANDIDATE_COMMIT_MISMATCH", got["problems"])
            self.assertIn("EXTERNAL_PINSET_CANDIDATE_TREE_MISMATCH", got["problems"])

    def test_sandbox_rejects_unpinned_python_file(self) -> None:
        td, root, pinset = self._subject()
        with td:
            extra = root / "governance-runtime/extra_candidate_file.py"
            extra.write_text("VALUE = 2\n", encoding="utf-8")
            got = r11.validate_staged_execution_sandbox(sandbox_root=root, pinset=pinset)
            self.assertIn(
                "EXTERNAL_SANDBOX_UNPINNED_FILE_PRESENT:governance-runtime/extra_candidate_file.py",
                got["problems"],
            )

    def test_sandbox_exact_file_set_passes(self) -> None:
        td, root, pinset = self._subject()
        with td:
            got = r11.validate_staged_execution_sandbox(sandbox_root=root, pinset=pinset)
            self.assertTrue(got["valid"], got["problems"])
            self.assertEqual(got["expected_python_file_count"], got["actual_python_file_count"])

    def test_symlink_bound_file_is_rejected(self) -> None:
        if not hasattr(Path, "symlink_to"):
            self.skipTest("symlink unsupported")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            g = root / "governance-runtime"
            g.mkdir(parents=True)
            target = g / "real.py"
            target.write_text("VALUE = 1\n", encoding="utf-8")
            link = g / "test_v24_link.py"
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("symlink creation unavailable")
            data = target.read_bytes()
            pinset = _pinset(
                [_row("governance-runtime/test_v24_link.py", data, "test")],
                ["governance-runtime/test_v24_link.py"],
            )
            got = r11.validate_external_execution_pinset(repo_root=root, pinset=pinset)
            self.assertIn(
                "EXTERNAL_PINSET_SYMLINK_REJECTED:governance-runtime/test_v24_link.py",
                got["problems"],
            )

    def test_scientific_execution_remains_closed(self) -> None:
        x = r11.construction_frontier()
        self.assertFalse(x["qualified"])
        self.assertTrue(x["external_authority_required"])
        self.assertEqual("CLOSED_PENDING_SUCCESSOR_REVIEW", x["scientific_execution_state"])
        self.assertEqual("NONE_EVIDENCE_ONLY", x["authority_effect"])


if __name__ == "__main__":
    unittest.main()
