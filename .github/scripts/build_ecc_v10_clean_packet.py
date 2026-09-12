from __future__ import annotations

from pathlib import Path
import glob
import hashlib
import json
import subprocess

ROOT = Path.cwd()
CANDIDATE = "63617dd1f01f0063b5534de128d5afce17f169be"
OUT = ROOT / "ECC_Derived_V10_Clean_External_Review_Packet.md"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


candidate_tree = subprocess.check_output(
    ["git", "rev-parse", f"{CANDIDATE}^{{tree}}"], text=True
).strip()
packaging_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()

patterns = [
    "experiments/ecc-derived/PROGRAM-CHARTER.md",
    "experiments/ecc-derived/FULL-COVERAGE-COMPLETION.md",
    "experiments/ecc-derived/EXP-ECC-*.md",
    "experiments/ecc-derived/V*-*.md",
    "experiments/ecc-derived/evidence/*.json",
    "experiments/ecc_derived/ecc_*.py",
    "experiments/ecc_derived/ecc_*.json",
    "experiments/ecc_derived/test_*.py",
    "experiments/ecc_derived/run_v*.py",
    ".github/scripts/apply_ecc_v*.py",
    ".github/workflows/ecc-derived-parallel.yml",
    ".github/workflows/apply-ecc-v*.yml",
]

files: set[Path] = set()
for pattern in patterns:
    for value in glob.glob(pattern):
        path = Path(value)
        if path.is_file():
            files.add(path)
files = set(sorted(files, key=lambda p: p.as_posix()))
if not files:
    raise SystemExit("No packet source files found")
files_sorted = sorted(files, key=lambda p: p.as_posix())

transcript = Path("/tmp/ecc_v10_test_transcript.txt").read_text(
    encoding="utf-8", errors="replace"
)
if "Ran 183 tests" not in transcript or "\nOK\n" not in transcript:
    raise SystemExit("Frozen V10 suite transcript is not 183/183 green")

manifest = []
for path in files_sorted:
    raw = path.read_bytes()
    manifest.append(
        {
            "path": path.as_posix(),
            "bytes": len(raw),
            "sha256": sha256_bytes(raw),
        }
    )

header = f"""# ECC-Derived Seven-Experiment Program — V10 Clean External Engineering Review Packet

## Packet identity

- Packet class: `CLEAN_EXTERNAL_ENGINEERING_REVIEW_PACKET`
- Review context requirement: `CLEAN_PACKET_ONLY_CONTEXT`
- Frozen reviewed candidate SHA: `{CANDIDATE}`
- Frozen reviewed candidate tree: `{candidate_tree}`
- Packaging branch head: `{packaging_head}`
- Packaging branch allowed diff from candidate: only the packet workflow and packet-builder script
- Evidence authority: `NONE_EVIDENCE_ONLY`
- Manual-review threshold contribution from any AI-generated review: `0`
- Production qualification claimed: `NO`
- V18 integration claimed: `NO`
- Live platform attestation claimed: `NO`
- Independent production trust-root claimed: `NO`
- Durable signed cross-process provenance claimed: `NO`

## Reviewer isolation instruction

Review **only this packet**. Do not use prior conversations, cached review outputs, model memory, repository browsing, or earlier dispositions. Prior reviewer prose is intentionally excluded. The packet contains the frozen experiment contracts, current reference mechanism, falsification tests, preserved RED/GREEN evidence records, repair lineage, and a fresh test transcript needed for this engineering review.

If you are an AI reviewer, begin your response with exactly:

`REVIEW_CONTEXT = CLEAN_PACKET_ONLY_CONTEXT`

`EVIDENCE_DECLARATION = AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`

Any AI review is engineering evidence only and contributes zero to a qualifying manual-review threshold.

## Current bounded program posture

The seven ECC-derived requirements remain evidence-only research candidates.

- EXP-ECC-1..5: reference mechanisms have been progressively falsified/hardened through V10, but still require live platform/integration evidence before adoption.
- EXP-ECC-6: `DEFER_PENDING_INTEGRATION_EVIDENCE` — no live automated reviewer transport/provider-identity/manual-review qualification is claimed.
- EXP-ECC-7: `DEFER_PENDING_INTEGRATION_EVIDENCE` — no actual governed learning/retraction pipeline integration is claimed.
- V10 reference mechanism: `BOUNDED_GREEN_PENDING_EXTERNAL_ENGINEERING_REREVIEW`.
- Nothing in this packet grants release, merge, production, freeze, qualification, terminal, or policy authority.

## What the reviewer must decide

For each EXP-ECC-1 through EXP-ECC-7, assign exactly one disposition:

- `ADOPT_REQUIREMENT_CANDIDATE`
- `NARROW_REQUIREMENT_CANDIDATE`
- `REJECT_REQUIREMENT_CANDIDATE`
- `DEFER_PENDING_INTEGRATION_EVIDENCE`
- `INSUFFICIENT_EVIDENCE`

Then assess the complete family on all of the following:

1. Does the preserved RED→repair→GREEN history support the claimed bounded reference-mechanism conclusions without laundering earlier failures?
2. Are all test supersessions explicit, technically justified, and non-history-rewriting?
3. Do the V5→V10 hardening generations close the demonstrated self-grant/false-green paths they claim to close?
4. Does the current mechanism still contain a concrete false-green path **inside the stated V10 threat model** that should block impact adjudication?
5. Are the remaining nonclaims (captured-callable mutation, deeper OS/runtime primitives, reflective/interpreter/native-memory compromise, repository/code-replacement authority, live platform attestation, independent trust roots, durable cross-process provenance) appropriately bounded, or does any one expose a design defect that must be fixed before bounded impact adjudication?
6. Is `REFERENCE_REPO_BOUND_SIMULATION_ONLY` evidence appropriately constrained, or is it being used as a substitute for live/independent evidence anywhere?
7. Should EXP-ECC-6 and EXP-ECC-7 remain deferred?
8. Is the seven-experiment family ready for **governed impact adjudication as requirement candidates**, while remaining non-production and non-authoritative?

## Required review output

Provide:

- Overall disposition: `READY_FOR_BOUNDED_IMPACT_ADJUDICATION`, `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`, or `INSUFFICIENT_EVIDENCE`.
- Per-experiment disposition for EXP-ECC-1..7.
- Findings ranked Critical / High / Medium / Low with exact artifact/function/test references.
- Any false-green path as a concrete attack sequence.
- Any missing negative and positive falsification cases.
- Assessment of historical supersessions and RED preservation.
- Assessment of whether remaining nonclaims are acceptable bounded exclusions.
- Freeze recommendation: `SAFE_TO_FREEZE_EXPERIMENT_EVIDENCE_FOR_IMPACT_ADJUDICATION`, `DO_NOT_FREEZE`, or `INSUFFICIENT_EVIDENCE_TO_FREEZE`.
- End with exactly: `AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`.

Do **not** grant production readiness, release authority, merge authority, policy authority, or manual-review qualification.

## Artifact manifest

```json
""" + json.dumps(manifest, indent=2) + """
```

## Fresh V10 execution transcript from packet build

This transcript was generated on the packaging branch after a guard verified that the only diff from the exact frozen candidate is the two packaging-only files.

```text
""" + transcript + """
```

## Frozen artifact contents
"""

parts = [header]
for item in manifest:
    path = Path(item["path"])
    text = path.read_text(encoding="utf-8", errors="replace")
    suffix = path.suffix.lower()
    language = (
        "json"
        if suffix == ".json"
        else "python"
        if suffix == ".py"
        else "yaml"
        if suffix in {".yml", ".yaml"}
        else "text"
    )
    parts.append(
        f"\n\n---\n\n### `{item['path']}`\n\n"
        f"SHA-256: `{item['sha256']}`  \nBytes: `{item['bytes']}`\n\n"
        f"```{language}\n{text}\n```\n"
    )

OUT.write_text("".join(parts), encoding="utf-8")
packet = OUT.read_bytes()
print(f"PACKET_PATH={OUT.name}")
print(f"PACKET_BYTES={len(packet)}")
print(f"PACKET_SHA256={sha256_bytes(packet)}")
print(f"PACKET_ARTIFACT_COUNT={len(manifest)}")
