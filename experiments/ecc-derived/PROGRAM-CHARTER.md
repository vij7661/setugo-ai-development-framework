# ECC-Derived Parallel Falsification Program — V1

Status: **PREREGISTERED — NON-AUTHORITATIVE — NOT YET ADJUDICATED**

Authority effect: **NONE_EVIDENCE_ONLY**

## Exact bindings

- Governed-platform baseline: `290ac043959f30db12c9ae16826eda1dd5bcbdfb`
- ECC evidence source: `affaan-m/ECC@b6ddd13a9f6ec2ccf55bc1773d52391c5afc05ab`
- ECC audit evidence: `research/ecc-frozen-audit-v1.md`
- Program branch: `experiments/ecc-derived-parallel-v1`

Any material governed-platform baseline change makes every affected experiment result `STALE_REVALIDATION_REQUIRED` until rerun against the new exact candidate.

## Program rule

Run seven isolated child experiments in parallel where implementation dependencies permit. Each child has its own hypothesis, fixtures, negatives, positives, evidence, result, and authority effect. A pass or failure in one child does not automatically affect another.

No child experiment may directly promote a platform requirement, alter V18, satisfy independent manual review, or grant merge/release/deploy/completion authority.

## Child experiments

1. `EXP-ECC-1` — Enforcement Execution Attestation
2. `EXP-ECC-2` — Declared-vs-Executable Enforcement Equivalence
3. `EXP-ECC-3` — Qualified Harness Capability Envelope
4. `EXP-ECC-4` — Capability / Power-Surface Activation Consent
5. `EXP-ECC-5` — Cross-Harness Tool/MCP Configuration Attestation and Drift
6. `EXP-ECC-6` — External Review Egress + Provider-Relationship Binding
7. `EXP-ECC-7` — Learned-Artifact Proposal / Promotion Boundary

## Role-provider rule

`R1`, `R2`, and `R3` are governed roles, not hardcoded model/provider identities. A user may choose any currently qualified model/provider for a role. Role binding must be exact, durable, and policy-valid. A mid-workflow model/provider substitution is a governed binding change and cannot occur silently.

## Testing/review constraint

During this testing phase, no external reviewer-model API calls are permitted. External review is manual only. AI-generated review supplied manually by the user remains `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY` with threshold contribution `0` unless a future qualified policy explicitly changes that evidence class.

## Completion barrier

The program reaches `ALL_CHILD_EXPERIMENTS_TERMINAL` only when each of EXP-ECC-1…7 has exactly one preserved terminal experimental disposition:

- `BOUNDED_PASS`
- `BOUNDED_FAIL`
- `INSUFFICIENT_EVIDENCE`

and has preserved all prior RED/failure/repair history.

Only after `ALL_CHILD_EXPERIMENTS_TERMINAL` may the program build one clean external-review packet. The packet must contain the exact frozen program baseline, all seven experiment specifications/results, all relevant evidence digests, unresolved limitations, and authority limitation. It must not expose prior external-review findings because there are none before that stage.

## External-review purpose

The final external review evaluates the complete ECC-derived experiment family as a whole: whether the evidence supports adopting, narrowing, rejecting, or deferring each candidate requirement. Reviewer agreement cannot promote a requirement if mandatory evidence is missing.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
