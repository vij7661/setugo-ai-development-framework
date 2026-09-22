A. Overall disposition: **CHANGES_REQUIRED**

Design review only. I did not perform implementation/runtime verification. I treat T0/EBA as an explicit bounded trust axiom, but v5 does not yet close all software-consumed bindings to that axiom. Several paths remain where a lower layer, stale state, concurrent operation, or unclassified semantic input can produce a false-green or self-grant effect.

B. Critical findings

1. **Genesis commit is not linearizable across constitution namespace and authorization state.**  
   `CAS_GENESIS` says it atomically changes authorization `UNUSED -> USED` and rejects if no existing constitution head exists. But v5 does not define an atomic compare-and-swap over `constitution_id`, `bootstrap_authorization_id`, and authorization serial. Two concurrent genesis attempts with different valid authorizations for the same `constitution_id` can both observe “no existing head” and both commit unless the operation is linearized through LAS/T0 or an equivalent atomic namespace. This is a self-grant/fork path.

2. **`CAS_APPEND` validation and head update are not atomic.**  
   `R8V5-I020` validates that `expected predecessor == currently committed head`, but v5 does not specify that validation, CommitCertificate acceptance, and head advancement occur as one atomic compare-and-swap. Two concurrent valid 2-of-3 certificates for the same predecessor can both pass validation before either updates the head. `LAS_EQUIVOCATION` is detection after the fact, not prevention. The design needs an atomic commit primitive and an explicit freeze state on equivocation.

3. **LAS term/index anti-rollback is missing.**  
   `CommitCertificate` binds `consensus_term` and `log_index`, but v5 does not require persistent monotonic tracking of highest term/index or durable vote state. A lower layer can roll back LAS replica state and replay an old majority certificate. This directly attacks the declared linearization point.

4. **`VerifiedStateSeal`/`COMMIT_WITH_SEAL` is incomplete for unnamed stores and multi-store atomicity.**  
   `R8V5-I050` seals “exact store IDs” and `R8V5-I051` rechecks “all mutable heads named by the seal.” If an authority predicate consumes a store, derived index, display field, governance snapshot, or configuration object not named in the seal, the seal can remain valid while authority-relevant state changes. v5 also does not define atomic multi-store verification/commit semantics. This is a TOCTOU false-green path.

5. **T0 pinning and rollback protection are not bound to secure monotonic persistence.**  
   T0 digest is provisioned out of band and `t0_generation + manifest_digest` is persisted. But v5 does not specify that this pin and persisted highest generation are stored in a rollback-resistant, hardware/attested, or otherwise lower-layer-resistant location. A lower layer can reset the store and replay a lower generation unless the out-of-band pin itself is monotonic and externally enforced.

6. **CSM-1 closure detection is not complete.**  
   `R8V5-I025` catches an “authority-bearing runtime dependency not represented in CSM-1,” but v5 does not define how all software-consumed semantic inputs are enumerated. Authority-relevant semantics can hide in extension maps, display/non-material fields, environment configuration, parser defaults, or derived indexes and not be classified as a runtime dependency. Default-deny must apply to any semantic input consumed by authority predicates, not only runtime dependencies.

7. **Recovery/root replacement can deadlock permanently.**  
   `R8V5-I049` and V5-048 block recovery when EBA, witness, or mandatory trigger evidence is unavailable. T0 successor activation also requires BTW inclusion/consistency under predecessor trust. If BTW or EBA is permanently unavailable, there is no constitutional recovery path. This may be an intentional security property, but v5 must explicitly declare and bound this deadlock rather than leave it implicit.

C. High findings

- T0 successor “activation sequence/time condition” is not exactly specified, and time authority may itself depend on T0/BTW.
- BTW first-seen uniqueness for bootstrap authorization is not bound to a split-view-resistant first-seen store.
- ControllerAttestation wildcard authority is allowed if EBA authorizes it, but v5 does not constrain wildcard scope, tenant scope, role scope, or revocation interaction.
- Attestation revocation/expiry lacks an explicit effective-sequence rule comparable to issuer/producer revocation.
- LineageProof rejects cyclic/ambiguous lineage, but no exact cycle/ambiguity resolution algorithm or canonical graph binding is frozen.
- Commutative exception `R8V5-I023` requires a proof of deterministic canonical output, but the verifier of that proof and the proof format are not specified.
- RuntimeManifest binds OS/container/crypto digests, but no hardware/attestation root proves those digests are the ones actually executing.
- GCP extension-map shadowing and NFC/canonical-key collision rules are not fully closed.
- Anchor rotation linkage to old/new quorum certificates is required, but the effective revocation sequence for old anchor controllers is not fully bound to a monotonic revocation head.
- Time nonce store rollback/replay is not protected by a monotonic nonce head.
- Issuer parent-compromise cascade is good, but general revocation undo, hidden/stale revocation, and monotonic revocation head are not closed.
- Producer temporal revocation is improved, but weak-to-strong laundering and producer executable mismatch are not fully addressed.
- Materiality masks do not close hidden semantics in display/non-material fields consumed by human reviewers or downstream tools.
- Tenant migration requires revalidation, but no exact requalification proof prevents migration widening.
- Channel X attestation is improved, but Channel H authenticity and provider-internal memory boundedness remain outside closure.
- State-root specification claims derived/indexed completeness, but no enforcement mechanism prevents an authority predicate from consuming an unsealed derived value.

D. Medium findings

- CSM-1’s canonical structure and digest computation are not frozen in v5.
- GCP-1 reference-vector digests are asserted but not independently derivable from the text alone without a frozen reference implementation.
- GCP-1 Unicode handling does not explicitly address noncharacters, normalization edge cases, or key canonicalization collisions beyond NFC.
- Admin-domain semantics are T0-bound, but v5 does not fully close how EBA itself may create/rotate domains without manufacturing quorum diversity.
- Time-source overlap window status is required, but exact status resolution at attestation sequence is not fully specified.
- Recovery trigger replay/context binding is not explicitly covered by nonce or decision-context binding.
- CaseProofContract independent fault proof is required only “where relevant,” leaving relevance to be gamed.
- Constant-reject false-green is partly mitigated by paired valid controls, but the guard catalog does not explicitly require anti-constant-reject proof for every guard.
- Over-governance may intentionally block unsafe operation, but no prospective liveness path is defined for simultaneous T0/BTW/witness outage.
- PR #39/#40 are repeatedly marked non-authoritative, but v5 does not specify a reconciliation gate that prevents their semantics from leaking into schema freeze.

E. T0/EBA/BTW/bootstrap assessment

**Not closed.** T0 is a bounded trust axiom, but software pinning, persistence, rollback resistance, successor activation, BTW first-seen uniqueness, same-generation equivocation, and witness outage handling are not sufficiently bound to lower-layer-resistant state. T0/EBA/BTW can be counterfeited or rolled back if the persistent pin and highest-generation state are not monotonic and attested.

F. Controller identity/independence assessment

**Partially improved, not closed.** Scoped `ControllerAttestation`, `LineageProof`, and `admin_domain_id` semantics are directionally correct. Remaining blockers: wildcard abuse, attestation revocation/expiry effective sequence, delegation-cycle canonical resolution, domain fabrication by EBA, Channel H authenticity, and provider-internal memory isolation.

G. LAS/CAS/anchor concurrency assessment

**Not closed.** The largest concurrency gaps are atomic `CAS_APPEND`, atomic genesis commit, LAS term/index anti-rollback, durable vote persistence, and explicit freeze/reconciliation on `LAS_EQUIVOCATION`. Without these, the claimed linearization point is not enforceable at design level.

H. CSM/GCP/runtime semantic closure assessment

**Partially closed, not sufficient.** CSM-1 is broad, but semantic closure detection is not complete. GCP-1 is mostly specified, but extension maps, NFC/key collisions, defaults, and reference-vector derivation need exact schema-level closure. Runtime attestation lacks a hardware/attestation root proving the runtime manifest matches actual execution.

I. Reviewer/issuer/revocation/time assessment

**Not closed.** Reviewer Channel X is improved; Channel H and provider isolation are not. Issuer rotation and parent compromise are improved; revocation monotonic head, hidden revocation, and revocation undo are not fully closed. Time nonce uniqueness is stated, but nonce-store rollback and replay resistance are not.

J. Evidence/materiality/tenant/recovery assessment

**Not closed.** Producer temporal revocation is improved. Materiality masks are a good step but do not close display/non-material hidden semantics. Tenant namespacing is good but migration widening and cross-constitution requalification need exact proofs. Recovery self-protection is good, but trigger replay and deadlock/liveness remain unresolved.

K. TOCTOU/state-integrity assessment

**Critical gap.** `VerifiedStateSeal` is necessary but not sufficient. v5 must define the complete authority-relevant store/derived/semantic manifest and an atomic multi-store `COMMIT_WITH_SEAL` protocol. Otherwise a valid seal can coexist with mutated authority state.

L. Guard catalog/falsification-mechanism-proof assessment

**Incomplete.** G026-G042 add useful guards, but missing load-bearing guards include: genesis concurrency linearization, LAS term/index rollback, revocation monotonic head, time nonce store rollback, T0 secure pin persistence, state-root/store completeness, Channel H authenticity, display/non-material hidden semantics, and recovery trigger replay. CaseProofContract v2 is directionally correct but does not by itself close these gaps.

M. Over-governance/deadlock assessment

**Bounded safe non-operation is present, but deadlock is not fully adjudicated.** If T0/EBA/BTW/witness/recovery dependencies are simultaneously unavailable, v5 may be permanently unable to recover or rotate. This may be acceptable as a safety property, but it must be explicitly declared as an accepted bounded deadlock, or a prospective liveness path must be added without inventing a weaker trust root.

N. Minimal required changes before executable-schema freeze

1. Define an atomic, linearizable genesis commit protocol across authorization serial, constitution namespace, and T0/BTW.
2. Define atomic `CAS_APPEND` compare-and-swap semantics and require durable LAS term/index/vote anti-rollback.
3. Bind T0 pin and highest accepted `t0_generation + manifest_digest` to secure monotonic/attested storage.
4. Define a complete authority-relevant store/derived/semantic manifest and require `COMMIT_WITH_SEAL` to recheck all of it atomically.
5. Close CSM-1 semantic dependency detection with default-deny for any authority-consumed semantic input.
6. Add missing guards for genesis concurrency, LAS rollback, revocation head monotonicity, time nonce rollback, state-root completeness, Channel H, display/non-material semantics, and recovery trigger replay.
7. Specify controller wildcard constraints, attestation revocation effective sequence, and canonical lineage-cycle/ambiguity resolution.
8. Specify BTW first-seen uniqueness and split-view-resistant persistence.
9. Specify hardware/attestation root for RuntimeManifest/OS/container/crypto execution.
10. Specify materiality treatment of display/non-material fields that can influence human or automated review.
11. Specify migration requalification proofs and cross-constitution import non-inheritance checks.
12. Specify reviewer provider memory isolation/boundedness or explicitly exclude it from Channel X qualification.
13. Resolve or explicitly bound the recovery/T0/BTW deadlock case.

O. Final bounded statement

This review grants no authority of any kind. R8 v5 remains **NOT_IMPLEMENTED** and **INDEPENDENT_REVIEW_REQUIRED**. PR #39 and PR #40 remain **NON_AUTHORITATIVE**. The unresolved material findings above block implementation start and block executable-schema freeze until addressed or explicitly adjudicated as accepted bounded trust assumptions. This review does not approve implementation, qualification, merge, release, deploy, production, policy, or terminal authority.