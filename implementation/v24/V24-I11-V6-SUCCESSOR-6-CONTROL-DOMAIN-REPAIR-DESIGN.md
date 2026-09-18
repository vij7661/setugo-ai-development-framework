# V24-I11-V6 Successor-6 — Candidate-Nonwritable Authority Gate Repair Design

Status: **IMPLEMENTED / ALL-UP GREEN / EXACT FINAL-HEAD FREEZE PENDING**

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

Against Successor-5 this assertion failed as expected and is now preserved as a genuine RED.

Preserved Successor-6 RED:
- branch head tested: `1d7f7024cddd6215a513a6c6f604561de0d4c417`
- workflow: `V24 V6 Successor-6 Gate Replacement RED`
- workflow run: `35333023688`
- job: `105561433493`
- test: `test_same_user_gate_executable_replacement_cannot_forge_authoritative_allow`
- compile step: `GREEN`
- attack regression: `RED`
- observed forged result: `construction_authoritative=True`, `decision=ALLOW`, expected gate id/version accepted at the substituted pathname.

This is a genuine mechanism defect. It is not a fixture defect and must never be relabeled as PASS.

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

## 9. Implemented construction evidence

The preregistered Successor-6 repair has been implemented without reclassifying the preserved RED.

All-up evidence:
- branch head tested: `b86e87ef199779b116224af0793cc3630519e662`
- workflow: `V24 V6 Successor-6 All-Up Trusted Gate`
- workflow run: `35334689053`
- job: `105566697724`
- Successor-6 + predecessor authority-boundary regressions: `29/29 GREEN`
- complete V24-V6 R1-R9 regressions: `199/199 GREEN`
- inherited V24 construction regressions: `90/90 GREEN`
- total all-up tests: `318/318 GREEN`
- trusted runtime: `/opt/v24-v6-trusted-runtime`
- candidate OS identity: `v24candidate` (unprivileged, no sudo)
- trusted runtime owner/mode: root-owned and candidate-nonwritable
- gate build-input SHA-256: `4e76eeaf554293d7f3a1faa615aec6c422c4b37d9b1677b94cdf1279fdcee818`
- trusted gate binary SHA-256: `724543687125ae63c62d801bd9e77721adaccc8b8c9726b1b3730b2368e7af5b`
- trusted gate evidence artifact: `10542249862`
- artifact digest: `sha256:402f2f7d4bc16e327f876e7c933547ca8cfd5e72f18fcac8e351e688be477644`

The all-up run also demonstrates that a tampered repository-built gate cannot be trusted-installed, installs the exact measured gate and worker/source set into a root-owned nonwritable control domain, and executes authority regressions under an unprivileged candidate identity. The candidate identity cannot chmod, unlink, replace, rename, or rewrite the trusted gate/worker paths. Caller-selected copies of the gate are rejected as non-authoritative.

This remains bounded construction evidence only. Scientific execution remains closed and runtime qualification remains `NOT_CLAIMED`.

The next permitted step is exact final-head freeze followed by independent manual review.
