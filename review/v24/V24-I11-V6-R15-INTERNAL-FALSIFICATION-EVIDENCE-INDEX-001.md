# V24-I11-V6-R15 — Internal Falsification Evidence Index 001

Status: **INTERNAL EVIDENCE REFERENCE / NO AUTHORITY EFFECT**

Authority effect: `NONE_EVIDENCE_ONLY`

## Purpose

This file separates detailed falsification evidence from the reviewer-facing R15 manual-review projection. It does not reproduce exploit procedures. It binds the raw review source by content hash and identifies which findings require controlled engineering follow-up.

## Raw independent review binding

- Source attachment: `Pasted text(20260913-191112).txt`
- SHA-256: `1f09d459550a7c2f6f63232b65de38c2261012bf149dfe45bb03ee965d4b9095`
- Candidate commit: `2e875bb29be48d39c9be6f3525d4f4610869848c`
- Candidate tree: `d2c9c0c85564808941fdb54cfbbd53f51f5397ee`
- Review disposition: `NEEDS_REVISION`
- Content binding: `CONSISTENT`
- Cryptographic recomputation in reviewer context: `NOT_VERIFIED`

## Controlled engineering evidence classes

### E1 — Directory-relative effective-path bypass

Maps to safe projection finding `R15-C1`.

Engineering reproduction should remain in a controlled falsification harness. Reviewer-facing documents should contain only the effective-path resolution defect, affected mechanism, governing rule, and expected fail-closed property.

Required regression identity:
`OS_OPEN_DIR_FD_PROC_SELF_MEM_REJECTED`

Required evidence properties:
- exact candidate commit/tree binding;
- exact trusted native source/binary identity;
- exact interpreter/environment binding;
- proof that the forbidden operation reached the intended policy endpoint;
- no authenticated native observation emitted;
- preserved historical REDs and harness-defect classifications.

### E2 — Candidate-readable authentication secret / forged-observation class

Maps to safe projection finding `R15-C2`.

Engineering evidence should prove the repaired design keeps authority-bearing authentication material outside candidate-readable state. Reviewer-facing material should not contain procedural secret-recovery or frame-forgery instructions.

Required regression property:
Even under hostile candidate execution with process-memory/introspection attempts, no candidate-originated observation can satisfy the native authentication and external-oracle authority path.

### E3 — Oracle scenario-library substitution

Maps to `R15-H1`.

Required regression property:
Substitution of scenario-library bytes must be rejected before scenario execution; the oracle must bind exact scenario-library identity at runtime.

### E4 — Native source-set completeness

Maps to `R15-H2`.

Required evidence property:
Every source file contributing to the trusted native binary must be individually content-bound, including inherited transport/runtime-binding sources, compiler identity, final binary identity, and candidate/environment context.

### E5 — Race-free effective-path confinement

Maps to `R15-M1`.

Required evidence property:
Restricted process-memory targets remain unreachable even under alias/path mutation attempts; the mechanism must not rely on a separable check-then-use path resolution sequence.

### E6 — Non-`open` memory/introspection routes

Maps to `R15-M2`.

Required evidence property:
The reachable candidate-side native-memory/introspection surface must be enumerated and tested. Unsupported or ungoverned representation classes must fail closed.

## Separation rule going forward

1. **Reviewer-facing package:** findings, severity, affected file/function, governing rule, evidence summary, narrow repair, and disposition.
2. **Internal falsification evidence:** exact test harnesses, hostile fixtures, operational reproduction detail, raw logs, artifact hashes, and attack-specific mechanics.
3. Reviewer-facing documents may reference internal evidence by stable ID and digest but should not reproduce operational exploit steps.
4. Internal evidence remains non-authoritative by itself and must still satisfy the project’s binding, provenance, and historical-preservation rules.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
