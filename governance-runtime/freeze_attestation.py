"""External, non-self-referential freeze attestation verification."""
from __future__ import annotations

import json
import hashlib
import re
import subprocess
from pathlib import Path
from typing import Callable, Mapping

SHA40 = re.compile(r"[0-9a-f]{40}\Z")
REQUIRED = {
    "schema", "candidate_commit", "candidate_tree", "frozen_ref",
    "linux_validation", "review_packet", "authority_effect", "fallback_to_3",
    "six_slice_cadence", "attestation_state",
}
REQUIRED_V2 = (REQUIRED - {"linux_validation", "review_packet"}) | {"linux_validation_statement", "review_packet_statement"}
STATEMENT_REQUIRED = {"schema", "kind", "run_id", "job_id", "workflow_identity", "baseline_commit", "candidate_commit", "candidate_tree", "changed_file_count", "conclusion", "artifact_digest", "statement_sha256"}


def canonical_sha256(value: Mapping) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def verify_execution_statement(statement: Mapping, *, kind: str, commit: str, tree: str, baseline: str | None = None, changed_file_count: int | None = None) -> bool:
    if not isinstance(statement, Mapping) or set(statement) != STATEMENT_REQUIRED:
        return False
    material = dict(statement); supplied = material.pop("statement_sha256", None)
    expected_conclusion = "SUCCESS" if kind == "LINUX_VALIDATION" else "GENERATED"
    return (
        statement.get("schema") == "r8-candidate-execution-evidence/v1"
        and statement.get("kind") == kind
        and all(isinstance(statement.get(key), str) and statement[key].isdigit() for key in ("run_id", "job_id"))
        and isinstance(statement.get("workflow_identity"), str) and bool(statement["workflow_identity"].strip())
        and isinstance(statement.get("baseline_commit"), str) and SHA40.fullmatch(statement["baseline_commit"]) is not None
        and statement.get("candidate_commit") == commit
        and statement.get("candidate_tree") == tree
        and isinstance(statement.get("changed_file_count"), int) and statement["changed_file_count"] >= 0
        and (baseline is None or statement.get("baseline_commit") == baseline)
        and (changed_file_count is None or statement.get("changed_file_count") == changed_file_count)
        and statement.get("conclusion") == expected_conclusion
        and isinstance(statement.get("artifact_digest"), str) and re.fullmatch(r"sha256:[0-9a-f]{64}", statement["artifact_digest"]) is not None
        and isinstance(supplied, str) and supplied == canonical_sha256(material)
    )


def git_resolve(root: Path, revision: str) -> str:
    candidates = (revision, f"refs/heads/{revision}", f"refs/remotes/origin/{revision}")
    for candidate in candidates:
        cp = subprocess.run(["git", "rev-parse", candidate], cwd=root, text=True, capture_output=True)
        if cp.returncode == 0:
            return cp.stdout.strip()
    raise ValueError(f"frozen ref cannot be resolved: {revision}")


def verify_freeze_attestation(attestation: Mapping, *, root: Path = Path("."), resolver: Callable[[Path, str], str] = git_resolve) -> bool:
    if not isinstance(attestation, Mapping):
        return False
    is_v2 = attestation.get("schema") == "r8-external-freeze-attestation/v2"
    if set(attestation) != (REQUIRED_V2 if is_v2 else REQUIRED):
        return False
    commit, tree, ref = attestation.get("candidate_commit"), attestation.get("candidate_tree"), attestation.get("frozen_ref")
    if not isinstance(commit, str) or not SHA40.fullmatch(commit) or not isinstance(tree, str) or not SHA40.fullmatch(tree):
        return False
    if not isinstance(ref, str) or not ref.startswith("frozen/"):
        return False
    if is_v2:
        if not verify_execution_statement(attestation["linux_validation_statement"], kind="LINUX_VALIDATION", commit=commit, tree=tree):
            return False
        if not verify_execution_statement(attestation["review_packet_statement"], kind="REVIEW_PACKET", commit=commit, tree=tree):
            return False
        linux, packet = attestation["linux_validation_statement"], attestation["review_packet_statement"]
        if (linux["baseline_commit"], linux["changed_file_count"]) != (packet["baseline_commit"], packet["changed_file_count"]):
            return False
    for field in (() if is_v2 else ("linux_validation", "review_packet")):
        evidence = attestation.get(field)
        if not isinstance(evidence, Mapping) or set(evidence) != {"run_id", "job_id", "conclusion"}:
            return False
        if not all(isinstance(evidence.get(key), str) and evidence[key].isdigit() for key in ("run_id", "job_id")):
            return False
        if field == "linux_validation" and evidence.get("conclusion") != "SUCCESS":
            return False
        if field == "review_packet" and evidence.get("conclusion") != "GENERATED":
            return False
    if attestation.get("authority_effect") != "NONE" or attestation.get("fallback_to_3") != "ACTIVE":
        return False
    if attestation.get("six_slice_cadence") != "NOT_RESTORED" or attestation.get("attestation_state") != "FROZEN_VERIFIED":
        return False
    try:
        return resolver(root, ref) == commit and resolver(root, f"{commit}^{{tree}}") == tree
    except (OSError, ValueError):
        return False


def load_and_verify(path: Path, *, root: Path = Path("."), require_v2: bool = False) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if (require_v2 and value.get("schema") != "r8-external-freeze-attestation/v2") or not verify_freeze_attestation(value, root=root):
        raise ValueError("freeze attestation verification failed")
    return value
