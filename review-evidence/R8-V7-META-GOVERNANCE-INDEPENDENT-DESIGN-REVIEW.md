A. Overall disposition: **CHANGES_REQUIRED**

The effective R8 v5+v6+v7 design is substantially stronger than prior generations and addresses many rollback, replay, and provenance risks. However, material design blockers remain in MTR reservation authorization, GGS rotation continuity, AIEP broker attestation, effect-executor revocation, time-context completeness, and review-packet completeness. The guard catalog cannot be fully assessed because inherited v4 case semantics for G001–G025 are omitted from the packet.

B. Critical findings

- **CF-1 — MTR `RESERVE_T0_SUCCESSOR` has no authorization precondition.**  
  v7 I006 defines the atomic reservation operation but requires only `next_generation = expected_current_generation + 1`, current generation match, and no existing reservation. It does **not** require the reservation request to be signed by the lawful predecessor T0 policy, EBA quorum, or a valid successor manifest. Ordinary software or a lower-layer actor could reserve the next generation with an arbitrary successor digest, causing `T0_EQUIVOCATION`, blocking the lawful successor, or forcing fail-closed T0 outage. This is a concrete denial/equivocation path against T0 succession.

- **CF-2 — Review packet omits canonical v4 inherited case semantics for G001–G025.**  
  v7 I046 says the consolidated table plus canonical v5 and v6 texts make inherited guards visible. But G001–G025 and V4-001…V4-084 are inherited from v4. The packet does not include the canonical v4 design text or v4 case semantics. Therefore the reviewer cannot verify that inherited case IDs were not silently weakened, that every negative case has an appropriate FP class, or that positive controls reach the exact guard. This is a design-review completeness failure under the prompt’s mandatory attack area 16.

C. High findings

- **HF-1 — MTR response-sequence high-water is not enforced at acceptance.**  
  v7 I003 includes an MTR monotonic response sequence, but v7 I004 does not require the verifier to compare it against a persisted highest accepted MTR response sequence. A verifier local rollback could replay an older MTRFreshnessAttestation if the challenge has not yet been marked CONSUMED. The MTR response sequence must be persisted and enforced monotonically.

- **HF-2 — AuthorityInputGateway is not explicitly required to be workload-attested as root-sensitive.**  
  AIEP-1 constrains the authority evaluator, and v6 I024 defines the AuthorityInputGateway, but the gateway itself is not clearly bound to a WorkloadAttestation/registry identity as a root-sensitive component. A compromised or counterfeit gateway could return unregistered values, forge AuthorityReadSet entries, or launder authority inputs. The gateway and its broker FDs must be attested and included in the authority input closure proof.

- **HF-3 — GGS-2 lacks explicit configuration/replica rotation continuity.**  
  GGS-2 adds hard state and namespace-root mirroring, but the design does not specify joint-consensus or equivalent hard-state-transfer semantics for GGS replica replacement or GGS configuration rotation. A new GGS replica could lack the committed namespace/auth-root history, or old GGS configuration certificates could be accepted after rotation.

- **HF-4 — QualifiedEffectExecutor revocation/compromise is not specified.**  
  EESM-1 defines effect states and reconciliation, but it does not define what happens when a QualifiedEffectExecutor is revoked, compromised, or loses workload attestation. In-flight `INTENT_COMMITTED` or `DISPATCHING` effects could continue, receipts could be forged, or compensation could be skipped. Executor revocation must freeze effect dispatch and require reconciliation/compensation.

- **HF-5 — `decision_preseal_digest` is incomplete for authority-bearing time context.**  
  v7 I043 includes candidate/action/tenant scope, governance snapshot, AuthorityReadSet, revocation head, runtime attestation, and effect class. It omits T0/MTR high-water, LAS configuration generation, MTR-mirrored revocation high-water for sensitive use, runtime identity mode, and exact effect ID. Final seal verification may catch some mismatches, but the preseal digest is the nonce-ledger key and must bind the complete authority context.

- **HF-6 — SPM-1 generator provenance is not self-protected.**  
  SPM-1 records a generator RuntimeManifest digest, but no CSM-bound generator identity or attestation requirement is stated for the generator itself. A compromised or drifted generator could emit schema elements with plausible-looking SPM-1 entries. RG-1 could pass while provenance is counterfeit.

D. Medium findings

- **M-1 — Migration destination policy freshness is not explicitly sealed at commit.**  
  RequalificationProof includes pre/post policy snapshot digests, but the design does not explicitly require the destination policy at migration commit to equal the policy used in the proof. `COMMIT_WITH_SEAL` may catch this if the policy stream is sealed, but the migration contract should state it directly.

- **M-2 — CSM “applicable scope” resolution is not exact.**  
  v7 I024 requires exactly one ACTIVE CSM entry for `semantic_input_id + applicable scope`, but the scope-resolution algorithm is not fully specified. Ambiguous scope could produce multiple active entries or unintended fallback.

- **M-3 — MTR challenge consumption persistence is not specified.**  
  The challenge is single-use, but where the ISSUED/CONSUMED state is stored and how it resists verifier rollback is not explicit. This overlaps HF-1 but should be closed independently.

- **M-4 — Compensation recursion/uncertainty is not fully bounded.**  
  EESM-1 defines `COMPENSATION_REQUIRED` and `COMPENSATED`, but not what happens if compensation itself becomes `UNCERTAIN` or `FAILED_FINAL`. The state machine should remain non-fabricating and visible.

- **M-5 — GCP v7 rejection vectors are deterministic but not linked to a full updated reference-vector manifest.**  
  The inherited v5 reference digests remain, and v7 adds rejection vectors. The packet should explicitly confirm that no inherited canonical-output vector changed under v7.

E. MTR/T0/GGS assessment

MTR freshness is improved by live challenge-response and fail-closed outage behavior, but the reservation operation is under-authenticated, and response-sequence rollback is not explicitly blocked. T0 activation binding through reservation, BTW inclusion, and exact digest match is directionally correct. GGS-2 hard-state and namespace-root mirroring are strong, but GGS configuration/replica rotation continuity is missing. **Not closed.**

F. LAS rotation/concurrency assessment

LAS-3 joint-consensus rotation, activation index, hard-state continuity, StreamHeadMap transfer, and idempotency-state transfer are well specified. Old-config-only certificates after activation are rejected. I did not find a material blocker in the LAS rotation design itself, provided the machine-readable schemas exactly encode the activation-index and hard-state proofs. **Bounded pass subject to schema freeze.**

G. Identity/AIEP/semantic-closure assessment

ACTIVE-only quorum domains, canonical subject registry, alias collision handling, and one-subject-per-diversity-slot rules are strong. AIEP-1 broker-only execution is directionally correct, but the gateway and broker FD path require explicit workload attestation and authority-input closure. CSM lifecycle and exactly-one-active resolution are strong. **High findings remain.**

H. Revocation/runtime/GCP assessment

Universal revocation head, lower-risk rollback protection, UNREVOKE interval preservation, UNATTESTED_RUNTIME restrictions, and workload-attestation downgrade are well designed. GCP v7 rejection vectors close NFC collision, noncharacter, `sys:` namespace, and extension-map shadowing cases. No critical blocker found here beyond the need to preserve inherited GCP reference vectors. **Bounded pass.**

I. Provenance/effect/migration/review-presentation assessment

SPM-1/RG-1 provenance is strong in principle, but generator provenance is not self-protected. EESM-1 correctly separates intent from completion and requires reconciliation, but executor revocation is missing. Migration object completeness is strong, but stale destination policy should be explicitly sealed. RPS-1 correctly defaults unknown display fields to `REVIEW_SEMANTIC`. **High and medium findings remain.**

J. Recovery/trust-loss/time-context assessment

TRUST_PATH_UNAVAILABLE versus TRUST_DOMAIN_UNRECOVERABLE is well distinguished. No-quorum recovery remains blocked, and emergency root substitution is prohibited. New-constitution non-inheritance is preserved. Time-context binding is directionally correct, but `decision_preseal_digest` is incomplete for full authority context. **High finding remains.**

K. Guard catalog/fault-proof/mechanism-proof assessment

The consolidated table contains G001–G081, positive controls, and FP0–FP6 classes. Mechanism-proof rules address constant-reject and earlier-guard masking. However, the packet omits canonical v4 case semantics for G001–G025/V4 cases. Therefore inherited case strength and fault-proof appropriateness cannot be fully verified. **Insufficient evidence for the inherited v4 portion; otherwise directionally strong.**

L. Over-governance/deadlock assessment

The design intentionally favors integrity over liveness and accepts permanent fail-closed states when the lawful trust root is gone. No liveness workaround is permitted to invent a weaker trust root. This is consistent with the stated trust model. **Accepted as bounded deadlock behavior.**

M. Minimal required changes before executable-schema freeze

1. Add authorization preconditions to `RESERVE_T0_SUCCESSOR`: require lawful predecessor T0/EBA threshold proof, exact successor manifest digest, and reject unauthorized reservations.
2. Persist and enforce MTR response-sequence high-water and challenge consumption; include in MTRFreshnessAttestation acceptance and VerifiedStateSeal.
3. Include canonical v4 design/case semantics for G001–G025 in the review packet, or explicitly re-freeze all inherited V4 cases in a v7 addendum.
4. Bind AuthorityInputGateway and broker FDs to WorkloadAttestation/CSM as root-sensitive components.
5. Add GGS-2 configuration/replica rotation continuity: joint consensus or T0 successor, hard-state transfer, and MTR high-water for namespace/auth roots.
6. Add QualifiedEffectExecutor revocation/compromise state machine, including in-flight intent freeze and compensation/reconciliation.
7. Complete `decision_preseal_digest` to include T0/MTR high-water, LAS config generation, MTR-mirrored revocation high-water for sensitive use, runtime identity mode, and exact effect ID.
8. Add SPM-1 generator identity/attestation and prevent generator drift from forging provenance.
9. Seal destination policy snapshot at migration commit and reject stale destination policy.
10. Specify exact CSM applicable-scope resolution.

N. Final bounded statement

This review grants no authority.  
R8 v7 remains **NOT_IMPLEMENTED**.  
Executable-schema freeze remains **BLOCKED** unless the design gate closes.  
PR #39 and PR #40 remain **NON_AUTHORITATIVE**.  
Unresolved material findings block implementation start.