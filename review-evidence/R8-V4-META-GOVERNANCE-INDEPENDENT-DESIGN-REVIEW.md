## A. Overall disposition

**CHANGES_REQUIRED**

R8 v4 is materially better bounded than an implicit-root design, but it is **not sufficiently closed at design level** to proceed to executable-schema freeze and implementation preparation. Several T0, bootstrap, CAS, semantic-closure, and guard-catalog gaps would allow lower layers or deployment configuration to evade, counterfeit, or bypass the claimed T0-bound semantics.

---

## B. Critical findings

**C1. EBA/T0 provisioning and replacement are not closed.**
R8V4-I001 says EBA-1 key set and policy digest are provisioned out of band, but the design does not freeze an immutable bootstrap manifest, external root pinning, or EBA version rollover/trust-root replacement rules. A deployment or lower layer could be configured with a different EBA key set, or software could accept a self-issued replacement EBA without a T0-anchored authorization path. The T0 axiom is declared, but its root boundary is not yet cryptographically and procedurally bounded.

**C2. BTW-1 trust root and first-seen guarantee are not T0-bound.**
R8V4-I009 relies on an external Bootstrap Transparency Witness for singleton pre-genesis registration. The design does not specify how BTW-1’s verification key/policy, initial trusted signed tree head, or split-view resistance are pinned to T0/EBA. If BTW-1 equivocates or the platform accepts an unauthenticated first-seen receipt, the same `BootstrapAuthorization` can bootstrap more than once. `CAS_GENESIS` must require a BTW inclusion proof against a T0-pinned initial STH.

**C3. `BootstrapAuthorization` → genesis byte binding is incomplete.**
`CAS_GENESIS(bootstrap_authorization_id, expected=UNUSED, genesis_digest)` does not state that `genesis_digest` must match the authorization’s allowed initial Meta-Governor/schema/CSR/GCP-1/first-registry digests. It also does not explicitly require authorization expiration checking or mandatory BTW inclusion/consistency proof before commit. A valid authorization could therefore be reused with unauthorized genesis bytes.

**C4. `CAS_APPEND` linearizability and commit-certificate semantics are not designed.**
R8V4-I019–I022 describe CAS_APPEND and single-predecessor consumption, but do not specify the linearization point, commit-certificate format, signer/quorum, validation rules, or how the system guarantees that one predecessor cannot obtain two valid commit certificates. The 2-of-3 anchor quorum does not itself linearize the ledger. Without an explicit linearizable register or consensus model, split-brain commit certificates remain possible.

**C5. Constitutional semantic artifact closure is incomplete.**
R8V4-I023 lists many digest-bound artifacts, but omits several authority-relevant semantic inputs, including:
- stream schemas and commutative-event markings;
- frozen merge functions for commutative exceptions;
- recovery trigger schemas;
- BTW/witness verification policy and initial trust root;
- EBA provisioning/rotation/replacement policy;
- state-root computation specification;
- guard catalog and CaseProofContract schemas;
- runtime/compiler/crypto dependency attestation policy.

If these remain outside the constitutional digest set, lower layers can rewrite or bypass T0-bound semantics without triggering `CONSTITUTIONAL_AMENDMENT_REQUIRED`.

**C6. Verify-before-authority has a TOCTOU gap.**
R8V4-I047 checks committed head, anchored head, recomputed state root, and schema digest before an authority-bearing decision consumes a store. It does not require an atomic read/seal or recheck at authority-use/commit time. A store mutation between check and use can invalidate the decision context. The decision must be bound to the exact verified state root/head and revalidated at commit.

---

## C. High findings

- **ControllerAttestation lacks constitution/tenant/role-instance binding.** R8V4-I004 binds controller identity and role classes, but not the specific constitution, tenant, or authority scope. An attestation valid in one constitution could be replayed in another unless scope is explicitly bound.
- **Independence lineage predicate is undefined.** R8V4-I005 says shared “EBA-attested controlling lineage” defeats independence, but no lineage proof format, root delegation graph, or resolution rule is specified. Admin-domain diversity depends on EBA-attested domains, but domain registry semantics are not frozen.
- **Anchor controller rotation and witness STH freshness are missing.** R8V4-I014–I018 cover equivocation but not anchor-controller rotation, expiry replacement, witness outage states, or anti-rollback for witness signed tree heads. Stale witness STHs could be replayed.
- **Time authority rotation and nonce uniqueness are missing.** R8V4-I038–I041 bind time to decision context and nonce, but do not require nonce uniqueness per action or specify time-authority rotation/rollover.
- **Issuer key rotation and parent-issuer compromise are not covered.** R8V4-I033 enforces SoD, but no cascade revocation, parent-compromise invalidation, or issuer-key rotation rule is specified.
- **QualifiedEvidenceProducer revocation temporal semantics are incomplete.** R8V4-I042–I045 define enrollment and strong-evidence minting, but not whether evidence minted before producer revocation remains strong, nor how producer compromise invalidates downstream evidence.
- **Materiality field-mask exactness and dependency-extractor digest are not frozen.** R8V4-I053–I054 require field masks and extractor binding, but the exact masks and digests are not in the design closure set. “Display” fields could still carry authority-relevant hidden semantics.
- **Tenant migration and cross-tenant stable-ID namespace rules are incomplete.** R8V4-I058 rejects aliases and requires stable IDs, but tenant migration, namespace scoping, and cross-tenant replay prevention are not fully specified.
- **Recovery trigger schemas are not in the constitutional artifact list.** R8V4-I056 says they are constitutional semantic artifacts, but R8V4-I023 does not include them. Recovery self-modification, new-constitution inheritance, and recovery-quorum collusion bounds need explicit closure.
- **Guard catalog is incomplete for critical attack areas.** Missing guards/cases include EBA rotation, BTW split-view, witness outage/stale STH, runtime dependency drift, TOCTOU, issuer key rotation, producer revocation temporal effects, tenant migration, and recovery-quorum self-modification.

---

## D. Medium findings

- GCP-1 escape mapping is described as “single frozen” but not actually defined. Exact escape bytes are required for canonical closure.
- GCP-1 absent/null, extension maps, whitespace, and exact set-vs-array discrimination are not fully specified.
- Reference vector SHA-256 digests are required before implementation, but not yet frozen in the design.
- CAS_APPEND retry/idempotency semantics are not specified; retries may produce avoidable `HEAD_CONFLICT` or duplicate-event ambiguity.
- Commutative exception abuse is possible if stream schemas/merge functions are not constitutional artifacts.
- Reviewer Channel X provider independence is not explicitly tied to EBA/controller/service attestation; “independently administered” is not a cryptographic predicate.
- Over-governance safe non-operation states are present, but EBA/witness/reviewer outage may deadlock without a bounded liveness/recovery path.

---

## E. T0/EBA/bootstrap assessment

**Bounded but not closed.**

The explicit T0 axiom is the correct move: R8 v4 does not claim to prove real-world non-collusion, and it correctly treats EBA-1 as a trust terminus. However, the software-facing root boundary is incomplete:

- EBA key/policy provisioning is out-of-band but not immutably pinned or rotation-bounded.
- BTW-1 is external but not explicitly rooted in T0/EBA.
- `BootstrapAuthorization` is not fully bound to `genesis_digest`.
- Expiration and BTW inclusion are not mandatory preconditions for `CAS_GENESIS`.
- Self-issued labels are rejected for controllers, but self-issued EBA/BTW replacements are not clearly blocked.

Until these are fixed, the design cannot yet claim that software cannot substitute self-issued labels for T0 attestations in the root/bootstrap path.

---

## F. Anchor/witness/CAS concurrency assessment

The 2-of-3 anchor quorum, distinct admin-domain requirement, witness inclusion requirement, and equivocation freeze are directionally sound. However:

- Witness STH freshness/anti-rollback is missing.
- Anchor controller rotation is missing.
- CAS_APPEND linearizability and commit-certificate semantics are underspecified.
- Split-brain commit certificates are not cryptographically prevented by the design text alone.
- Commutative-event exception can be abused if stream schema/merge function are not constitutional artifacts.

This area requires design closure before schema freeze.

---

## G. Constitutional semantic/GCP-1/SPR assessment

**Constitutional semantic closure is incomplete.** R8V4-I023 must include all authority-relevant semantic inputs, including stream schemas, commutative merge functions, recovery trigger schemas, BTW/witness policy, EBA rotation policy, state-root computation, guard catalog, CaseProofContract schema, and runtime dependency attestation policy.

**GCP-1 is partially closed.** Integer range and lexical forms are mostly addressed. Missing: exact escape mapping, absent/null, extension maps, whitespace, and complete reference vectors/digests.

**SPR lifecycle is directionally sound.** Immutable primitive IDs, append-only versions, alias prohibition, and old-evidence version binding are good. Missing: exact policy for old evidence under retired/superseded primitive versions and authority resolution across versions.

---

## H. Reviewer/issuer/revocation/time independence assessment

**Reviewer independence:** Channel H + Channel X and provider-internal-memory boundedness are good, but Channel X provider independence is not cryptographically tied to EBA/controller/service attestation. Packet isolation is stated, but packet-generation independence is not fully bounded.

**Issuer:** Non-overridable SoD is strong. Missing: issuer key rotation, parent-issuer compromise cascade, and revocation-undo lifecycle details.

**Revocation:** Monotonic head, immediate CAS/anchor, and exact decision-context binding are good. Missing: bootstrap trust for `last_seen_revocation_seq`, hidden revocation detection, and revocation undo constraints beyond SoD.

**Time:** Context-bound TimeAttestation and 2-of-3 domain diversity are good. Missing: nonce uniqueness, time-authority rotation, and circularity around expiration checks.

---

## I. Evidence/materiality/state-integrity assessment

**QualifiedEvidenceProducer path:** Enrollment, executable identity, and weak-to-strong no-laundering are good. Missing: producer revocation temporal effects and compromise invalidation of already-minted strong evidence.

**Materiality:** Field-mask-only non-material classification and unknown-field fail-closed are good. Missing: exact field-mask digests, hidden display-field semantics, and dependency-extractor compromise response.

**State integrity:** State-root/head verification and auditor role are good. Missing: TOCTOU-safe authority use and explicit derived-index inclusion in the state-root computation.

---

## J. Tenant/checkpoint/recovery assessment

**Tenants/checkpoints:** Stable-ID-only authority resolution, alias rejection, immediate checkpoint anchoring, and stale-checkpoint conflict rules are directionally sound. Missing: tenant migration semantics, cross-tenant namespace isolation, and stable-ID replay across tenants.

**Recovery:** Mandatory trigger schemas, root/recovery separation, and unrecoverable boundary are good. Missing: recovery trigger schemas in the constitutional artifact list, recovery-quorum self-modification constraints, and explicit new-constitution non-inheritance enforcement.

---

## K. Guard catalog / falsification-mechanism-proof assessment

The Guard Catalog and CaseProofContract v2 are a strong improvement. However, the catalog is not complete for the attack areas in the prompt. Missing load-bearing guards/cases include:

- EBA version rollover/trust-root replacement.
- BTW split-view/equivocation and initial STH pinning.
- Witness outage and stale STH replay.
- Anchor controller rotation.
- CAS_APPEND linearization and commit-certificate split-brain.
- Runtime/compiler/crypto dependency drift.
- TOCTOU in verify-before-authority.
- Issuer key rotation and parent-issuer compromise.
- Producer revocation temporal effects.
- Tenant migration and cross-tenant stable-ID replay.
- Recovery-quorum self-modification and new-constitution inheritance.

Without these, the falsification mechanism cannot prove the claimed closure.

---

## L. Over-governance/deadlock assessment

The blocked/bounded states are appropriate for safety: `CONSTITUTIONAL_UNRECOVERABLE`, `ANCHOR_EQUIVOCATION`, `LEDGER_EQUIVOCATION`, `REVOCATION_UNAVAILABLE`, `TIME_AUTHORITY_UNAVAILABLE`, `REVIEWER_UNAVAILABLE`, unresolved `POLICY_CONFLICT`, and `STATE_INTEGRITY_FAILURE`.

However, EBA/witness/reviewer outage can deadlock authority without a bounded liveness/recovery path. Recovery must be explicitly prevented from converting blocked states into authority except through a valid, T0-bound recovery authorization.

---

## M. Minimal required changes before executable-schema freeze/implementation preparation

1. **Freeze an immutable T0 bootstrap manifest** for EBA and BTW roots, including key sets, policy digests, initial trusted STH, and version/rotation/replacement rules.
2. **Bind BTW-1 to T0/EBA** and require inclusion/consistency proofs against a T0-pinned initial STH before `CAS_GENESIS`.
3. **Strengthen `CAS_GENESIS` preconditions**: unexpired authorization, `genesis_digest` matches authorization-allowed digests, BTW inclusion proof, and `expected=UNUSED`.
4. **Specify `CAS_APPEND` linearization and commit-certificate semantics**, including signer/quorum, certificate format, validation, idempotency, and conflict rules.
5. **Extend R8V4-I023** to include all authority-relevant semantic inputs: stream schemas, commutative merge functions, recovery trigger schemas, BTW/witness policy, EBA rotation policy, state-root computation, guard catalog, CaseProofContract schema, runtime dependency attestation policy, materiality masks, and GCP-1 reference vectors.
6. **Bind ControllerAttestation to constitution/tenant/role scope** and define the independence lineage proof format.
7. **Specify rotation/revocation temporal semantics** for anchors, time authorities, issuers, and qualified evidence producers.
8. **Add witness STH freshness/anti-rollback rules** and anchor-controller rotation rules.
9. **Make verify-before-authority TOCTOU-safe** by binding authority use to the exact verified state root/head and rechecking at commit.
10. **Add missing Guard Catalog cases** for all critical/high gaps above.
11. **Freeze exact GCP-1 escape mapping, absent/null, extension maps, and reference digests.**
12. **Close tenant migration, cross-tenant stable-ID, recovery self-modification, and new-constitution inheritance rules.**

---

## N. Final bounded statement

This review grants **no authority**. It is design review only and does not claim implementation, runtime, qualification, merge, release, deploy, production, policy, or terminal verification.

**R8 v4 remains NOT_IMPLEMENTED.**
**PR #39 and PR #40 remain NON_AUTHORITATIVE.**
**Unresolved material findings block implementation start.**

The correct next step is adjudication of these findings and a revised or clarified design closure pass before executable-schema freeze and implementation preparation.