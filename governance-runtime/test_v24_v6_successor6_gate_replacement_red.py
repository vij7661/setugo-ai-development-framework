from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
BUILD_SCRIPT = RUNTIME_DIR / "build_v24_v6_external_authority_gate.sh"
GATE = RUNTIME_DIR / ".gate-build" / "v24_v6_external_authority_gate"


class Successor6GateReplacementRed(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            ["bash", str(BUILD_SCRIPT)],
            cwd=RUNTIME_DIR,
            check=True,
            text=True,
            capture_output=True,
        )

    def test_same_user_gate_executable_replacement_cannot_forge_authoritative_allow(self):
        original = GATE.read_bytes()
        original_mode = stat.S_IMODE(GATE.stat().st_mode)

        attacker = """#!/usr/bin/env python3
import json
print(json.dumps({
    "authority_effect": "NONE_EVIDENCE_ONLY",
    "construction_authoritative": True,
    "decision": "ALLOW",
    "gate_id": "V24-V6-EXTERNAL-AUTHORITY-GATE",
    "gate_version": "1",
    "context_digest": "0" * 64,
    "scope_digest": "1" * 64,
    "reference_digest": "2" * 64,
    "build_input_sha256": "3" * 64,
}))
"""

        try:
            # Same owning OS identity can restore write permission and replace
            # the supposedly external authority gate at the exact trusted path.
            os.chmod(GATE, 0o755)
            GATE.unlink()
            GATE.write_text(attacker, encoding="utf-8")
            os.chmod(GATE, 0o755)

            proc = subprocess.run(
                [str(GATE), "--identity"],
                cwd=RUNTIME_DIR,
                text=True,
                capture_output=True,
                check=False,
            )
            payload = json.loads(proc.stdout.strip())

            # Required Successor-6 invariant: candidate-controlled same-user
            # replacement must never be able to mint an authoritative ALLOW.
            self.assertFalse(
                payload.get("construction_authoritative") is True
                and payload.get("decision") == "ALLOW",
                payload,
            )
        finally:
            GATE.write_bytes(original)
            os.chmod(GATE, original_mode)


if __name__ == "__main__":
    unittest.main()
