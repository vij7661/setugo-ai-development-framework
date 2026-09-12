# R3 Claude Engineering Review — WDPC V7 Composite Candidate

**Packet reviewed:** `WDPC-V7-R3-CLAUDE-5AB8198078888F12`
**Candidate commit:** `5b436e4bca26b041b9bfdf3526594c0234e9dc03`
**Reviewer role:** R3_CLAUDE_ENGINEERING_REVIEW
**Evidence type produced:** AI_GENERATED_ENGINEERING_FEEDBACK_ONLY
**Access used:** packet contents only — no repo, no prior chat, no internal API, no prior-reviewer findings, no runtime instrumentation.

This review treats the packet strictly as design/preregistered falsification material. No runtime implementation is assumed to exist, and no runtime PASS is inferred from design text anywhere below.

---

## A. Overall disposition

`CHANGES_REQUIRED`

The composite candidate is unusually rigorous for a design document — nearly every mechanism carries a signed-object contract, a fail-closed default, and a paired negative/positive falsification case. But three Critical and three High gaps remain, several of them in the packet's own self-referential machinery (how *ambiguity itself* gets detected, how the *root of trust* bootstraps, how a *newly introduced effector* defaults). Per the V7 freeze condition (§20), unresolved Critical/High findings block freeze regardless of how complete the rest of the matrix is.

## B. Critical findings

### C-1 — `COMPOSITE_PRECEDENCE_AMBIGUOUS` is not mechanically detectable
- **Section/case:** V7 active-clause map; mandatory question 4.
- **False-green path:** A future V8 patch adds a new normative clause or endpoint code and simply forgets to add a row to the active-clause map. Nothing in the packet defines an automated procedure that walks every normative clause and every endpoint code and asserts 1:1 coverage. `COMPOSITE_PRECEDENCE_AMBIGUOUS` as written is a conclusion a human reviewer reaches by reading tables, not a signed, owner-produced event.
- **Why V7 is insufficient:** The packet's own bar — "a prose label, reviewer statement, or unsigned status cannot satisfy an endpoint" (V7-ext §2) — is violated by its own precedence-ambiguity mechanism. Question 4 ("can `COMPOSITE_PRECEDENCE_AMBIGUOUS` itself be enforced/tested?") is answerable **No** on the evidence given.
- **Narrow required fix:** Define a signed `CompositePrecedenceAudit` object, produced by a root-governed authority, enumerating every normative clause ID and endpoint code with a coverage bit; missing coverage is a rejected event, not a reviewer's prose finding.
- **Falsification test:** Introduce a new endpoint code in a hypothetical patch without updating the active-clause map; verify the *platform*, not a human, halts freeze.

### C-2 — Root-of-trust genesis circularity is unaddressed
- **Section/case:** V7 §2 (`RootGuardianIndependenceSnapshot`); WDPC-96, WDPC-114.
- **False-green path:** Before any `RootGovernanceManifest` exists, no root-governed registry exists to certify who counts as an "independent attestation source" for the very first guardian-independence snapshot. WDPC-96 tests a bootstrap *self-grant* attempt; WDPC-114 tests guardian *alias/common-cloud* collusion after guardians are nominally distinct. Neither tests whether the attestation sources used at genesis are themselves guardian-controlled.
- **Why V7 is insufficient:** All root-of-trust designs face a bootstrap problem, but this packet doesn't name it as an accepted, bounded assumption — it implicitly treats genesis independence as solved by definition, which is exactly the kind of unstated assumption the "mandatory review questions" ask R3 to hunt for (Q5–Q7).
- **Narrow required fix:** Either (a) explicitly document genesis independence as an out-of-band, non-falsifiable trust assumption with a named accountable party, or (b) require a third-party/offline notarization step for the first `RootGuardianIndependenceSnapshot` that doesn't depend on any registry the guardians themselves will later control.
- **Falsification test:** At genesis, have a single administrator control the attestation-source infrastructure for three of five nominal guardians; verify the manifest is rejected — currently untested.

### C-3 — No default for an unregistered/new consequential effector
- **Section/case:** V7 §6 (end-to-end fencing); WDPC-116.
- **False-green path:** A new downstream effector is added to the system but is never given a `fencing_enforcement_mode` entry in PRR. WDPC-116 only tests a *known* effector that ignores a *stale* token — it doesn't test an effector with *no* registration at all, which is the more common real-world failure (a team ships a new integration and forgets the governance step).
- **Why V7 is insufficient:** V7 §6 says every effector "MUST either validate the token itself or be mediated" but never states what happens when neither is true because the effector was never inventoried — no fail-closed default is named. This is the effector analogue of the dependency-class-omission problem the packet already solved for PGR (WDPC-120).
- **Narrow required fix:** Root-governed effector registry with a default-deny posture: any consequential effector absent from the registry is blocked at the gateway by construction, not by discipline.
- **Falsification test:** Register a new effect class with zero `fencing_enforcement_mode` entry and attempt dispatch; expect a rejection, not silent pass-through.

## C. High findings

### H-1 — Emergency-exception *content* risk is out of scope
- **Case:** WDPC-126.
- **Gap:** The case falsifies a *generic* emergency flag bypassing escrow, but not a *validly root-governed* `EmergencyExceptionPolicy` that is itself written too broadly (e.g., trigger condition = "any disclosure timeout," duration = unbounded) — which would pass every check in WDPC-126 while functioning as a de facto bypass.
- **Fix:** Require RGA-enforced minimums on trigger specificity and duration ceiling at policy-activation time, plus a falsification case for an overly broad but validly-signed policy.

### H-2 — `PredicateBootstrapAudit` independence doesn't reach the root guardians
- **Case:** V7 §8; adjacent to WDPC-119/120, WDPC-114.
- **Gap:** The audit authority must be independent of the *policy owner and beneficiary*, but nothing requires it to be independent of the *root guardians* who ultimately authorize its registry entry. Guardian collusion is tested for root rotation (WDPC-114) but not cross-checked against predicate-audit independence.
- **Fix:** Extend `PrincipalIndependenceRegistry`-style checks to the predicate-audit authority relative to root-guardian control domains.

### H-3 — `OUTCOME_UNKNOWN` reconciliation conflates fact-finding with authorization
- **Case:** V7 §5.3; WDPC-122.
- **Gap:** `ExternalEffectReconciliationDecision` names who may *authorize* proceeding (PRR quorum) but not what independently proves whether the provider-side effect actually occurred. An operator could satisfy the governance quorum while asserting an unverifiable factual claim about provider state.
- **Fix:** Separate "evidentiary reconciliation" (provider audit log / independent query) from "authorization to proceed" as two distinct signed artifacts.

## Medium findings

### M-1 — No compound positive control for simultaneous mechanism firing
Per-mechanism positive controls are mandated everywhere (V6 §18, V7 §5), but nothing requires a legitimate scenario where several fire *at once* (root rotation + policy migration + quorum-gated downgrade + external effect, concurrently) to still succeed. A system could pass every isolated positive control and still overblock under realistic concurrent load. WDPC-112 is the closest analogue but is sequential/narrative, not concurrent.

### M-2 — Untested timing race between EXP-K claim retraction and workflow drift disclosure
Derived-Claim Invalidation (EXP-K) and Material Workflow Drift disclosure are both correctly asserted as independent authorities (WDPC-74, 86, 110, 132), but no case falsifies what happens when a claim retraction cascade and a workflow disclosure event land at the same authoritative sequence — a plausible source of ordering-dependent false-green.

## Low findings

### L-1 — Section-numbering traceability
The active-clause map cross-references V5/V6 by "§N Title," but the embedded full texts use different heading conventions ("## 2. Trust domains…" vs. "§2 Trust domains and service identities"). Cosmetic, but it makes mechanical (non-human) cross-referencing between the map and the source text harder than it needs to be.

### L-2 — "Where applicable" in universal PASS-proof lists is reviewer-judged
V5 §4 / V6 §2 / V7-ext §2 all qualify long PASS-evidence checklists with "where applicable" but never enumerate, per case, which fields apply — a minor ambiguity surface that shifts a judgment call onto whoever executes the case.

## D. Composite precedence assessment

The active-clause map is comprehensive at the section level — every V5 §1–24 and V6 §1–21 row carries an explicit status, and none were found silently blank or defaulting to a more permissive reading. Section 4 of the V7 extension explicitly re-maps the specific WDPC-01…113 cases affected by stricter V7 rules, which directly answers mandatory question 3 (no unresolved older-vs-stricter contradiction found in the material reviewed). The self-declared `COMPOSITE_PRECEDENCE_AMBIGUOUS` fallback is good design intent, but per **C-1** it is not itself a falsifiable, owner-signed mechanism — it is currently a reviewer's reading of a table.

## E. Root-governance/registry assessment

Strong: 3-of-5 threshold across independent control domains, hardware-backed/offline guardian keys, an explicit root-governed registry list (11 registries named), and monotonic non-rollback versioning. Gaps: genesis circularity (**C-2**), and no explicit test for a *non-guardian* platform-level override (e.g., a cloud provider itself, not a named guardian, with infrastructure-level access to "hardware-backed or offline-held" keys) — WDPC-114 covers guardian aliasing, not infrastructure-provider override outside the guardian identity model entirely.

## F. DGV/WSA decision-consumption assessment

Adequate. The `PREPARED → APPLIED → SUPERSEDED → EXPIRED` lifecycle, `ApplyDecision` final-authority revalidation (V7 §4), and `DecisionConsumptionLedger` idempotent-replay guarantee are all concretely specified and directly falsified by WDPC-98 (crash between ALLOW and commit) and WDPC-95/108 (mid-flight authority revocation).

## G. Provider/external-effect assessment

Reservation-before-dispatch, `ProviderCapabilityRegistry` qualification, and split-brain gateway single-writer rules are well specified and falsified (WDPC-104, 122–124). **H-3** is the remaining gap: the reconciliation *decision* is governed, but the reconciliation *evidence* is not.

## H. WSA consensus/fencing/downstream-effector assessment

Fencing-token monotonicity and linearizable WSA are solid (WDPC-17/37/70/81/91/105, all explicitly re-scoped by V7 §4 of the extension to require downstream — not just WSA-level — enforcement). **C-3** (unregistered-effector default) is the open gap.

## I. WSA/GEL/WAS completeness assessment

Adequate. `AuthoritativeTransitionCommitment`, contiguous WAS anchoring with no-gap requirements, and exactly-one-range inclusion proofs are all concretely falsified (WDPC-94, 109, 129–131).

## J. PGR/dependency/ChildImpact assessment

Strong structurally — mandatory dependency-class templates, SCC/fixpoint cycle handling, and the V7-added `PredicateBootstrapAudit` close most of the "policy owner grades its own homework" failure mode (WDPC-101, 119, 120). **H-2** (audit-authority vs. root-guardian independence) is the remaining gap.

## K. Quorum/independence assessment

Adequate. `PrincipalIndependenceRegistry` spans control domain, administrative domain, credential-admin domain, alias/service-account group, and beneficial-owner relation, with a final recheck at commit (WDPC-83, 103, 121). No gap found beyond what's already noted in C-2/H-2 at the root-guardian layer.

## L. Disclosure/approval assessment

The `ConsequenceClassRegistry` (READ_ONLY → TERMINAL_AUTHORITY) plus named `EmergencyExceptionPolicy` is a real improvement over a single reversible/irreversible binary. **H-1** (policy-content breadth) is the open gap — the machinery for *enforcing* a named policy is solid; nothing bounds what a validly-signed policy is allowed to say.

## M. RCB provenance/reviewer-isolation assessment

Adequate. Three distinct leak vectors are each independently falsified: forged provenance (WDPC-106), compromised provenance authority (WDPC-115), and clean-metadata-but-dirty-payload (WDPC-125). This is a genuinely well-decomposed threat model.

## N. Endpoint/evidence-class/test-governor assessment

Adequate. `EvidenceClassRecord` prevents post-hoc reclassification (WDPC-85, 128), and oracle immutability is strict — "no override can restore the run" (WDPC-111, 134) is a real, testable, no-exceptions rule, including against root governance itself.

## O. Cross-standard EXP-K boundary assessment

Adequate on administrative separation (WDPC-110, 132: distinct principal, key, admin domain, credential-admin domain, and policy lineage). **M-2** (timing race between claim retraction and drift disclosure) is untested.

## P. Positive-control/overblocking assessment

Per-mechanism positive controls are mandated pervasively and the packet explicitly forbids counting a block-all system as passing (V5 §8, V6 §18, V7-ext §5). **M-1** is the remaining gap: no *compound* positive control exists for several mechanisms firing concurrently under legitimate load.

## Q. WDPC-01..WDPC-135 audit

*(ADEQUATE = preregistered, falsifiable, actor/owner-bound, and post-hoc verifiable as written. Only exceptions are annotated.)*

WDPC-01 ADEQUATE · 02 ADEQUATE · 03 ADEQUATE · 04 ADEQUATE · 05 ADEQUATE
WDPC-06 NEEDS_NARROWING — "grandfather rule" has no defined authorizing threshold
WDPC-07 ADEQUATE · 08 ADEQUATE · 09 ADEQUATE · 10 ADEQUATE
WDPC-11 NEEDS_NARROWING — relies on absence-of-transition rather than a positive rejection endpoint
WDPC-12 ADEQUATE · 13 ADEQUATE (positive) · 14 ADEQUATE (positive) · 15 ADEQUATE · 16 ADEQUATE · 17 ADEQUATE · 18 ADEQUATE
WDPC-19 DUPLICATIVE_BUT_USEFUL — same enforcement path as WDPC-07/53
WDPC-20 ADEQUATE · 21 ADEQUATE · 22 ADEQUATE · 23 ADEQUATE · 24 ADEQUATE · 25 ADEQUATE · 26 ADEQUATE · 27 ADEQUATE · 28 ADEQUATE · 29 ADEQUATE · 30 ADEQUATE · 31 ADEQUATE · 32 ADEQUATE · 33 ADEQUATE · 34 ADEQUATE · 35 ADEQUATE · 36 ADEQUATE · 37 ADEQUATE · 38 ADEQUATE · 39 ADEQUATE · 40 ADEQUATE · 41 ADEQUATE · 42 ADEQUATE · 43 ADEQUATE · 44 ADEQUATE · 45 ADEQUATE · 46 ADEQUATE
WDPC-47 DUPLICATIVE_BUT_USEFUL — same path as WDPC-72 (packet itself flags this pairing)
WDPC-48 ADEQUATE · 49 ADEQUATE · 50 ADEQUATE · 51 ADEQUATE · 52 ADEQUATE
WDPC-53 DUPLICATIVE_BUT_USEFUL — same path as WDPC-19/68 (packet itself flags this pairing)
WDPC-54 ADEQUATE · 55 ADEQUATE · 56 ADEQUATE · 57 ADEQUATE (positive) · 58 ADEQUATE · 59 ADEQUATE · 60 ADEQUATE · 61 ADEQUATE (positive) · 62 ADEQUATE (positive) · 63 ADEQUATE (positive) · 64 ADEQUATE (positive) · 65 ADEQUATE · 66 ADEQUATE · 67 ADEQUATE · 68 ADEQUATE (positive)
WDPC-69 POST_HOC_AMBIGUOUS — depends on a `PolicyRebindDecision` taxonomy that is never fully enumerated beyond the three values in WDPC-82
WDPC-70 ADEQUATE · 71 ADEQUATE
WDPC-72 DUPLICATIVE_BUT_USEFUL — same path as WDPC-47
WDPC-73 ADEQUATE · 74 ADEQUATE · 75 ADEQUATE · 76 ADEQUATE · 77 ADEQUATE · 78 ADEQUATE · 79 ADEQUATE · 80 ADEQUATE · 81 ADEQUATE · 82 ADEQUATE · 83 ADEQUATE · 84 ADEQUATE · 85 ADEQUATE · 86 ADEQUATE · 87 ADEQUATE (positive) · 88 ADEQUATE · 89 ADEQUATE · 90 ADEQUATE · 91 ADEQUATE · 92 ADEQUATE · 93 ADEQUATE · 94 ADEQUATE · 95 ADEQUATE
WDPC-96 ADEQUATE · 97 ADEQUATE · 98 ADEQUATE (positive mandated) · 99 ADEQUATE · 100 ADEQUATE · 101 ADEQUATE · 102 ADEQUATE · 103 ADEQUATE · 104 ADEQUATE (positive mandated) · 105 ADEQUATE (positive mandated) · 106 ADEQUATE · 107 ADEQUATE (positive mandated) · 108 ADEQUATE · 109 ADEQUATE
WDPC-110 ADEQUATE — see M-2 for an adjacent untested interaction, not a defect in this case itself
WDPC-111 ADEQUATE
WDPC-112 ADEQUATE (positive) — see M-1: covers sequential recovery, not concurrent multi-mechanism load
WDPC-113 ADEQUATE (positive) · 114 ADEQUATE · 115 ADEQUATE
WDPC-116 MISSING_ENFORCEMENT — see C-3: tests a *known* effector ignoring a token, not an *unregistered* effector's default
WDPC-117 ADEQUATE · 118 ADEQUATE · 119 ADEQUATE · 120 ADEQUATE · 121 ADEQUATE · 122 ADEQUATE · 123 ADEQUATE · 124 ADEQUATE · 125 ADEQUATE
WDPC-126 NEEDS_NARROWING — see H-1: doesn't falsify an overly broad but validly-signed emergency policy
WDPC-127 ADEQUATE · 128 ADEQUATE · 129 ADEQUATE · 130 ADEQUATE · 131 ADEQUATE · 132 ADEQUATE
WDPC-133 ADEQUATE — adjacent to H-2, but H-2 concerns the *predicate*-audit authority, not the test-governor authority this case covers
WDPC-134 ADEQUATE · 135 ADEQUATE

## R. Missing falsification cases

1. **Genesis attestation-source independence** — parallel to WDPC-96, but testing whether the *attestation sources* used for the very first `RootGuardianIndependenceSnapshot` are themselves guardian-controlled (C-2).
2. **Effector-registration completeness** — parallel to WDPC-120, but for `fencing_enforcement_mode`: verify an unregistered consequential effector defaults to DENY rather than silent pass-through (C-3).
3. **Overly-broad-but-validly-signed `EmergencyExceptionPolicy`** — a policy that is technically named and root-signed but scoped so loosely it functions as a general bypass (H-1).
4. **Predicate-audit-authority vs. root-guardian independence** — extend the WDPC-114 guardian-independence pattern to the `PredicateBootstrapAudit` authority (H-2).
5. **Compound/concurrent legitimate-load positive control** — root rotation, policy migration, quorum-gated downgrade, and an external effect all in flight simultaneously, expected to resolve correctly with no false block (M-1).
6. **EXP-K/workflow simultaneous-sequence race** — a claim-retraction cascade and a material-drift disclosure event landing at the same authoritative sequence (M-2).
7. **`OUTCOME_UNKNOWN` evidentiary-sufficiency test** — separating what independently proves the provider-side fact from who is authorized to act on it (H-3).

## S. Freeze recommendation

`DO_NOT_FREEZE`

The V7 freeze condition (§20) requires "no unresolved Critical/High design finding remains under the governing review policy" before freeze. Three Critical and three High findings are identified above; per the packet's own stated freeze gate, that alone is sufficient to withhold freeze regardless of the matrix's otherwise strong coverage. This is a design-evidence disposition only — it says nothing about whether any runtime implementation exists or would satisfy these cases.

## T. Authority limitation

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
