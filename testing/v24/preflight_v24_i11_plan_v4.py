from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V24 = ROOT / "testing" / "v24"
BINDING = V24 / "V24-I11-FALSIFICATION-PLAN-V4-REVIEW-BINDING.json"
PAYLOAD = V24 / "WDPC-V24-I11-FALSIFICATION-PLAN-V4-PACKET.gz.b64"

SOURCE_BLOBS = {
    "experiments/governed-platform/conversation-drift-parent-child-falsification-v24-extension.md": "0f52617114f7d9d549d9822f11d5bc0156c6e676",
    "experiments/governed-platform/conversation-drift-parent-child-falsification-v24-runtime-extension.md": "ff8677ca1170f5cef6318662309ba119145e68cf",
    "experiments/governed-platform/conversation-drift-parent-child-falsification-v24-functional-closure-extension.md": "17bfa33f6388934d47323cea3c375466c178aadf",
    "experiments/governed-platform/conversation-drift-parent-child-falsification-v24-bootstrap-perimeter-extension.md": "042b881795929f9e8d9ff5bb72f8eda8ca93fad0",
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    packet = gzip.decompress(base64.b64decode(PAYLOAD.read_text(encoding="ascii")))

    assert hashlib.sha256(packet).hexdigest() == binding["packet_sha256"]
    assert len(packet) == binding["packet_bytes"]
    assert len(PAYLOAD.read_text(encoding="ascii")) == binding["base64_payload_chars"]

    marker = b"\n---\n\n"
    assert packet.count(marker) == 1
    body = packet.split(marker, 1)[1]
    assert hashlib.sha256(body).hexdigest() == binding["plan_body_sha256"]

    text = packet.decode("utf-8")
    assert "Falsification Plan V4" in text
    assert "this V4 review surface" in text
    assert "this V2 review surface" not in text
    assert "this V3 review surface" not in text
    assert "REVIEW_REQUIRED / NOT_EXECUTED" in text

    matrix = text.split("## 12. Case audit matrix", 1)[1].split("## 13. Clustering", 1)[0]
    ids = re.findall(r"^\| WDPC-(\d{3}) \|", matrix, flags=re.M)
    assert len(ids) == 76
    assert {int(x) for x in ids} == set(range(431, 507))

    for cid in ("469", "495"):
        line = next(line for line in matrix.splitlines() if line.startswith(f"| WDPC-{cid} |"))
        assert "`BLOCKED_STATUS`" in line
        assert line.count("`BLOCKED_BY_I1_SEMANTIC_QUALIFICATION`") >= 2
        assert "GovernedEndpointObservation" not in line

    line457 = next(line for line in matrix.splitlines() if line.startswith("| WDPC-457 |"))
    assert "`CONJUNCTIVE_ASSERTION`" in line457
    assert "AUTHORITY_EVIDENCE_SOURCE_INVALID" in line457
    assert "HISTORICAL_RESULT_UNCHANGED" in line457

    assert binding["execution_status"] == "NOT_EXECUTED"
    assert binding["authority_effect"] == "NONE_EVIDENCE_ONLY"

    harness_blob = git("hash-object", binding["harness_path"])
    assert harness_blob == binding["harness_blob_sha"]

    design_tree = git("show", "-s", "--format=%T", binding["design_sha"])
    impl_tree = git("show", "-s", "--format=%T", binding["implementation_sha"])
    assert design_tree == binding["design_tree"]
    assert impl_tree == binding["implementation_tree"]

    for path, expected_blob in SOURCE_BLOBS.items():
        actual = git("rev-parse", f"{binding['design_sha']}:{path}")
        assert actual == expected_blob, (path, actual, expected_blob)

    print("V24_I11_PLAN_V4_PREFLIGHT_PASS")
    print("cases=76")
    print(f"packet_sha256={binding['packet_sha256']}")
    print(f"plan_body_sha256={binding['plan_body_sha256']}")
    print("execution_status=NOT_EXECUTED")
    print("authority_effect=NONE_EVIDENCE_ONLY")


if __name__ == "__main__":
    main()
