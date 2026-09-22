A. Overall disposition: **CHANGES_REQUIRED**

The effective R8 v5+v6 design is materially stronger than v5 alone, but it is not yet sufficiently closed for executable-schema freeze. Several findings are true design blockers: MTR freshness/anti-replay is not closed, GGS-1 rollback resistance is not specified, T0 successor generation reservation is not shown atomic, LAS-2 configuration rotation is under-specified, and the complete G001-G066 guard/fault-proof catalog is not present in the review packet. These are not merely machine-readable schema details.

B. Critical findings

1. **MTR freshness and anti-replay are not closed.**
   - v6 I003 permits use of a “still-valid previously attested high-water token whose frozen freshness policy permits use.”
   - The packet does not define that freshness policy, the MTR challenge/nonce, maximum age, replay window, or MTR-outage fallback.
   - A replayed old MTR attestation could present lower T0/BTW/EBA-revocation high-water state. That attacks software/lower-layer rollback, not MTR operator honesty.
   - Required: exact MTR attestation profile, challenge binding, max age, nonce handling, and fail-closed rule when freshness cannot be established.

2. **GGS-1 rollback resistance is not specified.**
   - GGS-1 maintains `constitution_id -> EMPTY|COMMITTED` and `bootstrap_authorization_id -> UNUSED|USED`.
   - The packet does not state that GGS replica state is durable, monotonic, attested, or MTR-backed.
   - If GGS ordinary storage is rolled back or a replica is replaced, a committed genesis namespace could revert to `EMPTY`, allowing a second genesis for the same `constitution_id` with a different valid authorization.
   - Required: GGS hard-state/rollback-resistant state-machine semantics equivalent in strength to LAS-2 LASHardState, or MTR-backed GGS namespace state.

3. **T0 successor generation reservation is not shown atomic.**
   - v6 I004 says a T0 successor “receives MTR-1 reservation of the next `t0_generation`.”
   - It does not state that two successor manifests for the same next generation are rejected/reserved atomically as `T0_EQUIVOCATION`.
   - Without a single reserved digest per next generation, two conflicting successors could be prepared or witnessed.
   - Required: MTR generation-reservation CAS: `next_generation -> successor_manifest_digest`, one winner, conflicting reservation rejected.

4. **LAS-2 configuration rotation is under-specified.**
   - LASHardState includes `LAS configuration generation`, and CommitCertificate v2 binds LAS config generation.
   - The packet does not define how LAS configuration rotates while preserving term, vote, committed index, applied index, last committed entry digest, and stream head-map continuity.
   - A configuration rotation could become a rollback path if old-generation hard state or old certificates are accepted.
   - Required: CSM-bound LAS configuration rotation rule; continuity proof from old to new config; old-generation certificate rejection after effective rotation; hard-state preservation.

5. **Complete G001-G066 guard/fault-proof catalog is not in the packet.**
   - v5 inherits prior v4 guards G001-G025 and v5 adds G026-G042.
   - The packet contains G026-G042 and G043-G066, but not the full inherited v4 guard catalog.
   - v6 I056 requires every negative/adversarial case to declare `fault_proof = REQUIRED` or `NOT_APPLICABLE`; the guard tables do not show those declarations.
   - The review cannot verify every guard positive control, independent fault proof, anti-constant-reject property, or missing load-bearing guard.
   - Required: include the complete frozen G001-G066 catalog with positive controls, negative cases, and per-case fault-proof class.

C. High findings

1. **Admin-domain lifecycle lacks explicit quorum-eligibility rules.**
   - v6 I005 lists ACTIVE/SUSPENDED/RETIRED, but does not explicitly state that only ACTIVE domains count for EBA/LAS/GGS/recovery quorum.
   - SUSPENDED or RETIRED domains could be counted unless explicitly prohibited.
   - Required: only ACTIVE domains contribute signatures; SUSPENDED/RETIRED are non-voting; activation/retirement transitions are T0-successor and MTR-high-water bound.

2. **Admin-domain/controller alias closure is incomplete.**
   - LineageGraph nodes are keyed by stable principal/controller/service ID.
   - The packet does not define canonical alias resolution across controller IDs, service IDs, admin domains, or delegation roots.
   - A single principal could appear under multiple IDs/domains and falsely satisfy independence.
   - Required: canonical principal/admin-domain alias registry and collision rejection; aliases cannot manufacture domain diversity.

3. **RG-1 lacks a required provenance artifact.**
   - v6 I055 forbids schema fields/rules traceable only to PR #39/#40.
   - It does not require a schema-freeze provenance map from every schema element to effective v5+v6 design sections.
   - Without that map, undocumented manual incorporation cannot be reliably detected.
   - Required: mandatory semantic provenance manifest in the schema-freeze gate; any element without authoritative provenance is rejected.

4. **COMMIT_WITH_SEAL binds effect intent, not actual external side effect.**
   - v6 I048 atomically commits the “consequential effect intent” and advances its effect stream.
   - It does not bind actual external side-effect execution, idempotent executor behavior, compensation, or reconciliation.
   - A false-green path remains where intent commits but the external action is absent, duplicated, or altered.
   - Required: effect executor idempotency, effect stream state, and reconciliation/compensation rules for external side effects.

5. **AIM gateway enforcement profile is under-specified.**
   - v6 I024 prohibits direct env/database/network/config reads by authority code.
   - v6 I025 requires static declared manifest and runtime read traces, but says it does not claim mathematical completeness.
   - The packet does not define the enforced execution sandbox, language/runtime restrictions, syscall/network interception, or fail-closed behavior for undeclared reads.
   - Required: exact AuthorityInputGateway execution profile and mechanism-level enforcement class.

6. **CSM-2 lifecycle semantics are incomplete.**
   - CSM-2 entries have `lifecycle state`, but the packet does not define active/deprecated/revoked transitions or how AIM resolves to one active entry.
   - “Immutable candidate-bound evidence value whose governing schema/validator is CSM-bound” needs exact resolution rules.
   - Required: CSM-2 lifecycle state machine and AIM-to-CSM resolution algorithm.

D. Medium findings

1. Revocation high-water is mirrored into MTR-1 only for root-sensitive/terminal use. Lower-risk revocation rollback paths are not explicitly closed.
2. Workload-attestation downgrade is allowed when hardware attestation is unavailable, but the constitutional recording and authority limits of that downgrade are not fully specified.
3. GCP-1 v6 adds key-collision and Unicode noncharacter rules, but no new v6 reference vectors are listed for those rejection/canonicalization paths.
4. Tenant migration RequalificationProof requires an exact object map, but the packet does not state the failure result if an object is omitted and later referenced.
5. Review materiality depends on the review schema and non-material field masks. The exact reviewer-visible/non-material boundary remains schema-level, but should be frozen before schema freeze.
6. Recovery `TRUST_DOMAIN_UNRECOVERABLE` entry is a terminal fail-closed state, but the packet does not define the governed proof/sequence required to declare permanent unavailability.
7. Time NonceLedger uses `decision_context_digest`; the design should confirm that the digest includes the full AuthorityReadSet/seal context and nonce, not just a caller-supplied context label.

E. T0/MTR/bootstrap/GGS assessment

T0 successor activation via MTR is directionally strong, and MTR high-water addresses ordinary disk rollback. However, the design does not close MTR attestation freshness/replay, atomic generation reservation, or GGS rollback resistance. Bootstrap first-seen is improved by requiring MTR+BTW, but GGS state durability is essential. Without those changes, software/lower layers may still roll back or replay pre-genesis state.

F. Controller identity/lineage assessment

Exact-scope wildcard prohibition for root-sensitive roles is a strong improvement. Revocation effective sequence is present. LineageGraph canonical DAG and cycle/ambiguity rejection are good. Remaining gaps: admin-domain alias closure, canonical principal identity, and explicit quorum eligibility for ACTIVE-only domains.

G. LAS-2 concurrency/rollback assessment

LAS-2 adds LASHardState, durable vote anti-rollback, atomic StreamHeadMap CAS, and removes commutative authority bypass. This addresses the main v5 LAS-1 gaps. Remaining blocker: configuration rotation continuity. Without it, a rotation could reset or bypass hard-state/term/index constraints.

H. AIM/CSM/GCP/workload semantic-closure assessment

AIM-1 default-deny and AuthorityInputGateway are the right design direction. CSM-2 canonical envelope and CSM/AIM closure are strong. GCP-1 collision/Unicode closure improves v5. Workload attestation correctly treats hardware attestation as bounded. Remaining gaps: exact gateway enforcement profile, CSM-2 lifecycle resolution, and v6 GCP rejection reference vectors.

I. Revocation/time/evidence/reviewer assessment

Revocation high-water, UNREVOKE interval preservation, NonceLedger, time-source status at sequence, producer executable mismatch, weak-to-strong copy prohibition, review-packet digest binding, and signed Channel H are material improvements. Main residual risk: MTR freshness affects revocation/time high-water rollback. Lower-risk revocation rollback is not explicitly closed.

J. Tenant/migration/recovery/RG-1 assessment

RequalificationProof and no-implicit-widening are appropriate. Cross-constitution non-inheritance is clear. RecoveryContext anti-replay, single-use nonce, and TRUST_DOMAIN_UNRECOVERABLE are directionally correct. RG-1 correctly keeps PR #39/#40 non-authoritative, but needs a mandatory provenance artifact to detect leakage.

K. VerifiedStateSeal/COMMIT_WITH_SEAL TOCTOU assessment

AuthorityReadSet, derived-value sealing, and atomic LAS-2 head-map comparison are strong and address the main TOCTOU risks. The remaining material gap is actual external side-effect binding: intent commitment is not the same as external effect execution. That needs an idempotent executor/effect-state model.

L. Guard catalog/falsification-mechanism-proof assessment

The v6 guard additions are well targeted. However, the complete G001-G066 catalog is not in the packet, and the required per-guard fault-proof class is not shown. This prevents independent verification of positive controls, earlier-guard masking, constant-reject false-green, missing load-bearing guards, and missing fault proofs. This is a critical evidence/design gap.

M. Over-governance/deadlock assessment

The design intentionally favors integrity over liveness and accepts permanent fail-closed states. That is bounded and explicit. The main liveness-related risk is not deadlock itself, but whether fallback use of “still-valid” MTR/BTW high-water tokens becomes a weaker trust root. The freshness policy must be exact and fail-closed.

N. Minimal required changes before executable-schema freeze

1. Define MTR attestation freshness, challenge/nonce binding, max age, replay rejection, and MTR-outage behavior.
2. Add GGS-1 hard-state/rollback-resistant namespace and authorization state, or MTR-back it.
3. Define atomic MTR reservation for T0 successor generation; conflicting reservation = `T0_EQUIVOCATION`.
4. Define LAS-2 configuration rotation continuity and old-generation certificate rejection.
5. Include complete G001-G066 guard catalog with positive controls, negative cases, and per-case `fault_proof` class.
6. Specify admin-domain quorum eligibility: only ACTIVE domains count; lifecycle transitions are T0-successor/MTR-bound.
7. Add canonical controller/admin-domain alias resolution and collision rejection.
8. Add mandatory RG-1 provenance map for schema-freeze inputs.
9. Specify external effect executor idempotency/reconciliation for `COMMIT_WITH_SEAL`.
10. Define AuthorityInputGateway enforcement profile and CSM-2 lifecycle resolution.
11. Add v6 GCP reference/rejection vectors for key-collision and noncharacter cases.
12. Clarify lower-risk revocation rollback and time NonceLedger context binding.

O. Final bounded statement

This review is design-only and grants no authority. R8 v6 remains **NOT_IMPLEMENTED**. Executable-schema freeze remains **BLOCKED** unless the design gate closes. PR #39 and PR #40 remain **NON_AUTHORITATIVE**. Unresolved material findings block implementation start.