# V24 I11 V6 — Proof-Reference Closure Repair Design

Status: **PREREGISTERED REPAIR DESIGN / NOT RUNTIME AUTHORITY**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Scope and preserved history

This repair addresses finding `V6-PRC-001` discovered after the frozen V6/R9 successor candidate `88cba7e1224ecbd5a8264ba4c31c4c264fc24fef` had completed construction verification.

The predecessor commit, tree, GREEN runs, and the later RED run `35000549932` remain immutable historical evidence. No predecessor evidence is rewritten. All repair work occurs on `remediation/v24-i11-v6-proof-resolution` and must produce a new successor commit/tree before any clean successor review.

## 2. Failure being repaired

R1 defines structural validators for governed qualification, independence qualification, currentness binding, registry completeness, and paired genesis trust. Several R2-R8 authority-bearing paths nevertheless consume caller-supplied `QUALIFIED` / `CURRENT` labels and SHA-shaped references without resolving those references to the exact records that R1 can validate.

Therefore a syntactically plausible digest can act as an authority token even when the referenced proof is absent, stale, for the wrong subject, cyclic, self-granted, or fabricated.

The repair must make **proof resolution load-bearing**. A state label or digest shape is never sufficient by itself.

## 3. Trust-boundary rule

The candidate/decision object and the trusted governance proof context are separate inputs.

A `GovernanceProofContext` contains:

1. `governance_generation_id`;
2. an exact digest-indexed `evidence_records` surface containing governance proof records;
3. a validated `GenesisTrustedABGOUScopeRecord`;
4. an `expected_genesis_scope_digest` supplied by the invoking trusted environment/frozen successor configuration, not copied from the candidate decision object.

A candidate field named like `governance_proof_context`, `trusted_genesis_scope`, `expected_genesis_scope_digest`, or equivalent has **no authority** and cannot substitute for the separately supplied context.

## 4. Supported proof-record kinds

The shared resolver initially recognizes the exact R1 record classes that are already load-bearing dependencies:

- `GOVERNED_QUALIFICATION` -> R1 `validate_governed_qualification`;
- `INDEPENDENCE_QUALIFICATION` -> R1 `validate_independence_qualification`;
- `CURRENTNESS_BINDING` -> R1 `validate_currentness_binding`.

Each evidence-store entry is keyed by the record's canonical self-digest:

- governed qualification: `qualification_digest`;
- independence qualification: `qualification_digest`;
- currentness binding: `binding_digest`.

The resolver recomputes the applicable self-digest before the record can satisfy any dependency. Unknown keys, malformed records, key/self-digest mismatch, and duplicate/ambiguous digest entries fail closed.

## 5. Exact binding rules

### 5.1 Governed qualification

A referenced governed qualification is acceptable only if:

1. the exact digest resolves;
2. `validate_governed_qualification` returns no problems;
3. `result == QUALIFIED`;
4. the qualification's `subject_object_id` equals the expected subject ID when an expected ID is supplied;
5. the qualification's `subject_content_digest` equals the expected subject digest when an expected digest is supplied;
6. every `independence_qualification_digest` resolves and validates;
7. every embedded currentness binding validates and is `CURRENT`;
8. every embedded currentness binding's `verifier_qualification_digest` closes recursively;
9. the qualification's `verifier_mechanism_qualification_digest` closes recursively;
10. recursion terminates only through the exact paired genesis rule in Section 7.

### 5.2 Independence qualification

A referenced independence qualification is acceptable only if:

1. the exact digest resolves;
2. `validate_independence_qualification` returns no problems;
3. `result == QUALIFIED`;
4. `subject_identity_id` equals the expected subject identity when supplied;
5. each embedded currentness binding validates and is `CURRENT`;
6. each currentness verifier qualification closes recursively;
7. `verifier_qualification_digest` closes recursively;
8. the record is not part of a dependency cycle.

### 5.3 Currentness binding

A referenced or embedded currentness binding is acceptable only if:

1. `validate_currentness_binding` returns no problems;
2. `result == CURRENT`;
3. `source_object_id` and `source_digest` equal expected values when supplied;
4. `verifier_qualification_digest` closes recursively;
5. the record is not part of a dependency cycle.

A caller-provided state label outside the validated record cannot satisfy currentness.

## 6. Recursive closure and cycle rejection

The resolver maintains an active recursion stack keyed by `(record_kind, digest)`. Re-entering an active node is `PROOF_REFERENCE_CYCLE_REJECTED`.

Successful memoization is allowed only after the referenced record and all of its transitive dependencies have closed successfully.

A record cannot make itself trusted merely by pointing to another record that eventually points back to it.

## 7. Genesis termination rule

Genesis is a trust terminator only for an **exact `(object_id, content_digest)` pair** admitted by R1 `genesis_scope_match` against the separately supplied and validated genesis scope.

The supplied scope must satisfy all of the following before use:

1. `validate_genesis_trusted_scope` returns no problems;
2. its canonical `scope_digest` equals `expected_genesis_scope_digest` from the trusted invocation boundary;
3. `governance_generation_id` equals the proof context generation;
4. the exact subject pair is present.

Cross-pair composition is forbidden: an admitted object ID from one pair and an admitted content digest from another pair must not terminate recursion.

For a governed qualification whose exact subject pair is genesis-trusted, the resolver may stop **after** validating the qualification's own structure, result, subject binding, and self-digest. Its transitive verifier/independence chain is not used to bootstrap authority. This is the only recursive qualification shortcut in this repair.

## 8. Evidence classes outside governance-proof closure

`evidence_record_digests` and domain evidence-class records remain evidentiary inputs governed by their owning V6 mechanisms. This repair does not silently invent new evidence schemas for them.

However, any digest explicitly designated by an R2-R8 field as a qualification, independence, currentness, verifier-qualification, witness-qualification, parser-qualification, compiler-qualification, registry-qualification, gate-qualification, or equivalent governance proof reference must close through this resolver.

## 9. Downstream integration rule

Every R2-R8 authority-bearing function that can return an allowed/qualified/current/pass result from governance proof references must receive the trusted proof context separately and fail closed before its positive result if required proof closure is absent.

At minimum re-audit/integrate:

- R2 endpoint projection and applicability/compiler qualifications;
- R3 material-observation witness, material-surface derivation/classification, and effect-path qualifications;
- R4 decision/apply source, decision, latch and effect-path qualifications;
- R5 normative parser/disposition/projection qualifications;
- R6 effect-ledger verifier/witness/reconciler qualifications;
- R7 mode-registry/verifier/selector/atomic-mode qualifications;
- R8 case-universe/source/runtime-trace/gate/summary-compiler qualifications;
- R9 integrated successor validation of the repaired proof-closure surface.

No module may preserve a legacy positive path by treating absence of `proof_context` as implicitly trusted. Missing context is fail-closed.

## 10. Compatibility/migration rule

Existing positive construction fixtures that used dummy 64-hex proof labels must be migrated to a deterministic test-only proof context built from exact self-digesting R1-valid records and a separately supplied genesis scope.

The fixture helper is not production authority. Production code cannot synthesize proof records merely to convert a label into a passing proof.

## 11. Mandatory falsification matrix

Before a repaired successor can be frozen, deterministic tests must cover at least:

1. unknown qualification digest;
2. digest key does not match record self-digest;
3. governed qualification for wrong subject ID;
4. governed qualification for wrong subject content digest;
5. qualification result not `QUALIFIED`;
6. stale embedded currentness binding;
7. currentness binding for wrong source;
8. independence record with shared-control intersection;
9. independence record for wrong subject identity;
10. missing verifier qualification;
11. cyclic qualification/verifier dependency;
12. exact paired genesis termination succeeds;
13. genesis cross-pair ID/digest substitution fails;
14. candidate-provided fake genesis/proof context cannot override trusted invocation context;
15. R3 fabricated witness labels cannot qualify an observation ledger;
16. R4 opaque labels cannot open the apply latch;
17. at least one positive proof-closed path for every integrated R2-R8 workstream;
18. all inherited R1-R9 tests and predecessor V24 regression remain passing after fixture migration.

## 12. Successor gate

A repaired implementation is only a **new construction candidate**. It must complete, in order:

1. shared proof-closure module RED -> GREEN;
2. R2-R8 integration RED -> GREEN;
3. complete affected + inherited regression;
4. a new integrated successor manifest bound to the new commit/tree;
5. deterministic successor-verification package regeneration;
6. fresh clean independent successor review in a separate clean review context;
7. repository-binding adjudication;
8. only after those gates, scientific WDPC execution.

No result in this repair phase grants runtime, production, release, deployment, scientific, or terminal authority.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
