"""Deterministic tests for the descriptor-based governed file read."""
from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).parent))
import r8_v15_r1_frozen_schema_runtime as runtime


class RuntimeFileReadTests(unittest.TestCase):
    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW"), "platform has no O_NOFOLLOW")
    def test_regular_file_single_descriptor_read(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as td:
            path = Path(td) / "x"
            path.write_bytes(b"stable")
            self.assertEqual(runtime._read_verified_file(path), b"stable")

    @unittest.skipUnless(hasattr(os, "O_NOFOLLOW"), "platform has no O_NOFOLLOW")
    def test_directory_rejected_as_non_regular(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as td:
            with self.assertRaises(runtime.FrozenSchemaError) as cm:
                runtime._read_verified_file(Path(td))
            self.assertEqual(cm.exception.code, "ARTIFACT_NOT_REGULAR")

    def test_no_follow_capability_is_required(self):
        original = getattr(os, "O_NOFOLLOW", None)
        if original is None:
            with self.assertRaises(runtime.FrozenSchemaError) as cm:
                runtime._read_verified_file(Path("does-not-matter"))
            self.assertEqual(cm.exception.code, "NOFOLLOW_UNSUPPORTED")
            return
        try:
            delattr(os, "O_NOFOLLOW")
            with self.assertRaises(runtime.FrozenSchemaError) as cm:
                runtime._read_verified_file(Path("does-not-matter"))
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
                runtime._read_verified_file(link)


if __name__ == "__main__":
    unittest.main()
