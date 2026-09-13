# V24-I11-V6-R14 — Native Import Diagnostic 001

Status: **RED-001 ROOT CAUSE RESOLVED / NO SECURITY RULE WEAKENING AUTHORIZED**

Authority effect: `NONE_EVIDENCE_ONLY`

## Diagnostic runs

1. Python-level audit-policy diagnostic: run `34775152210`, head `7ea8ee398c848c274d719fe45526140ecdd75c78` — the frozen candidate module imported successfully under the same import/event/path deny policy.
2. Embedded-CPython diagnostic: run `34775211830`, head `74b0c1659b4464a68be50607c1ce776559eb09ef` — the frozen candidate module also imported successfully when the setup-python 3.12.14 embedding environment resolved its own stdlib correctly.
3. Exact-source diagnostic clone: run `34775253020`, head `784224cb9d1a51f9953b69eb210cc7c8e2edb939` — reproduced RED-001 and printed the previously hidden Python exception from the exact R14 native source path.

## Exact root cause

The exact-source diagnostic showed the failing embedded interpreter loading:

`/usr/lib/python3.12/hashlib.py`

while the native executable had been compiled/linked against the GitHub setup-python 3.12.14 runtime under `/opt/hostedtoolcache/Python/3.12.14/x64`.

The mixed runtime caused `hashlib` initialization to fail with:

`ValueError: unsupported hash type blake2b`

`hashlib` then entered its fallback warning/logging path, which imported `threading`. The R14 audit policy correctly rejected that import:

`PermissionError: R14_AUDIT_IMPORT_BLOCK:threading`

The resulting candidate import failure was therefore downstream of an incorrectly rooted embedded stdlib, not evidence that legitimate R14 candidate code requires thread authority.

## Classification refinement

RED-001 classification is refined from:

`FAIL_CLOSED_NORMAL_CANDIDATE_IMPORT_DEFECT`

to:

`EMBEDDED_INTERPRETER_HOME_BINDING_DEFECT_FAIL_CLOSED`

This is an R14 execution-boundary configuration defect. It is not a candidate-code defect and not a false-green acceptance.

## Required repair

The next native observer revision must bind the child interpreter to the same trusted Python installation used to compile/link the native observer. It must not solve the failure by allowing `threading`, `_thread`, or any other previously denied escape surface.

The repaired mechanism should also expose/bind actual child interpreter state before candidate import so a later review need not trust a declared parent/launcher interpreter contract as a proxy for the child interpreter.

Scientific execution remains closed. Runtime qualification remains not claimed.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
