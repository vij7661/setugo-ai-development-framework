# Candidate lifecycle state separation

Candidate-local state records construction facts only, such as `PRE_FREEZE_READY`. Freeze occurs after an immutable commit/tree exists, so `FROZEN`, validation execution, packet generation, and review are external lifecycle facts recorded in candidate-bound evidence statements and external freeze attestation v2.

Candidate-local pre-freeze state is neither proof that a later external freeze did not occur nor proof that it did occur. Review/merge tooling MUST verify external attestation v2, exact frozen-ref resolution, candidate-bound Linux and packet statements, parsed review identity, and expected candidate identity. It MUST NOT promote an in-tree post-freeze claim or infer lifecycle state from candidate-local construction fields.

This separation prevents self-reference: freezing never requires mutating the frozen candidate. `AUTHORITY_EFFECT = NONE`.

Candidate-local construction records are immutable point-in-time statements at their originating commit. Their prose cannot establish or deny later freeze, validation, packet, or review events. A later external lifecycle pointer or governed evidence receipt supersedes only the current lifecycle interpretation; it never rewrites or invalidates the historical construction record. Machine tooling obtains current state from the structured external lifecycle ledger and trusted receipt, never by interpreting historical negative prose.
