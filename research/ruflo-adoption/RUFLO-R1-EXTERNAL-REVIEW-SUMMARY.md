# Ruflo Selective Adoption R1 — Independent External Review

Overall disposition: `CHANGES_REQUIRED`

Source: user-supplied manual review.

Review summary:

- Critical findings: 0
- High findings: 2
- RQ16 stop preserved: PASS
- EXP-M R5 freeze preserved: PASS
- Direct Ruflo trust avoided: PASS
- Authority effect none: PASS

## High H-01 — RA-04 consumable amplification

Per-child `child <= parent` is insufficient for consumable resources because sibling/depth fan-out can amplify aggregate spend/tokens/concurrency/delegation.

Required repair accepted in R2:

- split non-consumable subset semantics from consumable conservation;
- atomic reservation against parent ledger;
- recorded release/re-lend;
- expiry bounded by parent;
- sibling/concurrency/depth tests.

## High H-02 — RA-11 enforcement not on prerequisite path

Diagnostic-only RA-11 was insufficient before multi-writer/swarm/research automation.

Required repair accepted in R2:

- RA-11 enforcement becomes an explicit prerequisite;
- prerequisite matrix replaces ordinal presence-only gate logic;
- RA-03/04/09/11 enforcement required before authority-bearing RA-10/12/13 paths;
- RA-06/07/10 additional prerequisites for RA-13;
- verify-then-load, revoked publisher/key, transitive dependency and signed-sandbox-escape tests.

## Medium/Low repairs accepted into R2

R2 additionally incorporates the review's requested corrections for:

- scoped/generation-bound qualification;
- evidence-assurance composition and trust roots;
- evaluator/promotion write isolation and CAS;
- RA-07/08 identity/supersession dependency;
- append-only rollback/tamper detection and privacy quarantine;
- source vs execution-context identity;
- explicit experiment oracles, positive controls and test-the-test mutations;
- commit-reveal self-adjudication;
- protected-resource fence enforcement;
- authority-boundary enumeration;
- exact EXP-M deterministic stability trigger;
- out-of-band package identity;
- source-status annotations;
- RA-07 advisory-only/non-deny-list rule;
- generated-registry laundering prevention;
- dirty-snapshot evidence non-transfer;
- composed exfiltration prevention;
- persistent-injection-safe failure retrieval.

This preserved summary is non-authoritative evidence. The complete original user-supplied review remains outside this repository unless separately imported as exact bytes.
