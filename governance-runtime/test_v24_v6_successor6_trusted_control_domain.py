from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_v24_v6_proof_reference_closure import ROOT_CONTENT, proof_bundle

TRUSTED_ROOT = Path(os.environ.get("V24_V6_TRUSTED_ROOT", "/opt/v24-v6-trusted-runtime"))
GATE = TRUSTED_ROOT / ".gate-build" / "v24_v6_external_authority_gate"
BUILD_JSON = TRUSTED_ROOT / ".gate-build" / "v24_v6_external_authority_gate_build.json"
WORKER = TRUSTED_ROOT / "v24_v6_external_gate_worker.py"
GATE_ID = "V24-V6-EXTERNAL-AUTHORITY-GATE"
GATE_VERSION = "1"


def _write_bundle(directory: Path, context: dict, boundary: dict) -> tuple[Path, Path]:
    context_path = directory / "context.json"
    boundary_path = directory / "boundary.json"
    context_path.write_text(
        json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    boundary_path.write_text(
        json.dumps(boundary, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return context_path, boundary_path


class Successor6TrustedControlDomainTests(unittest.TestCase):
    def test_candidate_identity_is_unprivileged(self):
        self.assertNotEqual(os.geteuid(), 0)
        sudo = shutil.which("sudo")
        if sudo:
            proc = subprocess.run(
                [sudo, "-n", "true"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)

    def test_trusted_gate_and_runtime_are_root_owned_nonwritable(self):
        for path in (TRUSTED_ROOT, TRUSTED_ROOT / ".gate-build"):
            st = path.stat()
            self.assertEqual(st.st_uid, 0, path)
            self.assertTrue(stat.S_ISDIR(st.st_mode), path)
            self.assertEqual(st.st_mode & 0o222, 0, oct(st.st_mode))

        for path in (GATE, WORKER):
            st = path.stat()
            self.assertEqual(st.st_uid, 0, path)
            self.assertTrue(stat.S_ISREG(st.st_mode), path)
            self.assertEqual(st.st_mode & 0o222, 0, oct(st.st_mode))

    def test_same_user_gate_executable_replacement_rejected(self):
        with self.assertRaises(PermissionError):
            os.chmod(GATE, 0o755)
        with self.assertRaises(PermissionError):
            GATE.unlink()
        with self.assertRaises(PermissionError):
            GATE.write_bytes(b"attacker")

    def test_gate_parent_directory_rename_unlink_replacement_rejected(self):
        fake = Path(tempfile.gettempdir()) / f"fake-gate-{os.getpid()}"
        fake.write_text("#!/bin/sh\necho forged\n", encoding="utf-8")
        fake.chmod(0o755)
        try:
            with self.assertRaises(PermissionError):
                os.replace(fake, GATE)
            with self.assertRaises(PermissionError):
                (TRUSTED_ROOT / ".gate-build").rename(
                    TRUSTED_ROOT / ".gate-build-attacker"
                )
        finally:
            fake.unlink(missing_ok=True)

    def test_pinned_source_post_measurement_substitution_rejected_by_permissions(self):
        with self.assertRaises(PermissionError):
            WORKER.write_text("print('forged')\n", encoding="utf-8")
        with self.assertRaises(PermissionError):
            os.chmod(WORKER, 0o644)

    def test_copied_gate_at_caller_selected_path_is_nonauthoritative(self):
        with tempfile.TemporaryDirectory() as td:
            copied = Path(td) / GATE.name
            shutil.copy2(GATE, copied)
            copied.chmod(0o555)
            proc = subprocess.run(
                [str(copied), "--identity"],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout.strip())
        self.assertEqual(payload["decision"], "DENY")
        self.assertEqual(payload["reason"], "TRUSTED_GATE_CONTROL_DOMAIN_INVALID")

    def test_live_gate_digest_matches_root_owned_build_manifest(self):
        manifest = json.loads(BUILD_JSON.read_text(encoding="utf-8"))
        actual = hashlib.sha256(GATE.read_bytes()).hexdigest()
        self.assertEqual(actual, manifest["binary_sha256"])

    def test_trusted_gate_positive(self):
        context, boundary, refs = proof_bundle()
        with tempfile.TemporaryDirectory() as td:
            context_path, boundary_path = _write_bundle(Path(td), context, boundary)
            proc = subprocess.run(
                [
                    str(GATE),
                    "resolve-governed",
                    str(context_path),
                    str(boundary_path),
                    refs["root"],
                    "ROOT-VERIFIER",
                    ROOT_CONTENT,
                    GATE_ID,
                    GATE_VERSION,
                    "enforce",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(proc.returncode, 0, (proc.stdout, proc.stderr))
        payload = json.loads(proc.stdout.strip())
        self.assertEqual(payload["decision"], "ALLOW")
        self.assertTrue(payload["construction_authoritative"])
        self.assertEqual(payload["gate_id"], GATE_ID)
        self.assertEqual(payload["gate_version"], GATE_VERSION)


if __name__ == "__main__":
    unittest.main()
