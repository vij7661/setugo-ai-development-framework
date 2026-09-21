# EXP-M R2E Static Review Clarification Adjudication

Status: REMEDIATED_PENDING_FRESH_S_E_P

Authority effect: NONE

EXP-M state: NOT_QUALIFIED

Live provider/API execution authorized: false

This record adjudicates the seven clarification findings returned by the static-only independent review of the prior R2E handoff. The reviewer explicitly stated that it could not fetch Git objects, recompute hashes, or execute suites. These findings are therefore separated into implementation defects, evidence/reporting defects, and inherent static-review limitations.

## SR-1 — CA-9 rejection label

Classification: REPORTING_AMBIGUITY

The production governor evaluates all non-disposition predicates first. It then derives PASS only when every underlying predicate is true; otherwise it derives CHANGES_REQUIRED. A caller-supplied disposition that disagrees with that derived disposition is rejected. Therefore the predicate named disposition_promotable is false in CA-9. The earlier compound result used the predicate identifier as a field named rejection_reason, which could be misread as a positive assertion.

Remediation:
- Preserve the preregistered CA-9 attack unchanged.
- Record rejection_reason_semantics as a blocking guard/control label.
- Record guard_semantics explaining that disposition_promotable=false when failed predicates derive CHANGES_REQUIRED and caller PASS cannot override it.
- Explain the same semantics in the review packet.

Adjudication: CLARIFIED; no production-validator weakness identified by this finding.

## SR-2 — CA-10 protocol unavailable while protocol is present

Classification: FAULT-INJECTION-REPORTING_AMBIGUITY

CA-10 intentionally creates an AuthorityHandle with protocol_available=False by calling with_missing_r5_protocol_for_test(). The test asks whether a self-consistent R5 record is rejected when the authoritative protocol is deliberately made unavailable. The real preregistered authority root still contains and hash-binds the R5 protocol.

Remediation:
- Preserve the preregistered CA-10 attack unchanged.
- Add explicit fault_injection metadata to the compound result.
- Explain in the packet that r5_protocol_unavailable is the expected result of this injected negative condition and does not state that the real authority root lacks the protocol.

Adjudication: CLARIFIED; no contradiction between CA-10 and the frozen real protocol.

## SR-3 — Evidence manifest does not list itself

Classification: SELF-REFERENCE / ATTESTATION GAP

A final manifest cannot contain its own final SHA-256 without recursive self-reference. The earlier packet did not explain this.

Remediation:
- Manifest schema explicitly records that it is intentionally not self-listed.
- P independently attests the exact manifest bytes stored at E using SHA-256, size, and Git blob identity.
- S-E-P verification recomputes the E manifest hash and requires the P content to contain the same attestation.

Adjudication: REMEDIATED.

## SR-4 — JSON results and STDOUT have identical hashes

Classification: EVIDENCE-INDEPENDENCE CLARIFICATION

Some runners serialize the result JSON to a file and print the same serialization to stdout. Those two files are duplicate representations and must not be counted as independent corroboration.

Remediation:
- Each command record now carries stdout_role.
- Where hashes and sizes match the corresponding JSON result, the manifest sets stdout_identical_to_result=true and labels STDOUT as duplicate_serialization_of_result_json.
- The packet explicitly states that such STDOUT is command-console capture, not independent evidence.

Adjudication: REMEDIATED.

## SR-5 — Authority-root referenced inputs were not visible in the packet

Classification: STATIC-REVIEW VISIBILITY GAP

The referenced authority inputs are not generated E artifacts. Runtime resolution pins them by the preregistered authority commit and validates the declared hashes. The prior static packet did not include their contents.

Remediation:
- P resolves the authority commit from source S.
- P embeds the authority root, test expectations, signature, R5 protocol, retrieval ledger, delivery ledger, qualification ledger, and retrieval backing-source identity.
- P recomputes declared hashes and fails packet construction on mismatch.
- Git blob identities and SHA-256 values are included for static inspection.

Adjudication: REMEDIATED for static visibility.

## SR-6 — Reproducibility information was partial

Classification: REPRODUCIBILITY EVIDENCE GAP

Remediation:
- E records Python version/executable, platform, Git version, GitHub runner image metadata when available, and portable commands.
- E records an AST import audit across the frozen governed Python source.
- Evidence generation fails if an unexpected third-party Python import is found.
- The governed test surface declares zero third-party Python dependencies and no network requirement for test commands.
- P includes exact source checkout guidance and portable re-execution commands.

Adjudication: REMEDIATED for the governed Python/offline scope.

## SR-7 — Prior failure preservation cannot be independently verified from text alone

Classification: INHERENT STATIC-ONLY REVIEW LIMITATION plus EVIDENCE-VISIBILITY GAP

Independent recomputation of historical Git-object hashes inherently requires the Git objects. A static text handoff cannot itself provide independent proof of repository history.

Remediation:
- E now executes verify_exp_m_prior_evidence.py as a dedicated evidence command and preserves its stdout/hash.
- The full prior-evidence index remains embedded in P.
- The packet explicitly states that independent historical recomputation still requires the pinned Git objects and does not convert a static assertion into authority.

Adjudication: EVIDENCE VISIBILITY REMEDIATED; external independent historical recomputation remains intentionally outside the candidate's authority.

## Closure rule

These clarifications do not grant a PASS. After these changes, a fresh source S, evidence E, packet P, and handoff Q must be generated and the full offline falsification + S-E-P verification gates must pass. The next independent reviewer must review that fresh handoff.

Authority effect remains NONE. EXP-M remains NOT_QUALIFIED.
