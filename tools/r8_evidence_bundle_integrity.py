"""Reusable deterministic evidence-file and lineage verification helpers."""
from __future__ import annotations
import hashlib, json
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_entries(root: Path, paths: list[str]) -> list[dict]:
    normalized = sorted({Path(p).as_posix() for p in paths})
    if len(normalized) != len(paths) or any(Path(p).is_absolute() or p.startswith("../") for p in normalized):
        raise ValueError("invalid or duplicate evidence path")
    return [{"path": p, "sha256": file_digest(root / p)} for p in normalized]


def manifest_digest(entries: list[dict]) -> str:
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256_bytes(payload)


def verify_bundle(bundle: dict, *, root: Path, expected_authority: str, expected_head: str | None = None) -> dict:
    required = {"schema", "run_id", "job_id", "workflow", "head_sha", "input_blobs", "files", "archive_sha256", "authority_effect", "activation_verification"}
    if set(bundle) != required:
        raise ValueError("bundle schema mismatch")
    if bundle["authority_effect"] != expected_authority:
        raise ValueError("authority boundary mismatch")
    if expected_head is not None and bundle["head_sha"] != expected_head:
        raise ValueError("stale head")
    if not bundle["run_id"] or not bundle["job_id"] or not bundle["workflow"]:
        raise ValueError("missing lineage identity")
    files = bundle["files"]
    if not isinstance(files, list) or not files:
        raise ValueError("missing file entries")
    actual = canonical_entries(root, [e.get("path", "") for e in files])
    if actual != files:
        raise ValueError("evidence file digest mismatch")
    if not isinstance(bundle["input_blobs"], dict) or not all(len(v) == 40 for v in bundle["input_blobs"].values()):
        raise ValueError("input blob identity mismatch")
    if bundle["activation_verification"].get("performed") is not False:
        raise ValueError("activation verification must be preserved as non-authoritative evidence")
    return {"file_count": len(files), "files_manifest_sha256": manifest_digest(files), "status": "PASS"}
