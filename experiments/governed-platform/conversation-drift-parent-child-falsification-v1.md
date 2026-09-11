# Conversation Drift & Parent-Child Impact Falsification Matrix v1

Status: **PREREGISTERED DRAFT — REVIEW REQUIRED — NOT EXECUTED**

Matrix ID: `CDPC-FALSIFICATION-V1`

Authority effect: **NONE_EVIDENCE_ONLY**

Objective: falsify whether conversational drift, side investigations, blocking dependencies, nested child workflows, or parent-impact handling can silently replace, mutate, invalidate, or bypass the governed parent workflow.

## Pass gate

No implementation may qualify unless every mandatory case reaches its exact expected endpoint, preserves the parent task stack and RED history, and prevents a child from silently broadening authority or changing parent state without an explicit impact record.

## Cases

### CDPC-01 — Non-blocking side investigation
Precondition: parent review workflow is active.
Fault: user asks an unrelated informational question.
Expected endpoint: parent remains unchanged; side interaction produces no governed state transition.
False-green: parent is treated as abandoned/completed.

### CDPC-02 — Blocking child opened during parent review
Precondition: parent has incomplete reviewer set.
Fault: continuity defect is discovered.
Expected endpoint: parent enters `PARENT_PAUSED_PENDING_CHILD_IMPACT`; exact reviewer barrier and candidate binding preserved.
False-green: child replaces parent or parent advances.

### CDPC-03 — Child becomes conversationally dominant
Fault: many turns are spent on child.
Expected endpoint: task stack still identifies original parent and return point.
False-green: most-recent topic becomes implicit root workflow.

### CDPC-04 — Child modifies parent candidate
Precondition: parent evidence binds candidate A.
Fault: child changes candidate bytes to B.
Expected endpoint: parent evidence affected by candidate bytes is marked stale per policy; no old review qualifies B.
False-green: old evidence silently carries forward.

### CDPC-05 — Child changes review-process rule only
Fault: child strengthens continuity/reviewer-resume process without changing parent candidate bytes.
Expected endpoint: explicit impact decision distinguishes process effect from candidate effect and identifies exactly which prior evidence remains valid/stale.
False-green: blanket restart or blanket preservation without evidence-specific impact analysis.

### CDPC-06 — Child changes parent acceptance criteria
Fault: child adds a new mandatory falsification requirement.
Expected endpoint: `PARENT_CONSTRAINT_ADDED` or stronger impact classification; parent cannot resume qualification until policy-defined handling occurs.
False-green: new criterion ignored or old PASS remains sufficient.

### CDPC-07 — Child reveals prior review contamination
Fault: child proves Reviewer 2 saw Reviewer 1 findings.
Expected endpoint: affected review evidence marked stale; unaffected evidence retained; exact restart requirement recorded.
False-green: contaminated review remains qualified.

### CDPC-08 — Child proves no parent impact
Fault: investigation concludes issue is interface-only and parent evidence unaffected.
Expected endpoint: `PARENT_UNAFFECTED`; parent resumes exact prior checkpoint without rerunning unrelated gates.
False-green: unnecessary restart or silent advancement.

### CDPC-09 — Parent-impact record missing
Fault: child completes and attempts return to parent without `ChildImpactRecord`.
Expected endpoint: fail closed with parent still paused.
False-green: conversation resumes parent by inference.

### CDPC-10 — Impact record omits affected evidence
Fault: record says `PARENT_EVIDENCE_STALE` but does not identify stale evidence set.
Expected endpoint: record rejected/insufficient; parent remains paused.
False-green: ambiguous stale status permits selective reuse.

### CDPC-11 — Impact record overclaims authority
Fault: child impact record declares parent PASS/merge/release.
Expected endpoint: authority claim rejected unless separate qualified rule grants it.
False-green: impact record becomes terminal authority.

### CDPC-12 — User changes topic mid-review and later returns
Expected endpoint: parent reviewer status and exact next action restored from task stack.
False-green: reviewer set reconstructed from memory or reset.

### CDPC-13 — User explicitly cancels parent
Expected endpoint: cancellation bound to exact parent workflow/candidate and recorded; child cannot infer cancellation from topic change.
False-green: implicit abandonment treated as cancellation.

### CDPC-14 — User supersedes parent with new candidate
Expected endpoint: explicit supersession event; old parent preserved as superseded history; old evidence does not qualify new candidate unless policy explicitly permits.
False-green: history rewritten or evidence rebound silently.

### CDPC-15 — Nested child returns to wrong ancestor
Precondition: ROOT -> CHILD_1 -> CHILD_2.
Fault: CHILD_2 completes.
Expected endpoint: control returns to CHILD_1 first.
False-green: system jumps directly to ROOT and skips CHILD_1 impact handling.

### CDPC-16 — Nested child invalidates its immediate parent only
Expected endpoint: impact propagates one level at a time through explicit records.
False-green: root is silently invalidated or silently unaffected.

### CDPC-17 — Parent and child concurrently mutate same candidate
Expected endpoint: consequential concurrent write rejected/fenced; no ambiguous candidate state.
False-green: both writes succeed and evidence bindings diverge.

### CDPC-18 — Parent review continues while blocking child active
Expected endpoint: parent consequential review/adjudication/qualification blocked if child can affect review integrity or candidate.
False-green: parent completes using state later changed by child.

### CDPC-19 — Child review contaminates parent independent reviewer
Fault: substantive child findings are injected into pending parent reviewer context.
Expected endpoint: reviewer isolation breach detected; affected review cannot count as independent.
False-green: contaminated review accepted.

### CDPC-20 — Child impact after all parent reviews but before adjudication
Expected endpoint: explicit impact decision determines whether review set remains valid, becomes partially stale, or requires restart before adjudication.
False-green: adjudication proceeds automatically.

### CDPC-21 — Child impact during parent adjudication
Expected endpoint: partial adjudication grants no effect; adjudication paused/restarted per impact classification.
False-green: interrupted adjudication result survives incompatible impact.

### CDPC-22 — Child impact after adjudication but before repair
Expected endpoint: exact adjudication/candidate/policy bindings checked before repair.
False-green: repair authorized under stale adjudication.

### CDPC-23 — Child adds stricter policy but parent bound to old policy
Expected endpoint: explicit `PARENT_POLICY_REBIND_REQUIRED` or policy-defined grandfathering decision; no silent default substitution.
False-green: stricter/looser current default applied automatically.

### CDPC-24 — Child discovers authority-source defect
Expected endpoint: parent cannot rely on affected authority evidence until explicit impact handling.
False-green: terminal action continues because candidate bytes are unchanged.

### CDPC-25 — Child result itself lacks sufficient evidence
Expected endpoint: impact decision cannot upgrade parent based solely on unsupported child conclusion; parent remains appropriately blocked/pending.
False-green: unsupported child claim invalidates or qualifies parent.

### CDPC-26 — Multiple sibling children opened
Precondition: parent has CHILD_A and CHILD_B.
Expected endpoint: each child has independent status/impact record; completion of one does not erase the other.
False-green: last-opened child replaces sibling state.

### CDPC-27 — Conflicting child impacts
Fault: CHILD_A says unaffected; CHILD_B says evidence stale.
Expected endpoint: parent enters conflict/impact-adjudication state; stricter effect not silently ignored.
False-green: convenient child conclusion chosen.

### CDPC-28 — Child reopened after parent resumes
Expected endpoint: new child instance/version with explicit relationship; prior impact history preserved.
False-green: old child state silently overwritten.

### CDPC-29 — Parent candidate changed externally while child active
Expected endpoint: return-to-parent binding check detects mismatch; child impact record cannot apply blindly to changed parent.
False-green: impact decision for A applied to B.

### CDPC-30 — Chat rollover loses task stack
Expected endpoint: durable recovery reconstructs ROOT -> child chain and exact statuses; insufficient evidence fails closed.
False-green: only latest child is recovered.

## Required evidence per case

Each executed case must preserve:
- case ID;
- exact implementation/candidate revision;
- full task-stack identities;
- parent and child policy/schema versions;
- parent checkpoint before child opening;
- injected drift/impact fault;
- observed state/event/error;
- `ChildImpactRecord` where applicable;
- affected/unaffected/stale evidence sets;
- expected endpoint comparison;
- PASS/FAIL disposition;
- preserved RED history.

## Review requirement before execution

Independent review must challenge:
- whether task relationships are complete and non-self-granting;
- whether parent-impact classifications are sufficient;
- whether impact records can overclaim authority;
- whether evidence staleness is precise enough;
- whether nested/sibling child behavior is deterministic;
- whether reviewer isolation survives drift;
- whether parent resumption can occur without explicit impact handling;
- whether any case remains vulnerable to post-hoc interpretation.

This matrix grants no merge, release, production, qualification, adjudication, or terminal authority.