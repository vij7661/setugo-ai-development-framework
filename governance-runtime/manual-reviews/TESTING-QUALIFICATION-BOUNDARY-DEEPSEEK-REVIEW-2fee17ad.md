# Independent re-falsification evidence — exact candidate 2fee17ad

Status: `USER_RELAYED_EXTERNAL_REVIEW_EVIDENCE`
Authority effect: `NONE_EVIDENCE_ONLY`
Candidate SHA: `2fee17adc147ef0b1e6ddd5d02ce9f7fe9ee45d1`
Reviewer provenance: user reports this was returned by DeepSeek after reviewing the exact-candidate text packet. This preserves the relayed content as evidence; it does not independently authenticate provider/model identity and does not grant authority.

## Relayed disposition

`CHANGES_REQUIRED`

## Relayed findings

### F1 — CRITICAL: Terminal authority can be self-granted without signed binding
`terminal_authority_allowed()` accepts caller-supplied issuer/provenance/current booleans and can return True without exact-SHA/policy/evidence/signature verification.

### F2 — CRITICAL: External trust-root pointer and policy constants are candidate-modifiable
Candidate-local root repository/ID/commit/fingerprint constants can be rebound together to an attacker-controlled archived repository/key.

### F3 — CRITICAL: Required status check is produced by candidate-modifiable workflow
The required `falsify-qualification-boundary` context is emitted by a workflow stored in the candidate repository and can be weakened while retaining the same context name.

### F4 — HIGH: Archived-root assumption relies on mutable GitHub API state
Archive state is administrative state, not cryptographic immutability; same-owner administrative control can unarchive/rebind/delete.

### F5 — HIGH: Policy hash is computed from candidate-controlled material
A candidate can weaken policy material and recompute a self-consistent hash when combined with trust-root rebinding.

### F6 — MEDIUM/HIGH: Phase deferral mapping is candidate-modifiable
Candidate-local `GOVERNED_RULE_PHASES` can be altered so a current TESTING defect is mapped to a later phase.

Full reviewer wording is preserved in the conversation record. Reviewer-stated authority effect: `NONE_EVIDENCE_ONLY`.
