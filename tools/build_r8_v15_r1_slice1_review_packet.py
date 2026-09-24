#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import subprocess

REPO = os.environ["GITHUB_REPOSITORY"]
BASE_FREEZE_HEAD = "6f0506b6cd2a12eeeb30d79f85224d4b87b6c368"
FROZEN_SCHEMA = "f93ca26975ecb64f0da13779889c75b36140cdfc"
CANDIDATE = "e106bdd44973f3b16b5479c7689cbe07cb0f5421"
GREEN_RUN = 36060770372
GREEN_JOB = 107838888005
EVIDENCE_HEAD = "6b74cb4a19a90cf2e2680ac403251854cf792fce"

OUT = pathlib.Path("review-packet-slice1")
OUT.mkdir(exist_ok=True)


def out(args):
    return subprocess.check_output(args)


def git_show(ref, path):
    return out(["git", "show", f"{ref}:{path}"])


def git_blob(ref, path):
    return out(["git", "rev-parse", f"{ref}:{path}"]).decode().strip()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def append_file(fp, ref, path, title="EXACT FILE"):
    data = git_show(ref, path)
    fp.write(f"\n===== BEGIN {title}: {ref}:{path} =====\n".encode())
    fp.write(f"git_blob_sha1={git_blob(ref, path)}\n".encode())
    fp.write(f"sha256={sha(data)}\n".encode())
    fp.write(data)
    if not data.endswith(b"\n"):
        fp.write(b"\n")
    fp.write(f"===== END {title}: {ref}:{path} =====\n".encode())


def gh_json(endpoint):
    return json.loads(out(["gh", "api", endpoint]))


def main():
    for ref in [BASE_FREEZE_HEAD, FROZEN_SCHEMA, CANDIDATE, EVIDENCE_HEAD]:
        got = out(["git", "rev-parse", f"{ref}^{{commit}}"]).decode().strip()
        assert got == ref, (ref, got)

    run = gh_json(f"repos/{REPO}/actions/runs/{GREEN_RUN}")
    assert run["status"] == "completed" and run["conclusion"] == "success"
    assert run["head_sha"] == CANDIDATE

    jobs = gh_json(f"repos/{REPO}/actions/runs/{GREEN_RUN}/jobs")["jobs"]
    job = [j for j in jobs if j["id"] == GREEN_JOB]
    assert len(job) == 1 and job[0]["conclusion"] == "success"

    instructions = f"""R8 v15-r1 — IMPLEMENTATION SLICE 1 FRESH BLIND REVIEW

Review only the exact implementation candidate and evidence supplied in this packet.
Do not use earlier chat history, model recollection, R2/R3 schema reviews, or any prior
implementation-review result. Construction failure history is supplied only to verify
non-laundering and repair lineage.

Exact implementation candidate:
{CANDIDATE}

Frozen executable-schema candidate consumed by this implementation:
{FROZEN_SCHEMA}

Executable-schema freeze evidence head:
{BASE_FREEZE_HEAD}

Implementation evidence-only head:
{EVIDENCE_HEAD}

Authoritative green construction run:
{GREEN_RUN}
job:
{GREEN_JOB}

Review posture:
- assume false-green until demonstrated otherwise;
- inspect the exact module and frozen harness, not only CI labels;
- verify no caller-controlled path can weaken candidate/hash/provenance checks;
- inspect canonicalization for lexical, Unicode, NFC, int64, extension-map, duplicate-key,
  and deterministic serialization errors;
- inspect whether SPM/source-map validation can accept mismatched artifacts or source refs;
- look for path traversal, TOCTOU, mutable global state, stale-cache, exception-to-success,
  or authority-boundary bugs;
- distinguish construction correctness from runtime qualification;
- do not treat the historical pre-materialization regression as applicable post-freeze.

Required response format:

A. OVERALL_DISPOSITION
Choose exactly one:
BOUNDED_PASS
CHANGES_REQUIRED
INSUFFICIENT_EVIDENCE

B. EXACT_IDENTITY
Repeat exact implementation candidate, frozen schema candidate, green run/job.

C. CRITICAL_FINDINGS
Concrete findings only.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. I1_ACCEPTANCE_ASSESSMENT
Assess I1-01 through I1-16 and identify any false-green or untested path.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State what this Slice 1 implementation does and does not establish.
Explicitly assess whether construction may be adjudicated BOUNDED_PASS.
Do not grant runtime qualification, release, deployment, production, policy, or terminal authority.

H. FINAL_GATE
State whether this exact implementation candidate may close the Slice 1 independent-review gate.

A review result is evidence, not self-authority.
"""
    (OUT / "00_INSTRUCTIONS.txt").write_text(instructions, encoding="utf-8")

    candidate_paths = [
        ".github/workflows/r8-v15-r1-implementation-slice1.yml",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-AUTHORIZATION.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-PREREGISTRATION.md",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-MARKER.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-CONSTRUCTION-FAILURE-001.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-CONSTRUCTION-FAILURE-002.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-CONSTRUCTION-FAILURE-003.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-CONTROL-FAILURE-004.json",
        "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
        "governance-runtime/test_r8_v15_r1_implementation_slice1.py",
        "governance-runtime/test_r8_v15_r1_post_freeze_regression.py",
    ]
    with (OUT / "01_EXACT_IMPLEMENTATION_CANDIDATE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 1 - exact implementation candidate\n")
        fp.write(out(["git", "show", "--no-patch", "--format=fuller", CANDIDATE]))
        fp.write(b"\n===== DIFF FROM EXECUTABLE-SCHEMA FREEZE EVIDENCE HEAD =====\n")
        fp.write(out(["git", "diff", "--name-status", BASE_FREEZE_HEAD, CANDIDATE]))
        for path in candidate_paths:
            append_file(fp, CANDIDATE, path)

    schema_paths = out([
        "git", "ls-tree", "-r", "--name-only", FROZEN_SCHEMA,
        "schemas/governance-r8/v15-r1"
    ]).decode().splitlines()
    with (OUT / "02_FULL_FROZEN_SCHEMA_INPUTS.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 1 - full exact frozen schema input directory\n")
        fp.write(f"frozen_schema_candidate={FROZEN_SCHEMA}\n".encode())
        for path in schema_paths:
            append_file(fp, FROZEN_SCHEMA, path, "FROZEN SCHEMA INPUT")

    evidence_paths = [
        "governance-r8/R8-V15-R1-EXECUTABLE-SCHEMA-FREEZE.json",
        "governance-r8/R8-V15-R1-SFV45-R3-FINAL-INDEPENDENT-REVIEW.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-CONSTRUCTION-GREEN.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-FREEZE.json",
    ]
    with (OUT / "03_CONSTRUCTION_AND_FREEZE_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 1 - construction/freeze evidence\n")
        fp.write(b"\n===== GREEN RUN METADATA =====\n")
        fp.write((json.dumps(run, indent=2) + "\n").encode())
        fp.write(b"\n===== GREEN JOB METADATA =====\n")
        fp.write((json.dumps(job[0], indent=2) + "\n").encode())

        # Download decoded job log through GitHub API/CLI.
        log = out(["gh", "run", "view", str(GREEN_RUN), "--repo", REPO, "--log"])
        fp.write(b"\n===== GREEN RUN RAW LOG =====\n")
        fp.write(log)
        if not log.endswith(b"\n"):
            fp.write(b"\n")

        for path in evidence_paths:
            ref = BASE_FREEZE_HEAD if path in evidence_paths[:2] else EVIDENCE_HEAD
            append_file(fp, ref, path, "EVIDENCE")

    files = [
        OUT / "00_INSTRUCTIONS.txt",
        OUT / "01_EXACT_IMPLEMENTATION_CANDIDATE.txt",
        OUT / "02_FULL_FROZEN_SCHEMA_INPUTS.txt",
        OUT / "03_CONSTRUCTION_AND_FREEZE_EVIDENCE.txt",
    ]
    manifest = [
        "R8 v15-r1 Slice 1 independent-review packet SHA-256 manifest",
        f"implementation_candidate={CANDIDATE}",
        f"frozen_schema_candidate={FROZEN_SCHEMA}",
        f"green_run={GREEN_RUN}",
        f"green_job={GREEN_JOB}",
        "",
    ]
    for p in files:
        manifest.append(f"{sha(p.read_bytes())}  {p.name}")
    (OUT / "04_SHA256_MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    full = OUT / "R8_V15_R1_SLICE1_FULL_REVIEW_PACKET.txt"
    with full.open("wb") as fp:
        for p in files + [OUT / "04_SHA256_MANIFEST.txt"]:
            fp.write(p.read_bytes())
            fp.write(b"\n")
    (OUT / "R8_V15_R1_SLICE1_FULL_REVIEW_PACKET.sha256").write_text(
        f"{sha(full.read_bytes())}  {full.name}\n", encoding="utf-8"
    )

    for p in sorted(OUT.glob("*.txt")):
        print(p.name, p.stat().st_size, sha(p.read_bytes()))


if __name__ == "__main__":
    main()
