Below are design-level remediations for every defect identified in the prior review. They are proposed changes only. They grant no authority, do not approve implementation, and do not close the schema-freeze gate by themselves.

---

## A. Critical defect solutions

### 1. Blind packet is not blind

**Defect:** Projected packet retains prior disposition/adjudication outcomes such as `R8 v1 — CHANGES_REQUIRED`, `R8 v1-v10 = CHANGES_REQUIRED`, predecessor status lists, and similar prior-review results.

**Solution:**

1. Expand BSP-1 redaction grammar beyond commit/hash metadata to include prior **disposition/adjudication outcome lines** for all versions earlier than the current reviewed subject.
2. Redact only prior-version outcome statuses, not the current v11 status.
3. Add deterministic patterns such as:
   - `^R8 v[0-9]+ .*—.*(CHANGES_REQUIRED|BOUNDED_PASS|INSUFFICIENT_EVIDENCE|NOT_IMPLEMENTED|INDEPENDENT_REVIEW_REQUIRED|REVIEW_REQUIRED)$`
   - `^R8 v[0-9]+-v[0-9]+ = CHANGES_REQUIRED$`
   - `^Predecessors?:$` followed by prior-version outcome lines
   - `^Until independent closure:$` followed by prior-version status lines
4. Keep:
   - current v11 status;
   - semantic lineage commits;
   - semantic rules, guards, cases, claim boundaries.
5. Regenerate the projection manifest with:
   - exact removed-line count;
   - SHA-256 of removed lines;
   - residual scan result;
   - explicit statement that prior-version disposition outcomes were removed.
6. Add/strengthen negative case:
   - `V11-025` must fail packet generation if any prior-version disposition outcome remains.
7. Add residual scan tokens for:
   - `CHANGES_REQUIRED`
   - `BOUNDED_PASS`
   - `INSUFFICIENT_EVIDENCE`
   - `REVIEW_REQUIRED`
   - `INDEPENDENT_REVIEW_REQUIRED`
   - `NOT_IMPLEMENTED` when attached to prior versions.

**Required rule change:** Modify R8V11-I034/I035 to cover prior disposition outcomes, not only commit/hash metadata.

---

### 2. CSRULE-3 `decision_sequence` is not bound to authoritative high-water state

**Defect:** `decision_sequence` can be supplied as a historical value before a revocation or permission narrowing, allowing resolution to select an entry that is no longer lawful.

**Solution:**

1. Add rule: `decision_sequence` is **not caller-supplied** for authority-bearing resolution.
2. Define:
   - `decision_sequence = current LAS-3 committed log index for the CSM-4 stream`, or
   - the current MTR/LAS-3 high-water sequence if CSM-4 is not directly a LAS-3 stream.
3. Any historical sequence may be used only for forensic replay with `authority effect = NONE`.
4. Include `decision_sequence`, CSM-4 head, AIM-2 head, and resolver policy digest in:
   - `AuthorityReadSet`;
   - `VerifiedStateSeal`;
   - `DecisionPresealContext` / DPS-2.
5. Add negative case:
   - revoked entry at sequence N;
   - caller supplies `decision_sequence < N`;
   - expected result: reject / `SEMANTIC_SCOPE_REVOKED`, not resolve.
6. Add positive case:
   - current sequence after revocation;
   - expected result: revoked-scope blocking applies.

**Required rule changes:**
- Modify R8V11-I009 to derive `decision_sequence` from current committed high-water.
- Add explicit `DecisionSequenceBinding` rule.
- Modify DPS-2 to include `decision_sequence`.

---

### 3. CSM-4 is not clearly included in LAS-3 AuthorityStateRoot or RBP-1 freeze scope

**Defect:** `LASAuthorityStateRoot(B)` omits CSM-4 head, AIM-2 head, and `any_scope_permissions` head. Semantic-registry changes could race rotation.

**Solution:**

1. Modify `LASAuthorityStateRoot(B)` to include:
   - `csm4_registry_head_B`
   - `aim2_head_B`
   - `any_scope_permissions_root_B`
   - `resolver_policy_digest_B`
2. Do the same for any GGS-3 root where semantic registry state is relevant.
3. Declare CSM-4, AIM-2, ANY permissions, and resolver policy as LAS-3-governed streams or as roots included in `authority_state_machine_root_B`.
4. RBP-1 `ROTATION_PREPARE` must freeze:
   - all authority commits;
   - CSM-4 updates;
   - AIM-2 updates;
   - ANY permission updates;
   - resolver policy updates.
5. Add negative case:
   - during `ROTATION_PREPARED`, attempt CSM-4 update;
   - expected result: `ROTATION_FROZEN`.
6. Add negative case:
   - STC snapshot does not match CSM-4 head at B;
   - expected result: reject rotation.

**Required rule changes:**
- Modify R8V11-I022.
- Modify R8V11-I025.
- Add explicit `SemanticRegistryFreeze` rule.

---

### 4. ANYScopePermission drift enforcement relies on Meta-Governor completeness

**Defect:** If Meta-Governor omits an affected entry, resolution may see it as ACTIVE and resolve it.

**Solution:**

1. Add resolver-level independent revalidation:
   - For every candidate at Smax that uses `ANY`, CSRULE-3 must independently resolve the active `ANYScopePermission` for its semantic class at `decision_sequence`.
   - Verify every `ANY` tuple position is permitted.
   - If not permitted, treat as `SCOPE_PERMISSION_REEVALUATION_REQUIRED`.
2. Do not rely solely on Meta-Governor-derived lifecycle events.
3. If permission is missing, narrowed, or revoked:
   - candidate is blocker-equivalent;
   - no lower-specificity fallback.
4. Add negative case:
   - permission narrowed;
   - no lifecycle event committed;
   - resolver still rejects with `SEMANTIC_SCOPE_PERMISSION_REEVALUATION_REQUIRED`.
5. Add positive case:
   - constitutionally revalidated successor under current permission;
   - resolver may use successor.

**Required rule changes:**
- Modify R8V11-I010 and R8V11-I019.
- Add explicit `ResolverLevelANYRevalidation` rule.

---

## B. High defect solutions

### 1. AIM-2 descriptor lifecycle and immutability not specified

**Defect:** AIM-2 `source_semantic_lineage_id` could be changed and redirect resolution.

**Solution:**

1. Declare AIM-2 descriptor CSM-bound.
2. Any change to:
   - `semantic_input_id`;
   - `source_semantic_lineage_id`;
   - `decision-scope construction rule ID`;
   - `expected semantic class`;
   - `resolver_policy_digest`
   requires constitutional amendment.
3. Ordinary policy cannot redirect source lineage.
4. Add negative case:
   - AIM-2 tries to substitute source lineage without amendment;
   - expected result: reject / `CONSTITUTIONAL_AMENDMENT_REQUIRED`.

**Required rule change:** Add `AIM2Immutability` rule.

---

### 2. `resolver_policy_digest` is opaque

**Defect:** The resolver policy artifact is not specified, so resolver behavior could drift.

**Solution:**

1. Define `ResolverPolicy` object containing:
   - algorithm version;
   - CSRULE-3 traversal rules;
   - specificity derivation;
   - mapping traversal order;
   - error precedence;
   - fallback prohibition rules.
2. Make `ResolverPolicy` CSM-bound.
3. Include `resolver_policy_digest` in:
   - CSM-4;
   - DPS-2;
   - `VerifiedStateSeal`;
   - `LASAuthorityStateRoot`.
4. Any change requires constitutional amendment.
5. Add negative case:
   - resolver algorithm differs from frozen policy digest;
   - expected result: `SEMANTIC_DEPENDENCY_UNBOUND` or equivalent.

**Required rule change:** Add `ResolverPolicyArtifact` rule.

---

### 3. State-root formulas omit semantic-registry heads

**Defect:** Same as critical 3, but broader.

**Solution:**

1. Update all relevant state-root formulas:
   - `LASAuthorityStateRoot`;
   - `GGSGenesisStateRoot`;
   - STC-2;
   - any rotation-barrier root.
2. Include:
   - CSM-4 registry head;
   - AIM-2 head;
   - ANY permission root;
   - resolver policy digest.
3. Add negative case:
   - omitted stream/head causes state-root mismatch;
   - expected result: `STATE_INTEGRITY_FAILURE` or rotation reject.

**Required rule change:** Modify R8V11-I022/I023 and STC-2 binding.

---

### 4. STC-2 uniqueness is per `rotation_id/barrier`, not per barrier

**Defect:** Multiple `rotation_id` values could exist for the same barrier.

**Solution:**

1. Add rule: for one barrier index `B`, at most one lawful `rotation_id` may exist.
2. `STC_COMMIT` must bind:
   - `barrier_id`;
   - `rotation_id`;
   - `stc_digest`.
3. Duplicate barrier with different rotation → `STC_EQUIVOCATION`.
4. Add negative case:
   - two different `rotation_id` values for same barrier;
   - expected result: one commits, other `STC_EQUIVOCATION`.
5. Add positive case:
   - retry same `rotation_id` + same `stc_digest` returns existing result.

**Required rule change:** Modify R8V11-I027.

---

### 5. PDF projection is corrupted

**Defect:** PDF contains repeated `1 1 1...` pages and missing tables.

**Solution:**

1. Regenerate PDF from the clean text projection.
2. Verify page count and content against text.
3. If PDF cannot be produced reliably:
   - mark PDF `NON_AUTHORITATIVE`;
   - use text-only packet for review.
4. Add manifest field:
   - `pdf_projection_status: PASS | FAIL | NOT_USED`.
5. If PDF is used, include SHA-256 of PDF and text, and confirm semantic equivalence.

**Required rule change:** Add projection manifest completeness check for PDF.

---

## C. Medium defect solutions

### 1. Consolidated guard catalog is spread across versions

**Solution:**

1. Add a single consolidated table to v11 or to the packet:
   - G001–G117;
   - mechanism;
   - positive case;
   - negative cases;
   - FP class.
2. Require packet generator to include it.
3. Add negative case:
   - missing inherited guard in consolidated table → `REVIEW_PACKET_INCOMPLETE`.

**Required rule change:** Add consolidated guard/case table requirement.

---

### 2. ANY revalidation authority class not named

**Solution:**

1. Define exact constitutional authority class:
   - e.g., `ANY_SCOPE_PERMISSION_AMENDMENT`.
2. Specify quorum and amendment path.
3. Project/org policy cannot revalidate.
4. Add positive/negative cases.

**Required rule change:** Add `ANYScopePermissionAuthorityClass` rule.

---

### 3. ScopeReplacementMapping allowed values/matching semantics not frozen

**Solution:**

1. Freeze exact allowed values for `replacement_effect_on_old_scope`:
   - `REPLACES_FOR_MATCHING_DECISIONS`
   - `DOES_NOT_REPLACE`
   - `REPLACES_FOR_EXACT_SCOPE_ONLY`
2. Define matching semantics:
   - new scope matches decision scope only if all exact components match and ANY positions are permitted.
3. Add positive/negative cases.

**Required rule change:** Add `ScopeReplacementSemantics` rule.

---

### 4. DPS-2 missing CSM-4/AIM-2/decision_sequence

**Solution:**

1. Add to DPS-2:
   - CSM-4 head;
   - AIM-2 head;
   - `decision_sequence`;
   - resolver policy digest.
2. Recompute `decision_preseal_digest`.
3. Add negative case:
   - any of these change after nonce issuance → old time proof reject.

**Required rule change:** Modify R8V11-I018 and DPS-2.

---

### 5. Resolver policy digest and CSRULE-3 algorithm need frozen artifact

**Solution:**

Same as High 2. Freeze `ResolverPolicy` and include in CSM-4.

**Required rule change:** Add `ResolverPolicyArtifact` rule.

---

## D. Minimal required changes before executable-schema freeze

1. Fix BSP-1 to remove prior-version disposition outcomes.
2. Bind `decision_sequence` to current LAS-3/MTR high-water.
3. Include CSM-4/AIM-2/ANY/resolver-policy heads in LAS-3 state roots and RBP-1 freeze scope.
4. Add resolver-level ANY permission revalidation.
5. Make AIM-2 descriptor immutable except by constitutional amendment.
6. Freeze `ResolverPolicy` artifact.
7. Strengthen STC-2 to one barrier → one lawful rotation.
8. Regenerate clean PDF or mark it non-authoritative.
9. Add consolidated G001–G117 guard/case table.
10. Name exact ANY revalidation authority class.
11. Freeze ScopeReplacementMapping values and matching semantics.
12. Add CSM-4/AIM-2/decision_sequence to DPS-2.

---

## E. Final bounded statement

These proposed solutions are design remediations only.  
This review grants no authority.  
R8 v11 remains **NOT_IMPLEMENTED**.  
Executable-schema freeze remains **BLOCKED** unless the design gate closes.  
PR #39 and PR #40 remain **NON_AUTHORITATIVE**.  
Unresolved material findings block implementation start.