"""External, non-self-referential freeze attestation verification."""
from __future__ import annotations

import json
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


def git_resolve(root: Path, revision: str) -> str:
    candidates = (revision, f"refs/heads/{revision}", f"refs/remotes/origin/{revision}")
    for candidate in candidates:
        cp = subprocess.run(["git", "rev-parse", candidate], cwd=root, text=True, capture_output=True)
        if cp.returncode == 0:
            return cp.stdout.strip()
    raise ValueError(f"frozen ref cannot be resolved: {revision}")


def verify_freeze_attestation(attestation: Mapping, *, root: Path = Path("."), resolver: Callable[[Path, str], str] = git_resolve) -> bool:
    if not isinstance(attestation, Mapping) or set(attestation) != REQUIRED:
        return False
    commit, tree, ref = attestation.get("candidate_commit"), attestation.get("candidate_tree"), attestation.get("frozen_ref")
    if not isinstance(commit, str) or not SHA40.fullmatch(commit) or not isinstance(tree, str) or not SHA40.fullmatch(tree):
        return False
    if not isinstance(ref, str) or not ref.startswith("frozen/"):
        return False
    for field in ("linux_validation", "review_packet"):
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


def load_and_verify(path: Path, *, root: Path = Path(".")) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not verify_freeze_attestation(value, root=root):
        raise ValueError("freeze attestation verification failed")
    return value
