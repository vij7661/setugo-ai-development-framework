# EXP-M R2 External Review Adjudication and Remediation

## Disposition of the supplied review

The external review disposition `CHANGES_REQUIRED` is accepted.

The Critical finding C-01, High findings H-01 through H-05, and Medium/Low findings M-01 through M-03 were evaluated as valid and have been incorporated into the preregistration/design.

This record does not claim independent closure. It documents the design response that is being submitted for R3 review.

## Finding adjudication

| Finding | Evaluation | Remediation |
|---|---|---|
| C-01 incomplete ReviewRequest can narrow required evidence | VALID / CRITICAL | Added independently derived `RequiredEvidenceContract`, mandatory-dimension and required-interaction closure. ReviewRequest is now a declaration checked against platform-derived governing requirements. Ambiguous derivation fails closed. |
| H-01 dirty reused provider session | VALID / HIGH | Material reviews require a fresh stateless request or fresh stateful session, unless all prior semantic context is completely governed. Ungoverned prior messages/tools/memory/custom instructions/connectors disqualify the attempt. |
| H-02 no statistical provider-qualification rule | VALID / HIGH | Added default preregistered policy: >=59 fresh independent trials per claimed point, zero hard failures, one-sided 95% exact-binomial lower bound ~>=0.95, 80% safety-margin cap, 7-day/drift-triggered requalification. |
| H-03 provider-injected semantic context unbound | VALID / HIGH | Provider capability profile now covers mutable default/custom prompts, memory and knowledge connectors. Unknown mutable semantic context => NOT_QUALIFIED_FOR_MATERIAL_REVIEW. |
| H-04 sparse witness coverage | VALID / HIGH | Added dense accessibility policy: deterministic range/retrieval proof or <=2048-byte probed text segments; opaque files require page/range/member-level probes or deterministic logs. Sparse head/middle/tail alone cannot qualify full content. |
| H-05 missing adversarial families | VALID / HIGH | Added explicit falsification/mutation tests for incomplete ReviewRequest, dirty sessions, provider semantic-context drift, insufficient/flaky capability trials, sparse-canary gaps, interaction omissions, and post-response expiry. |
| M-01 permissive where-available wording | VALID / MEDIUM | Load-bearing unavailable information now fails closed; provider/mode cannot claim the identity/accessibility property when required evidence is unavailable. |
| M-02 proposer-authored interaction list | VALID / MEDIUM | Added independently derived `RequiredInteractionContract`; proposer/subreview plans are checked against it. |
| M-03 expiry after wire before verdict | VALID / LOW-MEDIUM | Capability, egress and session state are explicitly revalidated immediately before verdict admission. |

## New governed structures

### RequiredEvidenceContract

Derived by the pinned delivery governor from:

- governing standards;
- experiment/qualification contract;
- protected-transition classification;
- mandatory review dimensions;
- platform-owned evidence-selection rules.

The ReviewRequest must fully cover this contract.

### RequiredInteractionContract

Derived independently from:

- mandatory dimensions;
- governing standards;
- evidence relationships;
- protected-transition rules.

Decomposed review cannot omit platform-required cross-evidence interactions.

### Clean material-review context

Material review uses:

- fresh stateless request; or
- fresh provider thread/session with no prior ungoverned semantic content.

Mutable provider memory, custom instructions, account/project knowledge connectors, or other provider-injected semantic context must be disabled/inventoried and profile-bound. If not, the provider/mode is not qualified.

### Default provider capability statistical policy

Unless a stricter provider-specific policy is independently preregistered:

- minimum 59 independent fresh trials per claimed operating point;
- 0 hard delivery/accessibility failures;
- one-sided 95% exact-binomial lower confidence bound approximately >=0.95;
- ambiguous/timeout/unverifiable trial counts as failure;
- qualified limit <= largest qualifying tested point;
- additionally <=80% of the smallest observed failure boundary;
- if no failure boundary is observed, <=80% of largest fully tested passing point;
- default expiry 7 days;
- immediate requalification on material provider/model/deployment/account/endpoint/region/adapter/session/file behavior drift.

### Dense accessibility policy

When deterministic truncation/range evidence is unavailable:

- sparse head/middle/tail canaries are insufficient;
- raw text qualification has <=2048 UTF-8 bytes per probed segment;
- fresh independent witness framing applies at every segment boundary;
- content locations are randomized across qualification trials;
- opaque attachments require page/range/member-level probes or deterministic provider retrieval/access logs;
- unprobed required content remains context-incomplete.

### Verdict-time revalidation

Immediately before admitting a verdict, the platform revalidates:

- provider capability profile;
- egress authorization;
- provider session/file state;
- prompt/evidence-isolation prerequisites.

Post-response expiry or revocation cannot be hidden by a stale preflight result.

## New/expanded falsification coverage

EXP-M now includes explicit tests for:

- ReviewRequest missing a standard-required evidence ref;
- ReviewRequest missing a mandatory dimension;
- dirty reused provider thread with prior messages;
- prior tool output in session;
- provider custom/default prompt drift;
- provider memory enabled;
- provider-side knowledge connector enabled;
- fewer than 59 capability trials;
- one hard failure among capability trials;
- omitted safety margin;
- sparse-canary internal-gap omission;
- dense per-segment witness failure;
- opaque attachment with unprobed required pages/ranges;
- omitted platform-derived interaction family;
- capability expiry after provider response but before verdict admission;
- egress/session invalidation after response before verdict admission.

## Self-check after remediation

A fresh adversarial design pass was performed on the R2 repairs.

No new Critical/High defect was identified in the specific repaired boundaries.

Remaining limitations are deliberately bounded:

- EXP-M is still design/preregistration only;
- no provider capability has been scientifically qualified;
- no implementation has been accepted;
- the numeric capability policy is intentionally conservative and may be revised only through a new governed preregistration/review boundary;
- fixed opaque provider service-level safety behavior remains a provider nonclaim; mutable provider/account/session semantic context must be controlled or the mode is disqualified;
- this adjudication is not independent review.

## R3 readiness

Disposition for handoff:

`READY_FOR_R3_INDEPENDENT_DESIGN_REVIEW`

No authority effect.
No EXP-M qualification.
No current API review is retroactively validated.
