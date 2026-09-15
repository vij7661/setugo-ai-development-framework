# V16 Slice 2 IAR8 Repair Contract

Status: **REPAIR PREREGISTRATION / NON-AUTHORITATIVE**

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`

## Objective

Repair IAR8-H1 without weakening the IAR7 external-assertion boundary.

Supervisor response completeness is defined by EOF on all inherited protocol pipe writers, not by exit of the original worker PID.

## Required mechanism

The repaired bounded-read loop MUST:

1. start one monotonic deadline before worker execution;
2. keep stdout/stderr registered until each stream returns EOF;
3. continue reading after main worker exit while any inherited writer remains open;
4. enforce byte limits cumulatively across every inherited writer on each stream;
5. never parse a response before stream completeness is established;
6. if any protocol stream remains open at the deadline, mark timeout/failure and attempt process-group termination;
7. fail closed on oversized output, signal exit, nonzero exit, timeout, invalid response, or oracle mismatch;
8. preserve supervisor-side post-worker oracle evaluation and receipt issuance.

## Mandatory regressions

- valid response with no descendants => PASS construction-only;
- main worker exits 0 without response => fail closed;
- valid response then nonzero exit => fail closed;
- valid prefix + delayed descendant extra stdout => fail closed after complete stream capture;
- valid prefix + descendant holds stdout open beyond deadline => fail closed timeout;
- descendant adds bytes that cross stdout limit => fail closed overflow;
- original V1 14-case matrix remains stable.

## Explicit non-goal

This repair proves protocol-stream completeness only for inherited stdout/stderr handles as observed by the supervisor. It does not prove that arbitrary descendant processes cannot detach, close the protocol handles, and persist elsewhere.

`WORKER_DESCENDANT_PROCESS_ESCAPE_ENFORCEMENT=NOT_YET_PROVEN`

`WORKER_PROCESS_REPLACEMENT_OS_ENFORCEMENT=NOT_YET_PROVEN`

Those are separate sandbox obligations.

## Stopping rule

IAR8-H1 closes only after the exact prior falsification no longer returns supervisor PASS, the pipe-held-open deadline case fails closed, the original mechanism matrix remains green, and a subsequent internal adversarial pass finds no unresolved Critical/High in this repair.

`INTERNAL_ADVERSARIAL_REVIEW_EXHAUSTED=false`

`V16_SLICE2_FREEZE_ALLOWED=false`

`IMPLEMENTATION_QUALIFICATION=NOT_CLAIMED`

`RUNTIME_QUALIFICATION=NOT_CLAIMED`

`SCIENTIFIC_AUTHORITY=NOT_CLAIMED`

`AUTHORITY_EFFECT=NONE_EVIDENCE_ONLY`
