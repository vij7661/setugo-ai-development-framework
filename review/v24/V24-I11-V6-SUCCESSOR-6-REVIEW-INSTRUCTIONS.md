# Successor-6 Independent Manual Review Instructions

Review only the exact frozen candidate bound by `V24-I11-V6-SUCCESSOR-6-FROZEN-BINDING.json`.

Required posture:
- treat the candidate as untrusted until independently justified;
- preserve all prior RED and CHANGES_REQUIRED evidence;
- do not infer authority from GREEN CI alone;
- inspect whether candidate-controlled code or the candidate OS identity can modify, replace, rename, unlink, race-substitute, select, or counterfeit any load-bearing gate executable, pinned worker/source object, root key material, verifier helper, payload binding, verdict, or authority decision;
- inspect the native gate source, build path, trusted installer, root-owned trusted runtime, and every pinned transitive production dependency;
- specifically attempt to falsify the candidate-nonwritable control-domain claim rather than accepting file modes or ownership labels at face value;
- inspect whether the trusted installer can itself be influenced by candidate-controlled build metadata, source paths, environment, symlinks, path traversal, race windows, or caller-selected destinations in ways that permit unauthorized bytes into the trusted runtime;
- inspect whether the live gate enforces its trusted execution location/control domain independently of candidate Python;
- inspect whether source measurement and later Python execution are tied to the same immutable bytes, with no hash-then-reopen TOCTOU path under the stated candidate threat model;
- explicitly re-evaluate PRC-1, DA-1, and NCP-1, including compound attacks through the hardened boundary;
- distinguish construction evidence from runtime/scientific qualification;
- do not open scientific execution or claim runtime qualification.

Mandatory adversarial focus:
1. same-user gate executable replacement;
2. trusted gate parent-directory rename/unlink/replacement;
3. caller-selected/copied gate path;
4. live gate binary digest mismatch;
5. post-measurement worker/source substitution;
6. installer input/build-manifest substitution;
7. symlink or path redirection into trusted installation;
8. environment-based trusted-root or executable-path rebinding;
9. DA-1 and NCP-1 compound self-grants through the hardened boundary;
10. any route by which candidate-controlled bytes can become authority-bearing after the trusted boundary is established.

Required disposition:
- `PASS_FOR_BOUNDED_CONSTRUCTION_REVIEW`, or
- `CHANGES_REQUIRED`.

Any blocking finding must include:
- the exact false-green/failure path;
- why the current Successor-6 controls do not close it;
- whether the finding is local or transitively reopens PRC-1/DA-1/NCP-1;
- the narrowest repair that preserves prior evidence.

The package includes the frozen candidate, exact final-head verification evidence, trusted gate/build/control-domain evidence, external trust artifacts, predecessor Successor-5 final review, approved V6 design bytes, and a deterministic package manifest.

Scientific execution must remain `CLOSED_PENDING_SUCCESSOR_REVIEW`.
Runtime qualification must remain `NOT_CLAIMED`.
Authority effect must remain `NONE_EVIDENCE_ONLY`.
