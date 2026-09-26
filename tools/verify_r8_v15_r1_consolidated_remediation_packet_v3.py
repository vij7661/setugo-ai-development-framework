from __future__ import annotations
import hashlib, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKET = ROOT / "governance-r8/R8-V15-R1-CONSOLIDATED-REMEDIATION-52-REVIEW-PACKET-V3.txt"
BASE = "7cd2787d85b189a4161f271ee131e42bd961140a"
HEADS = {
    "42": "615e762f97753aa52fb4d4166c9cf3ad73baa91d",
    "43": "c42f18f07b84197836d42ac72c1d22d09f8ac774",
    "44": "424afbe9892aa8a9cc73fc530652662948d30dfc",
    "46": "a8add41bf17efe5c5129607c26f5546963a6eebe",
    "50": "6f6b063432fe5987600df2d508af8443e53d5e67",
}
FILES = {
    "42": [
        ".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml",
        ".github/workflows/r8-v15-r1-stage2-sg1-review-packet.yml",
        ".github/workflows/r8-v15-r1-stage2-sg1-review003-remediation-packet.yml",
        ".github/workflows/r8-v15-r1-stage2-sg1-review004-remediation-packet.yml",
        "tools/r8_v15_r1_review_contract_parser.py",
        "tools/preflight_r8_v15_r1_stage2_sg1_review.py",
        "tools/validate_r8_v15_r1_stage2_sg1_activation_gate_parser.py",
        "tools/test_r8_v15_r1_review_contract_parser.py",
        "tools/test_r8_v15_r1_stage2_sg1_review_preflight.py",
    ],
    "43": [
        "tools/r8_v15_r1_stage2_semantic_gap_inventory.py",
        "tools/test_r8_v15_r1_stage2_semantic_gap_inventory.py",
        "governance-r8/R8-V15-R1-STAGE2-SEMANTIC-GAP-INVENTORY.json",
    ],
    "44": [
        "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
        "governance-runtime/test_r8_v15_r1_runtime_toctou_hardening.py",
    ],
    "46": [
        "governance-r8/R8-V15-R1-STAGE1-CHANGED-PATHS-ACCOUNTING.json",
        "tools/r8_evidence_bundle_integrity.py",
        "tools/test_r8_evidence_bundle_integrity.py",
        "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
        "governance-runtime/test_r8_v15_r1_runtime_toctou_hardening.py",
    ],
    "50": [
        "governance-r8/CODEX-WORK-QUEUE-51.json",
        "governance-r8/ISSUE-52-CONSOLIDATED-QUEUE-REPORT.md",
        "tools/r8_work_queue.py",
        "tools/test_r8_work_queue.py",
    ],
}

def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()

def raw(rev: str, path: str) -> bytes:
    return subprocess.check_output(("git", "show", f"{rev}:{path}"), cwd=ROOT)

def require(text: str, needle: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing required V3 metadata: {needle}")

def check() -> None:
    text = PACKET.read_text(encoding="utf-8")
    require(text, "R8 V15-R1 CONSOLIDATED REMEDIATION REVIEW PACKET V3")
    require(text, BASE)
    require(text, "REVIEWER OUTPUT CONTRACT")
    require(text, "final packet-bearing commit: EXTERNAL_IDENTITY_AFTER_COMMIT")
    require(text, "Packet source/parent head: 2837fc5b800d00f39dfb17fac479f69168ec080e")
    exact_mappings = {
        "C-1 | #43": "C-1 must map to #43",
        "C-2 | #46": "C-2 must map to #46",
        "H-1 | #42": "H-1 must map to #42",
        "H-2 | #42": "H-2 must map to #42",
        "H-3 | #43": "H-3 must map to #43",
        "H-4 | #43": "H-4 must map to #43",
        "H-5 | #44": "H-5 must map to #44",
        "H-6 | #44": "H-6 must map to #44",
        "H-7 | #46": "H-7 must map to #46",
        "H-8 | #46": "H-8 must map to #46",
        "H-9 | #46": "H-9 must map to #46",
        "H-10 | #46": "H-10 must map to #46",
        "H-11 | #50": "H-11 must map to #50",
        "H-12 | #50": "H-12 must map to #50",
        "H-13 | #50": "H-13 must map to #50",
        "H-14 | #46": "H-14 must map to #46",
        "M-2 | #46": "M-2 must map to #46",
        "M-5 | #43": "M-5 must map to #43",
        "M-6 | #44 | not accepted as mandatory": "M-6 adjudication missing",
        "M-7 | #43 | not accepted": "M-7 adjudication missing",
    }
    for needle, message in exact_mappings.items():
        require(text, needle)
    require(text, "governance-r8/R8-V15-R1-IG1-SUCCESSOR3-INTEGRATED-CANDIDATE-MANIFEST.json")
    require(text, "a78add847f6d4ba8914a66ee00d89422fbaa47f2")
    require(text, "M-1, M-3, and M-4 are intentionally not reconstructed")
    forbidden = [
        "C-1 | #44 | accepted",
        "H-1 | #44/#46",
        "H-2 | #44/#46",
        "H-10 | #44/#46/#43/#42/#50",
        "H-13 | #44/#46/#43/#42/#50",
        "M-1 | #42/#43/#46/#50",
    ]
    for needle in forbidden:
        if needle in text:
            raise SystemExit(f"old V2 generic mapping remains: {needle}")
    for n, head in HEADS.items():
        require(text, head)
        for path in FILES[n]:
            marker = f"FILE_PATH={path}"
            start = text.find(marker)
            if start < 0:
                raise SystemExit(f"missing embedded {path}")
            end = text.find("----- END EXACT FILE -----", start)
            if end < 0:
                raise SystemExit(f"unterminated embedded {path}")
            block = text[start:end]
            blob = re.search(r"FILE_BLOB_SHA1=([0-9a-f]{40})", block)
            sha = re.search(r"FILE_RAW_SHA256=([0-9a-f]{64})", block)
            if not blob or run("git", "rev-parse", f"{head}:{path}") != blob.group(1):
                raise SystemExit(f"blob mismatch {path}")
            if not sha or hashlib.sha256(raw(head, path)).hexdigest() != sha.group(1):
                raise SystemExit(f"raw sha mismatch {path}")
    print("R8_CONSOLIDATED_REMEDIATION_PACKET_V3_PASS")

if __name__ == "__main__":
    check()
