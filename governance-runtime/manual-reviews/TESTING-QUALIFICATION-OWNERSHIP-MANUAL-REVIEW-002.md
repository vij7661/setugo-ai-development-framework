# Manual TESTING Re-falsification Addendum — Authority Ingress and Phase Conflict

Review ID: `TESTING-QUALIFICATION-OWNERSHIP-MANUAL-REVIEW-002`
Review mode: **MANUAL ONLY — NO EXTERNAL REVIEWER API**
Reviewed candidate: `db29be705f2404976122f157679d9f6578e3a9a0`
Phase: `TESTING`
Disposition: `CHANGES_REQUIRED`
Authority effect: `NONE_REVIEW_EVIDENCE_ONLY`

## Context

The corrected harness preserved genuine RED at `d415d60cbb29d1943ef926fea384aa91c9be2043` / run `34438867816`. The subsequent construction repair replaced naked privileged role strings with sealed `AuthorityBinding` values and moved phase resolution to a platform-owned rule-to-phase map. Construction run `34439504323` on `9fcce813ac92b369d5ce30bb7e9afbd197fffa6c` was green with the frozen four attacks actually executed.

This addendum attempts to falsify the new trust boundary itself. Green CI remains evidence only.

## Finding MR-003 — Trusted authority ingress is candidate-callable in the same Python trust domain

Severity: **CRITICAL**
Material: **true**
Phase classification: `BLOCK_TESTING`
Affected cases: `QO-05`, `QO-06`, `QO-07`

### Failure path

`qualification_boundary_policy.py` contains `_issue_authority_binding_for_platform_ingress(...)` and the process-local sealing key in the same importable module as the verifier. Python's leading underscore is a convention, not access control. Code with ordinary import/call access to that module can invoke the issuer directly, request a privileged authority class and decision scope, provide any `evidence_ref`, and receive a valid HMAC-sealed binding that the verifier accepts.

The repair therefore prevents spoofing by raw serialized role text, but it does not yet prove that the authority issuer is outside the evaluated actor's callable trust domain.

### Required repair boundary

The privileged issuer/signing capability must live outside candidate-callable code. The governed runtime may contain only a verifier plus the public/trusted verification material. Creation of a privileged manual-governance attestation must require an authority action outside the evaluated process/trust domain. A local private function or secret readable by candidate-executed code is insufficient.

This is the point at which a real manual authority setup may be required. No automated reviewer/API may substitute for it in TESTING.

## Finding MR-004 — Contradictory legacy phase label is silently ignored when rule ID exists

Severity: **MEDIUM**
Material: **true**
Phase classification: `BLOCK_TESTING`
Affected case: `QO-08`

### Failure path

`phase_disposition(...)` correctly rejects `violated_contract_phase` when no governed `violated_rule_id` is supplied. But if both are supplied, a valid rule ID is used while a contradictory caller phase label is silently ignored.

This does not currently create a direct deferral when the governed rule maps to TESTING, but accepting contradictory governance inputs creates ambiguity and permits consumers/logs to disagree about which phase claim governed the decision.

### Required narrow repair

Any non-null `violated_contract_phase` compatibility input must fail closed as `REQUIREMENT_UNRESOLVED`, even when a governed rule ID is also present. There must be one authoritative phase source: the platform-owned governed-rule map.

## Acceptance posture

Freeze executable attacks for MR-003 and MR-004 before further mechanism changes. Repair MR-004 autonomously. MR-003 must remain blocking until authority issuance is demonstrably outside the evaluated actor's callable trust domain and a manual governance path exists to create/attest the trusted authority evidence.
