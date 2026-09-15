# V16 Slice 2 Internal Adversarial Review 002

Review class: **INTERNAL_ADVERSARIAL_RECORD**

Reviewed repaired candidate: `0d01a0500b1902036b25bf29ce77cd2f883b748c`

Construction run: `34988812900` — 45/45 mandatory tests PASS.

The 45-test PASS remains preserved as construction evidence. This review is not independent and creates no authority transition.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## IAR2-C-02 — repaired wrapper is bypassable through the still-public predecessor API

Severity: **Critical**

Affected surfaces:

- `review_safe_evidence_v16_independence.py`
- `review_safe_evidence_v16_independence_v2.py`
- current Slice 2 workflow/test universe

Concrete false-green path:

The V2 wrapper correctly hard-blocks global promotion/authority while real-world completeness is unproven, but the predecessor module remains directly callable in the same runtime/package. Its public functions still return the exact unsafe generic states identified in IAR1:

- disconnected domains can produce `promotion_blocked=false`;
- a structurally clear candidate-control result can produce `promotion_blocked=false`;
- registry-key resolution can produce `authority_admissible=true` and `promotion_blocked=false`.

The current V2 workflow deliberately re-runs the predecessor 30 tests, including tests that affirm those predecessor semantics. Therefore a caller can bypass the repaired wrapper simply by importing/calling the predecessor API. There is no dispatch/gateway mechanism that makes the V2 wrapper the only load-bearing route.

Why this remains Critical:

The original Critical was not merely that a safe API was absent; it was that the system exposed a generic false-green promotion/authority signal while qualification remained unproven. Leaving that same signal available on a parallel public path preserves the false-green mechanism.

Required narrow repair:

- repair the current predecessor/core API itself so generic `promotion_blocked` remains true and generic `authority_admissible` remains false under the Slice 2 construction boundary;
- expose separate explicitly named structural/within-graph fields for construction use;
- update current tests/manifests to reject the old false-green expectations;
- preserve the historical pre-repair source/result through Git history and the existing construction evidence rather than preserving an executable unsafe downgrade route;
- bind the repaired core blob into the V2 validator bundle/workflow.

## IAR2-C-03 — graph/registry bootstrap threshold counts distinct domain labels, not graph-derived independent non-candidate roots

Severity: **Critical**

Affected functions/surfaces:

- `review_safe_evidence_v16_independence._verify_graph_signatures`
- bootstrap-root/domain interaction with `CONTROL_DOMAIN_GRAPH`
- combined registry authority resolution in `review_safe_evidence_v16_independence_v2`

Concrete false-green paths:

1. Two bootstrap signing roots can use different `control_domain_id` strings while the signed control graph itself says those domains share a load-bearing ancestor. `_verify_graph_signatures` still counts both domains toward threshold because it only counts distinct root-domain strings; it does not apply the graph's ancestry-derived independence rule to the graph signers.

2. A graph can classify a bootstrap root domain as candidate-controlled, directly or through ancestry, yet that root's signature can still count toward graph threshold. The bootstrap trust validator only checks the earlier pinned `candidate_control_domain_ids`; it does not use the newly signed graph's expanded/derived candidate-control relation.

3. Bootstrap root control domains are not required to appear in the graph at all. In that case the mechanism can claim threshold-authenticated ancestry state without being able to derive the signing roots' own candidate-control/shared-ancestor status.

4. Combined registry authority relies on Slice 1 registry threshold authentication, which also counts distinct bootstrap domain labels. The V2 combined resolver does not re-check the registry head's authenticating bootstrap domains against the authenticated graph for candidate control or shared ancestry.

This is a direct within-model structural false green, not merely the already-disclosed real-world completeness limitation: the authenticated graph may itself contain evidence that the roots are non-independent/candidate-controlled, yet the threshold logic ignores it.

Required narrow repair:

- require bootstrap signing-root control domains used for Slice 2 graph authentication to be represented in the graph;
- derive candidate control and shared ancestry for those root domains from the graph before counting quorum;
- only count a quorum that contains at least the configured threshold of non-candidate, pairwise-independent root control domains;
- do the same at the combined registry-authority boundary for bootstrap domains authenticating the current registry state;
- fail closed when root-domain graph representation/independence is unknown;
- add adversarial tests for shared-root ancestry, candidate-controlled signing roots, absent root domains, and registry threshold relying on a graph-disqualified bootstrap root.

## Residual observations

The IAR1 repairs for exact Slice 2 validator/profile binding, common generation equality, canonical record-type role derivation and global blocking work as tested on the V2 route. They are not revoked by this review.

The following disclosed boundaries remain expected and are not reclassified here: source-byte measurement is self-measurement, graph real-world completeness is unproven, trust/currentness-head provisioning is out-of-band, and the common generation equality rule is not the final authenticated governance-generation mechanism.

## Disposition

`V16_SLICE2_CONSTRUCTION_HISTORY = PRESERVED`

`V16_SLICE2_IAR1_REPAIRS = PARTIALLY_EFFECTIVE`

`V16_SLICE2_INTERNAL_REVIEW = CHANGES_REQUIRED`

`V16_SLICE2_NEW_CRITICAL_FINDINGS = 2`

`V16_SLICE2_FREEZE_ALLOWED = false`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED = false`

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
