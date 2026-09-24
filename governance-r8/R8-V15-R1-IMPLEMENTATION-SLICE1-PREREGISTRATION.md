# R8 v15-r1 — Implementation Slice 1: Frozen Schema Runtime Loader

Status: **PREREGISTERED BEFORE ACCEPTANCE HARNESS OR MECHANISM IMPLEMENTATION**

## 1. Starting authority

This slice begins only after the exact executable-schema candidate
`f93ca26975ecb64f0da13779889c75b36140cdfc` reached
`EXECUTABLE_SCHEMA_FROZEN`, recorded by
`governance-r8/R8-V15-R1-EXECUTABLE-SCHEMA-FREEZE.json`
at evidence head `6f0506b6cd2a12eeeb30d79f85224d4b87b6c368`.

Bounded implementation construction is authorized by
`governance-r8/R8-V15-R1-IMPLEMENTATION-AUTHORIZATION.json`.

This slice does **not** grant runtime qualification, release, deployment,
production, policy, or terminal authority.

## 2. Goal

Falsify whether repository-local code can consume the exact frozen R8 v15-r1
schema set without silently substituting candidate bytes, weakening frozen
GCP rules, accepting out-of-range signed integers, trusting stale provenance,
or treating loader success as authority.

The mechanism is intentionally narrow: a deterministic, read-only frozen-schema
runtime loader plus GCP canonicalization helpers. It does not execute governance
decisions or external effects.

## 3. Included

- exact frozen-candidate identity pinning;
- exact artifact SHA-256 verification against the frozen SPM;
- exact source-map/SPM/traceability loading;
- exact `runtime-contracts.schema.json`, `gcp-rvm-2.json`, and validator-contract loading;
- fail-closed detection of missing/tampered artifacts;
- frozen GCP object-key ordering by NFC Unicode scalar sequence;
- canonical JSON output with no insignificant whitespace;
- signed-int64 range enforcement;
- positive GCP vector recomputation, including corrected P05;
- frozen rejection-vector checks that are implementable without authority state;
- deterministic, read-only operation;
- explicit non-authority result metadata.

## 4. Deferred / nonclaims

This slice does not implement or prove:

- authority resolution;
- MTR/BTW/T0 live verification;
- canonical identity quorum;
- revocation semantics;
- RIR/RCS live qualification;
- AuthorityReadSet sealing;
- qualified time proof;
- VerifiedStateSeal / COMMIT_WITH_SEAL;
- external effect execution or reconciliation;
- migration/recovery;
- GGS/LAS runtime rotation;
- production cryptographic key handling;
- distributed durability or consensus;
- runtime qualification;
- release/deployment/production readiness.

## 5. Frozen implementation invariants

**I1-I01 Exact candidate identity** — runtime configuration pins the exact frozen candidate
`f93ca26975ecb64f0da13779889c75b36140cdfc`; another candidate identity fails closed.

**I1-I02 Exact SPM identity** — the materialized SPM SHA-256 must equal
`84c484121c4c8dd0592bcd7e4c070d8a3ab7f17215f4c3d2b31863fb6dbf6797`.

**I1-I03 Exact artifact bytes** — every loaded artifact covered by the frozen SPM must hash to the
SPM-declared SHA-256 before use.

**I1-I04 No partial trust** — missing SPM/source map/traceability/runtime schema/GCP vector/validator
contract fails before returning a usable runtime bundle.

**I1-I05 Frozen provenance binding** — loaded SPM semantic candidate must equal
`1fa49fa4adfa6aa47fae68c0f1938083eeb1497f`; its coverage arrays must remain empty.

**I1-I06 Qualified-generator identity preserved** — SPM generator ID must be
`R8V15R1-SPG-V2`, qualification status `QUALIFIED`, and the frozen generator/runtime/workload
digests must match the SPM.

**I1-I07 GCP object ordering** — object keys are NFC and sorted lexicographically by Unicode scalar
sequence before encoding.

**I1-I08 Canonical JSON bytes** — output uses UTF-8, no insignificant whitespace, and deterministic
JSON string escaping/number representation for the supported frozen subset.

**I1-I09 Signed int64 closure** — integers outside
[-9223372036854775808, 9223372036854775807] reject.

**I1-I10 P05 correction** — the P05 input canonicalizes exactly to
`{"max":9223372036854775807,"min":-9223372036854775808}`
and SHA-256
`161a1dcda7bae00f28f0ba32675f218fd4977065d2aa0439cf451c6d066dbbfb`.

**I1-I11 Positive-vector recomputation** — every supplied GCP positive vector whose input is supported
by this slice recomputes to its exact frozen canonical UTF-8 and SHA-256.

**I1-I12 Duplicate/NFC-collision rejection** — duplicate semantic keys or keys that collide after NFC
normalization reject.

**I1-I13 Unicode rejection** — unpaired surrogates and Unicode noncharacters reject in
authority-bearing strings/keys.

**I1-I14 Read-only behavior** — loader/canonicalizer writes no repository or authority state and
performs no network access.

**I1-I15 Honest result boundary** — returned runtime metadata states
`authority_effect=NONE`, `runtime_qualified=false`, and cannot be changed by input content.

**I1-I16 Failure recovery** — after a failed tamper/canonicalization attempt, a fresh valid load remains
deterministic and succeeds without retained weakened state.

## 6. Frozen acceptance cases

- **I1-01** exact frozen tree loads and returns the exact candidate/SPM/semantic identities.
- **I1-02** candidate identity mismatch fails closed.
- **I1-03** SPM digest mismatch or missing SPM fails closed.
- **I1-04** tampering one covered artifact byte fails before bundle return.
- **I1-05** SPM coverage with any uncovered/non-authoritative/conflicting entry fails closed.
- **I1-06** generator ID/status/runtime/workload binding mismatch fails closed.
- **I1-07** canonical object key ordering is deterministic and NFC-aware.
- **I1-08** signed-int64 min/max pass; min-1/max+1 reject.
- **I1-09** P05 exact canonical bytes/hash recompute.
- **I1-10** all supported positive GCP vectors match expected bytes/hashes.
- **I1-11** duplicate/NFC-colliding object keys reject.
- **I1-12** unpaired surrogate and Unicode noncharacter inputs reject.
- **I1-13** missing required runtime/GCP/validator/source-map/traceability artifact fails closed.
- **I1-14** loader and canonicalizer make no network call and no repository mutation.
- **I1-15** output claim boundary is immutable/non-authoritative.
- **I1-16** a valid load succeeds after prior failed tamper/canonicalization attempts.

## 7. Construction sequence

1. Commit this preregistration before adding the acceptance harness or mechanism.
2. Add a dedicated frozen acceptance harness for I1-01..I1-16 without adding the implementation module.
3. Preserve the expected RED construction run showing the mechanism is absent.
4. Add only the narrow runtime-loader/canonicalization mechanism required by this slice.
5. Require I1-01..I1-16 plus existing R8 v15-r1 freeze/regression tests to pass on the same exact implementation candidate.
6. Preserve all failed construction attempts.
7. Freeze one exact implementation candidate SHA.
8. Require a fresh independent implementation review before any bounded implementation adjudication.
9. A construction pass does not grant runtime qualification, release, deployment, production, policy, or terminal authority.

## 8. Claim boundary

A positive result proves only that the repository-local reference implementation can load and
integrity-check the exact frozen R8 v15-r1 schema bundle and reproduce the supported frozen GCP
canonicalization behavior under the tested conditions. It does not prove that governance authority
decisions, live trust dependencies, cryptographic identities, external effects, or production runtime
behavior are correct.
