# V24-I11-V6-R12 — Consolidated Remediation Contract

Status: **IMPLEMENTATION AUTHORIZED / SCIENTIFIC EXECUTION CLOSED**

Base candidate: `68ce0df63ce0133ae19ec4402b41c4c09adfb54e`
Base tree: `d202b039285213b386557083a26de42e0fb20cf4`

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Purpose

R12 is a successor to rejected R11. It must repair the three adjudicated execution/evidence false-green paths without weakening R11 exact-file pinning or altering unrelated V6 H–P mechanisms.

R12 must not grant runtime, release, deployment, or scientific authority. WDPC remains closed until construction evidence, clean manual successor review, and repository adjudication complete.

## 2. Mandatory repair R12-R1 — trusted/untrusted process separation

Qualification-contributing candidate code and tests MUST execute only in an untrusted child process.

The trusted parent/orchestrator MUST:
- start before candidate bytes are importable;
- never import candidate modules or candidate test modules;
- own final qualification-contribution accounting;
- treat child stdout, stderr, exit status, files, JSON, and other outputs as untrusted evidence inputs;
- reject malformed, missing, duplicated, replayed, mismatched, or self-authorizing child evidence;
- prevent candidate monkey-patching of trusted parent `unittest`, result classes, `sys`, stdout/stderr handlers, exit helpers, or process-global state from affecting parent accounting.

A zero child exit code alone MUST NOT authorize PASS.

## 3. Mandatory repair R12-R2 — actual interpreter/runtime verification

Before any candidate-controlled execution, the trusted parent MUST independently verify actual runtime posture rather than trusting pinset declarations.

At minimum verify and bind:
- isolated startup posture;
- no-site posture;
- environment-ignore/safe-path posture required by the authorized execution contract;
- exact Python executable identity/path as authorized;
- exact Python version/build identity used for stdlib-shadow policy;
- candidate/sandbox paths absent from trusted-parent startup import path;
- trusted authority objects resolved outside candidate/sandbox paths.

Mismatch MUST fail closed before candidate execution contributes evidence.

The child MUST be launched with an explicit clean environment and authorized isolated startup flags. Parent evidence MUST record the exact child runtime identity and startup contract actually observed.

## 4. Mandatory repair R12-R3 — executed adversarial-check evidence binding

`mandatory_v6_adversarial_checks` name-only membership MUST NOT satisfy integrated-successor completeness.

Each required adversarial check MUST bind an executed evidence record containing at least:
- exact check ID;
- exact candidate commit and tree;
- exact execution environment/interpreter contract digest;
- run/round identity;
- terminal state and result;
- evidence digest;
- producing execution identity;
- independent witness/authority identity where required;
- freshness/currentness binding where applicable.

The integrated successor binding digest MUST commit to the evidence records themselves, not only to sorted check-name strings.

Missing, extra, duplicate, stale, mismatched, unexecuted, self-authored, name-only, or replayed evidence MUST fail closed.

## 5. R11 protections that MUST be preserved

R12 MUST preserve or strengthen:
- exact candidate commit/tree binding;
- exact admitted path + Git blob SHA-1 + raw SHA-256 + role pinning;
- executed-test selection from external authority, not candidate metadata;
- support-object pinning;
- source and sandbox exact-fileset equality;
- symlink rejection;
- bootstrap/stdlib shadow rejection;
- pre/post execution verification;
- no bytecode/cache expansion in authoritative sandbox state;
- external pinset/runner/parent origin outside candidate authority;
- append-only preservation of all historical RED/non-PASS evidence;
- `AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`.

## 6. Required adversarial construction tests

R12 construction MUST demonstrate fail-closed behavior for at least:

1. candidate monkey-patches `unittest.TextTestRunner`;
2. candidate monkey-patches `unittest.TestResult.wasSuccessful`;
3. candidate mutates `sys.stdout`/`sys.stderr` or emits forged structured PASS output;
4. candidate exits zero without valid executed evidence;
5. candidate calls direct exit helpers or terminates abnormally;
6. parent launched without required isolated/no-site/runtime posture;
7. child launched under wrong interpreter version/build;
8. candidate attempts stdlib/bootstrap shadow under mismatched runtime assumptions;
9. required adversarial check name present but no evidence record exists;
10. evidence record check ID/candidate/tree/environment/result digest mismatch;
11. stale/replayed adversarial evidence from another run/round/candidate;
12. candidate-authored or candidate-modifiable external evidence/pinset/parent object;
13. missing/extra/swapped/symlinked admitted file;
14. post-execution mutation or fileset expansion.

## 7. Evidence/accounting rule

No construction PASS, test count, verification JSON, workflow status, or reviewer label can independently grant qualification. All such outputs are evidence to challenge.

R12 scientific execution state remains:

`CLOSED_PENDING_R12_SUCCESSOR_REVIEW`

Runtime qualification remains:

`NOT_CLAIMED`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
