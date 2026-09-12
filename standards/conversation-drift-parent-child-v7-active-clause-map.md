# V7 Composite Active-Clause Map

Status: **PROPOSED V7 — REVIEW REQUIRED — NON-AUTHORITATIVE**

Authority effect: **NONE_EVIDENCE_ONLY**

Composite candidate precedence:

`V5 base -> V6 hardening -> V7 hardening -> this active-clause map`

This map is normative for interpreting the V7 composite candidate. `ACTIVE_NARROWED_BY_V7` means the earlier clause remains conceptually applicable only subject to the stricter V7 rule. `SUPERSEDED` means the earlier permissive mechanism must not be implemented for V7.

## V5 standard mapping

| V5 section | V7 status | Controlling clarification |
|---|---|---|
| §1 Scope and operating modes | ACTIVE_UNCHANGED | Manual/automatic runtime remain API-backed; testing remains manual-only. |
| §2 Trust domains and service identities | ACTIVE_NARROWED_BY_V6 | V6 administrative-domain separation applies. |
| §3 Cryptographic object contract | ACTIVE_NARROWED_BY_V7 | Root-governed registries, monotonic registry versions, root guardian independence apply. |
| §4 Authoritative state objects | ACTIVE_NARROWED_BY_V6 | Root bootstrap plus linearizable WSA apply. |
| §5 WCE | ACTIVE_NARROWED_BY_V6 | V6 schema/time authority and decision application apply. |
| §6 Dependency graph and staleness | ACTIVE_NARROWED_BY_V7 | PGR bootstrap audit and mandatory dependency-class completeness apply. |
| §7 R1 drift classification | ACTIVE_UNCHANGED | R1 remains proposal-only. |
| §8 R1 proposal and DGV evaluation | ACTIVE_NARROWED_BY_V7 | ApplyDecision final revalidation and prepared-decision expiry apply. |
| §9 Relationship downgrade/quorum | ACTIVE_NARROWED_BY_V7 | Root-governed independence registry and final independence recheck apply. |
| §10 ChildImpactRecord | ACTIVE_NARROWED_BY_V7 | Dependency completeness/PGR audit required for permissive impact. |
| §11 Disclosure/approval | ACTIVE_NARROWED_BY_V7 | Consequence-class escrow and live authentication assurance apply. |
| §12 R1 fallback | ACTIVE_NARROWED_BY_V6 | Root-governed fallback activation remains required. |
| §13 RCB isolation | ACTIVE_NARROWED_BY_V7 | Root-governed provenance attestation and content/side-channel controls apply. |
| §14 External request/result lifecycle | ACTIVE_NARROWED_BY_V7 | Provider capability qualification, reservation-before-dispatch, split-brain gateway rules apply. |
| §15 Policy migration/revocation | ACTIVE_NARROWED_BY_V7 | Root-governed schema registry and explicit object-class rebind rules apply. |
| §16 Concurrency/fencing | ACTIVE_NARROWED_BY_V7 | Linearizable WSA and end-to-end downstream fencing apply. |
| §17 WSA/GEL recovery | ACTIVE_NARROWED_BY_V7 | AuthoritativeTransitionCommitment and contiguous WSA->GEL->WAS completeness apply. |
| §18 GEL/WAS | ACTIVE_NARROWED_BY_V7 | Exactly-one-range inclusion and trusted-start completeness apply. |
| §19 Endpoint registry | ACTIVE_NARROWED_BY_V7 | EndpointSchemaRegistry is root-governed/append-only. |
| §20 Cross-standard incident | ACTIVE_NARROWED_BY_V7 | Separate administrative domains and explicit registered claim dependencies apply. |
| §21 Manual vs runtime evidence | ACTIVE_NARROWED_BY_V7 | Test-governor-signed EvidenceClassRecord prevents reclassification. |
| §22 Source precedence | ACTIVE_UNCHANGED | Dev Git/frozen artifacts vs runtime WSA/PRR/GEL separation remains. |
| §23 Current project application | REFERENCE_ONLY | Describes current project checkpoint; not a reusable runtime rule. |
| §24 Freeze condition | ACTIVE_NARROWED_BY_V7 | V7 composite freeze conditions control. |

## V6 hardening mapping

| V6 section | V7 status | Controlling clarification |
|---|---|---|
| §1 Base binding/precedence | ACTIVE_NARROWED_BY_V7 | This explicit map removes stricter-overrides ambiguity. |
| §2 RGA/bootstrap | ACTIVE_NARROWED_BY_V7 | RootGuardianIndependenceSnapshot and root-governed registry list apply. |
| §3 Administrative-domain separation | ACTIVE_NARROWED_BY_V7 | Root guardian/common-admin checks and cross-standard separation add constraints. |
| §4 DGV decision ledger/WSA application | ACTIVE_NARROWED_BY_V7 | Final authority revalidation and deterministic PREPARED expiry/supersession apply. |
| §5 Schema authority/sunset | ACTIVE_NARROWED_BY_V7 | GovernanceSchemaRegistry itself is root-governed and monotonic. |
| §6 Trusted time | ACTIVE_NARROWED_BY_V7 | Root-governed trusted-time authority/quorum and no local-clock authority apply. |
| §7 PGR | ACTIVE_NARROWED_BY_V7 | Independent PredicateBootstrapAudit required. |
| §8 Quorum identity/conflict | ACTIVE_NARROWED_BY_V7 | Independence registry is root-governed and rechecked at final commit. |
| §9 External effect boundary | ACTIVE_NARROWED_BY_V7 | Provider qualification, reservation-before-dispatch and gateway linearizability apply. |
| §10 Linearizable WSA/fencing | ACTIVE_NARROWED_BY_V7 | Every downstream effector must enforce fencing or be mediated. |
| §11 Reviewer provenance | ACTIVE_NARROWED_BY_V7 | Provenance authority is root-governed and producer cannot self-attest. |
| §12 Disclosure escrow | ACTIVE_NARROWED_BY_V7 | ConsequenceClassRegistry defines reversible vs irreversible actions. |
| §13 Approval assurance | ACTIVE_NARROWED_BY_V7 | Current AuthenticationAssuranceSnapshot required at commit. |
| §14 Endpoint registry | ACTIVE_NARROWED_BY_V7 | Registry itself root-governed; all endpoints require active schema. |
| §15 Continuous GEL/WAS coverage | ACTIVE_NARROWED_BY_V7 | WSA authoritative commitments and trusted-start completeness required. |
| §16 Cross-standard dual authority | ACTIVE_NARROWED_BY_V7 | Authorities must also have separate administrative/credential domains. |
| §17 Test governor/oracle | ACTIVE_NARROWED_BY_V7 | TestGovernorAuthorityRegistry root-governed; post-start oracle mutation permanently invalidates run. |
| §18 Unique path coverage/positives | ACTIVE_NARROWED_BY_V7 | Minimum per-critical-mechanism negative+positive+recovery coverage required. |
| §19 Regression obligation | ACTIVE_NARROWED_BY_V7 | WDPC-01..113 remain mandatory under this map. |
| §20 Current testing rule | ACTIVE_UNCHANGED | AI/model reviewer outputs are not qualifying manual review evidence. |
| §21 Freeze condition | SUPERSEDED | V7 freeze condition controls. |

## V7 hardening mapping

All normative V7 sections §1–§20 are `ACTIVE_UNCHANGED` for the V7 candidate unless a later exact revision explicitly supersedes them.

## Matrix precedence

- WDPC-01…95 remain active regressions from V5.
- WDPC-96…113 remain active regressions from V6.
- WDPC-114 onward are added by V7.
- When an older expected endpoint conflicts with a stricter V7 mechanism, the V7 extension MUST explicitly name the revised endpoint/constraint before execution; otherwise the case is `COMPOSITE_PRECEDENCE_AMBIGUOUS` and cannot count as PASS.

This map grants no merge, release, production, qualification, adjudication, or terminal authority.
