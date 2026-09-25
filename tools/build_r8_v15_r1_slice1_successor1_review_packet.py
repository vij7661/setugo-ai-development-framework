#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import subprocess

REPO = os.environ["GITHUB_REPOSITORY"]
FROZEN_SCHEMA = "f93ca26975ecb64f0da13779889c75b36140cdfc"
PREDECESSOR_IMPL = "e106bdd44973f3b16b5479c7689cbe07cb0f5421"
CANDIDATE = "2cf7adce8bdd67c8b78659d9359c178535af1d73"
EVIDENCE_HEAD = "8d8062c6ea8f8ccf0fd4597f3fa06f481ca8a006"
GREEN_RUN = 36105497132
GREEN_JOB = 107976990604
SPM_PATH = "schemas/governance-r8/v15-r1/schema-provenance-manifest-candidate.json"
SCHEMA_ROOT = "schemas/governance-r8/v15-r1"
OUT = pathlib.Path("review-packet-slice1-successor1")
OUT.mkdir(exist_ok=True)


def sh(args):
    return subprocess.check_output(args)


def git_show(ref, path):
    return sh(["git", "show", f"{ref}:{path}"])


def git_blob(ref, path):
    return sh(["git", "rev-parse", f"{ref}:{path}"]).decode().strip()


def sha(data):
    return hashlib.sha256(data).hexdigest()


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
    lines = data.splitlines(keepends=True)
    parts = []
    buf = bytearray()
    for line in lines:
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

    instructions = f"""R8 v15-r1 IMPLEMENTATION SLICE 1 SUCCESSOR 1 — FRESH BLIND REVIEW

Use only the supplied files. Do not use prior R8 review conversations, prior reviewer
findings, prior adjudications, or model recollection.

Exact implementation candidate:
{CANDIDATE}

Predecessor implementation candidate:
{PREDECESSOR_IMPL}

Frozen executable-schema candidate consumed:
{FROZEN_SCHEMA}

Evidence-only head:
{EVIDENCE_HEAD}

Authoritative exact-candidate construction run/job:
{GREEN_RUN} / {GREEN_JOB}

IMPORTANT PACKET NAVIGATION
- 00_INSTRUCTIONS.txt: this instruction.
- 01_EXACT_SUCCESSOR_CANDIDATE.txt: exact implementation/control bytes changed by the successor.
- 02_SCHEMA_INDEX.txt: exhaustive inventory of every file under the frozen schema directory.
- 03_SCHEMA_NON_SPM.txt: exact bytes for every indexed frozen schema file except the large SPM.
- 04_SPM_PART_*.txt: lossless line-boundary payload chunks of the exact frozen SPM.
  The index gives each chunk payload SHA-256 and the full SPM SHA-256.
- 05_INVOKED_REGRESSION_SOURCES.txt: exact bytes for every regression/test source invoked by the workflow.
- 06_CONSTRUCTION_EVIDENCE.txt: exact run/job metadata, raw CI log, freeze/green evidence and preserved successor failures.
- 07_SHA256_MANIFEST.txt: hashes for every transport file.

Do not report a file as missing until you have checked 02_SCHEMA_INDEX.txt and the mapped
transport file/part. The earlier independent review is deliberately NOT supplied, to preserve
fresh-review independence.

IDENTITY MODEL TO ASSESS
The historical frozen-schema SHA {FROZEN_SCHEMA} is the schema-lineage/configuration identity.
The post-freeze implementation necessarily executes from a later Git commit. Exact schema-byte
identity is established by the exact frozen SPM SHA, exact source-map SHA, per-artifact SPM hashes,
semantic-candidate binding, and generator binding. Assess whether that model is internally sound;
do not assume implementation HEAD must equal the historical schema commit unless the supplied
frozen contract itself requires that.

Review posture:
- assume false-green until evidenced otherwise;
- inspect exact code/tests/logs, not PASS labels alone;
- verify the single-read hash/parse closure and look for remaining TOCTOU paths;
- look for caller-controlled weakening, path traversal, symlink/identity substitution, cache/stale-state,
  exception-to-success, canonicalization ambiguity, Unicode/NFC/int64 errors, or incomplete SPM checks;
- verify workflow-trigger coverage and failure-history preservation;
- distinguish construction evidence from runtime qualification and all downstream authority.

Return only:

A. OVERALL_DISPOSITION
Choose exactly one: BOUNDED_PASS, CHANGES_REQUIRED, INSUFFICIENT_EVIDENCE

B. EXACT_IDENTITY
Repeat candidate, frozen schema, run/job, and packet/full SPM hashes you used.

C. CRITICAL_FINDINGS
Concrete findings only.

D. HIGH_FINDINGS
Concrete findings only.

E. MEDIUM_LOW_FINDINGS
Concrete findings only.

F. I1_AND_SUCCESSOR_REPAIR_ASSESSMENT
Assess original I1-01..I1-16 and S1R-01..S1R-08, including whether the predecessor TOCTOU
and evidence-transport gaps are closed. Separate code defects from transport gaps.

G. IMPLEMENTATION_AND_AUTHORITY_BOUNDARY
State exactly what construction proves and does not prove. Explicitly state whether bounded
Slice 1 construction may be adjudicated.

H. FINAL_GATE
State whether exact candidate {CANDIDATE} may close the Slice 1 independent-review gate.

This review is evidence only. It grants no runtime qualification, release, deployment,
production, policy, or terminal authority.
"""
    (OUT / "00_INSTRUCTIONS.txt").write_text(instructions, encoding="utf-8")

    candidate_paths = [
        ".github/workflows/r8-v15-r1-implementation-slice1.yml",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-PREREGISTRATION.md",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-PREREGISTRATION.md",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-MARKER.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-CONTROL-FAILURE-001.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-CONSTRUCTION-FAILURE-001.json",
        "governance-runtime/r8_v15_r1_frozen_schema_runtime.py",
        "governance-runtime/test_r8_v15_r1_implementation_slice1.py",
        "governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py",
        "governance-runtime/test_r8_v15_r1_post_freeze_regression.py",
    ]
    with (OUT / "01_EXACT_SUCCESSOR_CANDIDATE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 1 Successor 1 - exact candidate scope\n")
        fp.write(sh(["git", "show", "--no-patch", "--format=fuller", CANDIDATE]))
        fp.write(b"\n===== SUCCESSOR DIFF VS PREDECESSOR IMPLEMENTATION =====\n")
        fp.write(sh(["git", "diff", "--name-status", PREDECESSOR_IMPL, CANDIDATE]))
        fp.write(b"\n===== FROZEN SCHEMA DIRECTORY DIFF VS FROZEN SCHEMA COMMIT =====\n")
        schema_diff = sh(["git", "diff", "--name-status", FROZEN_SCHEMA, CANDIDATE, "--", SCHEMA_ROOT])
        fp.write(schema_diff if schema_diff else b"(none)\n")
        for path in candidate_paths:
            fp.write(exact_section(CANDIDATE, path, "SUCCESSOR CANDIDATE FILE"))

    schema_paths = sh(["git", "ls-tree", "-r", "--name-only", FROZEN_SCHEMA, SCHEMA_ROOT]).decode().splitlines()
    assert SPM_PATH in schema_paths

    schema_index = []
    non_spm = OUT / "03_SCHEMA_NON_SPM.txt"
    with non_spm.open("wb") as fp:
        fp.write(b"Exact frozen schema inputs except large SPM candidate.\n")
        for path in schema_paths:
            data = git_show(FROZEN_SCHEMA, path)
            row = {
                "path": path,
                "git_blob_sha1": git_blob(FROZEN_SCHEMA, path),
                "sha256": sha(data),
                "byte_count": len(data),
            }
            if path == SPM_PATH:
                row["transport"] = "04_SPM_PART_*.txt"
            else:
                row["transport"] = "03_SCHEMA_NON_SPM.txt"
                fp.write(exact_section(FROZEN_SCHEMA, path, "FROZEN SCHEMA INPUT"))
            schema_index.append(row)

    spm = git_show(FROZEN_SCHEMA, SPM_PATH)
    spm_parts = split_lines(spm)
    spm_part_rows = []
    for idx, payload in enumerate(spm_parts, 1):
        name = f"04_SPM_PART_{idx:02d}_OF_{len(spm_parts):02d}.txt"
        meta = (
            f"R8 v15-r1 exact frozen SPM payload chunk\n"
            f"source_commit={FROZEN_SCHEMA}\n"
            f"path={SPM_PATH}\n"
            f"git_blob_sha1={git_blob(FROZEN_SCHEMA, SPM_PATH)}\n"
            f"full_file_sha256={sha(spm)}\n"
            f"full_file_bytes={len(spm)}\n"
            f"part_index={idx}\n"
            f"part_count={len(spm_parts)}\n"
            f"payload_sha256={sha(payload)}\n"
            f"payload_bytes={len(payload)}\n"
            f"===== BEGIN EXACT SPM PAYLOAD PART {idx}/{len(spm_parts)} =====\n"
        ).encode()
        tail = f"===== END EXACT SPM PAYLOAD PART {idx}/{len(spm_parts)} =====\n".encode()
        (OUT / name).write_bytes(meta + payload + (b"" if payload.endswith(b"\n") else b"\n") + tail)
        spm_part_rows.append({
            "transport_file": name,
            "payload_sha256": sha(payload),
            "payload_bytes": len(payload),
        })

    index_doc = {
        "schema":"r8-v15-r1-successor1-review-schema-index/v1",
        "frozen_schema_commit":FROZEN_SCHEMA,
        "schema_file_count":len(schema_paths),
        "spm":{
            "path":SPM_PATH,
            "git_blob_sha1":git_blob(FROZEN_SCHEMA, SPM_PATH),
            "sha256":sha(spm),
            "byte_count":len(spm),
            "parts":spm_part_rows,
            "concatenated_payload_sha256":sha(b"".join(spm_parts)),
            "concatenation_exact":b"".join(spm_parts)==spm,
        },
        "files":schema_index,
    }
    (OUT / "02_SCHEMA_INDEX.txt").write_text(json.dumps(index_doc,indent=2)+"\n",encoding="utf-8")

    regression_paths = [
        ".github/workflows/r8-v15-r1-implementation-slice1.yml",
        "governance-runtime/test_r8_v15_r1_implementation_slice1.py",
        "governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py",
        "governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py",
        "governance-runtime/test_r8_v15_r1_post_freeze_regression.py",
    ]
    with (OUT / "05_INVOKED_REGRESSION_SOURCES.txt").open("wb") as fp:
        fp.write(b"Exact sources invoked by the final successor workflow.\n")
        for path in regression_paths:
            fp.write(exact_section(CANDIDATE, path, "INVOKED WORKFLOW/REGRESSION SOURCE"))

    run_log = sh(["gh", "run", "view", str(GREEN_RUN), "--repo", REPO, "--log"])
    evidence_paths = [
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-CONSTRUCTION-GREEN.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-FREEZE.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-CONTROL-FAILURE-001.json",
        "governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-SUCCESSOR1-CONSTRUCTION-FAILURE-001.json",
        "governance-r8/R8-V15-R1-EXECUTABLE-SCHEMA-FREEZE.json",
    ]
    with (OUT / "06_CONSTRUCTION_EVIDENCE.txt").open("wb") as fp:
        fp.write(b"R8 v15-r1 Slice 1 Successor 1 construction evidence\n")
        fp.write(b"\n===== EXACT FINAL RUN METADATA =====\n")
        fp.write((json.dumps(run,indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL JOB METADATA =====\n")
        fp.write((json.dumps(job[0],indent=2)+"\n").encode())
        fp.write(b"\n===== EXACT FINAL RUN RAW LOG =====\n")
        fp.write(run_log)
        if not run_log.endswith(b"\n"):
            fp.write(b"\n")
        for path in evidence_paths:
            fp.write(exact_section(EVIDENCE_HEAD, path, "EVIDENCE RECORD"))

    files = sorted([p for p in OUT.iterdir() if p.is_file()])
    # Do not include manifest/full before they exist.
    files = [p for p in files if p.name not in {"07_SHA256_MANIFEST.txt","R8_V15_R1_SLICE1_SUCCESSOR1_FULL_REVIEW_PACKET.txt","R8_V15_R1_SLICE1_SUCCESSOR1_FULL_REVIEW_PACKET.sha256"}]
    manifest_lines = [
        "R8 v15-r1 Slice 1 Successor 1 review transport SHA-256 manifest",
        f"implementation_candidate={CANDIDATE}",
        f"frozen_schema_candidate={FROZEN_SCHEMA}",
        f"green_run={GREEN_RUN}",
        f"green_job={GREEN_JOB}",
        f"full_spm_sha256={sha(spm)}",
        "",
    ]
    for p in files:
        manifest_lines.append(f"{sha(p.read_bytes())}  {p.name}")
    (OUT / "07_SHA256_MANIFEST.txt").write_text("\n".join(manifest_lines)+"\n",encoding="utf-8")

    all_files = files + [OUT/"07_SHA256_MANIFEST.txt"]
    full = OUT / "R8_V15_R1_SLICE1_SUCCESSOR1_FULL_REVIEW_PACKET.txt"
    with full.open("wb") as fp:
        for p in all_files:
            fp.write(f"\n######## TRANSPORT FILE: {p.name} ########\n".encode())
            fp.write(p.read_bytes())
            if not p.read_bytes().endswith(b"\n"):
                fp.write(b"\n")
    (OUT/"R8_V15_R1_SLICE1_SUCCESSOR1_FULL_REVIEW_PACKET.sha256").write_text(
        f"{sha(full.read_bytes())}  {full.name}\n",encoding="utf-8"
    )

    print(f"schema_files={len(schema_paths)}")
    print(f"spm_parts={len(spm_parts)}")
    print(f"full_spm_sha256={sha(spm)}")
    for p in sorted(OUT.iterdir()):
        if p.is_file():
            print(p.name, p.stat().st_size, sha(p.read_bytes()))


if __name__ == "__main__":
    main()
