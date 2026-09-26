# R8 v15-r1 Consolidated Remediation Queue — Fresh Independent Review Packet

## Review boundary

This packet covers the repaired draft PRs #42, #43, #44, #46, and #50 in issue #52. It grants no authority and is ready only for a fresh independent review. Do not merge, activate a gate, execute SG-1, qualify runtime, release, deploy, enable production, restore six-slice cadence, or grant policy/constitutional/root/terminal authority.

Baseline: `7cd2787d85b189a4161f271ee131e42bd961140a`

## Final repaired branch identities

| PR | branch | final commit | repair |
|---:|---|---|---|
| #44 | `codex/r8-q03-runtime-toctou-hardening` | `424afbe9892aa8a9cc73fc530652662948d30dfc` | root-confined descriptor parent walk, no-follow, regular-object checks |
| #46 | `codex/r8-q05-evidence-integrity-lineage` | `a8add41bf17efe5c5129607c26f5546963a6eebe` | finalized #44 safe-read integration, path/digest/lineage checks, exact 121/120 accounting |
| #43 | `codex/r8-q02-stage2-semantic-gap-inventory` | `c42f18f07b84197836d42ac72c1d22d09f8ac774` | closure/surface-bound edge classification, explicit insufficient-evidence categories, self-hash verifier |
| #42 | `codex/r8-q01-review-parser-consolidation` | `615e762f97753aa52fb4d4166c9cf3ad73baa91d` | structured hidden-marker parser hardening and exact artifact preflight |
| #50 | `codex/r8-q09-manual-intervention-status-ledger` | `6f6b063432fe5987600df2d508af8443e53d5e67` | fixed state vocabulary, structured blockers, #44→#46 dependency, external report-head semantics |

Changed-file Git blobs at those heads:

- #44: `governance-runtime/r8_v15_r1_frozen_schema_runtime.py` → `9c9d174cfd45bd9a41dbb0d3afb4d01ac4cb0a2c`; safe-read tests → `6c5bebf2b97ee99196278a10fe0547a6575594c3`.
- #46: accounting → `1942e534d069d2c402b72e40f56c3f1c72d0572e`; integrity tool → `9540c84b9b04e11d116d537655e59c3d6663272e`; tests → `c7d194bd2442aec62ebb7ec1e54125ddfd40fe79`.
- #43: inventory → `3d61d2494cc59f3fee7a6dc61786437c3700da17`; scanner → `7af4a790ab7301d4e95434a093abe59e0aecb890`; tests → `2aafa0325efb388eb2a6941bb80866417dd17b18`.
- #42: parser → `6d844d4de38b6e7743abf1d2a58095a692994cf7`; preflight → `8a47cc308021a1aac543b93efc57bce9a9f471a4`; tests → `90b640df55ab6d080cfe185cd6e007a3375906d5`, `d0e43471d835a8f02552c5ce6adea8cd666d6893`.
- #50: queue manifest → `c1eab0f3432879b17101b6c5229400c5a91f796d`; selector → `c0f56c6b093c7451b78b33fe31b9ef18b9c226fc`; tests → `9b141a9d8bbca73230a6cc55a2dc24547ec4ae1b`; Issue #52 report → `ec72034c44c77dd72e4be6d64476360fdb5d9011`.

## Validation evidence

- #42 parser validation: PASS; shared parser adversarial tests: PASS (14 cases); exact-artifact preflight tests: PASS (2 cases).
- #43 scanner: PASS (32 bound edges); evidence-bound inventory tests: PASS; lexical fake next-gate names do not create a gate.
- #44 safe-read tests: PASS on supported descriptor platforms; Windows run reports 5 capability-dependent skips because `O_NOFOLLOW`/`O_DIRECTORY` are unavailable and the implementation fails closed.
- #46 evidence tests: PASS on supported descriptor platforms; Windows run reports 6 capability-dependent skips for the same fail-closed capability boundary.
- #50 queue tests: PASS (5 cases), including state vocabulary, dependency blocking, human-block skipping, report external-head verification, and authority-false checks.

## Exact accounting repair

Stage1 accounting is explicit: `changed_paths=121`, `reviewed_allowlisted_entries=120`, with the one additional bound path `governance-r8/R8-V15-R1-IG1-SUCCESSOR3-INTEGRATED-CANDIDATE-MANIFEST.json` at blob `a78add847f6d4ba8914a66ee00d89422fbaa47f2`. Candidate composition is exact Slice7 base + 120 reviewed entries + this manifest.

## Remaining manual boundaries

1. Independent review of all five repaired branches and their integrated #44/#46 contract.
2. Linux capability validation for descriptor-safe adversarial filesystem tests.
3. Any future runtime credential/infrastructure action remains separately governed.
4. No next Stage2 gate is selected or authorized by the #43 inventory.

## Reviewer instructions

Do not stop after the first finding. Enumerate **all Critical, High, Medium, and Low findings** across parser structure, exact-artifact binding, descriptor path confinement, evidence lineage, archive/input identities, 121-vs-120 accounting, semantic-gap classification, queue-state/dependency logic, report self-reference, platform capability behavior, and every authority boundary. Determine solutions for every finding. A bounded PASS here would be review evidence only; it would not grant any authority.

## Authority state

`EXP-M`/R8 governance remains non-authoritative. Runtime, release, deployment, production, policy, constitutional, root, terminal, and merge authority are false. Fallback-to-3 is ACTIVE. Six-slice cadence is NOT RESTORED. No activation artifact was created and no SG-1 semantic execution was performed by this remediation.
