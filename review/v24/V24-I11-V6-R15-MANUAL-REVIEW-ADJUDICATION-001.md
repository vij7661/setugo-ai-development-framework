# V24-I11-V6-R15 — Manual Successor Review Adjudication 001

Status: **R15 REJECTED / R16 REQUIRED / SCIENTIFIC EXECUTION CLOSED**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Bound review

Independent review preserved verbatim as:
`review/v24/V24-I11-V6-R15-DEEPSEEK-MANUAL-SUCCESSOR-REVIEW-001.md`

Frozen R15 candidate:
- commit `2e875bb29be48d39c9be6f3525d4f4610869848c`
- tree `d2c9c0c85564808941fdb54cfbbd53f51f5397ee`

Canonical R15 clean review package:
- inner ZIP SHA-256 `c218d80951e112855f4a89234c4bfddbb651edb0be22de5d4dab87569ac5252d`
- 216 unique entries
- 190 exact admitted candidate files
- manifest-listed payload files: 215
- manifest SHA-256 `1a57743d94cf00c67a04c460c1ad380f2b5fe4dd57b8feb1af927dab5f0e09af`
- independent local package recomputation mismatch count: 0

The reviewer reported `CONTENT_BINDING = CONSISTENT`, `CRYPTOGRAPHIC_RECOMPUTATION = NOT_VERIFIED`, and overall `NEEDS_REVISION`.

The review-context cryptographic limitation is **not** adjudicated as a package defect. The canonical ZIP and manifest had already been independently recomputed before manual delivery. The reviewer correctly did not claim cryptographic verification from the single-file projection alone.

## 2. Independent mechanism verification performed during adjudication

Repository inspection of the exact frozen external/native sources confirms the review's central premises:

1. `review/v24/r15_native_observer.c::r15_audit_hook` inspects only the first argument of CPython's `open` audit event and passes that path representation to `r15_forbidden_normalized_path`.
2. `r15_forbidden_normalized_path` uses `realpath(raw, resolved)` without any directory-file-descriptor context.
3. A direct local audit-semantics probe confirmed that `os.open("proc/self/status", ..., dir_fd=rootfd)` emits an `open` audit event containing the relative path string but not the `dir_fd` value.
4. `review/v24/r14_native_observer.c::main` generates the 32-byte HMAC key before `fork()` and invokes `child_main(..., key, ...)`, so the candidate child inherits the same key bytes through the forked address space.
5. `review/v24/r14_trusted_external_oracle.py::load_scenarios` imports a supplied scenario-library filesystem path without recomputing/validating a required runtime Git-blob or SHA-256 identity before execution.

## 3. Accepted Critical findings

### R15-C1 — `dir_fd` / `openat` relative-path bypass

**Accepted — Critical / code-mechanism defect.**

The R15 representation-normalization policy is path-string based. CPython's `open` audit event does not expose `dir_fd`; therefore a relative path such as `proc/self`, `mem`, or another forbidden descendant can be resolved by the kernel relative to a directory file descriptor while the R15 audit hook resolves the same lexical path relative to the process current working directory.

Concrete bypass class:
- open a directory descriptor for `/`;
- use `os.open("proc/self", ..., dir_fd=rootfd)`;
- use `os.open("mem", ..., dir_fd=procfd)`;
- reach `/proc/self/mem` without any single audited path argument equalling or normalizing to `/proc/self/mem` under the current hook.

R16 requirement: path-string normalization alone may not be authority-bearing. The successor must either fail closed on all directory-relative candidate opens or establish a kernel/native confinement boundary that prevents access to forbidden memory/introspection surfaces independently of path representation. Mandatory regression: `OS_OPEN_DIR_FD_PROC_SELF_MEM_REJECTED`.

### R15-C2 — inherited HMAC secret becomes forgeable once child memory is reachable

**Accepted — Critical / trust-boundary defect.**

The HMAC key is generated in the native parent before `fork()`. The candidate Python child therefore inherits the key bytes. R15's security argument depended on candidate code being unable to recover those bytes. R15-C1 provides a concrete route to child process memory through `/proc/self/mem`, converting secret inheritance from a design caveat into an exploitable authority-bypass path.

R16 requirement: no authority-bearing authentication secret may reside in candidate-readable memory. Merely adding another Python/audit-hook denial around `/proc/self/mem` is not sufficient as the sole trust assumption. Qualification-contributing parent acceptance must be based on evidence/observations whose authenticity cannot be forged by any candidate process even if that process can inspect its own address space.

## 4. Accepted High findings

### R15-H1 — scenario library not runtime identity-bound before import

**Accepted — High.**

`r14_trusted_external_oracle.py::load_scenarios` imports the supplied path directly. Construction metadata declares a scenario-library blob, but the oracle does not itself verify an expected Git blob/SHA-256 immediately before loading it.

R16 requirement: exact trusted scenario/oracle source identity must be runtime-verified before import/execution and included in the evidence environment/binding digest.

### R15-H2 — transitive included R14 transport source incompletely bound at source level

**Accepted — High.**

`r15_native_observer.c` textually includes `r14_native_observer.c`. The compiled binary digest binds the final result, but the R15 compiler/source contract did not independently include the transitive R14 transport source blob in the declared source-input digest.

R16 requirement: every transitive trusted/native source input contributing to the compiled authority binary must be individually enumerated and digest-bound before compilation, with the resulting compiler-input set incorporated into the environment/evidence binding.

## 5. Medium / Low observations

### R15-M1 — `realpath()` TOCTOU

**Accepted as open adversarial risk, not a separate Critical blocker because R15-C1 already invalidates the path mechanism.**

R16 should prefer a kernel-enforced or file-descriptor-aware confinement mechanism rather than check-then-use pathname validation. Where Linux primitives are available, test `openat2`-style resolution restrictions, namespace/mount masking, or an equivalent invariant that removes the race class rather than merely narrowing it.

### R15-M2 — non-`open` memory/introspection surfaces

**Accepted as mandatory R16 completeness target.**

R16 must derive a closed candidate-visible native-memory/introspection surface inventory or fail closed where completeness cannot be established. A single CPython audit event family is insufficient as the entire confinement root.

### R15-L1 — import-time rejection diagnostic ambiguity

**Accepted as test-strengthening observation only.**

R16 falsification must include post-import/in-function attempts that reach the intended forbidden operation rather than relying only on module-import failure.

## 6. H–P `INSUFFICIENT_TO_ASSESS` handling

The review returned `INSUFFICIENT_TO_ASSESS` for H through P primarily because the clean manual context could not execute the supplied suite or independently resolve every Git object. These are not silently promoted to PASS and do not erase prior construction evidence.

They are also not, by themselves, new implementation defects. R16 must preserve all previously accepted V6/internal hardening and rerun the complete construction/falsification regression under the successor's exact binding.

## 7. R16 frozen remediation scope

R16 scope is frozen to the following minimum properties:

1. close `dir_fd`/`openat` and equivalent directory-relative pathname bypasses;
2. establish representation-independent denial of `/proc`, `/sys`, `/dev/mem`, `/dev/kmem`, process-memory/maps/fd aliases and equivalent native-memory/introspection surfaces;
3. remove authority-bearing secret material from every candidate-readable address space, including inherited fork memory;
4. make candidate-produced bytes/frames observations only; a candidate must not be able to manufacture a parent-accepted authenticated observation by recovering child-local material;
5. runtime-bind the trusted scenario library before import/execution;
6. enumerate and bind every transitive trusted/native source input used to construct the authority binary;
7. address pathname TOCTOU structurally or demonstrate a kernel/file-descriptor confinement invariant that makes it non-authoritative;
8. derive and falsify a closed inventory of reachable native-memory/introspection mechanisms, including routes not represented by CPython's `open` event;
9. add post-import semantic endpoint probes, not only import-time denial probes;
10. preserve all R1–R15 historical RED/PASS evidence and all accepted supplemental review hardening;
11. keep scientific execution closed and runtime qualification unclaimed until R16 construction/falsification and fresh manual successor review complete.

## 8. Mandatory R16 adversarial probes

At minimum:

- `OS_OPEN_DIR_FD_PROC_SELF_MEM_REJECTED`
- `OS_OPEN_DIR_FD_PROC_SELF_MAPS_REJECTED`
- `OS_OPEN_DIR_FD_PROC_SELF_FD_REJECTED`
- `DUPLICATED_DIRECTORY_FD_FORBIDDEN_SURFACE_REJECTED`
- `POST_IMPORT_DIR_FD_MEMORY_OPEN_REJECTED`
- `CANDIDATE_SELF_MEMORY_READ_CANNOT_RECOVER_AUTH_SECRET`
- `CANDIDATE_FORGED_FRAME_WITH_FULL_CHILD_MEMORY_KNOWLEDGE_REJECTED`
- `SCENARIO_LIBRARY_SUBSTITUTION_REJECTED_BEFORE_IMPORT`
- `TRANSITIVE_NATIVE_SOURCE_SUBSTITUTION_REJECTED_BEFORE_COMPILE`
- `SYMLINK_RACE_OR_TOCTOU_CANNOT_CREATE_AUTHENTICATED_OBSERVATION`
- `NON_OPEN_EVENT_NATIVE_MEMORY_ROUTE_REJECTED_OR_PROVEN_UNREACHABLE`

## 9. State transition

- `R15_REJECTED = true`
- `R16_REQUIRED = true`
- `R16_SCOPE_FROZEN = true`
- `SCIENTIFIC_EXECUTION = CLOSED`
- `RUNTIME_QUALIFICATION = NOT_CLAIMED`
- `AUTOMATED_EXTERNAL_REVIEWER_API_CALLS_DURING_TESTING = PROHIBITED`

R15 must not be patched in place. R16 requires a new successor branch from the exact frozen R15 candidate lineage.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
