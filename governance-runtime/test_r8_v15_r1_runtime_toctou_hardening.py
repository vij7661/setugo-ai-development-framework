"""Deterministic tests for the descriptor-based governed file read."""
from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import r8_v15_r1_frozen_schema_runtime as runtime


class RuntimeFileReadTests(unittest.TestCase):
    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY") and hasattr(os, "O_CLOEXEC"), "descriptor/cloexec capability unavailable")
    def test_open_flags_include_cloexec_for_root_intermediate_and_final(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as td:
            root = Path(td); nested = root / "nested"; nested.mkdir(); (nested / "x").write_bytes(b"ok")
            original_open = os.open
            calls = []
            def capture(path, flags, *args, **kwargs):
                calls.append(flags)
                return original_open(path, flags, *args, **kwargs)
            with mock.patch.object(os, "open", side_effect=capture):
                self.assertEqual(runtime.read_confined_file(root, nested / "x"), b"ok")
            self.assertEqual(len(calls), 3)
            self.assertTrue(all(flags & os.O_CLOEXEC for flags in calls))

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"), "descriptor walk unsupported")
    def test_intermediate_open_failure_closes_root_descriptor(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as td:
            root = Path(td)
            close_calls = []
            with mock.patch.object(os, "open", side_effect=[101, OSError("intermediate")]), \
                 mock.patch.object(os, "close", side_effect=lambda fd: close_calls.append(fd)):
                with self.assertRaises(runtime.FrozenSchemaError) as cm:
                    runtime.read_confined_file(root, root / "sub" / "file")
            self.assertEqual(cm.exception.code, "ARTIFACT_OPEN_FAILED")
            self.assertEqual(close_calls, [101])

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"), "descriptor walk unsupported")
    def test_final_open_failure_closes_root_descriptor(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as td:
            root = Path(td)
            close_calls = []
            with mock.patch.object(os, "open", side_effect=[102, OSError("final")]), \
                 mock.patch.object(os, "close", side_effect=lambda fd: close_calls.append(fd)):
                with self.assertRaises(runtime.FrozenSchemaError) as cm:
                    runtime.read_confined_file(root, root / "file")
            self.assertEqual(cm.exception.code, "ARTIFACT_OPEN_FAILED")
            self.assertEqual(close_calls, [102])

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"), "descriptor walk unsupported")
    def test_primary_open_error_survives_close_error(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as td:
            root = Path(td)
            with mock.patch.object(os, "open", side_effect=[103, OSError("final")]), \
                 mock.patch.object(os, "close", side_effect=OSError("close")):
                with self.assertRaises(runtime.FrozenSchemaError) as cm:
                    runtime.read_confined_file(root, root / "file")
            self.assertEqual(cm.exception.code, "ARTIFACT_OPEN_FAILED")

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW"), "platform has no O_NOFOLLOW")
    def test_regular_file_single_descriptor_read(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as td:
            path = Path(td) / "x"
            path.write_bytes(b"stable")
            self.assertEqual(runtime.read_confined_file(Path(td), path), b"stable")

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW"), "platform has no O_NOFOLLOW")
    def test_directory_rejected_as_non_regular(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as td:
            with self.assertRaises(runtime.FrozenSchemaError) as cm:
                runtime.read_confined_file(Path(td).parent, Path(td))
            self.assertEqual(cm.exception.code, "ARTIFACT_NOT_REGULAR")

    def test_no_follow_capability_is_required(self):
        original = getattr(os, "O_NOFOLLOW", None)
        if original is None:
            with self.assertRaises(runtime.FrozenSchemaError) as cm:
                runtime.read_confined_file(Path("."), Path("does-not-matter"))
            self.assertEqual(cm.exception.code, "NOFOLLOW_UNSUPPORTED")
            return
        try:
            delattr(os, "O_NOFOLLOW")
            with self.assertRaises(runtime.FrozenSchemaError) as cm:
                runtime.read_confined_file(Path("."), Path("does-not-matter"))
            self.assertEqual(cm.exception.code, "NOFOLLOW_UNSUPPORTED")
        finally:
            setattr(os, "O_NOFOLLOW", original)

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW"), "platform has no O_NOFOLLOW")
    def test_symlink_target_is_rejected_when_supported(self):
        if not hasattr(os, "symlink") or not hasattr(os, "O_NOFOLLOW"):
            self.skipTest("symlink/no-follow unsupported")
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as td:
            root = Path(td)
            target = root / "target"
            link = root / "link"
            target.write_bytes(b"outside")
            try:
                link.symlink_to(target)
            except OSError:
                self.skipTest("symlink creation unavailable")
            with self.assertRaises(runtime.FrozenSchemaError):
                runtime.read_confined_file(root, link)

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"), "descriptor walk unsupported")
    def test_parent_symlink_substitution_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as td:
            root = Path(td); safe = root / "safe"; safe.mkdir(); (safe / "x").write_bytes(b"ok")
            outside = root / "outside"; outside.mkdir(); (outside / "x").write_bytes(b"bad")
            link = root / "alias"
            try: link.symlink_to(safe, target_is_directory=True)
            except OSError: self.skipTest("symlink creation unavailable")
            with self.assertRaises(runtime.FrozenSchemaError): runtime.read_confined_file(root, link / "x")

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY"), "descriptor walk unsupported")
    def test_non_regular_final_object_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as td:
            root = Path(td); (root / "subdir").mkdir()
            with self.assertRaises(runtime.FrozenSchemaError) as cm: runtime.read_confined_file(root, root / "subdir")
            self.assertEqual(cm.exception.code, "ARTIFACT_NOT_REGULAR")


if __name__ == "__main__":
    unittest.main()
