# EXP-O Pilot 27 — Administratively Independent External Root Quorum Preregistration

## Status

PRE-EXECUTION AND EXTERNALLY BLOCKED.

Pilot 27 must not execute until three external asymmetric signing roots exist in three separately administered trust domains. Reusing multiple keys from the same AWS account, IAM administrative boundary, cloud project/subscription, or equivalent control plane does not satisfy this prerequisite.

## Purpose

Pilot 26 established a bounded 2-of-3 quorum across three distinct AWS KMS asymmetric key identities inside one AWS administrative domain. Pilot 27 tests the stronger boundary: whether the same exact-statement quorum remains safe when each root is controlled by a distinct administrative trust domain, including one-domain compromise/conflict, one-domain outage, identity substitution, stale evidence, and mixed-provider/account statement replay.

## Required external topology

Three registered roots A/B/C are required. Each must have:

- a non-exportable asymmetric signing key managed by an external KMS/HSM-capable service;
- its own administrative account/project/subscription boundary;
- its own workload identity / federation path;
- no shared long-lived signing credentials;
- exact provider/account/project/key identity recorded before execution;
- public verification material exportable to the verifier;
- no private signing material available to the verifier, witness, model, or GitHub repository.

At least the following separation is required:

1. no two roots may be controlled by the same AWS account, GCP project, Azure subscription/tenant-equivalent administrative boundary, or equivalent provider control plane;
2. no single workload identity role/service account may have signing authority over more than one root;
3. no one root may count twice through aliasing, cross-account grant labels, provider aliases, or duplicated signatures;
4. if roots use different providers, provider-specific identity metadata is retained as provenance but never treated as authority by itself.

The existing Pilot 26 AWS roots may be reused only as **one administrative-domain contribution**. Multiple keys from the current AWS account still count as one domain for Pilot 27.

## Frozen quorum rule

A checkpoint is eligible only when at least **2 distinct registered administrative domains** produce valid signatures over the exact same canonical checkpoint statement bytes and each contribution is bound to its exact registered external key identity.

Distinctness is evaluated by both:

- exact external key identity; and
- registered administrative-domain identity.

Two valid key signatures from one administrative domain cannot satisfy the threshold alone.

## Frozen canonical statement

The exact signed statement binds at minimum:

- experiment `EXP-O`;
- pilot `PILOT27-INDEPENDENT-ROOT-DOMAINS`;
- project `setugo`;
- task `exp-o-pilot27`;
- generation;
- checkpoint/root digest;
- purpose `independent-root-checkpoint-integrity`;
- nonce;
- registered root-set version.

## Frozen endpoints

1. **P27-01** — exact workload identity and exact external key metadata for all three roots are verified and retained.
2. **P27-02** — three roots have three distinct external key identities and three distinct registered administrative-domain identities.
3. **P27-03** — clean roots A+B from distinct domains over one exact current statement satisfy quorum.
4. **P27-04** — clean roots B+C from distinct domains over one exact current statement satisfy quorum.
5. **P27-05** — two distinct keys from the same administrative domain are insufficient even if both signatures are cryptographically valid.
6. **P27-06** — one valid domain alone is insufficient.
7. **P27-07** — duplicate signature or alias of one domain cannot manufacture a second domain.
8. **P27-08** — a locally forged or unregistered second-domain signature is rejected.
9. **P27-09** — valid signatures from distinct domains over different statement hashes do not combine.
10. **P27-10** — valid signatures from distinct domains over different generations do not combine.
11. **P27-11** — valid signatures from distinct domains over different project/task scope do not combine.
12. **P27-12** — one deliberately conflicting externally signed domain plus two honest domains agreeing resolves only to the exact two-domain agreeing statement.
13. **P27-13** — three valid domain signatures with no statement receiving two-domain agreement form no quorum.
14. **P27-14** — valid old two-domain quorum below trusted minimum generation is ineligible.
15. **P27-15** — external key identity substituted across registered domain identity is rejected rather than reassigned.
16. **P27-16** — provider/account/project metadata substitution cannot convert one domain into another.
17. **P27-17** — one administrative domain unavailable while the other two sign the exact same current statement retains liveness.
18. **P27-18** — signature/domain contribution ordering does not change quorum identity or result.
19. **P27-19** — all tested evidence paths retain `model_authority_effect=false` and `authoritative_platform_effect_count=0`.
20. **P27-20** — clean higher-generation two-domain quorum remains live after earlier isolated attacks/replays.

## Compromise simulation boundary

A compromised-domain case may intentionally obtain a valid signature from one external root over a conflicting but non-consequential synthetic checkpoint statement. This models one administrative domain producing conflicting evidence. It does not claim the cloud provider, KMS service, account, project, tenant, or HSM was actually compromised.

## Safety constraints

- No destructive key-disable, deletion, policy mutation, project/account mutation, or destructive administration probe merely to simulate compromise.
- No static cloud access keys or service-account private keys in GitHub secrets when workload identity federation/OIDC is supported.
- No locally generated private key may substitute for a missing external domain in scientific endpoints.
- Public/provider metadata is provenance only, not authority.
- Valid conflicting signatures are retained as evidence; do not retry until a desired answer appears.
- Root quorum is evidence only and creates no model, merge, release, deploy, or execution authority.
- Workflow success is operational completion only.

## Success criterion

All twenty frozen endpoints must be satisfied on a frozen execution SHA with:

- three registered external roots;
- three registered administrative domains;
- threshold 2-of-3 distinct administrative domains;
- zero same-domain double counting;
- zero duplicate/alias threshold manufacture;
- zero mixed-statement threshold manufacture;
- zero model authority effect;
- zero authoritative platform effects.

## Bounded interpretation

A successful Pilot 27 would establish bounded evidence for the tested external providers/accounts/projects and federation paths only. It would not establish universal cloud-provider security, global Byzantine consensus, resistance to compromise of two administrative domains, or safety of untested identity/federation configurations.
