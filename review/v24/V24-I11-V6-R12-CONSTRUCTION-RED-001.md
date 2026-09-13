# V24 I11 V6 R12 — Construction RED 001

Run: `34768505494`

Disposition: **CONSTRUCTION_HARNESS_SANDBOX_HYGIENE_DEFECT**

Authority effect: `NONE_EVIDENCE_ONLY`

## What passed before the failure

- exact R12 candidate resolution and external-authority separation;
- runtime-bound external pinset generation;
- exact source verification and sandbox staging;
- all eight exact-file attacks rejected;
- process-boundary attacks rejected for:
  - `unittest.TextTestRunner` monkeypatch;
  - `unittest.TestResult.wasSuccessful` monkeypatch;
  - direct `os._exit(0)`;
  - forged worker stdout;
  - trusted parent launched without required interpreter isolation;
  - interpreter-contract mismatch;
- canonical trusted-parent suite passed with `20` modules / `270` test cases;
- six exact mandatory adversarial checks executed and evidence-bound;
- R12 adversarial-evidence validator passed;
- R12 execution-boundary-evidence validator passed.

## Failure endpoint

The run failed only at `Post-execution exact sandbox verification`.

The preceding candidate-evidence validation step imported `v24_v6_r12_successor` from the staged sandbox in an inline Python process without first setting `sys.dont_write_bytecode = True`. Unlike the R12 untrusted worker, that inline validation process could therefore create `__pycache__/*.pyc` inside the exact-file sandbox. The unchanged post-execution guard correctly rejected the expanded sandbox.

## Classification

This is not evidence that the guard accepted a changed sandbox and not evidence of a candidate scientific failure. The post-check did exactly what the contract requires: it failed closed after sandbox mutation.

Narrow repair:
- preserve the exact post-execution fileset requirement unchanged;
- set `sys.dont_write_bytecode = True` before the construction-only inline candidate import;
- rerun the complete construction sequence, including every earlier attack and evidence check.

No prior RED/non-PASS evidence is removed or reclassified as PASS.

Scientific execution remains `CLOSED_PENDING_SUCCESSOR_REVIEW`.
Runtime qualification remains `NOT_CLAIMED`.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
