# R8 v15-r1 — Implementation Slice 1 Successor 1 Repair Preregistration

Status: **PREREGISTERED BEFORE SUCCESSOR REPAIR HARNESS OR MECHANISM CHANGE**

## 1. Lineage

Predecessor implementation candidate:
`e106bdd44973f3b16b5479c7689cbe07cb0f5421`

Predecessor independent review:
`governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-INDEPENDENT-REVIEW-001.txt`

Adjudication:
`governance-r8/R8-V15-R1-IMPLEMENTATION-SLICE1-REVIEW-001-ADJUDICATION.json`

Frozen executable-schema candidate remains:
`f93ca26975ecb64f0da13779889c75b36140cdfc`

The frozen executable-schema bytes and original I1-01..I1-16 acceptance semantics are unchanged.

## 2. Confirmed repair scope

Successor 1 may change only:

1. **Single-read digest/use closure** — each frozen artifact used by the loader must be read into bytes once per load attempt; SHA-256 verification and JSON parsing/use must consume those same bytes. No hash-then-reopen path is permitted.
2. **Explicit unpaired-surrogate regression** — add direct acceptance coverage for a lone surrogate in an authority-bearing string.
3. **Workflow trigger coverage** — implementation, acceptance/regression, workflow, preregistration, and marker changes must trigger the Slice 1 workflow on the successor branch.
4. **Lifecycle marker accuracy** — successor marker status must reflect the actual successor lifecycle at the frozen candidate.
5. **Load-time rejection-vector self-check** — as defense in depth, load must recompute every frozen GCP rejection vector and require the exact rejection code.
6. **Frozen-count/path defense in depth** — direct SPM document validation must require exactly 16 artifacts and 3058 entries and constrain artifact paths to the frozen schema directory.
7. **Review transport completeness** — the next independent-review packet must contain every workflow-invoked regression source file in exact bytes, in addition to the full frozen schema input directory.

No other implementation semantics may be broadened or weakened.

## 3. Identity clarification — non-relaxing

`candidate_sha=f93ca26975ecb64f0da13779889c75b36140cdfc` is the frozen
**schema-lineage/configuration identity** consumed by the post-freeze implementation.

The implementation checkout itself is necessarily a later Git commit because the loader did not exist
at the frozen-schema commit. Exact runtime schema-byte identity is therefore established by:

- exact frozen SPM SHA-256;
- exact source-map SHA-256;
- exact per-artifact SHA-256 from the frozen SPM;
- exact semantic-candidate binding;
- exact qualified-generator binding.

Successor 1 MUST NOT weaken any of those byte bindings. It is not required to assert that the
implementation repository HEAD equals the historical frozen-schema commit.

## 4. Frozen repair invariants

**S1R-I01 Same-byte verification/use** — an artifact's verified digest and parsed/used content derive
from the same immutable byte buffer from one read.

**S1R-I02 No verified-file reopen** — no required frozen artifact is reopened after its verified byte
buffer is obtained within a single load attempt.

**S1R-I03 Exact rejection-vector self-check** — every frozen GCP rejection vector rejects with its
exact expected code during loader self-check.

**S1R-I04 Explicit surrogate rejection** — a lone UTF-16 surrogate represented in JSON rejects as
`GCP_REJECT_UNPAIRED_SURROGATE`.

**S1R-I05 Exact SPM cardinalities** — direct SPM validation requires exactly 16 artifact records and
3058 provenance entries, in addition to declared-count equality.

**S1R-I06 Artifact path confinement** — every SPM artifact path is a normalized repository-relative
path directly under `schemas/governance-r8/v15-r1/`; absolute paths, traversal, alternate parent
directories, duplicate paths, or duplicate artifact IDs reject.

**S1R-I07 Trigger coverage** — changes to the loader, original Slice 1 harness, successor repair
harness, post-freeze regression, workflow, preregistration, or marker are covered by the successor
workflow trigger.

**S1R-I08 Original boundaries preserved** — I1-01..I1-16 remain unchanged and green; frozen schema
bytes remain unchanged; authority effect remains NONE/runtime_qualified=false.

## 5. Frozen repair acceptance cases

- **S1R-01** loader performs at most one byte read per frozen artifact per load attempt.
- **S1R-02** replacing a later text-read path cannot alter parsed content because no post-verification text reopen occurs.
- **S1R-03** lone-surrogate JSON input rejects with `GCP_REJECT_UNPAIRED_SURROGATE`.
- **S1R-04** all frozen GCP rejection vectors are self-checked during load with exact expected codes.
- **S1R-05** an SPM document with 3057 entries and declared `entry_count=3057` rejects.
- **S1R-06** an SPM artifact path moved outside the frozen schema directory rejects.
- **S1R-07** workflow trigger text covers all governed successor implementation/test/control paths.
- **S1R-08** original I1-01..I1-16 and applicable post-freeze regressions remain green with zero frozen-schema byte changes.

## 6. Construction sequence

1. Commit this preregistration first.
2. Update the workflow branch/path control without changing mechanism code.
3. Add/freeze the Successor 1 repair harness while predecessor mechanism remains unchanged.
4. Preserve the expected RED exposure for the confirmed repair gaps.
5. Apply only the narrow successor mechanism/control repair.
6. Require original I1-01..I1-16 + S1R-01..S1R-08 + applicable post-freeze regressions to pass.
7. Update the lifecycle marker to the final construction-green state and rerun.
8. Freeze one exact successor implementation candidate SHA.
9. Build a byte-complete independent-review packet including every invoked regression source.
10. Require a fresh blind independent implementation review before bounded Slice 1 adjudication.

## 7. Claim boundary

Successor construction may establish only a bounded repository-local implementation result.
It grants no runtime qualification, release, deployment, production, policy, or terminal authority.
