A. Overall disposition: **CHANGES_REQUIRED**

R8 v11 is not sufficiently closed for executable-schema freeze. The design has strong lineage/scope and rotation-barrier intent, but several material safety and blindness gaps remain. The most serious are replayable semantic resolution via unbound `decision_sequence`, incomplete integration of CSM-4 into LAS-3 state-root/rotation-freeze semantics, reliance on Meta-Governor self-reporting for ANY-permission drift, and a non-blind review packet that still contains prior disposition statuses.

B. Critical findings

1. **Blind packet is not blind.**
   The projected packet still contains prior review/adjudication outcomes such as `R8 v1 — CHANGES_REQUIRED`, `R8 v1-v10 = CHANGES_REQUIRED`, and predecessor status lines. These are prior dispositions/adjudications, not merely semantic lineage. BSP-1 removed some commit/hash metadata but did not remove prior outcome statuses. The packet header claims `Residual prior-review administrative metadata scan: PASS`, but this is false for blindness purposes. This violates the blindness rule and can bias the review.

2. **CSRULE-3 `decision_sequence` is not bound to authoritative current high-water state.**
   CSRULE-3 takes `decision_sequence` as an input and uses it to evaluate lifecycle transitions, including `SCOPE_PERMISSION_REEVALUATION_REQUIRED` and revoked/superseded traversal. If `decision_sequence` can be supplied as a historical value before a revocation or permission narrowing, resolution can select an entry that is no longer lawful. The design does not require `decision_sequence` to be the current LAS-3/MTR high-water sequence, nor does it explicitly include it in `AuthorityReadSet`, `VerifiedStateSeal`, or `DecisionPresealContext`. This creates a concrete false-green/replay path.

3. **CSM-4 is not clearly included in LAS-3 AuthorityStateRoot or RBP-1 freeze scope.**
   `LASAuthorityStateRoot(B)` enumerates `committed_log_prefix_digest_B`, `StreamHeadMap_root_B`, `idempotency_ledger_root_B`, `authority_state_machine_root_B`, `revocation_stream_head_B`, `nonce_ledger_head_B`, `effect_stream_head_B`, `configuration_generation`, and `prior_certificate_chain_digest_B`. It does not explicitly include the CSM-4 registry head, AIM-2 head, or `any_scope_permissions` head. If CSM-4 is not a LAS-3 stream or is not covered by `authority_state_machine_root_B`, semantic-registry changes could occur after `ROTATION_PREPARE` without being frozen or detected at the rotation barrier. This undermines RBP-1 and state-root integrity.

4. **ANYScopePermission drift enforcement relies on Meta-Governor completeness.**
   When an ANY permission is narrowed or revoked, v11 requires affected ACTIVE entries to receive a LAS-committed lifecycle event to `SCOPE_PERMISSION_REEVALUATION_REQUIRED`. The transition is “derived by Meta-Governor from CSM-4 state.” If the Meta-Governor omits an affected entry, or falsely declares the transition complete, the resolver may see that entry as ACTIVE and resolve it. CSRULE-3 does not independently re-check the active ANYScopePermission for every ANY-scoped candidate at decision time. This is a self-grant/incomplete-transition path.

C. High findings

1. **AIM-2 descriptor lifecycle and immutability are not specified.**
   AIM-2 binds `source_semantic_lineage_id`. If AIM-2 itself can be changed without constitutional amendment or CSM-4 binding, an attacker could redirect resolution to a different source lineage and bypass a revoked specific entry in the original lineage.

2. **`resolver_policy_digest` is opaque.**
   CSM-4 includes `resolver_policy_digest`, but the design does not specify the resolver policy artifact, its contents, its lifecycle, or how it is validated. This leaves the resolver algorithm potentially driftable despite the canonical envelope.

3. **State-root formulas omit semantic-registry heads.**
   Beyond LAS-3, the same omission applies to GGS-3 and any rotation/state-transfer certification that should bind the exact semantic registry state. If CSM-4/AIM-2 heads are not in the certified roots, rotation and state-transfer certificates can be produced over an authority state that does not fully bind semantic resolution.

4. **STC-2 uniqueness is per `rotation_id/barrier`, not per barrier.**
   v11 says exactly one `stc_digest` may commit for one `rotation_id/barrier`. It does not explicitly prohibit multiple `rotation_id` values for the same barrier. Under equivocation or authorized confusion, competing STCs for the same barrier could arise. A stronger rule should bind one barrier to at most one lawful rotation.

5. **PDF projection is corrupted.**
   The PDF version contains many pages of repeated `1 1 1...` and missing tables/content. The text version is complete, but the PDF cannot be treated as a reliable blind packet projection.

D. Medium findings

1. The consolidated guard catalog is spread across v4-v11 texts. v11 alone lists only G108-G117. The packet includes inherited texts, but a single consolidated G001-G117 table with FP classes would reduce omission risk.

2. ANY revalidation authority is described as “the constitutional authority class governing ANYScopePermission,” but the exact class and amendment path are not named.

3. `ScopeReplacementMapping` and `replacement_effect_on_old_scope` are specified in prose; executable-schema details are deferred, but the design should state the exact allowed values and matching semantics before freeze.

4. `DecisionPresealContext`/DPS-2 does not explicitly include the CSM-4 head, AIM-2 head, or CSRULE-3 `decision_sequence`. Time/nonce binding may therefore not bind semantic resolution state.

5. The `resolver_policy_digest` and CSRULE-3 algorithm need a frozen CSM-bound artifact before schema freeze.

E. CSM-4/AIM-2/CSRULE-3/ANY assessment

**CSM-4 representability:** Mostly strong. Multiple entries per `semantic_input_id`, nine-component scope tuple, canonical key, deterministic ordering, and mapping objects are present. However, `resolver_policy_digest` is not backed by an explicit artifact, and CSM-4 head is not clearly included in LAS-3 state roots. Representability is not the main gap; binding and resolution-time enforcement are.

**AIM-2/CSRULE-3:** Starting lineage binding exists, cross-lineage fallback is prohibited, and mapping conflict rules are present. The critical gap is unbound `decision_sequence`, which permits historical replay. AIM-2 immutability is also missing.

**ANY:** Lifecycle states, Smax blocking, fallback prohibition, and revalidation paths are defined. Enforcement is too dependent on Meta-Governor-derived lifecycle events. Resolver-level independent revalidation is required.

F. LAS-3/GGS-3/RBP-1/STC-2/CTS-3 assessment

**LAS-3/GGS-3:** State-root formulas are detailed but omit CSM-4/AIM-2/ANY permission heads. Exact root contents must include all authority-semantic registry heads used by resolution.

**RBP-1:** The barrier concept is strong: `ROTATION_PREPARE` at B freezes ordinary authority writes. However, the freeze scope must explicitly include CSM-4, AIM-2, and semantic-registry updates. Otherwise semantic changes can race the rotation.

**STC-2:** Unique committed transfer certificate per `rotation_id/barrier` is good, but should be strengthened to one barrier → one lawful rotation.

**CTS-3:** PRE_JOINT / ROTATION_PREPARED / JOINT / ACTIVE_NEW quorum semantics are clear. Wrong STC/JOIN on ACTIVATE is rejected. No critical flaw found beyond the missing CSM-4 freeze scope.

G. Inherited T0/MTR/AIEP/time/provenance/effect/recovery assessment

Inherited protections from v4-v10 are largely present: T0 reservation, MTR freshness, AIEP/AIG, revocation/time binding, schema provenance, effect reconciliation, migration, and trust-loss states. v11 does not explicitly weaken them. However, the CSRULE-3 `decision_sequence` replay gap can bypass inherited revocation/time/semantic freshness. The inherited protections must be integrated into semantic resolution by binding `decision_sequence` to current LAS/MTR high-water and including CSM-4/AIM-2 heads in sealed state.

H. Guard/case lineage and packet-completeness assessment

G001-G117 lineage appears represented across canonical v4-v11 texts. v11 adds G108-G117 with positive cases, negatives, and FP classes. Cross-lineage positive/negative, ANY-drift Smax, post-PREPARE write race, and residual blind-metadata negative cases are present. The main completeness problem is not guard lineage but blind-packet hygiene and the lack of a single consolidated G001-G117 table in v11 itself.

I. Blind-packet hygiene assessment

**FAIL.**

The packet is not blind. It retains prior disposition statuses such as `CHANGES_REQUIRED` for v1-v10. These are prior adjudication outcomes. BSP-1’s residual scan is insufficient because it targets commit/hash metadata and some adjudication headers, but not prior outcome status lines. The projection manifest’s `PASS` claim is therefore inaccurate for blindness. The PDF is also corrupted. A clean blind packet must remove all prior review outcome statuses and regenerate the manifest.

J. Over-governance/deadlock assessment

The design intentionally favors fail-closed safety over liveness. Rotation freeze, permission reevaluation, revoked-scope blocking, and mapping conflicts can all cause indefinite non-operation. That is acceptable only if no weaker authority path is created. No such liveness workaround was found. However, the ANY-permission enforcement gap is a safety hole masquerading as completeness. The critical findings above must be fixed before deadlock behavior can be considered acceptable.

K. Minimal required changes before executable-schema freeze

1. **Fix blind packet hygiene.** Remove all prior disposition/adjudication outcome statuses from the projected packet, including `CHANGES_REQUIRED`, `BOUNDED_PASS`, `INSUFFICIENT_EVIDENCE`, and predecessor status lists. Rerun BSP-1 with expanded residual patterns. Regenerate manifest. Ensure PDF is complete or not used.

2. **Bind `decision_sequence` to authoritative high-water.** Require CSRULE-3 `decision_sequence` to be the current LAS-3/MTR-committed sequence or explicitly bounded by it. Include it in `AuthorityReadSet`, `VerifiedStateSeal`, and `DecisionPresealContext`. Add negative cases for historical replay.

3. **Make CSM-4/AIM-2 LAS-3-governed streams.** Include CSM-4 registry head, AIM-2 head, and `any_scope_permissions` head in `LASAuthorityStateRoot` and in RBP-1 freeze scope. Add cases for CSM-4 update during rotation freeze.

4. **Add resolver-level ANY permission revalidation.** CSRULE-3 must independently verify the active ANYScopePermission for every ANY-scoped candidate at decision time. Do not rely solely on Meta-Governor lifecycle marking. Add case where permission is narrowed but lifecycle event is omitted.

5. **Specify AIM-2 immutability.** Bind AIM-2 descriptor to CSM-4/constitutional amendment. Prohibit source-lineage substitution except by constitutional amendment. Add negative case.

6. **Freeze `resolver_policy_digest` artifact.** Specify the resolver policy object, its lifecycle, and its validation. Make CSRULE-3 algorithm a CSM-bound artifact.

7. **Strengthen STC-2 to one barrier → one rotation.** Prohibit multiple lawful `rotation_id` values for the same barrier.

8. **Add a consolidated G001-G117 guard/case table** in v11 or the packet, including FP classes and positive controls, to reduce omission risk.

L. Final bounded statement

This review grants no authority.  
R8 v11 remains **NOT_IMPLEMENTED**.  
Executable-schema freeze remains **BLOCKED** unless the design gate closes.  
PR #39 and PR #40 remain **NON_AUTHORITATIVE**.  
Unresolved material findings block implementation start.