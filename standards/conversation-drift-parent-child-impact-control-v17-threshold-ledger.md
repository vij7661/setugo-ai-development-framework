# Workflow Drift and Parent-Child Impact Control — V17 Threshold-Ledger Hardening

Status: **PROPOSED V17 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

## V17-C01 — Exact base binding

V17 is an additive hardening layer over exact V16 candidate:

- V16 candidate commit: `a93cdf692dd165cb72d12d704e89787d0214676a`
- V16 threshold-atomicity blob: `9968bbbecf922113ca699cf5ba56172b8a1241e1`
- V16 threshold/semantic-assurance map blob: `de598a0810ed3cd4bb9526389576fc00f7f0482b`
- V16 falsification extension blob: `552728b271d2a27b5f59a812425e97012d559c47`

V5–V16 remain preserved source/history artifacts. V17 narrows only threshold consumption, cross-gate uniqueness, NRVA/RPAA joint independence, canonical conflict precedence/corpus liveness, packet-generation anti-fork, and endpoint-export replay controls.

V17 is design/preregistered falsification material only. It is not runtime implementation evidence.

## V17-C02 — One admissible qualification-to-threshold path

For any review intended to contribute to a qualifying threshold, the V16 alternate `fresh live recheck then later threshold commit` path is removed.

The only admissible path is one authoritative atomic transaction/consensus operation that:

1. reads the exact `ReviewQualificationSnapshot` and all bound predicate versions;
2. revalidates every current predicate inside the same serializable/linearizable decision boundary;
3. verifies the snapshot has not been consumed, superseded, or invalidated;
4. writes the `ReviewThresholdRecord`;
5. writes the durable threshold-consumption uniqueness record;
6. advances the authoritative threshold sequence;
7. commits all effects together or none.

No detached proof of “no intervening transition,” timestamp freshness, prior successful recheck, chat declaration, or external observer statement may substitute for the atomic commit.

Any state change that wins ordering before the commit is observed by the same transaction/consensus decision and causes revalidation. Any conflicting concurrent change causes retry from a fresh snapshot; it cannot be ignored.

Failure emits `REVIEW_THRESHOLD_ATOMIC_COMMIT_FAILED` and contributes zero.

## V17-C03 — Durable ReviewThresholdConsumptionLedger

A root-governed append-only `ReviewThresholdConsumptionLedger` is authoritative for review-count consumption.

Each committed record binds:

- reviewer evidence ID/digest;
- review qualification snapshot ID/digest;
- candidate/projection/packet ID and generation;
- gate ID and gate-policy version;
- review scope ID;
- evidence class;
- reviewer role/identity binding;
- idempotency key;
- atomic commit sequence;
- predecessor ledger digest;
- result `COUNTED | REJECTED | DUPLICATE | REUSE_NOT_AUTHORIZED`.

The authoritative store enforces durable uniqueness on the governed consumption key in the same transaction as the threshold count.

At minimum, duplicate submission of the same review evidence to the same gate/policy/scope cannot increment the threshold more than once.

Retries MUST reuse the same idempotency key and resolve to the original result.

## V17-C04 — Cross-gate review reuse is explicit and default-deny

A review counted for one gate, gate-policy version, or review scope does not silently become eligible for another.

RGA governs `ReviewEvidenceReusePolicy`.

Default: `CROSS_GATE_REUSE_DENIED`.

Cross-gate reuse is allowed only when the policy explicitly binds:

- exact review evidence class and scope;
- allowed source gate(s) and destination gate(s);
- exact policy versions;
- candidate/projection compatibility rule;
- reviewer-independence requirements;
- maximum reuse count;
- reason and expiry;
- independent approval required by the governing review policy.

Absent an exact allow rule, a second gate consumption emits `REVIEW_THRESHOLD_REUSE_NOT_AUTHORIZED` and count remains zero.

No reuse policy may retroactively legalize an earlier rejected duplicate/reuse attempt.

## V17-C05 — Root-governed NRVA registry and joint-independence proof

RGA governs a `NormativeReExpressionVerifierRegistry` containing active NRVA principals, keys, algorithm/version, authorization scope, activation/sunset sequence, credential/recovery/identity/HSM/cloud-root domains, aliases, beneficial ownership, and administrative controllers.

Every qualifying re-expression requires a current signed `NRVAIndependenceRecord` and a `NRVA_RPAA_JointIndependenceProof`.

The joint proof evaluates both declared and independently sourced control facts and MUST reject shared or transitive control sufficient to compromise both NRVA and RPAA, including:

- shared credential administrators;
- recovery administrators;
- identity-provider administrators;
- HSM/KMS/cloud-root controllers;
- service-account aliases;
- beneficial ownership/control;
- common platform super-admin domains;
- root-threshold-capable combinations;
- delegated or emergency administrative paths.

Formal records that omit a discovered shared control path are conflicting evidence, not a PASS.

Failure emits `NRVA_RPAA_JOINT_INDEPENDENCE_REJECTED`.

## V17-C06 — NRVA independence is consumed atomically

NRVA registry version, NRVA independence record, and NRVA/RPAA joint-independence proof are bound into the exact `ReviewQualificationSnapshot` and revalidated inside the V17 atomic threshold transaction.

If NRVA authority/control state changes before atomic commit, the old snapshot cannot be consumed and count remains zero.

## V17-C07 — Canonical semantic conflict precedence

The canonicalization system has separate evidence for:

- `DISTINCT_OBLIGATIONS` / collision-resistance classification;
- `SEMANTICALLY_EQUIVALENT` / equivalence-acceptance classification.

If active evidence for the same clause pair conflicts, no precedence rule may silently choose the more permissive result.

Conflict yields `CANONICAL_SEMANTIC_CONFLICT` and qualification is `INSUFFICIENT_EVIDENCE` until the governed canonicalizer/corpus is revised and the affected candidate projection is recomputed under a new proof generation.

No reviewer, candidate author, RPAA, or NRVA may override a conflict by assertion.

A conflict is preserved as evidence; later repair does not rewrite the earlier result.

## V17-C08 — Canonical positive-corpus integrity and liveness

RGA governs `CanonicalSemanticCorpusRegistry` binding:

- corpus ID/version/digest;
- collision-resistance fixtures;
- semantically equivalent paraphrase fixtures;
- obligation-strength fixtures;
- adversarial ambiguity fixtures;
- source/provenance of fixtures;
- independent corpus audit result;
- activation/sunset sequence;
- freshness/revalidation policy;
- contamination/retraction state.

A stale, superseded, contradicted, or integrity-failed corpus cannot support qualification.

Failure emits `CANONICAL_SEMANTIC_CORPUS_STALE`.

Discovery of a new canonicalization evasion triggers corpus expansion and invalidates affected qualification evidence until revalidated.

## V17-C09 — Endpoint export replay remains commit-exact even with identical content

An authoritative endpoint registry export is qualified only for the exact candidate commit recorded in the export.

Identical Git tree, schema version, registry digest, tuple-set digest, or source content does not authorize replay to another commit.

If a different commit requires the same endpoint export, the authority must issue a distinct exact-commit-bound attestation or a separately governed candidate-equivalence attestation explicitly permitted by policy. No implicit content-equivalence substitution exists.

Wrong-commit replay emits `REVIEW_ENDPOINT_EXPORT_REPLAY_REJECTED`.

## V17-C10 — PacketGenerationLedger prevents reset/fork

A root-governed append-only `PacketGenerationLedger` is authoritative for packet generations.

Only the first packet generation in a governed lineage may have no predecessor.

Every later packet generation MUST bind the current predecessor packet digest and monotonically advance the generation sequence for the exact candidate/projection lineage.

Creating a null-predecessor reset, sibling fork, reused generation number, or hidden alternate lineage after a predecessor/superseding packet exists emits `REVIEW_PACKET_GENERATION_FORK_REJECTED`.

A fork cannot become current merely because its packet contents are otherwise valid.

## V17-C11 — Qualification proof-view completeness

Reviewer-safe proof view MUST explicitly expose predicates for:

- atomic threshold-commit protocol;
- threshold-consumption ledger currentness;
- cross-gate reuse policy/result;
- NRVA registry currentness;
- NRVA/RPAA joint-independence status;
- canonical semantic-conflict status;
- canonical corpus currentness;
- endpoint-export exact-commit binding;
- packet-generation anti-fork currentness.

Missing values are `NOT_PRESENT`, never implicit PASS.

## V17-C12 — Prior positive-control tightening

WDPC-237, WDPC-250, and WDPC-257 qualifying positives are narrowed to require all active V17 predicates, including atomic threshold commit, durable consumption uniqueness, reuse-policy compliance, current NRVA joint independence, conflict-free canonical evidence, current canonical corpus, exact-commit endpoint export, and anti-fork packet generation.

## V17-C13 — New endpoints

V17 adds owner-bound endpoint schemas:

- `REVIEW_THRESHOLD_ATOMIC_COMMIT_FAILED`
- `REVIEW_THRESHOLD_REUSE_NOT_AUTHORIZED`
- `NRVA_RPAA_JOINT_INDEPENDENCE_REJECTED`
- `CANONICAL_SEMANTIC_CONFLICT`
- `CANONICAL_SEMANTIC_CORPUS_STALE`
- `REVIEW_ENDPOINT_EXPORT_REPLAY_REJECTED`
- `REVIEW_PACKET_GENERATION_FORK_REJECTED`

V17 narrows enforcement of:

- `REVIEW_THRESHOLD_SNAPSHOT_STALE`
- `REVIEW_QUALIFICATION_EVIDENCE_INCOMPLETE`
- `NORMATIVE_REEXPRESSION_VERIFIER_INDEPENDENCE_REJECTED`
- `CANONICAL_EQUIVALENCE_FALSE_NEGATIVE`
- `REVIEW_PACKET_GENERATION_STALE`
- `REVIEW_ENDPOINT_TUPLE_MISMATCH`

## V17-C14 — Freeze rule

V17 cannot freeze for execution while unresolved Critical/High design findings remain.

No qualifying review may count through a non-atomic recheck/commit path, duplicate or unauthorized cross-gate reuse, stale/colluding NRVA assurance, unresolved canonical semantic conflict, stale canonical corpus, wrong-commit endpoint export, or forked packet generation.

This document grants no merge, release, production, qualification, adjudication, or terminal authority.
