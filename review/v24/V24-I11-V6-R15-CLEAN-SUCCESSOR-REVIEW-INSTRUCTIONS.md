# V24-I11-V6-R15 — Clean Manual Successor Review Instructions

Status: **MANUAL INDEPENDENT REVIEW ONLY / NO AUTHORITY EFFECT**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## 1. Clean-context requirement

Perform this review in a fresh context with no access to prior reviewer conclusions, prior chat reasoning, model memory about this project, or hidden repository state beyond the supplied package.

Do not call another reviewer/model/provider API. Do not assume green CI, test names, artifact labels, or construction PASS records are authoritative. All supplied evidence is challengeable.

## 2. Review objective

Determine whether frozen successor R15 adequately remediates the known R11–R14 false-green classes **without introducing a new false-green path**, and whether the package contains enough evidence to permit repository adjudication toward scientific falsification.

The review does not grant runtime, deployment, release, terminal, or scientific authority.

## 3. Mandatory package binding checks

Independently verify, where tooling is available:

- package manifest file count, byte lengths, SHA-256 values;
- frozen candidate commit `2e875bb29be48d39c9be6f3525d4f4610869848c`;
- frozen candidate tree `d2c9c0c85564808941fdb54cfbbd53f51f5397ee`;
- exact-file pinset SHA-256 `e2f7689d4b9902823d94fe11e87c895e4036a080e0795aacfd9070354cf134b9`;
- native observer source Git blob `bfd16c1f3b7103b25c2f1abee536ebceb199e295`;
- native observer binary SHA-256 `6bfb7c6ce0db74a0a3d8b8fc6229a84dc229ac481f5212ae057918b07fa44eee`;
- compiler digest `153246e96a6b5d9d1856762a6171db87c8f4c218c0481e66c0d8c443bbcde233`;
- interpreter contract digest `eed7733f7032dd1f588cd048469130e52487335d2a7f32d2016cbc1d883d206b`;
- environment digest `afefcc6f01255ace8f35125be4810180d5aa1aecd4e3a4dfce21f315eb96af1e`;
- six-oracle evidence SHA-256 `99802aabf7b6d1451a7e698aaa6b540592a036f4870366fbe3fd577a333aebd8`;
- full construction run `34776147253` and its evidence bindings as represented in the package.

If raw bytes/tooling do not permit cryptographic recomputation, report that explicitly rather than treating declared hashes as verified.

## 4. Historical blockers that R15 claims to address

Do not remove or downgrade these merely because R15 construction is green:

- R11: actual interpreter isolation must be runtime-verified, not merely declared.
- R11/R12: candidate-controlled Python must not be able to forge trusted result accounting through shared mutable Python state.
- R11: mandatory adversarial checks require executed evidence, not check names alone.
- R12: same-process Python frame introspection defeated worker canaries.
- R13: candidate frame introspection forged observations that the external oracle accepted.
- R14: byte-string path `b'/proc/self/mem'` bypassed Unicode-only audit filtering and still produced an authenticated native observation.

## 5. R15-specific trust-boundary audit — mandatory

Read the exact trusted/native sources and challenge the implementation rather than its stated intent.

### A. Representation-complete path/memory denial

Audit whether R15 reliably rejects forbidden memory/introspection surfaces for:

- Unicode paths;
- bytes paths;
- `os.PathLike`/`__fspath__` outputs;
- `pathlib` paths;
- integer file descriptors;
- lexical variants (`//`, `..`, relative paths);
- symlink file aliases;
- symlink directory aliases;
- `builtins.open`, `os.open`/`posix.open`, `_io.FileIO`, and other reachable `open` audit events;
- `/proc`, `/sys`, `/dev/mem`, `/dev/kmem`, process maps/memory/fd aliases and equivalent native-memory surfaces.

Look for normalization gaps, TOCTOU, `realpath()` limitations, missing audit events, alternate filesystem APIs, inherited descriptors, file-descriptor duplication, or routes that never generate the expected audit event.

### B. Native parent / forked child / HMAC boundary

Audit the exact R14 transport source inherited by R15 plus the R15 wrapper.

Do **not** assume the HMAC boundary is safe because Python APIs are blocked. Determine concretely:

- when the ephemeral HMAC key is generated relative to `fork()`;
- whether candidate child address space inherits key bytes through copy-on-write;
- whether candidate-controlled Python can recover, influence, overwrite, replay, or reuse those bytes through any permitted mechanism;
- whether candidate code can reach native memory by a route not covered by current audit/import restrictions;
- whether file descriptors, `/proc/self/fd`, buffer/protocol objects, extension loading, signal/tracing/debug facilities, serialization, exception objects, import hooks, or other CPython/native surfaces expose a bypass;
- whether a child can forge a syntactically and cryptographically valid frame without executing the intended function;
- whether parent-side framing, length parsing, HMAC comparison, child termination handling, or stdout/stderr separation has ambiguity or replay paths.

A finding that the child inherits the authority secret is not automatically a blocker by itself; provide a concrete recovery/influence path or explain why the remaining confinement assumption is insufficient under the governing design.

### C. Trusted external oracle

Verify that the trusted oracle, scenario library, launcher and native observer remain outside the candidate tree and are identity-bound. Determine whether the external oracle derives PASS from independently held assertions rather than candidate-supplied PASS labels.

Challenge whether candidate-crafted plain-data observations can still satisfy an oracle without executing intended semantics, as occurred in R13.

### D. Exact-file admission and environment

Audit whether all qualification/construction-contributing candidate files and support objects are covered by the pinset, with no executable/config/runtime dependency able to influence results outside the admitted set or independently bound environment.

## 6. Review-protocol and supplemental systemic findings

R15 lineage also includes the supplemental internal hardening produced after the R11 dependency review. Audit that the currently supplied candidate actually preserves those fixes, including:

- no vacuous `BOUNDED_PASS` with an empty mandatory semantic dimension set;
- caller-created `DispatchResult`/transport labels cannot establish authenticated reviewer identity;
- material Git commit identity is required, resolves to governed Git provenance and matches the transition under review;
- legacy review schemas are historical/non-authoritative for material promotion;
- review request state, trigger and material-authority transition are mutually bound;
- the complete pending-review set is grounded, not only its first item;
- no-commit reconciliation, completeness universes, migration/cache evidence, admission/application witnesses, reviewer-proof history and authority-surface inventory retain the accepted supplemental hardening.

## 7. Systemic V6 audit — H through Q mandatory

Report each separately. If supplied material is insufficient, use `INSUFFICIENT_TO_ASSESS`; do not silently convert missing evidence to PASS.

H. ABGOU/meta-closure and authority inheritance.

I. Completeness derivation/root closure.

J. Genesis trusted-scope integrity.

K. Endpoint/predicate/evaluator/condition/evidence completeness.

L. Revalidation snapshot and decision/apply latch.

M. Material authority surface/effect classes/durable ledgers.

N. Atomic binding modes and replay resistance.

O. Normative projection and anti-false-green enforcement.

P. Result accounting and historical result integrity.

Q. External authority, execution boundary and recovery integrity.

## 8. Historical/falsification evidence handling

The package intentionally preserves RED evidence. Distinguish:

- code/mechanism defects;
- harness/probe defects before the intended endpoint;
- fixture/expectation drift;
- package/transport defects;
- insufficient evidence.

Do not use a harness RED as proof that the mechanism failed, and do not use a later PASS to erase the historical RED.

R15 RED history that must remain visible:

- construction RED 001 — intended endpoint observability defect;
- construction RED 002 — oracle CLI argument mismatch before oracle execution;
- alias RED 003 — relative symlink probe used the wrong process working directory;
- corrected symlink V2 — all three absolute sandbox aliases rejected at the intended R15 endpoint.

## 9. Required output

Return all sections below:

A. `CONTENT_BINDING = CONSISTENT | INCONSISTENT | INSUFFICIENT_TO_ASSESS`

B. `CRYPTOGRAPHIC_RECOMPUTATION = VERIFIED | NOT_VERIFIED | INSUFFICIENT_TO_ASSESS`

C. Overall = `READY_FOR_FALSIFICATION | NEEDS_REVISION | INSUFFICIENT_TO_ASSESS`

D. Critical findings.

E. High / Medium / Low findings.

F. R15 representation-complete path/memory denial assessment.

G. R15 native-parent/forked-child/HMAC assessment.

H. ABGOU/meta-closure.

I. Completeness/root closure.

J. Genesis trusted scope.

K. Endpoint/predicate/evaluator/condition/evidence completeness.

L. Revalidation snapshot + decision/apply latch.

M. Material surface/effect/ledger integrity.

N. Atomic binding modes.

O. Normative projection/anti-false-green.

P. Result accounting/history.

Q. External authority/recovery integrity.

R. Review-protocol/supplemental-hardening assessment.

S. Exact candidate/package binding audit.

T. Remaining concrete bypass paths or untested trust assumptions.

For every blocker provide the exact file/function/mechanism, concrete false-green or authority-bypass path, governing rule, and narrow repair requirement.

End exactly:

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
