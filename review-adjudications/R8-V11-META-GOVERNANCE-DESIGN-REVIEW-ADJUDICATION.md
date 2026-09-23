# R8 v11 Independent Design Review + Remediation Proposal — Adjudication

Status: **CHANGES_REQUIRED — ADOPT_WITH_NARROW_REVISIONS — SUCCESSOR DESIGN REQUIRED**
Authority effect: **NONE**

Reviewed candidate:
- R8 v11 commit: `3d6a0820d851bc629fc4c7ccfee4a081b70ce117`
- R8 v11 blob: `21e5134fa972d9e62f770beb69e2f3ea5c4f96e6`

Independent review evidence:
- `review-evidence/R8-V11-META-GOVERNANCE-INDEPENDENT-DESIGN-REVIEW.md`
- original uploaded SHA-256: `46bedc5df36fb887cd3bec81bfbdbe6c0a5a89ae2a675fcdd9b6a5173a8edca7`
- disposition: `CHANGES_REQUIRED`

Reviewer remediation proposal:
- `review-evidence/R8-V11-META-GOVERNANCE-REMEDIATION-PROPOSAL.md`
- original uploaded SHA-256: `0ba58c9fa43374af698cacd356a22f2e0fd6a2779c57886e497f0b90118b1e51`
- status: proposed design remediations only
- authority effect: `NONE`

## 1. Overall adjudication

The independent v11 findings are materially valid.

The remediation proposal is directionally strong and is **adopted with narrow revisions**. It must not be copied verbatim into the successor because several proposed fixes still contain ambiguity capable of recreating the same classes of false-green or schema-time drift.

R8 v11 remains preserved unchanged as the reviewed exposure.

## 2. Accepted critical blockers and successor requirements

### V11-C1 — Blind packet is not blind
**ACCEPTED — BLOCKER**

The successor must:
- remove prior-version disposition outcomes from the blind reviewer projection;
- preserve current-candidate status and all semantic governance content;
- deterministically reject residual prior outcome/status metadata;
- make canonical TXT the authoritative reviewer packet;
- treat PDF only as a convenience projection with explicit authority status.

Narrow revision:
- do not globally strip status words;
- redact only prior-version review/disposition metadata;
- retain semantic statements required to express authority effect and current candidate status;
- maintain a projection manifest with removed-line count and digest.

### V11-C2 — decision_sequence replay
**ACCEPTED — BLOCKER**

The successor must not expose authority-bearing `decision_sequence` as a caller-selected input.

Narrow revision:
- define exactly one authority source: `semantic_state_sequence = current committed LAS-3 semantic-state sequence`;
- historical sequence resolution is a separate forensic API with authority effect NONE;
- bind semantic_state_sequence + CSM head + AIM head + resolver-policy digest into AuthorityReadSet, DecisionPresealContext, VerifiedStateSeal, and consequential commit checks;
- do not use an “LAS or MTR” alternative semantic-sequence source.

### V11-C3 — semantic registry not bound to AuthorityStateRoot/freeze
**ACCEPTED — BLOCKER**

The successor must explicitly include named semantic heads in authority state:
- CSM registry head;
- AIM descriptor head;
- ANY permission root/head;
- resolver-policy digest/head.

Narrow revision:
- these must appear as named members of LAS authority state and RBP freeze semantics, not only hidden underneath a generic state-machine root;
- if GGS certification consumes semantic state, the same exact heads must be bound there as well.

### V11-C4 — ANY permission drift relies on Meta-Governor completeness
**ACCEPTED — BLOCKER**

The successor must make **resolver-time permission verification the authority mechanism**.

Narrow revision:
- Meta-Governor lifecycle marking remains durable evidence/bookkeeping only;
- every ANY-scoped candidate must independently re-resolve active ANY permission at the current semantic-state sequence;
- missing/narrowed/revoked permission blocks at Smax even if no lifecycle transition was written.

## 3. Accepted high findings and tightened remedies

### V11-H1 — AIM descriptor lifecycle
**ACCEPTED**

AIM descriptors become append-only/versioned constitutional semantic objects.

Changing semantic_input_id, source lineage, scope-construction rule, semantic class, or resolver-policy binding creates a constitutionally authorized successor descriptor. No in-place mutation.

### V11-H2 — resolver_policy_digest opaque
**ACCEPTED**

Successor must freeze a machine-readable ResolverPolicy object and additionally bind:
- resolver implementation/artifact digest;
- RuntimeManifest/workload identity;
- deterministic conformance-vector-set digest.

Policy text/digest alone is not proof that execution follows the policy.

### V11-H3 — semantic heads missing from state-root formulas
**ACCEPTED**

Apply the explicit named-head rule to:
- LASAuthorityStateRoot;
- STC/barrier roots;
- GGS state root wherever semantic state is consumed;
- DecisionPresealContext;
- VerifiedStateSeal.

### V11-H4 — one barrier can admit multiple rotation IDs
**ACCEPTED**

One barrier index may correspond to at most one lawful rotation.

Narrow revision:
- ROTATION_ABORT closes that barrier permanently;
- any retry/new rotation after abort requires a fresh barrier index;
- the old barrier cannot be recycled under a new rotation ID.

### V11-H5 — PDF corruption
**ACCEPTED AS PACKAGING DEFECT**

Canonical TXT is authoritative.

PDF is:
- `NON_AUTHORITATIVE_CONVENIENCE` by default;
- usable only if projection validation passes;
- never allowed to override TXT.

The manifest records PDF projection status and hashes when a PDF exists.

## 4. Accepted medium findings and tightened remedies

### V11-M1 — consolidated guard catalog
**ACCEPTED**

The successor review packet must contain one deterministic consolidated catalog generated from canonical guard definitions.

Generation fails on:
- missing or duplicate guard IDs;
- missing positive control;
- missing/invalid case references;
- missing FP class for negative cases.

Do not maintain the consolidated table by manual copy.

### V11-M2 — ANY revalidation authority unnamed
**ACCEPTED**

Freeze explicit constitutional authority class:
`ANY_SCOPE_PERMISSION_AMENDMENT`.

Project/org/experiment policy cannot satisfy it.

### V11-M3 — ScopeReplacementMapping enum ambiguity
**ACCEPTED WITH REVISION**

Do not rely on vague enum names alone.

Freeze a machine-readable replacement truth table binding:
- old_scope_tuple;
- new_scope_tuple;
- decision_scope_match_rule;
- old_scope_effect;
- effective sequence;
- lineage/mapping identity.

The resolver evaluates the truth table deterministically.

### V11-M4 — DPS-2 semantic state missing
**ACCEPTED**

DPS successor includes:
- semantic_state_sequence;
- CSM head;
- AIM head;
- ANY permission head/root;
- resolver-policy digest;
- AuthorityReadSet digest.

Any change after nonce/time proof issuance invalidates that proof.

### V11-M5 — resolver algorithm artifact
**ACCEPTED**

Covered by ResolverPolicy + implementation + runtime identity + conformance-vector binding.

## 5. Fresh-review consequence

Because the v11 reviewer observed prior-version dispositions, the v11 review is useful independent technical evidence but does **not** satisfy the intended fresh-blind review condition.

After v12 freeze, a genuinely clean new reviewer context is still mandatory.

## 6. Successor rule

Create R8 v12 as a new successor overlay.

Do not mutate v4-v11.

R8 v12 must receive a fresh blind independent design review before executable-schema freeze.

Until then:
- R8 v1-v11 = `CHANGES_REQUIRED`
- R8 v12 = not yet reviewed
- executable-schema freeze = `BLOCKED`
- PR #39 = `NON_AUTHORITATIVE`
- PR #40 = `NON_AUTHORITATIVE`
- holistic governance = `CHANGES_REQUIRED`
- authority effect = `NONE`
