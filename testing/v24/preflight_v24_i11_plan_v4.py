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
MANIFEST = V24 / "WDPC-V24-I11-FALSIFICATION-PLAN-V4-PACKET-MANIFEST.json"

SOURCE_BLOBS = {
    "experiments/governed-platform/conversation-drift-parent-child-falsification-v24-extension.md": "0f52617114f7d9d549d9822f11d5bc0156c6e676",
    "experiments/governed-platform/conversation-drift-parent-child-falsification-v24-runtime-extension.md": "ff8677ca1170f5cef6318662309ba119145e68cf",
    "experiments/governed-platform/conversation-drift-parent-child-falsification-v24-functional-closure-extension.md": "17bfa33f6388934d47323cea3c375466c178aadf",
    "experiments/governed-platform/conversation-drift-parent-child-falsification-v24-bootstrap-perimeter-extension.md": "042b881795929f9e8d9ff5bb72f8eda8ca93fad0",
}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def parse_matrix_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def main() -> None:
    binding = json.loads(BINDING.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["format"] == "ordered_base64_chunks_of_gzip_packet"
    assert manifest["packet_sha256"] == binding["packet_sha256"]
    assert manifest["packet_bytes"] == binding["packet_bytes"]
    assert manifest["gzip_sha256"] == binding["payload_gzip_sha256"]
    assert len(manifest["chunks"]) == binding["payload_chunk_count"]

    chunks: list[str] = []
    for item in manifest["chunks"]:
        path = ROOT / item["path"]
        chunk = path.read_text(encoding="ascii")
        assert len(chunk) == item["chars"], item["path"]
        assert sha256_bytes(chunk.encode("ascii")) == item["sha256"], item["path"]
        chunks.append(chunk)

    payload = "".join(chunks)
    assert len(payload) == manifest["total_base64_chars"] == binding["payload_base64_chars"]
    gz = base64.b64decode(payload, validate=True)
    assert sha256_bytes(gz) == manifest["gzip_sha256"] == binding["payload_gzip_sha256"]
    packet = gzip.decompress(gz)

    assert sha256_bytes(packet) == binding["packet_sha256"]
    assert len(packet) == binding["packet_bytes"]

    marker = b"\n---\n\n"
    assert packet.count(marker) == 1
    body = packet.split(marker, 1)[1]
    assert sha256_bytes(body) == binding["plan_body_sha256"]

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
        cells = parse_matrix_row(line)
        assert len(cells) == 10
        assert cells[2] == "`BLOCKED_STATUS`"
        assert cells[3] == "`BLOCKED_BY_I1_SEMANTIC_QUALIFICATION`"
        assert cells[5] == "`NONE_WHILE_BLOCKED`"
        assert cells[9] == "`BLOCKED_BY_I1_SEMANTIC_QUALIFICATION`"

    line457 = next(line for line in matrix.splitlines() if line.startswith("| WDPC-457 |"))
    cells457 = parse_matrix_row(line457)
    assert cells457[2] == "`CONJUNCTIVE_ASSERTION`"
    assert "AUTHORITY_EVIDENCE_SOURCE_INVALID" in cells457[3]
    assert "HISTORICAL_RESULT_UNCHANGED" in cells457[3]

    assert binding["execution_status"] == "NOT_EXECUTED"
    assert binding["authority_effect"] == "NONE_EVIDENCE_ONLY"

    assert git("hash-object", binding["harness_path"]) == binding["harness_blob_sha"]
    assert git("show", "-s", "--format=%T", binding["design_sha"]) == binding["design_tree"]
    assert git("show", "-s", "--format=%T", binding["implementation_sha"]) == binding["implementation_tree"]

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
