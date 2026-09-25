"""Fail-closed cross-artifact SG-1 review/activation consistency verifier."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


OLD_GATE = "056bce33" + "da38a2178ca2827d581b5a81c8bf4416"
EXPECTED_MANIFEST = Path("governance-r8/R8-V15-R1-STAGE2-SG1-REVIEW-ACTIVATION-MANIFEST.json")
EXPECTED_BINDING = Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION-GATE-BINDING.json")
EXPECTED_PACKET = Path("stage2-sg1-review/R8-V15-R1-STAGE2-SG1-CONSOLIDATED-REVIEW-002-PACKET.txt")


def git_blob(path: str) -> str:
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()


def raw_sha1(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(message)


def validate_review_002(path: Path, expected: dict, proposal: dict) -> str:
    text = path.read_text(encoding="utf-8")
    headings=list(re.finditer(r"(?m)^([A-H])\.\s+[^\r\n]*$", text))
    if len(headings) != 8 or [m.group(1) for m in headings] != list("ABCDEFGH"):
        fail("Review 002 is not exactly one ordered A-H document")
    sections={}
    for index, match in enumerate(headings):
        end=headings[index+1].start() if index+1 < len(headings) else len(text)
        sections[match.group(1)]=text[match.end():end].strip()
    if sections["A"] != expected["required_disposition"]:
        fail("Review 002 disposition mismatch")
    if not re.fullmatch(r"(?i:none\.?)", sections["C"]):
        fail("Review 002 Critical section is not clean")
    if not re.fullmatch(r"(?i:none\.?)", sections["D"]):
        fail("Review 002 High section is not clean")
    if len(re.findall(r"(?mi)^Stage2 SG-1 may be explicitly activated by user:\s*YES\s*$", sections["H"])) != 1:
        fail("Review 002 activation declaration mismatch")
    if re.search(r"(?mi)^Stage2 SG-1 may be explicitly activated by user:\s*NO\s*$", text):
        fail("Review 002 contradictory activation declaration")
    if len(re.findall(r"(?mi)^Broader Stage2 semantic authority granted:\s*NO\s*$", sections["H"])) != 1 or re.search(r"(?mi)^Broader Stage2 semantic authority granted:\s*YES\s*$", text):
        fail("Review 002 broader authority declaration mismatch")
    if proposal["id"] not in text or proposal["commit"] not in text or proposal["blob_sha1"] not in text:
        fail("Review 002 proposal identity mismatch")
    return git_blob(str(path))


def verify(manifest_path: Path, binding_path: Path, packet_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    packet = packet_path.read_text(encoding="utf-8")

    if manifest.get("schema") != "r8-v15-r1-stage2-sg1-review-activation-manifest/v1":
        fail("manifest schema mismatch")
    if manifest.get("status") != "PROPOSAL_REVIEW_EVIDENCE_ONLY_NOT_ACTIVE" or manifest.get("authority_effect") != "NONE":
        fail("manifest status/authority mismatch")

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
    proposal_doc = json.loads(subprocess.check_output(["git", "show", f"HEAD:{p['path']}"], text=True))
    candidate = manifest["candidate"]
    if candidate != {
        "commit": "4984f06a4420b76ad1ad475751aebda04a2d2c5c",
        "tree": "5a34e0d7db3e750dd5b0f722ccecc8014be189ef",
        "parent": "751162ee42c603cb6c84ee12021d16bab6fa626b",
    }:
        fail("frozen candidate identity mismatch")
    candidate_tree = subprocess.check_output(["git", "rev-parse", f"{candidate['commit']}^{{tree}}"], text=True).strip()
    candidate_parent = subprocess.check_output(["git", "show", "-s", "--format=%P", candidate["commit"]], text=True).strip().split()[0]
    if candidate_tree != candidate["tree"]:
        fail("candidate tree mismatch")
    if candidate_parent != candidate["parent"]:
        fail("candidate parent mismatch")
    stage1_binding = proposal_doc.get("stage1_binding", {})
    if (stage1_binding.get("exact_candidate"), stage1_binding.get("exact_tree"), stage1_binding.get("exact_parent")) != (candidate["commit"], candidate["tree"], candidate["parent"]):
        fail("manifest candidate disagrees with proposal stage1 binding")
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
    if binding.get("schema") != "r8-v15-r1-stage2-sg1-activation-gate-binding/v1" or binding.get("status") != manifest["status"] or binding.get("authority_effect") != manifest["authority_effect"]:
        fail("binding schema/status/authority mismatch")
    if binding["activation_gate"]["path"] != manifest["activation_gate"]["path"]:
        fail("binding activation gate path mismatch")
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
    if binding["expected_review"] != {
        "path": manifest["reviews"]["expected_fresh_review_002"]["path"],
        "blob_sha1": manifest["reviews"]["expected_fresh_review_002"]["blob_sha1"],
        "required_disposition": manifest["reviews"]["expected_fresh_review_002"]["required_disposition"],
        "required_critical_findings": manifest["reviews"]["expected_fresh_review_002"]["required_critical_findings"],
        "required_high_findings": manifest["reviews"]["expected_fresh_review_002"]["required_high_findings"],
        "required_exact_proposal_id": p["id"],
        "required_exact_proposal_commit": p["commit"],
        "required_final_gate": manifest["reviews"]["expected_fresh_review_002"]["required_final_gate"],
    }:
        fail("binding expected review drift")
    if binding["exact_required_machinery"] != manifest["machinery"]:
        fail("binding machinery map drift")
    if binding["exact_required_evidence"] != manifest["evidence"]:
        fail("binding evidence map drift")

    for group in ("machinery", "evidence", "dependency_targets"):
        for path, expected in manifest[group].items():
            if git_blob(path) != expected:
                fail(f"{group} blob mismatch: {path}")

    historical = manifest["reviews"]["historical_review_001"]
    historical_path = Path(historical["path"])
    if not historical_path.exists() or git_blob(historical["path"]) != historical["blob_sha1"] or raw_sha1(historical_path) != "6d21b0fa1165c4879bff238ab65b8daedb2366f0":
        fail("Review 001 missing or altered")
    if historical["disposition"] != "CHANGES_REQUIRED" or "CHANGES_REQUIRED" not in historical_path.read_text(encoding="utf-8", errors="strict"):
        fail("Review 001 disposition mismatch")
    if not Path(expected_review).exists():
        fail("Review 002 is missing")
    review_002_blob = validate_review_002(Path(expected_review), manifest["reviews"]["expected_fresh_review_002"], p)
    if binding["expected_review"].get("blob_sha1") != review_002_blob:
        fail("Review 002 blob binding mismatch")
    if Path("governance-r8/R8-V15-R1-STAGE2-SG1-ACTIVATION.json").exists():
        fail("activation artifact unexpectedly present")

    preflight = json.loads(Path(manifest["preflight"]["path"]).read_text(encoding="utf-8"))
    if git_blob(manifest["preflight"]["path"]) != manifest["evidence"][manifest["preflight"]["path"]]:
        fail("preflight blob mismatch")
    if (str(preflight.get("run_id")), str(preflight.get("job_id"))) != (manifest["preflight"]["run"], manifest["preflight"]["job"]):
        fail("preflight run/job mismatch")
    if preflight.get("exact_stage1_candidate") != candidate["commit"] or preflight.get("exact_stage1_tree") != candidate["tree"] or preflight.get("semantic_execution_performed") is not False:
        fail("preflight scope mismatch")

    if manifest["governance"]["authority_boundary"] != "LOCAL DEPENDENCY SEMANTIC FALSIFICATION ONLY":
        fail("authority boundary mismatch")
    if manifest["governance"]["fallback_to_3"] != "ACTIVE" or manifest["governance"]["six_slice_cadence_restored"] is not False:
        fail("cadence boundary mismatch")
    if manifest["governance"]["semantic_execution_performed"] is not False:
        fail("semantic execution flag mismatch")
    if manifest["governance"]["activation_artifact_exists"] is not False:
        fail("activation artifact unexpectedly present")
    if manifest["governance"].get("broader_stage2_authorized") is not False or manifest["governance"].get("runtime_release_deployment_production_policy_constitutional_root_terminal_authority") is not False:
        fail("authority grant boundary mismatch")
    gate_text = subprocess.check_output(["git", "show", f"HEAD:{manifest['activation_gate']['path']}"], text=True)
    if f'EXPECTED_REVIEW_PATH="{expected_review}"' not in gate_text:
        fail("activation gate expected review path mismatch")

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
    if manifest["reviews"]["expected_fresh_review_002"]["blob_sha1"] not in header:
        fail("Review 002 blob absent from packet header")
    if "expected fresh review: governance-r8/R8-V15-R1-STAGE2-SG1-INDEPENDENT-EARLY-REVIEW-001.txt" in header:
        fail("stale Review 001 expected path in active packet instructions")
    if "historical Review 001:" not in header or "CHANGES_REQUIRED" not in header:
        fail("historical Review 001 disclosure absent from packet header")
    h_match = "activation-gate blob " + manifest["activation_gate"]["blob_sha1"]
    if h_match not in packet:
        fail("current H. FINAL_GATE activation gate identity absent")
    historical_marker = "===== BEGIN HISTORICAL INDEPENDENT EARLY REVIEW 001"
    if OLD_GATE in packet:
        if historical_marker not in packet:
            fail("old gate identity has no historical provenance")
        hstart=packet.index(historical_marker)
        hend=packet.find("===== END HISTORICAL INDEPENDENT EARLY REVIEW 001", hstart)
        if hend < 0:
            fail("historical Review 001 delimiter missing")
        if OLD_GATE in packet[:hstart] or OLD_GATE in packet[hend:]:
            fail("old gate identity appears outside historical Review 001")
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
