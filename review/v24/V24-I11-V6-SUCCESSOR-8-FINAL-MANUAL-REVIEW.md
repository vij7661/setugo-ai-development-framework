# Independent Manual Engineering Review — V24-I11-V6-INTEGRATED-SUCCESSOR-8

## A. Overall disposition

**CHANGES_REQUIRED**

Successor-8 materially improves the construction boundary by making the candidate-visible service response diagnostic-only, introducing root-private one-shot authority records, preserving request/replay/gate/service bindings, and keeping DA-1/NCP-1 denials behind the trusted consume path.

The remaining blocker is that the authority-bearing `--consume-record` operation is still exposed through the same ordinary dynamically linked service executable that candidate code can launch directly. The implementation decides whether the invocation is authoritative by calling `geteuid()` and checking root-owned filesystem state inside that candidate-launched process. Because the binary is not a privileged secure-execution binary, candidate-controlled dynamic-loader state can interpose those libc calls before `main()` and make the consumer itself behave as though it were executing in the trusted root control domain.

A second blocking binding weakness remains: the root consumer accepts only a caller-supplied opaque `expected_request_digest`. It does not independently reconstruct the digest from the trusted intended operation/context/payload, nor does the consumed result expose those semantics. A genuine ALLOW record is therefore cryptographically bound to some request, but the authority consumer does not itself prove that it is the request the trusted caller intends to authorize.

Scientific execution remains **CLOSED_PENDING_SUCCESSOR_REVIEW**. Runtime qualification remains **NOT_CLAIMED**. Authority effect remains **NONE_EVIDENCE_ONLY**.

## B. Candidate and package identity

- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-8`
- frozen candidate commit: `2accab62a8437b74c5ad599f0c3d338b7825bbbf`
- frozen candidate tree: `36f020a7f1553259cc4dd76253e9fc0850a59974`
- exact final-head run: `35345890327`
- exact final-head job: `105602248702`
- integration binding digest: `b7820190d1892ae572e52e5a52d64bab5a006ad9aefe7186b9ab84a29aae976e`
- bound file count: `28`
- preserved Successor-8 RED run: `35342416032`
- integrated all-up run: `35345347709`
- evidence-bound revalidation run: `35345531082`
- all-up tests: `337/337 GREEN`
- namespace falsification run: `35345014849`
- frozen namespace policy: `BLOCKED_LOAD_BEARING`
- final-head verification artifact: `10547385398`
- final-head verification artifact digest: `sha256:d9e4bb6aef3587f22ec2cc9cdbaa3578c4f2010762f7c4a8262416ff313c1fda`
- verification JSON SHA-256: `e38ad7a9429ccab6e6dca1032767254a3dd53bebf25c94422d80c2db1ca7e80b`
- clean review package run: `35346388071`
- clean review package artifact: `10547575858`
- clean review package artifact digest: `sha256:536b0206a8fcb255b7c2cba246254bd3f0ef06009357ac738398f72af6053282`
- deterministic package ZIP SHA-256: `a142f7d3d0dfae9aa4a58875356baf195f6ed594044e5fdb13a3aef9c4e708eb`
- package manifest SHA-256: `95f5273ddfc657ca0e9b825c85a6f2fb1dc7913b01cd27e508d5b10a436f9075`
- bootstrap trust commit: `bd1000404d6e7c7f2f0e130a49c2747e7b2d83ac`
- bootstrap trust tree: `0a1c277976fdc6c51eb5465d2f7c945e7de090eb`
- bootstrap manifest blob: `8fe0ad1c96d1f1c2ce855846dfe342c79d947483`
- bootstrap script blob: `7412614144e160d6a493d6e39e5a2cf3805375a1`
- gate binary SHA-256: `7c69d78f5bf0f0d09dfe0ec92b738f86f7b6c18de3895cef23662ecb91e30069`
- trusted service binary SHA-256: `77a6f8c68a16fc4277c087d68a4338664106f232cf538459707e22af8b3c1124`

The GREEN evidence remains valid bounded construction evidence for the tested surfaces. It does not override the findings below.

## C. Critical finding

### C-01 — Candidate-launchable authority consumer is still loader-mutable

**Severity:** Critical  
**Blocking:** Yes  
**Affected path:** candidate process -> root-owned service executable -> `--consume-record` -> `geteuid()/prepare_runtime()/record parse` -> authoritative JSON

The build script links the trusted service normally with `gcc ... -lcrypto`; it is not installed setuid/setgid and no secure-execution boundary is created for candidate invocations.

The same binary exposes:

`v24_v6_trusted_authority_service --consume-record RECORD_ID EXPECTED_REQUEST_SHA256`

The consumer decides that it is executing in the trusted authority domain with:

`geteuid() == 0`

plus root-owned runtime/filesystem checks performed through normal libc/syscall-facing functions.

A candidate process can directly execute the root-owned mode-0555 binary under its own UID. Because this is an ordinary dynamically linked candidate-launched process, candidate-controlled loader state can execute before `main()`. A preload interposer can target the consumer path itself, for example by falsifying or redirecting:

- `geteuid()`;
- `lstat()/chmod()` checks used by `prepare_runtime()`;
- `fopen()` for the authority record path;
- `rename()` for one-shot consume state;
- other libc-facing reads/writes used by the consume path.

With an attacker-provided record body containing the publicly known service/build/request fields, the candidate-launched process can be induced to emit the same shape of:

`construction_authoritative=true, decision=ALLOW`

without the genuine root consumer reading or consuming a root-private record.

This is structurally the same trust failure class that Successor-7 exposed for a candidate-launched gate, shifted to the new consume endpoint.

#### Why existing controls do not close it

Current Successor-8 regressions prove that:

- a normal unprivileged invocation of `--consume-record` returns `ROOT_CONSUMER_REQUIRED`;
- fabricated record IDs cannot be consumed normally;
- namespace-local/fake service responses cannot create genuine root-private records;
- the genuine root workflow can consume an exact legitimate record once.

They do **not** attempt candidate-controlled loader/process interposition against the `--consume-record` authority consumer itself.

The root ownership and mode bits of the binary protect its bytes; they do not protect a separately candidate-launched process from candidate loader state.

#### Narrow required repair

The authority-bearing consume action must not be a candidate-launchable process whose own internal checks decide that it is trusted.

Use a separately controlled already-running trusted parent/service for consumption, or an equivalent trusted control channel where:

1. candidate code cannot directly execute the authority consumer with candidate-selected environment;
2. consume requests enter through a root-owned endpoint/capability unavailable for candidate impersonation;
3. the trusted process itself performs the one-shot record transition and emits/executes the authoritative effect;
4. candidate-local process output is always non-authoritative;
5. a permanent regression attempts loader/process interposition against any candidate-launchable consume helper and proves that no authoritative effect can result.

### C-02 — Root consume accepts an opaque caller-supplied request digest instead of the trusted intended request

**Severity:** Critical  
**Blocking:** Yes  
**Affected path:** `--consume-record RECORD_ID EXPECTED_REQUEST_SHA256`

The authority record commits the original operation and bytes only indirectly through `request_sha256`. At consume time, the root consumer receives only:

- record ID; and
- caller-supplied expected request digest.

It does not receive or independently reconstruct the intended operation, reference, subject, context, boundary, payload, generation, or effect identity.

The consumed authoritative result likewise returns the opaque request digest but not the exact request semantics.

This means the consumer can prove:

> “this record matches this digest”

but not:

> “this is the exact request/effect the trusted caller currently intends to authorize.”

A genuine ALLOW record for one permitted request can therefore become a confused-deputy token if a privileged orchestration path accepts the candidate-supplied record ID and its matching digest without independently deriving that digest from the trusted intended action.

The current CI harness reads the record ID and request digest from the diagnostic record output and passes both to the root consumer. That proves record integrity/replay behavior, but not end-to-end semantic binding at the authority consumer.

#### Narrow required repair

The trusted consumer must independently bind consumption to the intended request/effect. Suitable bounded shapes include:

- pass the complete trusted request material to the trusted consumer and have it recompute the digest itself;
- store the canonical request fields/identities in the root-private record and require exact trusted-side matching;
- perform the actual downstream authority-bearing effect inside the trusted service using the already evaluated request, eliminating a detached opaque-token consume step.

The candidate must not be able to choose both the authority token and the value used to validate that token.

## D. High findings

### H-01 — DA-1 remains transitively open through the consume boundary

The genuine Successor-8 service correctly creates DENY records for the tested fresh effect-path self-grant.

However, C-01 permits the candidate to counterfeit the authority-consumer process result, and C-02 leaves the trusted consumer without independent semantic knowledge of the requested effect.

**DA-1: LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING.**

### H-02 — NCP-1 remains transitively open through the consume boundary

The genuine Successor-8 service likewise creates DENY records for the tested fresh clause/control reassignment.

The same consume-path defects allow the authority boundary to be bypassed or confused after the genuine service evaluation.

**NCP-1: LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING.**

## E. Positive findings

The following controls are materially stronger and should be preserved:

- the original candidate-local fake-service RED is preserved and not relabeled;
- candidate-visible service responses are now explicitly diagnostic-only;
- genuine authority records are created only in root-private state;
- record IDs are random and pending records use exclusive creation;
- request digest, service build identity, decision and gate-result digest are recorded;
- normal candidate invocation of `--consume-record` fails closed;
- successful consume is one-shot under the tested path and replay is rejected;
- request-digest mismatch is rejected;
- fake diagnostic JSON alone cannot create a root-private record;
- genuine DA-1/NCP-1 attack requests produce DENY records;
- external bootstrap v4 independently pins the gate/service/source set;
- candidate-selected trusted-root substitution remains rejected;
- coherent candidate source/build substitution remains rejected;
- the frozen construction environment explicitly measures and binds the blocked user/mount namespace primitive;
- exact final-head and clean package identities are deterministic and preserved.

## F. Bounded observation — namespace prohibition evidence

The frozen environment records that:

`unshare --user --map-root-user --mount`

is blocked for the candidate identity, and Successor-8 explicitly treats that as load-bearing construction evidence.

That is useful bounded evidence, but a single utility invocation is not by itself a durable production namespace-security contract. A later successor should either keep authority safe even if user namespaces become available or bind a fuller host policy/attestation that covers the relevant kernel/LSM namespace creation paths.

This observation does not replace C-01; the loader-consumer finding does not require user namespaces.

## G. Explicit blocker adjudication

- **PRC-1:** **OPEN / CRITICAL / BLOCKING** at the candidate-launchable consume process and end-to-end request-binding boundary.
- **DA-1:** **LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING** through PRC-1.
- **NCP-1:** **LOCALLY REPAIRED BUT TRANSITIVELY OPEN / HIGH / BLOCKING** through PRC-1.

## H. Evidence and claim boundary

This review is construction-level only.

It does not claim hostile-root resistance, production IAM/HSM/KMS custody, production namespace policy, release/deployment authority, remote-service security, scientific WDPC outcomes, or general native-code memory safety.

No earlier failure is reclassified. The preserved Successor-8 candidate-local service RED remains a genuine mechanism failure. The later `337/337` GREEN all-up evidence, evidence-bound revalidation, exact-final-head GREEN, and clean-package GREEN remain valid bounded evidence for the specific surfaces they exercise.

## I. Final progression statement

**Successor-8 may not progress.**

A new repair/refreeze/re-review cycle is required.

The next successor should preserve the root service, root-private one-shot records, bootstrap v4, predecessor regressions and bounded namespace evidence, while moving record consumption/effect execution into a trusted already-running control domain that candidate code cannot directly launch or loader-inject.

Permanent new regression coverage should include:

1. candidate `LD_PRELOAD`/loader interposition against the consume path;
2. candidate-launched consume helper with forged `geteuid`/filesystem results;
3. genuine ALLOW record substituted for a different intended operation/effect;
4. trusted-side recomputation of exact request/effect binding;
5. DA-1 and NCP-1 compound attacks through the hardened consume/effect path.

Scientific execution remains **CLOSED_PENDING_SUCCESSOR_REVIEW**.  
Runtime qualification remains **NOT_CLAIMED**.  
Authority effect remains **NONE_EVIDENCE_ONLY**.
