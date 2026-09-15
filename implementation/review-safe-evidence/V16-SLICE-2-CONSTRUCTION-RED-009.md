# V16 Slice 2 Construction RED 009

## Classification

`CODE_DEFECT / TRUSTED_COMPLETION_SELF_GRANT`

This record preserves a mechanically reproduced false-green in the V8 construction harness. A later repair or PASS MUST NOT erase, replace, or reclassify this RED.

## Predecessor mechanism under falsification

- V8 candidate commit: `d793f342168f34d7874badac2dbaa44aece0e242`
- V8 candidate tree: `5b7c697afa5fc73b43aab9ffd0249eca23208cd7`
- V8 construction run: `34997335370`
- V8 construction job: `104476767292`
- V8 result: `success` as construction evidence
- related finding: `IAR7-H1`

The V8 green result remains preserved as evidence that parent-controlled identity, read-only snapshot isolation, exact 77-test identity reconciliation, and governed-byte re-attestation worked. RED 009 narrows the unsupported claim: V8 did not establish that a zero child exit status proves the trusted post-test assertion path completed.

## Falsification run

- probe commit: `26fa9720f7279fda4f7bf0fe9d2fb55b4d9fc972`
- probe tree: `3762d8a0dab2c07a955cc3696e11befcc0a28970`
- workflow: `Review Safe Evidence V16 Slice 2 IAR7 Falsification`
- workflow run: `34997883796`
- job: `104478620018`
- workflow result: `success`

The falsification workflow is green because its intended success condition was to reproduce the predecessor defect. It is **not** a PASS of the V8 completion mechanism.

## Mechanically reproduced false-green

The synthetic exact test `probe_module.AbruptExitTests.test_abrupt_success` calls `os._exit(0)` while executing inside a V8-style strict child runner.

Observed facts:

- trusted runner reached its pre-suite point;
- evaluated test entered execution;
- evaluated code terminated the process with exit status 0;
- trusted runner never reached its post-suite assertion/check point;
- parent nevertheless observed `rc=0`;
- a V8-style parent receipt therefore had the same load-bearing zero return code that V8 treats as successful completion.

The run emitted:

`IAR7_FALSE_GREEN_REPRODUCED=YES`

`IAR7_PARENT_OBSERVED_RC=0`

`IAR7_TRUSTED_POST_SUITE_ASSERTION_REACHED=false`

`IAR7_PARENT_RECEIPT_WOULD_ACCEPT_ZERO_EXIT_UNDER_V8_RULE=true`

`IAR7_PROBE_DISPOSITION=MECHANISM_DEFECT_CONFIRMED_NONAUTHORITATIVE`

## Adjudication

IAR7-H1 is **CONFIRMED**.

The defect is not test-ID forgery. V8 repaired that earlier problem: the parent owns the exact requested test identity. The remaining false-green is the completion/success boundary. The evaluated process can terminate itself successfully before the trusted runner performs its post-suite checks, and the parent cannot distinguish that path from a normally completed successful child using exit code alone.

Therefore a child-generated marker, console line, nonce, signature, or status from the same evaluated process is not an adequate narrow repair. The assertion/completion authority must move outside the evaluated process boundary.

## Required repair boundary

The successor must use a trusted assertion supervisor that owns the oracle and final receipt while candidate/evaluated implementation logic executes in a separate worker boundary. Worker exit/disconnect — including exit status 0 — is not a PASS. The supervisor must receive bounded operation data and make the governed assertion after the worker interaction completes.

Mandatory failure cases include abrupt zero exit, nonzero exit, process replacement, signal termination, timeout, malformed/no response, wrong operation identity, forged console output, and self-declared PASS unsupported by the supervisor oracle.

## Authority boundary

`IAR7_H1=CONFIRMED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`V16_SLICE2_FREEZE_ALLOWED=false`

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
