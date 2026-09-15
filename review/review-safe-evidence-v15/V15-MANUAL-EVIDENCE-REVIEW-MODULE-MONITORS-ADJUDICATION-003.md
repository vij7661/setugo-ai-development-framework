# V15 Monitor-Module Review Adjudication — 003

Status: **V15 IMPLEMENTATION REJECTED / SUCCESSOR REQUIRED / REVIEW CONTINUES**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Adjudication

The monitor-module review is accepted.

### Accepted Critical findings

1. `C-MON-001` — the hidden-evidence coverage certificate is not cryptographically/structurally bound to the actual monitor bundle it claims to certify. A caller-provided `monitor_result` can be laundered into a green certificate.
2. `C-MON-002` — monitor quorum, independence and `NO_REOPEN_FOUND` outcomes can be synthesized from self-consistent caller-supplied identities, domains, proof records and digests without authenticated execution over the referenced evidence.

### Accepted High findings

1. `H-MON-001` — certificate-verifier independence is a caller-supplied assertion rather than a registry/proof-derived property.
2. `H-MON-002` — `expected_obligations` is a caller-controlled universe and can be truncated to omit a material obligation.

### Accepted Medium / Low

- `M-MON-001` — threshold naming/semantics do not correspond to an actual N-of-M per-obligation quorum.
- `L-MON-001` — two-implementation diversity permits majority reuse of one implementation.

## Relationship to existing findings

These findings confirm and amplify the existing systemic V15 Critical: ordinary self-hashes provide integrity-of-serialization, not authority authenticity. They also add two independent relational-binding defects:

- certificate -> bundle/result binding is missing;
- monitor coverage -> authoritative obligation universe binding is missing.

These are not duplicates of the original root-of-trust finding because they remain concrete false-green paths even after merely replacing hashes with signatures unless the successor also fixes the missing cross-object bindings and authoritative-set derivation.

## Successor requirements accumulated so far

The successor must include at minimum:

- externally authenticated authority records rather than candidate-recomputable self-hashes;
- authority/identity/currentness resolution from a governed registry, not caller booleans/labels;
- independence recomputation from authenticated ancestry/control data;
- blocker resolution cross-binding to an actual reopened review and real evidence;
- governance-generation witness authority cross-verification;
- residual-trust limitations derived from unresolved upstream state;
- monitor execution evidence bound to raw evidence + obligation + implementation identity;
- coverage certificate recomputation from the exact monitor bundle;
- certificate-verifier authority/independence verification;
- monitor obligation coverage bound to the authoritative obligation set.

## State

- `V15_IMPLEMENTATION_ACCEPTANCE = REJECTED`
- `V15_SUCCESSOR_REQUIRED = true`
- `V15_SUCCESSOR_SCOPE_FROZEN = false`
- `V15_MANUAL_REVIEW_CONTINUES = true`
- `NEXT_MODULE = review_safe_evidence_v15_review.py`
- `IMPLEMENTATION_QUALIFICATION = NOT_CLAIMED`
- `RUNTIME_QUALIFICATION = NOT_CLAIMED`

Do not repair the frozen V15 candidate in place. Finish review of the unchanged frozen candidate first so the successor scope captures the complete failure family.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
