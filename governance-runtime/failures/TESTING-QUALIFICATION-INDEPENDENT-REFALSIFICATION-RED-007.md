# TESTING Qualification Boundary — Independent Re-falsification RED 007

Status: `PRESERVED_GENUINE_RED`
Authority effect: `NONE_EVIDENCE_ONLY`
Candidate SHA: `2fee17adc147ef0b1e6ddd5d02ce9f7fe9ee45d1`
Post-merge CI evidence: workflow `34452469174` was green on this exact SHA, but independent manual re-falsification subsequently returned `CHANGES_REQUIRED`.

## Adjudication
- F1 is directly confirmed from candidate code: `terminal_authority_allowed()` can authorize from naked caller-supplied issuer/provenance/current values without `verify_authority_binding`.
- F2, F3, F5 and F6 are material candidate-self-definition paths and remain blocking until an authoritative anchor exists outside the evaluated candidate revision.
- F4 is materially valid as a limitation on claims of immutability: GitHub `archived=true` is administrative state, not cryptographic immutability. The threat model must distinguish authorized human-governance administration from candidate authority, but archive state alone cannot serve as the sole root of trust.

## Scientific significance
The post-merge construction green did not establish closure. Independent attack exposed false-authority/self-qualification paths. This RED remains part of permanent failure history after any repair.
