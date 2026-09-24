# R8 v15-r1 Qualified-v2 Executable-Schema Review Adjudication — 2026-09-24

Status: **CHANGES_REQUIRED — REPAIR SUCCESSOR REQUIRED**
Authority effect: **NONE**

Reviewed candidate:
- qualified executable-schema candidate: `dab6c2e2692d7e2061b77af83b43888b84d705ae`
- frozen semantic candidate: `c721b38cf8b00294797300b526596ce723a47ff8`
- independent review disposition: `CHANGES_REQUIRED`
- independent review raw UTF-8 SHA-256: `1ed967d477b962cb6c9b257012fea8d3f194ee1bf6858360865100fa5fc2a007`
- independent review byte length: `10803`
- history rewritten: **NO**

This adjudication does not upgrade the reviewed candidate. The original qualified-v2 candidate remains rejected for SFV-45. Repairs occur only on a successor branch and predecessor review evidence remains preserved.

## Finding dispositions

### C-1 — SPM-1 candidate manifest absent/empty
Disposition: **PARTIALLY_SUSTAINED_AS_REVIEW_PACKET_DEFECT / CANDIDATE_ALLEGATION_NOT_SUSTAINED**

The exact candidate contains `schemas/governance-r8/v15-r1/schema-provenance-manifest-candidate.json` as Git blob `115ca22688a7ade2892b639498c16a1ebf8f2631`, 2,121,629 UTF-8 characters as retrieved by blob API, with:
- `status = FINAL_FREEZE_ELIGIBLE`;
- generator `R8V15R1-SPG-V2`;
- non-null runtime-manifest binding;
- empty `uncovered_semantic_elements`;
- empty `non_authoritative_only_sources`;
- empty `conflicting_entries`.

The blind packet builder used the ordinary GitHub contents/file read for this >1 MB artifact and received empty content while retaining the blob header. The reviewer therefore correctly found that the supplied packet could not establish SFV-35/36/43/44, but the statement that the candidate manifest itself was absent/empty is false.

Required repair:
- rebuild the successor review packet using the exact Git blob API for large artifacts;
- bind raw byte length/hash in the handoff;
- never interpret an empty oversized contents-API response as artifact content;
- prior SFV-45 review cannot transfer.

### C-2 — ScopeReplacementDecision / SRTT15-R00 contradiction
Disposition: **SUSTAINED — CRITICAL**

NORM-027 explicitly says non-REVOKED source state is outside the SRTT-4 table and returns `NOT_A_REPLACEMENT_BRANCH` before lookup. The reviewed schema required `source_entry_state = REVOKED` even for `SRTT15-R00`.

Repair:
- add a distinct non-REVOKED `ScopeReplacementOutsideTableInput`;
- condition `SRTT15-R00` + `NOT_A_REPLACEMENT_BRANCH` on that input;
- condition SRTT15-R01..R11 on the existing fixed-REVOKED table input;
- leave the 2304-row SRTT table domain unchanged.

Semantic change: **NO**. This restores frozen NORM-027.

### C-3 — SUCCEEDED_RECONCILED permits null executor identity
Disposition: **SUSTAINED — CRITICAL**

NORM-034 requires a qualified idempotent executor plus provider-specific reconciliation for external-effect success. The reviewed schema only forced reconciliation evidence non-null.

Repair:
- `SUCCEEDED_RECONCILED` requires non-null `executor_identity_digest`;
- existing non-null reconciliation evidence remains required;
- SFV-22 is strengthened to state the qualified-executor + reconciliation requirement explicitly.

Semantic change: **NO**. This restores NORM-034.

### H-1 — GCP-RVM2 source-case mismatches
Disposition: **SUSTAINED — HIGH**

Audit result:
- R01..R05 exact case mappings are consistent.
- R06 (+1), R07 (1e0), R08 (1.0): authoritative source rule `R8V4-I027` is exact, but no exact preregistered source case exists; `V4-025` is only the leading-zero case.
- R09..R12 mappings to V6-029/V6-030 are consistent with the frozen v7 rejection vectors.
- R13 reserved `sys:`: frozen v7 rejection rule is exact, but `V5-027` is unrelated and there is no exact preregistered case literal.
- R14 standard-field shadowing: `V5-026` is the exact inherited case; `V5-027` was wrong.

Repair:
- `source_case_id` remains mandatory as a field but may be null only where the authoritative rule has no exact preregistered case;
- R06/R07/R08/R13 -> null case with existing exact source rule retained;
- R14 -> `V5-026`;
- no new semantic test case is invented merely to satisfy metadata.

### H-2 — Digest / CanonicalId underconstraint
Disposition: **PARTIALLY_SUSTAINED — PROPOSED GLOBAL SHA-256 FIX REJECTED**

The false-green concern is valid if malformed digest/ID tokens can reach authority use without source/crypto-profile validation. However the blanket proposal to make every `Digest` SHA-256 is not authorized:
- executable-schema freeze preregistration says unknown source details remain opaque IDs/digests/references rather than invented semantics;
- inherited T0 semantics include a bound crypto profile and permitted algorithms;
- `CanonicalId` is not a digest and its lexical syntax is not globally frozen.

Repair:
- generic `Digest` remains an opaque non-empty token at structural-schema level;
- validator obligation now requires exact lexical/algorithm validation under the governing source rule or bound crypto profile before authority use;
- fields whose frozen source explicitly fixes SHA-256 or another concrete encoding must satisfy that exact encoding;
- `CanonicalId` validator obligation now requires stable canonical registry/source identity and rejects aliases/display names where authority requires stable IDs;
- SFV-31 and SFV-12 are strengthened accordingly.

No global hash algorithm is invented.

### M-1 — RuleRegistry precedence uniqueness/contiguity
Disposition: **SUSTAINED — MEDIUM**

Repair:
- RuleRegistry gets explicit deterministic validator invariants requiring exactly one R01..R11 and precedence exactly unique contiguous 1..11;
- SFV-03 now carries the same obligation.

### M-2 — total-table row IDs uniqueness/sequentiality
Disposition: **SUSTAINED — MEDIUM**

Repair:
- total-table schema gets an explicit validator invariant requiring row IDs exactly unique contiguous 1..2304;
- SFV-02 now carries the same obligation.

### M-3 — x-validator invariant coverage
Disposition: **PARTIALLY_SUSTAINED — MEDIUM/LOW**

Many cited examples were already covered by existing SFV rules (T0 successor, MTR, BTW, revocation, resolver conformance, reviewer independence, evidence strength, AIEP). The review nevertheless identified a real contract-clarity gap for several load-bearing runtime-schema invariants.

Repair strengthens the corresponding existing SFV obligations rather than inventing a new semantic layer:
- SFV-12: stable canonical ID/alias rule;
- SFV-15: AIM specificity, AIMScopePolicy uniqueness/non-broadening, constitutional successor linkage;
- SFV-18: SemanticEntry specificity + semantic_entry_key + ANY validation;
- SFV-22: qualified executor + reconciliation for success;
- SFV-31: source/crypto-profile digest validation;
- SFV-33: CSM frozen ordering, LAS-governed updates, current semantic sequence, LASAuthorityStateRoot digest binding;
- SFV-02/SFV-03: SRTT row/rule identity closure.

## Successor boundary

The reviewed candidate `dab6c2e...` remains `CHANGES_REQUIRED`.

The repair successor must:
1. contain only the narrow schema/validator/provenance-source-map repairs above;
2. delete or invalidate the predecessor-generated SPM artifact before regeneration;
3. recompute SPM under the qualified generator only after the repaired candidate bytes are fixed;
4. re-establish SFV-35, SFV-36, and SFV-44 for the exact successor;
5. receive a fresh blind independent SFV-45 review whose packet includes the complete large SPM blob;
6. grant no implementation/runtime/release/deployment/production authority merely from any schema-review PASS.

