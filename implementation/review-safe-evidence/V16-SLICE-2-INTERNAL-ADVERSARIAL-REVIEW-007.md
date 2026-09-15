# V16 Slice 2 Internal Adversarial Review 007

Review target: exact V8 construction candidate `d793f342168f34d7874badac2dbaa44aece0e242` (tree `5b7c697afa5fc73b43aab9ffd0249eca23208cd7`) and successful construction run `34997335370`.

Review posture: falsification-first. The 77/77 parent-receipt construction result is preserved as evidence only. This review is internal/non-independent and creates no authority transition.

## Disposition

`CHANGES_REQUIRED`

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`V16_SLICE2_FREEZE_ALLOWED=false`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

## High finding

### IAR7-H1 — Parent receipt identity is protected, but successful completion is still self-grantable by the evaluated process

Affected surface: `.github/workflows/review-safe-evidence-v16-slice2-independence-v8.yml`, specifically the root-owned strict child runner and the parent rule that treats child `rc=0` as successful completion of the exact invoked test.

V8 correctly removed child stdout/stderr from the load-bearing execution-identity channel. The parent now supplies the exact test ID and writes the receipt. However, the root-owned runner executes the governed test and evaluated implementation in the **same Python process** whose exit status the parent trusts.

The runner performs its load-bearing checks only *after* `suite.run(result)` returns. Arbitrary evaluated Python code reached by the test can terminate or replace that process before control returns to those checks. For example, `os._exit(0)` can terminate the process with status zero; an equivalent successful replacement/termination path can bypass the post-`suite.run` validation entirely.

Concrete false-green path:

1. parent invokes exact declared test ID T;
2. trusted child runner loads T and enters `suite.run(result)`;
3. code reached by T calls an abrupt successful process-termination primitive before the test returns;
4. the runner never evaluates `result.started`, `result.succeeded`, failures/errors/skips, or `wasSuccessful()`;
5. the operating system reports child return code 0;
6. the parent records T with `rc=0` and, under the V8 rule, accepts that row as successful completion.

This differs from IAR6-H1. The receipt **identity** is now parent-controlled, so a forged console line cannot invent T. The remaining defect is that the **success bit** is still derived from a process that the evaluated code can terminate before the trusted runner reaches its success decision.

### Governing rule

A load-bearing success/completion claim must not be grantable merely by the process being evaluated. Parent-controlled invocation identity is necessary but insufficient when the evaluated process can cause the parent-observed success condition without returning control to the trusted assertion harness.

### Narrow required repair

Do not treat a bare zero exit status from the process that executes evaluated code as proof that the trusted assertion harness completed.

The successor execution design must place the assertion/completion authority outside the evaluated process boundary. At minimum:

1. evaluated implementation code must execute in a worker boundary that cannot terminate or replace the trusted assertion supervisor;
2. worker exit/disconnect, including exit code 0, is not itself a PASS;
3. the trusted supervisor must derive the test verdict after receiving the worker's bounded data result and applying the governed assertion/oracle outside the worker;
4. no worker-written console string, exit status, self-issued marker, or caller label may substitute for supervisor-side assertion completion;
5. abrupt exit, `exec*`, signal termination, worker crash, timeout, malformed result, missing result, and premature connection close must all fail closed;
6. add an adversarial mechanism probe that uses `os._exit(0)` before assertion return and proves it cannot create a successful trusted receipt;
7. preserve V8 as construction history and do not relabel it as invalid; V8 established identity/isolation improvements but not this stronger completion property.

If a fully externalized assertion boundary is not implemented in Slice 2, the limitation must remain explicit and Slice 2 must not claim that its construction test harness is resistant to arbitrary evaluated-process self-termination.

## Confirmed properties retained from V8

The following V8 observations remain valid construction evidence and are not revoked by this finding: exact pre/post governed-byte checks, root-owned read-only execution snapshot, non-repository-writer test principal, checkout inaccessibility from the test principal, 77 manifest/source identities, parent-controlled invocation IDs, forged-console rejection as execution identity, and strict current-manifest validation.

## Required next state

Reproduce IAR7-H1 with a bounded harness falsification probe, preserve the result, then either implement an external supervisor/worker assertion boundary or keep Slice 2 freeze blocked with the limitation explicit. Do not advance to independent review while this High remains open.

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
