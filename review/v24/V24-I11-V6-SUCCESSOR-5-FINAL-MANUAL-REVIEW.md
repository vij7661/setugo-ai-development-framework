# Independent Manual Engineering Review — V24-I11-V6-INTEGRATED-SUCCESSOR-5

## A. Overall disposition

**CHANGES_REQUIRED**

Successor-5 materially improves the construction trust boundary by moving root-attestation verification and the final construction ALLOW/DENY decision into a native parent gate, and the preserved Python-local verifier/key/helper attacks are correctly rejected by that gate.

However, the candidate does not yet satisfy its own load-bearing invariant that candidate Python cannot replace the authority gate. The gate executable is built into the repository-owned `.gate-build` directory under the same operating-system user and is only changed to mode `0555`. That removes write bits from the file but does not create an ownership or privilege boundary: the file owner can chmod it again, unlink/replace it through the writable containing directory, or otherwise substitute the executable before invocation. No separate trusted consumer verifies the frozen gate binary digest immediately before accepting its output.

A second related race exists because the gate hashes the pinned Python sources and then launches `/usr/bin/python3`, which reopens those paths later. With same-user write access to the runtime tree, a concurrent attacker can race source replacement between the digest check and interpreter load.

Scientific execution remains **CLOSED_PENDING_SUCCESSOR_REVIEW**. Runtime qualification remains **NOT_CLAIMED**. Authority effect remains **NONE_EVIDENCE_ONLY**.

## B. Candidate identity

- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-5`
- frozen candidate commit: `65d138bf8ceb7567459eb6d20f6dab2fe53df388`
- frozen candidate tree: `50c5c61af1b3508cbd9deb1a046b1f9985c5c3ea`
- exact final-head run: `35331392047`
- integration binding digest: `71a23d0c3903f1c714c57646b9c12cb959ad84b634aa764b3247a6599595f48b`
- preserved Successor-5 RED run: `35326754734`
- all-up gate run: `35331004892`
- clean review package run: `35331829181`
- gate build-input SHA-256: `0065c4334cd23c55f241aeb7f7e221a414b2e5d01ba74bb85cd0968557ecff84`
- frozen native gate SHA-256: `e2145e97c96e1af335234c2d58b4a9c0be2bba5e32da696bb36bc38b28f6ca5a`
- all-up tests: `310/310 GREEN`

The GREEN evidence remains valid bounded construction evidence. It does not override the findings below.

## C. Critical findings

### C-01 — Native authority gate remains replaceable by the candidate OS identity

**Severity:** Critical  
**Blocking:** Yes  
**Affected path:** build script -> `.gate-build/v24_v6_external_authority_gate` -> native gate invocation

The build script creates the gate under the repository runtime tree and finishes with:

```bash
chmod 0555 "$OUT"
```

The directory is created with ordinary `mkdir -p` under the same working tree. Mode `0555` is not an immutable or ownership boundary. The owning user can restore write permission, and—more importantly—can remove or rename the file through the writable parent directory and place a different executable at the same pathname.

A candidate-controlled same-user process can therefore use a sequence equivalent to:

```text
locate .gate-build/v24_v6_external_authority_gate
    -> unlink/rename existing gate
    -> install attacker executable at identical path
    -> attacker executable emits construction_authoritative=true, decision=ALLOW,
       expected gate_id/version and attacker-selected bindings
    -> caller invokes substituted path
```

The frozen SHA-256 is verified in CI/package evidence, but there is no separate runtime authority outside the executable that measures the live gate binary immediately before consuming its result. The gate cannot self-prove that the process currently running is the frozen gate when the executable itself is the object being substituted.

This directly conflicts with the preregistered Successor-5 invariant:

- candidate Python cannot replace the authority gate;
- the authority-bearing consumer must validate/enforce the external verdict outside candidate-mutable state.

The current implementation moves the boundary out of Python but not out of the candidate's effective OS control domain.

#### Why existing controls do not close it

The current regressions cover:

- imported Python verifier replacement;
- Python root-key substitution;
- Python RSA-helper substitution;
- direct Python `qualified=True` being non-authoritative;
- forged/rebound verdict fields;
- context/scope/generation/version rebinding;
- DA-1 and NCP-1 compound attacks.

They do not attempt replacement of the gate executable itself under the same user/working-tree ownership model.

The recorded `gate_binary_sha256` is evidence-time identity, not live enforcement of executable identity.

#### Narrow required repair

Create a real authority boundary for the gate executable and its invocation. Acceptable construction shapes include a trusted parent/service or OS identity that:

1. owns the gate executable and pinned trust material outside candidate-writable directories;
2. denies candidate write/rename/unlink/replace access to the gate and its parent directory;
3. invokes or measures the exact gate binary itself rather than accepting a caller-selected path;
4. binds and consumes the verdict in that trusted parent/control domain;
5. fails closed if the measured executable/build identity differs from the frozen identity.

A same-user repository-local executable, even if native and mode `0555`, is insufficient under the current stated threat model.

### C-02 — Hash-then-reopen TOCTOU permits source substitution between pin check and worker import

**Severity:** Critical  
**Blocking:** Yes  
**Affected path:** `verify_pinned_python_sources()` -> `run_worker()/run_downstream_worker()`

The native gate computes SHA-256 over each pinned Python source by pathname. After those checks complete, it launches a new Python interpreter with the worker path. That interpreter and its imports reopen the files from the filesystem.

Therefore the authority path is:

```text
hash source path
    -> check succeeds
    -> time gap
    -> Python reopens same path
```

If candidate code has same-user write access to the runtime tree, a concurrent process can replace a checked source after the digest check but before the worker/import open. The worker may then execute bytes different from the bytes the gate measured.

The gate later validates worker output bindings, but a substituted worker/dependency can emit a syntactically valid success response for the exact caller inputs. The native parent currently does not execute from already-open immutable descriptors or remeasure the loaded bytes after import.

#### Narrow required repair

The trusted parent must eliminate the check/use split. Examples include:

- copy the exact frozen source set into a candidate-nonwritable trusted directory before execution and verify there;
- open/verify immutable file descriptors and execute from a controlled filesystem namespace/snapshot;
- package the worker and dependencies into an immutable measured artifact controlled by the trusted parent;
- or move the load-bearing structural checks into the trusted/native side so candidate-controlled Python source is not authoritative.

The permanent regression must race or deterministically substitute a pinned source between measurement and execution and prove that no ALLOW can result.

## D. High findings

### H-01 — DA-1 and NCP-1 remain transitively dependent on the unresolved gate boundary

The new compound DA-1 and NCP-1 tests are materially stronger and correctly show that local same-process Python self-grants do not survive an unmodified native gate.

However, if C-01 or C-02 succeeds, an attacker can replace the authority gate/worker boundary itself and restore an externally shaped ALLOW for attacker-selected downstream bindings.

Therefore DA-1 and NCP-1 are locally repaired but not independently closed while the gate-control-domain defect remains open.

## E. Positive findings

The following controls appear sound within the bounded unmodified-gate model:

- detached construction attestation is verified natively against a pinned RSA public key;
- context, scope and generation digests are recomputed externally;
- direct Python `qualified=True` is explicitly non-authoritative;
- caller-supplied verdict consumption is rejected;
- verifier identity/version rebinding is rejected;
- malformed/nonzero worker execution fails closed;
- gate output is bound to context/scope/payload identities;
- DA-1 fresh effect-path self-grant is rejected by the unmodified external gate;
- NCP-1 fresh clause/control self-grant is rejected by the unmodified external gate;
- exact final-head CI rebuilds the gate and binds the evidence artifact;
- prior RED and CHANGES_REQUIRED history is preserved.

These positives are preserved and should remain permanent regressions.

## F. Explicit blocker adjudication

- **PRC-1:** **OPEN / CRITICAL / BLOCKING** at the native gate ownership and hash/use boundary.
- **DA-1:** **LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING** through PRC-1.
- **NCP-1:** **LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING** through PRC-1.

## G. Evidence and claim boundary

This review is construction-level only. It does not claim production HSM/KMS custody, hostile-host resistance, production IAM, remote-service security, release/deployment authority, scientific WDPC outcomes, or general native-code memory safety.

No earlier failure is reclassified. The preserved Successor-5 mutable-verifier RED remains a genuine mechanism failure, and the later GREEN runs remain valid bounded evidence for the repaired attack surfaces they actually exercise.

## H. Final progression statement

**Successor-5 may not progress.**

A new repair/refreeze/re-review cycle is required.

The next successor should preserve the native/root-attestation improvements but move the gate executable and measured worker surface into a genuinely candidate-nonwritable control domain, then add permanent regressions for:

1. same-user gate executable replacement;
2. gate parent-directory rename/unlink replacement;
3. pinned-source replacement after measurement but before worker import;
4. DA-1/NCP-1 compound attacks repeated through the hardened boundary.

Scientific execution remains **CLOSED_PENDING_SUCCESSOR_REVIEW**. Runtime qualification remains **NOT_CLAIMED**. Authority effect remains **NONE_EVIDENCE_ONLY**.
