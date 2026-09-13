# V24-I11-V6-R13 — Construction RED 001

Status: **PRESERVED RED / PROBE HARNESS DEFECT BEFORE INTENDED FALSIFICATION ENDPOINT**

Authority effect: `NONE_EVIDENCE_ONLY`

## Bound run

- Workflow run: `34769660994`
- Workflow head: `e755ce2b2b81b52d50891b4ed5a9c2f8d33844ec`
- Candidate commit: `94728f0bbf0564e5d9c2e4f8b11e600dffabee99`
- Candidate tree: `d15efec0a63e53866592e0961504495331d89025`
- Review authority snapshot: `8210f624b2109899aa3cc11afe9e746053cc83f8`

## Completed before failure

The following construction steps completed successfully before the RED endpoint:

1. exact candidate/review-authority fetch and identity checks;
2. external pinset construction, source verification, staging, and pre-execution sandbox verification;
3. candidate unittest suite executed as `NON_AUTHORITATIVE_DIAGNOSTIC_ONLY`;
4. trusted runtime/environment binding computation;
5. all six trusted external-oracle assertions completed successfully;
6. candidate-side external-oracle evidence validator accepted the external evidence structurally while remaining `qualified = false`.

These successes are construction evidence only and do not qualify R13.

## Failure endpoint

Step: `Falsify optimized-interpreter authority path`.

The probe invoked:

`python -O -I -S r13_trusted_oracle_launcher.py --help`

The launcher uses `argparse`. `--help` causes `parse_args()` to print help and terminate with exit code 0 before `require_launcher_runtime()` is reached. The probe therefore observed exit 0 and failed its expectation that the optimization guard reject the process.

## Classification

`PROBE_HARNESS_DEFECT_BEFORE_INTENDED_FALSIFICATION_ENDPOINT`

This run does **not** show that an optimized authority-bearing launcher invocation is accepted. The probe never reached the authority-bearing launch path. It also does not show the mechanism is safe: the intended attack still needs to be executed using a syntactically complete launch invocation under `python -O -I -S`.

## Narrow repair

Change only the optimized-interpreter probe so that it supplies the complete real launcher arguments used by the successful oracle run, while invoking the launcher with `-O -I -S`. Require:

- non-zero exit;
- explicit `R13_LAUNCHER_OPTIMIZATION_FORBIDDEN` diagnostic;
- no oracle evidence output file.

Do not change the R13 candidate or trusted launcher mechanism based on this harness failure.

The later forged-observer, R12 frame-introspection, exact-file admission, post-execution sandbox, and artifact steps were skipped because the workflow stopped at this harness failure. They remain unexecuted and must not be inferred PASS.

Scientific execution remains closed. Runtime qualification remains not claimed.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
