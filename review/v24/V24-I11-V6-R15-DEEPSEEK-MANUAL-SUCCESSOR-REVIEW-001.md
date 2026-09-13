A. `CONTENT_BINDING = CONSISTENT`

Declared manifest counts and spot-checked embedded SHA-256/byte-length metadata agree between `PACKAGE-MANIFEST.json` and the embedded file headers. I did not have the raw ZIP bytes or a writable repository checkout, so I could not recompute the canonical ZIP SHA-256, Git blob identities, or whole-package hashes.

B. `CRYPTOGRAPHIC_RECOMPUTATION = NOT_VERIFIED`

No raw canonical package, no Git object database, and no tool execution were available in this review context. All cryptographic claims remain declared-only.

C. Overall = `NEEDS_REVISION`

D. Critical findings

1. **R15 normalized path denial is not representation-complete for `dir_fd`/`openat` semantics.**
   - Exact file/function: `external/r15_native_observer.c`, `r15_audit_hook`, `r15_forbidden_normalized_path`, `r15_extract_path`.
   - Mechanism: R15 only inspects the path argument of the CPython `open` audit event. CPython’s `open` audit event does not expose the `dir_fd` argument used by `os.open`/`openat`. A relative path resolved through a directory file descriptor is therefore compared as a relative string, and `realpath()` is resolved against the process CWD rather than the `dir_fd`.
   - Concrete false-green / authority-bypass path:
     1. `fd_root = os.open("/", os.O_RDONLY | os.O_DIRECTORY)`
     2. `fd_proc = os.open("proc/self", os.O_RDONLY | os.O_DIRECTORY, dir_fd=fd_root)`
     3. `fd_mem = os.open("mem", os.O_RDWR, dir_fd=fd_proc)`
     4. Read/write `/proc/self/mem`.
     R15 sees audit paths `"/"`, `"proc/self"`, and `"mem"`. None are forbidden by the current policy. `realpath("proc/self")` is resolved from the native child’s CWD, not from `fd_root`, so it does not normalize to `/proc/self`. The forbidden process-memory access succeeds.
   - Governing rule: 00-REVIEW-INSTRUCTIONS §5A requires representation-complete denial of forbidden memory/introspection surfaces, including integer file descriptors, inherited descriptors, file-descriptor duplication, and routes that never generate the expected audit event. R15’s own contract requires `/proc`, `/sys`, `/dev/mem`, `/dev/kmem`, process maps/memory/fd aliases and equivalent native-memory surfaces to fail closed.
   - Narrow repair requirement: Fail closed on any candidate use of `dir_fd`/`openat` with a directory fd, or enforce a kernel/namespace boundary that prevents `/proc/self/mem` access regardless of path spelling. Add mandatory regression `OS_OPEN_DIR_FD_PROC_SELF_MEM_REJECTED` and demonstrate rejection at the intended R15 endpoint with no authenticated native observation.

2. **The native-parent/forked-child/HMAC boundary is broken by finding D1.**
   - Exact file/function: `external/r14_native_observer.c`, `child_main` (ephemeral HMAC key generated before `fork()` and inherited by the child); `external/r15_native_observer.c` audit bypass above.
   - Mechanism: The child process inherits the HMAC key bytes via copy-on-write. Candidate Python executes in that child. With the `dir_fd` bypass, candidate code can read `/proc/self/mem`, locate the key, compute a valid HMAC, and write a forged frame to the child→parent pipe. It can then call `os._exit(0)` to suppress the legitimate frame. The parent accepts any syntactically valid, correctly authenticated frame.
   - Concrete authority-bypass path: Candidate uses `dir_fd` to open `/proc/self/mem`, extracts the ephemeral HMAC key, forges an authenticated `R14F1` frame containing arbitrary plain-data observations, writes it to the pipe fd, and exits cleanly. The external oracle then derives PASS from forged observations rather than intended candidate semantics.
   - Governing rule: 00-REVIEW-INSTRUCTIONS §5B requires concrete determination that candidate-controlled Python cannot recover, influence, overwrite, replay, or reuse the ephemeral HMAC key. R15’s own contract requires the native parent / forked child / HMAC separation not to be weakened.
   - Narrow repair requirement: Eliminate the D1 bypass. Additionally, move the authority secret out of the candidate child’s address space, or bind frame validity to a parent-generated nonce that candidate cannot obtain without executing the intended function. Add adversarial regression proving candidate cannot forge a frame even if it can read child memory.

E. High / Medium / Low findings

- **High:** `external/r14_trusted_external_oracle.py::load_scenarios` loads the scenario library from a filesystem path without verifying its Git blob or content digest at runtime. The construction record binds a scenario-library Git blob (`f0f72ca...`), but the oracle does not enforce it. A substituted scenario library could weaken the oracle’s independently held assertions. Repair: require and verify an exact scenario-library SHA-256/Git blob before import.
- **High:** The R15 native observer source includes `r14_native_observer.c`, but the native construction evidence appears to bind only the R15 source Git blob. The included R14 transport source is not separately bound in the R15 native construction record. The final compiled binary SHA-256 partially compensates, but source-level reproducibility and reviewability are incomplete. Repair: bind both source blobs and include them in the external evidence set.
- **Medium:** `realpath()` in `r15_forbidden_normalized_path` introduces a TOCTOU window if candidate code can mutate symlinks between the audit hook and the actual open. Threading/fork imports are blocked, but the audit hook is not a complete race-free confinement mechanism. Repair: use `openat2`/`RESOLVE_NO_SYMLINKS` or a mount namespace with `/proc` unmounted or masked.
- **Medium:** R15 only handles the `open` audit event. Other reachable native-memory or introspection surfaces that do not emit `open` are not shown to be covered by equivalent normalized policy. Repair: enumerate and test all reachable file/memory APIs against the representation-complete policy.
- **Low:** The R15 path regression evidence shows expected rejection diagnostics, but the stderr also contains `R14_CHILD_CANDIDATE_IMPORT_FAILED` and `R14_NATIVE_CHILD_NOT_CLEAN_EXIT`. This is consistent with audit-hook rejection during import, but it does not prove the rejected operation would have reached the intended semantic endpoint if import had continued. Repair: add a probe that reaches the forbidden open from inside an already-imported candidate function and demonstrates the same R15 diagnostic.

F. R15 representation-complete path/memory denial assessment

`FAIL`.

R15 correctly adds bytes-path normalization, pathlib/path-like handling, integer-fd fail-closed behavior, lexical variants, and symlink alias resolution for the tested cases. However, it does not cover `dir_fd`/`openat` relative path resolution. That is a concrete false-green route to `/proc/self/mem`. The mandatory R15 contract is not satisfied.

G. R15 native-parent/forked-child/HMAC assessment

`FAIL` due to D1.

The design intent is sound: native parent does not initialize Python, candidate runs only in forked child, HMAC authenticates child→parent frames, and external oracle applies independent assertions. But because the child inherits the HMAC key and candidate can reach child memory via the `dir_fd` bypass, the authentication boundary is not safe against a candidate that can read `/proc/self/mem`. A finding that the child inherits the secret is not automatically fatal by itself, but here there is a concrete recovery and forgery path.

H. ABGOU/meta-closure

`INSUFFICIENT_TO_ASSESS`.

Supplied modules (`v24_v6_governance_foundation.py`, etc.) appear to implement generic qualification, completeness, currentness, independence, and anti-self-qualification contracts. I could not execute the tests or verify all object bindings against raw repository bytes.

I. Completeness/root closure

`INSUFFICIENT_TO_ASSESS`.

The completeness derivation graph validator is present and rejects cycles, disallowed terminals/sources, and unrooted omission-sensitive subjects. No raw execution evidence was available to independently confirm all reachable-terminal closure properties.

J. Genesis trusted scope

`INSUFFICIENT_TO_ASSESS`.

The genesis trusted-scope implementation uses exact `{object_id, content_digest}` pairs and rejects cross-pair matching. I could not verify the actual genesis records or their Git bindings.

K. Endpoint/predicate/evaluator/condition/evidence completeness

`INSUFFICIENT_TO_ASSESS`.

The endpoint projection and coverage validators appear to enforce complete one-record-per-applicable-predicate coverage and reject producer-selected N/A. Runtime verification was not possible.

L. Revalidation snapshot + decision/apply latch

`INSUFFICIENT_TO_ASSESS`.

The snapshot source and decision/apply latch code enforce currentness, independence, exact binding, and reevaluation on drift. I could not execute the adversarial cases.

M. Material surface/effect/ledger integrity

`INSUFFICIENT_TO_ASSESS`.

Material surface derivation, effect-class registry, and durable ledger validators are present. No independent execution evidence was available.

N. Atomic binding modes

`INSUFFICIENT_TO_ASSESS`.

The atomic-binding-mode registry validator appears to enforce omission-sensitive set equality and proof binding. I could not verify the full runtime path.

O. Normative projection/anti-false-green

`INSUFFICIENT_TO_ASSESS`.

Structural projection and anti-false-green scanners are present. No independent execution of the adversarial probes was possible.

P. Result accounting/history

`INSUFFICIENT_TO_ASSESS`.

The qualification summary compiler appears to count only exact-candidate/environment `EXECUTED` terminal `PASS` and to preserve historical unresolved records. I could not verify the full result set.

Q. External authority/recovery integrity

`NEEDS_REVISION`.

The external oracle and native observer are outside the candidate tree, but the critical `dir_fd` bypass breaks the native observation authority boundary. The scenario library is not runtime identity-bound by the oracle.

R. Review-protocol/supplemental-hardening assessment

`INSUFFICIENT_TO_ASSESS` for execution; code inspection supports presence of several hardening controls:

- `review_protocol.py` rejects material review requests without at least one mandatory dimension.
- `BOUNDED_PASS` cannot vacuously validate an empty mandatory set.
- Caller-forged `DispatchResult` instances are rejected through a process-local issuance registry.
- Material commit identity must resolve to a governed Git commit.
- Legacy review schemas are historical/non-authoritative for material promotion.
- Request state, trigger, material transition, and pending-review grounding are bound.
- Shared memory must contain exactly one grounded active pending-review entry.

These are construction-code observations only; no executed regression evidence was independently recomputed.

S. Exact candidate/package binding audit

`CONSISTENT` for declared projection metadata; `NOT_VERIFIED` cryptographically.

- Manifest-listed payload files: 215.
- Candidate entries: 190.
- External pinset admitted files: 190.
- Canonical ZIP entries: 216 (215 payload + manifest).
- Spot-checked manifest SHA-256 values match embedded file headers.
- No raw ZIP, Git object database, or tool execution was available to recompute canonical ZIP SHA-256, candidate commit/tree, pinset SHA-256, native observer blob/binary, compiler digest, interpreter contract digest, environment digest, six-oracle evidence SHA-256, or construction run bindings.

T. Remaining concrete bypass paths or untested trust assumptions

1. `os.open`/`openat` with `dir_fd` relative path to `/proc/self/mem` bypasses R15 normalized path policy. This is the primary critical bypass.
2. Candidate can use the D1 bypass to recover the inherited HMAC key and forge authenticated native frames.
3. Scenario library loaded by the external oracle is not runtime identity-bound; substitution could weaken oracle assertions.
4. `realpath()` TOCTOU window remains if candidate can mutate symlinks during execution.
5. R15 does not demonstrate representation-complete denial for every reachable file/memory API that emits an audit event other than `open`.
6. The included `r14_native_observer.c` source is not separately bound in the R15 native construction record.
7. All cryptographic bindings remain declared-only in this review context.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`