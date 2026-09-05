# Review Engine MVP v0.1 — Frozen implementation baseline

## Frozen implementation

- Repository: `vij7661/setugo-ai-development-framework`
- Product branch: `feature/review-engine-mvp`
- **Frozen implementation SHA:** `5fda61c3078c80ac0d607f546f40db316f2c9b6d`
- Exact-head CI run: `33977202103`
- CI conclusion: **SUCCESS**

This document is a review marker only. The implementation under external review is the exact SHA above; later documentation commits must not be silently included in the reviewed artifact.

## Product contract for v0.1

The system is a model-neutral governed multi-LLM review engine.

1. R1 is the Interpreter/Builder and produces the initial artifact.
2. Platform-owned facts and policy determine the minimum risk/materiality floor. R1 may escalate those signals but may not lower platform-owned floors.
3. Low-risk work may finalize at R1 when policy permits.
4. Material/consequential/high-risk work can require an independent R2 Detector/Challenger.
5. A material R2 finding is frozen and localized before R1 receives a scoped correction request.
6. R2 does not obtain release/production authority and does not directly rewrite the final artifact.
7. A material revision can require a foundation-lineage-independent R3 Verifier/Adjudicator.
8. R3 forms a blinded independent view before prior model conclusions are disclosed for adjudication.
9. Majority voting is not a convergence rule.
10. Unresolved material conflict, requirement ambiguity, incomplete consequential evidence, missing required reviewer, or qualification failure must fail closed to `HUMAN_REQUIRED`.
11. Shared memory is typed/versioned; model-private reasoning and protected truth are not shared across reviewers.
12. Authoritative memory changes require external/platform authority.
13. Review artifacts and reviewer responses are bound to artifact hashes.
14. Governed assurance requires retained reviewer qualification matching provider, model, SKU, deployment path, role, risk/task scope and lineage.
15. Raw API keys are not committed or persisted in memory/evidence; provider credentials are resolved from environment/secret references.
16. Session routing/convergence evidence is append-only and hash-linked in the MVP SQLite evidence store.
17. The dashboard/API expose review decisions and evidence but do not obtain governance authority.
18. `action_execution_enabled` is false in v0.1; no model or convergence result authorizes an external/production action.

## Intentional v0.1 boundaries

These are declared MVP scope boundaries, not claims of production completeness:

- Local-only HTTP service; authentication and multi-user tenancy are not implemented.
- SQLite memory/evidence are single-node reference stores, not distributed-consensus proof.
- Hash-linked evidence is tamper-evident, not externally immutable against privileged full-history rewrite.
- Provider qualification/identity evidence is a governance input; v0.1 does not claim universal cryptographic runtime identity proof for every provider.
- User model selection is configuration-driven in v0.1 rather than a credential-management product UI.
- Tool/agent execution and consequential action authorization are disabled.

## External review rule

All Claude findings are candidate evidence only. Each finding must be independently reproduced/adjudicated against this frozen SHA before it changes the implementation or becomes a regression test.
