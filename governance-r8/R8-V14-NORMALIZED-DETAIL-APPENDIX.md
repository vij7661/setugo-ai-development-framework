# R8 v14 — Normalized Load-Bearing Detail Appendix

Status: **INTERNAL_NORMALIZATION_ARTIFACT — NON_AUTHORITATIVE — NCG-1 INPUT**
Authority effect: **NONE**

Purpose:
Carry forward load-bearing inherited constants and exact behavioral constraints that would otherwise be lost in a high-level normalized view.

If this appendix conflicts with a canonical source design, NCG-1 must fail until adjudicated.

## 1. Constitutional trust / EBA

- Reference EBA population: 5 offline trust officers.
- Ordinary root/bootstrap threshold: 3-of-5 where inherited rule requires EBA threshold.
- T0 successor manifest: 4-of-5 active EBA officers across at least 3 active admin domains.
- Newly created/reactivated admin domain cannot sign the T0 successor that creates/reactivates it.
- Only ACTIVE admin domains count toward quorum/diversity.
- Admin-domain aliases cannot manufacture diversity.
- Root-sensitive wildcards in ControllerAttestation constitution/tenant/role-instance scope are prohibited.

Trace: v4 T0 External Trust Axiom; v5 T0 successor; v7 admin-domain lifecycle.

## 2. MTR / freshness

Authority-bearing MTR challenge:
- random 256-bit challenge;
- verifier_instance_id;
- trust_domain_id;
- purpose_class;
- expected minimum T0 generation;
- expected minimum BTW tree size;
- expected minimum EBA revocation sequence;
- local monotonic issuance tick.

MTR response binds:
- exact challenge/verifier/domain/purpose;
- current T0 generation + manifest digest;
- current BTW tree size + root hash;
- current EBA revocation high-water;
- current T0-domain lifecycle sequence;
- monotonic MTR response sequence;
- MTR configuration generation.

Freshness:
- live challenge required for authority-bearing use;
- accepted once;
- reference maximum response age: 30 seconds verifier-monotonic time;
- no stale-token authority fallback;
- MTR outage -> MTR_UNAVAILABLE.

Trace: v7 MTRF-1; v8 response/high-water refinements.

## 3. BTW

- BTW verification keys/policy/initial trusted STH are T0-pinned.
- verifier preserves highest accepted tree_size/root_hash.
- smaller tree or missing required consistency proof -> reject.
- same tree size with different root -> BTW_EQUIVOCATION.
- authority bootstrap/anchor operations freeze on equivocation pending lawful recovery.

Trace: v5/v6 BTW rules.

## 4. GGS-3

- 3 replicas.
- 2-of-3 majority.
- replicas use distinct qualified admin domains.
- rollback-resistant hard state includes:
  - highest seen term;
  - vote state;
  - highest committed genesis index;
  - last committed genesis digest;
  - constitution namespace root;
  - bootstrap authorization state root;
  - configuration generation.
- stale/rolled-back replica is non-voting.
- constitution namespace and bootstrap authorization consumption occur atomically.
- one constitution_id can acquire only one committed genesis head.

Trace: v6 GGS-1; v7 GGS-2; v8-v11 GGS-3 rotation.

## 5. LAS-3

- 3 replicas.
- 2-of-3 ordinary majority.
- rollback-resistant hard state includes:
  - highest_seen_term;
  - vote_for_current_term;
  - highest_committed_log_index;
  - highest_applied_log_index;
  - last_committed_entry_digest;
  - configuration generation.
- StreamHeadMap and idempotency ledger are replicated authority state.
- non-commutative authority append atomically validates predecessor and advances head.
- authority-bearing streams have no commutative bypass under current reference design.
- during JOINT rotation, every governed authority/configuration commit requires both old majority and new majority.
- after activation index, old-config-only certificates are invalid.

Trace: v6 LAS-2; v7/v9 LAS-3; v10-v12 STC/RBP.

## 6. Rotation barrier / STC

ROTATION_PREPARE:
- commits barrier B;
- freezes covered authority writes.

STC contains at minimum:
- old/new configuration identity;
- barrier/snapshot index;
- committed log prefix digest;
- highest term/committed/applied index;
- last committed entry digest;
- state-root/StreamHeadMap root;
- idempotency ledger root;
- prior certificate-chain digest;
- GGS namespace/authorization roots where applicable;
- named semantic heads covered by the rotating authority state.

One barrier -> one rotation:
- same rotation/config/STC retry = idempotent;
- same rotation ID + changed config/STC = IDEMPOTENCY_CONFLICT;
- different rotation ID on reserved barrier = BARRIER_ALREADY_RESERVED;
- contradictory valid reservation certificates = STC_EQUIVOCATION;
- ABORT permanently closes B.

Trace: v10 STC-1; v11 STC-2/RBP; v12-v14 barrier semantics.

## 7. GCP canonicalization

Effective canonicalization constraints include:
- no insignificant whitespace in canonical output;
- absent != null;
- defaults are applied before canonical signing/digest and no post-digest defaults;
- object keys must already be NFC;
- duplicate keys after canonical interpretation reject;
- key collisions after NFC normalization reject;
- unpaired surrogates reject;
- Unicode noncharacters reject in authority-bearing strings/keys;
- ordered arrays preserve order;
- set-typed arrays sort canonically and reject duplicates;
- signed integers use frozen signed-int64 lexical/range rules;
- extension maps are schema-declared, included in digest, cannot shadow standard fields, and cannot use reserved `sys:` namespace.

Trace: v5/v6 GCP-1 closure.

## 8. Workload/runtime identity and AIEP

Root-sensitive/terminal authority components require qualified workload/runtime identity when the constitutional mode requires it.

AIEP reference constraints:
- read-only root filesystem;
- no arbitrary mutable environment;
- no direct DB/cloud/provider credentials;
- no general external network/DNS route;
- only approved broker/attestation/sequencer channels;
- dynamic code/plugin loading not in RuntimeManifest prohibited.

UNATTESTED_RUNTIME:
- explicit state;
- can perform only permitted non-authority/read-only work;
- cannot act as root/terminal authority evaluator, strong evidence producer, or other roles requiring runtime identity.

Trace: v6/v7/v8 runtime/AIEP rules.

## 9. Revocation

- revocation history is append-only.
- UNREVOKE is a new event; prior revoked interval remains revoked.
- root/terminal-sensitive revocation high-water protected by MTR.
- every authority-bearing decision uses current LAS revocation head.
- producer/executor/reviewer validity is evaluated at effective sequence.
- post-effective evidence/action by revoked identity is invalid.
- retrospective invalidation requires an explicit governed event.

Trace: v5-v8 revocation rules.

## 10. Time

Reference authority time:
- multiple independent qualified time authorities;
- inherited reference threshold: 2-of-3;
- single-use random 256-bit challenge/nonce;
- nonce state is LAS-governed;
- source status evaluated at the relevant sequence;
- replay of consumed nonce rejects.

Time proof binds the DecisionPresealContext digest, not a caller-controlled label.

Trace: v3-v8 time rules.

## 11. Review independence

Constitutional human review:
- signed by active attested human/controller identity;
- binds exact candidate/snapshot/packet digest;
- independent from proposer under canonical identity/domain rules.

Provider/model review:
- provider/service/runtime qualification is bounded;
- provider-internal undisclosed memory is outside proof;
- model/provider review alone cannot replace a required human constitutional channel.

Trace: v6 Channel H/X.

## 12. Evidence

Strong evidence:
- requires qualified producer and matching execution/runtime proof;
- exact input/output derivation binding;
- weak evidence cannot become strong by byte copying/repackaging.

Evidence promotion:
- missing or contradictory mandatory evidence blocks;
- history/retractions are preserved;
- derived claims are individually re-evaluated after source invalidation.

Trace: EXP-J; v5-v7 QEP/evidence transitions.

## 13. Tenant/migration

Stable authority identity:
`constitution_id + tenant_uuid + object_uuid`.

Migration:
- exact source/destination namespaces;
- complete object map;
- policy/scope comparisons;
- destination-policy freshness;
- explicit widening flags;
- fresh destination authorization for widening;
- omitted later-referenced source object -> MIGRATION_OBJECT_UNBOUND.

Cross-constitution import:
- no inherited terminal/promotion/root authority;
- imported artifacts are historical/external evidence until requalified.

Trace: v5-v8 tenant migration.

## 14. Recovery / trust loss

Recovery requires:
- predeclared trigger schema;
- current RecoveryContext;
- random single-use recovery nonce;
- exact trigger/evidence binding;
- lawful recovery quorum;
- current trust state.

Replay of approvals/evidence under another state/context rejects.

Trust loss:
- unavailable lawful root/recovery path -> TRUST_PATH_UNAVAILABLE;
- authoritative TRUST_DOMAIN_UNRECOVERABLE declaration only if a still-lawful recovery quorum can commit it;
- no lawful quorum -> remain blocked indefinitely;
- new constitution inherits no authority.

Trace: v6/v7 recovery/trust loss.

## 15. Effect state

External effect states include:
- INTENT_COMMITTED;
- DISPATCHING;
- ACKNOWLEDGED_UNVERIFIED;
- SUCCEEDED_RECONCILED;
- FAILED_FINAL;
- UNCERTAIN;
- COMPENSATION_REQUIRED;
- COMPENSATED.

Only SUCCEEDED_RECONCILED is success evidence.

Retries reuse one effect idempotency key.

Provider success response alone is insufficient without qualified reconciliation.

Trace: v7-v9 EESM / reconciler rules.
