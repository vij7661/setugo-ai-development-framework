#!/usr/bin/env python3
import hashlib
import json
import os
import pathlib
import shutil
import subprocess

REPO = os.environ["GITHUB_REPOSITORY"]
CANDIDATE = "f93ca26975ecb64f0da13779889c75b36140cdfc"
FIXED = "d61f9278f1daceac6de536a8894d266726733345"
PRIOR = "5cde19b285989da95c7e68b489663ba2e503ef02"
SEMANTIC = "1fa49fa4adfa6aa47fae68c0f1938083eeb1497f"
ACCEPTANCE = "c1d983ebd6eca0a78a41c946709bf246cf876f68"
EVIDENCE = "96113f437846ba002e39394b758490295081d986"
FINAL_SPM = "84c484121c4c8dd0592bcd7e4c070d8a3ab7f17215f4c3d2b31863fb6dbf6797"

RUNS = [
    {
        "run_id": 36050313120,
        "artifact_id": 10830007314,
        "artifact_name": "r8-v15-r1-spg1-v2-r1-36050313120-1",
        "artifact_sha256": "ed5c6004904be47922b2b86f44ca03cd36522a631f1c87b537888a30e14517fc",
        "label": "stage1",
    },
    {
        "run_id": 36050575731,
        "artifact_id": 10830052586,
        "artifact_name": "r8-v15-r1-spg1-v2-r1-post-run-36050575731-1",
        "artifact_sha256": "ab3a3197216091ca5a66247b45b666024f2c94b0a33695a4bbffb2e64b95dbe3",
        "label": "stage1-verify",
    },
    {
        "run_id": 36051390674,
        "artifact_id": 10831151305,
        "artifact_name": "r8-v15-r1-spg1-v2-r1-final-36051390674-1",
        "artifact_sha256": "d1b5df7c294a9e208ee72ecfe2ee5cb9ef3b34b0a5f3f44e610c516546c6dd44",
        "label": "final",
    },
    {
        "run_id": 36051607632,
        "artifact_id": 10830213828,
        "artifact_name": "r8-v15-r1-spg1-v2-r1-final-post-run-36051607632-1",
        "artifact_sha256": "5821dbc2b9bb367a361ef79da2153df43ffbd98066a6e7752715fa60974eab85",
        "label": "final-verify",
    },
]

OUT = pathlib.Path("review-packet")
RAW = OUT / "raw-artifacts"


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def out(args):
    return subprocess.check_output(args)


def git_blob(ref, path):
    return out(["git", "show", f"{ref}:{path}"])


def git_blob_sha(ref, path):
    return out(["git", "rev-parse", f"{ref}:{path}"]).decode().strip()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def append_blob(fp, ref, path, title="EXACT FILE"):
    data = git_blob(ref, path)
    fp.write(f"\n===== BEGIN {title}: {ref}:{path} =====\n".encode())
    fp.write(f"git_blob_sha1={git_blob_sha(ref, path)}\n".encode())
    fp.write(f"sha256={sha256_bytes(data)}\n".encode())
    fp.write(data)
    if not data.endswith(b"\n"):
        fp.write(b"\n")
    fp.write(f"===== END {title}: {ref}:{path} =====\n".encode())


def gh_json(endpoint):
    return json.loads(out(["gh", "api", endpoint]))


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    RAW.mkdir(parents=True)

    run(["git", "fetch", "--no-tags", "origin", "semantic/r8-v15-r1-gcp-p05-correction-2026-09-24"])
    run(["git", "fetch", "--no-tags", "origin", "freeze/r8-v15-r1-executable-schema-qualified-r3-reviewed-semantic"])

    for ref in [CANDIDATE, FIXED, PRIOR, SEMANTIC, ACCEPTANCE, EVIDENCE]:
        got = out(["git", "rev-parse", f"{ref}^{{commit}}"]).decode().strip()
        assert got == ref, (ref, got)

    instructions = f"""R8 v15-r1 SFV-45 — EXACT RAW-EVIDENCE REVIEW PACKET

Review mode: fresh blind exact-candidate review.
Use only the supplied packet files.
Do not use prior R2/R3 reviews, adjudications, chat history, or model recollection.
Do not accept PASS from labels alone. Recompute/cross-check from the exact bytes and raw evidence.

Exact candidate: {CANDIDATE}
Fixed-point input: {FIXED}
Prior reviewed candidate: {PRIOR}
Reviewed semantic candidate: {SEMANTIC}
Semantic acceptance commit: {ACCEPTANCE}
Final SPM SHA-256: {FINAL_SPM}

A prior fresh review returned INSUFFICIENT_EVIDENCE because the transport contained summaries
instead of enough raw inspectable bytes. That result is an evidence-transport finding, not proof
of a candidate defect and not evidence of candidate correctness.

Review the exact material supplied for semantic mismatch, false-green paths, caller-controlled
weakening, canonicalization ambiguity, omitted authority binding, stale evidence transfer,
provenance/source mismatch, exact-SHA mismatch, and any unsafe SFV-45 grant path.

Required response:
A. OVERALL_DISPOSITION — exactly one of BOUNDED_PASS / CHANGES_REQUIRED / INSUFFICIENT_EVIDENCE
B. EXACT_CANDIDATE_IDENTITY
C. CRITICAL_FINDINGS
D. HIGH_FINDINGS
E. MEDIUM_LOW_FINDINGS
F. REPAIR_CLOSURE_ASSESSMENT
G. SFV_ASSESSMENT — specifically SFV-17,27,30,31,33,35,36,37,44 and whether SFV-45 may be granted
H. AUTHORITY_BOUNDARY

The review grants no implementation, runtime qualification, release, deployment, production,
policy, or terminal authority.
"""
    (OUT / "00_MANIFEST_AND_INSTRUCTIONS.txt").write_text(instructions)

    candidate_files = [
        "schemas/governance-r8/v15-r1/runtime-contracts.schema.json",
        "schemas/governance-r8/v15-r1/gcp-rvm-2.json",
        "schemas/governance-r8/v15-r1/schema-freeze-validator-contract.json",
        "schemas/governance-r8/v15-r1/schema-freeze-traceability.json",
        "governance-r8/R8-V15-R1-SFV45-R3-REVIEWED-SEMANTIC-REBIND.json",
        "governance-r8/R8-V15-R1-SPG1-ENROLLMENT-EXTENSION-V2-R1.json",
        "governance-r8/R8-V15-R1-SPG1-V2-R1-POST-RUN-VERIFICATION.json",
    ]
    with (OUT / "01_EXACT_CANDIDATE_BYTES.txt").open("wb") as fp:
        fp.write("R8 v15-r1 SFV-45 — PART 1: EXACT CANDIDATE BYTES\n".encode())
        fp.write(f"CANDIDATE_SHA={CANDIDATE}\nFIXED_POINT_SHA={FIXED}\n".encode())
        fp.write(b"\n===== CANDIDATE COMMIT =====\n")
        fp.write(out(["git", "show", "--no-patch", "--format=fuller", CANDIDATE]))
        fp.write(b"\n===== EXACT DIFF NAME/STATUS: PRIOR REVIEWED -> CURRENT =====\n")
        fp.write(out(["git", "diff", "--name-status", PRIOR, CANDIDATE]))
        for path in candidate_files:
            append_blob(fp, CANDIDATE, path)

    source_specs = [
        (SEMANTIC, "governance-r8/R8-V15-NORMALIZED-EFFECTIVE-SPEC.md"),
        (SEMANTIC, "governance-r8/R8-V15-NORMALIZED-DETAIL-APPENDIX.md"),
        (SEMANTIC, "governance-r8/R8-V15-R1-GCP-P05-SEMANTIC-CORRECTION.json"),
        (ACCEPTANCE, "governance-r8/R8-V15-R1-GCP-P05-SEMANTIC-SUCCESSOR-INDEPENDENT-REVIEW.json"),
        (ACCEPTANCE, "governance-r8/R8-V15-R1-GCP-P05-SEMANTIC-SUCCESSOR-ACCEPTANCE.json"),
        (SEMANTIC, "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V3.md"),
        (SEMANTIC, "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V5.md"),
        (SEMANTIC, "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V11.md"),
        (SEMANTIC, "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V12.md"),
        (SEMANTIC, "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V13.md"),
        (SEMANTIC, "governance-r8/R8-META-GOVERNANCE-PREREGISTRATION-V14.md"),
    ]
    with (OUT / "02_SEMANTIC_SOURCE_CONTRACTS.txt").open("wb") as fp:
        fp.write("R8 v15-r1 SFV-45 — PART 2: EXACT SEMANTIC/SOURCE CONTRACTS\n".encode())
        for ref, path in source_specs:
            append_blob(fp, ref, path, "EXACT SOURCE")

    with (OUT / "03_PROVENANCE_AND_FULL_SPM.txt").open("wb") as fp:
        fp.write("R8 v15-r1 SFV-45 — PART 3: FULL PROVENANCE SOURCE MAP + FINAL MATERIALIZED SPM\n".encode())
        for path in [
            "schemas/governance-r8/v15-r1/schema-provenance-source-map.json",
            "schemas/governance-r8/v15-r1/schema-provenance-manifest-candidate.json",
        ]:
            append_blob(fp, CANDIDATE, path)

    metadata = []
    for item in RUNS:
        rid = item["run_id"]
        aid = item["artifact_id"]
        run_meta = gh_json(f"repos/{REPO}/actions/runs/{rid}")
        assert run_meta["status"] == "completed"
        assert run_meta["conclusion"] == "success"
        arts = gh_json(f"repos/{REPO}/actions/runs/{rid}/artifacts")["artifacts"]
        art = [a for a in arts if a["id"] == aid]
        assert len(art) == 1
        art = art[0]
        assert art["digest"] == "sha256:" + item["artifact_sha256"]
        assert not art["expired"]
        metadata.append({"run": run_meta, "artifact": art})

        dest = RAW / item["label"]
        dest.mkdir()
        run(["gh", "run", "download", str(rid), "--repo", REPO, "--name", item["artifact_name"], "--dir", str(dest)])

    (OUT / "run-and-artifact-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    final_spm = RAW / "final" / "final-r1" / "spm-final-v2-r1.json"
    assert sha256_bytes(final_spm.read_bytes()) == FINAL_SPM
    assert final_spm.read_bytes() == git_blob(CANDIDATE, "schemas/governance-r8/v15-r1/schema-provenance-manifest-candidate.json")

    sections = {
        "stage1": [
            "stage-r1-attestation-bundle.jsonl",
            "stage-r1-output.json",
            "stage-r1-same-run-verification.json",
            "stage-r1/subject-manifest.json",
            "stage-r1/enrollment-extension.json",
            "stage-r1/qualified-binding.json",
            "stage-r1/schema-freeze-traceability.json",
            "stage-r1/schema-provenance-source-map.json",
            "stage-r1/spm-qualified-v2-r1.sha256",
            "stage-r1/workflow.yml",
        ],
        "stage1-verify": [
            "post-run-gh-attestation-verification.json",
            "post-run-verification.json",
        ],
        "final": [
            "final-r1-attestation-bundle.jsonl",
            "final-r1-output.json",
            "final-r1-same-run-verification.json",
            "final-r1/final-subject-manifest.json",
            "final-r1/enrollment-extension.json",
            "final-r1/prior-post-run-verification.json",
            "final-r1/qualified-binding.json",
            "final-r1/schema-freeze-traceability.json",
            "final-r1/schema-provenance-source-map.json",
            "final-r1/spm-final-v2-r1.sha256",
            "final-r1/workflow.yml",
        ],
        "final-verify": [
            "final-post-run-gh-attestation-verification.json",
            "final-post-run-verification.json",
        ],
    }

    with (OUT / "04_RAW_QUALIFICATION_EVIDENCE.txt").open("wb") as fp:
        fp.write("R8 v15-r1 SFV-45 — PART 4: RAW QUALIFICATION / ATTESTATION / VERIFIER EVIDENCE\n".encode())
        fp.write(b"\n===== RUN + ARTIFACT METADATA =====\n")
        fp.write((OUT / "run-and-artifact-metadata.json").read_bytes())

        for label, paths in sections.items():
            fp.write(f"\n===== {label.upper()} RAW FILES =====\n".encode())
            for rel in paths:
                p = RAW / label / rel
                data = p.read_bytes()
                fp.write(f"\n----- {label}/{rel} -----\n".encode())
                fp.write(f"sha256={sha256_bytes(data)}\n".encode())
                fp.write(data)
                if not data.endswith(b"\n"):
                    fp.write(b"\n")

        append_blob(
            fp,
            EVIDENCE,
            "governance-r8/R8-V15-R1-R3-REVIEWED-SEMANTIC-FINAL-SPM-MATERIALIZATION-EVIDENCE.json",
            "MATERIALIZATION EVIDENCE",
        )
        append_blob(
            fp,
            EVIDENCE,
            "governance-r8/R8-V15-R1-SPG1-R3-REVIEWED-SEMANTIC-FINAL-POST-RUN-VERIFICATION.json",
            "FINAL VERIFIER EVIDENCE",
        )

    packet_files = [
        OUT / "00_MANIFEST_AND_INSTRUCTIONS.txt",
        OUT / "01_EXACT_CANDIDATE_BYTES.txt",
        OUT / "02_SEMANTIC_SOURCE_CONTRACTS.txt",
        OUT / "03_PROVENANCE_AND_FULL_SPM.txt",
        OUT / "04_RAW_QUALIFICATION_EVIDENCE.txt",
    ]

    manifest_lines = [
        "R8 v15-r1 SFV-45 RAW REVIEW PACKET SHA-256 MANIFEST",
        f"candidate={CANDIDATE}",
        f"fixed_point={FIXED}",
        f"semantic={SEMANTIC}",
        f"semantic_acceptance={ACCEPTANCE}",
        f"final_spm_sha256={FINAL_SPM}",
        "",
    ]
    for p in packet_files:
        manifest_lines.append(f"{sha256_bytes(p.read_bytes())}  {p.name}")
    (OUT / "05_PACKET_SHA256_MANIFEST.txt").write_text("\n".join(manifest_lines) + "\n")

    with (OUT / "SFV45_R3_FULL_RAW_EVIDENCE_PACKET.txt").open("wb") as fp:
        for p in packet_files + [OUT / "05_PACKET_SHA256_MANIFEST.txt"]:
            fp.write(p.read_bytes())
            fp.write(b"\n")

    full = OUT / "SFV45_R3_FULL_RAW_EVIDENCE_PACKET.txt"
    (OUT / "SFV45_R3_FULL_RAW_EVIDENCE_PACKET.sha256").write_text(
        f"{sha256_bytes(full.read_bytes())}  {full.name}\n"
    )

    for p in sorted(OUT.glob("*.txt")):
        print(p.name, p.stat().st_size, sha256_bytes(p.read_bytes()))


if __name__ == "__main__":
    main()
