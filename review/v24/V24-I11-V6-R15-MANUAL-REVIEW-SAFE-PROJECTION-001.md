# V24-I11-V6-R15 — Manual Review Safe Projection 001

Status: **NEEDS_REVISION / REVIEW-SAFE PROJECTION**

Authority effect: `NONE_EVIDENCE_ONLY`

## Purpose

This document is a reviewer-facing projection of the independent R15 manual review. It preserves the review disposition, severities, affected mechanisms, governing rules, and repair requirements while deliberately omitting step-by-step exploit reproduction details.

The raw independent review remains the evidentiary source. This projection must not be used to replace, rewrite, or erase that source.

## Binding

- Frozen candidate commit: `2e875bb29be48d39c9be6f3525d4f4610869848c`
- Frozen candidate tree: `d2c9c0c85564808941fdb54cfbbd53f51f5397ee`
- Raw review attachment: `Pasted text(20260913-191112).txt`
- Raw review SHA-256: `1f09d459550a7c2f6f63232b65de38c2261012bf149dfe45bb03ee965d4b9095`
- Raw review disposition: `NEEDS_REVISION`
- Raw review content binding: `CONSISTENT`
- Raw review cryptographic recomputation: `NOT_VERIFIED`

## Critical findings

### R15-C1 — Effective-path denial is incomplete for directory-relative open semantics

**Severity:** Critical

**Affected mechanism:** `external/r15_native_observer.c`, especially the path-extraction and normalized-path policy used by the audit hook.

**Problem:** The current policy reasons primarily from the path representation visible to the audit event. Directory-relative file operations can cause the effective filesystem target to differ from the path string that the policy evaluates. This creates a route by which a restricted process-memory target can be reached without the policy seeing the final effective target.

**False-green consequence:** A forbidden memory/introspection surface could be reached while the observer believes the path policy was satisfied. Any authenticated observation produced after that point is no longer trustworthy as qualification evidence.

**Governing rule:** R15 requires representation-complete denial of restricted memory/introspection surfaces, including alternate path representations, directory-relative resolution, inherited descriptors, and equivalent native-memory routes.

**Required repair:** Resolve or constrain the effective target rather than trusting only the presented path string. The repair must either fail closed for directory-relative file access in the candidate domain or enforce a lower-level isolation boundary that prevents restricted process-memory access regardless of path spelling. Add a dedicated regression proving directory-relative access to restricted process-memory targets is rejected at the intended policy endpoint and cannot produce an authenticated observation.

### R15-C2 — Native HMAC observation boundary remains breakable if child memory is readable

**Severity:** Critical

**Affected mechanism:** `external/r14_native_observer.c` inherited by R15, together with the R15 path/memory policy.

**Problem:** The candidate child inherits native process state needed to authenticate the child-to-parent observation frame. If candidate-controlled Python can obtain direct process-memory access, the authentication secret is no longer isolated from the candidate execution domain.

**False-green consequence:** Candidate-controlled execution could potentially manufacture an observation that satisfies the native framing/authentication checks even though the intended candidate semantics were not actually established.

**Governing rule:** Qualification-contributing observation authentication must remain outside candidate-recoverable mutable state. Candidate-side execution may provide only untrusted observations; it must not be able to create authority-bearing evidence.

**Required repair:** First eliminate the process-memory reachability in R15-C1. In addition, redesign the observation boundary so that the authority secret is not present in candidate-readable child memory, or otherwise make authenticated evidence dependent on trusted state that candidate code cannot recover or synthesize. Add a regression proving that candidate-side memory access cannot be used to create a qualification-valid native observation.

## High findings

### R15-H1 — Scenario library identity is not enforced at oracle runtime

`external/r14_trusted_external_oracle.py::load_scenarios` loads the scenario library from a filesystem path, while the construction evidence binds an expected scenario-library identity outside the actual runtime import check.

**Required repair:** Verify the exact scenario-library content identity before import and fail closed on substitution.

### R15-H2 — Included R14 transport source is not separately source-bound in the R15 construction record

R15 compiles against inherited R14 transport code. The final binary is bound, but the review found source-level reproducibility incomplete because the inherited source object is not independently bound in the R15 construction record.

**Required repair:** Bind every native source input separately in the evidence record, including inherited transport source, compiler identity, and final binary identity.

## Medium findings

### R15-M1 — `realpath()`-based policy retains a potential TOCTOU class

Path normalization and target use are separate operations. The current construction evidence does not establish a race-free confinement boundary for mutable aliases.

**Required repair:** Prefer an OS-level resolution/confinement mechanism that binds path resolution and access atomically, or mask/unmount restricted namespaces so the target is unreachable independent of race timing.

### R15-M2 — Coverage is centered on the `open` audit event

The review did not establish representation-complete denial for every reachable native-memory or introspection route that may bypass the expected `open` policy path.

**Required repair:** Enumerate the reachable candidate-side memory/file/introspection surface and add explicit fail-closed coverage for routes outside the currently governed audit event.

## Low finding

### R15-L1 — Current path-regression evidence mixes intended rejection with import termination diagnostics

The expected R15 policy diagnostic is present, but the same traces also contain later child/import failure diagnostics. This is compatible with fail-closed rejection but is less clean as endpoint evidence.

**Required repair:** Add a regression that performs the forbidden operation after normal candidate import and demonstrates the same policy rejection without depending on import-time termination.

## Systemic review dimensions

The independent reviewer returned the following conservative assessments because the review context did not permit independent execution or full cryptographic recomputation:

- H. ABGOU/meta-closure: `INSUFFICIENT_TO_ASSESS`
- I. Completeness/root closure: `INSUFFICIENT_TO_ASSESS`
- J. Genesis trusted scope: `INSUFFICIENT_TO_ASSESS`
- K. Endpoint/predicate/evaluator/condition/evidence completeness: `INSUFFICIENT_TO_ASSESS`
- L. Revalidation snapshot + decision/apply latch: `INSUFFICIENT_TO_ASSESS`
- M. Material surface/effect/ledger integrity: `INSUFFICIENT_TO_ASSESS`
- N. Atomic binding modes: `INSUFFICIENT_TO_ASSESS`
- O. Normative projection/anti-false-green: `INSUFFICIENT_TO_ASSESS`
- P. Result accounting/history: `INSUFFICIENT_TO_ASSESS`
- Q. External authority/recovery integrity: `NEEDS_REVISION`
- R. Review-protocol/supplemental hardening: `INSUFFICIENT_TO_ASSESS` for execution; code inspection supported the presence of several hardening controls.
- S. Exact candidate/package binding: metadata `CONSISTENT`, cryptographic recomputation `NOT_VERIFIED` in the independent review context.

## Review-safe disposition

R15 must not proceed to scientific falsification or runtime qualification on the basis of the current package. The two Critical findings are sufficient to require a successor repair before any authority-bearing transition.

This projection intentionally omits operational exploit reproduction. Exact reproduction detail, if needed for engineering, must remain in separately controlled falsification evidence and must not be required in ordinary reviewer-facing material.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
