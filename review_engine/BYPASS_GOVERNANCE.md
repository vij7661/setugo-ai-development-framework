# Review Engine Bypass Governance

A bypass attempt is a falsification technique, never an implementation shortcut.

## Core rule

**No test, debug, compatibility, legacy, manual-relay, emergency, or convenience switch may weaken an authority-bearing production invariant.**

Bypass work must search for missing invariants from the outside. If an adversarial case succeeds, preserve that first failure, repair the underlying mechanism, freeze the adversarial case as a permanent regression, run the full suite, and obtain independent review when the bypass affects an authority boundary.

## Required lifecycle

`DISCOVERED -> PRESERVED -> MECHANISM_REPAIRED -> REGRESSION_FROZEN -> FULL_SUITE_GREEN -> INDEPENDENTLY_REVIEWED -> CLOSED`

`review_engine.bypass_governance.BypassRecord` enforces the evidence references required to advance through this lifecycle and forbids skipped/backward transitions.

For non-authority observations where independent review is not required, the record may set `independent_review_required=false`; the full-suite evidence requirement still applies. Authority, reviewer-independence, provider-identity, promotion, evidence, execution, mutation, or release-path bypasses require independent review before `CLOSED`.

## Evidence meanings

- `first_failure_ref` — immutable first red CI/test/evidence reference proving the pre-repair mechanism admitted the bypass.
- `repair_ref` — exact production-mechanism commit/reference. A test-only or fixture-only change cannot satisfy this field.
- `regression_ref` — frozen adversarial test reference preserving the attack.
- `full_suite_ref` — exact full-suite CI evidence after repair.
- `independent_review_ref` — governed independent-review evidence when required.

## Prohibited patterns

The following are not valid repairs on an authority-bearing path:

- `if test_mode: skip_governance()`
- `allow_legacy_bypass=true`
- catching validation failure and continuing anyway
- changing an expected rejection into acceptance merely to obtain green CI
- weakening a required invariant because a provider/reviewer is unavailable
- treating pasted/self-declared reviewer metadata as authenticated provenance

The repair target is the missing invariant, not the individual attack string.
