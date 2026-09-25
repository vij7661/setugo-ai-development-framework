#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import subprocess

REPO = os.environ["GITHUB_REPOSITORY"]
FROZEN_SCHEMA = "f93ca26975ecb64f0da13779889c75b36140cdfc"
PREDECESSOR_IMPL = "2cf7adce8bdd67c8b78659d9359c178535af1d73"
CANDIDATE = "fdf825cb45fbd00441a4cd02bb1912bb3cda01b0"
EVIDENCE_HEAD = "181f83bbdfbb59894705e7df92b8cbf33708e136"
GREEN_RUN = 36107415256
GREEN_JOB = 107983021495
SCHEMA_ROOT = "schemas/governance-r8/v15-r1"
SPM_PATH = f"{SCHEMA_ROOT}/schema-provenance-manifest-candidate.json"
OUT = pathlib.Path("review-packet-slice1-successor2")
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


def split_lines(data, max_payload=650_000):
    parts = []
    buf = bytearray()
    for line in data.splitlines(keepends=True):
        if buf and len(buf) + len(line) > max_payload:
            parts.append(bytes(buf))
            buf = bytearray()
        buf.extend(line)
    if buf or not parts:
        parts.append(bytes(buf))
    assert b"".join(parts) == data
    return parts


def main():
    for ref in [FROZEN_SCHEMA, PREDECESSOR_IMPL, CANDIDATE, EVIDENCE_HEAD]:
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

    schema_paths = sh([
        "git", "ls-tree", "-r", "--name-only", FROZEN_SCHEMA, SCHEMA_ROOT
    ]).decode().splitlines()
    assert SPM_PATH in schema_paths

    # File 2: every frozen schema file except the large SPM.
    non_spm = OUT / "02_FROZEN_SCHEMA_NON_SPM.txt"
    schema_index = []
    with non_spm.open("wb") as fp:
        fp.write(b"R8 v15-r1 frozen schema inputs -- every file except materialized SPM.\n")
        fp.write(f"frozen_schema_commit={FROZEN_SCHEMA}\n".encode())
        for path in schema_paths:
            data = git_show(FROZEN_SCHEMA, path)
            row = {
                "path": path,
                "git_blob_sha1": git_blob(FROZEN_SCHEMA, path),
                "sha256": sha(data),
                "byte_count": len(data),
            }
            if path == SPM_PATH:
                row["transport"] = "03..06 SPM files"
            else:
                row["transport"] = "02_FROZEN_SCHEMA_NON_SPM.txt"
                fp.write(exact_section(FROZEN_SCHEMA, path, "FROZEN SCHEMA INPUT"))
            schema_index.append(row)

    # Files 3-6: exact SPM chunks.
    spm = git_show(FROZEN_SCHEMA, SPM_PATH)
    parts = split_lines(spm)
    assert len(parts) == 4
    part_info = []
    for idx, payload in enumerate(parts, 1):
        name = f"{idx+2:02d}_FROZEN_SPM_PART_{idx}_OF_4.txt"
        meta = (
            "R8 v15-r1 exact frozen SPM payload chunk\n"
            f"source_commit={FROZEN_SCHEMA}\n"
            f"path={SPM_PATH}\n"
            f"git_blob_sha1={git_blob(FROZEN_SCHEMA, SPM_PATH)}\n"
            f"full_file_sha256={sha(spm)}\n"
            f"full_file_bytes={len(spm)}\n"
            f"part_index={idx}\n"
            "part_count=4\n"
            f"payload_sha256={sha(payload)}\n"
            f"payload_bytes={len(payload)}\n"
            f"===== BEGIN EXACT SPM PAYLOAD PART {idx}/4 =====\n"
        ).encode()
        tail = f"===== END EXACT SPM PAYLOAD PART {idx}/4 =====\n".encode()
        outp = OUT / name
        outp.write_bytes(meta + payload + (b"" if payload.endswith(b"\n") else b"\n") + tail)
        part_info.append({
            "transport_file": name,
            "payload_sha256": sha(payload),
            "payload_bytes": len(payload),
            "transport_sha256": sha(outp.read_bytes()),
            "transport_bytes": outp.stat().st_size,
        })
    assert b"".join(parts) == spm

    non_spm_sha = sha(non_spm.read_bytes())
    non_spm_bytes = non_spm.stat().st_size

    # File 1: everything else needed for review.
    instructions = f"""R8 v15-r1 IMPLEMENTATION SLICE 1 SUCCESSOR 2 — FRESH BLIND REVIEW

USE ONLY THESE SIX FILES. Do not use prior review conversations, prior reviewer findings,
prior adjudications, or model recollection.

FILES
1. 01_CORE_REVIEW_EVIDENCE.txt — this instruction + exact candidate code/tests/workflow,
   exhaustive schema index, exact final run/job/log, freeze/green evidence, and transport hashes.
2. 02_FROZEN_SCHEMA_NON_SPM.txt — exact bytes for every frozen schema file except the large SPM.
3-6. 03..06_FROZEN_SPM_PART_* — four lossless line-boundary chunks of the exact frozen SPM.

Exact implementation candidate:
{CANDIDATE}

Predecessor implementation candidate:
{PREDECESSOR_IMPL}

Frozen executable-schema candidate:
{FROZEN_SCHEMA}

Evidence-only freeze head:
{EVIDENCE_HEAD}

Authoritative exact-candidate run/job:
{GREEN_RUN} / {GREEN_JOB}

The full frozen SPM SHA-256 is:
{sha(spm)}

IMPORTANT TRANSPORT RULE
Before reporting any missing/truncated evidence:
- consult the exhaustive schema index in this CORE file;
- verify the mapped transport filename;
- for the SPM, verify all four BEGIN/END payload markers and concatenate payloads in order;
- compare concatenated SHA-256 to the full SPM hash above.
There are exactly six intended review attachments. No file 07 or later exists.

Review posture:
- assume false-green until demonstrated otherwise;
- inspect exact code/tests/logs, not status labels alone;
- test the nested integer lexical-preservation repair, especially object/array -0;
- test symlink/realpath confinement, including same-byte external targets and symlink components;
- verify exact full-path source-map/SPM artifact equality;
- inspect artifact-ID/digest shape checks, SPM cardinality, single-read hash/use closure,
  GCP positive/rejection-vector behavior, Unicode/NFC/int64 rules, path traversal, cache/stale state,
  exception-to-success paths, caller-controlled weakening, and authority-boundary metadata;
- verify original I1 + Successor 1 S1R + Successor 2 S1R2 are all represented in the final run;
- distinguish bounded construction evidence from runtime qualification.

Return only:

A. OVERALL_DISPOSITION
Choose exactly one: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_IDENTITY
Repeat exact candidate, frozen schema, run/job, full SPM SHA-256, and the six transport hashes used.

C. CRITICAL_FINDINGS
Concrete findings only.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. I1_S1R_S1R2_ASSESSMENT
Assess I1-01..I1-16, S1R-01..S1R-08, and S1R2-01..S1R2-08. State whether nested
negative-zero, TOCTOU, symlink/path, source-map path, and prior transport gaps are closed.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State what bounded construction proves and does not prove. Explicitly state whether bounded
Slice 1 construction may be adjudicated. Do not grant runtime qualification, release,
deployment, production, policy, or terminal authority.

H. FINAL_GATE
State whether exact candidate {CANDIDATE} may close the Slice 1 independent-review gate.

This review is evidence only, not self-authority.
"""

    candidate_paths = [
        ".github/workflows/r8-v15-r1-implementation-slice1.yml",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-AUTHORIZATION.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-PREREGISTRATION.md",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-PREREGISTRATION.md",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR2-PREREGISTRATION.md",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-MARKER.json",
        "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
        "governance-runtime/test_r8_v15_r1_implementation_slice1.py",
        "governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py",
        "governance-runtime/test_r8_v15_r1_implementation_slice1_successor2.py",
        "governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py",
        "governance-runtime/test_r8_v15_r1_post_freeze_regression.py",
    ]
    evidence_paths = [
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR2-CONSTRUCTION-GREEN.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR2-FREEZE.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR2-CONTROL-FAILURE-001.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR2-CONSTRUCTION-FAILURE-001.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR2-CONSTRUCTION-FAILURE-002.json",
        "governance-r8/R8-V15-R1-EXECUTABLE-SCHEMA-FREEZE.json",
    ]

    schema_index_doc = {
        "schema":"r8-v15-r1-successor2-review-schema-index/v1",
        "frozen_schema_commit":FROZEN_SCHEMA,
        "schema_file_count":len(schema_paths),
        "full_spm":{
            "path":SPM_PATH,
            "git_blob_sha1":git_blob(FROZEN_SCHEMA, SPM_PATH),
            "sha256":sha(spm),
            "byte_count":len(spm),
            "parts":part_info,
            "concatenation_exact":b"".join(parts)==spm,
        },
        "non_spm_transport":{
            "file":"02_FROZEN_SCHEMA_NON_SPM.txt",
            "sha256":non_spm_sha,
            "byte_count":non_spm_bytes,
        },
        "files":schema_index,
    }

    core = OUT / "01_CORE_REVIEW_EVIDENCE.txt"
    with core.open("wb") as fp:
        fp.write(instructions.encode())
        fp.write(b"\n===== EXHAUSTIVE FROZEN SCHEMA INDEX =====\n")
        fp.write((json.dumps(schema_index_doc,indent=2)+"\n").encode())

        fp.write(b"\n===== EXACT CANDIDATE COMMIT =====\n")
        fp.write(sh(["git","show","--no-patch","--format=fuller",CANDIDATE]))

        fp.write(b"\n===== FROZEN SCHEMA BYTE DIFF =====\n")
        schema_diff=sh(["git","diff","--name-status",FROZEN_SCHEMA,CANDIDATE,"--",SCHEMA_ROOT])
        fp.write(schema_diff if schema_diff else b"(none)\n")

        fp.write(b"\n===== SUCCESSOR 2 GOVERNED CODE / TEST / WORKFLOW BYTES =====\n")
        for path in candidate_paths:
            fp.write(exact_section(CANDIDATE,path,"CANDIDATE REVIEW FILE"))

        fp.write(b"\n===== EXACT FINAL RUN METADATA =====\n")
        fp.write((json.dumps(run,indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL JOB METADATA =====\n")
        fp.write((json.dumps(job[0],indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL RUN RAW LOG =====\n")
        fp.write(raw_log)
        if not raw_log.endswith(b"\n"):
            fp.write(b"\n")

        fp.write(b"\n===== CONSTRUCTION/FREEZE EVIDENCE =====\n")
        for path in evidence_paths:
            fp.write(exact_section(EVIDENCE_HEAD,path,"EVIDENCE RECORD"))

        fp.write(b"\n===== EXTERNAL TRANSPORT HASHES =====\n")
        fp.write(f"02_FROZEN_SCHEMA_NON_SPM.txt sha256={non_spm_sha} bytes={non_spm_bytes}\n".encode())
        for row in part_info:
            fp.write(
                f"{row['transport_file']} sha256={row['transport_sha256']} "
                f"bytes={row['transport_bytes']} payload_sha256={row['payload_sha256']} "
                f"payload_bytes={row['payload_bytes']}\n".encode()
            )
        fp.write(
            f"SPM_CONCATENATED_PAYLOAD_SHA256={sha(b''.join(parts))}\n"
            f"SPM_EXPECTED_FULL_SHA256={sha(spm)}\n"
            f"SPM_CONCATENATION_EXACT={b''.join(parts)==spm}\n".encode()
        )

    print(f"candidate={CANDIDATE}")
    print(f"run={GREEN_RUN} job={GREEN_JOB}")
    print(f"schema_files={len(schema_paths)}")
    print(f"spm_sha256={sha(spm)}")
    print(f"spm_parts={len(parts)}")
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            print(p.name, p.stat().st_size, sha(p.read_bytes()))


if __name__ == "__main__":
    main()
