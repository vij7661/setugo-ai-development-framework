# V24-I11-V6 Successor-6 — Candidate-Nonwritable Authority Gate Repair Design

Status: **PREREGISTERED AFTER SUCCESSOR-5 MANUAL REVIEW / RED EXECUTION PENDING**

Authority effect: `NONE_EVIDENCE_ONLY`

## 1. Predecessor and blocking review

Frozen predecessor:
- family: `V24-I11-V6-INTEGRATED-SUCCESSOR-5`
- commit: `65d138bf8ceb7567459eb6d20f6dab2fe53df388`
- tree: `50c5c61af1b3508cbd9deb1a046b1f9985c5c3ea`
- exact final-head run: `35331392047`
- all-up evidence: `310/310 GREEN`
- final manual-review commit: `47f55b1be51a35980cc720e676686addc04beb00`
- disposition: `CHANGES_REQUIRED`

The Successor-5 GREEN evidence remains valid bounded evidence and is not reclassified.

## 2. Findings to falsify

Successor-5 moved the authority decision into a native executable but left that executable and its pinned Python source tree under the same effective OS control domain as candidate execution.

Two blocking paths are preregistered:

### PRC-1A — gate executable replacement

The build script writes:

`governance-runtime/.gate-build/v24_v6_external_authority_gate`

and only applies `chmod 0555`. The owning user can still chmod/unlink/rename/replace the file through the writable containing directory.

A same-user attacker can therefore replace the native gate with an executable that emits an apparently authoritative `ALLOW`.

### PRC-1B — source hash/use TOCTOU

The native gate hashes pinned Python sources by pathname and later launches `/usr/bin/python3`, which reopens the worker and imports dependencies by pathname. If the runtime tree remains candidate-writable, checked bytes can be replaced between measurement and use.

## 3. Required Successor-6 invariant

No candidate-controlled OS identity may modify, replace, rename, unlink, race-substitute, or select any executable/source object that contributes to the authority-bearing gate decision.

The bounded construction authority path MUST place:
- gate executable;
- pinned root identity/material;
- measured worker/source set or equivalent load-bearing logic;
- verdict consumer/enforcer;

inside a control domain that candidate execution cannot write or replace.

The trusted parent MUST select the gate path and verify/measure the live gate identity itself. Caller-selected gate paths are forbidden.

## 4. First mandatory preserved RED

The first Successor-6 regression MUST:

1. build the frozen Successor-5 native gate;
2. demonstrate that the current OS owner can replace the `.gate-build` executable at the same pathname;
3. install an attacker executable that emits:
   - `construction_authoritative=true`;
   - `decision=ALLOW`;
   - expected gate id/version;
4. invoke the substituted path;
5. assert that such a forged authoritative ALLOW must be impossible.

Against Successor-5 this assertion is expected to fail and MUST be preserved as a genuine RED.

This RED must never later be relabeled as a fixture failure.

## 5. Mandatory permanent regressions

At minimum:

1. `SAME_USER_GATE_EXECUTABLE_REPLACEMENT_REJECTED`
2. `GATE_PARENT_DIRECTORY_RENAME_UNLINK_REPLACEMENT_REJECTED`
3. `PINNED_SOURCE_POST_MEASUREMENT_SUBSTITUTION_REJECTED`
4. `CALLER_SELECTED_GATE_PATH_REJECTED`
5. `LIVE_GATE_DIGEST_MISMATCH_REJECTED`
6. `TRUSTED_GATE_POSITIVE`
7. all Successor-5 PRC-1 regressions remain mandatory;
8. DA-1/NCP-1 compound attacks rerun through the hardened boundary.

## 6. Prohibited repairs

The following are insufficient:
- another `chmod` mode on a file still owned/control-accessible by candidate;
- storing the expected binary hash in candidate Python;
- checking the gate binary hash only in CI;
- checking the gate binary hash only inside the gate itself;
- caller-supplied executable path;
- same-user wrapper script that can itself be replaced;
- rehashing sources and then reopening mutable pathnames;
- documentation-only narrowing of the attacker model.

## 7. Acceptable bounded construction directions

A repair may use a separate trusted OS identity/service, root-owned candidate-nonwritable directory, immutable/read-only mount or snapshot controlled by the trusted parent, or another mechanism that demonstrably prevents candidate replacement.

For the worker/source TOCTOU path, execution must be tied to the exact measured immutable bytes, not merely the same pathname observed at two different times.

## 8. Claim boundary

Successor-6 remains construction-only. It does not claim hostile-host resistance, production IAM/HSM/KMS, deployment authority, scientific outcomes, or general native memory safety.

Scientific execution remains closed. Runtime qualification remains `NOT_CLAIMED`.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
