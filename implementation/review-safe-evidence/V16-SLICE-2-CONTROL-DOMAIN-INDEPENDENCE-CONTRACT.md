# V16 Slice 2 — Authenticated Control-Domain Ancestry and Independence Contract

Status: **CONSTRUCTION IMPLEMENTATION / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## 1. Scope

Slice 2 implements the control-domain/independence portion of the frozen V16 successor-remediation scope. It consumes the frozen Slice 1 construction foundation at:

- commit `36f22a35ff57b6994d55c705c08686609276ddb3`;
- tree `cc0a4e4b6ddb8d8fd8693d05eafde5ce25514602`;
- freeze ref `freeze/review-safe-evidence-v16-slice1`.

Slice 2 replaces caller-declared strings such as `verifier_independence_result="INDEPENDENT"`, `candidate_controlled=false`, and format-only `ancestry_graph_digest` with a deterministic computation over a bootstrap-threshold-authenticated control-domain graph.

It does not claim that repository data alone proves real-world corporate ownership, cloud-account ownership, credential custody, hidden common administrators, or external bootstrap/currentness provisioning. Those remain independent-review/qualification boundaries.

## 2. Authenticated control-domain graph

A `CONTROL_DOMAIN_GRAPH` snapshot binds:

- candidate ID;
- graph ID and governance generation ID;
- exact sequence and predecessor graph digest;
- bootstrap trust-set ID/digest;
- exact domain-node set;
- exact parent/control-ancestor edges;
- candidate-domain set; and
- bootstrap threshold signatures.

The graph content receives a canonical SHA-256 digest. Distinct pinned bootstrap-root control domains sign that exact digest using an identity/domain-separated Ed25519 signature message.

A `PinnedControlDomainGraphHead` independently supplies the expected current graph ID, candidate, sequence, generation and digest. The code verifies relation to this pin but does not prove pin provisioning/freshness.

## 3. Graph semantics

Each domain node has one canonical `control_domain_id` and zero or more canonical `parent_control_domain_ids`. Parents represent load-bearing control/ownership ancestry. The graph must be a DAG; unknown parents, self-edges, duplicate IDs and cycles fail closed.

Ancestry closure includes the subject domain itself. Therefore aliases through a shared direct domain cannot count as independent.

For the current Slice 2 epoch, graph history is conservative/additive:

- prior domain IDs cannot disappear;
- prior parent edges cannot be removed;
- candidate-domain membership cannot be removed;
- graph updates require an exact predecessor digest, next sequence and new generation ID.

A legitimate need to remove a previously asserted load-bearing relation requires a separately anchored graph epoch until a later governed correction protocol exists. This prevents an update from manufacturing independence by deleting ancestry.

## 4. Deterministic independence

`assess_domain_independence(A, B)` derives transitive ancestry from the authenticated current graph. It does not accept a caller-provided result.

- if A/B are absent or graph/currentness is invalid: `INDEPENDENCE_UNPROVEN` and blocking;
- if ancestor closures intersect: `NOT_INDEPENDENT` and blocking;
- otherwise: `INDEPENDENT_WITHIN_AUTHENTICATED_GRAPH`.

The returned shared-ancestor set is derived, not caller supplied.

## 5. Candidate control

Candidate control is derived from graph ancestry. A subject domain is candidate-controlled when its ancestry closure intersects the union of ancestry closures for the bootstrap-authenticated candidate-domain set.

The candidate-domain set is part of signed graph state and is append-only within this epoch. A caller cannot neutralize candidate control by setting `candidate_controlled=false`.

## 6. Registry-backed issuer resolution

Slice 2 resolves operational authority from the Slice 1 bootstrap-authenticated governance-key registry:

1. validate the supplied registry chain;
2. require exact match to the pinned current registry head;
3. resolve the current active `key_id` and issuer/control-domain identity;
4. require the requested role to be present in signed registry state;
5. require that control domain to exist in the authenticated current control-domain graph; and
6. derive candidate-control/independence from that graph.

No caller-provided issuer domain, role, `candidate_controlled` flag, or independence result can override the authenticated registries.

## 7. Stopping rule

Slice 2 construction may advance only after stable mandatory adversarial tests prove at minimum:

- bootstrap threshold and root-identity binding;
- graph-digest tamper rejection;
- exact current-head binding and stale-prefix rejection;
- unknown-parent/cycle/self-edge rejection;
- canonical identifier enforcement;
- parent-edge removal rejection;
- candidate-domain removal rejection;
- shared-ancestor detection through multiple hops;
- disconnected-domain independence;
- candidate-control derivation through ancestry;
- missing-domain `INDEPENDENCE_UNPROVEN`;
- registry key/domain/role resolution from authenticated state;
- caller labels cannot override derived independence/candidate control; and
- no PASS path claims implementation/runtime/scientific/effect authority.

## 8. Preserved limitations

The graph is an authenticated governance assertion, not independent proof that no hidden real-world common controller exists. Independent manual review of graph completeness, root ownership, provider/account ownership and credential custody remains required before implementation/runtime qualification.

`IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`

`RUNTIME_QUALIFICATION = NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY = NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
