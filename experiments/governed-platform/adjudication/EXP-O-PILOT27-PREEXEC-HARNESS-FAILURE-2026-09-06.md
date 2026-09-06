# EXP-O Pilot 27 — Pre-execution Harness Failure Record

## Run

GitHub Actions run `34034678775` at commit `564828fdab627e7105f8f29414507b68eb39f953`.

## Classification

TEST HARNESS / IMPORT-PATH DEFECT. NOT A PILOT 27 SCIENTIFIC EXECUTION AND NOT A DOMAIN-QUORUM MECHANISM FAILURE.

The new provider-neutral Pilot 27 module compiled successfully. The governance suite failed before executing its Pilot 27 assertions because `test_exp_o_pilot27_domain_quorum.py` imported `experiments.governed_platform...`, while the repository directory is `experiments/governed-platform` and is not an importable package under that dotted name in the harness execution layout.

Observed error:

`ModuleNotFoundError: No module named 'experiments'`

## Allowed repair

Only the test import/bootstrap mechanism may change so the already-committed provider-neutral module is loaded from its exact repository path. No Pilot 27 preregistered endpoint, domain-distinctness rule, threshold rule, canonical statement, authority rule, or provider requirement may be weakened or changed to obtain green CI.

## Scientific status

Pilot 27 remains PRE-EXECUTION / EXTERNALLY BLOCKED. This run created no external signing evidence and provides no scientific endpoint result.
