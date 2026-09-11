# RELEASE R1 Hardening Preregistration 001

Status: FROZEN_BEFORE_RELEASE_MECHANISM_CHANGE
Authority effect: NONE

Exact TESTING source SHA: `15d50cc25ae524fc64e2c65269c91135e0361846`.
RELEASE qualification PR: `#36` targets `phase/release` and remains intentionally unmerged.

This preregistration freezes the first RELEASE hardening obligations carried forward from the independently reviewed TESTING bounded pass.

## Frozen carried-forward findings

### REL-R1-01 — bridge-imported async/generator/awaitable false-green
The TESTING bridge directly invokes pinned top-level `test_*` functions. A future bridge-imported async/generator/awaitable function could return an unevaluated object and be treated as PASS. RELEASE must reject such shapes or execute them correctly before relying on the bridge.

### REL-R1-02 — mutable action tags in local required workflow
The candidate TESTING qualification workflow uses mutable `actions/checkout@v4` and/or `actions/setup-python@v5` tags. RELEASE must pin governance-contributing third-party actions to immutable commit SHAs before relying on that workflow as release evidence.

### REL-R1-03 — external checker coverage gap
The external governance checker does not execute the candidate experiment regression `experiments/governed-platform/governance/test_integrated_governed_mvp_slice6_terminal_authority.py` or candidate live-boundary verifier `governance-runtime/verify_external_trust_root_control.py`. RELEASE qualification must independently execute or equivalently verify these paths.

## Frozen acceptance conditions

1. Each finding above must receive an executable regression before or with its narrow repair.
2. No repair may weaken exact-SHA binding, App-source binding, signed authority verification, failure preservation, or evidence-versus-authority separation.
3. RELEASE candidate work occurs on a distinct release lineage; `phase/testing` remains frozen at the independently reviewed TESTING SHA.
4. The protected `phase/release` branch must not be updated until RELEASE qualification and separate RELEASE merge authority are satisfied.
5. Any new material false-green exposed during RELEASE qualification must be preserved and preregistered before repair.
6. CI/reviewer/check results remain evidence only and grant no RELEASE or PRODUCTION authority.
