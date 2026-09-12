from __future__ import annotations

from pathlib import Path
import glob
import hashlib
import json
import subprocess

ROOT = Path.cwd()
CANDIDATE = "a87cccd803ce307c601b32e1ad47bfd45790d38c"
OUT = ROOT / "ECC_Derived_V12_Clean_External_Review_Packet.md"
TRANSCRIPT = Path("/tmp/ecc_v12_test_transcript.txt")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def neutral_evidence_file(path: Path) -> bool:
    name = path.name.upper()
    if any(token in name for token in ("REVIEW", "REREVIEW", "ADJUDIC", "DISPOSITION")):
        return False
    return name.startswith(("V", "CONSTRUCTION-", "REFERENCE-", "FULL-COVERAGE-", "CHILD-TERMINAL-"))


candidate_tree = subprocess.check_output(
    ["git", "rev-parse", f"{CANDIDATE}^{{tree}}"], text=True
).strip()
packaging_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()

# Clean projection: mechanism, contracts, frozen tests/runners, deterministic
# repair/diagnostic machinery, and neutral machine evidence only. Prior reviewer
# prose and outcome-bearing ledgers are deliberately excluded.
files: set[Path] = set()
for pattern in (
    "experiments/ecc-derived/PROGRAM-CHARTER.md",
    "experiments/ecc-derived/EXP-ECC-*.md",
    "experiments/ecc_derived/ecc_*.py",
    "experiments/ecc_derived/ecc_*.json",
    "experiments/ecc_derived/test_*.py",
    "experiments/ecc_derived/run_v*.py",
    ".github/scripts/apply_ecc_v*.py",
    ".github/workflows/ecc-derived-parallel.yml",
    ".github/workflows/apply-ecc-v*.yml",
    ".github/scripts/diagnose_ecc_v12_runtime.py",
    ".github/workflows/diagnose-ecc-v12-runtime.yml",
    ".github/scripts/correct_ecc_v12_reference_runtime_hash.py",
    ".github/workflows/correct-ecc-v12-reference-runtime-hash.yml",
):
    for value in glob.glob(pattern):
        path = Path(value)
        if path.is_file():
            files.add(path)

for value in glob.glob("experiments/ecc-derived/evidence/*.json"):
    path = Path(value)
    if path.is_file() and neutral_evidence_file(path):
        files.add(path)

files_sorted = sorted(files, key=lambda p: p.as_posix())
if not files_sorted:
    raise SystemExit("No review-safe packet source files found")

transcript = TRANSCRIPT.read_text(encoding="utf-8", errors="replace")
if "Ran 198 tests" not in transcript or "\nOK\n" not in transcript:
    raise SystemExit("Frozen V12 suite transcript is not 198/198 green")

manifest = []
for path in files_sorted:
    raw = path.read_bytes()
    manifest.append({"path": path.as_posix(), "bytes": len(raw), "sha256": sha256_bytes(raw)})

# Reviewer-safe machine lineage. Only objective execution fields are projected;
# no prior reviewer identity, disposition, recommendation, or prose is copied.
lineage = []
for path in files_sorted:
    if path.parent.as_posix() != "experiments/ecc-derived/evidence" or path.suffix != ".json":
        continue
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        continue
    result = data.get("result") if isinstance(data.get("result"), dict) else {}
    entry = {
        "path": path.as_posix(),
        "record_type": data.get("record_type"),
        "record_id": data.get("record_id"),
        "exact_candidate_sha": data.get("exact_candidate_sha"),
        "workflow_run_id": data.get("workflow_run_id"),
        "workflow_job_id": data.get("workflow_job_id"),
        "tests_run": result.get("tests_run"),
        "failures": result.get("failures"),
        "errors": result.get("errors"),
        "conclusion": result.get("conclusion"),
        "authority_effect": data.get("authority_effect"),
    }
    lineage.append({k: v for k, v in entry.items() if v is not None})

header = f"""# ECC-Derived Seven-Experiment Program — V12 Clean External Engineering Re-Review Packet

## Packet identity

- Packet class: `CLEAN_EXTERNAL_ENGINEERING_REREVIEW_PACKET`
- Review context requirement: `CLEAN_PACKET_ONLY_CONTEXT`
- Frozen reviewed candidate SHA: `{CANDIDATE}`
- Frozen reviewed candidate tree: `{candidate_tree}`
- Packaging branch head: `{packaging_head}`
- Review projection: `PRIOR_REVIEW_PROSE_AND_OUTCOME_BEARING_LEDGERS_EXCLUDED`
- Packaging branch allowed diff from candidate: only the packet workflow and packet-builder script
- Evidence authority: `NONE_EVIDENCE_ONLY`
- Manual-review threshold contribution from any AI-generated review: `0`
- Production qualification claimed: `NO`
- Live platform attestation claimed: `NO`
- Independent production trust-root claimed: `NO`
- Durable signed cross-process provenance claimed: `NO`

## Reviewer isolation instruction

Review **only this packet**. Do not use prior conversations, cached review outputs, model memory, repository browsing, or earlier reviewer dispositions. Prior reviewer prose and outcome-bearing ledgers are intentionally excluded. The packet contains the exact mechanism, manifest, experiment contracts, frozen tests, deterministic repair/diagnostic machinery, neutral machine RED/GREEN evidence, and a fresh execution transcript.

If you are an AI reviewer, begin your response with exactly:

`REVIEW_CONTEXT = CLEAN_PACKET_ONLY_CONTEXT`

`EVIDENCE_DECLARATION = AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`

Any AI review is engineering evidence only and contributes zero to a qualifying manual-review threshold.

## Current bounded posture presented without prior reviewer outcomes

The seven ECC-derived requirements remain evidence-only research candidates. The reference mechanism has undergone repeated falsification and repair generations through V12. V12 specifically tests transitive primitive-attribute mutation in the EXP-ECC-5 strict config-digest path and direct semantic binding of raw config fields. The exact V12 ledger-head suite is green, but this packet asks you to determine whether the available evidence is sufficient for **bounded impact adjudication of requirement candidates**.

V12's active semantics include one explicit historical supersession: an older V9 positive assumption about `boundary.json.dumps` substitution is excluded because `boundary.json` and `strict_core.json` are the same module object, so that substitution also mutates the exact strict EXP-ECC-5 digest primitive. The V9 source is preserved unchanged; the active runner prints the supersession reason and stronger V12 negative/positive replacements.

Explicit nonclaims remain:

- mutation of already captured callable objects themselves;
- concurrent/TOCTOU mutation between successful verification and subsequent strict/reference execution;
- reflective extraction or mutation of closure-held captured objects;
- deeper interpreter/native-memory compromise;
- repository/code-replacement authority;
- live platform attestation;
- independent production trust-root separation; and
- durable signed cross-process provenance.

EXP-ECC-6 and EXP-ECC-7 have no live integration evidence in this packet. Nothing here grants release, merge, production, freeze, qualification, terminal, policy, or manual-review authority.

## Review questions

For each EXP-ECC-1 through EXP-ECC-7, assign exactly one disposition:

- `ADOPT_REQUIREMENT_CANDIDATE`
- `NARROW_REQUIREMENT_CANDIDATE`
- `REJECT_REQUIREMENT_CANDIDATE`
- `DEFER_PENDING_INTEGRATION_EVIDENCE`
- `INSUFFICIENT_EVIDENCE`

Then answer:

1. Does the neutral RED→repair→GREEN machine evidence support the claimed bounded reference-mechanism conclusions without laundering failures?
2. Are historical test supersessions explicit, technically justified, and non-history-rewriting?
3. Does V12 close ordinary mutation of `strict_core.hashlib.sha256` and `strict_core.json.dumps` for the stated EXP-ECC-5 reference threat model?
4. Does the EXP-ECC-5 candidate cross-check now bind raw `argv` and `permission_profile` adequately in addition to digest fields?
5. Is there any concrete false-green path still inside the stated ordinary-module V12 threat model?
6. Are the explicit remaining nonclaims acceptable bounded exclusions before impact adjudication, or does any represent a design defect that must be falsified first?
7. Is `REFERENCE_REPO_BOUND_SIMULATION_ONLY` still appropriately constrained and clearly non-live/non-independent?
8. Should EXP-ECC-6 and EXP-ECC-7 remain deferred pending integration evidence?
9. Is the seven-experiment family ready for governed **bounded impact adjudication as requirement candidates**, while remaining non-production and non-authoritative?

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

Do **not** grant production readiness, release authority, merge authority, policy authority, terminal authority, or manual-review qualification.

## Neutral machine-evidence lineage projection

```json
{json.dumps(lineage, indent=2)}
```

## Artifact manifest

```json
{json.dumps(manifest, indent=2)}
```

## Fresh V12 execution transcript from packet build

The packaging workflow first verifies that its only diff from the exact frozen candidate consists of the two packaging-only files, then executes the frozen V12 runner.

```text
{transcript}
```

## Review-safe frozen artifact contents
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
print(f"NEUTRAL_EVIDENCE_RECORD_COUNT={len(lineage)}")
