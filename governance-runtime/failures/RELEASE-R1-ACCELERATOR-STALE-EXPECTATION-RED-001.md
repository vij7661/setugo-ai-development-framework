# RELEASE R1 Accelerator Stale-Expectation RED — 001

Status: PRESERVED_RED
Authority effect: NONE_EVIDENCE_ONLY

## Exact exposed candidate

`35d0b2e85e0779eb582d7968f67b06e05a5b493d`

## Failing CI evidence

Workflow run: `34500926417`
Job: `accelerator-tests` (`102951208721`)

Observed failures:

1. `test_acc03_testing_packet_is_phase_explicit_and_manual_default`
   - expected legacy `default_transport == "MANUAL"`
   - actual governed phase policy returns `"MANUAL_ONLY"`

2. `test_acc03b_testing_api_allowed_only_when_explicitly_justified`
   - expected a TESTING API-boundary flag to permit `external_api_allowed == True`
   - actual governed phase policy deliberately prohibits external reviewer API use in TESTING, including when an API boundary is itself under test.

## Classification

TEST_EXPECTATION_DEFECT / STALE_TEST_CONTRACT.

The current `phase_policy.py` and its dedicated regression suite encode the stricter TESTING rule: manual-only review transport and no external reviewer API override. The accelerator tests retained pre-repair expectations and therefore correctly failed when PR #37 caused the broader integrated suite to run.

This RED is preserved before changing the stale tests. A later green must not erase this history.
