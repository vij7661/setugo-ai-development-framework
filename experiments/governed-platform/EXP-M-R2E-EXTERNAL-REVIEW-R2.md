# Independent External Review — EXP-M Deterministic Implementation R2E — R2

Disposition: **CHANGES_REQUIRED**

Authority effect: **NONE**

EXP-M: **NOT_QUALIFIED**

Live provider/API execution: **not authorized and not performed**

## Finding 1 — Unrecorded post-processing breaks chain-of-custody for critical results

The evidence manifest records `stdout_payload_identical_to_result=false` for `reviewer-compound` and `self-falsification`, with `stdout_role` stating the final result artifact differs because governed post-processing occurred after command execution.

Impact: `EXP-M-R2E-COMPOUND-RESULTS.json` and `EXP-M-SELF-FALSIFICATION-RESULTS.json` are not directly bound to the captured command output. No post-processing command, script hash, input/output hash binding, or capture envelope is present. This is a remaining false-green/replay path.

Required remediation: Either eliminate post-processing so the result artifact is byte-identical to the command stdout raw payload, or record post-processing as a governed command with its own source-bound capture envelope, script hash, input raw-payload hash, output artifact hash, and S identity.

## Finding 2 — Authority delivery-ledger mismatch

The source freeze contains a current-S delivery record for request `r`, while the pinned authority delivery ledger and signed test expectations remain anchored to the legacy reviewed commit `2814499a37912ea252b759c530fc07bdcef4950c`.

Impact: Two conflicting delivery-authority records exist. If runtime uses the source-freeze copy it is an authority substitution; if runtime uses the pinned ledger the source freeze is inconsistent or stale.

Required remediation: Reconcile the two records and state which is authoritative for the current S-E-P-Q sequence. Any current-S derivation must be explicitly rooted in the external authority rather than silently substituting candidate-generated authority.

## Finding 3 — Missing generation provenance for EXP-M-SOURCE-FREEZE.json

`EXP-M-SOURCE-FREEZE.json` is an E artifact but the evidence manifest contains no source-bound command record for its generation.

Impact: Its final hash is attested, but its generation provenance is outside the command-capture chain.

Required remediation: Add a source-bound generation capture with S commit/tree, command identity, exit code, raw output hash/size, and result artifact binding.

## Finding 4 — Q / S-E-P-Q separation is incomplete

The textual handoff identifies S, E and P but not Q commit/tree and contains no explicit S-E-P-Q verification output.

Impact: The complete S -> E -> P -> Q sequence cannot be independently verified from the handoff.

Required remediation: Publish Q commit/tree and an explicit S-E-P-Q verification capture.

## Finding 5 — Full mutation and self-falsification results are not embedded

Only summaries are visible in the textual handoff.

Impact: The reviewer cannot adversarially inspect every mutation/self-falsification case and rejection reason from the handoff text alone.

Required remediation: Embed the complete mutation and self-falsification JSON or make their complete bytes available and hash-bound in the portable review bundle.

## Finding 6 — CA-9 / CA-10 clarified, but field name remains misleading

CA-9 and CA-10 semantics are sufficiently clarified, but `rejection_reason` still carries a guard/predicate identifier for CA-9.

Required remediation: Rename the field to `blocking_guard` or `predicate_failed` in the next schema revision. This is secondary to the primary blockers.

## Finding 7 — Handoff alone cannot complete hash / Git-object verification

The handoff does not itself contain the referenced Git objects.

Impact: Commit/blob and manifest identities cannot be independently recomputed from text alone.

Required remediation: Ensure the portable bundle contains the required Git objects or exact offline fetch instructions plus a verifier; bind every required artifact, excluding only a self-referential manifest with explicit justification.

## Final disposition

**CHANGES_REQUIRED**

Authority effect remains **NONE**. EXP-M remains **NOT_QUALIFIED**. No live provider/API execution is authorized or performed.
