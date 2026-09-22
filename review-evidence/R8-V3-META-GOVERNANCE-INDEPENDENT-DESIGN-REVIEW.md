A. Overall disposition: **CHANGES_REQUIRED**

This is a design-only blind review. It finds R8 v3 substantially more closed than a bare MUST-based design, but not sufficiently closed to begin implementation. The main blockers are trust-root and independence proofs that remain self-asserted, plus concurrency/fork gaps in authority-bearing heads.

B. Critical findings

1. **No non-self-asserted root of trust for principal/controller identity.**  
   R8V3-I01, I03, I37-I40, I45-I46, and I63 rely on `controller_id`, `credential_id`, `execution_identity`, delegation lineage, and time-source independence. The design does not prove how those identifiers are bound to real independent control. An attacker can create multiple principal labels with distinct IDs but the same actual controller, satisfying nominal 2-of-3 root, recovery, time, reviewer, or issuer independence. This undermines L0, recovery, time, reviewer isolation, and separation-of-duties.

2. **Anchor replica independence and collusion are not closed.**  
   R8V3-I10 says `ANCHOR-A` and `ANCHOR-B` are independently administered, but no proof, enrollment, or independence predicate is defined for replica controllers. If both replicas share one controller or collude, they can present the same malicious digest at the same sequence, and R8V3-I11 divergence detection never triggers. There is no external witness or transparency mechanism.

3. **L0 bootstrap is self-authenticating.**  
   R8V3-I04-I08 signs the genesis with root keys, but the first trust in those root keys is not established by anything outside the bootstrap ceremony itself. An attacker can run the first ceremony with three attacker-controlled Ed25519 keys, label them `ROOT-A/B/C`, produce a valid genesis, and satisfy the written checks. “Root principal authentication” is therefore not closed at design level.

4. **Concurrent constitutional/registry fork race is unresolved.**  
   R8V3-I18 rejects an amendment if the predecessor is not current or if the same predecessor already has an authoritative successor. But the checks are not specified as atomic. Two valid amendments with the same predecessor could both pass pre-checks before either successor is recorded. The same issue applies to registry heads under R8V3-I35. A compare-and-swap, single-writer, or explicit fork-detection protocol is missing.

C. High findings

1. **CSR “reinterpretation” is not formally decidable.**  
   R8V3-I13-I14 makes CSR changes constitutional, including “reinterpreting” a CSR entry. The design does not define who determines whether a change is a reinterpretation, nor how that determination is independently validated. A compromised or buggy Meta-Governor could classify a semantic change as non-CSR.

2. **Separation-of-duties is conditional.**  
   R8V3-I42 requires configurator/beneficiary disjointness only “where effective policy requires separation.” For terminal or root-sensitive issuer changes, this should be non-overridable. Otherwise a policy actor can waive the separation and allow self-benefiting issuer control.

3. **Revocation head freshness is not sufficiently anchored.**  
   R8V3-I43 denies use when the revocation head cannot be verified, which is fail-closed. But the design does not require every revocation update to be dual-anchored or monotonic against rollback. A stale or hidden revocation head could cause denial, and a rollback could restore a revoked authority if the revocation registry is not fully anchored.

4. **Time attestation replay binding is incomplete.**  
   R8V3-I45 includes `attestation_nonce` and `issued_sequence`, but the design does not bind a time attestation to the exact decision, candidate digest, or use context. A valid old attestation may be replayed if the nonce/sequence check is not context-bound.

5. **Evidence transition “trusted execution path” is undefined.**  
   R8V3-I54 correctly prohibits metadata-only upgrades, but R8V3-I53-I55 does not define the trusted execution path that can create a stronger evidence object. Without that, the non-upgradable rules can be bypassed by claiming a new evidence object was produced through an ambiguous trusted path.

6. **Out-of-band mutation detection is asserted, not designed.**  
   R8V3-I68 says authority-bearing storage mutated outside an authorized path creates integrity failure and requires recovery. The design does not specify how that mutation is detected, who detects it, or how detection is anchored. A database edit could otherwise remain invisible until conflicting evidence appears.

7. **Reviewer independence excludes provider-internal memory.**  
   R8V3-I39 limits isolation claims to platform-controlled context and explicitly excludes undetectable provider-internal memory. If reviewer independence is load-bearing for constitutional amendment, then provider-internal leakage must either be qualified or compensated by additional controls, such as multi-provider or human-independent review.

D. Medium findings

1. **GCP-1 lacks exact integer and edge-case rules.**  
   R8V3-I24 prohibits floats, exponents, NaN, Infinity, and negative zero, but does not define integer range, leading-zero rules, or exact canonical representation for all integer edge cases. R8V3-I29 depends on exact bytes.

2. **Object-class non-material mutations may hide semantic changes.**  
   R8V3-I49-I52 closes unknown classes and caller metadata downgrades, but “allowed non-material mutations” could still alter semantics if the dependency extraction rule is incomplete or stale.

3. **Checkpoint anchoring frequency is vague for non-terminal events.**  
   R8V3-I60 requires immediate dual anchor for terminal/constitutional/review-barrier checkpoints, but ordinary lifecycle-advancing checkpoints use “effective anchoring frequency” without an exact bound.

4. **Recovery trigger evidence is not schema-mandatory.**  
   R8V3-I62 says each trigger requires evidence defined by the constitution. If the constitution omits or weakens that evidence schema, a recovery quorum assertion could be accepted without independent fault proof.

5. **Positive-control mapping is incomplete.**  
   Section 20 lists minimum guards requiring paired controls, but does not freeze complete guard IDs, case mapping, or coverage proof. V3-085-V3-090 correctly address masking and constant rejection, but the full matrix is not yet closed.

6. **Tenant alias safety depends on enforcement.**  
   R8V3-I57 says aliases are display metadata only. The design must prove that no authority resolution path ever uses an alias, especially during migration or recovery.

7. **SPR alias safety is good, but primitive lifecycle needs exactness.**  
   R8V3-I31-I33 prevents shadowing and makes primitive change constitutional, but deletion, retirement, supersession, and unit-conversion migration rules remain under-specified.

E. L0/bootstrap/root/recovery assessment

**Not closed.** Root principal authentication is circular: the first root keys are trusted because they sign the genesis, but the genesis is valid because the root keys sign it. Independence is defined by IDs, not proven by external control separation. Bootstrap anti-replay depends on a global namespace that does not exist before first genesis. Root replacement relies on recovery trigger evidence whose authentication is not closed. Recovery/root separation is only a `controller_id` separation, not a proof of distinct real-world control. Simultaneous root+recovery loss is handled as `CONSTITUTIONAL_UNRECOVERABLE`, which is acceptable, but new-constitution creation cannot inherit authority without independent requalification.

F. Constitutional self-amendment assessment

**Partially closed.** CSR enumeration is strong, and amendment requires independent root quorum plus dual CAL-1 anchoring. However, “reinterpretation” is not formally decidable, the Meta-Governor implementation binding does not solve initial trust in the Meta-Governor artifact, and amendment anti-replay is not atomic. Migration/recovery laundering is prohibited by R8V3-I16, but enforcement depends on CSR classification.

G. CAL-1/history/registry-fork assessment

**Partially closed.** CAL-1 gives a concrete event schema, dual anchoring, divergence detection, and recovery rules. The critical gap is replica independence and collusion. A malicious or shared-controller `ANCHOR-A`/`ANCHOR-B` pair can agree on a false digest, making divergence detection useless. Registry fork detection is good in principle, but non-commutative fork reconciliation can be captured by a compromised recovery/adjudication authority. Stale-head selection by recovery is not fully prevented if recovery is malicious.

H. GCP-1/SPR/policy semantic assessment

**Mostly specified, but not frozen.** GCP-1 covers NFC, duplicate keys, ordering, integers, null/absence, sets, unknown fields, and parser binding. It is close to implementable, but exact reference vectors, integer range rules, escape edge cases, and parser/schema digests are deferred to post-review. SPR alias safety is reasonable, but primitive lifecycle and semantic equivalence are not fully formalized. Policy conflict handling correctly fails closed, but the only resolution path for non-overridable constitutional semantics is constitutional amendment, which may be unavailable.

I. Reviewer/issuer/time independence assessment

**Weak.** All three domains depend on the same unproven controller/lineage model. Reviewer isolation is bounded honestly, but the provider-internal exclusion means independence cannot be fully proven for load-bearing review. Issuer enrollment has parent authority, but parent authority bootstrapping and separation-of-duties conditionality are not closed. Time quorum uses 2-of-3, but time-source independence and replay binding are incomplete.

J. Materiality/evidence/tenant/checkpoint assessment

**Partially closed.** Unknown classes fail closed, dependency metadata cannot lower materiality, tenant IDs are stable, and checkpoint producer attestation is specified. Gaps remain in trusted execution for evidence transitions, out-of-band mutation detection, non-material mutation semantics, and checkpoint anchoring frequency. Tenant alias collisions are safe only if authority resolution never falls back to display aliases.

K. Recovery/blocked-state/deadlock assessment

**Fail-closed posture is good, but recovery trigger proof is not closed.** `CONSTITUTIONAL_UNRECOVERABLE`, `REVIEWER_UNAVAILABLE`, `ANCHOR_DIVERGENCE`, `REVOCATION_UNAVAILABLE`, and `TIME_AUTHORITY_UNAVAILABLE` are explicitly allowed to remain blocked. That is acceptable. However, recovery quorum collusion and false recovery triggers remain possible under the identity-independence gap. Blocked-state bypass is prohibited, but detection of out-of-band mutation is not designed.

L. Falsification-matrix/mechanism-proof assessment

**Good structure, incomplete closure.** The CaseProofContract, earlier-guard masking rule, and paired positive-control requirement are strong. But independent fault proof is not defined, guard IDs are not frozen, positive-control mapping is only “at minimum,” and the full V3 matrix does not yet prove every load-bearing guard is reached. Constant-reject false greens are addressed by V3-088.

M. Minimal required changes before implementation

1. Define a non-self-asserted root of trust for principal/controller/credential/execution identity, including out-of-band or external attestation for root, recovery, anchor, time, reviewer, and issuer independence.
2. Add anchor replica independence proof and collusion resistance, e.g., at least three independent replicas or an external transparency/witness mechanism.
3. Close L0 bootstrap authentication with a pre-genesis trust anchor and atomic singleton bootstrap that prevents concurrent genesis.
4. Make constitutional amendment and registry head updates atomic or explicitly fork-detecting; no two valid successors from the same predecessor.
5. Freeze exact GCP-1 reference vectors, integer range rules, parser/schema digests, and canonicalization edge cases before implementation.
6. Make separation-of-duties non-conditional for root-sensitive and terminal issuer changes.
7. Bind revocation heads and time attestations to the exact use context; require dual anchoring or monotonic proof for revocation updates.
8. Define the trusted execution path for evidence transitions and prove non-upgradable rules cannot be bypassed by metadata or ambiguous new object creation.
9. Specify out-of-band mutation detection and integrity monitoring for blocked-state bypass prevention.
10. Qualify or compensate for provider-internal reviewer memory if reviewer independence is load-bearing.
11. Complete the falsification matrix with frozen guard IDs, complete positive-control mapping, and exact independent fault-proof requirements.

N. Final bounded statement

This review grants no authority. R8 v3 remains **NOT_IMPLEMENTED**. PR #39 and PR #40 remain **NON_AUTHORITATIVE**. Unresolved material findings above block implementation start.