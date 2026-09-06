# EXP-O Pilot 3 — Post-hoc Trusted-Time Falsification Finding

Status: **POST-ADJUDICATION MECHANISM DEFECT DISCOVERED**

This record is additive. It does not rewrite or delete the original Pilot 3 preregistration, implementation, test evidence, or adjudication.

## Discovery point

Discovered after Pilot 3 adjudication commit `83ceb7f0ca3b7eef98cfeb5182ae2f1a468e05af`, while designing the next process/transport-boundary falsification stage.

## Defect

The Pilot 3 `LocalEnforcementPoint.authorize(...)` API accepts `now_ms` through the worker call path and uses it to decide capability expiry and cached-authority age. The Pilot 3 `McpGateway.execute(...)` API also accepts `now_ms` through the caller path and uses it to decide permit expiry.

Therefore the security decision is not structurally bound to an enforcement-side trusted clock in the frozen Pilot 3 implementation.

A malicious or compromised worker that can control the supplied `now_ms` could attempt to backdate time so an actually expired capability or LEP permit appears current to the single-host pilot implementation.

## Why the original green tests did not catch it

Pilot 3 pre-registered exact threshold, expiry-related structure, identity, scope, gateway bypass, crash/retry, and evidence tests, but its test harness itself supplied the synthetic `now_ms` values. It did not include an adversarial case where the worker lies about current time.

Thus `20/20` remains an accurate statement about the pre-registered cases, but it is not evidence that enforcement time is trustworthy.

## Scientific correction

The Pilot 3 conclusion is narrowed as follows:

- the observed capability/permit/scope/idempotency/evidence behavior passed **under the harness-supplied time assumption**;
- Pilot 3 does **not** establish secure expiry/freshness enforcement against a malicious worker-controlled clock;
- any broader statement that authority/permit expiry was externally trustworthy is unsupported by Pilot 3.

This is a mechanism defect, not a test defect.

## Required correction

The next implementation must:

1. remove request-controlled current time from security-sensitive LEP and gateway decisions;
2. obtain current time inside the trusted enforcement component/process;
3. allow deterministic tests to inject a clock only at trusted component construction/startup, never per worker request;
4. bind permits to an enforcement-side issued/expiry time;
5. reject expired permits using gateway-process time;
6. test worker attempts to supply forged/backdated time and prove it has no authority effect.

## Historical integrity

The frozen Pilot 3 implementation is retained unchanged as historical evidence. The fix must be implemented in a subsequent EXP-O stage so the repository preserves both the false-green boundary and the correction lineage.

## EXP-N isolation

This finding concerns only the EXP-O Pilot 3 runtime slice. It does not modify or reinterpret the frozen EXP-N Pilot 8/9 scientific execution paths.
