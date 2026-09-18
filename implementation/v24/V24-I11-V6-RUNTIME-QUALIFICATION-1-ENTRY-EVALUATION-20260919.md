# V24-I11-V6 Runtime Qualification 1 — Entry Evaluation

Evaluation date: 2026-09-19  
Phase state: `IN_PROGRESS_NOT_QUALIFIED`  
Runtime status: `NOT_NOMINATED`  
Scientific execution: `CLOSED_PENDING_SUCCESSOR_REVIEW`  
Authority effect: `NONE_EVIDENCE_ONLY`

## Provider baseline re-verification

The provider baseline supplied for this evaluation is internally consistent as an
AWS x86_64 production-representative image binding:

- AMI: `ami-0990d6cd071996c3c`
- snapshot: `snap-02073dd5c4e924a8f`
- AMI name: `v24-rq1-qualified-baseline-20260918`
- root volume: `50 GiB gp3`
- runner name: `v24-rq1-aws`
- runner label: `v24-rq1`

These values are recorded as provider-supplied baseline facts. They do not by
themselves nominate the runtime or satisfy the subject's required immutable
runtime evidence fields. The subject JSON therefore remains intentionally
unbound (`runtime_binding.status=NOT_NOMINATED`).

## Criterion evaluation

| # | Entry criterion | Evaluation | Status |
|---:|---|---|---|
| 1 | Frozen predecessor commit/tree reverified | Subject and preregistration retain commit `c6304d0f14914c3b1e9f30a8a42ac231f152fa8f` and tree `dc55289eff2294dbc172e41b045ec80b05d61299`. | SATISFIED |
| 2 | Phase ancestry verified | Qualification branch is `qualification/v24-i11-v6-runtime-qualification-1`; predecessor is retained as immutable construction evidence. | SATISFIED |
| 3 | Preregistration committed before runtime tests | Preregistration commit `d640f4994c980e775e6b0af726ec8ff4e46c1588` is present. | SATISFIED |
| 4 | Exact service/gate/bootstrap/protocol/schema identities bound | Subject contains all exact construction identities and hashes. | SATISFIED |
| 5 | Target host/image bound by immutable evidence | AMI/snapshot facts are available, but have not been entered into a nominated subject binding with host/image evidence digest. | PENDING NOMINATION |
| 6 | Runtime owner and evidence custodian identified | Runtime owner was named by the human as project owner/Vijay Kumar; evidence custodian is not recorded in the subject. | BLOCKED — HUMAN ACTION |
| 7 | Trust assumptions explicitly accepted and measurable | Preregistered assumptions exist; formal runtime acceptance by the owner is not recorded. | BLOCKED — HUMAN ACTION |
| 8 | Every falsification case has deterministic oracle/evidence location | RQ-01 through RQ-32 and their required outcomes are preregistered. | SATISFIED |
| 9 | Synthetic/evidence-only sinks confirmed | Phase contract requires synthetic evidence-only sinks; no scientific or external effect sink is authorized. | SATISFIED |
| 10 | Scientific execution asserted closed | Subject remains `CLOSED_PENDING_SUCCESSOR_REVIEW`. | SATISFIED |
| 11 | Authority effect asserted none-evidence-only | Subject remains `NONE_EVIDENCE_ONLY`. | SATISFIED |
| 12 | Phase remains in progress/not qualified | Subject remains `IN_PROGRESS_NOT_QUALIFIED` / `NOT_QUALIFIED`. | SATISFIED |
| 13 | Trusted and candidate identities provisioned independently | Sealed VM preparation evidence records `v24candidate` and root-owned trusted paths; subject runtime binding is not yet populated. | CONDITIONALLY VERIFIED — BINDING PENDING |
| 14 | Required OS controls/filesystem semantics measurable | Sealed VM evidence records the post-fix controls, AppArmor/auditd posture, root filesystem, and same-filesystem preparation. | CONDITIONALLY VERIFIED — BINDING PENDING |
| 15 | Successor-9 and inherited regressions available unchanged | Construction evidence retains `338/338 PASS` and immutable historical RED/CHANGES_REQUIRED evidence. | SATISFIED |
| 16 | Historical RED/failed workflow evidence immutably bound | Successor-9 RED `35347420339`, final construction run `35352723840`, and prior failure evidence remain referenced. | SATISFIED |
| 17 | Independent final reviewer designated | Independent review is required after runtime evidence freeze; reviewer identity is not recorded. | BLOCKED — HUMAN ACTION |
| 18 | Production dependencies not silently replaced by fixtures | No runtime tests have started; no dependency substitution has been authorized. | SATISFIED FOR ENTRY PREPARATION |

## Gate result

The entry gate remains **NOT READY**. The deterministic preflight reports
`RUNTIME_NOT_NOMINATED` and must continue to fail closed. No RQ-01–RQ-32 case,
runner registration, provider snapshot, or qualification claim is permitted.

Human-only actions still required before nomination are:

1. nominate this exact AMI/snapshot-backed runtime and provide immutable host/image evidence;
2. record the evidence custodian;
3. record explicit owner acceptance of the trust assumptions;
4. designate the independent final reviewer.

