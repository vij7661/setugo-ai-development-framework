from __future__ import annotations

from pathlib import Path
import glob
import hashlib
import json
import subprocess

ROOT = Path.cwd()
CANDIDATE = "39d19dbf4d62b2861128f00e62a7325ff1039fa6"
OUT = ROOT / "ECC_Derived_V11_Clean_External_Review_Packet.md"


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
files_sorted = sorted(files, key=lambda p: p.as_posix())
if not files_sorted:
    raise SystemExit("No packet source files found")

transcript = Path("/tmp/ecc_v11_test_transcript.txt").read_text(
    encoding="utf-8", errors="replace"
)
if "Ran 190 tests" not in transcript or "\nOK\n" not in transcript:
    raise SystemExit("Frozen V11 suite transcript is not 190/190 green")

manifest = []
for path in files_sorted:
    raw = path.read_bytes()
    manifest.append({"path": path.as_posix(), "bytes": len(raw), "sha256": sha256_bytes(raw)})

header = f"""# ECC-Derived Seven-Experiment Program — V11 Clean External Engineering Re-Review Packet

## Packet identity

- Packet class: `CLEAN_EXTERNAL_ENGINEERING_REREVIEW_PACKET`
- Review context requirement: `CLEAN_PACKET_ONLY_CONTEXT`
- Frozen reviewed candidate SHA: `{CANDIDATE}`
- Frozen reviewed candidate tree: `{candidate_tree}`
- Packaging branch head: `{packaging_head}`
- Packaging branch allowed diff from candidate: only the packet workflow and packet-builder script
- Evidence authority: `NONE_EVIDENCE_ONLY`
- Manual-review threshold contribution from any AI-generated review: `0`
- Production qualification claimed: `NO`
- Live platform attestation claimed: `NO`
- Independent production trust-root claimed: `NO`
- Durable signed cross-process provenance claimed: `NO`

## Reviewer isolation instruction

Review **only this packet**. Do not use prior conversations, cached review outputs, model memory, repository browsing, or earlier reviewer dispositions. Prior reviewer prose is intentionally excluded. The packet contains the frozen experiment contracts, preserved RED/GREEN evidence lineage, current V11 mechanism, frozen V11 assertions, repair lineage, and a fresh 190-test transcript.

If you are an AI reviewer, begin your response with exactly:

`REVIEW_CONTEXT = CLEAN_PACKET_ONLY_CONTEXT`

`EVIDENCE_DECLARATION = AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`

Any AI review is engineering evidence only and contributes zero to a qualifying manual-review threshold.

## Current bounded posture

- V10 external re-review identified an ordinary-module mutable-global false-green path; V11 was opened to falsify that class.
- V11 preserved a clean pre-repair RED: `190 tests; 5 failures; 0 errors`.
- V11 repairs bind exact checked-entrypoint function objects, recursively referenced module-global dependencies, mutable-data state, helper function identity/code/defaults, and closure-captured experiment coverage.
- The same frozen V11 suite now reports `190/190 PASS` at the reviewed ledger head.
- EXP-ECC-1..5 remain reference mechanisms only and still require live platform/integration evidence before adoption.
- EXP-ECC-6 and EXP-ECC-7 remain `DEFER_PENDING_INTEGRATION_EVIDENCE`.
- Nothing in this packet grants production, release, merge, freeze, terminal, policy, or manual-review authority.

## What the reviewer must decide

For each EXP-ECC-1 through EXP-ECC-7 assign exactly one disposition:

- `ADOPT_REQUIREMENT_CANDIDATE`
- `NARROW_REQUIREMENT_CANDIDATE`
- `REJECT_REQUIREMENT_CANDIDATE`
- `DEFER_PENDING_INTEGRATION_EVIDENCE`
- `INSUFFICIENT_EVIDENCE`

Then assess:

1. Does V11 actually close the mutable-module-global false-green class that blocked V10?
2. Can ordinary module monkeypatching still cause candidate authority to be minted while all V11 runtime checks pass?
3. Is recursive referenced-global binding complete enough for the stated bounded threat model, including helper functions, mutable data, defaults, and same-code/new-function substitution?
4. Are the V11 RED→repair→GREEN and earlier V2→V10 histories preserved without failure laundering or unjustified supersession?
5. Are any remaining nonclaims actually ordinary-module attacks that belong inside the present threat model and therefore still block bounded impact adjudication?
6. Is `REFERENCE_REPO_BOUND_SIMULATION_ONLY` still correctly constrained as non-live evidence?
7. Should EXP-ECC-6 and EXP-ECC-7 remain deferred?
8. Is the seven-experiment family now ready for governed bounded impact adjudication as requirement candidates, while remaining non-production and non-authoritative?

## Required review output

Provide:

- Overall disposition: `READY_FOR_BOUNDED_IMPACT_ADJUDICATION`, `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`, or `INSUFFICIENT_EVIDENCE`.
- Per-experiment disposition for EXP-ECC-1..7.
- Findings ranked Critical / High / Medium / Low with exact artifact/function/test references.
- Any false-green path as a concrete attack sequence.
- Missing negative and positive falsification cases.
- Assessment of historical supersessions and RED preservation.
- Assessment of whether remaining nonclaims are acceptable bounded exclusions.
- Freeze recommendation: `SAFE_TO_FREEZE_EXPERIMENT_EVIDENCE_FOR_IMPACT_ADJUDICATION`, `DO_NOT_FREEZE`, or `INSUFFICIENT_EVIDENCE_TO_FREEZE`.
- End with exactly: `AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`.

Do **not** grant production readiness, release authority, merge authority, policy authority, or manual-review qualification.

## Artifact manifest

```json
""" + json.dumps(manifest, indent=2) + """
```

## Fresh V11 execution transcript from packet build

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
    language = "json" if suffix == ".json" else "python" if suffix == ".py" else "yaml" if suffix in {".yml", ".yaml"} else "text"
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
