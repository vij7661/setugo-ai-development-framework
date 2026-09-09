#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance-runtime"
SHA40 = __import__("re").compile(r"^[0-9a-f]{40}$")


def canon(v: Any) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_status(args: argparse.Namespace) -> int:
    state = load_json(GOV / "session-state.json")
    mem = load_json(GOV / "shared-memory.json")
    head = git_head()
    work = state["active_workstream"]
    handoff = state["execution_handoff"]
    expected = args.expected_sha or work["head_commit"]
    ok = head == expected
    out = {
        "schema_version": 1,
        "checkout_head": head,
        "expected_head": expected,
        "head_match": ok,
        "checkpoint_id": state["checkpoint_id"],
        "workstream": work["name"],
        "workstream_state": work["state"],
        "governed_head": work["head_commit"],
        "memory_head": mem["current_work"]["authoritative_head"],
        "stop_condition": handoff["stop_condition"],
        "manual_input_required": handoff["manual_input_required"],
        "next_required_action": handoff["next_required_action"],
        "review_status": state["independent_review"]["current_review_status"],
        "promotion_authority_granted": False,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0 if ok else 2


def read_manifest(path: Path) -> dict[str, Any]:
    m = load_json(path)
    if not SHA40.fullmatch(str(m.get("candidate_sha", ""))):
        raise ValueError("candidate_sha must be exact lowercase SHA40")
    files = m.get("required_files")
    if not isinstance(files, list) or not files or len(set(files)) != len(files):
        raise ValueError("required_files must be unique non-empty list")
    return m


def build_artifacts(m: dict[str, Any]) -> list[dict[str, Any]]:
    artifacts = []
    for rel in m["required_files"]:
        p = ROOT / rel
        if not p.is_file():
            raise FileNotFoundError(rel)
        b = p.read_bytes()
        artifacts.append({"path": rel, "sha256": sha256_bytes(b), "byte_length": len(b), "content": b.decode("utf-8")})
    return artifacts


def cmd_packet(args: argparse.Namespace) -> int:
    m = read_manifest(Path(args.manifest))
    head = git_head()
    if head != m["candidate_sha"]:
        raise ValueError(f"checkout {head} != manifest candidate {m['candidate_sha']}")
    artifacts = build_artifacts(m)
    packet: dict[str, Any] = {
        "schema_version": 1,
        "packet_type": args.mode.upper(),
        "candidate_sha": m["candidate_sha"],
        "included_files": [a["path"] for a in artifacts],
        "omitted_files": m.get("omitted_files", []),
        "mandatory_dimensions": m.get("mandatory_dimensions", []),
        "artifacts": artifacts,
        "promotion_authority_granted": False,
    }
    if args.mode == "delta":
        prior = m.get("prior_packet_manifest_sha256")
        prior_candidate = m.get("prior_candidate_sha")
        if not isinstance(prior, str) or len(prior) != 64 or not SHA40.fullmatch(str(prior_candidate or "")):
            raise ValueError("delta requires prior_packet_manifest_sha256 and prior_candidate_sha")
        packet["prior_packet_manifest_sha256"] = prior
        packet["prior_candidate_sha"] = prior_candidate
    manifest_view = {k: v for k, v in packet.items() if k != "artifacts"}
    packet["packet_manifest_sha256"] = sha256_bytes(canon(manifest_view))
    Path(args.output).write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"output": args.output, "candidate_sha": m["candidate_sha"], "packet_manifest_sha256": packet["packet_manifest_sha256"], "files": len(artifacts)}, sort_keys=True))
    return 0


def cmd_ingest(args: argparse.Namespace) -> int:
    review = load_json(Path(args.review))
    expected = args.candidate_sha
    if review.get("reviewed_artifact_commit") != expected:
        raise ValueError("review candidate mismatch")
    required = list(args.dimension)
    coverage = review.get("review_coverage")
    if not isinstance(coverage, list):
        raise ValueError("review_coverage missing")
    ids = [x.get("dimension_id") for x in coverage if isinstance(x, dict)]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate review dimensions")
    if set(ids) != set(required):
        raise ValueError("mandatory dimension coverage mismatch")
    for row in coverage:
        if not isinstance(row.get("evidence"), str) or not row["evidence"].strip():
            raise ValueError(f"empty evidence for {row.get('dimension_id')}")
    out = {
        "schema_version": 1,
        "candidate_sha": expected,
        "disposition": review.get("disposition"),
        "findings_count": len(review.get("findings", [])),
        "dimensions": len(ids),
        "structurally_valid": True,
        "counts_for_promotion": False,
        "requires_deterministic_adjudication": True,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("status")
    s.add_argument("--expected-sha")
    s.set_defaults(func=cmd_status)
    q = sub.add_parser("packet")
    q.add_argument("--manifest", required=True)
    q.add_argument("--output", required=True)
    q.add_argument("--mode", choices=["full", "delta"], default="full")
    q.set_defaults(func=cmd_packet)
    i = sub.add_parser("ingest")
    i.add_argument("--review", required=True)
    i.add_argument("--candidate-sha", required=True)
    i.add_argument("--dimension", action="append", default=[])
    i.set_defaults(func=cmd_ingest)
    return p


def main() -> int:
    try:
        a = parser().parse_args()
        return a.func(a)
    except Exception as exc:
        print(f"GOVERNED_ACCELERATOR_FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
