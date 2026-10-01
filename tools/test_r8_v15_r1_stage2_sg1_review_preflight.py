from __future__ import annotations
import hashlib, shutil, unittest
from unittest import mock
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from preflight_r8_v15_r1_stage2_sg1_review import validate_artifact

def assert_separate_packet_commands(text:str):
    if "\\n\\n" in text: raise ValueError("literal newline escape in executable block")
    commands=[line.strip() for line in text.replace("\r\n","\n").splitlines() if line.strip().startswith("python3 ")]
    validators=[c for c in commands if "validate_r8_v15_r1_stage2_sg1_activation_gate_parser.py" in c]
    preflights=[c for c in commands if "preflight_r8_v15_r1_stage2_sg1_review.py" in c]
    if len(validators)!=1 or len(preflights)!=1 or validators[0]==preflights[0]:raise ValueError("validator and preflight must be separate executable commands")

class ReviewPreflightTests(unittest.TestCase):
    def test_exact_artifact_binding(self):
        path = Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt")
        raw = path.read_bytes()
        blob = __import__("subprocess").check_output(["git", "rev-parse", f"HEAD:{path.as_posix()}"], text=True).strip()
        self.assertEqual(validate_artifact(path, expected_sha256=hashlib.sha256(raw).hexdigest(), expected_blob=blob)["status"], "PASS")

    def test_parseable_substitution_and_wrong_digest_reject(self):
        source = Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt")
        copy_path = Path("stage2-sg1-evidence") / "_substituted-review.txt"
        copy_path.parent.mkdir(exist_ok=True); shutil.copyfile(source, copy_path)
        try:
            with self.assertRaises(ValueError): validate_artifact(copy_path, expected_sha256="0" * 64)
        finally: copy_path.unlink(missing_ok=True)

    def test_invalid_utf8_is_controlled_failure(self):
        path = Path("stage2-sg1-evidence") / "_invalid-review.txt"
        path.parent.mkdir(exist_ok=True); path.write_bytes(b"\xff\xfe")
        try:
            with self.assertRaises(ValueError): validate_artifact(path)
        finally: path.unlink(missing_ok=True)

    def test_git_blob_lookup_failure_is_controlled(self):
        source = Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt")
        path = Path("stage2-sg1-evidence") / "_untracked-review.txt"
        path.parent.mkdir(exist_ok=True)
        try:
            path.write_bytes(source.read_bytes())
            with self.assertRaisesRegex(ValueError, "review Git blob lookup failed"):
                validate_artifact(path, expected_blob="0" * 40)
        finally:
            path.unlink(missing_ok=True)

    def test_review_workflows_bind_exact_artifacts(self):
        root = Path(".github/workflows")
        checks = {
            "r8-v15-r1-stage2-sg1-review-packet.yml": ("--expected-sha256", "--expected-blob"),
            "r8-v15-r1-stage2-sg1-review003-remediation-packet.yml": ("--expected-sha256", "--expected-blob"),
            "r8-v15-r1-stage2-sg1-review004-remediation-packet.yml": ("--expected-sha256", "--expected-blob"),
        }
        for name, needles in checks.items():
            workflow=(root/name).read_text(encoding="utf-8");assert_separate_packet_commands(workflow);lines=workflow.splitlines()
            commands = []
            for i, line in enumerate(lines):
                if "preflight_r8_v15_r1_stage2_sg1_review.py" in line:
                    commands.append(" ".join(lines[i:i + 4]))
            self.assertTrue(commands)
            for command in commands:
                for needle in needles:
                    self.assertIn(needle, command)

    def test_literal_backslash_newline_packaging_fails(self):
        good=Path(".github/workflows/r8-v15-r1-stage2-sg1-review003-remediation-packet.yml").read_text(encoding="utf-8")
        broken=good.replace("\n\n          python3 tools/preflight_","\\n\\n          python3 tools/preflight_",1)
        with self.assertRaises(ValueError):assert_separate_packet_commands(broken)

    def test_validate_artifact_reads_one_raw_stream(self):
        path = Path("governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-002.txt")
        raw = path.read_bytes()
        blob = __import__("subprocess").check_output(["git", "rev-parse", f"HEAD:{path.as_posix()}"], text=True).strip()
        with mock.patch.object(Path, "read_bytes", wraps=path.read_bytes) as read:
            self.assertEqual(validate_artifact(path, expected_sha256=hashlib.sha256(raw).hexdigest(), expected_blob=blob)["status"], "PASS")
            self.assertEqual(read.call_count, 1)

if __name__ == "__main__": unittest.main()
