A. Overall disposition: **CHANGES_REQUIRED**

Design review only. I do not claim implementation/runtime verification. I treat T0/EBA/MTR/BTW/GGS/LAS/workload-attestation roots as bounded assumptions and attack bypass/counterfeit/rollback paths rather than demanding infinite trust regress. R8 v9 is not sufficiently closed to proceed to executable-schema freeze.

B. Critical findings

1. **CSM-2 envelope directly conflicts with CSRULE-2.**
   - v6 `R8V6-I026` defines CSM-2 entries with `semantic_input_id` and states: “Duplicate semantic_input_id is rejected.”
   - v9 `R8V9-I003` requires CSRULE-2 to build a candidate set from “all entries in the same `semantic_input_id + semantic_lineage_id`.”
   - v9 also relies on per-entry scope, lifecycle, predecessor/successor relation, and `ANYScopePermission`.
   - The inherited CSM-2 canonical envelope does not include `semantic_lineage_id`, scope tuple, predecessor/successor relation, or ANY-permission binding, and it forbids multiple entries with the same `semantic_input_id`.
   - Therefore CSRULE-2 cannot be instantiated over the inherited CSM-2 structure without a design-level amendment to CSM-2.
   - This is a genuine design blocker, not a safely deferred schema detail, because v9’s core anti-fallback rule depends on a registry shape that v6 explicitly prohibits.

C. High findings

1. **LAS-3/GGS-3 rotation continuity lacks an atomic state-transfer binding.**
   - v9 `R8V9-I010`–`I011` require a joining replica to prove matching `StreamHeadMap`, term/index, certificate chain, and idempotency/dedup ledger root, and says the idempotency root must equal the root committed by the old configuration at the JOINT-entry prerequisite index.
   - v9 CTS-1 `R8V9-I013` binds only `old_config_generation`, `old_config_digest`, `proposed_new_config_digest`, `transition_id`, `expected_config_stream_seq`, and `expected_config_stream_head`.
   - The CTS-1 transition command does not bind the LAS/GGS log prefix, `StreamHeadMap` root, idempotency ledger root, prior certificate-chain digest, or JOINT-entry prerequisite index.
   - Without such a binding, the old configuration’s committed state is not independently tied into ENTER_JOINT/ACTIVATE, so continuity is asserted rather than enforced.
   - Required fix: define a signed `LASStateTransferCertificate`/`GGSStateTransferCertificate` and require it to be referenced by JOINT and ACTIVATE, with old+new quorum signatures.

2. **Mandatory v9 falsification cases are incomplete.**
   - G092 lacks a positive case for a valid constitutional successor re-establishing a revoked scope.
   - G092/G093 lack an explicit cross-lineage fallback rejection case.
   - G093 lacks a case where project/org policy attempts to broaden `ANYScopePermission`.
   - G095/G096 lack an explicit case where ACTIVATE does not match the committed JOINT transition.
   - Because the schema-freeze gate requires all G001-G099 CaseProofContracts to be frozen, these omissions block closure.

D. Medium findings

1. **CTS-1 “current valid configuration” during JOINT is ambiguous.**
   - v9 `R8V9-I013` says the configuration-transition stream is governed by the current valid configuration.
   - v7 `R8V7-I014` says during JOINT every authority commit requires majority old + majority new.
   - Clarify that configuration-transition commands during JOINT require old+new quorum and that ACTIVATE must bind the exact committed JOINT certificate.

2. **Successor replacement-scope specificity is not fully defined.**
   - v9 `R8V9-I006` allows an ACTIVE successor with “exact same effective scope or an explicitly constitutionally authorized replacement scope.”
   - If the replacement scope changes specificity, it may not participate at `Smax`.
   - Clarify whether replacement-scope successors must preserve specificity, or how `Smax` is recalculated.

3. **Registration may allow an ACTIVE non-successor at the same `Smax` as a REVOKED entry.**
   - v9 `R8V9-I001` forbids conflicting ACTIVE entries at the exact same slot, but does not require a replacement ACTIVE entry to declare the revoked predecessor as successor.
   - CSRULE-2 will later block if no valid successor explicitly supersedes the revoked entry, so this fails closed, but registration should reject or mark such entries ineligible to avoid misleading state.

4. **Packet hygiene issue.**
   - The blind packet says it excludes prior reviewer findings/adjudications, but canonical texts still contain adjudication hash references.
   - This is not a design blocker, but if strict exclusion is required, those references should be removed or isolated from the blind packet.

E. CSRULE-2/ANY-scope assessment

- The intended CSRULE-2 logic is strong: it fixes `Smax` before lifecycle filtering, blocks revoked-specific fallback to lower ACTIVE/ANY general rules, forbids cross-lineage fallback without constitutional mapping, and requires an explicit constitutional successor to re-establish revoked scope.
- `ANYScopePermission` is correctly placed as a CSM-bound constitutional rule that project/org policy cannot broaden.
- However, the CSM-2 envelope conflict prevents the rule from being operationalized. The missing cross-lineage and ANY-broadening falsification cases also leave the guard incomplete for schema freeze.

F. LAS-3/CTS-1 rotation assessment

- LAS-3 formal version identity is well stated: CSM-bound artifact set, idempotency ledger, rotation protocol digest, and “no runtime may claim LAS-3 while using older/different semantics.”
- Idempotency continuity across rotation is correctly required: consumed keys remain consumed, replay after rotation with different event digest yields `IDEMPOTENCY_CONFLICT`.
- CTS-1 correctly makes ENTER_JOINT atomic and prevents two different JOINT branches from consuming the same old-config predecessor.
- The missing state-transfer certificate binding and missing ACTIVATE-mismatch case are material gaps before schema freeze.

G. SPG historical-validity assessment

- SGHVP-1 is adequately specified at design level: pre-effective output, post-effective output, unknown sequence, retrospective invalidation, replacement-generator non-inheritance, and preservation of history.
- The v9 cases V9-017 through V9-020 cover the main historical-validity branches.
- No critical SPG blocker found, assuming the CSM-bound SGHVP-1 artifact is later frozen correctly.

H. Reconciler/effect assessment

- RIP-1 is appropriately strict: canonical subject, admin domain, delegation lineage, credential, workload identity, and effect-class independence rule.
- It correctly blocks alias-to-same-canonical-subject reconcilers, shared prohibited delegation roots, and domain overlap where prohibited.
- Reconciler authority is observation-only and cannot forge `SUCCEEDED_RECONCILED` without provider-specific evidence.
- Cases V9-021 through V9-023 are adequate for the stated attack areas.

I. Inherited T0/MTR/GGS/AIEP/time/provenance assessment

- Inherited T0 reservation authorization, MTRF-2 freshness, GGS-3 rollback/rotation, AIEP/AIG broker-only input enforcement, DPS-2 time context, SPM/RG provenance, EESM effect state, migration freshness, trust-loss recovery, GCP vectors, and guard/case lineage appear preserved across v4-v9.
- I found no new critical bypass in these inherited areas beyond the CSM-2 conflict and LAS-3/GGS-3 state-transfer binding gap.
- This is design review only; it does not verify implementation or runtime behavior.

J. Guard/case lineage and packet-completeness assessment

- G001-G099 are present across the inherited catalogs: G001-G025 from v4, G026-G042 from v5, G043-G066 from v6, G067-G081 from v7, G082-G091 from v8, and G092-G099 from v9.
- Each listed guard has a positive control and listed negatives have FP classes.
- However, mandatory v9 attack areas are missing cases: valid constitutional successor, cross-lineage fallback, ANY-permission broadening, and ACTIVATE/JOINT mismatch.
- Canonical v4-v9 texts are present in the packet. Minor packet hygiene issue: prior adjudication hash references remain.

K. Over-governance/deadlock assessment

- The design correctly favors integrity over liveness and preserves fail-closed states such as `SEMANTIC_SCOPE_REVOKED`, `CONFIG_HEAD_CONFLICT`, `SCHEMA_GENERATOR_INVALID_AT_GENERATION`, `EXECUTOR_REVOKED_UNCERTAIN`, and `MTR_UNAVAILABLE`.
- No liveness workaround appears to weaken authority.
- Blocked semantic scope and JOINT transition conflict can cause deliberate deadlock until constitutional amendment or lawful recovery; this is consistent with the stated claim boundary.

L. Minimal required changes before executable-schema freeze

1. Amend CSM-2 to support CSRULE-2:
   - Replace duplicate `semantic_input_id` rejection with a canonical per-entry key, e.g. `semantic_entry_id` or `semantic_input_id + semantic_lineage_id + scope + version`.
   - Add scope tuple, `semantic_lineage_id`, lifecycle state, predecessor/successor relation, and `ANYScopePermission` reference.
   - Define canonical sorting and duplicate rejection at the new entry key.

2. Define and bind LAS-3/GGS-3 state-transfer continuity:
   - Add a signed state-transfer certificate containing term/index, `StreamHeadMap` root, idempotency ledger root, prior certificate-chain digest, and configuration generation.
   - Require ENTER_JOINT and ACTIVATE to reference it.
   - Require old+new quorum signatures where JOINT state applies.

3. Add missing preregistered falsification cases:
   - Valid constitutional successor re-establishes revoked scope.
   - Cross-lineage fallback blocked without mapping.
   - Policy attempts to broaden `ANYScopePermission` -> reject.
   - ACTIVATE does not match committed JOINT -> reject.
   - State-transfer mismatch for `StreamHeadMap`, term/index, certificate chain, or idempotency ledger -> non-voting/reject.

4. Clarify CTS-1 quorum semantics during JOINT and define “current valid configuration” for configuration-transition stream commands.

5. Clarify replacement-scope specificity in CSRULE-2 successor re-establishment.

6. If strict blind-packet exclusion is required, remove or isolate adjudication hash references.

M. Final bounded statement

This review grants no authority.  
R8 v9 remains **NOT_IMPLEMENTED**.  
Executable-schema freeze remains **BLOCKED** unless the design gate closes.  
PR #39 and PR #40 remain **NON_AUTHORITATIVE**.  
Unresolved material findings, especially the CSM-2/CSRULE-2 conflict and LAS-3/GGS-3 state-transfer binding gap, block implementation start.