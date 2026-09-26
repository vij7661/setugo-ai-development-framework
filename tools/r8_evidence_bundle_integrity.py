"""Reusable deterministic evidence-file and lineage verification helpers."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from pathlib import PurePosixPath
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "governance-runtime"))
from r8_v15_r1_frozen_schema_runtime import read_confined_file


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(root: Path, path: Path) -> str:
    """Digest a file only through the caller-supplied fixed evidence root."""
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError("evidence path escapes fixed root") from exc
    return sha256_bytes(read_confined_file(root, path))


def _canonical_relative_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or (len(value) >= 2 and value[1] == ":"):
        raise ValueError("invalid evidence path")
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or any(part in {"", ".", ".."} for part in parsed.parts):
        raise ValueError("invalid evidence path")
    normalized = parsed.as_posix()
    if normalized != value:
        raise ValueError("non-canonical evidence path")
    return normalized


def canonical_entries(root: Path, paths: list[str]) -> list[dict]:
    normalized = [_canonical_relative_path(p) for p in paths]
    if len(set(normalized)) != len(normalized):
        raise ValueError("invalid or duplicate evidence path")
    normalized.sort()
    return [{"path": p, "sha256": file_digest(root, root / p)} for p in normalized]


def manifest_digest(entries: list[dict]) -> str:
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(payload)


def verify_bundle(
    bundle: dict,
    *,
    root: Path,
    expected_authority: str,
    expected_run_id: str | None = None,
    expected_job_id: str | None = None,
    expected_workflow: str | None = None,
    expected_head: str | None = None,
    expected_inputs: dict | None = None,
    expected_archive_sha256: str | None = None,
    expected_activation_verification: dict | None = None,
) -> dict:
    required = {"schema", "run_id", "job_id", "workflow", "head_sha", "input_blobs", "files", "archive", "authority_effect", "activation_verification"}
    if set(bundle) != required:
        raise ValueError("bundle schema mismatch")
    if bundle["authority_effect"] != expected_authority:
        raise ValueError("authority boundary mismatch")
    if not isinstance(bundle["run_id"], str) or not bundle["run_id"] or not isinstance(bundle["job_id"], str) or not bundle["job_id"] or not isinstance(bundle["workflow"], str) or not bundle["workflow"]:
        raise ValueError("missing lineage identity")
    if expected_run_id is not None and bundle["run_id"] != expected_run_id:
        raise ValueError("wrong run identity")
    if expected_job_id is not None and bundle["job_id"] != expected_job_id:
        raise ValueError("wrong job identity")
    if expected_workflow is not None and bundle["workflow"] != expected_workflow:
        raise ValueError("wrong workflow identity")
    if not isinstance(bundle["head_sha"], str) or len(bundle["head_sha"]) != 40 or any(c not in "0123456789abcdef" for c in bundle["head_sha"]):
        raise ValueError("head identity syntax mismatch")
    if expected_head is not None and bundle["head_sha"] != expected_head:
        raise ValueError("stale head")
    files = bundle["files"]
    if not isinstance(files, list) or not files:
        raise ValueError("missing file entries")
    actual = canonical_entries(root, [e.get("path", "") for e in files])
    if actual != files:
        raise ValueError("evidence file digest mismatch")
    if not isinstance(bundle["input_blobs"], dict) or not all(isinstance(v, str) and len(v) == 40 and all(c in "0123456789abcdef" for c in v) for v in bundle["input_blobs"].values()):
        raise ValueError("input blob identity mismatch")
    if expected_inputs is not None and bundle["input_blobs"] != expected_inputs:
        raise ValueError("substituted input blob mapping")
    archive = bundle["archive"]
    if set(archive) != {"format", "sha256"} or archive["format"] not in {"zip", "tar", "directory"} or not isinstance(archive["sha256"], str) or len(archive["sha256"]) != 64 or any(c not in "0123456789abcdef" for c in archive["sha256"]):
        raise ValueError("archive digest schema mismatch")
    if expected_archive_sha256 is not None and archive["sha256"] != expected_archive_sha256:
        raise ValueError("archive digest mismatch")
    av = bundle["activation_verification"]
    if set(av) != {"performed", "run_id", "job_id", "conclusion"} or not isinstance(av["performed"], bool):
        raise ValueError("activation verification evidence incomplete")
    if not isinstance(av["run_id"], str) or not isinstance(av["job_id"], str) or not isinstance(av["conclusion"], str):
        raise ValueError("activation verification identity malformed")
    if expected_activation_verification is not None and av != expected_activation_verification:
        raise ValueError("activation verification mismatch")
    if bundle["authority_effect"] != "NONE":
        raise ValueError("authority promotion")
    return {"file_count": len(files), "files_manifest_sha256": manifest_digest(files), "status": "PASS"}
