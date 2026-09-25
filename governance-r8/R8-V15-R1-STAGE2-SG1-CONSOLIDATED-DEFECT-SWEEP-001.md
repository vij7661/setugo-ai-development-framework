# R8 v15-r1 Stage2 SG-1 Consolidated Defect Sweep 001

Status: FROZEN_READ_ONLY_AUDIT_BEFORE_REPAIR

Starting branch: governance/r8-v15-r1-stage2-semantic-gate-proposal-2026-09-25
Starting HEAD: 815bd424fd2949b244ee14ad68dfa186b2b6fc06
Frozen proposal: R8V15R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-CONFORMANCE-001
Frozen proposal commit/blob: 67c84138140e86ba4a85a954f368f4c0f7e9ef3c /
d1ebd1427d5dfb07348fda2f817aa7f3d20feb3b

This inventory was created before remediation edits. Review 001 remains immutable
historical evidence and is not rewritten.

## Complete defect inventory

### SG1-SWEEP-HIGH-001 — High — confirmed blocking

- Affected files: tools/build_r8_v15_r1_stage2_sg1_review_packet.py and the
  generated stage2-sg1-review/R8-V15-R1-STAGE2-SG1-EARLY-REVIEW-PACKET.txt.
- Mechanism: packet required-output text, section H. FINAL_GATE.
- Failure path: the builder hardcodes obsolete activation-gate blob
  previous activation-gate blob while the repaired gate and binding
  use 1078bc673665b3e23d99d2d1699a7ccab90bbf6d. A reviewer or future approver
  can bind approval to the wrong gate.
- Evidence: generated packet line 140; current workflow blob and binding both
  identify 1078bc673665b3e23d99d2d1699a7ccab90bbf6d.
- Blocking: yes. Dependency: repair builder identity source before packet
  regeneration. Changes the packet-builder blob and regenerated packet only.
- Required regeneration: run the consistency verifier before and after one final
  packet regeneration; do not alter Review 001.

### SG1-SWEEP-MEDIUM-001 — Medium — confirmed recurrence risk

- Affected files: activation binding, review packet marker, packet builder,
  activation workflow.
- Mechanism: repeated identity literals are maintained independently rather than
  checked by one deterministic verifier.
- Failure path: a future repair can update the gate/binding while leaving a
  packet instruction, review path, proposal identity, machinery identity, or
  cadence statement stale.
- Blocking: no immediate activation bypass proven; recurrence risk is real.
- Narrow repair: add a read-only canonical manifest and a fail-closed
  cross-artifact consistency verifier. Changes verifier/manifest/builder support
  and regenerated packet material.

### SG1-SWEEP-MEDIUM-002 — Medium — confirmed testability gap

- Affected files: no existing cross-artifact verifier; packet-generation
  workflow and marker.
- Mechanism: stale identity negative cases are not deterministically tested as a
  repository-local suite.
- Failure path: stale old gate SHA or Review 001 path could reappear without a
  focused failure.
- Blocking: no current activation artifact exists, so this is prevention rather
  than an active bypass.
- Narrow repair: add deterministic verifier tests using temporary copies,
  without mutating authoritative files.

### SG1-SWEEP-LOW-001 — Low — deferred by scope

- The audit hook does not claim exhaustive defense against every possible Python
  dynamic technique. No new concrete false-green or practical external-effect
  path was demonstrated in the bounded harness audit. Defer.

### SG1-SWEEP-LOW-002 — Low — deferred by scope

- The activation gate does not directly bind the informational
  activation-gate-binding JSON as a gate-bound blob. No concrete bypass was
  demonstrated without an activation artifact. Defer.

### SG1-SWEEP-LOW-003 — Low — deferred by scope

- The dependency surface is bound from the reviewed semantic surface and Stage1
  scan rather than rescanned by the SG-1 harness itself. Static inspection found
  the declared 31 + 1 direct edges and two target modules; no additional
  materially relevant direct edge was demonstrated. Defer.

## Audit conclusions by dimension

- A1 Identity propagation: inspected all SG-1-specific files, workflows, builder,
  packet, binding, proposal, markers, Review 001, machinery/evidence references.
  Confirmed SG1-SWEEP-HIGH-001 and duplicate-source risk.
- A2 Single source of truth: duplicated literals identified; SG1-SWEEP-MEDIUM-001.
- A3 Proposal binding consistency: proposal ID/commit/blob/path, machinery,
  evidence, authority and cadence fields agree.
- A4 Binding/activation consistency: repaired gate and binding agree; packet H
  instruction was stale (SG1-SWEEP-HIGH-001).
- A5 Packet builder: fully inspected; H. FINAL_GATE used a stale hardcoded gate
  SHA while header gate identity was dynamic.
- A6 Generated packet consistency: stale H instruction confirmed; embedded
  binding/workflow identities otherwise agree.
- A7 Review parser: strict case-insensitive None/None. matcher remains bounded;
  no new parser false-green was demonstrated.
- A8 Activation-artifact contract: exact key sets, proposal/review/machinery/
  evidence bindings and no-activation boundary are present; no artifact exists.
- A9 GitHub activation workflow: branch/path restriction, pinned checkout,
  read-only permissions, verify-before-reusable-core ordering inspected. No
  direct bypass was demonstrated in the bounded repository workflow.
- A10 Packet workflow: builder uses the current HEAD for bundle identity; packet
  output is reproducible, but its manually repeated H gate literal caused the
  confirmed defect.
- A11 Historical preservation: Review 001 is present, CHANGES_REQUIRED, and
  retains its historical old gate identity. It must not be rewritten.
- A12 Semantic dependency surface: declared 39 files/32 edges/2 targets
  inspected against the bound surface and Stage1 scan; no additional concrete
  bounded-scope dependency was demonstrated.
- A13 Runtime resolution oracle: SG1-01..06 and exact target identity checks
  inspected; no new concrete bypass demonstrated.
- A14 GCP/INT64 oracle: SG1-07..10 inspect the used frozen-runtime surface; no
  new concrete false-green demonstrated.
- A15 Effect-state/effect-intent boundary: SG1-11..18, delegation, error,
  binding, idempotency and non-authority checks inspected; no new concrete
  false-green demonstrated.
- A16 Import-order contamination: forward/reverse order and fingerprint oracle
  inspected; stronger permutations are defense-in-depth, not blocking here.
- A17 Comparator: exact case IDs, fingerprints, statuses and malformed-result
  failure behavior inspected; no new concrete normalization bypass demonstrated.
- A18 Harness side effects: audit-hook policy and AST restrictions inspected;
  no practical bounded-scope escape demonstrated; optional hardening deferred.
- A19 Stage1 guard: exact candidate/tree and before/after guard references
  inspected; no new bypass demonstrated.
- A20 Candidate immutability: HEAD/tree/worktree and reviewed-file checks
  inspected; no new concrete bypass demonstrated.
- A21 Preflight evidence: run/job 36169709850 / 108185981758 and blob
  963b3e29ce2cdb2621d83e4e9f3f657a45222ad6 cover proposal machinery/evidence,
  not the repaired activation parser; no silent scope expansion found.
- A22 Authority language: SG-1 artifacts preserve LOCAL DEPENDENCY SEMANTIC
  FALSIFICATION ONLY, broader Stage2 NO, and all downstream authority false.
- A23 Cadence: fallback-to-3 remains active; six-slice restoration remains NO.
- A24 Post-execution gate: fresh independent review remains required after any
  future SG-1 execution; no execution has occurred.
- A25 Generated provenance: packet records bundle commit and embedded blob
  identities, but stale H identity and lack of cross-artifact verification
  motivated SG1-SWEEP-HIGH-001 and SG1-SWEEP-MEDIUM-001.

## Frozen repair order

1. Add canonical identity manifest and deterministic verifier/test fixtures.
2. Make packet H. FINAL_GATE derive the current activation-gate identity.
3. Run verifier before packet regeneration.
4. Regenerate the consolidated Review-002 packet once.
5. Run verifier again against the final packet.

## AUDIT_DIMENSIONS_COMPLETED

A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12, A13, A14, A15, A16,
A17, A18, A19, A20, A21, A22, A23, A24, A25.

No review dimension was abandoned after the first blocking finding.
