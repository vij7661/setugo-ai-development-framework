# R3 Review — WDPC V9 Composite Candidate

**Evidence declaration:** `AI_GENERATED_ENGINEERING_FEEDBACK_ONLY`
**Packet:** `WDPC-V9-R3-58BB28F4B7D7A65A` · **Candidate:** `c605b4540fcfaa053072fcb8fee6c281c8b44121`
**Access used:** packet contents only. No GitHub/repo, no prior-chat, no internal API, no R1/R2/prior-reviewer findings, no runtime instrumentation.

This is a delta review. V5–V7 in this packet are byte-identical to the V7 packet reviewed previously; that review's findings are treated as the baseline and only updated where V8/V9 change them. Full re-derivation of WDPC-01…135 is not repeated here.

---

## Provenance flag — read this first

The integrity manifest marks `byte_roundtrip_match: false` for the **V9 hardening overlay only**, with an in-packet explanation attributing the mismatch to "GitHub connector" text normalization.

This cannot be independently verified in this review: no GitHub connector was available to check the claim, which means the explanation is a **self-declared provenance claim about the one artifact whose provenance is in question** — the exact pattern WDPC-106/115 and the EXP-K standard exist to falsify. This is not evidence that the V9 hardening text has been altered; it *is* evidence that its authenticity relative to the claimed source commit cannot be confirmed from this packet alone.

**Recommendation:** verify the V9 hardening overlay against the actual repository blob (`5a2c6a362c748bafef2a6a09e7af78c58831eab3`) through an independently attested path before treating any finding below about that document as authoritative. This is logged as **Critical-0** and is sufficient by itself to block freeze regardless of the rest of this review.

## A. Overall disposition

`CHANGES_REQUIRED`

## B. Findings

### Critical-0 — Unverified provenance of V9 hardening overlay
See above. Independent of content quality, a design artifact whose byte-identity to its claimed source cannot be confirmed is not reviewable as "the candidate" in the sense the packet's own evidence rules require (EP-BASE requires "candidate commit and composite artifact-manifest digest" as authoritative proof — a digest of unverifiable provenance does not satisfy that bar).

### High-1 — NormativeClauseRegistry completeness is corpus-relative, not proven
**Mechanism:** MECH-PRECEDENCE (V9-C02).
Three-source reconciliation (syntactic keywords, author-declared IDs, semantic/reference extraction) plus an adversarial extraction corpus is a strong design, but it bounds *known* evasion patterns — it cannot prove completeness against a genuinely novel phrasing that uses no keyword, declares no ID, and references no known object/endpoint/state name. V8's genesis-trust boundary is explicitly named as an irreducible, bounded assumption (V8-C03); NCR completeness receives no equivalent honest labeling — it's presented as a completeness *proof* rather than a completeness *bound relative to the adversarial corpus*.
**Fix:** State NCR completeness as bounded by adversarial-corpus coverage, require corpus versioning/expansion review as a standing obligation, and require the freeze gate to disclose corpus coverage explicitly rather than implying total completeness.

### High-2 — CompositeAuditAuthority independence from candidate authors is unspecified
**Mechanism:** MECH-PRECEDENCE.
Every other authority in this design (predicate auditors, root guardians, genesis notaries, observation sources) has an explicit independence-from-beneficiary requirement. CompositeAuditAuthority — which decides whether the *audit itself* passes — has no stated requirement to be independent from whoever authored the V8/V9 clauses it's auditing. Mandatory question 6 ("can CAA or NCR governance self-grant a PASS?") is not answered by anything in the text.
**Fix:** Extend PrincipalIndependenceRegistry-style checks to CAA relative to candidate-authoring principals.

### Medium-1 — No aggregate ceiling across multiple valid emergency policies
**Mechanism:** MECH-EMERGENCY (V9-C08).
Invocation budgets are tracked and enforced per-policy (`remaining invocation budget` is scoped to "policy ID/version"). Nothing bounds what several distinct, individually narrow, individually valid emergency policies could achieve in combination if invoked together — this is the multi-policy analogue of mandatory question 37, and it isn't closed.
**Fix:** An aggregate emergency-scope ledger across concurrently active policies, with a root-governed combined ceiling.

### Low-1 — Genesis qualification expiry isn't tied to a recheck-at-freeze rule
V9-C03's `GenesisQualificationRecord` has an "acceptance scope and expiry/review date," but nothing explicitly requires every *later* freeze attempt to recheck that the record hasn't expired — only that it exists at genesis.

### Low-2 — Effector attestation lacks an explicit re-attestation trigger on implementation change
V9-C13 binds `EffectorEnforcementAttestation` to a "token-validation/gateway implementation digest," implying a changed digest invalidates the attestation, but no endpoint/rule explicitly requires re-attestation when that digest changes post-activation.

## C. What V8 closed from the prior review (confirmed)

| Prior finding | V8/V9 closure |
|---|---|
| C-1: `COMPOSITE_PRECEDENCE_AMBIGUOUS` not mechanically detectable | V8-C02 `CompositeAuditAuthority` + mechanical fail-closed audit; strengthened by V9-C02 triple-source NCR |
| C-2: Root-of-trust genesis circularity unacknowledged | V8-C03 explicit bounded `GenesisTrustAssumption` + offline notarization; V9-C03 makes acceptance an explicit gated record |
| C-3: No default for unregistered effector | V8-C04 `ConsequentialEffectorRegistry`, default DENY; V9-C05/C13 add mandatory egress mediation + enforcement attestation |
| H-1: Emergency policy content risk | V8-C05 `EmergencyPolicyConstraintRegistry`; V9-C08 executable trigger allowlist + atomic invocation ledger |
| H-2: Predicate-audit authority vs. root guardians | V8-C06; V9-C07 extends to every threshold-capable subset |
| H-3: OUTCOME_UNKNOWN fact/authority conflation | V8-C07 splits observation from reconciliation; V9-C06 adds independence + freshness rules |
| M-1: No compound positive control | V8-C14, WDPC-142; V9-C14 requires compound-or-justified-N/A per mechanism, WDPC-169 |
| M-2: EXP-K/workflow timing race | V8-C11 `CrossDomainOrderingService`; V9-C12 requires registered causal evidence, fail-closed to `CONCURRENT_REEVALUATION_REQUIRED` |
| WDPC-06 grandfather authority undefined | V8-C08 `GrandfatherDecision`; V9-C10 makes grandfatherability itself a governed, default-false property |
| WDPC-11 no positive rejection endpoint | V8-C09 `TERMINAL_AUTHORITY_CLAIM_REJECTED` |
| WDPC-69 rebind taxonomy incomplete | V8-C10 closed enum; V9-C11 mechanical `LiveAuthorityObjectInventory` |
| L-2: "where applicable" ambiguity | V8-C13 Evidence Profile Map; V9-C09 `CaseRegistry` set-equality enforcement |

No regressions found — none of the V8/V9 clauses reviewed reintroduce a permissive V5–V7 interpretation.

## D. WDPC-136…171 audit

*(Verdicts as in the prior review: ADEQUATE = preregistered, falsifiable, actor/owner-bound, post-hoc verifiable as written.)*

WDPC-136 ADEQUATE · 137 ADEQUATE · 138 ADEQUATE · 139 ADEQUATE · 140 ADEQUATE · 141 ADEQUATE · 142 ADEQUATE (compound positive) · 143 ADEQUATE · 144 ADEQUATE · 145 ADEQUATE · 146 ADEQUATE · 147 ADEQUATE · 148 ADEQUATE · 149 ADEQUATE (positive) · 150 ADEQUATE (positive) · 151 ADEQUATE (positive) · 152 ADEQUATE (positive)
WDPC-153 ADEQUATE · 154 ADEQUATE · 155 ADEQUATE · 156 ADEQUATE · 157 ADEQUATE · 158 ADEQUATE · 159 ADEQUATE · 160 ADEQUATE · 161 ADEQUATE · 162 ADEQUATE · 163 ADEQUATE · 164 ADEQUATE · 165 ADEQUATE · 166 ADEQUATE · 167 ADEQUATE · 168 ADEQUATE
WDPC-169 ADEQUATE (compound positive) — see Medium-1: doesn't exercise multiple *distinct* emergency policies combined, only the mechanism list generally
WDPC-170 ADEQUATE · 171 ADEQUATE (positive)

No case in this range was found unfalsifiable or duplicative-only; V8/V9's design discipline (explicit mechanism IDs, explicit evidence profiles per case) is a real improvement in auditability over the earlier V5–V7 matrices.

## E. Missing falsification cases

1. Multi-policy aggregate emergency-scope ceiling (Medium-1).
2. CompositeAuditAuthority independence from candidate-authoring principals (High-2).
3. Adversarial-corpus-boundary disclosure test: confirm the freeze report states NCR completeness as corpus-relative rather than absolute (High-1).
4. Re-attestation-on-digest-change for registered effectors (Low-2).
5. Freeze-time genesis-qualification expiry recheck (Low-1).

## F. Freeze recommendation

`DO_NOT_FREEZE`

Primarily on Critical-0 (unverified provenance of the V9 hardening overlay) — the freeze gate cannot be meaningfully evaluated against a document whose byte-identity to its claimed source is itself unconfirmed. High-1 and High-2 are independently sufficient to block freeze under the V9 freeze rule (V9-C18) even if provenance is resolved.

## G. Authority limitation

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
