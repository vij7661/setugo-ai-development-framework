A. Review-evidence declaration
`AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`

B. Overall disposition
`CHANGES_REQUIRED`

C. Critical findings

| Finding ID | Severity | Affected section/case | Concrete false-green/failure path | Why V8 is insufficient | Narrow required fix | Exact falsification test |
|---|---|---|---|---|---|---|
| CF-01 | Critical | V8-C03, WDPC-137, WDPC-148 | Genesis notary independence is asserted out-of-band; a cloud/org/HSM/identity admin can control enough notary/guardian real-world identities to satisfy genesis. | V8 honestly bounds the assumption but does not provide an in-system falsification of real-world notary independence. | Require an explicit qualification gate that treats genesis independence as `INSUFFICIENT_EVIDENCE` unless out-of-band attestation is independently accepted by the governing authority. | Compromise one cloud root admin; attempt to satisfy 2-of-3 notary plus 3-of-5 guardian threshold via aliases/shared domains; expect `GENESIS_ATTESTATION_REJECTED` or freeze block. |
| CF-02 | Critical | V8-C04, WDPC-138 | A consequential operation is mislabeled non-consequential or routed outside the Effect Gateway, bypassing ConsequentialEffectorRegistry and default deny. | V8 defaults deny for unregistered effectors but does not prove who classifies consequence class or prevent non-gateway external calls. | Require independent classification of consequence class and mandate that all external consequential paths be mediated by Effect Gateway or registered effector enforcement. | Route a consequential external call outside the gateway; expect `UNREGISTERED_EFFECTOR_BLOCKED` before side effect. |
| CF-03 | Critical | V8-C02, WDPC-136 | CompositePrecedenceAudit misses a normative clause that lacks listed keywords or references an endpoint implicitly. | Mechanical extraction rules are stated but not proven complete for all normative forms. | Require an extraction proof/corpus demonstrating that all normative and endpoint-bearing clauses are captured, including implicit endpoint references. | Inject a normative clause without keywords; expect `COMPOSITE_PRECEDENCE_AMBIGUOUS`. |
| CF-04 | Critical | V8-C07, WDPC-141, WDPC-151 | ExternalEffectObservation source is compromised or not independent; operator/quorum treats `INDETERMINATE` as `NOT_OCCURRED` and retries, creating duplicate effect. | V8 separates fact from authority but does not fully qualify observation-source independence for high-consequence effects. | Require registered independent observation sources and forbid any retry when observation is `INDETERMINATE` or source is unqualified. | Use compromised observation source claiming `NOT_OCCURRED`; expect `EXTERNAL_EFFECT_OBSERVATION_INSUFFICIENT` and no retry. |
| CF-05 | Critical | V8-C06, WDPC-140 | Predicate auditors are nominally separate but share credential/recovery/admin domains with root guardians, so root can indirectly control audit result. | V8 adds overlap checks but does not fully prove independence from all root-threshold-capable sets. | Require predicate auditors to be independent of any root-threshold-capable subset and rechecked at activation and at `PARENT_UNAFFECTED`. | Create auditors sharing credential-admin domain with three guardians; expect `PREDICATE_AUDIT_INDEPENDENCE_REJECTED`. |
| CF-06 | Critical | V8-C05, WDPC-139, WDPC-150 | A validly signed emergency policy uses a broad trigger or allowed class to become a general bypass within permitted bounds. | V8 constrains exclusions but does not fully bound trigger specificity or invocation-count enforcement. | Require maximum invocation count enforcement, narrow trigger predicate IDs, and audit of every emergency invocation against the root constraint registry. | Invoke broad emergency trigger repeatedly; expect `EMERGENCY_POLICY_SCOPE_REJECTED` or invocation ceiling block. |
| CF-07 | Critical | V8-C13, V8-M04, WDPC-147 | Case Evidence Profile Map omits a required profile for a new case or allows “where applicable” judgment to waive evidence. | V8 mechanically audits profile coverage but depends on complete case registry and profile definitions. | Require TestGovernor/CompositePrecedenceAudit to reject any case lacking explicit profile coverage and forbid executor removal of profiles. | Add a case without profile mapping; expect `EVIDENCE_PROFILE_INCOMPLETE`. |

D. High / Medium / Low findings

| Finding ID | Severity | Affected section/case | Concrete false-green/failure path | Why V8 is insufficient | Narrow required fix | Exact falsification test |
|---|---|---|---|---|---|---|
| HF-01 | High | V8-C08, WDPC-144 | `PRESERVE_EXACT` grandfathering becomes generic bypass for newly mandatory criteria. | V8 requires GrandfatherDecision but does not fully govern the “grandfatherable” property independently. | Require independent root/PRR governance of criterion grandfatherable status. | Mark new criterion grandfatherable without independent approval; expect `GRANDFATHER_DECISION_REJECTED`. |
| HF-02 | High | V8-C10, WDPC-146 | Policy rebind omits a live object class that appears later and inherits default disposition. | V8 closes enum but depends on complete live-object inventory. | Require mechanical inventory comparison at rebind time. | Add live object class after rebind; expect `REBIND_DISPOSITION_MISSING`. |
| HF-03 | High | V8-C11, WDPC-143 | CrossDomainOrderingService becomes hidden authority through ordering choice. | V8 declares non-substantive but causal evidence can be forged/incomplete. | Require ordering record to be evidence-only with no substantive authority and fail closed on ambiguity. | Forge causal evidence to force `WORKFLOW_BEFORE_CLAIM`; expect `CONCURRENT_REEVALUATION_REQUIRED` or rejection. |
| HF-04 | High | V8-C04, WDPC-152 | Newly registered effector accepts stale fencing token despite registry entry. | V8 requires fencing mode but does not prove end-to-end enforcement. | Require direct token validation or WSA gateway mediation for every registered effector. | Send stale token to registered effector; expect rejection before side effect. |
| HF-05 | High | V8-C14, WDPC-142 | Compound positive control is special-cased while common legitimate workloads still overblock. | V8 adds one compound scenario but does not define minimum unique-path coverage threshold. | Define minimum coverage per critical mechanism and include broader legitimate workload variants. | Run broad legitimate recovery; expect no false block. |
| MF-01 | Medium | V8-C15, WDPC-127 | Post-run registry change retroactively legalizes failing run. | V8 binds run to frozen start digests but does not fully prevent later reinterpretation. | Require run evaluation against frozen start registry digests only; post-run changes require new run. | Change endpoint schema after run; expect run remains FAIL. |
| MF-02 | Medium | V8-C16, WDPC-136 | New endpoint added without owner/schema registration. | V8 adds endpoint list but depends on EndpointSchemaRegistry completeness. | Require mechanical endpoint registration check before execution. | Execute case with unregistered endpoint; expect block. |
| MF-03 | Medium | V8-C03, WDPC-148 | Platform super-admin invokes enough root/notary keys. | V8 states requirement but not proof of storage architecture. | Require hardware-backed/offline root key policy proof. | Attempt threshold via platform admin; expect failure or `INSUFFICIENT_EVIDENCE`. |
| LF-01 | Low | V8-M06 | Human section references used as machine keys. | V8 defines stable identity but legacy map may still rely on display numbers. | Use only source blob SHA + normalized heading path + ordinal + canonical text digest. | Change heading format; expect stable clause identity. |

E. Composite precedence assessment
V8-C02 and V8-M05 improve mechanical audit and fail-closed mapping. Remaining gap: extraction completeness for non-keyword normative clauses and implicit endpoint references. The audit itself is root-governed, but freeze depends on an unproven extraction algorithm. `NEEDS_NARROWING`.

F. Genesis/root-governance assessment
V8-C03 honestly bounds the genesis trust assumption and adds offline notarization. However, real-world notary independence remains out-of-band and cannot be falsified in-system. This is acceptable only if qualification explicitly marks genesis independence as `INSUFFICIENT_EVIDENCE` until independently accepted. Otherwise, false trust bootstrap remains. `NEEDS_NARROWING` / `INSUFFICIENT_EVIDENCE`.

G. Effector/fencing assessment
ConsequentialEffectorRegistry and default deny close many gaps. Remaining risks: consequence-class mislabeling, non-gateway external paths, and downstream effectors not enforcing fencing tokens. Need independent consequence classification and mandatory gateway mediation. `NEEDS_NARROWING`.

H. Emergency-policy assessment
V8-C05 adds hard bounds and forbidden consequence classes. Remaining risk: validly signed emergency policy with broad trigger or weak invocation ceiling. Need maximum invocation enforcement and audit. `NEEDS_NARROWING`.

I. PGR/dependency assessment
V8-C06 strengthens predicate-audit independence from root guardians. Remaining risk: indirect control via shared credential/recovery domains and incomplete mandatory dependency inventory. Need independent bootstrap audit and recheck at `PARENT_UNAFFECTED`. `NEEDS_NARROWING`.

J. OUTCOME_UNKNOWN evidence/authorization assessment
V8-C07 correctly separates ExternalEffectObservation from reconciliation decision. Remaining risk: observation source compromise and `INDETERMINATE` treated as `NOT_OCCURRED`. Need independent observation-source qualification. `NEEDS_NARROWING`.

K. Grandfather/rebind/terminal-rejection assessment
V8-C08, V8-C09, V8-C10 close many audit gaps. Remaining risk: `PRESERVE_EXACT` as bypass and incomplete live-object inventory. Need independent grandfatherable governance and mechanical inventory comparison. `NEEDS_NARROWING`.

L. Cross-standard ordering assessment
V8-C11 keeps ordering non-substantive and fails closed on concurrency. Remaining risk: forged causal evidence. Need evidence-only ordering with ambiguity forced to `CONCURRENT_REEVALUATION_REQUIRED`. `NEEDS_NARROWING`.

M. Evidence-profile/test-governor assessment
V8-C13 and V8-M04 eliminate “where applicable” discretion. Remaining risk: missing case mapping and profile omission. Need mechanical verification of all WDPC cases. `NEEDS_NARROWING`.

N. Positive-control/overblocking assessment
V8 adds WDPC-142 and other positives. Still lacks minimum unique-enforcement-path coverage threshold and broader legitimate workload variants. `NEEDS_NARROWING`.

O. WDPC-01..WDPC-152 audit

| Case | Status | Note |
|---|---|---|
| WDPC-01 | ADEQUATE | UI focus only; no governed transition. |
| WDPC-02 | ADEQUATE | Authorized blocking child creation. |
| WDPC-03 | ADEQUATE | Long-running child cannot become root. |
| WDPC-04 | ADEQUATE | Candidate mutation invalidates dependent evidence. |
| WDPC-05 | ADEQUATE | Process-only change staleness. |
| WDPC-06 | NEEDS_NARROWING | Grandfather decision must be independent; V8-C08. |
| WDPC-07 | ADEQUATE | Reviewer contamination blocked. |
| WDPC-08 | ADEQUATE | Deterministic unaffected child. |
| WDPC-09 | ADEQUATE | Return without ChildImpactRecord blocked. |
| WDPC-10 | ADEQUATE | Malformed impact rejected. |
| WDPC-11 | NEEDS_NARROWING | Terminal rejection endpoint required; V8-C09. |
| WDPC-12 | ADEQUATE | Device/session leave and return. |
| WDPC-13 | ADEQUATE | Valid manual cancellation. |
| WDPC-14 | ADEQUATE | Valid supersession. |
| WDPC-15 | ADEQUATE | Nested child root jump denied. |
| WDPC-16 | ADEQUATE | One-edge nested propagation. |
| WDPC-17 | ADEQUATE | Concurrent writer race. |
| WDPC-18 | ADEQUATE | Parent review while child active. |
| WDPC-19 | ADEQUATE | Prior finding injected. |
| WDPC-20 | ADEQUATE | Impact after reviews before adjudication. |
| WDPC-21 | ADEQUATE | Impact while adjudication in flight. |
| WDPC-22 | ADEQUATE | Impact after adjudication before repair. |
| WDPC-23 | ADEQUATE | Policy change requires rebind. |
| WDPC-24 | ADEQUATE | Authority-source defect. |
| WDPC-25 | ADEQUATE | Child result lacks mandatory evidence. |
| WDPC-26 | ADEQUATE | Multiple sibling children. |
| WDPC-27 | ADEQUATE | Conflicting sibling impacts. |
| WDPC-28 | ADEQUATE | Reopen completed child. |
| WDPC-29 | ADEQUATE | Parent changes while child result in flight. |
| WDPC-30 | ADEQUATE | Client restart loses graph cache. |
| WDPC-31 | ADEQUATE | Late result after child cancellation. |
| WDPC-32 | ADEQUATE | Duplicate request after restart. |
| WDPC-33 | ADEQUATE | Result carries wrong workflow ID. |
| WDPC-34 | ADEQUATE | Child creation carries wrong parent ID. |
| WDPC-35 | ADEQUATE | Approval replay. |
| WDPC-36 | ADEQUATE | Automatic policy overreach. |
| WDPC-37 | ADEQUATE | Manual/automatic race. |
| WDPC-38 | ADEQUATE | Timeout + late success + retry success. |
| WDPC-39 | ADEQUATE | Provider substitution mid-child. |
| WDPC-40 | ADEQUATE | UI label changes only. |
| WDPC-41 | ADEQUATE | WSA/GEL mismatch. |
| WDPC-42 | ADEQUATE | Replay ChildImpactRecord. |
| WDPC-43 | ADEQUATE | Unauthorized downgrade. |
| WDPC-44 | ADEQUATE | Information-only child attempts mutation. |
| WDPC-45 | ADEQUATE | Recursive child loop/cycle. |
| WDPC-46 | ADEQUATE | Blocking child times out. |
| WDPC-47 | ADEQUATE | Paste external review into manual mode. |
| WDPC-48 | ADEQUATE | Resume from another device. |
| WDPC-49 | ADEQUATE | R1 fresh-session self-drift. |
| WDPC-50 | ADEQUATE | R1 asserts SAME_WORKFLOW for forbidden action. |
| WDPC-51 | ADEQUATE | Manual material drift without disclosure. |
| WDPC-52 | ADEQUATE | Automatic material drift disclosure timing. |
| WDPC-53 | ADEQUATE | R2/R3 receive R1 narrative. |
| WDPC-54 | ADEQUATE | R1 self-authorized downgrade. |
| WDPC-55 | ADEQUATE | R1 memory conflicts with durable state. |
| WDPC-56 | ADEQUATE | R1 unavailable. |
| WDPC-57 | ADEQUATE | Positive: legitimate next parent action. |
| WDPC-58 | ADEQUATE | User falsely claims gate complete. |
| WDPC-59 | ADEQUATE | Oracle leak in prompt/context. |
| WDPC-60 | ADEQUATE | R1 later corrects prior self-drift. |
| WDPC-61 | ADEQUATE | Authorized downgrade positive. |
| WDPC-62 | ADEQUATE | Legitimate information-only child. |
| WDPC-63 | ADEQUATE | Legitimate nonblocking child. |
| WDPC-64 | ADEQUATE | Valid unaffected resume. |
| WDPC-65 | ADEQUATE | WCE stale/replayed/superseded. |
| WDPC-66 | ADEQUATE | Disclosure wrong recipient. |
| WDPC-67 | ADEQUATE | Acknowledgement but no approval. |
| WDPC-68 | ADEQUATE | Minimum reviewer metadata positive. |
| WDPC-69 | NEEDS_NARROWING | Closed rebind taxonomy; V8-C10. |
| WDPC-70 | ADEQUATE | Cancellation vs supersession race. |
| WDPC-71 | ADEQUATE | Siblings one impacts one unaffected. |
| WDPC-72 | ADEQUATE | Exceptional admin import absent. |
| WDPC-73 | ADEQUATE | Oracle leak via fixture name. |
| WDPC-74 | ADEQUATE | Workflow drift + claim contamination. |
| WDPC-75 | ADEQUATE | Process-only staleness boundary. |
| WDPC-76 | ADEQUATE | WCE key rotation/revocation replay. |
| WDPC-77 | ADEQUATE | PRR self-granted policy entry. |
| WDPC-78 | ADEQUATE | RCB timing/metadata side channel. |
| WDPC-79 | ADEQUATE | Async disclosure failure/timeout. |
| WDPC-80 | ADEQUATE | WSA/GEL crash between transition and event. |
| WDPC-81 | ADEQUATE | Fencing monotonicity across restart. |
| WDPC-82 | ADEQUATE | Policy migration + in-flight child + late result. |
| WDPC-83 | ADEQUATE | Independent confirmer collusion. |
| WDPC-84 | ADEQUATE | Endpoint label without owner-signed record. |
| WDPC-85 | ADEQUATE | Manual review falsely counted as runtime. |
| WDPC-86 | ADEQUATE | Cross-standard workflow recovery tries claim validation. |
| WDPC-87 | ADEQUATE | Normal no-drift positive. |
| WDPC-88 | ADEQUATE | PARENT_UNAFFECTED with hidden dependency. |
| WDPC-89 | ADEQUATE | Approval replay after policy rebind. |
| WDPC-90 | ADEQUATE | Manual disclosure delivered after approval. |
| WDPC-91 | ADEQUATE | Child cancellation vs sibling completion race. |
| WDPC-92 | ADEQUATE | External request dedup after restart. |
| WDPC-93 | ADEQUATE | R1 fallback expiry/revocation bypass. |
| WDPC-94 | ADEQUATE | GEL privileged rewrite attempt. |
| WDPC-95 | ADEQUATE | PRR role revocation during in-flight transition. |
| WDPC-96 | NEEDS_NARROWING | Genesis root bootstrap self-grant; V8-C03. |
| WDPC-97 | NEEDS_NARROWING | Single infra principal attacks WSA+DGV+PRR. |
| WDPC-98 | NEEDS_NARROWING | Crash between DGV ALLOW and WSA commit; final revalidation. |
| WDPC-99 | NEEDS_NARROWING | Old schema authority replay after sunset. |
| WDPC-100 | NEEDS_NARROWING | Clock skew / trusted-time conflict. |
| WDPC-101 | NEEDS_NARROWING | Predicate-owner self-grant. |
| WDPC-102 | NEEDS_NARROWING | Mandatory dependency edge omitted. |
| WDPC-103 | NEEDS_NARROWING | Quorum alias/common-control bypass. |
| WDPC-104 | NEEDS_NARROWING | Provider success then local crash. |
| WDPC-105 | NEEDS_NARROWING | WSA split-brain token issuance. |
| WDPC-106 | NEEDS_NARROWING | Forged reviewer provenance attestation. |
| WDPC-107 | NEEDS_NARROWING | Automatic material drift disclosure escrow timeout. |
| WDPC-108 | NEEDS_NARROWING | Approval assurance downgrade before commit. |
| WDPC-109 | NEEDS_NARROWING | WAS unanchored rewrite / coverage gap. |
| WDPC-110 | NEEDS_NARROWING | Cross-standard single-authority forgery. |
| WDPC-111 | NEEDS_NARROWING | Test oracle mutation after actor execution. |
| WDPC-112 | NEEDS_NARROWING | Broad legitimate recovery positive. |
| WDPC-113 | NEEDS_NARROWING | Root-governed valid key/policy rotation positive. |
| WDPC-114 | NEEDS_NARROWING | Root guardian alias/common-cloud-root collusion. |
| WDPC-115 | NEEDS_NARROWING | Provenance authority compromise. |
| WDPC-116 | NEEDS_NARROWING | Downstream effector ignores stale fencing token. |
| WDPC-117 | NEEDS_NARROWING | Schema-registry migration replay/downgrade. |
| WDPC-118 | NEEDS_NARROWING | Trusted-time source compromise/disagreement. |
| WDPC-119 | NEEDS_NARROWING | Independent falsification of permissive predicate logic. |
| WDPC-120 | NEEDS_NARROWING | Mandatory dependency-class omission at bootstrap. |
| WDPC-121 | NEEDS_NARROWING | Quorum credential-admin impersonation. |
| WDPC-122 | NEEDS_NARROWING | Provider falsely claims idempotency. |
| WDPC-123 | NEEDS_NARROWING | Dispatch before durable EffectReservation. |
| WDPC-124 | NEEDS_NARROWING | Split-brain Effect Gateway duplicate dispatch. |
| WDPC-125 | NEEDS_NARROWING | Reviewer artifact-content leakage. |
| WDPC-126 | NEEDS_NARROWING | Emergency exception becomes general bypass. |
| WDPC-127 | NEEDS_NARROWING | EndpointSchemaRegistry mutation. |
| WDPC-128 | NEEDS_NARROWING | Evidence-class metadata forgery. |
| WDPC-129 | NEEDS_NARROWING | Authoritative transition outside GEL commitment. |
| WDPC-130 | NEEDS_NARROWING | Privileged actor races event before WAS anchor. |
| WDPC-131 | NEEDS_NARROWING | Witness rollback/overlap/duplicate sequence. |
| WDPC-132 | NEEDS_NARROWING | One admin domain controls both cross-standard authorities. |
| WDPC-133 | NEEDS_NARROWING | Test-governor bootstrap/authority compromise. |
| WDPC-134 | NEEDS_NARROWING | Oracle mutation after actor start. |
| WDPC-135 | NEEDS_NARROWING | Minimum unique-enforcement-path coverage gate. |
| WDPC-136 | NEEDS_NARROWING | Mechanical composite precedence omission. |
| WDPC-137 | NEEDS_NARROWING | Genesis attestation-source common-control collusion. |
| WDPC-138 | NEEDS_NARROWING | Unregistered consequential effector defaults to deny. |
| WDPC-139 | NEEDS_NARROWING | Overly broad but validly signed emergency policy. |
| WDPC-140 | NEEDS_NARROWING | Predicate-audit authority overlaps root-guardian control. |
| WDPC-141 | NEEDS_NARROWING | OUTCOME_UNKNOWN operator assertion without independent fact evidence. |
| WDPC-142 | NEEDS_NARROWING | Compound concurrent legitimate-operation positive control. |
| WDPC-143 | NEEDS_NARROWING | EXP-K claim retraction races workflow drift disclosure. |
| WDPC-144 | NEEDS_NARROWING | Grandfather decision self-grant or missing threshold. |
| WDPC-145 | NEEDS_NARROWING | Unauthorized terminal-authority claim gets positive rejection endpoint. |
| WDPC-146 | NEEDS_NARROWING | Policy rebind omits one live object class. |
| WDPC-147 | NEEDS_NARROWING | Evidence profile mapping omission. |
| WDPC-148 | NEEDS_NARROWING | Platform/cloud super-admin cannot invoke root threshold. |
| WDPC-149 | NEEDS_NARROWING | Valid composite precedence audit positive control. |
| WDPC-150 | NEEDS_NARROWING | Narrow valid emergency policy positive control. |
| WDPC-151 | NEEDS_NARROWING | Valid independent effect observation and reconciliation positive control. |
| WDPC-152 | NEEDS_NARROWING | Newly registered effector positive control. |

P. Missing falsification cases

1. Consequence-class mislabeling: a consequential operation classified as `READ_ONLY` or `REVERSIBLE_INTERNAL` to bypass escrow or registry.
2. Non-gateway external call path: business logic directly calls provider without Effect Gateway.
3. Emergency invocation-count ceiling enforcement failure.
4. CompositePrecedenceAudit extraction failure for implicit endpoint references.
5. Root registry rewrite of prior root evidence meaning.
6. Provider observation source compromised while returning `NOT_OCCURRED`.
7. Grandfatherable property self-grant by policy owner.
8. Live-object inventory omission at rebind after object class introduction.
9. Cross-standard ordering causal evidence forgery.
10. Evidence profile map omission for a new WDPC case.
11. Post-run registry change retroactively legalizing failing run.
12. Compound positive control special-casing while common workloads overblock.
13. Root guardian indirect control of predicate auditors via recovery-admin domain.
14. Downstream effector mediation layer compromise.
15. Test-governor signing authority bootstrap compromise.

Q. Freeze recommendation
`DO_NOT_FREEZE`

R. Authority limitation
`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`