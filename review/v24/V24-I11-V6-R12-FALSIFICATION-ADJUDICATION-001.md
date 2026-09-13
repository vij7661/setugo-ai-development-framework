# V24 I11 V6 R12 — Falsification Adjudication 001

Status: **R12 REJECTED / R13 REQUIRED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Bound R12 candidate

- commit: `e887613f4e9012be59dcd8c4840035748ee0de7e`
- tree: `c584cf728ca70c663ba04cf4bfb50fd29f5f1e0f`
- successful construction run before stronger falsification: `34768595774`
- stronger falsification run: `34769043441`
- falsification artifact ID: `10320624212`
- falsification artifact SHA-256: `0ddecf025f15888dfcd9ab588cd05854ff3792db253256c63e5044a935f3d687`
- inner falsification record SHA-256: `0add6013ab11177f5cc9fcc1109daa3690012456bffa6a76ff2eee28aa70b81b`

## Critical mechanism defect — same-process introspection defeats worker canaries

**Accepted / Critical / `FAIL_CODE_DEFECT`.**

R12 correctly moved the trusted parent outside the candidate process, but it still allowed candidate-controlled Python test modules to execute in the same interpreter process as the R12 worker that produced the structured result envelope consumed by the parent.

A malicious admitted test module used `sys._getframe()` to walk the worker's active call stack and obtain:

- the worker's pre-import `baseline` framework fingerprint; and
- the locally captured `trusted_runner_cls` object.

The candidate module then modified the running worker through `__main__`:

1. replaced `framework_fingerprint` so all later integrity checks returned the stolen pre-import baseline;
2. replaced `_internal_negative_canary` so later canary checks always returned `True`;
3. replaced `trusted_runner_cls.run` with a forged runner result reporting `testsRun=1`, zero failures/errors/unexpected successes;
4. supplied a real `unittest.TestCase` whose body deliberately fails.

Because the result envelope was still produced inside the candidate-compromised worker process, the trusted parent accepted the forged envelope as a successful module result.

The evidence-bearing falsification run exactly pinned and staged these malicious bytes before execution. The observed parent result was:

- parent return code: `0`;
- normal `R12_PARENT_RESULT` emitted;
- `result_accounting_origin: TRUSTED_PARENT` asserted;
- `trusted_parent_imported_candidate: false` asserted;
- `false_green_reproduced: true`;
- observed behavior: `ACCEPTED_FORGED_PASS`.

This disproves the R12 construction claim that worker canaries plus parent-side envelope validation are sufficient to make candidate-side unittest results qualification-safe.

## Why the earlier R12 construction PASS remains historical but insufficient

Run `34768595774` genuinely passed the attack set it executed, including direct `TextTestRunner` monkeypatch, `TestResult.wasSuccessful` monkeypatch, direct `os._exit(0)`, forged stdout, missing isolation flags, and runtime-contract mismatch.

The stronger attack demonstrates that those probes did not span the full same-process mutation surface. The successful run is therefore preserved as construction evidence for the tested paths, but it cannot support R12 successor acceptance or scientific execution opening.

No earlier evidence is deleted or rewritten.

## Required R13 structural property

R13 must not attempt another same-process integrity-canary patch around candidate-controlled unittest execution.

For any qualification-contributing check:

- trusted assertion/oracle logic must execute in a process/address space that never imports or executes candidate-controlled Python;
- candidate-side Python may return only untrusted domain observations/outputs/errors, never a PASS/FAIL decision that can directly satisfy qualification;
- the trusted external oracle must derive PASS/FAIL from those untrusted observations and independently held expectations/invariants;
- candidate-side test modules and candidate-side `unittest` results may remain construction diagnostics, but they are `NON_AUTHORITATIVE_DIAGNOSTIC_ONLY` and cannot satisfy mandatory qualification evidence;
- the six mandatory V6 adversarial checks must be migrated to external trusted assertions rather than candidate-side unittest outcomes;
- runtime-generated challenge material should be used where practical so the authoritative oracle is not reduced to checking candidate-known static fixture labels;
- the R12 frame-introspection exploit becomes a mandatory regression target and must be incapable of producing qualification evidence even if the candidate process emits a syntactically valid success payload.

## State transition

- R12: `REJECTED`
- R12 manual successor review package: `CANCELLED_KNOWN_BLOCKER`
- R13: `REQUIRED`
- scientific WDPC: `CLOSED`
- runtime qualification: `NOT_CLAIMED`
- automated external reviewer APIs during TESTING: `PROHIBITED`

A new successor branch is required. R12 must not be patched in place.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
