# R8 v14 — NCG-1 Cross-Mechanism Adversarial Corpus

Status: **INTERNAL_NORMALIZATION_ARTIFACT — NON_AUTHORITATIVE — NCG-1 INPUT**
Authority effect: **NONE**

Purpose:
Test interactions between individually-correct mechanisms before another independent review.

Each case must produce one deterministic expected disposition. A case is unresolved if two normalized rules imply different results.

## A. AIM × ANY × specificity

### X14-001 — high AIM ANY permission revoked, lower ACTIVE exact/general descriptor exists
Setup:
- high-specificity AIM descriptor matches scope;
- its ANY permission is no longer valid;
- lower-specificity ACTIVE descriptor also matches.
Expected:
- compute AIM_Smax before permission filtering;
- return `AIM_SCOPE_PERMISSION_REEVALUATION_REQUIRED`;
- lower descriptor must not resolve.

### X14-002 — high AIM ANY permission valid, lower descriptor exists
Expected:
- high descriptor remains eligible;
- lower descriptor ignored by specificity.

### X14-003 — high AIM permission invalid and high descriptor REVOKED
Expected:
- permission blocker wins before lifecycle;
- `AIM_SCOPE_PERMISSION_REEVALUATION_REQUIRED`.

### X14-004 — two tied AIM_Smax descriptors, one invalid ANY and one ACTIVE exact
Expected:
- invalid-permission blocker prevents ordinary active selection;
- no lower/tied bypass.

## B. AIM × successor × source lineage

### X14-005 — revoked AIM descriptor + lower active descriptor
Expected:
- no fallback;
- linked successor required.

### X14-006 — AIM successor changes source lineage without constitutional authorization
Expected:
- successor invalid;
- source-lineage redirect rejected.

### X14-007 — two ACTIVE AIM descriptors tie at Smax
Expected:
- `AIM_DESCRIPTOR_CONFLICT`.

## C. RIR × sequence × conformance

### X14-008 — RIR ACTIVE label, activation sequence in future
Expected:
- ineligible despite ACTIVE label.

### X14-009 — RIR ACTIVE label, revocation sequence <= semantic sequence
Expected:
- ineligible.

### X14-010 — conformance PASS but runtime digest differs from RIR
Expected:
- resolver unqualified.

### X14-011 — conformance PASS but evidence exceeds MAX_SEQUENCE_AGE
Expected:
- fresh execution required.

### X14-012 — two ACTIVE RIR records for same policy but different implementations; runtime attests one exact tuple
Expected:
- exactly matching tuple resolves one record; no ambiguity.

### X14-013 — two non-equivalent ACTIVE RIR records match same exact tuple
Expected:
- `RESOLVER_IMPLEMENTATION_CONFLICT`.

## D. Semantic Smax × ANY × revoked × peer ACTIVE

### X14-014 — revoked Smax rule + unrelated active peer
Expected:
- revoked branch dominates;
- no ordinary active selection until discharge.

### X14-015 — revoked branch has valid successor and unrelated peer normalizes to same SREP digest
Expected:
- one semantic result may continue; path evidence preserved.

### X14-016 — revoked branch valid successor + peer has different SREP digest
Expected:
- `SEMANTIC_ENTRY_CONFLICT`.

### X14-017 — two valid successor paths yield same SREP digest
Expected:
- equivalent one semantic result; preserve both paths.

### X14-018 — two valid successor paths yield different SREP digests
Expected:
- `SEMANTIC_SUCCESSOR_CONFLICT`.

## E. Scope replacement × ANY × expansion

### X14-019 — exact replacement to narrower scope
Expected:
- invalid under EXACT effect.

### X14-020 — mapped replacement to narrower scope
Expected:
- eligible if other predicates valid.

### X14-021 — broader mapped replacement without expansion amendment
Expected:
- invalid.

### X14-022 — broader mapped replacement with amendment but decision outside AuthorizedExpansionDomain
Expected:
- blocked/invalid.

### X14-023 — broader mapped replacement with valid amendment and in-domain decision
Expected:
- eligible.

### X14-024 — mapping otherwise valid but current semantic ANY permission revoked
Expected:
- permission blocker; no replacement.

## F. Semantic state × seal × rotation

### X14-025 — semantic head changes after time proof, before final seal
Expected:
- old time proof invalid; recompute.

### X14-026 — semantic head changes after seal, before COMMIT_WITH_SEAL
Expected:
- `STATE_CHANGED`; no effect intent.

### X14-027 — rotation barrier active and semantic registry update attempted
Expected:
- `ROTATION_FROZEN`.

### X14-028 — STC omits/mismatches resolver implementation registry head
Expected:
- rotation reject.

### X14-029 — barrier aborted, same barrier reused with new rotation ID
Expected:
- reject; fresh barrier required.

## G. Guard registry × projection

### X14-030 — legacy table says G044 meaning A, GuardRegistry says meaning B
Expected:
- GuardRegistry is sole guard identity authority;
- legacy table omitted from blind projection;
- no co-authoritative conflict.

### X14-031 — omitted legacy guard table contains unique non-table case semantics not present elsewhere
Expected:
- omission forbidden; packet incomplete until semantics restored.

### X14-032 — GuardRegistry missing G081 but legacy table contains it
Expected:
- `GUARD_REGISTRY_INCOMPLETE`; legacy table cannot repair authority.

## H. BSP blindness × semantic literals

### X14-033 — predecessor line “R8 v12 = NOT_IMPLEMENTED”
Expected:
- classified PRIOR_STATUS and removed.

### X14-034 — current v14 status “NOT_IMPLEMENTED”
Expected:
- CURRENT_STATUS retained.

### X14-035 — case text tests literal “CHANGES_REQUIRED”
Expected:
- SEMANTIC_TEST_LITERAL retained.

### X14-036 — prior review-evidence path appears in inherited administrative block
Expected:
- removed as PRIOR_REVIEW_METADATA.

## I. Effect/revocation/semantic state

### X14-037 — resolver qualified at preseal, RIR record revoked before commit
Expected:
- registry head changes; `STATE_CHANGED`; no effect intent.

### X14-038 — EffectIntent committed, executor revoked before execution
Expected:
- original executor cannot proceed;
- effect remains governed uncertain/pending state; independent reconciler rules apply.

### X14-039 — provider success response but no qualified reconciliation
Expected:
- not success; remain ACKNOWLEDGED_UNVERIFIED/UNCERTAIN.

## J. Recovery/liveness interactions

### X14-040 — semantic permission unavailable and recovery trust path unavailable
Expected:
- authority remains blocked;
- no emergency semantic fallback.

### X14-041 — MTR unavailable but cached prior semantic heads are present
Expected:
- no root-sensitive authority fallback; blocked.

### X14-042 — NCG detects rule contradiction but all guard unit cases individually pass
Expected:
- NCG-1 FAIL; external review packet cannot be frozen.

## Closure criterion

Corpus closure requires:
- one expected outcome per case;
- no conflict between normalized spec and matrices;
- every blocker preserves fail-closed semantics;
- no case relies on an unowned mutable authority state;
- no case can reach authority via lower-specificity fallback after a higher-specificity blocker.


---

# R8 v15 Cross-Mechanism Closure Additions

Status: **INTERNAL_NORMALIZATION_ARTIFACT_NON_AUTHORITATIVE**
Authority effect: **NONE**

These cases extend the inherited X14-001..X14-042 corpus. Expected outcomes are preregistered falsification vectors, not proof.

### X15-043 — AIM blocker precedes stale RCS
Setup:
- AIM_Smax descriptor has invalid current AIMScopePolicy permission.
- A lower-specificity AIM descriptor is ACTIVE.
- The resolver tuple that would otherwise be considered has stale/expired RCS evidence.

Expected:
- `AIM_SCOPE_PERMISSION_REEVALUATION_REQUIRED`.
- No lower AIM fallback.
- Stale RCS may be recorded diagnostically but cannot supersede or convert the earlier AIM blocker.

### X15-044 — GuardRegistry present but source case semantics omitted
Setup:
- GuardRegistry remains contiguous and includes every expected guard ID.
- One omitted legacy table case semantic record is absent from the normalized review surface and no exact trace proves preservation.

Expected:
- NCG closure fails.
- Registry contiguity alone is insufficient.
- `REVIEW_PACKET_INCOMPLETE`.

### X15-045 — Rotation barrier with ambiguous committed effect
Setup:
- An EffectIntent was committed before a rotation barrier.
- Provider dispatch result is ambiguous / `ACKNOWLEDGED_UNVERIFIED`.
- Rotation freezes covered authority writes.

Expected:
- no duplicate logical dispatch;
- no fabricated success;
- reconciliation may continue only under the exact committed intent and currently qualified reconciliation rules;
- unavailable required authority state fails closed.

### X15-046 — two revoked Smax blockers converge to same SREP
Setup:
- two applicable REVOKED entries exist at Smax;
- each has exactly one valid discharge chain;
- both chains normalize to the same canonical semantic_result_digest.

Expected:
- both blockers are discharged;
- final selection contains one unique semantic result;
- both discharge-path evidences remain preserved.

### X15-047 — partial multi-revoked discharge
Setup:
- two applicable REVOKED entries exist at Smax;
- first blocker has one valid discharge;
- second blocker has zero valid discharge paths.

Expected:
- `SEMANTIC_SCOPE_REVOKED`;
- first discharge does not enter authority selection;
- no partial-discharge authority.

### X15-048 — multi-revoked distinct terminal results
Setup:
- two applicable REVOKED entries exist at Smax;
- each has exactly one valid discharge;
- canonical terminal semantic_result_digest values differ.

Expected:
- after all blockers discharge, complete result-set comparison yields `SEMANTIC_ENTRY_CONFLICT`.

### X15-049 — one revoked blocker has two non-equivalent discharge paths
Setup:
- one applicable REVOKED Smax blocker has two otherwise valid linked successor/replacement chains;
- their canonical semantic_result_digest values differ.

Expected:
- `SEMANTIC_SUCCESSOR_CONFLICT`;
- no path is selected by traversal order.

### X15-050 — semantic_state_sequence rollback with matching-looking heads
Setup:
- a caller or stale component presents a lower historical semantic_state_sequence;
- named semantic heads are made to look equal to expected values.

Expected:
- reject historical/replayed sequence for authority use;
- sequence is internally derived from current LAS committed state;
- no caller-selected historical authority.

### X15-051 — duplicate current-candidate status block
Setup:
- projected packet contains two `BSP:CURRENT_STATUS_BEGIN version=15` blocks.

Expected:
- `REVIEW_PACKET_INCOMPLETE`;
- neither block is selected heuristically.

### X15-052 — undefined SRTT decisive-rule reference
Setup:
- all 2304 table tuples are present exactly once;
- one row references a decisive_rule_id absent from SRTT-4 RuleRegistry.

Expected:
- `SRTT_RULE_REGISTRY_INVALID`;
- arithmetic completeness cannot close the design.

### X15-053 — mapped effect terminates at exact destination
Setup:
- source REVOKED;
- old_scope_match = EXACT_MATCH;
- old_scope_effect = REPLACE_OLD_SCOPE_FOR_MAPPED_MATCH;
- destination_scope_match = EXACT_MATCH;
- scope_relation = BROADER;
- ANY, mapping and lineage validity = true;
- scope_expansion_authorized = true;
- decision_inside_authorized_expansion_domain = true.

Expected:
- `REPLACEMENT_ELIGIBLE` under canonical v13 I013/I014/I015 preserved by v15 I005/I006.
- The tuple is not malformed solely because mapped effect terminates at an EXACT_MATCH destination.
