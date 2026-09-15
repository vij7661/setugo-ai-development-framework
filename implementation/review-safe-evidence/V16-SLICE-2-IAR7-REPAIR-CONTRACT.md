# V16 Slice 2 IAR7 Repair Contract

Status: **REPAIR PREREGISTRATION / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

## Objective

Repair IAR7-H1: a zero exit code from the same process that executes evaluated Python code must not be sufficient to create a trusted test-completion receipt.

## Frozen observations

The repair MUST preserve the V8 improvements already demonstrated at run `34997335370`:

- exact manifest/source identity derivation;
- root-owned read-only execution snapshot;
- non-repository-writer evaluated principal;
- inaccessible repository checkout from that principal;
- parent-controlled exact test identity;
- diagnostic-only child stdout/stderr;
- strict manifest/source/receipt set equality;
- pre/post governed-byte and worktree re-attestation;
- all historical REDs and evidence records.

## Required execution architecture

The successor harness must separate two responsibilities:

1. **trusted assertion supervisor** — owns the test identity, expected oracle/assertion, timeout, receipt, and final success decision;
2. **evaluated worker** — may execute candidate implementation logic and return bounded data, but cannot grant PASS through its own exit status, console output, or self-issued marker.

A worker process exiting 0 without a complete supervisor-validated result MUST be failure, not success.

## Mandatory falsification cases

Before the repair may be called construction-green, the harness must demonstrate fail-closed behavior for at least:

- worker calls `os._exit(0)` before returning a result;
- worker exits nonzero;
- worker performs `exec*`/replacement and closes the expected channel;
- worker is killed by signal;
- worker times out;
- worker returns malformed result data;
- worker returns no result;
- worker returns a result for a different requested operation/test identity;
- worker emits forged unittest-looking success text;
- worker emits a self-declared `PASS` field unsupported by the supervisor oracle.

Only the trusted supervisor may write the load-bearing receipt row.

## Scope rule

If current test architecture cannot externalize assertion logic without a substantial rewrite, do not weaken this contract by adding another child-generated success token. A marker, nonce, signature, or status produced from inside the evaluated process is not by itself an independent completion proof when arbitrary evaluated code shares that process.

A bounded predecessor-mechanism falsification probe is permitted before implementation of the externalized assertion architecture. Such a probe is evidence of the defect, not a qualification result.

## Stopping rule

The repair remains open until:

- the predecessor false-green is mechanically reproduced and preserved;
- the successor boundary causes every mandatory premature-termination case to fail closed;
- normal governed cases still run under exact-byte/snapshot binding;
- another internal adversarial pass finds no unresolved Critical/High in this repair family.

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`V16_SLICE2_FREEZE_ALLOWED=false`

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
