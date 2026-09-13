# V24-I11-V6-R12 — Clean Successor Manual Review Instructions

Status: **FROZEN SUCCESSOR / MANUAL REVIEW REQUIRED / SCIENTIFIC EXECUTION CLOSED**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Independence posture

Perform this review in a fresh clean context. Review only the bytes supplied in the R12 review bundle. Do not rely on prior chats, prior reviewer conclusions, model memory, green CI labels, construction PASS claims, test names, comments, or declared booleans as authority.

This is a manual review. Do not initiate or rely on automated external reviewer API calls.

The supplied construction and verification records are evidence to challenge, not authority to qualify. The candidate remains non-authoritative even if every construction test is green.

## 2. Frozen subject

The review bundle must bind exactly:

- candidate commit `e887613f4e9012be59dcd8c4840035748ee0de7e`;
- candidate tree `c584cf728ca70c663ba04cf4bfb50fd29f5f1e0f`;
- predecessor R11 commit `68ce0df63ce0133ae19ec4402b41c4c09adfb54e`;
- predecessor R11 tree `d202b039285213b386557083a26de42e0fb20cf4`;
- approved V6 design exact bytes: 19,297 bytes, raw SHA-256 `96ec464fbf602ac6b8c89fca5af16aa71a8d53f9f042605e46a07b4cd628ca62`, Git blob SHA-1 `4a15d50a0488464816d235b273d1dbf808fdce94`, plan-body SHA-256 `286217399947144630c29e991c3529dfee64d382be08a6ccd3f87e9fc5173ad5`;
- external R12 pinset raw SHA-256 `8f6ca5108354cadacbf9b836faffb3f27e8b87fbb9bba981529148693f95429e`;
- trusted external guard Git blob SHA-1 `28e82a1e995fea9b585950e8ea33886f3f900fcf`;
- trusted parent Git blob SHA-1 `8d7dbb76f766c8314dfd8143cf6be0b6961f4359`;
- untrusted worker Git blob SHA-1 `e20534e76652c9019c93ffd69787b659d5f7d807`;
- trusted adversarial-evidence builder Git blob SHA-1 `a0a4a58fe066ad4f12e5161d097642ba28dbf460`.

If the bundle does not supply enough bytes to recompute a claimed identity, report that limitation. Never convert absence of contrary evidence into PASS.

## 3. R12 remediation properties to falsify

R12 is a successor remediation. Independently determine whether the supplied implementation actually establishes all of the following properties; do not assume the property holds because its name appears in a contract or test.

### R12-A — trusted/untrusted process separation

Verify that qualification-contributing candidate/test code cannot mutate trusted result-accounting state.

Attempt to identify a concrete path by which candidate-controlled code could:

- monkey-patch `unittest`, result classes, subprocess helpers, stdout/stderr handling, or other trusted parent state;
- forge child PASS/result records;
- exploit exit code 0, crafted stdout/JSON, exception handling, signal behavior, timeout behavior, partial writes, or process termination to cause trusted PASS;
- become imported into the trusted parent process before or during result accounting;
- cause the trusted parent to rely on candidate-supplied terminal status without independent derivation.

The trusted parent must remain outside candidate mutable state. Candidate output, child exit code, or serialized child claims must not self-authorize qualification.

### R12-B — actual interpreter/runtime startup verification

Verify the trusted authority checks actual runtime state before candidate bytes become importable, including the load-bearing interpreter isolation semantics and exact runtime identity used for stdlib/bootstrap-shadow policy.

A pinset field saying `true` is not proof that the running process actually has the corresponding flag. Look for fail-closed checks against actual process/runtime state and for version/runtime mismatch paths.

### R12-C — executed adversarial-check evidence binding

Verify that every mandatory adversarial check is bound to executed evidence, not merely to a required check-name string.

The binding must prevent missing, duplicate, stale, mismatched, replayed, cross-candidate, cross-tree, cross-environment, cross-run, cross-round, self-authored, non-executed, or name-only evidence from satisfying completeness. Determine whether the integrated successor commits to the actual evidence set and whether the evidence can be forged by the candidate or by the same authority it purports to witness.

### R12-D — external authority origin

Verify that external guard/parent/worker/evidence objects are distinguishable from candidate-controlled content by exact identity and that package colocation, labels, paths, or self-declared `authority_origin` cannot alone prove authorization.

State explicitly what can and cannot be established about repository/branch authorization from supplied bytes alone.

## 4. Preserve V6 systemic falsification

R12 repair must not regress the previously designed V6 systemic controls. Review the supplied candidate and support bytes for the following sections independently:

- H — ABGOU/meta-closure and authority inheritance;
- I — completeness derivation/root closure;
- J — genesis trusted-scope integrity;
- K — endpoint/predicate/evaluator/condition/evidence completeness;
- L — revalidation snapshot + decision/apply latch;
- M — material authority surface, effect class, durable ledgers;
- N — atomic binding modes/replay resistance;
- O — normative projection and anti-false-green controls;
- P — result accounting and historical result integrity;
- Q — external authority and recovery integrity.

For each section, identify any caller-controlled labels, names, status strings, booleans, counts, digests, registries, or self-reported evidence that can substitute for independently bound evidence.

## 5. Required adversarial constructions

At minimum, reason through or construct the following attacks against the supplied bytes:

1. candidate module monkey-patches `unittest`/result state;
2. candidate child prints forged PASS JSON and exits 0;
3. candidate child exits 0 without producing trustworthy result evidence;
4. candidate child writes partial/truncated/multiple/conflicting result records;
5. candidate child times out, is killed, crashes, or closes output early;
6. parent is invoked without required isolation/no-site/environment-ignore/safe-path posture;
7. runtime/interpreter version differs from the version whose stdlib universe is assumed;
8. mandatory adversarial check appears only by name with no execution evidence;
9. adversarial evidence is replayed from another candidate/tree/environment/run/round;
10. adversarial evidence is self-authored or witnessed by a non-independent authority;
11. pinned candidate file is changed, added, removed, symlinked, or substituted after precheck;
12. external authority object is substituted while retaining the same filename/label.

Do not infer success merely because a corresponding unit test exists.

## 6. Construction evidence posture

The bundle may contain construction evidence showing a preserved RED run and a later green run. Preserve both as historical evidence. Determine whether the green run actually demonstrates the claimed mechanism or merely demonstrates that the supplied harness accepted itself.

A construction PASS does not open scientific WDPC execution and does not establish runtime qualification.

## 7. Required output

Return the following sections in order:

A. `CONTENT_BINDING = CONSISTENT | INCONSISTENT | INSUFFICIENT_TO_ASSESS`

B. `CRYPTOGRAPHIC_RECOMPUTATION = VERIFIED | MISMATCH | NOT_PERFORMED | INSUFFICIENT_TO_ASSESS`

C. Overall disposition: `READY_FOR_FALSIFICATION | NEEDS_REVISION | INSUFFICIENT_TO_ASSESS`

D. Critical findings — each with exact file/function, concrete false-green or bypass path, governing requirement, and narrow required repair.

E. High / Medium / Low findings.

F. R12-A trusted/untrusted process separation audit.

G. R12-B actual interpreter/runtime startup verification audit.

H. R12-C executed adversarial-check evidence-binding audit.

I. R12-D external-authority-origin audit.

J. ABGOU/meta-closure audit.

K. Completeness derivation/root audit.

L. Genesis trusted-scope audit.

M. Endpoint/predicate/evaluator/condition/evidence audit.

N. Revalidation snapshot + decision/apply latch audit.

O. Material surface/effect-class/ledger audit.

P. Atomic-mode/replay audit.

Q. Normative/anti-false-green audit.

R. Result-accounting/historical-result audit.

S. External-authority/recovery integrity audit.

T. Exact candidate/package/evidence binding audit.

U. Remaining concrete bypass paths.

If any section lacks sufficient supplied evidence, say `INSUFFICIENT_TO_ASSESS` for that section rather than converting it to PASS.

End exactly:

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
