"""Fail-closed cross-artifact SG-1 review/activation consistency verifier."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


OLD_GATE = "056bce33da38a2178ca2827d581b5a81c8bf4416"
EXPECTED_MANIFEST = Path("governance-r8/R8-V15-R1-STAGE2-SG1-REVIEW-ACTIVATION-MANIFEST.json")
EXPECTED_BINDING = Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-GATE-BINDING.json")
EXPECTED_PACKET = Path("stage2-sg1-review/R8-V15-R1-STAGE2-SG1-CONSOLIDATED-REVIEW-002-PACKET.txt")


def git_blob(path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()


def raw_sha1(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(message)


def verify(manifest_path: Path, binding_path: Path, packet_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    packet = packet_path.read_text(encoding="utf-8")

    p = manifest["proposal"]
    if p != {
        "id": "R8V15R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-CONFORMANCE-001",
        "commit": "67c84138140e86ba4a85a954f368f4c0f7e9ef3c",
        "blob_sha1": "d1ebd1427d5dfb07348fda2f817aa7f3d20feb3b",
        "path": "governance-r8/R8-V15-R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-CONFORMANCE-PROPOSAL.json",
    }:
        fail("proposal manifest mismatch")
    if git_blob(p["path"]) != p["blob_sha1"]:
        fail("proposal blob mismatch")
    candidate = manifest["candidate"]
    candidate_tree = subprocess.check_output(["git", "rev-parse", f"{candidate['commit']}^{{tree}}"], text=True).strip()
    candidate_parent = subprocess.check_output(["git", "show", "-s", "--format=%P", candidate["commit"]], text=True).strip().split()[0]
    if candidate_tree != candidate["tree"]:
        fail("candidate tree mismatch")
    if candidate_parent != candidate["parent"]:
        fail("candidate parent mismatch")
    if git_blob(manifest["activation_gate"]["path"]) != manifest["activation_gate"]["blob_sha1"]:
        fail("activation gate blob mismatch")
    if git_blob(manifest["activation_binding"]["path"]) != manifest["activation_binding"]["blob_sha1"]:
        fail("activation binding blob mismatch")

    if binding["proposal_contract"]["proposal_id"] != p["id"]:
        fail("binding proposal id mismatch")
    if binding["proposal_contract"]["exact_commit"] != p["commit"]:
        fail("binding proposal commit mismatch")
    if binding["proposal_contract"]["blob_sha1"] != p["blob_sha1"]:
        fail("binding proposal blob mismatch")
    if binding["activation_gate"]["blob_sha1"] != manifest["activation_gate"]["blob_sha1"]:
        fail("binding activation gate mismatch")
    expected_review = manifest["reviews"]["expected_fresh_review_002"]["path"]
    if binding["expected_review"]["path"] != expected_review:
        fail("binding expected review mismatch")
    if binding["expected_review"]["required_disposition"] != "BOUNDED_PASS":
        fail("binding required disposition mismatch")
    if binding["expected_review"]["required_critical_findings"] != 0 or binding["expected_review"]["required_high_findings"] != 0:
        fail("binding required finding counts mismatch")
    if binding["expected_review"]["required_final_gate"] != "YES":
        fail("binding final gate requirement mismatch")

    for group in ("machinery", "evidence", "dependency_targets"):
        for path, expected in manifest[group].items():
            if git_blob(path) != expected:
                fail(f"{group} blob mismatch: {path}")

    historical = manifest["reviews"]["historical_review_001"]
    historical_path = Path(historical["path"])
    if not historical_path.exists() or raw_sha1(historical_path) != "6d21b0fa1165c4879bff238ab65b8daedb2366f0":
        fail("Review 001 missing or altered")
    if historical["disposition"] != "CHANGES_REQUIRED" or "CHANGES_REQUIRED" not in historical_path.read_text(encoding="utf-8", errors="strict"):
        fail("Review 001 disposition mismatch")
    if Path(expected_review).exists():
        fail("Review 002 must remain an external fresh review")
    if Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION.json").exists():
        fail("activation artifact unexpectedly present")

    if manifest["governance"]["authority_boundary"] != "LOCAL DEPENDENCY SEMANTIC FALSIFICATION ONLY":
        fail("authority boundary mismatch")
    if manifest["governance"]["fallback_to_3"] != "ACTIVE" or manifest["governance"]["six_slice_cadence_restored"] is not False:
        fail("cadence boundary mismatch")
    if manifest["governance"]["semantic_execution_performed"] is not False:
        fail("semantic execution flag mismatch")
    if manifest["governance"]["activation_artifact_exists"] is not False:
        fail("activation artifact unexpectedly present")

    header = packet.split("===== BEGIN", 1)[0]
    if OLD_GATE in header:
        fail("stale old gate identity in active packet instructions")
    if manifest["activation_gate"]["blob_sha1"] not in header:
        fail("current gate identity absent from packet header")
    for value in (candidate["commit"], candidate["tree"], candidate["parent"]):
        if value not in header:
            fail("candidate identity absent from packet header")
    if expected_review not in header:
        fail("Review 002 path absent from packet header")
    if "expected fresh review: governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-001.txt" in header:
        fail("stale Review 001 expected path in active packet instructions")
    if "historical Review 001:" not in header or "CHANGES_REQUIRED" not in header:
        fail("historical Review 001 disclosure absent from packet header")
    h_match = "activation-gate blob " + manifest["activation_gate"]["blob_sha1"]
    if h_match not in packet:
        fail("current H. FINAL_GATE activation gate identity absent")
    historical_marker = "===== BEGIN HISTORICAL INDEPENDENT EARLY REVIEW 001"
    if OLD_GATE in packet and historical_marker not in packet:
        fail("old gate identity has no historical provenance")
    if packet.count("R8V15R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-CONFORMANCE-001") < 2:
        fail("proposal identity missing from packet")
    if "Broader Stage2 semantic authority granted: NO" not in packet:
        fail("broader Stage2 boundary missing")
    if "Automatic six-slice cadence restoration: NO" not in packet:
        fail("cadence boundary missing")

    return {
        "status": "PASS",
        "manifest": str(manifest_path),
        "packet": str(packet_path),
        "old_gate_references": packet.count(OLD_GATE),
        "historical_old_gate_allowed": OLD_GATE in packet,
        "activation_artifact_exists": False,
        "semantic_execution_performed": False,
        "broader_stage2_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=EXPECTED_MANIFEST)
    parser.add_argument("--binding", type=Path, default=EXPECTED_BINDING)
    parser.add_argument("--packet", type=Path, default=EXPECTED_PACKET)
    args = parser.parse_args()
    result = verify(args.manifest, args.binding, args.packet)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
