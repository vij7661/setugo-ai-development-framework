# Independent Blind Review — R8 Meta-Governance Preregistered Design

Status: REVIEW_REQUIRED / DESIGN_ONLY / NON_AUTHORITATIVE

Authority effect: NONE

## Frozen subject

Primary candidate:
- R8 preregistration commit: `d7d4876781fb82bcf8df43cf15bbe069acf33a0a`
- R8 file: `governance-r8/R8-META-GOVERNANCE-PREREGISTRATION.md`
- R8 blob SHA: `1cd69adbe924660d8dbc71826e9366b3e6e46b5c`

Supporting context included in the packet:
- current authoritative governance baseline;
- continuity/handoff rules;
- evidence/provenance standards;
- bounded terminal-authority and external-side-effect contracts;
- proposed PR #39 continuity rules;
- proposed PR #40 project-policy composition rules.

Do NOT use prior R1/R3 findings, prior adjudication conclusions, or prior remediation plans. Review the R8 design from scratch.

## Review objective

Attempt to falsify whether R8 is a sufficient preregistered design for a meta-governance layer.

Treat every registry, issuer, classifier, checkpoint, snapshot, policy engine, review dimension, recovery path, and meta-governor as potentially attacker-controlled until the design proves otherwise.

Do not assume that a component is trustworthy because its name contains "trusted", "authenticated", "platform", "governor", "registry", "immutable", "signed", or "authoritative".

## Mandatory attack areas

1. Root of trust / bootstrap
   - Who creates the first invariant registry, first authority issuer, first revocation registry, first policy registry, and first meta-governor configuration?
   - Can the actor being governed seed its own root authority?
   - Are bootstrap, key rotation, recovery, and root replacement distinct from ordinary policy changes?

2. Meta-governor self-grant
   - Can the meta-governor change the rules that define its own authority?
   - Can a registry update alter the predicate that validates the same registry update?
   - Is there a circular "governor validates governor" path?

3. Platform invariant registry
   - Can invariants be omitted, superseded, retired, or reclassified as overridable without independent authority?
   - Is "absence means non-overridable" enough if deletion of the invariant record is possible?
   - Are invariant IDs/version lineage immutable and monotonic?

4. Policy composition
   - Are ordering, scope overlap, conflict detection, same-level precedence, rollback, migration, and canonicalization fully deterministic?
   - Can policy text or schema shape exploit parser/canonicalization ambiguity?
   - Can a lower layer create a rule whose semantics indirectly weaken a higher-level invariant without an explicit contradiction?

5. Review governance
   - Can required dimensions be omitted through policy gaps, registry gaps, scope mismatch, or classifier failure?
   - Can self-review occur through aliases, shared credentials, same organization identity, delegated agents, or model/provider identity indirection?
   - Can BOUNDED_PASS remain vacuous under any combination of dimensions?
   - Can reviewer isolation be defeated through shared caches, shared memory, prompt history, reused sessions, or packet contamination?

6. Materiality / governance-impact classification
   - Can an authority-bearing change escape classification because dependency metadata is stale, incomplete, or attacker-authored?
   - What happens when a new governance object class is added?
   - Can non-file state changes alter authority while avoiding the classifier?

7. Authority issuer / revocation
   - Who authorizes issuers?
   - Can issuer enrollment, scope expansion, key rotation, revocation undo, or registry rollback self-grant authority?
   - What is the use-time trust source for revocation?
   - Can a stale but correctly signed authority record pass when revocation information is unavailable?

8. PLATFORM_POLICY terminal authority
   - Is the proposed narrowing sufficient to prevent policy text from becoming specific terminal approval?
   - Can a deterministic platform-policy issuer be configured by the same actor it later authorizes?

9. Continuity / checkpoint integrity
   - What anchors checkpoint authenticity?
   - Can a valid old checkpoint be replayed?
   - Can sequence/predecessor chains fork?
   - Can an attacker choose between two valid histories?
   - Does recovery ever permit a stale checkpoint to regain authority?

10. History / repository integrity
   - Are immutable objects enough if authoritative references can move?
   - What anchors accepted history outside the mutable repository?
   - How are history rewrites, garbage collection, mirror divergence, or repository migration handled?

11. Evidence ingestion
   - Can evidence move between classes by metadata-only changes?
   - Can telemetry, external evidence, reviewer assertions, or packet manifests be laundered into a stronger class?
   - Does the proposed state machine have an authenticated transition authority?

12. Recovery / emergency governance
   - Who authorizes recovery?
   - Can recovery replace a lost root with an attacker-controlled root?
   - Is there a safe way to recover from compromised issuer registry, corrupted policy registry, unavailable evidence store, or total reviewer outage?
   - Can recovery deadlock permanently?

13. Time / freshness
   - Which clock or sequence is authoritative?
   - Can clock rollback/forward skew affect expiry, revocation, reviewer availability, or recovery?
   - Are monotonic sequence identities globally scoped and tamper-resistant?

14. Multi-project / multi-tenant isolation
   - Can project/org IDs collide, alias, be renamed, migrated, or reassigned?
   - Can policy/evidence/authority from one tenant bleed into another?
   - Are issuer scopes and registry namespaces tenant-bound?

15. Falsification matrix quality
   - Identify false-green cases where R8-01..R8-45 could all pass while an untested authority bypass remains.
   - Identify cases that only test labels/return codes rather than the load-bearing mechanism.
   - Identify missing positive controls that would detect constant-rejection implementations.
   - Identify cases requiring independent fault proof.

16. Over-governance / impossible closure
   - Identify cycles, permanent fail-closed states, impossible recovery conditions, reviewer starvation, root-loss deadlocks, or policies that can never lawfully be changed.

## Reviewer constraints

- Design review only. Do not claim implementation/runtime verification.
- Do not grant qualification, merge, release, deploy, production, policy, or terminal authority.
- Keep current authoritative rules distinct from proposed PR #39/#40 context.
- Do not assume any named component exists unless the R8 design specifies it.
- Do not use prior reviewer findings or conclusions.
- Prefer concrete false-green or authority-laundering paths over stylistic criticism.
- If a defect depends on an implementation choice not fixed by the design, classify it as a design ambiguity/gap rather than asserting an implementation bug.
- A PASS must not be based on "the design says MUST"; evaluate whether the trust root, ownership, transitions, and failure states are actually closed.

## Required output

A. Overall disposition: `BOUNDED_PASS`, `CHANGES_REQUIRED`, or `INSUFFICIENT_EVIDENCE`.

B. Critical findings.

C. High findings.

D. Medium findings.

E. Root-of-trust / bootstrap assessment.

F. Meta-governor self-grant / circular-authority assessment.

G. Review of R8-I01..R8-I32: identify any invariant that is incomplete, contradictory, unenforceable, or missing a trust owner.

H. Review of R8-01..R8-45 falsification matrix: identify false-green cases, missing attacks, missing positive controls, and cases that do not actually prove the claimed mechanism.

I. Missing governance transitions / recovery paths.

J. Over-governance, deadlock, and impossible-closure risks.

K. Required preregistration changes before implementation. Be specific and minimal.

L. Final bounded statement explicitly confirming:
- review grants no authority;
- R8 remains NOT_IMPLEMENTED;
- PR #39/#40 remain non-authoritative;
- unresolved material findings block R8 implementation freeze/promotion.
