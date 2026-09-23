#!/usr/bin/env python3
"""Deterministic R8 v15-r1 SPM-1 generator candidate.

This program is intentionally non-authoritative unless executed by a qualified
SchemaProvenanceGenerator runtime whose exact artifact/runtime/attestation
binding satisfies the frozen SPG-1 contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

GENERATOR_ID = "R8V15R1-SPG-V2"

def canonical_json(obj: Any) -> bytes:
    # This serialization is for the provenance artifact file itself only.
    # It does NOT redefine GCP-1 canonical authority serialization.
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def git_blob_sha1(data: bytes) -> str:
    hdr = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(hdr + data).hexdigest()

def esc(token: str) -> str:
    return token.replace("~", "~0").replace("/", "~1")

def leaf_pointers(value: Any, base: str = "") -> list[str]:
    out: list[str] = []
    if isinstance(value, dict):
        if not value:
            out.append(base or "/")
        for k, v in value.items():
            p = f"{base}/{esc(str(k))}"
            out.extend(leaf_pointers(v, p))
    elif isinstance(value, list):
        if not value:
            out.append(base or "/")
        for i, v in enumerate(value):
            out.extend(leaf_pointers(v, f"{base}/{i}"))
    else:
        out.append(base or "/")
    return out

def source_ids_for(path_name: str, pointer: str, source_map: dict[str, Any]) -> list[str]:
    cfg = source_map["artifact_sources"][path_name]
    best: tuple[int, list[str]] | None = None
    for prefix, ids in cfg.get("pointer_prefix_sources", {}).items():
        if pointer == prefix or pointer.startswith(prefix + "/"):
            if best is None or len(prefix) > best[0]:
                best = (len(prefix), list(ids))
    if best:
        return best[1]
    return list(cfg["source_design_ids"])

def source_ref_catalog(source_map: dict[str, Any]) -> dict[str, dict[str, str]]:
    catalog: dict[str, dict[str, str]] = {}
    seen: dict[tuple[str, str, str], str] = {}
    counter = 0
    for group in ("default_source_refs", "process_source_refs"):
        for r in source_map.get(group, []):
            key = (r["path"], r["commit"], r["blob"])
            if key in seen:
                continue
            counter += 1
            rid = f"SRC-{counter:03d}"
            seen[key] = rid
            catalog[rid] = r
    return catalog

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema-root", required=True)
    ap.add_argument("--source-map", required=True)
    ap.add_argument("--generator-binding", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    root = Path(args.schema_root)
    source_map = json.loads(Path(args.source_map).read_text(encoding="utf-8"))
    generator = json.loads(Path(args.generator_binding).read_text(encoding="utf-8"))

    if generator["generator_id"] != GENERATOR_ID:
        raise SystemExit("generator_id mismatch")

    artifacts = []
    entries = []
    source_catalog = source_ref_catalog(source_map)
    source_ref_ids = list(source_catalog.keys())

    for name in sorted(source_map["artifact_sources"]):
        path = root / name
        if not path.is_file():
            raise SystemExit(f"missing schema artifact: {name}")
        raw = path.read_bytes()
        parsed = json.loads(raw.decode("utf-8"))
        digest = sha256_bytes(raw)
        artifact_id = parsed.get("$id") or parsed.get("schema") or name
        artifacts.append({
            "artifact_id": artifact_id,
            "path": str(path).replace("\\", "/"),
            "git_blob_sha1": git_blob_sha1(raw),
            "sha256": digest,
        })
        for ptr in leaf_pointers(parsed):
            entries.append({
                "artifact_id": artifact_id,
                "artifact_sha256": digest,
                "json_pointer": ptr,
                "semantic_purpose": f"Frozen executable-schema element {name}{ptr}",
                "source_design_ids": source_ids_for(name, ptr, source_map),
                "source_ref_ids": source_ref_ids,
                "generator_id": GENERATOR_ID,
                "generator_runtime_manifest_digest": generator["runtime_manifest"]["runtime_manifest_digest"],
                "reviewer_status": "REVIEW_REQUIRED",
            })

    out = {
        "schema": "r8-v15-r1-spm-1/v1",
        "status": "FINAL_FREEZE_ELIGIBLE" if generator["qualification_status"] == "QUALIFIED" else "SCHEMA_FREEZE_CANDIDATE_NON_AUTHORITATIVE",
        "authority_effect": "NONE",
        "semantic_candidate_commit": source_map["semantic_candidate_commit"],
        "generator": {
            "generator_id": generator["generator_id"],
            "generator_artifact_path": generator["generator_artifact_path"],
            "generator_artifact_sha256": generator["generator_artifact_sha256"],
            "runtime_manifest_digest": generator["runtime_manifest"]["runtime_manifest_digest"],
            "workload_attestation_proof_digest": generator["workload_attestation_proof_digest"],
            "qualification_status": generator["qualification_status"],
        },
        "source_ref_catalog": source_catalog,
        "artifact_count": len(artifacts),
        "entry_count": len(entries),
        "artifacts": artifacts,
        "entries": entries,
        "coverage": {
            "uncovered_semantic_elements": [],
            "non_authoritative_only_sources": [],
            "conflicting_entries": [],
        },
    }
    Path(args.output).write_bytes(canonical_json(out))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
