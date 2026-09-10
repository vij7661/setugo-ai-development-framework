# TESTING Qualification Boundary — Independent Re-falsification RED 007

Status: `PRESERVED_GENUINE_RED`
Authority effect: `NONE_EVIDENCE_ONLY`
Candidate SHA: `2fee17adc147ef0b1e6ddd5d02ce9f7fe9ee45d1`
Post-merge CI evidence: workflow `34452469174` was green on this exact SHA, but independent manual re-falsification subsequently returned `CHANGES_REQUIRED`.

## Scientific significance

The post-merge construction green did not establish closure. Independent attack identified concrete paths where terminal authority and qualification governance remain candidate-modifiable. This RED therefore supersedes any claim that the `2fee17ad...` construction green closed the TESTING qualification-boundary defect.

## Confirmed/adjudicated immediate defect

`terminal_authority_allowed()` accepts caller-supplied `issuer_class`, `provenance_verified`, and `current` and can return authorization without consuming `verify_authority_binding`. This violates the terminal-authority ownership standard and is a direct false-authority path.

## Additional material findings requiring repair/falsification

Candidate-local trust-root pointer/pin rebinding, candidate-controlled required-check workflow, archived-root lifecycle assumptions, candidate-computed policy identity, and candidate-local phase mapping all require an authoritative anchor outside the evaluated candidate revision before closure can be claimed.

## Preservation rule

This failure must remain in history after any later repair. A later green run or reviewer PASS cannot rewrite this RED or grant terminal authority.
