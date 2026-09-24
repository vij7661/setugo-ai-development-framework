#!/usr/bin/env python3
"""Build non-authoritative Stage-A evidence for R8 v15-r1 SPG-1 qualification.

This helper never grants qualification. It measures the exact generator/runtime
candidate, reruns the existing unqualified SPM generator, and emits evidence that
is later signed by GitHub Artifact Attestations. A separate post-run verifier
must validate that attestation before any binding may become QUALIFIED.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import ssl
import subprocess
import sys
from pathlib import Path
from typing import Any

import _hashlib
import json as json_module
import json.decoder
import json.encoder
import json.scanner

EXPECTED_GENERATOR_SHA256 = "388fb8a61f31cbf99b001a2313d554c8a4aac36e61188eb95230b93c6b0077e6"
EXPECTED_CANDIDATE_COMMIT = "8c71169f9d6eb474ec89e950e452eb2130860ede"
EXPECTED_SEMANTIC_COMMIT = "c721b38cf8b00294797300b526596ce723a47ff8"
GENERATOR_REL = "tools/generate_r8_v15_r1_spm.py"
BINDING_REL = "schemas/governance-r8/v15-r1/schema-provenance-generator-binding.json"
SOURCE_MAP_REL = "schemas/governance-r8/v15-r1/schema-provenance-source-map.json"
SPM_CANDIDATE_REL = "schemas/governance-r8/v15-r1/schema-provenance-manifest-candidate.json"

def canonical(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")

def pretty(obj: Any) -> bytes:
    return (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())

def file_identity(path: Path) -> dict[str, Any]:
    resolved = path.resolve()
    return {
        "path": str(path),
        "resolved_path": str(resolved),
        "sha256": sha256_file(resolved),
        "bytes": resolved.stat().st_size,
    }

def component_digest(obj: Any) -> str:
    return sha256_bytes(canonical(obj))

def require(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(msg)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-root", required=True)
    ap.add_argument("--control-root", required=True)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--candidate-commit", required=True)
    ap.add_argument("--control-commit", required=True)
    ap.add_argument("--policy-rel", required=True)
    ap.add_argument("--workflow-rel", required=True)
    ap.add_argument("--container-reference", required=True)
    ap.add_argument("--container-repo-digest", required=True)
    ap.add_argument("--container-image-id", required=True)
    ap.add_argument("--runner-os", required=True)
    ap.add_argument("--runner-arch", required=True)
    ap.add_argument("--runner-image-os", required=True)
    ap.add_argument("--runner-image-version", required=True)
    ap.add_argument("--repository", required=True)
    ap.add_argument("--repository-id", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--run-attempt", required=True)
    args = ap.parse_args()

    candidate = Path(args.candidate_root)
    control = Path(args.control_root)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    require(args.candidate_commit == EXPECTED_CANDIDATE_COMMIT, "candidate commit mismatch")
    require(args.repository == "vij7661/setugo-ai-development-framework", "repository mismatch")
    require(args.repository_id == "1354031068", "repository id mismatch")
    require(args.container_repo_digest.startswith("python@sha256:"), "container RepoDigest missing/invalid")
    require(args.container_image_id.startswith("sha256:"), "container image id missing/invalid")

    generator = candidate / GENERATOR_REL
    binding_path = candidate / BINDING_REL
    source_map_path = candidate / SOURCE_MAP_REL
    existing_spm = candidate / SPM_CANDIDATE_REL
    policy_path = control / args.policy_rel
    workflow_path = control / args.workflow_rel

    require(generator.is_file(), "generator missing")
    require(binding_path.is_file(), "generator binding missing")
    require(source_map_path.is_file(), "source map missing")
    require(existing_spm.is_file(), "existing SPM candidate missing")
    require(policy_path.is_file(), "policy missing")
    require(workflow_path.is_file(), "workflow missing")
    require(sha256_file(generator) == EXPECTED_GENERATOR_SHA256, "generator SHA-256 drift")

    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    require(binding["generator_artifact_sha256"] == EXPECTED_GENERATOR_SHA256, "binding generator digest drift")
    require(binding["qualification_status"] == "UNATTESTED_RUNTIME", "Stage A requires unqualified binding")
    require(binding["revocation_state"] == "UNKNOWN", "Stage A requires UNKNOWN revocation state")
    require(binding["runtime_manifest"]["runtime_manifest_digest"] is None, "Stage A binding already carries runtime digest")
    require(binding["workload_attestation_policy_digest"] is None, "Stage A binding already carries policy digest")
    require(binding["workload_attestation_proof_digest"] is None, "Stage A binding already carries proof digest")
    require(binding["signing_credential_id"] is None, "Stage A binding already carries signing credential")
    source_map = json.loads(source_map_path.read_text(encoding="utf-8"))
    require(source_map["semantic_candidate_commit"] == EXPECTED_SEMANTIC_COMMIT, "semantic candidate drift")

    py_exe = Path(sys.executable)
    python_identity = {
        "implementation": platform.python_implementation(),
        "version": sys.version,
        "version_info": list(sys.version_info[:5]),
        "cache_tag": getattr(sys.implementation, "cache_tag", None),
        "executable": file_identity(py_exe),
        "platform": platform.platform(),
        "machine": platform.machine(),
    }

    crypto_identity = {
        "openssl_version": ssl.OPENSSL_VERSION,
        "_hashlib": file_identity(Path(_hashlib.__file__)),
        "algorithms_available": sorted(hashlib.algorithms_available),
        "algorithms_guaranteed": sorted(hashlib.algorithms_guaranteed),
    }

    parser_identity = {
        "parser_kind": "python-stdlib-json",
        "json": file_identity(Path(json_module.__file__)),
        "decoder": file_identity(Path(json.decoder.__file__)),
        "encoder": file_identity(Path(json.encoder.__file__)),
        "scanner": file_identity(Path(json.scanner.__file__)),
    }

    repo_digest_hex = args.container_repo_digest.split("@sha256:", 1)[1]
    require(len(repo_digest_hex) == 64 and all(c in "0123456789abcdef" for c in repo_digest_hex), "invalid OCI RepoDigest")
    runtime_basis = {
        "application_artifact_digest": EXPECTED_GENERATOR_SHA256,
        "interpreter_compiler_runtime_version_digest": component_digest(python_identity),
        "crypto_library_digest": component_digest(crypto_identity),
        "schema_parser_bundle_digest": component_digest(parser_identity),
        "os_container_image_digest": repo_digest_hex,
        "las_anchor_client_library_digest": None,
    }
    runtime_manifest_digest = component_digest(runtime_basis)
    runtime_manifest = dict(runtime_basis)
    runtime_manifest["runtime_manifest_digest"] = runtime_manifest_digest

    input_records = []
    for rel in binding["allowed_input_design_artifacts"]:
        p = candidate / rel
        require(p.is_file(), f"allowed input missing: {rel}")
        input_records.append({"path": rel, "sha256": sha256_file(p), "bytes": p.stat().st_size})
    input_manifest = {
        "schema": "r8-v15-r1-spg1-input-artifact-manifest/v1",
        "candidate_commit": args.candidate_commit,
        "records": input_records,
    }
    (out / "input-artifact-manifest.json").write_bytes(pretty(input_manifest))

    runtime_evidence = {
        "schema": "r8-v15-r1-spg1-runtime-manifest-evidence/v1",
        "status": "STAGE_A_ATTESTATION_SUBJECT_NON_AUTHORITATIVE",
        "authority_effect": "NONE",
        "candidate_commit": args.candidate_commit,
        "semantic_candidate_commit": EXPECTED_SEMANTIC_COMMIT,
        "control_commit": args.control_commit,
        "repository": args.repository,
        "repository_id": args.repository_id,
        "github_run_id": args.run_id,
        "github_run_attempt": args.run_attempt,
        "runner": {
            "environment": "github-hosted",
            "runs_on": "ubuntu-24.04",
            "os": args.runner_os,
            "arch": args.runner_arch,
            "image_os": args.runner_image_os,
            "image_version": args.runner_image_version,
        },
        "container": {
            "requested_reference": args.container_reference,
            "resolved_repo_digest": args.container_repo_digest,
            "image_id": args.container_image_id,
            "execution_rule": "generator executed by resolved immutable RepoDigest",
        },
        "python_identity": python_identity,
        "crypto_identity": crypto_identity,
        "schema_parser_identity": parser_identity,
        "las_anchor_client": {
            "used_by_generator": False,
            "digest": None,
            "reason": "Generator reads local frozen files only and makes no LAS/client calls.",
        },
        "runtime_manifest_digest_basis": "SHA256(canonical JSON of runtime_manifest fields excluding runtime_manifest_digest; UTF-8; sorted keys; compact separators; trailing LF)",
        "runtime_manifest": runtime_manifest,
        "policy_sha256": sha256_file(policy_path),
        "workflow_sha256": sha256_file(workflow_path),
        "generator_sha256": sha256_file(generator),
    }
    (out / "runtime-manifest-evidence.json").write_bytes(pretty(runtime_evidence))

    recomputed = out / "spm-candidate-recomputed.json"
    cmd = [
        sys.executable,
        str(generator),
        "--schema-root", str(candidate / "schemas/governance-r8/v15-r1"),
        "--source-map", str(source_map_path),
        "--generator-binding", str(binding_path),
        "--output", str(recomputed),
    ]
    subprocess.run(cmd, check=True)
    require(recomputed.read_bytes() == existing_spm.read_bytes(), "SPM candidate deterministic recomputation mismatch")

    shutil.copyfile(generator, out / "generator.py")
    shutil.copyfile(binding_path, out / "generator-binding-candidate.json")
    shutil.copyfile(policy_path, out / "attestation-policy.json")
    shutil.copyfile(workflow_path, out / "workflow.yml")

    file_names = sorted(p.name for p in out.iterdir() if p.is_file())
    records = [{"name": name, "sha256": sha256_file(out / name), "bytes": (out / name).stat().st_size} for name in file_names]
    subject_manifest = {
        "schema": "r8-v15-r1-spg1-stage-a-subject-manifest/v1",
        "status": "NON_AUTHORITATIVE_PENDING_EXTERNAL_ATTESTATION_VERIFICATION",
        "authority_effect": "NONE",
        "candidate_commit": args.candidate_commit,
        "control_commit": args.control_commit,
        "generator_sha256": EXPECTED_GENERATOR_SHA256,
        "runtime_manifest_digest": runtime_manifest_digest,
        "spm_candidate_sha256": sha256_file(recomputed),
        "existing_spm_candidate_sha256": sha256_file(existing_spm),
        "deterministic_spm_match": True,
        "files": records,
    }
    (out / "qualification-subject-manifest.json").write_bytes(pretty(subject_manifest))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
