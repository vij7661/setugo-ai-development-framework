# RELEASE R1 Accelerator Stale-Expectation Repair Preregistration — 001

Status: FROZEN_BEFORE_REPAIR
Authority effect: NONE_EVIDENCE_ONLY

## Exposed candidate

`35d0b2e85e0779eb582d7968f67b06e05a5b493d`

## Frozen defect

The integrated PR suite exposed two stale expectations in `governance-runtime/test_governed_accelerator.py` that contradict the already-governed TESTING phase policy:

- TESTING review transport must be `MANUAL_ONLY`, not legacy `MANUAL`.
- `api_boundary_under_test` must not permit an external reviewer API in TESTING.

## Allowed repair

Only align the accelerator test expectations with the existing stricter `phase_policy.py` contract. Do not weaken `phase_policy.py`, do not re-enable TESTING external reviewer APIs, and do not grant any promotion or terminal authority.

Required repaired assertions:

1. expect `default_transport == "MANUAL_ONLY"`;
2. expect `external_api_allowed == False` even when `api_boundary_under_test == True`;
3. verify the explicit non-override marker remains false/closed where available;
4. rerun the exact candidate's integrated CI after the repair;
5. because this changes the candidate SHA, external RELEASE qualification must be rebound to the repaired exact successor before independent review.

A green result is evidence only and cannot erase the preserved RED.
