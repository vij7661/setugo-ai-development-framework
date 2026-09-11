# A0 Governance Automation Baseline

A0 reduces manual coordination errors before Production Requirements v1 is frozen.

## Goals

- resolve and validate exact authoritative state;
- use one canonical execution-manifest contract;
- fail closed before expensive execution when SHA/branch/policy/evidence state is wrong;
- canonicalize machine-readable evidence rather than retyping it;
- validate signature shape before cryptographic verification by the phase-specific checker;
- classify PR lifecycle state deterministically;
- produce readiness reports that distinguish checks, manual review, and human authority;
- preserve RED history and surface blockers rather than replacing earlier evidence.

## Non-goals / prohibited authority expansion

A0 does **not** sign, mint, infer, or grant human authority. It contains no private-key interface and no automatic reviewer API. Manual independent review remains manual wherever the phase policy requires it. Human terminal authority remains a separately signed act verified by the appropriate external trust root.

## Execution manifest

`execution-manifest.schema.json` is the v1 field contract. The Python implementation also performs stdlib-only structural validation so CI does not depend on an external JSON-schema package.

The manifest is the single input contract for phase automation. Workflows should derive repeated SHA/policy/evidence values from it instead of maintaining duplicate constants.

## CLI

```text
python governance-runtime/a0/governance_automation.py validate-manifest MANIFEST.json
python governance-runtime/a0/governance_automation.py canonicalize INPUT.json --output canonical.json
python governance-runtime/a0/governance_automation.py verify-signature-shape signature.sig.b64
python governance-runtime/a0/governance_automation.py preflight MANIFEST.json --repo . --expected-branch BRANCH
```

`verify-signature-shape` only verifies Base64 and exact 64-byte Ed25519 signature shape. Cryptographic signature verification remains in the trust-root-bound verifier for the relevant governance phase.

## Failure classes

Automation and downstream reporting should distinguish:

- `CODE_DEFECT`
- `FIXTURE_DEFECT`
- `EVIDENCE_PACKAGING_DEFECT`
- `GOVERNANCE_DEFECT`
- `ENVIRONMENT_DEFECT`
- `EXTERNAL_INFRASTRUCTURE_FAILURE`

A failed job is evidence. It is not automatically classified as a product/code defect.

## PR lifecycle vocabulary

- `ACTIVE`
- `REVIEW_PENDING`
- `QUALIFIED`
- `SUPERSEDED`
- `HISTORICAL`

Closing a superseded/historical PR does not erase commits, comments, CI, or RED evidence.

## Falsification

`a0-falsification-matrix.json` is preregistered before A0 is promoted. Tests cover stale candidate SHA, wrong branch, malformed policy binding, duplicate checks/evidence, malformed signatures, absent manual review, absent human authority, missing required checks, non-hash-bound evidence, prohibited signing capability, deterministic PR classification, and RED-history retention.

A0 may be merged only as automation construction evidence. It does not itself authorize Production promotion.
