A. Overall disposition: **CHANGES_REQUIRED**

R8 v12 is not sufficiently closed at design level to proceed to executable-schema freeze. Several material design gaps remain, primarily around resolver implementation/policy binding, scope-replacement truth-table completeness, and guard-catalog packet consistency. The design is substantially stronger than inherited versions, but the remaining gaps are design-level blockers, not merely deferred schema details.

B. Critical findings

1. **Resolver implementation identity is not fully bound to ResolverPolicy-1 / CSM-5.**  
   R8 v12 requires `resolver_implementation_digest`, `resolver_runtime_manifest_digest`, workload attestation, and exact `ResolverPolicy-1` digest. However, the design does not define a CSM-bound registry or explicit mapping from `ResolverPolicy-1` to the allowed resolver implementation digest(s).  
   Risk: a substituted or drifted resolver implementation could be used if it passes conformance vectors or presents a matching policy digest, without an authoritative binding that the exact implementation is the one authorized by the active policy.  
   Required: define where allowed resolver implementation digests are registered and how the seal verifies them against the active policy.

2. **ScopeReplacementTruthTable-1 is not fully specified.**  
   The design lists allowed `old_scope_effect` values and says `decision_scope_match_rule` is a CSM-bound executable rule identifier, but it does not freeze the actual truth table for exact-match vs mapped-match, ANY-position authorization, effective-sequence handling, and prevention of accidental unblocking of a broader revoked scope.  
   Risk: a replacement mapping could unblock more scope than intended, or could fail to block when required.  
   Required: freeze the complete machine-readable truth table and reference vectors before schema freeze.

C. High findings

1. **CSRULE-4 blocker precedence does not explicitly resolve coexistence of REVOKED and ACTIVE entries at Smax.**  
   The precedence says REVOKED requires a valid successor/mapping, else `SEMANTIC_SCOPE_REVOKED`. It does not explicitly state whether other ACTIVE entries at the same Smax are ignored, or whether they cause `SEMANTIC_ENTRY_CONFLICT`.  
   Required: state that the revoked branch dominates, and define how same-Smax ACTIVE entries are treated during successor traversal.

2. **GCC-1 packet contains an inconsistent inherited guard table.**  
   In the consolidated G001–G066 section, there is a visible misalignment/omission around G044/G045 (e.g., G044 appears mislabeled as Scoped ControllerAttestation revocation, while the final GCC-1 generated view correctly lists G044 as Admin-domain lifecycle/quorum).  
   Risk: guard/case completeness checks may fail or be ambiguous.  
   Required: regenerate the packet from the authoritative machine-readable guard records and remove conflicting manual/legacy tables.

3. **AIM-3 descriptor applicability resolution is underspecified.**  
   AIM-3 requires exactly one ACTIVE applicable descriptor, but does not define the scope/applicability rule when multiple descriptors exist for the same `semantic_input_id`.  
   Risk: ambiguous descriptor selection or false `AIM_DESCRIPTOR_CONFLICT`.  
   Required: define the canonical matching rule for AIM-3 descriptors.

D. Medium findings

1. `LASAuthorityStateRoot v12` does not explicitly include `semantic_state_sequence` as a GCP-1 field; it relies on `committed_log_prefix_digest_i`. This is likely safe but should be made explicit to avoid ambiguity.

2. BSP-2 residual scan is described as version-aware, but the exact mechanism to retain current v12 `NOT_IMPLEMENTED` while removing predecessor `NOT_IMPLEMENTED` is not fully specified.

3. One-barrier–one-rotation error taxonomy mixes `STC_EQUIVOCATION` and `BARRIER_ALREADY_RESERVED`; same `rotation_id` with different proposed config should clearly map to an idempotency conflict.

4. Conformance-vector generation and runtime verification details remain deferred; they must be frozen before executable-schema freeze.

E. BSP-2/blindness assessment

The packet substantially satisfies blindness. It retains current v12 status and semantic content while excluding prior reviewer findings, adjudications, and prior-version disposition outcomes. The TXT surface is correctly authoritative; PDF is convenience-only unless manifest marks it PASS. The neutral predecessor-authority statement is appropriate. However, the inconsistent inherited guard table noted above is a packet-hygiene defect. The projection manifest must record removed-line accounting and residual-scan PASS. No prior-outcome leakage was identified in the current v12 sections.

F. CSM-5/AIM-3/semantic-state-sequence assessment

The CSM-5 named-head model, single-snapshot requirement, and derived `semantic_state_sequence` are directionally sound. Mixed heads from different LAS snapshots are rejected. Semantic updates outside LAS are prohibited. The main gaps are AIM-3 descriptor applicability resolution and the lack of an explicit CSM-bound resolver-implementation registry. GGS semantic binding is present but should be verified in schema freeze.

G. ResolverPolicy-1/CSRULE-4/ANY/scope-replacement assessment

Resolver-time ANY revalidation is a strong improvement: the resolver independently checks current permission from the same CSM-5 snapshot, and missing/narrowed/revoked permission blocks lower-specificity fallback. CSRULE-4 blocker precedence is mostly clear, but the coexistence of REVOKED and ACTIVE entries at Smax needs explicit treatment. ScopeReplacementTruthTable is the major gap: the design names the rule but does not freeze the actual truth table. ResolverPolicy-1 lacks an explicit policy-to-implementation digest mapping.

H. LASAuthorityStateRoot/RBP-2/barrier-rotation assessment

LASAuthorityStateRoot v12 includes the required named semantic heads and makes semantic streams LAS-governed. RBP-2 freezes CSM-5, AIM-3, ANY, and ResolverPolicy writes during `ROTATION_PREPARED`. Barrier uniqueness and abort semantics are defined. STC semantic-head equality is required. The main refinement needed is explicit inclusion of `semantic_state_sequence` in the state-root object and clearer error taxonomy for barrier reservation conflicts.

I. DPS-v3/seal/TOCTOU assessment

DecisionPresealContext-v3 includes semantic sequence, CSM-5 head, AIM-3 head, ANY permission head, ResolverPolicy digest, resolver implementation/runtime identity, revocation head, and runtime attestation. VerifiedStateSeal binds the same fields plus time/nonce proof. Consequential commit compares current LAS semantic heads and sequence to the seal; any change yields `STATE_CHANGED`. This adequately addresses TOCTOU at design level, provided the resolver implementation binding gap is closed.

J. GCC-1 guard/case completeness assessment

The final GCC-1 generated view lists G001–G130 contiguously with no missing guards, positive controls, and FP classes. However, the packet contains an inconsistent inherited consolidated table around G044/G045. GCC-1 compilation must fail on duplicate/conflicting definitions; therefore the packet must be regenerated from authoritative machine-readable guard records before closure. The final GCC-1 view itself appears complete, but the packet as supplied is not clean.

K. Inherited protection/no-regression assessment

R8 v12 appears to strengthen inherited controls rather than weaken them. It adds CSM-5, AIM-3, ResolverPolicy-1, CSRULE-4, resolver-time ANY revalidation, LASAuthorityStateRoot v12, RBP-2, one-barrier–one-rotation, DPS-v3, BSP-2, and GCC-1. No concrete weakening of T0/MTR/GGS/LAS/AIEP/revocation/time/evidence/effect/migration/recovery controls was identified. The inherited v11 CSM-4/AIM-2/CSRULE-3 requirements remain unless superseded by stronger v12 rules. No regression finding is raised, but schema freeze must verify no accidental omission.

L. Over-governance/deadlock assessment

The design intentionally favors fail-closed integrity over liveness. If ANY permission amendment, resolver policy update, or MTR/semantic state is unavailable, authority can block. This is acceptable for a governance design, but the resulting deadlock modes should be documented as bounded liveness risks. No emergency bypass that weakens authority is permitted, which is correct.

M. Minimal required changes before executable-schema freeze

1. Define a CSM-bound registry or explicit policy mapping for allowed resolver implementation digests and runtime manifests; require DPS-v3/seal to verify them.
2. Freeze the complete ScopeReplacementTruthTable-1, including exact/mapped match rules, ANY authorization, effective sequence, and prevention of broader revoked-scope unblocking.
3. Clarify CSRULE-4 Smax handling when REVOKED and other ACTIVE entries coexist; specify that revoked successor/mapping traversal dominates.
4. Define AIM-3 descriptor applicability resolution when multiple descriptors exist for one `semantic_input_id`.
5. Regenerate GCC-1 from authoritative machine-readable guard records and remove/repair the inconsistent inherited table.
6. Explicitly include `semantic_state_sequence` in the LASAuthorityStateRoot v12 GCP-1 object.
7. Specify BSP-2 version-aware residual scan so current v12 `NOT_IMPLEMENTED` is retained while predecessor outcomes are removed.
8. Clarify one-barrier rotation error taxonomy for same rotation ID with different proposed config.

N. Final bounded statement

This review grants no authority.  
R8 v12 remains **NOT_IMPLEMENTED**.  
Executable-schema freeze remains **BLOCKED** unless the design gate closes.  
PR #39/#40 remain **NON_AUTHORITATIVE**.  
Unresolved material findings block implementation start.