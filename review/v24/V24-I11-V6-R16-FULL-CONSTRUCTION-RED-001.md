# V24-I11-V6-R16 — Full Native Construction RED 001

Status: **PRESERVED RED / WORKFLOW STATE-PROPAGATION DEFECT BEFORE ORACLE/FALSIFICATION ENDPOINTS**

Authority effect: `NONE_EVIDENCE_ONLY`

## Bound run

- workflow: `V24 V6 R16 Full Native Construction`
- run: `34778014805`
- review-authority head: `ada4b71825b54296e055f53efda2d7f3abd7d930`
- frozen R16 candidate commit: `7c8ae745ff8270122c0cf05e123b8108af04eaad`
- frozen R16 candidate tree: `9d8db8766fee1eb76e24d62ca88d8b04ea8e3b58`

## Completed before failure

The following completed successfully:

1. exact candidate commit/tree binding and proof that R16 trusted authority objects are outside the candidate tree;
2. external exact-file pinset construction for **193** candidate/support files;
3. source verification, exact staging, and pre-execution sandbox verification;
4. trusted source inventory construction for five exact external authority inputs;
5. exact historical scenario-library Git blob verification;
6. trusted source-set digest construction;
7. hardened R16 native binary compilation;
8. linked-library inventory and digest construction.

Recorded pre-failure values include:

- pinset SHA-256: `cfd1cf82687ab77a1d1ba1dce41ac8a759da27ff56cb1acc4ed1c73fa5727366`
- guard runtime/interpreter digest: `eed7733f7032dd1f588cd048469130e52487335d2a7f32d2016cbc1d883d206b`
- trusted source-set digest: `7e13785fa0ef09ec5f678fd3a9eb9db15c13b34b399ab98dc79007ab4f00d0af`
- scenario library blob: `f0f72ca65eb443fd2db2917622a327256d15db05`
- scenario library SHA-256: `9ccb4e3329cbe5422bd6e56293865c794cc41252319c80968ad827c6917ef88e`
- R16 native observer blob: `820979bc1ede499d3b0db4a5f01d0955224d1472`
- R16 native observer source SHA-256: `d9ffd22f59441b28b2ec86ac408db6121eff28ac9883d5c2225277b26e25dd21`
- linked-library digest: `4b1d1172002943942bf2a2971f71731193328fad38650a6dd2be5ebcc374557c`

## Failure endpoint

Step: `Compile exact R16 native authority binary and bind environment`.

A Python helper correctly computed `LINKED_LIBRARIES_DIGEST` and appended it to `$GITHUB_ENV`. The same shell step then immediately referenced `$LINKED_LIBRARIES_DIGEST` while constructing the environment digest.

GitHub Actions applies values appended to `$GITHUB_ENV` only to **subsequent steps**, not later commands inside the same current shell. With `set -u`, the current shell therefore failed with:

`LINKED_LIBRARIES_DIGEST: unbound variable`

## Classification

`WORKFLOW_STATE_PROPAGATION_DEFECT_BEFORE_ORACLE_ENDPOINT`

This is not evidence of a candidate, native-confinement, oracle, or secret-separation mechanism defect. The six external-oracle scenarios and all fifteen R16 falsification probes were skipped and must not be inferred PASS.

## Narrow repair

Capture the linked-library digest into a current-shell variable (or split the environment-binding logic into the following workflow step) while continuing to persist it through `$GITHUB_ENV` for later steps. Do not alter candidate bytes, trusted source bytes, compiler hardening, pinning, confinement, oracle policy, or falsification expectations.

- scientific execution: `CLOSED_PENDING_SUCCESSOR_REVIEW`
- runtime qualification: `NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
