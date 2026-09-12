**Note:** This is an AI-generated candidate engineering review of the supplied packet. It is not a valid independent manual external review, does not satisfy the packet’s prohibition on reviewer/model API calls, and must not be treated as manual-review evidence, approval, authority, or adjudication.

---

### A. Overall disposition

`CHANGES_REQUIRED`

---

### B. Critical findings

| Finding ID | Severity | Affected section/case | Concrete false-green path | Why V6 is insufficient | Narrow fix | Exact falsification test |
|---|---|---|---|---|---|---|
| CF-01 | Critical | RGA / root bootstrap / WDPC-96, WDPC-113 | Root bootstrap threshold is satisfied by guardians who are aliases or controlled by one cloud/org root admin. | V6 requires 3-of-5 across three control domains but does not require independent verification of control-domain ownership or forbid common cloud/org root control. | Add root-governance attestation proving each guardian’s control domain is administratively independent, with no shared cloud/org root, HSM admin, or identity admin. | Compromise one cloud root admin; attempt to satisfy root threshold via aliases or shared domains; expect `ROOT_GOVERNANCE_REJECTED`. |
| CF-02 | Critical | DGV/WSA decision application / WDPC-98 | DGV `ALLOW` is prepared, WSA crashes, decision is replayed after policy/key revocation, and WSA commits because it trusts the old decision. | V6 adds `DecisionConsumptionLedger` but does not explicitly require revocation/expiry recheck at `ApplyDecision` beyond decision lifecycle. | Require WSA `ApplyDecision` to revalidate current key/role/policy/revocation state and reject if any authority changed after decision preparation. | Revoke DGV key after `PREPARED`; call `ApplyDecision`; expect rejection, not transition. |
| CF-03 | Critical | External effects / WDPC-104 | Provider has no true idempotency but claims it; gateway retries after ambiguous failure, creating two external effects. | V6 relies on provider idempotency capability but does not require independent qualification/attestation of that capability. | Require provider idempotency capability to be independently attested and tested; default to at-most-once/`OUTCOME_UNKNOWN_BLOCKED` if unproven. | Use provider that falsely claims idempotency; inject post-dispatch crash; retry; expect exactly one effect or blocked unknown, never two. |
| CF-04 | Critical | WSA consensus/fencing / WDPC-105 | Partitioned former leader commits to downstream system that does not enforce fencing tokens. | V6 requires linearizable WSA but does not require downstream effectors to validate fencing tokens or be part of same consensus boundary. | Require every consequential downstream effector to enforce current fencing token or be mediated by WSA-backed gateway. | Partition WSA; former leader attempts downstream write with stale token; expect downstream rejection or no effect. |
| CF-05 | Critical | GEL/WAS coverage / WDPC-109 | Privileged actor deletes a RED event before next anchor; later anchor omits it; qualification relies on unanchored history. | V6 requires contiguous anchoring but does not fully prove completeness from genesis/current trusted start or prevent authoritative events outside GEL sequence. | Require authoritative event sequence commitment from WSA outbox to GEL, with WAS verifying inclusion of every authoritative event before terminal qualification. | Delete recent RED event before anchor; attempt qualification; expect `LEDGER_ANCHOR_COVERAGE_GAP` and block. |
| CF-06 | Critical | PGR/dependency completeness / WDPC-101, WDPC-102 | Policy owner omits a mandatory dependency class at bootstrap; PGR never includes it; `PARENT_UNAFFECTED` becomes permanently available. | V6 requires root-governed dependency-class templates but does not fully define bootstrap completeness or independent falsification of PGR logic. | Add independent PGR bootstrap audit and mandatory dependency-class completeness proof before any `PARENT_UNAFFECTED` can qualify. | Omit a known material dependency edge; submit `PARENT_UNAFFECTED`; expect `DEPENDENCY_GRAPH_INCOMPLETE_BLOCKED`. |
| CF-07 | Critical | Quorum/independence / WDPC-103 | Two confirmers have distinct keys but same credential-admin domain or beneficial owner, so quorum is not independent. | V6 defines `PrincipalIndependenceRegistry` but does not fully prevent stale or misreported beneficial ownership or credential-admin control. | Require atomic recheck of independence registry at final commit and forbid quorum when any shared credential-admin domain could impersonate both. | Create two keys under same credential-admin domain; attempt gate-removing decision; expect `QUORUM_INDEPENDENCE_REJECTED`. |
| CF-08 | Critical | Disclosure escrow / WDPC-107 | Automatic material drift enters escrow, disclosure times out, but irreversible effect is released because timeout is misinterpreted. | V6 says timeout blocks escrow release but does not fully define all irreversible effects or emergency exceptions. | Narrowly define irreversible effects and require root-governed emergency policy to name exact action class and authority. | Timeout disclosure; attempt terminal qualification or external effect; expect blocked and escalated. |
| CF-09 | Critical | Approval assurance / WDPC-108 | Session assurance drops after approval but before final commit; WSA commits using stale assurance. | V6 requires revalidation at final commit but does not fully bind to authentication event freshness and revocation propagation. | Require final commit to verify current session assurance and authentication event validity, not just recorded assurance level. | Downgrade session assurance after approval; attempt commit; expect `APPROVAL_ASSURANCE_REJECTED`. |
| CF-10 | Critical | Cross-standard authority / WDPC-110 | One workflow authority signs both workflow and claim dispositions; linker accepts it as dual authority. | V6 requires separate signatures but does not fully prevent one administrative domain from controlling both authorities. | Require independent root authorization for `WorkflowDispositionAuthority` and `ClaimEvidenceDispositionAuthority` with separate administrative domains. | Sign both dispositions with same service principal; expect `CROSS_STANDARD_AUTHORITY_COUPLING_REJECTED`. |

---

### C. High / Medium / Low findings

| Finding ID | Severity | Affected section/case | Concrete false-green path | Why V6 is insufficient | Narrow fix | Exact falsification test |
|---|---|---|---|---|---|---|
| HF-01 | High | Schema sunset / WDPC-99 | Old-schema signed object is replayed after sunset but accepted because signature valid. | V6 defines sunset but does not fully prevent schema-registry migration replay or downgrade. | Require schema registry changes to be root-threshold signed and monotonic; reject any new authority use of sunset schema. | Replay old-schema WCE after sunset; expect rejection. |
| HF-02 | High | Trusted time / WDPC-100 | Time source rolls back; object sequence matches but expiry passes incorrectly. | V6 sequence-first but does not fully define time-source disagreement resolution. | Require trusted-time disagreement to produce `TIME_AUTHORITY_CONFLICT_BLOCKED` for all time-dependent authority. | Roll back time source beyond tolerance; attempt expiry-dependent action; expect block. |
| HF-03 | High | Reviewer provenance / WDPC-106 | Forged provenance attestation is accepted because producer self-declares allowed origin. | V6 requires separate provenance service but does not fully prevent provenance service compromise or forged ingestion origin. | Require provenance service to be root-governed and independently attested; chain to signed WSA/GEL/PRR state. | Forge provenance tag; expect `INSUFFICIENT_REVIEW_PROVENANCE`. |
| HF-04 | High | Endpoint registry / WDPC-84 | Endpoint label exists but owner-signed record missing; test governor accepts label. | V6 requires registry but does not fully prevent registry mutation to make invalid outcome look valid. | Make EndpointSchemaRegistry root-governed and append-only; reject any unregistered endpoint. | Claim endpoint without owner record; expect `INSUFFICIENT_EVIDENCE`. |
| HF-05 | High | Test governor/oracle / WDPC-111 | Expected endpoint changed after actor execution; run still qualifies. | V6 requires frozen endpoint but does not fully prevent root-governed post-hoc change. | Require oracle mutation to invalidate run as `ORACLE_INTEGRITY_REJECTED` with no override. | Change expected endpoint after execution; expect invalidation. |
| HF-06 | High | Composite precedence / D | V6 silent on a V5 rule; ambiguity allows permissive V5 interpretation. | V6 precedence rule is clear but does not enumerate every V5 clause that remains active. | Produce explicit V5+V6 active-clause matrix before freeze. | Find a V5 clause that V6 contradicts without narrowing; expect ambiguity finding. |
| HF-07 | Medium | Positive controls / R | System blocks all but narrow happy paths; positive controls insufficient to detect overblocking. | V6 adds positives but does not define minimum unique-enforcement-path coverage threshold. | Define minimum coverage per critical mechanism with negative and positive controls. | Run broad legitimate recovery; expect no false block. |
| HF-08 | Medium | DGV decision lifecycle / F | WSA never applies `PREPARED` decisions; DGV lifecycle remains ambiguous. | V6 does not fully define expiry/supersession of never-applied decisions. | Add decision expiry/supersession policy and reconciliation. | Leave `PREPARED` decision unapplied; expect expiry/supersession. |
| HF-09 | Medium | External effect reconciliation / J | Operator override bypasses `OUTCOME_UNKNOWN_BLOCKED` without authority. | V6 mentions reconciliation but does not fully bind operator override to authority. | Require operator override to be root-governed or quorum-authorized. | Attempt manual override of unknown effect; expect rejection without authority. |
| HF-10 | Low | RCB side channels / WDPC-78 | Timing/completion count leaks through metadata. | V6 normalizes side channels but does not prove all channels covered. | Add explicit side-channel test corpus. | Inject timing side channel; expect `REVIEW_CONTEXT_REJECTED_LEAKAGE`. |

---

### D. Composite V5+V6 precedence assessment

V6 correctly states stricter-overrides-V5. However, the composite candidate does not provide an explicit active-clause matrix. This creates ambiguity for WDPC-01..95: some V5 endpoints may need V6 endpoint/authority updates (e.g., DGV decisions, escrow, quorum independence). Without a clause-by-clause mapping, reviewers cannot deterministically know which V5 rules remain active. **Status: NEEDS_NARROWING.**

---

### E. RGA/root-of-trust and administrative-domain assessment

Root bootstrap still moves the trust problem upward to 3-of-5 guardians. V6 does not sufficiently prove control-domain independence, prevent common cloud/org root control, or prevent guardian aliases. Root rotations are chained but not fully replay-protected. Runtime components cannot self-bootstrap, which is good, but administrative-domain separation is necessary-not-sufficient. **Status: NEEDS_NARROWING.**

---

### F. DGV/WSA decision-consumption assessment

`DecisionConsumptionLedger` improves at-most-once semantics. However, WSA `ApplyDecision` must recheck revocation/expiry/policy changes at commit. Crash between DGV `PREPARED` and WSA commit is handled, but ambiguous never-applied decisions need expiry. Split-brain between DGV and WSA is not fully addressed. **Status: NEEDS_NARROWING.**

---

### G. Schema/time/cryptographic-governance assessment

Schema sunset and trusted-time rules are directionally correct. Gaps: schema-registry migration replay/downgrade, time-source compromise, and trusted-time disagreement. Historical verification vs current authority use is separated, but schema registry changes themselves need root-threshold protection and monotonicity. **Status: NEEDS_NARROWING.**

---

### H. PGR/dependency/ChildImpact assessment

PGR introduces predicate governance but does not fully answer who falsifies predicate logic, how mandatory dependency-class completeness is decided, or how graph/template migration prevents stale evidence from appearing valid. SCC/fixpoint semantics are mentioned but not fully specified. `PARENT_UNAFFECTED` remains vulnerable to omitted dependencies. **Status: MISSING_ENFORCEMENT.**

---

### I. Quorum/independence assessment

`PrincipalIndependenceRegistry` is a good addition. Gaps: who governs the registry, can it self-grant, stale beneficial ownership, credential-admin impersonation, and atomic recheck at final commit. Two confirmers across two control domains may be insufficient for gate-removing decisions without credential-admin independence. **Status: NEEDS_NARROWING.**

---

### J. External-effect exactly-once assessment

`EffectReservation` plus provider idempotency is directionally correct. Critical gaps: provider idempotency capability is not independently qualified/attested; non-idempotent providers can deadlock or require unsafe manual override; dispatch-before-reservation and split-brain gateway duplication are not fully prevented. **Status: MISSING_ENFORCEMENT.**

---

### K. WSA consensus/fencing assessment

V6 requires linearizable WSA and quorum-committed fencing. Gaps: downstream systems may not enforce fencing tokens; token allocation and state mutation must be in same consensus state machine; failover must preserve decision-consumption history; no-quorum behavior must fail closed for all consequential writes. **Status: NEEDS_NARROWING.**

---

### L. RCB provenance/reviewer-isolation assessment

`SourceProvenanceAttestation` improves independence. Gaps: provenance service itself must be root-governed; forged ingestion origin; artifact content can still leak prior findings; timing/provider/length/order side channels need explicit normalization; positive reviewer-context path must remain useful. **Status: NEEDS_NARROWING.**

---

### M. Disclosure/approval assessment

Escrow and approval assurance are improvements. Gaps: “reversible internal bookkeeping” must be narrowly defined; emergency/root-governed exception must not become general bypass; disclosure delivery identity must match actual user/channel semantics; approval assurance must be rechecked at commit and bound to action class. **Status: NEEDS_NARROWING.**

---

### N. Endpoint/evidence-class assessment

V6 requires complete endpoint registry. Gaps: EndpointSchemaRegistry itself can be changed to make invalid outcomes look valid; `DESIGN_MANUAL_REVIEW` can masquerade as runtime evidence unless enforced; evidence-class metadata can be forged/reclassified. **Status: NEEDS_NARROWING.**

---

### O. GEL/WAS completeness assessment

Contiguous anchoring is an improvement. Gaps: completeness from genesis/current trusted start is not proven; authoritative events outside GEL sequence are possible; privileged actor can race/replace event sequence before WAS; exactly-one-range inclusion is not fully required; gaps/overlaps/duplicate sequence numbers/witness rollback need explicit handling. **Status: MISSING_ENFORCEMENT.**

---

### P. Cross-standard EXP-K boundary assessment

Dual signatures and hard-coded non-authorization flags are good. Gaps: who authorizes `WorkflowDispositionAuthority` and `ClaimEvidenceDispositionAuthority`; can one administrative domain control both; can claim state influence workflow via PRR predicates without explicit transition. EXP-K reference does not contradict V6 but exposes overlap risk. **Status: NEEDS_NARROWING.**

---

### Q. Test-governor/oracle assessment

Test governor independence is asserted but not fully bootstrapped or governed. Gaps: who governs test-governor signing authority; can evaluator metadata leak expected endpoint; can root governance change expected endpoint after execution; opaque fixture handles may not prevent semantic leakage through payload content. **Status: NEEDS_NARROWING.**

---

### R. Positive-control/overblocking assessment

V6 adds positive controls but does not define minimum unique-enforcement-path coverage threshold. A system that blocks all but explicit happy paths could still pass. Missing legitimate concurrent, recovery, degraded-mode, failover, policy-migration, disclosure, reviewer-context, and external-effect positive variants. **Status: NEEDS_NARROWING.**

---

### S. WDPC-01..WDPC-113 audit

Note: Classifications assess the preregistered case specification, not runtime execution. Runtime PASS for any case remains INSUFFICIENT_EVIDENCE until executed under the required evidence class.

| Case | Status | Note |
|---|---|---|
| WDPC-01 | ADEQUATE | No consequential transition; owner record expected. |
| WDPC-02 | ADEQUATE | Child creation bound to WSA. |
| WDPC-03 | ADEQUATE | Root identity preserved. |
| WDPC-04 | NEEDS_NARROWING | Dependency impact needs V6 PGR/template completeness. |
| WDPC-05 | NEEDS_NARROWING | Process-only staleness needs PGR predicate governance. |
| WDPC-06 | ADEQUATE | Constraint addition requires impact record. |
| WDPC-07 | NEEDS_NARROWING | RCB leakage; needs V6 provenance attestation. |
| WDPC-08 | NEEDS_NARROWING | `PARENT_UNAFFECTED` needs V6 graph completeness. |
| WDPC-09 | ADEQUATE | Resume without impact rejected. |
| WDPC-10 | ADEQUATE | Malformed impact rejected. |
| WDPC-11 | ADEQUATE | No terminal authority from claim alone. |
| WDPC-12 | ADEQUATE | Client state non-authoritative. |
| WDPC-13 | ADEQUATE | Valid cancellation positive. |
| WDPC-14 | ADEQUATE | Valid supersession positive. |
| WDPC-15 | ADEQUATE | Nested child root jump denied. |
| WDPC-16 | ADEQUATE | One-edge propagation. |
| WDPC-17 | NEEDS_NARROWING | Fencing needs V6 linearizable WSA. |
| WDPC-18 | ADEQUATE | Parent review blocked while child active. |
| WDPC-19 | NEEDS_NARROWING | RCB needs V6 provenance. |
| WDPC-20 | ADEQUATE | Impact before adjudication blocks. |
| WDPC-21 | ADEQUATE | Stale result rejected. |
| WDPC-22 | ADEQUATE | Repair references stale adjudication denied. |
| WDPC-23 | ADEQUATE | Policy rebind required. |
| WDPC-24 | ADEQUATE | Authority-source defect blocks. |
| WDPC-25 | ADEQUATE | Missing evidence blocks permissive resume. |
| WDPC-26 | ADEQUATE | Sibling independence. |
| WDPC-27 | ADEQUATE | Conflicting siblings blocked. |
| WDPC-28 | ADEQUATE | Reopened child immutable history. |
| WDPC-29 | ADEQUATE | Stale external result. |
| WDPC-30 | ADEQUATE | Client cache non-authoritative. |
| WDPC-31 | ADEQUATE | Late result quarantined. |
| WDPC-32 | NEEDS_NARROWING | Dedup needs V6 EffectReservation. |
| WDPC-33 | ADEQUATE | Wrong workflow ID rejected. |
| WDPC-34 | ADEQUATE | Wrong parent denied. |
| WDPC-35 | ADEQUATE | Approval replay denied. |
| WDPC-36 | ADEQUATE | Automatic overreach denied. |
| WDPC-37 | NEEDS_NARROWING | Race needs V6 linearizable WSA. |
| WDPC-38 | NEEDS_NARROWING | Timeout/late success needs V6 external effect. |
| WDPC-39 | ADEQUATE | Provider substitution checked. |
| WDPC-40 | ADEQUATE | UI label no transition. |
| WDPC-41 | ADEQUATE | WSA/GEL mismatch blocked. |
| WDPC-42 | ADEQUATE | Replayed impact rejected. |
| WDPC-43 | ADEQUATE | Unauthorized downgrade rejected. |
| WDPC-44 | ADEQUATE | Info-only child cannot mutate. |
| WDPC-45 | ADEQUATE | Recursive cycle denied. |
| WDPC-46 | ADEQUATE | Timeout not approval. |
| WDPC-47 | ADEQUATE | Admin evidence import rejected. |
| WDPC-48 | ADEQUATE | Device has zero authority. |
| WDPC-49 | ADEQUATE | R1 self-drift blocked. |
| WDPC-50 | ADEQUATE | R1 assertion overridden by DGV. |
| WDPC-51 | ADEQUATE | Manual material drift disclosure gate. |
| WDPC-52 | NEEDS_NARROWING | Async disclosure needs V6 escrow. |
| WDPC-53 | NEEDS_NARROWING | RCB contamination needs V6 provenance. |
| WDPC-54 | NEEDS_NARROWING | Quorum needs V6 independence registry. |
| WDPC-55 | ADEQUATE | Durable state wins. |
| WDPC-56 | ADEQUATE | R1 unavailable blocked. |
| WDPC-57 | ADEQUATE | Legitimate positive. |
| WDPC-58 | ADEQUATE | False user claim blocked. |
| WDPC-59 | NEEDS_NARROWING | Oracle leak needs V6 test governor. |
| WDPC-60 | ADEQUATE | Prior RED preserved. |
| WDPC-61 | NEEDS_NARROWING | Authorized downgrade needs V6 quorum. |
| WDPC-62 | ADEQUATE | Info-only child positive. |
| WDPC-63 | ADEQUATE | Nonblocking child positive. |
| WDPC-64 | NEEDS_NARROWING | Unaffected resume needs V6 graph completeness. |
| WDPC-65 | ADEQUATE | WCE replay rejected. |
| WDPC-66 | ADEQUATE | Disclosure wrong recipient rejected. |
| WDPC-67 | ADEQUATE | Acknowledgement not approval. |
| WDPC-68 | NEEDS_NARROWING | Clean context needs V6 provenance. |
| WDPC-69 | ADEQUATE | Old-policy result handled. |
| WDPC-70 | NEEDS_NARROWING | Race needs V6 fencing. |
| WDPC-71 | ADEQUATE | Sibling histories preserved. |
| WDPC-72 | ADEQUATE | Unqualified admin import rejected. |
| WDPC-73 | NEEDS_NARROWING | Oracle metadata needs V6 governor. |
| WDPC-74 | ADEQUATE | Cross-standard linkage separate. |
| WDPC-75 | NEEDS_NARROWING | Process-only staleness needs PGR. |
| WDPC-76 | ADEQUATE | WCE key revocation replay rejected. |
| WDPC-77 | ADEQUATE | PRR self-grant rejected. |
| WDPC-78 | NEEDS_NARROWING | Side-channel needs V6 provenance. |
| WDPC-79 | NEEDS_NARROWING | Async timeout needs V6 escrow. |
| WDPC-80 | ADEQUATE | Crash recovery blocked or reconciled. |
| WDPC-81 | NEEDS_NARROWING | Fencing monotonicity needs V6 consensus. |
| WDPC-82 | ADEQUATE | Policy migration + in-flight result handled. |
| WDPC-83 | NEEDS_NARROWING | Confirmer collusion needs V6 independence. |
| WDPC-84 | NEEDS_NARROWING | Endpoint label needs V6 registry. |
| WDPC-85 | NEEDS_NARROWING | Manual vs runtime needs V6 evidence-class enforcement. |
| WDPC-86 | ADEQUATE | Cross-standard recovery separate. |
| WDPC-87 | ADEQUATE | Normal positive control. |
| WDPC-88 | NEEDS_NARROWING | Hidden dependency needs V6 graph completeness. |
| WDPC-89 | ADEQUATE | Approval replay after rebind rejected. |
| WDPC-90 | ADEQUATE | Disclosure ordering enforced. |
| WDPC-91 | NEEDS_NARROWING | Cancellation/sibling race needs V6 fencing. |
| WDPC-92 | NEEDS_NARROWING | Dedup after restart needs V6 EffectReservation. |
| WDPC-93 | ADEQUATE | Fallback expiry/revocation enforced. |
| WDPC-94 | NEEDS_NARROWING | GEL rewrite needs V6 contiguous coverage. |
| WDPC-95 | ADEQUATE | Role revocation at commit enforced. |
| WDPC-96 | NEEDS_NARROWING | Root bootstrap self-grant needs independent domain attestation. |
| WDPC-97 | NEEDS_NARROWING | Single infra principal attack needs stronger admin separation. |
| WDPC-98 | NEEDS_NARROWING | Crash between DGV and WSA needs revocation recheck. |
| WDPC-99 | NEEDS_NARROWING | Old schema replay needs root-governed sunset. |
| WDPC-100 | NEEDS_NARROWING | Time conflict needs deterministic resolution. |
| WDPC-101 | MISSING_ENFORCEMENT | Predicate-owner self-grant needs independent PGR approval. |
| WDPC-102 | NEEDS_NARROWING | Mandatory edge omission needs template completeness. |
| WDPC-103 | NEEDS_NARROWING | Quorum alias needs atomic independence recheck. |
| WDPC-104 | MISSING_ENFORCEMENT | Provider idempotency needs independent attestation. |
| WDPC-105 | NEEDS_NARROWING | Split-brain needs downstream fencing enforcement. |
| WDPC-106 | NEEDS_NARROWING | Forged provenance needs root-governed provenance service. |
| WDPC-107 | NEEDS_NARROWING | Escrow timeout needs narrow irreversible definition. |
| WDPC-108 | NEEDS_NARROWING | Assurance downgrade needs current-session check. |
| WDPC-109 | MISSING_ENFORCEMENT | Unanchored rewrite needs full authoritative event commitment. |
| WDPC-110 | NEEDS_NARROWING | Single-authority forgery needs independent root authorization. |
| WDPC-111 | NEEDS_NARROWING | Oracle mutation needs post-execution invalidation. |
| WDPC-112 | NEEDS_NARROWING | Broad recovery positive needs minimum coverage threshold. |
| WDPC-113 | NEEDS_NARROWING | Root rotation positive needs domain independence proof. |

---

### T. Missing falsification cases

1. Root guardian alias/common-cloud-root collusion.
2. Provenance service compromise/forged ingestion origin.
3. Downstream system ignoring fencing token.
4. Schema-registry migration replay/downgrade.
5. Trusted-time source compromise.
6. PGR predicate logic falsification by independent party.
7. Mandatory dependency-class bootstrap omission.
8. Quorum credential-admin domain impersonation.
9. Provider falsely claiming idempotency.
10. Dispatch before durable reservation commit.
11. Split-brain gateway duplicate dispatch.
12. Reviewer artifact content leaking prior findings despite clean metadata.
13. Emergency/root-governed exception becoming general bypass.
14. EndpointSchemaRegistry mutation making invalid outcome valid.
15. Evidence-class metadata forgery/reclassification.
16. Authoritative event occurring outside GEL sequence.
17. Privileged actor racing/replacing event sequence before WAS.
18. Witness rollback/overlapping anchors/duplicate sequence numbers.
19. One administrative domain controlling both cross-standard authorities.
20. Test-governor signing authority bootstrap/compromise.
21. Oracle mutation after actor execution without invalidation.
22. Minimum unique-enforcement-path coverage threshold.

---

### U. Freeze recommendation

`DO_NOT_FREEZE`

---

### V. Authority limitation

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`