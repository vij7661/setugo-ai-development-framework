A. Overall disposition: **CHANGES_REQUIRED**

Design-level closure is not sufficient to proceed to executable-schema freeze. Several material design gaps remain, including one concrete false-green/fallback path in AIM applicability and missing blind-packet/projection completeness artifacts. This review grants no authority.

---

B. Critical findings

1. **AIMApplicability-1 can fall back after invalid/narrowed ANY permission**
   - v13 I023 computes AIM applicability by first retaining only descriptors whose ANY components are permitted by current `AIMScopePolicy`, then derives specificity and determines `AIM_Smax`.
   - That means a high-specificity descriptor whose ANY permission was narrowed/revoked is discarded before `AIM_Smax`, allowing a lower-specificity ACTIVE descriptor to resolve.
   - This violates the inherited no-fallback/blocker principle and can produce a false-green authority decision under a less-specific rule.
   - Required fix: compute `AIM_Smax` over all matching effective descriptors before ANY-permission filtering. If any descriptor at `AIM_Smax` has invalid/narrowed/revoked ANY permission, return a blocker state such as `AIM_SCOPE_PERMISSION_REEVALUATION_REQUIRED` and prohibit lower-specificity fallback.

---

C. High findings

1. **RIR-1 effective-sequence predicate is not explicit**
   - I002 requires an exact ACTIVE RIR-1 record at `semantic_state_sequence`, but does not explicitly require:
     - `activation_sequence <= semantic_state_sequence`; and
     - `retirement_or_revocation_sequence == null || retirement_or_revocation_sequence > semantic_state_sequence`.
   - Lifecycle state alone is insufficient unless the state transition is guaranteed atomic with the sequence. Add an explicit effective-sequence predicate.

2. **CSRULE-5 “exactly one semantic result” lacks canonical equivalence**
   - I020 says if multiple non-equivalent ACTIVE semantic results remain, return `SEMANTIC_ENTRY_CONFLICT`; if exactly one remains, continue.
   - “Equivalent” is not defined as a CSM-bound canonical rule. Without it, the resolver may either falsely conflict equivalent results or falsely merge non-equivalent results.
   - Add a canonical semantic-result equivalence rule and bind it into ResolverPolicy-1.

3. **Blind packet lacks required BSP-3 projection manifest and GuardRegistry omission manifest**
   - v13 I030 requires the BSP-3 manifest to record classifier version, current candidate version, removed records, and residual classified-record count.
   - v13 I034 permits omission of legacy manual guard tables only when the projection manifest lists the omitted table section digest/source.
   - The supplied packet contains a blindness/guard-authority statement but not the required machine-verifiable projection manifests. Packet completeness and residual-outcome blindness cannot be independently confirmed.
   - Add the BSP-3 projection manifest and GuardRegistry omission manifest to the authoritative TXT packet.

4. **BSP-3 classifier is not an exact deterministic redaction grammar**
   - I028 defines a semantic classifier, but not an exact machine-readable line/block grammar and residual-scan pattern set.
   - v11 BSP-1 had exact redaction grammar. v13 BSP-3 should likewise freeze exact patterns, including the current-candidate-version exception and test-vector retention rule.
   - Without this, packet generation is not deterministically reproducible.

---

D. Medium findings

1. **SRTT-2 total Cartesian table not yet fully enumerated**
   - I011–I015 define ordering and rows, and the 12 reference vectors are useful.
   - However, the design does not itself enumerate every Cartesian branch implied by all enum combinations. Executable-schema freeze can generate this, but design closure would be stronger if the total truth table or a deterministic generation rule were frozen now.

2. **RCS-1 conformance freshness/expiration not specified**
   - RIR-1 records bind a conformance suite digest and execution evidence. The design does not state whether conformance evidence expires, must be refreshed after runtime/policy changes, or remains valid indefinitely while the record is ACTIVE.
   - Add a conformance validity/freshness rule.

3. **Minor field-name typo in LASAuthorityStateRoot v13**
   - I026 contains `semantic_state_sequence_i:i`; intended is likely `semantic_state_sequence_i`. This is not a semantic blocker but should be corrected before schema freeze.

4. **GuardRegistry-1 G044/G045 identity appears correct, but omission manifest absent**
   - G044 = Admin-domain lifecycle/quorum; G045 = Scoped ControllerAttestation revocation. The mapped V6 cases appear consistent.
   - No duplicate/conflicting record found. However, the packet lacks the required omission manifest proving legacy-table omission did not remove unique case semantics.

---

E. RIR-1/RCS-1 assessment

RIR-1 and RCS-1 are substantially closed at design level:
- exact policy/implementation/runtime/workload/conformance tuple binding is required;
- conformance alone is not authorization;
- missing/failed vectors make the resolver record unqualified;
- DPS/seal bind the RIR head and active record.

Remaining gaps:
- explicit effective-sequence check for RIR records;
- conformance evidence freshness/expiration;
- ensure multiple ACTIVE records for the same ResolverPolicy but different implementations cannot be selected ambiguously for one decision context.

---

F. SRTT-2/CSRULE-5 assessment

SRTT-2 is largely total and ordered:
- exact replacement requires SAME destination;
- mapped replacement permits SAME/NARROWER;
- BROADER requires `SEMANTIC_SCOPE_EXPANSION_AMENDMENT` and decision inside `AuthorizedExpansionDomain`;
- invalid ANY, ineffective mapping, invalid cross-lineage mapping, destination no-match, and BLOCK_OLD_SCOPE are handled.

CSRULE-5 revoked dominance is well specified:
- REVOKED at Smax dominates unrelated ACTIVE peers;
- each revoked blocker must be uniquely discharged;
- zero discharge -> `SEMANTIC_SCOPE_REVOKED`;
- multiple non-equivalent discharge paths -> `SEMANTIC_SUCCESSOR_CONFLICT`;
- successful discharge then compares against genuine ACTIVE peers.

Remaining gap:
- canonical equivalence for “exactly one semantic result” is undefined.

---

G. AIMApplicability-1 assessment

**Material blocker.** AIMApplicability-1 is not closed because invalid/narrowed ANY permission is filtered before `AIM_Smax`. This permits lower-specificity fallback where the inherited security principle requires a blocker at the highest matching specificity. This is a concrete false-green path and must be fixed before schema freeze.

Other AIM aspects are directionally correct:
- AIM-4 descriptors are append-only;
- AIMScopePolicy is CSM-bound;
- revoked highest-specificity descriptor without valid successor blocks lower fallback;
- source-lineage redirect requires constitutional amendment.

---

H. LASAuthorityStateRoot/BSP-3/barrier assessment

LASAuthorityStateRoot v13 correctly makes `semantic_state_sequence` and named registry heads explicit, including CSM-5, AIM-4, ANY permission, AIM scope policy, ResolverPolicy, RIR-1, and GuardRegistry-1.

BarrierRotation v13 error taxonomy is clear:
- idempotent replay for same rotation/config/STC;
- `IDEMPOTENCY_CONFLICT` for same rotation with different config/STC;
- `BARRIER_ALREADY_RESERVED` for different rotation on reserved barrier;
- `STC_EQUIVOCATION` for contradictory valid reservations;
- ABORTED barrier permanently closed.

BSP-3 gaps:
- exact redaction grammar missing;
- projection manifest missing from packet;
- residual-scan classifier not yet frozen as a deterministic pattern set.

---

I. GuardRegistry-1/case-lineage assessment

GuardRegistry-1 appears structurally sound:
- G001–G140 are contiguous and unique in the supplied JSON;
- each guard has at least one positive case;
- each negative case has a fault-proof class;
- G044/G045 identities appear correct against inherited V6 semantics;
- G131–G140 correctly map to v13 mechanisms and cases.

Legacy manual guard tables are omitted as display/index artifacts, and GuardRegistry-1 is declared sole guard-identity authority. However, the packet does not contain the required omission manifest proving every omitted guard ID remains present and no unique case semantics were removed.

---

J. Inherited protection/no-regression assessment

v13 is mostly additive and does not intentionally weaken inherited T0/MTR/GGS/LAS/AIEP/revocation/time/evidence/effect/migration/recovery, semantic state sealing, ANY revalidation, or rotation freeze protections.

However, two areas create regression risk:
- AIM ANY filtering before `AIM_Smax` weakens inherited ANY drift/no-fallback semantics;
- missing BSP-3 projection manifest weakens verifiable blindness and packet completeness.

These must be corrected before no-regression can be affirmed.

---

K. Over-governance/deadlock assessment

The design intentionally favors fail-closed operation:
- resolver implementation unavailable -> blocked;
- scope replacement blocked -> blocked;
- AIM conflict -> blocked;
- guard registry conflict -> blocked;
- no emergency bypass weakens authority.

This is acceptable for safety. The critical AIM finding is not merely a liveness issue; it is a potential false-authority path.

---

L. Minimal required changes before executable-schema freeze

1. Fix AIMApplicability-1:
   - compute `AIM_Smax` over all matching effective descriptors before ANY-permission filtering;
   - treat invalid/narrowed/revoked ANY at `AIM_Smax` as blocker-equivalent;
   - prohibit lower-specificity fallback.

2. Add explicit RIR-1 effective-sequence predicate:
   - `activation_sequence <= semantic_state_sequence`;
   - `retirement_or_revocation_sequence == null || > semantic_state_sequence`.

3. Define canonical semantic-result equivalence for CSRULE-5 and bind it into ResolverPolicy-1.

4. Freeze exact BSP-3 redaction grammar and residual-scan patterns, including current-candidate-version retention and semantic test-vector retention.

5. Add BSP-3 projection manifest and GuardRegistry omission manifest to the authoritative TXT packet.

6. Freeze the total SRTT-2 Cartesian truth table or a deterministic generation rule for executable-schema freeze.

7. Add conformance freshness/expiration rule for RCS-1.

8. Correct the `semantic_state_sequence_i:i` typo in LASAuthorityStateRoot v13.

9. Add reference cases covering the above fixes, especially AIM ANY blocker-before-Smax and BSP-3 residual metadata retention.

---

M. Final bounded statement

This review grants no authority.

R8 v13 remains **NOT_IMPLEMENTED**.

Executable-schema freeze remains **BLOCKED** unless the design gate closes.

PR #39 and PR #40 remain **NON_AUTHORITATIVE**.

Unresolved material findings above block implementation start.