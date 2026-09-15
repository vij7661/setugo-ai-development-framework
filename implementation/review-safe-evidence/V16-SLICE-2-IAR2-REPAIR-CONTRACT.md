# V16 Slice 2 IAR2 Repair Contract

Status: **CONSTRUCTION REPAIR CONTRACT / NON-AUTHORITATIVE**

Predecessor repaired candidate: `0d01a0500b1902036b25bf29ce77cd2f883b748c`

Predecessor internal review: `V16-SLICE-2-INTERNAL-ADVERSARIAL-REVIEW-002.md`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## R1 — remove executable downgrade path

The current `review_safe_evidence_v16_independence.py` core must itself enforce the global Slice 2 construction boundary:

- every generic `promotion_blocked` remains `true` while real-world graph/control/independence completeness is unproven;
- generic `authority_admissible` remains `false`;
- bounded structural outcomes use explicit names such as `construction_independence_satisfied`, `construction_candidate_control_clear`, and `authority_structurally_admissible_within_authenticated_graph`;
- the V2 wrapper must consume those structural fields rather than relying on a globally admissible predecessor result.

Historical unsafe semantics remain preserved by Git history and construction-evidence records, not by a live downgrade API.

## R2 — bootstrap graph quorum must be graph-derived independent and non-candidate

A cryptographically valid bootstrap signature may count toward graph threshold only when its root control domain:

1. is represented in the signed control-domain graph;
2. is not candidate-controlled under the graph's own ancestry/candidate-domain semantics; and
3. participates in a threshold-sized set of pairwise-independent signing-root domains under the graph's ancestry relation.

Distinct strings alone are insufficient. Unknown/absent root-domain representation fails closed. The authenticated-domain result must report the qualified independent quorum rather than every cryptographically valid signer label.

## R3 — combined registry authority must requalify registry bootstrap quorum through the graph

When registry authority is combined with graph-derived candidate-control/independence, every registry snapshot relied upon by the chain must retain a threshold of bootstrap signing-root domains that are represented, non-candidate and pairwise independent under the current additive control graph. A registry chain whose cryptographic threshold depends on a graph-disqualified root is structurally non-admissible.

This does not replace the later dedicated governance-generation/currentness mechanism.

## Mandatory adversarial additions

The next candidate must prove at least:

- direct core disconnected-domain independence still leaves global promotion blocked;
- direct core not-candidate-controlled result still leaves global promotion blocked;
- direct core registry authority can be structurally satisfied but generic authority remains false and promotion remains blocked;
- direct core registry-key independence remains globally blocked;
- graph root domains absent from graph cannot satisfy bootstrap threshold;
- two cryptographically valid graph signers with a shared load-bearing ancestor cannot satisfy independent threshold;
- a graph signer that is candidate-controlled by the signed graph cannot count toward threshold;
- a valid independent non-candidate root quorum still structurally authenticates the graph;
- registry chain authentication relying on a root that is candidate-controlled by the graph is rejected by combined authority resolution;
- registry chain authentication relying on roots that share a graph ancestor is rejected by combined authority resolution;
- the V2 exact-profile/artifact binding tests remain green after the core repair;
- no PASS path claims implementation/runtime/scientific/effect authority.

## Preserved boundaries

Real-world graph completeness, root/account ownership, external trust/currentness provisioning, independent runtime source measurement and final authenticated governance-generation currentness remain unproven.

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
