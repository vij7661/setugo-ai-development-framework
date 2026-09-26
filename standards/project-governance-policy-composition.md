# Project Governance Policy Composition Standard

Status: PROPOSED_PENDING_INDEPENDENT_REVIEW

## 1. Purpose

This standard defines how user-, organization-, project-, and experiment-specific governance rules compose with mandatory platform governance.

The governing principle is:

> Users may strengthen or specialize governance for their project, but lower-level configuration must not silently weaken mandatory platform invariants.

## 2. Governance hierarchy

Effective governance is composed in this order:

1. Platform mandatory invariants
2. Organization governance
3. Project governance
4. Experiment / release governance

Lower levels inherit all applicable higher-level requirements.

Effective Governance = Platform Mandatory Rules + Organization Rules + Project Rules + Experiment/Release Rules

Project or experiment configuration does not replace the platform baseline.

## 3. Non-weakenable platform floor

A lower-level rule MUST NOT disable, bypass, contradict, redefine, or silently weaken a mandatory platform invariant.

Examples of platform invariants include, where applicable:

- no self-granted PASS or qualification;
- preservation of prior failures, retractions, and contrary evidence;
- exact evidence/source identity binding;
- mandatory independent review where policy requires it;
- no fabricated or candidate-self-authored evidence being treated as independent proof;
- fail closed when mandatory evidence, authority, identity, or review is missing or invalid;
- no unauthorized promotion, deployment, release, or live provider/API authority;
- deterministic or otherwise governed evidence requirements defined by the applicable platform policy.

If a lower-level rule conflicts with a mandatory invariant, the conflict MUST be rejected and the effective policy MUST remain non-promotable until resolved.

## 4. User/project rule capability

Authorized users MAY add project-specific governance requirements, including but not limited to:

- additional independent reviewers;
- stricter mutation or coverage thresholds;
- security/privacy requirements;
- logging restrictions;
- manual approval gates;
- approved-model or approved-provider constraints;
- retention periods;
- domain-specific evidence requirements;
- performance, accessibility, compliance, or release conditions.

Such rules may specialize or strengthen the platform baseline.

## 5. Explicit override policy

No implicit override is permitted.

A higher-level rule MAY be overridden only when all of the following are true:

1. the higher-level rule is explicitly marked overridable;
2. the lower-level actor has explicit authority for that override;
3. the override is recorded as a distinct policy change;
4. the resulting effective policy is recomputed and validated;
5. the override does not weaken any invariant marked mandatory/non-overridable;
6. any required independent review of the governance change is completed before promotion.

Absence of an override declaration means the higher-level rule remains authoritative.

## 6. Effective Governance Snapshot

Before governed execution, the platform MUST derive an immutable Effective Governance Snapshot containing at least:

- platform policy version/identity;
- organization policy version/identity, if any;
- project policy version/identity, if any;
- experiment/release policy version/identity, if any;
- composed effective requirements;
- conflict-resolution result;
- identities/hashes of all contributing policy inputs;
- actor/authority metadata for policy changes;
- creation timestamp or governed sequence identity.

The Effective Governance Snapshot MUST be content-addressed or otherwise immutably bound to the governed candidate and its evidence.

Changing governance after a candidate is frozen MUST produce a new governance snapshot and, where the changed rule is material, a fresh governed candidate/evidence cycle.

## 7. Conflict rules

Policy composition MUST be fail-closed.

For the same governed requirement:

- a stricter compatible constraint wins;
- additive requirements accumulate;
- a contradictory lower-level weakening is rejected;
- ambiguity is non-promotable until resolved;
- missing mandatory policy inputs are non-promotable.

Examples:

- Platform requires >=1 independent reviewer; project requires 2 -> effective requirement is 2.
- Platform requires independent review; project says none -> project rule is invalid.
- Platform requires failures preserved; project says delete old failures -> project rule is invalid.
- Platform allows retention >=1 year; project requires 7 years -> effective retention is 7 years.

## 8. Auditability

Every governance change MUST preserve:

- rule identifier;
- old value/state;
- new value/state;
- actor identity/authority;
- rationale;
- effective policy scope;
- governed sequence/version;
- review/adjudication evidence when required.

Policy history MUST NOT be silently rewritten.

## 9. Authority boundary

Policy definition is not qualification authority.

A user, organization, project owner, model, reviewer, or policy composer MUST NOT gain release/promotion authority merely by authoring or selecting governance rules.

The effective policy determines constraints; separate governed evidence and review determine whether those constraints are satisfied.

## 10. Required implementation architecture

The governed platform should expose these logical components:

- Governance Policy Registry
  - Platform Policy
  - Organization Policy
  - Project Policy
  - Experiment / Release Policy
- Policy Composition Engine
- Effective Governance Snapshot
- Policy Conflict Validator
- Policy Change Audit Log
- Governance Snapshot -> Candidate/Evidence Binding

The composition engine MUST be deterministic for the same ordered policy inputs.

## 11. Required falsification cases

At minimum, implementation tests must attempt to falsify:

1. project rule disables mandatory independent review;
2. project rule enables self-approval;
3. project rule lowers a mandatory evidence threshold;
4. project rule deletes/purges required historical failures;
5. project rule weakens a non-overridable authority boundary;
6. conflicting policies are silently accepted;
7. policy changes after source freeze do not trigger a new governance snapshot;
8. evidence produced under policy version A is presented under policy version B;
9. unauthorized actor changes project governance;
10. policy composer produces different effective policy for identical ordered inputs.

Any surviving case blocks promotion.

## 12. Promotion rule

This standard becomes authoritative only after the repository's applicable governance-change review and promotion process closes successfully.

Until then:

- Status = PROPOSED_PENDING_INDEPENDENT_REVIEW
- Authority effect = NONE
