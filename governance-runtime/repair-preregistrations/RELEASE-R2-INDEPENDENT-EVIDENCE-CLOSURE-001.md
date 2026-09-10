# RELEASE R2 Independent Evidence Closure — Preregistration 001

Status: `FROZEN_BEFORE_NEW_EVIDENCE_MECHANISM`
Authority effect: `NONE_EVIDENCE_ONLY`
Exposed RELEASE candidate: `ffec566022fcd221fb4ab7569ed3bc245f75b546`
Exposed checker: `45604c8425bcad623be87d8f88106e509345e266`
Prior independent disposition: `INSUFFICIENT_EVIDENCE`

## Objective

Falsify whether the current RELEASE candidate can satisfy independent review when the reviewer is given directly reproducible repository/API evidence rather than packet assertions. This preregistration does not assume the mechanisms are correct. Missing, contradictory, stale, or unverifiable evidence fails closed.

## Frozen requirements

### R2-01 Exact-SHA check evidence
For both required RELEASE contexts, capture independently retrievable GitHub check-run evidence proving exact `head_sha`, context name, conclusion, App ID `4895420`, and checker revision carried in `external_id`. Old or different-SHA checks must not qualify.

### R2-02 Live ruleset source binding
Capture the live ruleset `22789078` response showing exact target `refs/heads/phase/release`, active enforcement, strict status policy, empty bypass actors/current-user bypass `never`, and both required contexts bound to integration ID `4895420`. Add a preregistered negative same-name/wrong-producer falsification where technically possible without weakening the protected branch.

### R2-03 RELEASE-entry ancestry proof
Provide reproducible source/candidate commit objects and exact ancestry algorithm. Fail closed on shallow-history insufficiency, replace-ref influence, ambiguous revision names, or any lineage proof not using immutable full object IDs. Add negative lineage vectors for unrelated/non-ancestor commits.

### R2-04 External checker revision/provenance
Bind evidence to protected checker `main` exact SHA and demonstrate that emitted App checks use the workflow runtime checker SHA as `external_id`. A packet string or caller-supplied revision alone is insufficient.

### R2-05 Harness/import isolation adversarial matrix
Execute a checker-owned negative matrix against candidate-controlled import/discovery attacks including at least unittest module/package shadowing, representative stdlib shadows, `sitecustomize`, `usercustomize`, `.pth`, `PYTHONPATH`/`PYTHONHOME`, pytest/conftest/plugin influence, symlink/path substitution where supported, async/generator/awaitable nonexecution, zero-test collection, and unsupported runner-command shapes. Every attack expected to influence qualification must fail closed.

### R2-06 Dependency/test/workflow closure
Produce an explicit qualification-contributing closure manifest. Every candidate-controlled file that can materially influence a required RELEASE check must be pinned by immutable Git object ID, verified by the checker, or explicitly classified as non-authoritative/non-contributing with rationale. Include bridge imports, helpers, fixtures, scripts, workflows, and runtime modules.

### R2-07 Mutable dependency/workflow review
Enumerate all governance-contributing `uses:` actions, containers, package-install steps, reusable workflows, remote execution, and runner assumptions. Mutable tags/branches or unverified remote execution in a required qualification path fail closed unless independently constrained.

### R2-08 Ruleset/bypass fail-closed evidence
Independently present live ruleset evidence and preserve any mismatch. A same-name check from an unauthorized producer must not be accepted as satisfying the App-bound contract. Unknown bypass state fails closed.

### R2-09 Authority separation
No RELEASE merge may occur from CI, reviewer PASS, App check, or model output. `MERGE_RELEASE_CANDIDATE` requires a separate exact-SHA `HUMAN_RELEASE_AUTHORITY` signed attestation under the configured external trust root after independent review findings are adjudicated. Public verification material may be presented; private signing material must remain off-repository and must never be requested or committed. HSM custody is not assumed unless separately established.

### R2-10 RELEASE contract mapping
Provide the governing RELEASE qualification contract and map every review finding to an applicable RELEASE clause or explicitly classify it as deferred production-only. Unknown materiality fails closed.

### R2-11 RED/prereg chronology
Provide immutable Git commit timestamps, workflow run identities, failure logs, preregistration commits, and successor diffs sufficient to independently verify that each known repair was preregistered before mechanism change and that later greens did not erase prior RED evidence.

## Negative-control rule

Where the evidence gap concerns a mechanism that can be falsified safely, prefer a frozen negative control over narrative proof. A negative test that unexpectedly passes is a new RELEASE-blocking RED and must be preserved before repair.

## Completion rule

R2 is not complete until a fresh independent reviewer can verify the exact candidate/checker/root/ruleset subject from the supplied evidence and returns `PASS` or `BOUNDED_PASS` with no unadjudicated RELEASE-blocking finding. Reviewer output remains evidence only.
