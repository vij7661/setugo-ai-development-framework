from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

CANDIDATE = "63617dd1f01f0063b5534de128d5afce17f169be"
V4_REVIEW_COMMIT = "e34dfe387920e7f5fddf902cafceaa6fa13e0eb8"
OUT = Path("ECC_Derived_V10_External_Engineering_Rereview_Packet.md")


def git_bytes(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


def candidate_file(path: str) -> bytes:
    return git_bytes("show", f"{CANDIDATE}:{path}")


def review_file(path: str) -> bytes:
    return git_bytes("show", f"{V4_REVIEW_COMMIT}:{path}")


tree_paths = git_bytes("ls-tree", "-r", "--name-only", CANDIDATE).decode("utf-8").splitlines()
include: list[tuple[str, str, bytes]] = []

for path in (
    "reviews/ecc-derived-v4/rereview-raw.md",
    "reviews/ecc-derived-v4/rereview-fix-guidance-raw.md",
):
    include.append(("prior-review", path, review_file(path)))

for path in tree_paths:
    if path.startswith("experiments/ecc-derived/") or path.startswith("experiments/ecc_derived/"):
        include.append(("candidate", path, candidate_file(path)))

for path in tree_paths:
    if path == ".github/workflows/ecc-derived-parallel.yml":
        include.append(("candidate", path, candidate_file(path)))
    elif path.startswith(".github/workflows/apply-ecc-v") and path.endswith(".yml"):
        include.append(("candidate", path, candidate_file(path)))
    elif path.startswith(".github/scripts/apply_ecc_v") and path.endswith(".py"):
        include.append(("candidate", path, candidate_file(path)))

seen: set[tuple[str, str]] = set()
deduped: list[tuple[str, str, bytes]] = []
for item in include:
    key = (item[0], item[1])
    if key not in seen:
        seen.add(key)
        deduped.append(item)
include = deduped

manifest_rows = [
    (source_class, path, len(data), hashlib.sha256(data).hexdigest())
    for source_class, path, data in include
]

header = f"""# ECC-Derived Seven-Experiment Program — V10 Targeted External Engineering Re-review Packet

## Packet identity and authority limits

- Exact frozen V10 candidate: `{CANDIDATE}`
- Candidate ledger-head CI run: `34696128949`
- Candidate ledger-head CI conclusion: `SUCCESS`
- Prior V4 AI rereview preservation commit: `{V4_REVIEW_COMMIT}`
- Review context requested: `TARGETED_REMEDIATION_REREVIEW_WITH_PRIOR_REVIEW_INCLUDED`
- Evidence declaration required from reviewer: `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`
- Manual-review threshold contribution: `0`
- Authority effect: `NONE_EVIDENCE_ONLY`
- Production qualification: `NOT_CLAIMED`
- Live platform attestation: `NOT_CLAIMED`
- Independent production trust root: `NOT_CLAIMED`
- Durable cross-process signed provenance: `NOT_CLAIMED`
- Requirement adoption/promotion: `NONE`
- V18 integration: `NONE`

This packet is a targeted engineering re-review of the remediation chain triggered by the preserved V4 AI review. It is **not** a clean-room independent/manual review and must not be counted toward any qualifying manual-review threshold.

## Why this review is being requested now

The earlier V4 AI rereview identified structural false-green paths around public strict-mode bypass, permissive candidate eligibility, optional candidate-boundary use, runtime-policy identity, and same-fixture cross-checks. Those findings were not patched once and declared complete. They produced separately falsified hardening generations:

- **V5 — Closed candidate boundary:** pre-repair `144 tests / 33 failures`; repaired `144/144 PASS`.
- **V6 — Eligibility provenance:** clean pre-repair `155 / 11 failures`; repaired `155/155 PASS`.
- **V7 — Seal capability:** pre-repair `162 / 5 failures`; first repair exposed `162 / 16 failures`; corrected mechanism reached `162/162 PASS` and ledger-head PASS.
- **V8 — Verifier substitution:** pre-repair `170 / 5 failures`; repaired `170/170 PASS`, then ledger-head PASS.
- **V9 — Verifier primitive integrity:** pre-repair `176 / 5 failures`; repaired `176/176 PASS`, then ledger-head PASS.
- **V10 — Path primitive integrity:** pre-repair `183 / 6 failures`; repaired `183/183 PASS`; exact ledger head `{CANDIDATE}` also passed run `34696128949`.

All historical REDs, repair failures, superseded assertions, and bounded nonclaims are intentionally preserved in the embedded artifacts. The reviewer must not infer production qualification from a green reference suite.

## Current bounded interpretation

The current reference mechanism attempts to establish only that, under its declared ordinary-Python-module threat model:

1. public shared-core APIs cannot opt themselves into strict candidate authority;
2. candidate-positive results require the governed candidate boundary;
3. candidate eligibility is process-local, sealed to the exact payload, and cannot be recreated by ordinary dict/JSON/pickle reconstruction;
4. ordinary module access cannot invoke a generic positive-seal capability;
5. substitution of the public diagnostic verifier does not control candidate issuance/consumption;
6. ordinary substitution of public JSON/marshal aliases does not control verifier/seal authority;
7. ordinary substitution of public `Path.read_text`, `read_bytes`, `resolve`, `is_file`, or `is_symlink` aliases does not control candidate authority; and
8. actual mutation of the captured strict/reference dependency objects remains fail-closed in the tested cases.

The mechanism explicitly **does not claim** resistance to reflective closure-cell extraction/rewriting, mutation of captured callable objects themselves, interpreter/native-memory compromise, deeper OS/filesystem compromise beneath captured callables, repository/code-replacement authority, live platform trust roots, or durable cross-process authority.

EXP-ECC-1…5 therefore remain reference-mechanism candidates that still need real live integration evidence. EXP-ECC-6 and EXP-ECC-7 remain deferred pending their respective integration evidence.

## Reviewer task

Review the embedded exact artifacts adversarially. Do not grant authority because tests pass or because multiple generations converged.

For **each EXP-ECC-1…7**, provide:

- disposition: `READY_FOR_BOUNDED_IMPACT_ADJUDICATION`, `NARROWING_STILL_REQUIRED`, `DEFER_PENDING_LIVE_INTEGRATION_EVIDENCE`, `REJECT_REQUIREMENT_CANDIDATE`, or `INSUFFICIENT_EVIDENCE`;
- the strongest remaining false-green path, if any;
- whether the V4 finding relevant to that experiment is closed at the **reference-mechanism** layer;
- what live/integration evidence is still mandatory before production/platform qualification.

Also evaluate the experiment program itself:

1. Were tests materially frozen before each repair, with RED history preserved rather than rewritten?
2. Are the recorded test supersessions legitimate semantic supersessions, or do any hide regressions?
3. Do the positive controls prevent a block-all false green?
4. Is repository-bound reference evidence correctly labeled as simulation rather than independent production evidence?
5. Does any current mechanism still allow ordinary in-scope callers to manufacture candidate authority without traversing the governed boundary?
6. Are V6–V10 protections meaningful within their bounded threat models, or are any claims stronger than their tests support?
7. Are we at a sensible stopping boundary for reference-mechanism hardening, with deeper interpreter/OS primitives properly recorded as nonclaims, or is there a concrete **in-scope** false-green path that still requires another reference-generation experiment?
8. Confirm that EXP-ECC-6/7 are not accidentally promoted by generic green tests.

### Program-level disposition

Choose exactly one:

- `READY_FOR_BOUNDED_IMPACT_ADJUDICATION`
- `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`
- `DEFER_PENDING_LIVE_INTEGRATION_EVIDENCE`
- `INSUFFICIENT_EVIDENCE`

### Freeze recommendation

Choose exactly one:

- `SAFE_TO_FREEZE_REFERENCE_REQUIREMENT_CANDIDATES_FOR_IMPACT_ADJUDICATION`
- `DO_NOT_FREEZE`
- `DEFER_FREEZE_PENDING_LIVE_INTEGRATION_EVIDENCE`
- `INSUFFICIENT_EVIDENCE_TO_FREEZE`

The review must end with:

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

---

## Embedded artifact manifest

| Source | Path | Bytes | SHA-256 |
|---|---|---:|---|
"""

rows = "".join(
    f"| {source_class} | `{path}` | {size} | `{sha}` |\n"
    for source_class, path, size, sha in manifest_rows
)

body = bytearray((header + rows + "\n---\n\n## Exact embedded artifacts\n").encode("utf-8"))
for source_class, path, data in include:
    sha = hashlib.sha256(data).hexdigest()
    body.extend(
        f"\n\n### {source_class}: `{path}`\n\nBytes: `{len(data)}`  \nSHA-256: `{sha}`\n\n```text\n".encode("utf-8")
    )
    body.extend(data)
    if not data.endswith(b"\n"):
        body.extend(b"\n")
    body.extend(b"```\n")

pre_footer_sha = hashlib.sha256(body).hexdigest()
body.extend(
    (
        "\n---\n\n## Packet build note\n\n"
        f"The packet body above was assembled from exact Git objects. Pre-footer SHA-256: `{pre_footer_sha}`. "
        "The CI step reports the final packet SHA-256 and byte size separately.\n"
    ).encode("utf-8")
)

OUT.write_bytes(body)
final_sha = hashlib.sha256(body).hexdigest()
metadata = (
    f"candidate={CANDIDATE}\n"
    f"packet={OUT.name}\n"
    f"bytes={len(body)}\n"
    f"sha256={final_sha}\n"
    f"artifacts={len(include)}\n"
)
Path("packet-metadata.txt").write_text(metadata, encoding="utf-8")
print(metadata, end="")
