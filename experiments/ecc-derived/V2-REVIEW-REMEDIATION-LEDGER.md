# ECC-Derived Program — V2 External-Review Remediation Ledger

Status: **BOUNDED REMEDIATION COMPLETE — EXTERNAL RE-REVIEW REQUIRED**

Authority effect: **NONE_EVIDENCE_ONLY**

Parent reviewed experiment-family candidate: `c45994259de99565faab54cf616058e218628846`

External AI review evidence:
- context: `CLEAN_PACKET_ONLY_CONTEXT`
- evidence class: `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`
- disposition: `CHANGES_REQUIRED_BEFORE_IMPACT_ADJUDICATION`
- freeze recommendation: `DO_NOT_FREEZE_EXPERIMENT_EVIDENCE`
- raw review SHA-256: `09d5c00f7740cdbd771c6cd1d9393c7823292d7edd5d59e8702ca431beaca67d`
- manual-review threshold contribution: `0`

## Methodology repair

The reviewer identified that the original 86 executable named cases were implemented after the first reference mechanism existed. V2 therefore froze the exact additional executable reviewer-remediation harness **before any mechanism change**.

Frozen v2 executable-harness commit:
`387a32ae3dba3b92fff28b747cd294827fdba893`

Pre-repair run:
- workflow run `34689754450`
- job `103542823956`
- exact checkout verified: `387a32ae3dba3b92fff28b747cd294827fdba893`
- tests: `132`
- result: `17 failures + 2 errors`
- mechanism was unchanged from the reviewed v1 family when the harness was frozen and executed.

Repair candidate:
`e176df47dd1faca4eca5437095c5bc55b09e4a4d`

Repair run:
- workflow run `34689873921`
- job `103543142617`
- exact checkout verified: `e176df47dd1faca4eca5437095c5bc55b09e4a4d`
- tests: `132`
- result: `132/132 PASS`

## Per-experiment V2 disposition

| Experiment | V1 review recommendation | V2 bounded disposition | Remaining integration boundary |
|---|---|---|---|
| EXP-ECC-1 | `NARROW_REQUIREMENT_CANDIDATE` | `NARROWED_REFERENCE_MECHANISM_PASS` | live platform-attested enforcement-point receipts and TOCTOU/process identity |
| EXP-ECC-2 | `NARROW_REQUIREMENT_CANDIDATE` | `NARROWED_REFERENCE_MECHANISM_PASS` | machine-derived executable/runtime semantics against real hook/adaptor paths |
| EXP-ECC-3 | `NARROW_REQUIREMENT_CANDIDATE` | `NARROWED_REFERENCE_MECHANISM_PASS` | live harness identity and per-capability qualification attestation |
| EXP-ECC-4 | `NARROW_REQUIREMENT_CANDIDATE` | `NARROWED_REFERENCE_MECHANISM_PASS` | authenticated platform activation issuance/revocation at runtime |
| EXP-ECC-5 | `NARROW_REQUIREMENT_CANDIDATE` | `NARROWED_REFERENCE_MECHANISM_PASS` | secret-safe cryptographic live configuration attestation and runtime rebinding |
| EXP-ECC-6 | `DEFER_PENDING_INTEGRATION_EVIDENCE` | `DEFER_PENDING_INTEGRATION_EVIDENCE` | real provider/gateway identity and authenticated manual-review attestation; automated reviewer transport remains disabled in testing |
| EXP-ECC-7 | `DEFER_PENDING_INTEGRATION_EVIDENCE` | `DEFER_PENDING_INTEGRATION_EVIDENCE` | integration with the actual claim/dependency/retraction governance pipeline |

## Reviewer false-green paths now covered by frozen executable cases

- spoofed worker execution receipt;
- verification/action TOCTOU sequence mismatch;
- hook-process replacement;
- declared blocking policy over a runtime fail-open path;
- hidden disable flag;
- generated documentation stronger than runtime semantics;
- unverified executable profile;
- incomparable capability classes represented by explicit per-capability allowed sets;
- unattested harness identity and post-qualification downgrade;
- forged activation authority;
- cross-project activation replay;
- approval-to-activation revocation race;
- canonical config digest forgery/recomputation;
- secret-redaction identity collision;
- DNS/runtime endpoint rebinding;
- unauthenticated cross-provider identity claim;
- forged manual-review attestation credit;
- egress consent-sequence replay;
- self-asserted learning support;
- incomplete retraction/dependency traversal;
- stale learned-artifact session injection.

## Nonclaims

The V2 green result remains a bounded deterministic/reference result. It does **not** prove production/V18 integration, live external harness enforcement, cryptographic provider identity in production, qualifying external-review transport, independent manual review, or terminal authority.

No requirement is automatically promoted by this ledger. A fresh external re-review is required before any governed impact-adjudication step.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
