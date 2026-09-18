# Successor-7 Independent Manual Review Instructions

Review only the exact frozen candidate bound by `V24-I11-V6-SUCCESSOR-7-FROZEN-BINDING.json`.

Required posture:
- treat the candidate, candidate UID, client transport, service protocol, native gate, bootstrap process, and all reported GREEN evidence as untrusted until independently justified;
- preserve every prior RED and `CHANGES_REQUIRED` record; GREEN CI is bounded construction evidence only;
- explicitly re-evaluate PRC-1, DA-1, and NCP-1 through the new service boundary;
- do not open scientific execution or claim runtime qualification.

Mandatory adversarial focus:

1. **Service process/control-domain isolation**
   - prove the candidate cannot launch the authoritative service with attacker-selected `LD_PRELOAD`, `LD_LIBRARY_PATH`, executable path, worker path, startup environment, UID, namespace, or parent-process state;
   - attempt same-UID and cross-UID signal/debug/ptrace/process-injection routes;
   - inspect whether numeric UID/root labels remain trustworthy under the bounded host assumptions actually claimed.

2. **IPC endpoint and peer identity**
   - inspect Unix-socket ownership/mode and `SO_PEERCRED` enforcement;
   - test whether a candidate-controlled endpoint, socket replacement, namespace/path rebinding, stale socket, proxy, or peer impersonation can produce an authoritative response;
   - inspect request framing for truncation, extra bytes, ambiguity, oversized fields, operation confusion, and replay/rebinding.

3. **Authority-bearing result channel**
   - verify worker/probe/result material is never stored in candidate-owned pathname-addressable state;
   - attempt post-write/pre-parse substitution, symlink/hardlink/path replacement, race substitution, and candidate access to the trusted-private scratch directory;
   - inspect whether the trusted service validates the gate result structurally enough that crafted output cannot be accepted merely by containing expected substrings.

4. **External bootstrap/root of trust**
   - independently verify exact trust commit/tree/blob identities;
   - attempt coherent gate/service/source/build-manifest substitution;
   - attempt candidate-selected trusted-root or destination rebinding;
   - inspect whether the bootstrap script itself, expected manifest, source paths, compiler/toolchain inputs, environment, symlinks, or reproducible-build assumptions can be candidate-controlled;
   - determine whether the external trust object actually authenticates every byte that becomes authority-bearing.

5. **Inherited boundaries**
   - preserve Successor-6 static replacement checks;
   - preserve Successor-5 verifier/key/helper attacks;
   - preserve Successor-4 root-attestation attacks;
   - rerun DA-1 fresh decision/effect-path self-grant and NCP-1 fresh clause/control self-grant through the service;
   - inspect stale/replay/cross-control variants rather than relying only on positive service tests.

Required disposition:
- `PASS_FOR_BOUNDED_CONSTRUCTION_REVIEW`, or
- `CHANGES_REQUIRED`.

Any blocking finding must state:
- concrete false-green/failure path;
- severity and affected boundary;
- why current controls do not close it;
- whether PRC-1, DA-1, or NCP-1 is reopened directly or transitively;
- narrowest repair that preserves historical evidence.

The review package must preserve:
- frozen candidate commit/tree;
- exact final-head verification artifact;
- Successor-7 preserved loader-injection RED;
- Successor-6 final manual review;
- external Successor-7 bootstrap v3 trust artifacts;
- external root-attestation trust artifacts;
- exact approved V6 reviewed bytes;
- deterministic package manifest/binding.

Scientific execution must remain `CLOSED_PENDING_SUCCESSOR_REVIEW`.
Runtime qualification must remain `NOT_CLAIMED`.
Authority effect must remain `NONE_EVIDENCE_ONLY`.
