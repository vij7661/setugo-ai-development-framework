# Independent Blind Design Review — R8 v14 Normalized Candidate

**Reviewer basis:** normalized current v14 design only, as presented in the packet. No prior findings, dispositions, or internal NCG PASS outputs considered.

**Authority effect of this review:** NONE.

---

## A. Overall Disposition

`CHANGES_REQUIRED`

The normalized v14 design is materially closer to closure than a stacked-overlay review would suggest, but it is **not** sufficiently closed at design level to proceed to executable-schema freeze. Several concrete false-green/self-grant paths and completeness gaps remain in load-bearing mechanisms, most notably SRTT-3, the guard-omission proof, and the BSP-4 projection grammar.

The design should not be frozen until the findings below are resolved or explicitly dispositioned as non-material with mechanism-level proof.

---

## B. Critical Findings

### B-1. SRTT-3 is not demonstrably total over its actual domain; `source_entry_state` is unenumerated and fixed to `REVOKED`

The SRTT-3 artifact declares:

```json
"enum_order": {
  "old_scope_match": ["NO_MATCH", "EXACT_MATCH"],
  "destination_scope_match": ["NO_MATCH", "EXACT_MATCH", "MAPPED_MATCH"],
  "old_scope_effect": ["BLOCK_OLD_SCOPE", "REPLACE_OLD_SCOPE_FOR_EXACT_MATCH", "REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH"],
  "scope_relation": ["SAME", "NARROWER", "BROADER", "DISJOINT"],
  "any_permission_valid": [false, true],
  "mapping_effective": [false, true],
  "lineage_mapping_valid": [false, true],
  "scope_expansion_authorized": [false, true],
  "decision_inside_authorized_expansion_domain": [false, true]
}
```

`row_count` is `2304`, which is exactly `2 × 3 × 3 × 4 × 2 × 2 × 2 × 2 × 2`. Every row also contains a `source_entry_state` field, and in every one of the 2304 rows it is `"REVOKED"`.

This means one of the following is true:

1. `source_entry_state` is a dimension of the table but was omitted from `enum_order`, in which case the table is incomplete for any other source state (e.g., `ACTIVE`, `SUSPENDED`, `RETIRED`). The claim “SRTT-3 is total” would be false.
2. `source_entry_state` is intentionally fixed to `REVOKED`, in which case the artifact must declare that the table is scoped only to revoked source entries. The normalized spec (NORM-027) and the review prompt both refer to “the total SRTT-3 machine-readable decision table” without this scoping qualifier.

Either way, the artifact as frozen does not carry a machine-readable domain declaration that proves totality over the intended input space. This is a material completeness gap for a mechanism that is explicitly required to be total and deterministic.

**Impact:** An implementation could legitimately reject the table as non-total, or could fail to apply the correct replacement semantics for non-REVOKED source states, depending on how the ambiguity is resolved. Because SRTT-3 is load-bearing for scope replacement after revocation, this blocks design closure.

**Minimal required resolution:** Either extend the table to include all legitimate `source_entry_state` values and add the dimension to `enum_order`, or add an explicit `domain_fixed: {"source_entry_state": "REVOKED"}` declaration and update NORM-027 to state that SRTT-3 is total only for revoked source entries, with a separate total table (or explicit rule) for other source states.

---

### B-2. SRTT-3 defines an over-permissive combination that can bypass the exact-replacement BROADER prohibition

The normalized spec (NORM-027) states:

> exact replacement requires SAME exact destination;
> mapped SAME/NARROWER replacement may be allowed;
> BROADER requires SEMANTIC_SCOPE_EXPANSION_AMENDMENT plus decision inside the AuthorizedExpansionDomain.

The SRTT-3 table, however, contains rows where `old_scope_effect` is `REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH` while `destination_scope_match` is `EXACT_MATCH`. These are semantically incoherent: a mapped-match replacement effect should correspond to a mapped destination match, not an exact destination match. The table nevertheless assigns results to these combinations.

Concrete example:

- Row 1757: `old_scope_match=EXACT_MATCH`, `destination_scope_match=EXACT_MATCH`, `old_scope_effect=REPLACE_OLD_SCOPE_FOR_EXACT_MATCH`, `scope_relation=BROADER`, `any_permission_valid=true`, `mapping_effective=true`, `lineage_mapping_valid=true`, `scope_expansion_authorized=false`, `decision_inside_authorized_expansion_domain=false` → `SEMANTIC_SCOPE_REPLACEMENT_INVALID`.
- Row 1760: same as 1757 but `scope_expansion_authorized=true`, `decision_inside_authorized_expansion_domain=true` → `SEMANTIC_SCOPE_REPLACEMENT_INVALID`.
- Row 1888: `old_scope_match=EXACT_MATCH`, `destination_scope_match=EXACT_MATCH`, `old_scope_effect=REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH`, `scope_relation=BROADER`, `any_permission_valid=true`, `mapping_effective=true`, `lineage_mapping_valid=true`, `scope_expansion_authorized=true`, `decision_inside_authorized_expansion_domain=true` → `REPLACEMENT_ELIGIBLE`.

So, for a broader destination scope with a valid expansion amendment and an in-domain decision, the exact-replacement effect is always invalid, but the mapped-replacement effect is eligible **even though the destination is an exact match**. If `old_scope_effect` and `destination_scope_match` are independently supplied inputs (or if the resolver does not cross-check them), this is a false-green path: an actor could claim a mapped replacement effect against an exact destination to gain broader-scope eligibility that the exact-replacement rules forbid.

The normalized spec does not state that `old_scope_effect` must be consistent with `destination_scope_match`, nor does it declare these incoherent combinations unreachable. The SRTT-3 table therefore defines authority-relevant outcomes for states that should either be rejected as malformed or collapsed into the exact-effect branch.

**Impact:** This is a concrete self-grant path for broader-scope unblocking after revocation, which is exactly the class of dangerous interaction the design is required to prevent.

**Minimal required resolution:** Either (a) remove all rows where `old_scope_effect` is inconsistent with `destination_scope_match`, or (b) add an explicit precondition/coherence rule that forces the effect to be derived from the destination match type, and make the table total only over coherent tuples. In either case, add a cross-mechanism case that exercises the incoherent tuple and proves it rejects.

---

### B-3. Guard-omission manifest does not actually prove preservation of all referenced case semantics

The `R8-V14-GUARD-OMISSION-MANIFEST-1.json` claims `invalid_omission_count: 0` and asserts for each omitted legacy guard table that `all_referenced_case_ids_in_current_case_registry: true`.

However, the v4 omitted table’s `referenced_case_ids` list skips `V4-025` through `V4-029`. The list goes from `V4-024` directly to `V4-030`. But the GuardRegistry record for `G008` explicitly references:

- positive: `V4-023`
- negatives: `V4-024`, `V4-025`, `V4-026`, `V4-027`, `V4-028`, `V4-029`, `V4-030`

So the omission manifest’s enumeration of referenced case IDs is incomplete for the v4 table. It does not list `V4-025` through `V4-029`, even though those cases are referenced by a guard in the omitted table.

This means the manifest does not fully prove that all unique case semantics from the omitted legacy table are preserved in the current CaseRegistry. The CaseRegistry itself does contain those cases, but the omission proof — which is supposed to be the machine-checkable bridge between omitted legacy tables and the normalized review surface — is incomplete.

**Impact:** NORM-042 requires that omission of legacy guard tables must prove all guard IDs remain in GuardRegistry and unique case/invariant semantics remain in the normalized spec. The current manifest fails that proof for `V4-025`–`V4-029`. This is a direct violation of a stated closure condition.

**Minimal required resolution:** Regenerate the omission manifest so that every referenced case ID from every omitted legacy guard table is enumerated and checked against the CaseRegistry. If `V4-025`–`V4-029` are intentionally not considered “unique semantics” (e.g., they are duplicated elsewhere), that must be stated explicitly with a mapping, not omitted silently.

---

## C. High Findings

### C-1. BSP-4 grammar does not deterministically identify the current candidate’s Status block

The BSP-4 grammar defines parser states including `PREDECESSOR_STATUS_BLOCK` and `CURRENT_STATUS`, and its `classification_order` says:

> classify explicit current-candidate Status block as CURRENT_STATUS

But the grammar provides no pattern or rule that identifies which `Status:` block is the current candidate’s. The only version-related pattern is `version_token: "\\bR8\\s+v(?<version>\\d+)\\b"`. The `current_candidate_exception` states `retain_version: 14` and `retain_current_status: true`, but the parser has no defined procedure for associating a `Status:` block with version 14, nor for distinguishing the current candidate’s status from a predecessor’s status when both appear in the same document.

Without such a rule, the blind projection is not demonstrably deterministic. A parser could:

- remove the current candidate’s status as if it were a predecessor status, producing `REVIEW_PACKET_INCOMPLETE`; or
- retain a predecessor status as if it were the current status, producing `REVIEW_PACKET_NOT_BLIND`.

Either outcome violates NORM-041 and the BSP-4 closure requirement.

**Impact:** The blind-review surface is the authoritative input to independent review. If its projection grammar is ambiguous, the review packet cannot be trusted to preserve semantic content or blindness. This blocks the design gate.

**Minimal required resolution:** Add an explicit, deterministic rule to BSP-4 that binds the current candidate status to the current version token (e.g., a `Status:` block within the same document section as the current version, or an explicit `CURRENT_CANDIDATE_STATUS` marker). Add a positive and negative case proving the rule works when predecessor and current status both appear.

---

### C-2. Multiple revoked branches at Smax are not fully formalized in relation to SRTT-3

NORM-024 (revoked dominance) states:

> any applicable REVOKED entry at Smax suspends ordinary ACTIVE selection;
> each revoked branch requires one unique valid linked successor/replacement discharge path;
> zero path → SEMANTIC_SCOPE_REVOKED;
> multiple non-equivalent paths → SEMANTIC_SUCCESSOR_CONFLICT;
> only after all revoked blockers are discharged are resulting successors compared with genuine ACTIVE peers.

SRTT-3 is a per-entry total table: each row describes the replacement result for **one** revoked source entry. The normalized spec does not define how SRTT-3 is composed when **multiple** revoked entries are simultaneously at Smax and each has its own replacement path.

The cross-mechanism corpus covers some single-branch cases (X14-014 to X14-018), but does not cover:

- two revoked Smax entries, both with valid replacement paths, producing two eligible replacement candidates;
- one revoked Smax entry with a valid replacement path and another revoked Smax entry with zero discharge path;
- two revoked Smax entries whose replacements normalize to the same SREP digest vs different digests.

Without a composition rule, the design is ambiguous about whether SRTT-3 results are combined via CSRULE-5, whether they must be applied sequentially, or whether multiple revoked branches at Smax are themselves a conflict condition. This is a dangerous interaction because revocation is exactly where fallback and replacement semantics can silently widen authority.

**Impact:** A false-green path could exist if an implementation applies SRTT-3 per entry and then incorrectly treats the set of replacements as independently eligible, without a defined conflict/discharge composition.

**Minimal required resolution:** Add a normalized rule that defines the composition of SRTT-3 results across multiple revoked Smax entries. At minimum, specify:

- the order of discharge;
- whether replacements are combined before or after SREP comparison;
- the exact conflict condition when multiple non-equivalent replacements exist;
- how partial discharge (one branch discharged, one not) is handled.

Add cross-mechanism cases covering multi-revoked-branch Smax interactions.

---

### C-3. SRTT-3 generator rules are not included, so table completeness and semantic correctness are trusted rather than verifiable

The SRTT-3 artifact declares:

```json
"generator_rule": "R8V14-I010..I012"
```

But the rules `R8V14-I010`, `R8V14-I011`, and `R8V14-I012` are not provided in the packet. The table’s decisive_rule_id values reference `R8V14-I011.2` through `R8V14-I011.7`, `R8V14-I012`, and `R8V14-I013`, but the actual rule text is absent.

This means an independent reviewer cannot verify:

- that the table was generated from a total and consistent rule set;
- that the decisive rule IDs correspond to actual normalized rules;
- that the table’s result distribution follows from the rules rather than from a generator that happened to produce a self-consistent artifact.

The review prompt explicitly says: “Do not treat normalization artifacts, registries, matrices, or generated tables as proof merely because they exist.” Without the generator rules, the SRTT-3 table is an opaque artifact whose completeness and semantic correctness cannot be independently falsified.

**Impact:** This is a traceability and verifiability gap for a load-bearing mechanism. It does not by itself prove the table is wrong, but it prevents the design gate from closing because the table’s correctness cannot be checked against normalized rules.

**Minimal required resolution:** Include the normalized text of `R8V14-I010` through `R8V14-I013` in the review surface, or provide a machine-readable rule set that the table claims to implement, and add a traceability check that every decisive_rule_id maps to a declared rule.

---

## D. Medium Findings

### D-1. Cross-mechanism corpus is strong but has identifiable coverage gaps

The 42-case corpus (X14-001 to X14-042) covers the mandatory attack areas reasonably well. However, the following dangerous interactions are not explicitly covered:

- **AIM ANY × RIR conformance:** AIM_Smax ANY permission is valid, but the resolver implementation tuple is temporally ineligible or conformance-freshness fails. The corpus covers AIM ANY and RIR/RCS separately, but not the combined blocker precedence. Which blocker wins if both are present?
- **GuardRegistry × NCG closure:** A guard is present and contiguous, but its referenced case semantics are not provable from the normalized spec. The corpus covers guard omission (X14-030 to X14-032) but not the interaction between guard completeness and NCG-1 closure.
- **Rotation barrier × external effect:** A rotation barrier is active while an EffectIntent is in `DISPATCHING` or `ACKNOWLEDGED_UNVERIFIED`. The corpus covers rotation × semantic registry (X14-027 to X14-029) and effect × revocation (X14-037 to X14-039), but not rotation × external effect.
- **Multiple revoked branches at Smax:** As noted in C-2.
- **Time proof × semantic state sequence:** The corpus covers semantic head changes after time proof (X14-025), but not a case where `semantic_state_sequence` itself is rolled back or replaced by a lower value while the semantic heads remain superficially consistent.

These are not necessarily design flaws, but they are gaps in the adversarial corpus that should be filled before claiming closure under NORM-043.

### D-2. SRTT-3 row distribution is not evidence of correctness, and some decisive-rule assignments are opaque

The result distribution (`1808 REVOKED`, `288 PERMISSION_REEVALUATION`, `144 MAPPING_NOT_APPLICABLE`, `22 ELIGIBLE`, `42 INVALID`) is arithmetically consistent with the table size. However, the distribution alone does not prove semantic correctness. Several decisive-rule assignments rely on rules not present in the packet (see C-3). For example:

- Rows 29–32 use `R8V14-I011.5` to produce `MAPPING_NOT_APPLICABLE` when `old_scope_match=NO_MATCH`, `destination_scope_match=NO_MATCH`, `old_scope_effect=BLOCK_OLD_SCOPE`, and all predicates are valid. The semantic justification is plausible but not stated in the normalized spec.
- Rows 1181–1184 use `R8V14-I011.6` to produce `SEMANTIC_SCOPE_REVOKED` when `old_scope_match=EXACT_MATCH`, `destination_scope_match=NO_MATCH`, `old_scope_effect=BLOCK_OLD_SCOPE`, and all predicates are valid. Again plausible, but the rule text is absent.

Without the rule text, a reviewer cannot distinguish a semantically correct assignment from a generator artifact.

### D-3. BSP-4 grammar’s `residual_rule` does not fully address raw-token search

The `residual_rule` states:

```json
"fail_if": ["PRIOR_STATUS", "PRIOR_REVIEW_METADATA"],
"raw_token_search_is_authoritative": false
```

This is appropriate: raw token search is not authoritative. However, the grammar does not specify how to handle a case where a status token appears in a semantic context that is neither a case section nor a status block. For example, a normalized spec paragraph might discuss the meaning of `CHANGES_REQUIRED` as a disposition token. The grammar’s `classification_order` says status-token lines inside semantic-test contexts become `SEMANTIC_TEST_LITERAL`, but it does not define “semantic-test context” precisely. This could lead to either over-removal (semantic content lost) or under-removal (prior status retained). This is a medium-severity determinism gap.

### D-4. The structured closure graph’s topological order is plausible but has no explicit proof of acyclicity for all authority-relevant edges

The graph reports `dependency_acyclic: true` and provides a topological order. The listed edges appear acyclic. However, the graph does not include edges for some authority-relevant dependencies that appear in the matrices, such as:

- `Revocation` → `RIR2` (temporal eligibility of resolver records may depend on revocation state);
- `CSM5` → `RCS2` (conformance suite identity is CSM-bound);
- `GuardRegistry` → `CSRULE_SRTT_SREP` (guard identity may influence mechanism-proof evaluation).

If these edges are missing, the graph may understate the dependency structure. This is a medium-severity completeness issue for the dependency/ownership assessment, though not a proven cycle.

---

## E. Normalized-Spec Completeness / No-Regression Assessment

The normalized spec (NORM-001 through NORM-043) covers the inherited trust model, T0/MTR/BTW, identity/revocation, GGS/LAS, rotation, AIEP/AIG, CSM/AIM, resolver authorization, semantic resolution, scope replacement, review materiality, seals, external effects, evidence, tenant/migration, recovery/trust loss, guard authority, blind review, and NCG closure.

The traceability manifest shows `rule_count: 43`, `missing_rules: []`, `untraced_rules: []`, and each rule has a trace to inherited sources.

**Strengths:**

- The trust boundary and authority default (NORM-001, NORM-002) are explicitly bounded and preserve the fail-closed posture.
- T0/MTR/BTW and GGS/LAS rules carry forward the inherited monotonic, rollback-resistant semantics.
- AIM applicability (NORM-018) correctly moves AIM_Smax computation before ANY permission and lifecycle filtering.
- Resolver authorization (NORM-019 to NORM-021) correctly separates policy, implementation tuple, and conformance freshness, and explicitly denies conformance-as-authority.
- Semantic resolution (NORM-022 to NORM-025) correctly moves Smax before lifecycle, enforces revoked dominance, and defines canonical semantic-result equivalence.
- Scope replacement (NORM-026, NORM-027) correctly requires explicit lineage mapping and ties broader expansion to a constitutional amendment and authorized domain.
- State sealing and commit (NORM-030 to NORM-033) preserve the TOCTOU defenses.
- External effects (NORM-034) preserve intent ≠ success and reconciliation independence.
- Recovery and trust loss (NORM-038, NORM-039) preserve permanent blocking and no weaker emergency root.

**Gaps:**

- SRTT-3 domain ambiguity and incoherent-tuple over-permissiveness (B-1, B-2).
- Guard-omission proof incompleteness (B-3).
- BSP-4 current-candidate status identification ambiguity (C-1).
- Multiple-revoked-branch composition not normalized (C-2).
- Generator rules for SRTT-3 not included (C-3).

Overall, the normalized spec does **not** silently weaken inherited trust assumptions. The gaps are in the machine-readable normalization artifacts and in the completeness of the adversarial closure evidence, not in the high-level trust model.

---

## F. Dependency / Evaluation-Order / Ownership Assessment

**Evaluation order:** The 21-stage authority-bearing evaluation order is internally consistent with the normalized rules. Stages 1–9 handle current authority state, runtime, semantic snapshot, AIM resolution, RIR/RCS, and resolver qualification. Stages 10–15 handle semantic candidate construction, Smax, ANY validation, revoked dominance, successor/lineage/scope traversal, and SREP comparison. Stages 16–21 handle read-set capture, DPS, time proof, seal, commit, and external effect.

The critical ordering properties are present:

- AIM_Smax before AIM ANY permission and lifecycle (stage 5 before 6–7).
- Semantic Smax before semantic ANY validation and lifecycle (stage 11 before 12–13).
- Revoked dominance before successor comparison (stage 13 before 14–15).
- Read-set capture and DPS before time proof and seal (stage 16–17 before 18–19).
- Seal before COMMIT_WITH_SEAL (stage 19 before 20).
- COMMIT_WITH_SEAL before external effect (stage 20 before 21).

**Ownership:** The ownership matrix assigns exactly one authority owner per mutable authority state. The structured closure graph reports `duplicate_ownership_classes: []`. No two independent owners are defined for the same state.

**Dependency:** The dependency graph is reported acyclic. The listed edges are acyclic. However, as noted in D-4, some authority-relevant edges may be missing from the graph, so the acyclicity proof is not complete over the full dependency set.

**Assessment:** The evaluation order and ownership assignments are fundamentally sound. The missing dependencies in the closure graph and the multi-revoked-branch composition gap (C-2) are the main weaknesses. Neither is a proven cycle, but both are closure-relevant.

---

## G. AIM / Resolver / Semantic-Resolution Assessment

**AIM (NORM-017, NORM-018):** The AIM candidate/Smax order is correct: candidates are selected without filtering by ANY permission, specificity is derived, AIM_Smax is computed over the full effective set, AIMScopePolicy is evaluated at AIM_Smax, and invalid/narrowed/revoked permission produces `AIM_SCOPE_PERMISSION_REEVALUATION_REQUIRED` with no lower fallback. This matches the mandatory attack area and the cross-mechanism cases X14-001 to X14-004.

**Resolver (NORM-019 to NORM-021):** ResolverPolicy is a CSM-bound algorithm contract. RIR requires exactly one temporally eligible ACTIVE tuple. Temporal eligibility uses `activation_sequence <= semantic_state_sequence` and `retirement_or_revocation_sequence == null || > semantic_state_sequence`. Conformance freshness is bound to the exact policy/implementation/runtime/suite/registry tuple. Conformance alone is not authorization. This is a strong design.

**Semantic resolution (NORM-022 to NORM-025):** Semantic Smax is computed before lifecycle filtering. Semantic ANY is checked at Smax from the same CSM snapshot. Revoked dominance suspends ordinary ACTIVE selection and requires unique discharge paths. SREP-1 defines canonical equivalence over `{semantic_input_id, semantic_class, terminal_semantic_entry_id, terminal_rule_digest, terminal_lineage_id, effective_scope_tuple_digest}`. This is a rigorous design.

**Weaknesses:**

- The interaction between SRTT-3 (per-entry replacement) and CSRULE-5 (multi-branch revoked dominance) is not fully normalized (C-2).
- The SRTT-3 table’s incoherent effect/destination combinations create a potential false-green path (B-2).
- The SRTT-3 generator rules are absent (C-3).

**Assessment:** The AIM and resolver designs are strong. The semantic-resolution design is strong in its single-branch form. The main gap is the composition of multiple revoked branches and the coherence of the scope-replacement table.

---

## H. SRTT-3 Assessment

**Completeness:** The table contains 2304 rows, matching the product of the 9 declared dimensions. However, `source_entry_state` is present in every row as `REVOKED` and is not declared in `enum_order`. The table is therefore not demonstrably total over any source state other than `REVOKED`, and it does not declare that limitation. This is a completeness gap for a mechanism claimed to be total.

**Determinism:** Each row has exactly one result and one decisive_rule_id. The table does not contain duplicate input tuples with conflicting outputs, assuming the 9 declared dimensions plus `source_entry_state=REVOKED` are the full input space.

**Semantic correctness:** The table’s results are broadly consistent with the normalized rules, but the following issues remain:

1. The table allows `old_scope_effect=REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH` with `destination_scope_match=EXACT_MATCH`, which is semantically incoherent and creates a broader-scope eligibility path that the exact-effect branch forbids (B-2).
2. The decisive_rule_id assignments reference rules `R8V14-I011.2` through `R8V14-I011.7`, `R8V14-I012`, and `R8V14-I013`, but the rule text is not included, so the assignments cannot be independently verified (C-3).
3. The distribution is not evidence of correctness by itself, and the table’s semantic justification for several branches (e.g., `MAPPING_NOT_APPLICABLE` when both old and destination scopes are `NO_MATCH` and all predicates are valid) is not stated in the normalized spec.

**Assessment:** SRTT-3 is the weakest load-bearing artifact in the review surface. It is arithmetically complete over its declared dimensions, but its domain is ambiguous, it contains at least one dangerous over-permissive combination, and its generator rules are not verifiable from the packet.

---

## I. State-Seal / Rotation / Effect Assessment

**State sealing (NORM-030 to NORM-033):** AuthorityReadSet captures every mutable authority input with source/head/value digest. DecisionPresealContext binds candidate/action/scope, governance snapshot, read set, semantic_state_sequence, CSM/AIM/ANY/ResolverPolicy heads, RIR record/head, resolver identity, revocation/runtime/workload state, and effect class. Time proof uses a single-use nonce bound to the DPS. VerifiedStateSeal binds the full read set and state. COMMIT_WITH_SEAL atomically rechecks current heads. This preserves the TOCTOU defenses from v5–v8.

**Rotation/barrier (NORM-011, NORM-012):** One barrier serves at most one rotation. ROTATION_PREPARE commits barrier index B and freezes covered authority writes. STC binds the exact committed state at B. ENTER_JOINT and ACTIVATE bind the same STC and transition certificate. Mismatch makes a joining replica non-voting and blocks rotation. ABORT permanently closes B. Retry requires a new barrier. This matches the v10–v12 STC/RBP rules and the v13/v14 barrier taxonomy.

**External effects (NORM-034):** COMMIT_WITH_SEAL may commit an EffectIntent only. External success requires a qualified idempotent executor plus provider-specific reconciliation. Ambiguous results remain UNCERTAIN. This preserves the v7–v9 effect-state rules.

**Weaknesses:**

- The cross-mechanism corpus does not cover rotation × external effect interaction (D-1).
- The multi-revoked-branch composition gap (C-2) can affect seal-time semantic state if multiple revoked branches are resolved after read-set capture but before seal.

**Assessment:** The state-seal, rotation, and external-effect designs are strong and preserve inherited defenses. The main gap is in adversarial coverage, not in the core rules.

---

## J. GuardRegistry / CaseRegistry / Mechanism-Proof Assessment

**GuardRegistry:** 148 records, contiguous G001–G148, exactly one ACTIVE record per ID. Every positive case ID is listed. Every negative case has an FP class. The registry correctly treats legacy guard tables as non-authoritative.

**CaseRegistry:** 442 cases, all guard-referenced cases present, no duplicate conflicts, no missing guard-referenced cases. The registry covers v4–v14.

**Mechanism-proof:** The guard registry includes mechanism-proof adjudication (G025) and per-guard fault proof/anti-constant-reject (G066). V4-082 explicitly addresses earlier-guard masking, and V4-084 addresses constant-reject false green.

**Weakness:** The guard-omission manifest’s referenced-case-ID enumeration is incomplete for the v4 table, omitting `V4-025`–`V4-029` even though G008 references them (B-3). This means the omission proof does not fully establish that unique case semantics are preserved.

**Assessment:** The registries themselves are complete and non-conflicting. The omission manifest fails to prove what it claims. This is a closure-blocking finding because NORM-042 requires that omission of legacy guard tables prove all guard IDs and unique case/invariant semantics remain in the normalized spec.

---

## K. Cross-Mechanism Adversarial Coverage Assessment

The 42-case corpus covers the mandatory areas:

- AIM × ANY × specificity (X14-001 to X14-004)
- AIM × successor × source lineage (X14-005 to X14-007)
- RIR × sequence × conformance (X14-008 to X14-013)
- Semantic Smax × ANY × revoked × peer ACTIVE (X14-014 to X14-018)
- Scope replacement × ANY × expansion (X14-019 to X14-024)
- Semantic state × seal × rotation (X14-025 to X14-029)
- Guard registry × projection (X14-030 to X14-032)
- BSP blindness × semantic literals (X14-033 to X14-036)
- Effect/revocation/semantic state (X14-037 to X14-039)
- Recovery/liveness (X14-040 to X14-042)

**Strengths:** The corpus includes concrete false-green paths (e.g., X14-001, X14-014, X14-019, X14-030) and fail-closed liveness cases (X14-040 to X14-042). It correctly treats expected results as test vectors, not as proof.

**Gaps:** As noted in D-1, the corpus does not cover:

- AIM ANY × RIR conformance combined blocker precedence;
- GuardRegistry completeness × NCG closure;
- Rotation barrier × external effect;
- Multiple revoked branches at Smax;
- `semantic_state_sequence` rollback with superficially consistent heads.

**Assessment:** The corpus is a strong start but does not yet meet the NORM-043 requirement that the cross-mechanism adversarial corpus have no unresolved false-green path. The gaps above are not proven false-green paths, but they are unclosed attack surfaces.

---

## L. BSP-4 / Blindness / Packet-Completeness Assessment

**Strengths:**

- TXT is authoritative; PDF is non-authoritative convenience only.
- The BSP-4 grammar defines deterministic line classes and an explicit classification order.
- `remove_classes` includes `PRIOR_STATUS`, `PRIOR_REVIEW_METADATA`, and `LEGACY_GUARD_TABLE`.
- `retain_classes` includes `CURRENT_STATUS`, `SEMANTIC_CONTENT`, `SEMANTIC_TEST_LITERAL`, and `BLANK_STRUCTURAL`.
- `raw_token_search_is_authoritative: false` correctly prevents naive token stripping from being authoritative.
- `guard_table_omission_rule` requires the omission manifest and prohibits removing unique case/invariant semantics.

**Weaknesses:**

- No deterministic rule for identifying the current candidate’s Status block (C-1).
- The guard-omission manifest does not fully prove preservation of all referenced case semantics (B-3).
- The definition of “semantic-test context” in the classification order is not precise, which could lead to over-removal or under-removal of status tokens in semantic prose (D-3).

**Assessment:** The BSP-4 design is conceptually sound but not yet deterministic or complete enough to guarantee that the authoritative review surface preserves semantic content and removes prior outcomes. This blocks the blind-review closure requirement.

---

## M. Over-Governance / Deadlock Assessment

**Strengths:**

- Fail-closed states are preserved: MTR outage → `MTR_UNAVAILABLE`; trust path unavailable → blocked; no emergency weaker root.
- Recovery requires predeclared triggers, exact context, single-use nonce, lawful quorum, and current trust state.
- Permanent trust loss blocks authority indefinitely if no lawful recovery quorum exists.
- `TRUST_DOMAIN_UNRECOVERABLE` can only be authoritatively recorded by a still-lawful recovery quorum.
- No liveness workaround weakens authority: X14-040 and X14-041 explicitly reject emergency semantic fallback and cached-head fallback.

**Weakness:** The design does not define a bounded liveness guarantee for legitimate operations when lawful trust is available but a non-authority dependency (e.g., time source, resolver conformance harness) is temporarily unavailable. This is not a safety violation, but it is an over-governance/liveness gap that could cause permanent blocking even when authority is intact. NORM-004, NORM-021, and NORM-032 require fail-closed behavior, which is correct for safety, but the design does not specify a recovery path for transient non-authority failures. This may be intentional, but it should be explicit.

**Assessment:** The design correctly prioritizes safety over liveness. The lack of a bounded liveness path for transient non-authority failures is a policy decision, not a safety bug, but it should be dispositioned before schema freeze because it affects operational viability.

---

## N. Minimal Required Changes Before Executable-Schema Freeze

1. **SRTT-3 domain declaration (B-1):** Either extend the table to include all legitimate `source_entry_state` values and add the dimension to `enum_order`, or explicitly declare `source_entry_state=REVOKED` as a fixed domain and update NORM-027 accordingly. Add a machine-readable domain declaration.

2. **SRTT-3 coherence rule (B-2):** Remove or explicitly reject all rows where `old_scope_effect` is inconsistent with `destination_scope_match`. Add a normalized rule that forces the effect to be derived from the destination match type. Add a cross-mechanism case proving the incoherent tuple rejects.

3. **SRTT-3 generator rules (C-3):** Include the normalized text of `R8V14-I010` through `R8V14-I013` in the review surface, or provide a machine-readable rule set that the table claims to implement. Add a traceability check that every decisive_rule_id maps to a declared rule.

4. **Guard-omission manifest completeness (B-3):** Regenerate the omission manifest so that every referenced case ID from every omitted legacy guard table is enumerated and checked. Specifically, include `V4-025`–`V4-029` for the v4 table and verify they are preserved in the CaseRegistry.

5. **BSP-4 current-candidate status rule (C-1):** Add an explicit deterministic rule that binds the current candidate’s Status block to the current version token or an explicit marker. Add positive and negative cases proving correct classification when predecessor and current status both appear.

6. **Multi-revoked-branch composition (C-2):** Add a normalized rule defining how SRTT-3 results compose across multiple revoked Smax entries. Specify discharge order, replacement combination, conflict conditions, and partial-discharge handling. Add cross-mechanism cases covering multi-revoked-branch Smax interactions.

7. **Cross-mechanism corpus gaps (D-1):** Add cases for AIM ANY × RIR conformance combined blockers, GuardRegistry completeness × NCG closure, rotation barrier × external effect, and `semantic_state_sequence` rollback with superficially consistent heads.

8. **Closure graph dependency completeness (D-4):** Add any missing authority-relevant edges (e.g., Revocation → RIR2, CSM5 → RCS2, GuardRegistry → CSRULE_SRTT_SREP) and re-verify acyclicity.

9. **Over-governance/liveness disposition (M):** Explicitly disposition whether transient non-authority failures (e.g., time source, conformance harness) may have a bounded liveness workaround that does not weaken authority. If not, state that permanent blocking is the intended behavior.

These changes are minimal in the sense that they are targeted at the specific gaps identified. They do not require re-architecting the normalized design; they require closing the machine-readable normalization and adversarial-coverage gaps.

---

## O. Final Bounded Statement

This review grants no authority.

- v14 remains **NOT_IMPLEMENTED**.
- Executable-schema freeze remains **BLOCKED** unless the design gate closes.
- PR #39/#40 remain **NON_AUTHORITATIVE**.
- Unresolved material findings block implementation start.

The normalized v14 design preserves the inherited bounded trust assumptions and fail-closed authority model. The AIM, resolver, semantic-resolution, state-seal, rotation, and external-effect designs are fundamentally sound. However, the SRTT-3 total table is not demonstrably total over its actual domain, contains at least one over-permissive incoherent combination, and lacks included generator rules. The guard-omission manifest does not fully prove preservation of all referenced case semantics. The BSP-4 grammar does not deterministically identify the current candidate’s Status block. Multi-revoked-branch composition is not fully normalized. These are material design-closure gaps.

Until the minimal required changes in section N are made or explicitly dispositioned as non-material with mechanism-level proof, the design gate remains open and executable-schema freeze must not proceed.