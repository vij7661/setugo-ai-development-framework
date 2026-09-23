# R8 Meta-Governance Redesign v14 — Normalized Successor Preregistration

Status: **PREREGISTERED_DESIGN_V14 — NOT_IMPLEMENTED — INTERNAL_NORMALIZATION_REQUIRED**
Authority effect: **NONE**

Effective design lineage:
- R8 v4 through R8 v13 remain immutable historical design layers.
- R8 v14 supersedes prior generations only where stronger or more specific.
- R8 v14 additionally defines NCG-1, a mandatory normalization/closure gate before fresh external review.

## 1. Objective

R8 v14 closes the R8 v13 findings and changes the review workflow from overlay-by-overlay review to normalized effective-design review.

Core rule:

> The next independent reviewer must evaluate one internally normalized effective specification whose evaluation order, state ownership, cross-mechanism dependencies, guard registry, review projection, and unresolved contradictions have already been checked by NCG-1.

## 2. AIMApplicability-2 — no permission filtering before Smax

### R8V14-I001 — candidate construction

For one `semantic_input_id`, build the AIM candidate set from descriptors that:
- match semantic_input_id and expected semantic class;
- are effective at semantic_state_sequence;
- match the decision scope on exact components;
- may contain ANY components even if current AIMScopePolicy no longer permits those components.

ANY permission is **not** used to discard candidates during initial candidate construction.

### R8V14-I002 — AIM_Smax first

For every candidate, derive specificity from exact scope components.

`AIM_Smax` is the maximum specificity across the full effective matching candidate set **before** lifecycle or ANY-permission filtering.

### R8V14-I003 — AIM Smax blocker order

At AIM_Smax, evaluate in this exact order:

1. invalid/missing/narrowed/revoked current AIMScopePolicy permission -> `AIM_SCOPE_PERMISSION_REEVALUATION_REQUIRED`;
2. REVOKED descriptor -> valid linked successor required, else `AIM_DESCRIPTOR_REVOKED`;
3. multiple ACTIVE eligible descriptors -> `AIM_DESCRIPTOR_CONFLICT`;
4. exactly one ACTIVE eligible descriptor -> resolve;
5. only SUPERSEDED/RETIRED -> successor traversal or `AIM_DESCRIPTOR_UNBOUND`.

Lower-specificity fallback is prohibited after any AIM_Smax blocker.

### R8V14-I004 — policy drift is resolver-time authority

Lifecycle marking of affected AIM descriptors is evidence/bookkeeping only.

The authority mechanism is current-policy validation at AIM_Smax.

Missing bookkeeping cannot create fallback authority.

## 3. RIR-2 — exact effective-sequence predicate

### R8V14-I005 — temporal eligibility

An RIR record is eligible at semantic_state_sequence only when:

`activation_sequence <= semantic_state_sequence`

and

`retirement_or_revocation_sequence == null || retirement_or_revocation_sequence > semantic_state_sequence`.

Lifecycle state must also be ACTIVE.

Both sequence predicate and lifecycle state are required.

### R8V14-I006 — exact execution tuple

The running resolver supplies attested:
- implementation digest;
- runtime manifest digest;
- workload policy/proof identity;
- conformance suite/result identity.

Exactly one temporally eligible ACTIVE RIR record must match the exact tuple and current ResolverPolicy digest.

Different active implementations under one policy are allowed only when the running attested tuple selects exactly one record.

## 4. SemanticResultEquivalencePolicy-1 — SREP-1

### R8V14-I007 — canonical semantic result

A resolved semantic result is normalized as:

`{semantic_input_id, semantic_class, authoritative_rule_digest, normalized_effect_digest, scope_effect_digest, lineage_terminal_id}`

The GCP-1 digest of this object is `semantic_result_digest`.

### R8V14-I008 — equivalence

Two semantic results are equivalent **iff** their canonical semantic_result_digest values are identical.

No implementation-local equivalence heuristic is permitted.

### R8V14-I009 — successor/peer comparison

CSRULE successor discharge and peer comparison use semantic_result_digest.

- one unique digest -> one semantic result;
- more than one digest -> `SEMANTIC_ENTRY_CONFLICT`;
- multiple paths producing the same digest are equivalent for result selection but their path evidence remains preserved.

SREP-1 is ResolverPolicy/CSM-bound.

## 5. SRTT-3 — deterministic total truth-table generation

### R8V14-I010 — total domain

SRTT-3 input domain is the Cartesian product of:
- source_entry_state: {REVOKED};
- old_scope_match: {NO_MATCH, EXACT_MATCH};
- destination_scope_match: {NO_MATCH, EXACT_MATCH, MAPPED_MATCH};
- old_scope_effect: {BLOCK_OLD_SCOPE, REPLACE_OLD_SCOPE_FOR_EXACT_MATCH, REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH};
- scope_relation: {SAME, NARROWER, BROADER, DISJOINT};
- any_permission_valid: {false,true};
- mapping_effective: {false,true};
- lineage_mapping_valid: {false,true};
- scope_expansion_authorized: {false,true};
- decision_inside_authorized_expansion_domain: {false,true}.

### R8V14-I011 — deterministic generator

The SRTT-3 generator enumerates tuples lexicographically in the exact enum order listed in I010 and applies the precedence/rules inherited from SRTT-2.

For every tuple it emits:
- input tuple;
- result enum;
- decisive rule ID.

The generated table is canonical GCP-1 JSON.

### R8V14-I012 — totality requirement

Every tuple in the Cartesian product must produce exactly one result.

Missing row -> `SRTT_INCOMPLETE`.

Multiple results for one tuple -> `SRTT_CONFLICT`.

The generator implementation digest and generated table digest are CSM/ResolverPolicy-bound before external review.

## 6. RCS-2 — conformance evidence freshness

### R8V14-I013 — invalidation conditions

Resolver conformance evidence is invalid immediately when any bound value changes:
- ResolverPolicy digest;
- resolver implementation digest;
- runtime manifest digest;
- workload-attestation policy digest;
- RCS suite/vector/harness digest;
- RIR record ID or lifecycle validity.

### R8V14-I014 — freshness profile

Each RIR record binds one conformance freshness profile:
- `VALID_UNTIL_BOUND_CHANGE`; or
- `MAX_SEQUENCE_AGE(n)`; or
- `MAX_WALL_AGE(seconds)` using qualified time.

A result is usable only if its profile remains satisfied at semantic_state_sequence.

### R8V14-I015 — requalification

After invalidation or expiry, fresh conformance execution under the exact current tuple is required.

Old evidence cannot be re-labeled as current.

## 7. LASAuthorityStateRoot v14

### R8V14-I016 — corrected explicit fields

`LASAuthorityStateRoot(i) = SHA-256(GCP-1({semantic_state_sequence_i, committed_log_prefix_digest_i, StreamHeadMap_root_i, idempotency_ledger_root_i, authority_state_machine_root_i, revocation_stream_head_i, nonce_ledger_head_i, effect_stream_head_i, csm5_registry_head_i, aim4_descriptor_head_i, any_scope_permission_head_i, aim_scope_policy_head_i, resolver_policy_head_i, resolver_implementation_registry_head_i, guard_registry_head_i, configuration_generation, prior_certificate_chain_digest_i}))`

The earlier typographical form `semantic_state_sequence_i:i` is superseded.

## 8. BSP-4 — exact deterministic blindness grammar

### R8V14-I017 — line classes

Each source line is classified into exactly one class:
- CURRENT_STATUS;
- PRIOR_STATUS;
- PRIOR_REVIEW_METADATA;
- SEMANTIC_CONTENT;
- SEMANTIC_TEST_LITERAL;
- LEGACY_GUARD_TABLE;
- BLANK/STRUCTURAL.

### R8V14-I018 — exact prior-status grammar

A line is PRIOR_STATUS only when:
1. it is inside a predecessor-version status block, or contains an explicit predecessor version token `R8 vN` where N < current_candidate_version; and
2. it contains one of the exact status tokens:
   - CHANGES_REQUIRED
   - BOUNDED_PASS
   - INSUFFICIENT_EVIDENCE
   - REVIEW_REQUIRED
   - INDEPENDENT_REVIEW_REQUIRED
   - NOT_IMPLEMENTED
3. it is not lexically inside a fenced code block or case/vector line tagged SEMANTIC_TEST_LITERAL.

### R8V14-I019 — review metadata grammar

A line/block is PRIOR_REVIEW_METADATA when it contains predecessor:
- review-evidence path;
- review-adjudications path;
- independent-review heading;
- adjudication heading;
- preserved review commit/hash field.

Candidate/source design commit/blob identifiers are not prior-review metadata.

### R8V14-I020 — current candidate exception

CURRENT_STATUS is the current candidate's own status block and is retained.

The current candidate version is a required generator input.

### R8V14-I021 — semantic test literal retention

Guard/case/vector lines are SEMANTIC_TEST_LITERAL when the parser is inside:
- a preregistered case section;
- a guard/case machine-readable record;
- a fenced literal block explicitly marked semantic-test-data.

Outcome/status words in these locations are retained.

### R8V14-I022 — residual scan

Residual scan re-runs the same parser after projection.

Any PRIOR_STATUS or PRIOR_REVIEW_METADATA record -> `REVIEW_PACKET_NOT_BLIND`.

Raw string matching alone is not authoritative.

## 9. ProjectionManifest-2 and GuardOmissionManifest-1

### R8V14-I023 — manifests are part of authoritative TXT

The authoritative review TXT embeds, before design content:
1. `ProjectionManifest-2`;
2. `GuardOmissionManifest-1`.

They are not merely sidecar files.

### R8V14-I024 — ProjectionManifest-2

Contains:
- BSP version;
- current candidate version/commit/blob;
- each source commit/blob;
- removed record count by class;
- digest of ordered removed records;
- residual classified record counts;
- projected semantic-section digest list;
- authoritative TXT digest excluding the manifest's self-digest field.

### R8V14-I025 — GuardOmissionManifest-1

For each omitted legacy guard table:
- source version/commit/blob;
- heading/line locator;
- omitted section digest;
- guard IDs present in omitted table;
- proof each ID exists in current GuardRegistry;
- proof unique case/invariant sections from the same source remain in projection.

If any unique case/invariant exists only inside the omitted table, omission is forbidden.

## 10. Barrier error taxonomy — frozen

### R8V14-I026 — reservation outcomes

For one barrier:
- same rotation_id + same config + same STC -> idempotent replay;
- same rotation_id + different config or STC -> `IDEMPOTENCY_CONFLICT`;
- different rotation_id while reserved/joint/activated -> `BARRIER_ALREADY_RESERVED`;
- two contradictory valid reservation certificates -> `STC_EQUIVOCATION`;
- ABORTED -> permanently closed.

## 11. NCG-1 — Normalization and Closure Gate

### R8V14-I027 — required artifacts

Before any fresh external review packet, NCG-1 must freeze:
- normalized effective specification;
- invariant/dependency matrix;
- evaluation-order matrix;
- state/registry ownership matrix;
- cross-mechanism adversarial corpus;
- guard/case registry;
- review-projection completeness report;
- unresolved-contradiction report.

### R8V14-I028 — normalized-spec rule

The normalized effective specification states the current effective rule once.

Historical superseded variants remain in immutable source files but are not repeated as co-effective rules.

Every normalized rule carries source-trace identifiers to its governing version/invariant.

### R8V14-I029 — zero-contradiction requirement

NCG-1 result is PASS only when:
- zero unresolved material rule contradictions;
- zero ambiguous evaluation-order edges;
- zero unowned authority state;
- zero unclassified cross-mechanism false-green cases;
- GuardRegistry contiguous/unique;
- review projection internally reproducible.

NCG-1 PASS grants no authority; it only permits freezing a fresh blind design-review packet.

## 12. Additional Guard Catalog v14

| Guard | Mechanism | Positive | Negatives with fault-proof class |
|---|---|---|---|
| G141 | AIMApplicability-2 Smax-before-permission | V14-001 | V14-002 FP5; V14-003 FP5 |
| G142 | RIR-2 effective sequence | V14-004 | V14-005 FP1; V14-006 FP1 |
| G143 | SREP-1 canonical equivalence | V14-007 | V14-008 FP5; V14-009 FP5 |
| G144 | SRTT-3 total deterministic table | V14-010 | V14-011 FP5; V14-012 FP5 |
| G145 | RCS-2 freshness | V14-013 | V14-014 FP4; V14-015 FP4 |
| G146 | BSP-4 deterministic grammar | V14-016 | V14-017 FP5; V14-018 FP5 |
| G147 | embedded projection/omission manifests | V14-019 | V14-020 FP5; V14-021 FP5 |
| G148 | NCG-1 normalized closure | V14-022 | V14-023 FP5; V14-024 FP5 |

## 13. R8 v14 preregistered cases

### AIM
- V14-001 high-specificity AIM descriptor with valid ANY + lower ACTIVE descriptor -> high-specificity resolves.
- V14-002 high-specificity AIM descriptor has narrowed/revoked ANY + lower ACTIVE descriptor -> AIM_SCOPE_PERMISSION_REEVALUATION_REQUIRED; no fallback.
- V14-003 high-specificity AIM descriptor has invalid ANY but lifecycle marker absent -> same blocker; no fallback.

### RIR
- V14-004 ACTIVE RIR record with activation <= sequence and no prior retirement/revocation -> eligible.
- V14-005 activation_sequence > semantic_state_sequence -> ineligible.
- V14-006 retirement/revocation_sequence <= semantic_state_sequence -> ineligible.

### Equivalence
- V14-007 two successor paths normalize to identical semantic_result_digest -> one semantic result.
- V14-008 different authoritative_rule_digest or normalized_effect_digest -> non-equivalent conflict.
- V14-009 implementation claims equivalence despite different canonical digest -> reject.

### SRTT
- V14-010 generator enumerates complete Cartesian domain exactly once -> table complete.
- V14-011 missing tuple -> SRTT_INCOMPLETE.
- V14-012 duplicate tuple with conflicting output -> SRTT_CONFLICT.

### Conformance freshness
- V14-013 evidence remains within bound freshness profile and all tuple digests unchanged -> valid.
- V14-014 runtime/policy/suite changes after evidence -> evidence invalid.
- V14-015 evidence exceeds configured age/sequence limit -> fresh execution required.

### Blindness
- V14-016 predecessor status removed, current status retained, semantic test literal retained -> BSP pass.
- V14-017 predecessor review metadata survives -> REVIEW_PACKET_NOT_BLIND.
- V14-018 semantic test literal is removed by classifier -> REVIEW_PACKET_INCOMPLETE.

### Manifests
- V14-019 embedded projection+omission manifests prove all removed content and current guard coverage -> packet complete.
- V14-020 omission manifest cannot prove guard IDs/case semantics preserved -> packet incomplete.
- V14-021 sidecar-only manifest missing from authoritative TXT -> packet incomplete.

### NCG
- V14-022 normalized spec/matrices/cross-cases show zero unresolved contradictions -> NCG-1 PASS.
- V14-023 one evaluation-order contradiction remains -> NCG-1 FAIL.
- V14-024 authority state has no unique owner/head -> NCG-1 FAIL.

## 14. Schema-freeze gate

Even a future v14 design BOUNDED_PASS only permits executable-schema-freeze preparation.

Before that external review is even requested, NCG-1 must PASS.

## 15. Current state

- R8 v1-v13 = CHANGES_REQUIRED
- R8 v14 = NOT_IMPLEMENTED / INTERNAL_NORMALIZATION_REQUIRED
- external v14 review packet = NOT YET AUTHORIZED TO FREEZE
- executable-schema freeze = BLOCKED
- PR #39/#40 = NON_AUTHORITATIVE
- authority effect = NONE
