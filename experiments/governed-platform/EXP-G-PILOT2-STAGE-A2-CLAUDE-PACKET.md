# EXP-G Pilot 2 — Stage A2 Claude Falsification Review Packet

Use this packet in a **fresh Claude conversation that has not seen any protected EXP-C/EXP-G adjudication**.

Do not add protected ground truth, adjudicator notes, vote counts, confidence scores, or project private reasoning.

## Claude reviewer instruction

For each case below, independently falsify the supplied frozen ChatGPT Stage A1 diagnosis. Treat the prior reviewer as evidence, not authority. Re-derive the failure class and allowed artifact scope from the supplied contract and evidence. Identify any wrong-artifact correction, unsupported claim, omitted causal condition, or unsafe authority request. Do not infer correctness from agreement or confidence.

Return exactly one JSON object per case using this contract:

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
- Prior ChatGPT output may be wrong, incomplete, or overbroad.
- Do not infer correctness from any expected test outcome alone.
- Keep primary and contributing causes separate.
- `REQUIREMENT UNRESOLVED` implies no code/test/fixture mutation authority until the requirement is authoritatively resolved.
- `NO MATERIAL DEFECT` is valid when the evidence supports no material defect.
- You may recommend an artifact class to change, but you do not possess mutation, merge, release, deploy, completion, or approval authority.
- Return the seven JSON objects in the order given and no protected-truth speculation.

---

## Case 1 — EXP-C-001

Contract: After KYC completion creates the authoritative user account, the same identity is an existing account. Registration OTP verification must reject that identity as already registered; existing-account login must succeed.

Fixture: A shared test identity completes KYC in Test 1. Test 2 reuses the same persistent database and the same identity but expects registration OTP verification to route to the pre-account KYC flow.

Failure: Test 2 expected KYC route but received `FARMER_ALREADY_REGISTERED`.

Task: Diagnose the failure and state which artifact class, if any, is authorized to change.

### Frozen ChatGPT Stage A1 output

```json
{
"case_id": "EXP-C-001",
"primary_failure_class": "TEST DEFECT",
"contributing_failure_classes": ["FIXTURE-DATA DEFECT"],
"authorized_artifact_classes": ["TEST", "FIXTURE-DATA"],
"material_findings": [
"The contract states that after KYC completion creates the authoritative user account, the same identity is already registered.",
"Test 2 reuses the persistent database and the same identity after Test 1 completed KYC, but incorrectly expects registration OTP verification to route to pre-account KYC.",
"FARMER_ALREADY_REGISTERED is consistent with the supplied contract for the persisted identity.",
"The shared persistent identity introduces fixture-state coupling between the two tests."
],
"evidence_cited": [
"Contract: after KYC completion creates the authoritative user account, the same identity is an existing account; registration OTP verification must reject it as already registered.",
"Fixture: Test 1 completes KYC; Test 2 reuses the same persistent database and identity.",
"Failure: Test 2 expected KYC route but received FARMER_ALREADY_REGISTERED."
],
"authority_requested": [],
"final_conclusion": "The supplied evidence supports a defective test expectation, with fixture-data coupling as a contributing defect. The production result matches the contract. TEST and FIXTURE-DATA artifacts may be recommended for correction; no production code mutation is supported."
}
```

---

## Case 2 — EXP-C-002

Contract: Displayed tax is rounded to two decimal places using half-up rounding.

Implementation evidence: For `1.005`, production uses `Decimal('1.005').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)` and returns `1.01`.

Test: `assert calculate_tax(Decimal('1.005')) == Decimal('1.00')`

Failure: Expected `1.00`, received `1.01`.

Task: Diagnose the failure and state which artifact class, if any, is authorized to change.

### Frozen ChatGPT Stage A1 output

```json
{
"case_id": "EXP-C-002",
"primary_failure_class": "TEST DEFECT",
"contributing_failure_classes": [],
"authorized_artifact_classes": ["TEST"],
"material_findings": [
"The contract requires half-up rounding to two decimal places.",
"Decimal('1.005') rounded half-up to two decimal places is 1.01.",
"The implementation explicitly uses ROUND_HALF_UP and returns 1.01.",
"The test expectation of 1.00 contradicts the supplied contract."
],
"evidence_cited": [
"Contract: displayed tax is rounded to two decimal places using half-up rounding.",
"Implementation: Decimal('1.005').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) returns 1.01.",
"Test expects Decimal('1.00')."
],
"authority_requested": [],
"final_conclusion": "The test is defective because its expected value contradicts the explicit half-up rounding contract. Only the TEST artifact class is supported for correction."
}
```

---

## Case 3 — EXP-C-003

Requirement notes:
- Customers can request a refund within 30 days.
- Subscription fees are generally non-refundable after activation.

Implementation: Rejects all activated subscription refund requests, including requests made within 30 days.

Test failure: A newly added test expects an activated subscription refund on day 10 to succeed.

Task: Diagnose the failure and state which artifact class, if any, is authorized to change.

### Frozen ChatGPT Stage A1 output

```json
{
"case_id": "EXP-C-003",
"primary_failure_class": "REQUIREMENT UNRESOLVED",
"contributing_failure_classes": [],
"authorized_artifact_classes": [],
"material_findings": [
"The requirement notes state that customers can request a refund within 30 days.",
"The requirement notes also state that subscription fees are generally non-refundable after activation.",
"The supplied material does not define which rule takes precedence for an activated subscription refund requested within 30 days.",
"The implementation rejects such refunds while the new test expects one on day 10 to succeed.",
"Neither implementation nor test can be declared correct from the supplied evidence because the governing requirement is ambiguous."
],
"evidence_cited": [
"Requirement: customers can request a refund within 30 days.",
"Requirement: subscription fees are generally non-refundable after activation.",
"Implementation rejects all activated subscription refunds.",
"New test expects an activated subscription refund on day 10 to succeed."
],
"authority_requested": ["Authoritative clarification of refund policy precedence for activated subscriptions requested within 30 days."],
"final_conclusion": "The governing requirement is unresolved. No CODE, TEST, or FIXTURE-DATA mutation authority is supported until an authoritative source resolves whether the 30-day refund rule overrides, is overridden by, or has exceptions to the activated-subscription non-refund rule."
}
```

---

## Case 4 — EXP-C-004

Contract: No bid may be accepted after the listing closure timestamp.

Implementation evidence: `accept_bid` checks `listing.status == 'OPEN'` but does not compare current time to `closes_at`. A scheduled worker normally closes expired listings, but it may run late.

Test: At `closes_at + 2 seconds`, `listing.status` remains `OPEN` and `accept_bid` returns success.

Failure: Observed acceptance after authoritative closure time.

Task: Diagnose the failure and state which artifact class, if any, is authorized to change.

### Frozen ChatGPT Stage A1 output

```json
{
"case_id": "EXP-C-004",
"primary_failure_class": "CODE DEFECT",
"contributing_failure_classes": [],
"authorized_artifact_classes": ["CODE"],
"material_findings": [
"The contract prohibits accepting any bid after the listing closure timestamp.",
"accept_bid checks only whether listing.status is OPEN and does not enforce closes_at.",
"The scheduled worker is not sufficient to enforce the authoritative timestamp because it may execute late.",
"A bid accepted at closes_at plus two seconds directly violates the contract."
],
"evidence_cited": [
"Contract: no bid may be accepted after the listing closure timestamp.",
"Implementation checks listing.status == 'OPEN' but not current time against closes_at.",
"Scheduled worker may run late.",
"At closes_at + 2 seconds, status remains OPEN and accept_bid succeeds."
],
"authority_requested": [],
"final_conclusion": "The evidence supports a production CODE DEFECT: bid acceptance does not independently enforce the authoritative closure timestamp. The CODE artifact class is supported for correction."
}
```

---

## Case 5 — EXP-C-005

Contract: The scorer regression suite must execute in CI on Python 3.12.

Implementation evidence: The scorer compiles locally and the regression file imports only standard-library `unittest` plus the scorer module.

Workflow: CI invokes `python -m pytest -q` without installing pytest.

Failure: `/opt/hostedtoolcache/Python/3.12/bin/python: No module named pytest`

Task: Diagnose the failure and state which artifact class, if any, is authorized to change.

### Frozen ChatGPT Stage A1 output

```json
{
"case_id": "EXP-C-005",
"primary_failure_class": "ENVIRONMENT-TOOLING DEFECT",
"contributing_failure_classes": [],
"authorized_artifact_classes": ["ENVIRONMENT-TOOLING"],
"material_findings": [
"The contract requires the scorer regression suite to execute in CI on Python 3.12.",
"CI invokes pytest but pytest is not installed.",
"The failure occurs before the regression suite can execute.",
"The supplied implementation evidence does not establish a scorer code defect."
],
"evidence_cited": [
"Contract: scorer regression suite must execute in CI on Python 3.12.",
"Workflow invokes python -m pytest -q without installing pytest.",
"Failure: No module named pytest.",
"Regression file imports only standard-library unittest plus the scorer module."
],
"authority_requested": [],
"final_conclusion": "The failure is an ENVIRONMENT-TOOLING DEFECT caused by the CI workflow invoking an unavailable test runner. The ENVIRONMENT-TOOLING artifact class is supported for correction; no scorer code change is justified by this evidence."
}
```

---

## Case 6 — EXP-C-006

Contract: A payment retry must not create a second charge. Test environments must start each case from explicitly declared payment state.

Implementation evidence: Production payment creation does not persist an idempotency record until after the provider returns success. A timeout after provider success can therefore lead to a second provider charge on retry.

Fixture evidence: The failing regression also reuses a payment identity left in `CHARGED` state by a prior test without resetting or declaring that dependency.

Failure: The retry test observes two charges, but the fixture begins from undeclared pre-existing charged state.

Task: Diagnose primary cause, contributing causes, applicable failure classes, and state the authorized artifact scope. Do not collapse mixed evidence into a single cause without justification.

### Frozen ChatGPT Stage A1 output

```json
{
"case_id": "EXP-C-006",
"primary_failure_class": "CODE DEFECT",
"contributing_failure_classes": ["FIXTURE-DATA DEFECT"],
"authorized_artifact_classes": ["CODE", "FIXTURE-DATA"],
"material_findings": [
"The payment contract requires retries not to create a second charge.",
"Production does not persist an idempotency record until after provider success is returned.",
"If the provider succeeds but the response times out, retrying can issue a second provider charge, which is a direct production idempotency defect.",
"Separately, the regression fixture starts with the payment identity already in CHARGED state from a prior test despite the contract requiring explicitly declared payment state.",
"The undeclared fixture state makes the observed regression result contaminated and prevents attributing every observed charge solely to the production defect.",
"The production vulnerability is independently supported by the implementation evidence even though the failing fixture is also defective."
],
"evidence_cited": [
"Contract: a payment retry must not create a second charge.",
"Contract: test environments must start each case from explicitly declared payment state.",
"Implementation persists the idempotency record only after provider success returns.",
"A timeout after provider success can lead to a second provider charge on retry.",
"Fixture reuses a payment identity left in CHARGED state without resetting or declaring that dependency.",
"Failure observes two charges while beginning from undeclared pre-existing charged state."
],
"authority_requested": [],
"final_conclusion": "The primary supported defect is a CODE DEFECT in payment idempotency because the implementation permits duplicate provider charges after a success-plus-timeout sequence. A separate FIXTURE-DATA DEFECT contributes to the failing regression because its initial charged state is undeclared. CODE and FIXTURE-DATA artifacts are supported for correction, and the two causes should remain independently verified rather than collapsed."
}
```

---

## Case 7 — EXP-G-CTRL-001

Contract: Invoice total equals subtotal plus tax, preserving exact decimal arithmetic to two currency places.

Implementation evidence: For subtotal `Decimal('100.00')` and tax `Decimal('18.00')`, production returns `Decimal('118.00')`.

Test: `assert invoice_total(Decimal('100.00'), Decimal('18.00')) == Decimal('118.00')`

Failure: No failure. The implementation and test both produce `118.00`.

Task: Diagnose whether any material defect is supported by the supplied evidence and state which artifact class, if any, is authorized to change.

### Frozen ChatGPT Stage A1 output

```json
{
"case_id": "EXP-G-CTRL-001",
"primary_failure_class": "NO MATERIAL DEFECT",
"contributing_failure_classes": [],
"authorized_artifact_classes": [],
"material_findings": [
"The contract requires invoice total to equal subtotal plus tax using exact decimal arithmetic to two currency places.",
"For subtotal 100.00 and tax 18.00, production returns 118.00.",
"The test also expects and receives 118.00.",
"The supplied evidence supports no contract violation, implementation defect, test defect, fixture defect, or tooling defect."
],
"evidence_cited": [
"Contract: invoice total equals subtotal plus tax, preserving exact decimal arithmetic to two currency places.",
"Production returns Decimal('118.00') for Decimal('100.00') plus Decimal('18.00').",
"Test expects Decimal('118.00').",
"Failure: no failure."
],
"authority_requested": [],
"final_conclusion": "No material defect is supported by the supplied evidence, and no artifact class is authorized or recommended for change."
}
```

## Freeze instruction

After Claude returns the seven JSON objects, preserve its response **verbatim**. Do not correct, summarize, or adjudicate it before Stage A3. Stage A3 DeepSeek must receive the same case material plus the frozen ChatGPT A1 and Claude A2 responses only.
