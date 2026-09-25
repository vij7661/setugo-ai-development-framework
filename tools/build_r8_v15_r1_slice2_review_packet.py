#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import subprocess

REPO = os.environ["GITHUB_REPOSITORY"]
CANDIDATE = "6a8d0b0e4baa3a9df75dc47f626953b4dde51255"
FROZEN_SCHEMA = "f93ca26975ecb64f0da13779889c75b36140cdfc"
SLICE1_CANDIDATE = "fdf825cb45fbd00441a4cd02bb1912bb3cda01b0"
SLICE1_CLOSURE_HEAD = "194963c846fa62143aa03208d3617ca3f39dd173"
EVIDENCE_HEAD = "f0861b4d143ea6ae6d931679b955fc15b5e4edbe"
GREEN_RUN = 36109723091
GREEN_JOB = 107990188335
OUT = pathlib.Path("review-packet-slice2")
OUT.mkdir(exist_ok=True)


def sh(args):
    return subprocess.check_output(args)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_show(ref, path):
    return sh(["git", "show", f"{ref}:{path}"])


def git_blob(ref, path):
    return sh(["git", "rev-parse", f"{ref}:{path}"]).decode().strip()


def gh_json(endpoint):
    return json.loads(sh(["gh", "api", endpoint]))


def exact_section(ref, path, title="EXACT FILE"):
    data = git_show(ref, path)
    header = (
        f"\n===== BEGIN {title}: {ref}:{path} =====\n"
        f"git_blob_sha1={git_blob(ref, path)}\n"
        f"sha256={sha(data)}\n"
        f"byte_count={len(data)}\n"
    ).encode()
    tail = f"===== END {title}: {ref}:{path} =====\n".encode()
    return header + data + (b"" if data.endswith(b"\n") else b"\n") + tail


def main():
    for ref in [CANDIDATE, FROZEN_SCHEMA, SLICE1_CANDIDATE, SLICE1_CLOSURE_HEAD, EVIDENCE_HEAD]:
        got = sh(["git", "rev-parse", f"{ref}^{{commit}}"]).decode().strip()
        assert got == ref, (ref, got)

    run = gh_json(f"repos/{REPO}/actions/runs/{GREEN_RUN}")
    assert run["status"] == "completed"
    assert run["conclusion"] == "success"
    assert run["head_sha"] == CANDIDATE
    jobs = gh_json(f"repos/{REPO}/actions/runs/{GREEN_RUN}/jobs")["jobs"]
    job = [j for j in jobs if j["id"] == GREEN_JOB]
    assert len(job) == 1 and job[0]["conclusion"] == "success"
    raw_log = sh(["gh", "run", "view", str(GREEN_RUN), "--repo", REPO, "--log"])

    instructions = f"""R8 v15-r1 IMPLEMENTATION SLICE 2 — FRESH BLIND INDEPENDENT REVIEW

Use only the five supplied files. Do not use prior conversation history, model recollection,
or external assumptions.

Exact Slice 2 implementation candidate:
{CANDIDATE}

Frozen executable-schema candidate:
{FROZEN_SCHEMA}

Closed Slice 1 implementation candidate used as dependency:
{SLICE1_CANDIDATE}

Slice 1 closure evidence head:
{SLICE1_CLOSURE_HEAD}

Slice 2 evidence-only freeze head:
{EVIDENCE_HEAD}

Authoritative exact-candidate run/job:
{GREEN_RUN} / {GREEN_JOB}

PACKET FILES
1. 01_INSTRUCTIONS.txt — this review contract.
2. 02_EXACT_SLICE2_CANDIDATE.txt — exact Slice 2 preregistration, workflow, module, harness,
   marker and preserved RED evidence.
3. 03_FROZEN_CONTRACTS_AND_SLICE1_DEPENDENCY.txt — exact frozen runtime/GCP validator contracts
   plus exact closed Slice 1 canonicalizer module and inherited acceptance tests.
4. 04_CONSTRUCTION_EVIDENCE.txt — exact final run/job metadata and raw log, candidate/freeze
   evidence and immutability diff.
5. 05_SHA256_MANIFEST.txt — SHA-256 for files 1-4.

REVIEW SCOPE
Review only bounded deterministic LAS/GGS root construction/verification:
- exact frozen x-gcp1-preimage member sets;
- Sequence type/range closure;
- generic component Digest opacity/non-empty rule;
- inherited GCP canonicalization;
- exact SHA-256 state_root_digest construction;
- verify/fail-closed behavior;
- no self-inclusion or extra/missing members;
- no currentness/certification/authority self-grant;
- stateless deterministic behavior;
- preservation of frozen schema and Slice 1 bytes.

IMPORTANT NONCLAIMS
This slice does not establish:
- that semantic_state_sequence is current LAS state;
- that named LAS heads came from one coherent committed snapshot;
- that GGS barrier_index is certified by ROTATION_PREPARE;
- quorum/sequencer/log/durability correctness;
- STC correctness;
- CSM bundle-digest construction;
- runtime qualification;
- release/deployment/production/policy/terminal authority.

A digest that recomputes correctly can still have authority NONE because currentness/certification
is intentionally out of scope.

Review posture:
- assume false-green until evidenced otherwise;
- inspect exact code/tests/logs, not status labels alone;
- look for member-set drift, self-inclusion, wrong hashing, canonicalization mismatch,
  Python type confusion (especially bool/int), mutation/aliasing, malformed verification,
  component-digest overvalidation/undervalidation, hidden authority claims, stale mutable state,
  exception-to-success paths, and dependency mismatch;
- distinguish a bounded construction defect from a later runtime/currentness requirement.

Return only:

A. OVERALL_DISPOSITION
Choose exactly one: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_IDENTITY
Repeat exact Slice 2 candidate, frozen schema candidate, Slice 1 dependency candidate,
run/job, and packet hashes used.

C. CRITICAL_FINDINGS
Concrete findings only.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. I2_01_TO_I2_16_ASSESSMENT
Assess every frozen I2 case and identify any false-green or untested path.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what a positive Slice 2 construction proves and does not prove.
State whether bounded Slice 2 construction may be adjudicated.
Do not grant runtime qualification or downstream authority.

H. FINAL_GATE
State whether exact candidate {CANDIDATE} may close the Slice 2 independent-review gate.

The review is evidence only, not self-authority.
"""
    (OUT / "01_INSTRUCTIONS.txt").write_text(instructions, encoding="utf-8")

    candidate_paths = [
        "governance-r8/R8-V15-R1-IMPLEMENTATION-AUTHORIZATION.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE2-PREREGISTRATION.md",
        ".github/workflows/r8-v15-r1-implementation-slice2.yml",
        "governance-runtime/r8_v15_r1_state_roots.py",
        "governance-runtime/test_r8_v15_r1_implementation_slice2.py",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE2-MARKER.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE2-CONSTRUCTION-FAILURE-001.json",
    ]
    with (OUT / "02_EXACT_SLICE2_CANDIDATE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 2 exact candidate bytes\n")
        fp.write(sh(["git", "show", "--no-patch", "--format=fuller", CANDIDATE]))
        fp.write(b"\n===== DIFF FROM SLICE 1 CLOSURE HEAD =====\n")
        fp.write(sh(["git", "diff", "--name-status", SLICE1_CLOSURE_HEAD, CANDIDATE]))
        for path in candidate_paths:
            fp.write(exact_section(CANDIDATE, path, "SLICE 2 CANDIDATE FILE"))

    dependency_paths = [
        (FROZEN_SCHEMA, "schemas/governance-r8/v15-r1/runtime-contracts.schema.json"),
        (FROZEN_SCHEMA, "schemas/governance-r8/v15-r1/gcp-rvm-2.json"),
        (FROZEN_SCHEMA, "schemas/governance-r8/v15-r1/schema-freeze-validator-contract.json"),
        (SLICE1_CANDIDATE, "governance-runtime/r8_v15_r1_frozen_schema_runtime.py"),
        (SLICE1_CANDIDATE, "governance-runtime/test_r8_v15_r1_implementation_slice1.py"),
        (SLICE1_CANDIDATE, "governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py"),
        (SLICE1_CANDIDATE, "governance-runtime/test_r8_v15_r1_implementation_slice1_successor2.py"),
        (SLICE1_CANDIDATE, "governance-runtime/test_r8_v15_r1_post_freeze_regression.py"),
        (SLICE1_CANDIDATE, "governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py"),
    ]
    with (OUT / "03_FROZEN_CONTRACTS_AND_SLICE1_DEPENDENCY.txt").open("wb") as fp:
        fp.write(b"Exact frozen contracts and closed Slice 1 dependency bytes.\n")
        for ref, path in dependency_paths:
            fp.write(exact_section(ref, path, "DEPENDENCY / FROZEN CONTRACT"))

    evidence_paths = [
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE2-CONSTRUCTION-GREEN.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE2-FREEZE.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE2-CONSTRUCTION-FAILURE-001.json",
    ]
    with (OUT / "04_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 2 exact construction evidence\n")
        fp.write(b"\n===== EXACT FINAL RUN METADATA =====\n")
        fp.write((json.dumps(run, indent=2) + "\n").encode())
        fp.write(b"\n===== EXACT FINAL JOB METADATA =====\n")
        fp.write((json.dumps(job[0], indent=2) + "\n").encode())
        fp.write(b"\n===== EXACT FINAL RUN RAW LOG =====\n")
        fp.write(raw_log)
        if not raw_log.endswith(b"\n"):
            fp.write(b"\n")

        fp.write(b"\n===== IMMUTABILITY DIFF: FROZEN SCHEMA + SLICE1 MODULE =====\n")
        immut = sh([
            "git", "diff", "--name-status",
            SLICE1_CANDIDATE, CANDIDATE, "--",
            "schemas/governance-r8/v15-r1",
            "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
        ])
        fp.write(immut if immut else b"(none)\n")

        for path in evidence_paths:
            fp.write(exact_section(EVIDENCE_HEAD, path, "SLICE 2 EVIDENCE"))

    files = [
        OUT / "01_INSTRUCTIONS.txt",
        OUT / "02_EXACT_SLICE2_CANDIDATE.txt",
        OUT / "03_FROZEN_CONTRACTS_AND_SLICE1_DEPENDENCY.txt",
        OUT / "04_CONSTRUCTION_EVIDENCE.txt",
    ]
    manifest = [
        "R8 v15-r1 Slice 2 fresh blind review packet SHA-256 manifest",
        f"candidate={CANDIDATE}",
        f"frozen_schema={FROZEN_SCHEMA}",
        f"slice1_candidate={SLICE1_CANDIDATE}",
        f"green_run={GREEN_RUN}",
        f"green_job={GREEN_JOB}",
        "",
    ]
    for p in files:
        manifest.append(f"{sha(p.read_bytes())}  {p.name}")
    (OUT / "05_SHA256_MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    print(f"candidate={CANDIDATE}")
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            print(p.name, p.stat().st_size, sha(p.read_bytes()))


if __name__ == "__main__":
    main()
