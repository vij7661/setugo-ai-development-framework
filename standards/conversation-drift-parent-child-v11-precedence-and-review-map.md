# V11 Composite Precedence, Provenance, and Review-Evidence Map

Status: **PROPOSED V11 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## 1. Candidate order

`V5 -> V6 -> V7 -> V8 -> V9 -> V10 -> V11`

V11 narrows V10 without deleting prior history.

## 2. V10 R3 findings narrowed by V11

| V10 R3 area | V11 disposition |
|---|---|
| packet self-consistency without repository provenance | `NARROWED_BY V11-C02/C14` — independent SourceRepositoryAttestation + transparency anti-rollback |
| hidden reviewer memory/retrieval/cache contamination | `NARROWED_BY V11-C03` — mandatory ReviewerCleanRoomAttestation; unavailable provenance => insufficiency |
| CAA/root-threshold overlap | `NARROWED_BY V11-C04` — CAA independence against every threshold-capable control combination |
| aggregate emergency cross-root evasion | `NARROWED_BY V11-C05` — global correlated emergency budget |
| genesis material-change/automated renewal | `NARROWED_BY V11-C06` — GMCA + human/manual re-acceptance |
| effector non-digest runtime drift | `NARROWED_BY V11-C07` — runtime configuration attestation |
| NCR post-evasion reuse | `NARROWED_BY V11-C08` — mandatory corpus expansion and stale revalidation |
| AI R3 counted as human manual evidence | `NARROWED_BY V11-C09` — evidence-class-aware ReviewThresholdRecord |
| EXP-K reference used as candidate authority | `NARROWED_BY V11-C10` — signed ArtifactRoleRegistry |
| consequence downgrade self-quorum | `NARROWED_BY V11-C11` — downgrade independence proof |
| trusted GEL/WAS start rollback | `NARROWED_BY V11-C12` — external history-start witness |
| stale predicate-auditor facts | `NARROWED_BY V11-C13` — recheck every PARENT_UNAFFECTED |
| packet manifest rollback | `NARROWED_BY V11-C14` — monotonic transparency log |

All other active V5–V10 rules remain active unless mechanically superseded.

## 3. New mechanism IDs

- `MECH-SOURCE-REPOSITORY-ATTESTATION`
- `MECH-REVIEWER-CLEAN-ROOM`
- `MECH-CAA-ROOT-INDEPENDENCE`
- `MECH-GLOBAL-EMERGENCY-BUDGET`
- `MECH-GENESIS-MATERIAL-CHANGE`
- `MECH-EFFECTOR-RUNTIME-CONFIG`
- `MECH-NCR-CORPUS-EXPANSION`
- `MECH-REVIEW-EVIDENCE-CLASS`
- `MECH-ARTIFACT-ROLE-SEPARATION`
- `MECH-CONSEQUENCE-DOWNGRADE-INDEPENDENCE`
- `MECH-HISTORY-START-WITNESS`
- `MECH-PREDICATE-LIVE-RECHECK`
- `MECH-REVIEW-PROVENANCE-ANTI-ROLLBACK`

## 4. New evidence profiles

- `EP-SOURCE-REPOSITORY-ATTESTATION`
- `EP-REVIEWER-CLEAN-ROOM`
- `EP-CAA-ROOT-INDEPENDENCE`
- `EP-GLOBAL-EMERGENCY-BUDGET`
- `EP-GENESIS-MATERIAL-CHANGE`
- `EP-EFFECTOR-RUNTIME-CONFIG`
- `EP-NCR-CORPUS-EXPANSION`
- `EP-REVIEW-EVIDENCE-CLASS`
- `EP-ARTIFACT-ROLE-SEPARATION`
- `EP-CONSEQUENCE-DOWNGRADE-INDEPENDENCE`
- `EP-HISTORY-START-WITNESS`
- `EP-PREDICATE-LIVE-RECHECK`
- `EP-REVIEW-PROVENANCE-ANTI-ROLLBACK`

## 5. Prior-case tightening

The following earlier cases inherit V11 evidence profiles in addition to their existing profiles:

- WDPC-07,19,53,68,78,106,115,125,178,179,180 -> `EP-REVIEWER-CLEAN-ROOM`
- WDPC-172 -> `EP-SOURCE-REPOSITORY-ATTESTATION + EP-REVIEW-PROVENANCE-ANTI-ROLLBACK`
- WDPC-174 -> `EP-CAA-ROOT-INDEPENDENCE`
- WDPC-126,139,150,161,162,175 -> `EP-GLOBAL-EMERGENCY-BUDGET`
- WDPC-96,113,114,137,148,155,176 -> `EP-GENESIS-MATERIAL-CHANGE`
- WDPC-116,138,152,167,171,177,181 -> `EP-EFFECTOR-RUNTIME-CONFIG`
- WDPC-136,149,153,173 -> `EP-NCR-CORPUS-EXPANSION`
- any review-threshold case -> `EP-REVIEW-EVIDENCE-CLASS`
- any packet containing reference-only material -> `EP-ARTIFACT-ROLE-SEPARATION`
- WDPC-156 and consequence-downgrade paths -> `EP-CONSEQUENCE-DOWNGRADE-INDEPENDENCE`
- WDPC-129,130,131 -> `EP-HISTORY-START-WITNESS`
- every PARENT_UNAFFECTED case -> `EP-PREDICATE-LIVE-RECHECK`

## 6. Clean V10 R3 evidence status

The V10 R3 review for candidate `f4b895e22f3a39c7673df2b412acad0ac8c44f48` declared:

- context: `CLEAN_PACKET_ONLY_CONTEXT`
- evidence class: `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`
- disposition: `CHANGES_REQUIRED`
- freeze: `DO_NOT_FREEZE`
- authority: `NONE_EVIDENCE_ONLY`

It is admissible as independent R3 engineering feedback for V10. It does not satisfy a human/manual review gate.

## 7. Mechanical completeness rule

Candidate build/freeze must reconcile:

1. active candidate artifacts and exact source attestations;
2. artifact roles;
3. normative clause and endpoint manifests;
4. active WDPC cases;
5. evidence-profile mappings;
6. review gate/evidence-class policies;
7. reviewer clean-room/independence records;
8. CAA/root-independence records;
9. emergency global-budget registry;
10. genesis material-change status;
11. active effector runtime attestations;
12. NCR corpus-expansion status;
13. history-start witness;
14. review-provenance transparency sequence.

Any set mismatch or stale required evidence blocks freeze.

## 8. Authority limitation

This map is design evidence only.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
