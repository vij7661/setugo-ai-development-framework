"""Q15 review/merge evidence gate. This module grants no merge authority."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from freeze_attestation import load_and_verify  # noqa: E402
from r8_v15_r1_independent_review_parser import (  # noqa: E402
    eligible_for_bounded_merge,
    parse_independent_review_file,
)


def review_merge_evidence_eligible(*, review_path: Path, freeze_attestation_path: Path, review_packet_statement_path: Path, expected_identity: dict, root: Path = ROOT) -> bool:
    parsed = parse_independent_review_file(review_path, candidate_label=expected_identity["candidate_label"])
    attestation = load_and_verify(freeze_attestation_path, root=root, require_v2=True)
    packet_statement = json.loads(review_packet_statement_path.read_text(encoding="utf-8"))
    identity = parsed["identity"]
    exact_fields = ("baseline", "candidate_commit", "candidate_tree", "changed_file_count", "packet_run_job", "linux_run_job")
    if any(identity.get(field) != expected_identity.get(field) for field in exact_fields): return False
    if attestation.get("candidate_commit") != expected_identity["candidate_commit"] or attestation.get("candidate_tree") != expected_identity["candidate_tree"]: return False
    linux, packet = attestation["linux_validation_statement"], attestation["review_packet_statement"]
    for statement in (linux, packet):
        if statement.get("baseline_commit") != expected_identity["baseline"] or statement.get("changed_file_count") != expected_identity["changed_file_count"]: return False
    if packet_statement != packet: return False
    if (linux["run_id"], linux["job_id"]) != tuple(expected_identity["linux_run_job"]): return False
    if (packet["run_id"], packet["job_id"]) != tuple(expected_identity["packet_run_job"]): return False
    return eligible_for_bounded_merge(parsed, freeze_verified=True)
