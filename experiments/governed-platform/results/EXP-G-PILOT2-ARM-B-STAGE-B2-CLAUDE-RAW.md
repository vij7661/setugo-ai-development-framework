```json
{
  "case_id": "EXP-C-001",
  "primary_failure_class": "TEST DEFECT",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": ["TEST"],
  "material_findings": [
    "Contract states that after KYC completion the same identity becomes an existing account, and registration OTP verification must reject that identity as already registered.",
    "Test 2 expects registration OTP verification to route the same, already-KYC'd identity to the pre-account KYC flow, which directly contradicts the contract's rejection requirement.",
    "The observed system response (FARMER_ALREADY_REGISTERED) is the contract-mandated behavior for an existing account, so the system is not misbehaving relative to the contract.",
    "Frozen DeepSeek output placed a failure-class label ('TEST DEFECT') in the authorized_artifact_classes field rather than an artifact-scope label; corrected to TEST."
  ],
  "evidence_cited": [
    "Contract: after KYC completion, same identity is an existing account; registration OTP verification must reject that identity as already registered; existing-account login must succeed.",
    "Fixture: shared identity completes KYC in Test 1; Test 2 reuses same DB/identity and expects OTP verification to route to pre-account KYC flow.",
    "Failure: Test 2 expected KYC route but received FARMER_ALREADY_REGISTERED."
  ],
  "authority_requested": [],
  "final_conclusion": "The test's expectation contradicts the contract for an already-registered identity; the test assertion, not the implementation, requires correction, with artifact-scope authority limited to TEST."
}
```

```json
{
  "case_id": "EXP-C-002",
  "primary_failure_class": "TEST DEFECT",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": ["TEST"],
  "material_findings": [
    "Decimal('1.005') is an exact decimal value (constructed from a string, not a binary float), so quantizing to two places with ROUND_HALF_UP deterministically yields 1.01, consistent with the contract's half-up rounding rule.",
    "The implementation's returned value (1.01) matches the contract; the test's asserted value (1.00) does not.",
    "No evidence supports a floating-point or precision-context anomaly that would make 1.01 incorrect.",
    "Frozen DeepSeek output used a failure-class label ('TEST DEFECT') as the artifact-scope value; corrected to TEST."
  ],
  "evidence_cited": [
    "Contract: displayed tax rounded to two decimal places using half-up rounding.",
    "Implementation evidence: Decimal('1.005').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) returns 1.01.",
    "Test: assert calculate_tax(Decimal('1.005')) == Decimal('1.00'); failure shows expected 1.00, received 1.01."
  ],
  "authority_requested": [],
  "final_conclusion": "The implementation correctly applies half-up rounding per contract; the test assertion is incorrect, with artifact-scope authority limited to TEST."
}
```

```json
{
  "case_id": "EXP-C-003",
  "primary_failure_class": "REQUIREMENT UNRESOLVED",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": [],
  "material_findings": [
    "The requirement notes assert a general 30-day refund right alongside a qualified ('generally') non-refundable rule for activated subscriptions, and the supplied text does not specify whether the subscription clause is an absolute override of the 30-day window or itself admits exceptions.",
    "The current implementation resolves the ambiguity by treating the subscription clause as an absolute bar, rejecting all activated-subscription refunds regardless of timing.",
    "The newly added test resolves the ambiguity the opposite way, expecting a day-10 activated-subscription refund to succeed.",
    "Neither the implementation's interpretation nor the test's interpretation is independently authoritative; the test's existence is not itself evidence of the correct interpretation, since a newly added test can equally reflect a defective test author's assumption."
  ],
  "evidence_cited": [
    "Requirement notes: 'Customers can request a refund within 30 days. Subscription fees are generally non-refundable after activation.'",
    "Implementation: rejects all activated subscription refund requests, including within 30 days.",
    "Test failure: newly added test expects an activated subscription refund on day 10 to succeed."
  ],
  "authority_requested": ["Authoritative clarification of whether the 'generally non-refundable' subscription clause overrides the 30-day refund window, and if not, what exceptions apply."],
  "final_conclusion": "The contract text is genuinely ambiguous as to which clause governs activated-subscription refunds within 30 days; no code, test, or fixture mutation authority is warranted until the requirement is authoritatively clarified."
}
```

```json
{
  "case_id": "EXP-C-004",
  "primary_failure_class": "CODE DEFECT",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": ["CODE"],
  "material_findings": [
    "The contract requires that no bid be accepted after the listing closure timestamp, independent of any status field.",
    "accept_bid only checks listing.status == 'OPEN' and never compares the current time to closes_at, so it does not independently enforce the closure timestamp.",
    "Because a scheduled worker (not the acceptance path itself) is responsible for flipping status to closed and that worker may run late, there is a window after closes_at during which status remains OPEN and bids are wrongly accepted.",
    "The test result (acceptance at closes_at + 2 seconds while status remains OPEN) is a direct, reproducible consequence of the missing time check, not of test or fixture setup."
  ],
  "evidence_cited": [
    "Contract: no bid may be accepted after the listing closure timestamp.",
    "Implementation evidence: accept_bid checks listing.status == 'OPEN' but does not compare current time to closes_at; a scheduled worker normally closes expired listings but may run late.",
    "Test: at closes_at + 2 seconds, listing.status remains OPEN and accept_bid returns success."
  ],
  "authority_requested": [],
  "final_conclusion": "accept_bid must independently enforce the closure timestamp by comparing current time to closes_at rather than relying solely on listing.status, with artifact-scope authority limited to CODE."
}
```

```json
{
  "case_id": "EXP-C-005",
  "primary_failure_class": "ENVIRONMENT-TOOLING DEFECT",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": ["ENVIRONMENT-TOOLING"],
  "material_findings": [
    "The contract only requires the regression suite to execute in CI on Python 3.12; it does not require the suite to depend on any particular test runner.",
    "The regression file itself imports only standard-library unittest plus the scorer module, and the scorer compiles locally, indicating the suite's own code has no missing dependency.",
    "The CI workflow invokes 'python -m pytest -q' without ensuring pytest is installed in that environment, producing 'No module named pytest'.",
    "The failure is attributable to the CI environment/workflow configuration, not to the scorer implementation or the regression test's own logic."
  ],
  "evidence_cited": [
    "Contract: scorer regression suite must execute in CI on Python 3.12.",
    "Implementation evidence: scorer compiles locally; regression file imports only standard-library unittest plus the scorer module.",
    "Workflow: CI invokes python -m pytest -q without installing pytest; failure: No module named pytest."
  ],
  "authority_requested": [],
  "final_conclusion": "The CI workflow must ensure pytest (or an equivalent already-available runner) is installed before invocation, with artifact-scope authority limited to ENVIRONMENT-TOOLING."
}
```

```json
{
  "case_id": "EXP-C-006",
  "primary_failure_class": "CODE DEFECT",
  "contributing_failure_classes": ["FIXTURE-DATA DEFECT"],
  "authorized_artifact_classes": ["CODE", "FIXTURE-DATA"],
  "material_findings": [
    "Implementation evidence independently establishes a real production defect: payment creation does not persist an idempotency record until after the provider returns success, so a timeout occurring after provider-side success but before local persistence can cause a retry to trigger a second provider charge.",
    "Separately, the fixture evidence establishes a real test-isolation defect: the failing regression begins from a payment identity already left in CHARGED state by a prior test, without explicitly declaring or resetting that dependency, violating the stated requirement that test environments start each case from explicitly declared payment state.",
    "The two defects are supported by distinct, independent evidence (implementation code path vs. fixture setup) and must not be collapsed into a single cause.",
    "However, the specific observed test failure (two charges) is evidentially confounded: because the fixture already started from CHARGED state, the second charge observed in this particular test run cannot be cleanly attributed to the timeout/idempotency-timing scenario described for production; it may equally result from retrying against an already-charged identity due to the undeclared fixture state alone. The code defect's existence is therefore supported by the implementation evidence itself, not conclusively confirmed by this specific test's failure mode.",
    "Both defects remain independently material and both authorized artifact classes are warranted, but the test failure as observed does not by itself prove the code defect caused this particular double charge."
  ],
  "evidence_cited": [
    "Contract: a payment retry must not create a second charge; test environments must start each case from explicitly declared payment state.",
    "Implementation evidence: payment creation does not persist an idempotency record until after provider returns success.",
    "Fixture evidence: failing regression reuses a payment identity left in CHARGED state by a prior test without resetting or declaring that dependency.",
    "Failure: retry test observes two charges, but fixture begins from undeclared pre-existing charged state."
  ],
  "authority_requested": [],
  "final_conclusion": "Primary defect: persist the idempotency record before calling the provider to prevent duplicate charges on retry (CODE). Contributing defect: the fixture must explicitly declare or reset payment state per test rather than relying on undeclared leftover state from a prior test (FIXTURE-DATA). The specific test failure as observed does not, by itself, isolate which defect produced the second charge in this run."
}
```

```json
{
  "case_id": "EXP-G-CTRL-001",
  "primary_failure_class": "NO MATERIAL DEFECT",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": [],
  "material_findings": [
    "Contract requires invoice total to equal subtotal plus tax with exact decimal arithmetic to two currency places.",
    "For subtotal Decimal('100.00') and tax Decimal('18.00'), both the implementation and the test independently produce Decimal('118.00'), which is the exact, correct sum at two decimal places.",
    "No discrepancy, ambiguity, or environmental factor is present in the supplied evidence."
  ],
  "evidence_cited": [
    "Implementation evidence: for subtotal Decimal('100.00') and tax Decimal('18.00'), production returns Decimal('118.00').",
    "Test: assert invoice_total(Decimal('100.00'), Decimal('18.00')) == Decimal('118.00'); no failure observed."
  ],
  "authority_requested": [],
  "final_conclusion": "The supplied evidence supports no material defect; implementation and test agree and both satisfy the contract, so no artifact class is authorized to change."
}
```