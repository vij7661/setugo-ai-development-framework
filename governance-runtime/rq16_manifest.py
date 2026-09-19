#!/usr/bin/env python3
"""Canonical source/evidence manifest definitions for the RQ-16 review packet."""
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_RELATIVE=(
    "implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md",
    "governance-runtime/build_rq16_preregistration_review.py",
    "governance-runtime/check_rq16_preregistration_packet.py",
    "governance-runtime/collect_rq16_results.py",
    "governance-runtime/run_v24_v6_rq1_rq16_mutations.py",
    "governance-runtime/rq16_manifest.py",
    "governance-runtime/test_v24_v6_rq1_rq16_harness.py",
    "governance-runtime/test_rq16_manifest.py",
    "governance-runtime/v24_v6_rq1_rq16_harness.py",
)
EVIDENCE_RELATIVE=(
    "implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json",
    "implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json",
)

def canonical_review_source_files(root=ROOT):
    return [root / rel for rel in SOURCE_RELATIVE]

def canonical_evidence_files(root=ROOT):
    return [root / rel for rel in EVIDENCE_RELATIVE]

def _entries(files, root=ROOT):
    entries=[]
    for path in files:
        rel=path.resolve().relative_to(root.resolve()).as_posix()
        if rel.startswith("/") or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise ValueError(f"non-canonical path: {rel}")
        entries.append({"path":rel,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    if len({e["path"] for e in entries}) != len(entries):
        raise ValueError("duplicate canonical path")
    return sorted(entries,key=lambda e:e["path"])

def build_source_manifest(files=None, root=ROOT):
    return json.dumps(_entries(files or canonical_review_source_files(root),root),ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"

def build_evidence_manifest(root=ROOT):
    return json.dumps(_entries(canonical_evidence_files(root),root),ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n"

def manifest_sha256(manifest):
    return hashlib.sha256(manifest.encode("utf-8")).hexdigest()
