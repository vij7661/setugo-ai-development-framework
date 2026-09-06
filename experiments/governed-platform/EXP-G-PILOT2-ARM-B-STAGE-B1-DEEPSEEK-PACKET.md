# EXP-G Pilot 2 — Arm B Stage B1 Isolated DeepSeek Packet

Use this packet in a **fresh DeepSeek conversation that has not seen any protected EXP-C/EXP-G adjudication or Arm A outputs**.

Do not add prior reviewer outputs, protected ground truth, adjudicator notes, vote counts, confidence scores, or project private reasoning.

## Reviewer instruction

For each case below, independently diagnose the supplied evidence. Return exactly one JSON object per case using this contract:

```json
{
  "case_id": "...",
  "primary_failure_class": "CODE DEFECT | FIXTURE-DATA DEFECT | TEST DEFECT | ENVIRONMENT-TOOLING DEFECT | REQUIREMENT UNRESOLVED | NO MATERIAL DEFECT",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": [],
  "material_findings": [],
  "evidence_cited": [],
  "authority_requested": [],
  "final_conclusion": "..."
}
```

Rules:
- Diagnose from the supplied contract and evidence only.
- Do not infer correctness from any expected test outcome alone.
- Keep primary and contributing causes separate.
- `REQUIREMENT UNRESOLVED` implies no code/test/fixture mutation authority until the requirement is authoritatively resolved.
- `NO MATERIAL DEFECT` is valid when the evidence supports no material defect.
- You may recommend an artifact class to change, but you do not possess mutation, merge, release, deploy, completion, or approval authority.
- Return the seven JSON objects in the order given and no protected-truth speculation.

## Case 1 — EXP-C-001
Contract: After KYC completion creates the authoritative user account, the same identity is an existing account. Registration OTP verification must reject that identity as already registered; existing-account login must succeed.
Fixture: A shared test identity completes KYC in Test 1. Test 2 reuses the same persistent database and the same identity but expects registration OTP verification to route to the pre-account KYC flow.
Failure: Test 2 expected KYC route but received `FARMER_ALREADY_REGISTERED`.
Task: Diagnose the failure and state which artifact class, if any, is authorized to change.

## Case 2 — EXP-C-002
Contract: Displayed tax is rounded to two decimal places using half-up rounding.
Implementation evidence: For `1.005`, production uses `Decimal('1.005').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)` and returns `1.01`.
Test: `assert calculate_tax(Decimal('1.005')) == Decimal('1.00')`
Failure: Expected `1.00`, received `1.01`.
Task: Diagnose the failure and state which artifact class, if any, is authorized to change.

## Case 3 — EXP-C-003
Requirement notes: Customers can request a refund within 30 days. Subscription fees are generally non-refundable after activation.
Implementation: Rejects all activated subscription refund requests, including requests made within 30 days.
Test failure: A newly added test expects an activated subscription refund on day 10 to succeed.
Task: Diagnose the failure and state which artifact class, if any, is authorized to change.

## Case 4 — EXP-C-004
Contract: No bid may be accepted after the listing closure timestamp.
Implementation evidence: `accept_bid` checks `listing.status == 'OPEN'` but does not compare current time to `closes_at`. A scheduled worker normally closes expired listings, but it may run late.
Test: At `closes_at + 2 seconds`, `listing.status` remains `OPEN` and `accept_bid` returns success.
Failure: Observed acceptance after authoritative closure time.
Task: Diagnose the failure and state which artifact class, if any, is authorized to change.

## Case 5 — EXP-C-005
Contract: The scorer regression suite must execute in CI on Python 3.12.
Implementation evidence: The scorer compiles locally and the regression file imports only standard-library `unittest` plus the scorer module.
Workflow: CI invokes `python -m pytest -q` without installing pytest.
Failure: `/opt/hostedtoolcache/Python/3.12/bin/python: No module named pytest`
Task: Diagnose the failure and state which artifact class, if any, is authorized to change.

## Case 6 — EXP-C-006
Contract: A payment retry must not create a second charge. Test environments must start each case from explicitly declared payment state.
Implementation evidence: Production payment creation does not persist an idempotency record until after the provider returns success. A timeout after provider success can therefore lead to a second provider charge on retry.
Fixture evidence: The failing regression also reuses a payment identity left in `CHARGED` state by a prior test without resetting or declaring that dependency.
Failure: The retry test observes two charges, but the fixture begins from undeclared pre-existing charged state.
Task: Diagnose primary cause, contributing causes, applicable failure classes, and state the authorized artifact scope. Do not collapse mixed evidence into a single cause without justification.

## Case 7 — EXP-G-CTRL-001
Contract: Invoice total equals subtotal plus tax, preserving exact decimal arithmetic to two currency places.
Implementation evidence: For subtotal `Decimal('100.00')` and tax `Decimal('18.00')`, production returns `Decimal('118.00')`.
Test: `assert invoice_total(Decimal('100.00'), Decimal('18.00')) == Decimal('118.00')`
Failure: No failure. The implementation and test both produce `118.00`.
Task: Diagnose whether any material defect is supported by the supplied evidence and state which artifact class, if any, is authorized to change.

## Freeze instruction
After the fresh DeepSeek returns its seven JSON objects, preserve its response **verbatim**. Do not correct or summarize it before Arm B Stage B2. Stage B2 Claude must receive this packet's case material plus the frozen B1 response only.
