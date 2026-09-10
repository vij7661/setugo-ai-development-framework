# RELEASE R3 Policy-Version Expectation RED 001

Status: PRESERVED_RED / PREREGISTERED_NARROW_REPAIR
Authority effect: NONE_EVIDENCE_ONLY

## Subject

Exact candidate SHA exposed by PR #37 before repair:
`35187768376958cdc103f96ee0594608e86fdaac`

Workflow run:
`34508645759` (`RELEASE R1 Hardening`)

## Observed failure

The frozen RELEASE R1 regression suite reached `test_policy_binding_is_deterministic_and_nonempty` and failed because the legacy test asserted:

`qualification_policy_version == 6`

The active compatibility facade now intentionally points to policy v7 after the separately preregistered RELEASE trust-root separation repair.

## Classification

`TEST_EXPECTATION_DEFECT / STALE_TEST_CONTRACT`

The failure does not indicate that policy v7 returned a wrong version. It indicates that the regression expectation was pinned to the previous authoritative policy version and therefore correctly went RED when the governed policy version changed.

## Frozen repair boundary

Only the stale expected policy version in `governance-runtime/test_qualification_boundary_policy.py` may change from `6` to `7` for this repair.

The repair MUST NOT weaken:
- exact policy-hash binding;
- phase-scoped trust-root separation;
- RELEASE authority scope;
- TESTING root restrictions;
- terminal action restrictions;
- any prior adversarial case.

After repair, the exact successor SHA must be rerun through the RELEASE R1 regression suite and RELEASE R3 phase-scoped authority suite. This RED remains preserved regardless of later green evidence.
