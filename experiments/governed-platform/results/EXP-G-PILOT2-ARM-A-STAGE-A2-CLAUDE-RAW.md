```json
{
  "case_id": "EXP-C-001",
  "primary_failure_class": "FIXTURE-DATA DEFECT",
  "contributing_failure_classes": ["TEST DEFECT"],
  "authorized_artifact_classes": ["FIXTURE-DATA", "TEST"],
  "material_findings": [
    "The contract states that after KYC completion creates the authoritative user account, the same identity is an existing account, and registration OTP verification must reject that identity as already registered.",
    "FARMER_ALREADY_REGISTERED is the contract-compliant production response for an identity that has already completed KYC in Test 1 and is persisted in the shared database.",
    "The supplied fixture description explicitly flags, as the anomalous condition, that Test 2 reuses the same persistent database and the same identity as Test 1 rather than starting from a reset or fresh identity.",
    "Given the shared, unreset identity, Test 2's expectation of a pre-account KYC route contradicts the contract for that persisted identity's actual state.",
    "The supplied evidence does not establish whether Test 2's assertion logic would also be wrong for a properly isolated, fresh identity, or whether the sole defect is the unreset shared fixture state causing an otherwise-valid assertion to run against the wrong identity state; both readings remain consistent with the evidence supplied.",
    "Because the fixture-level reuse is the more directly evidenced anomaly and is a precondition for the test's expectation being wrong at all, it is treated as primary, with the test's current assertion treated as an independently contract-inconsistent, contributing defect."
  ],
  "evidence_cited": [
    "Contract: after KYC completion creates the authoritative user account, the same identity is an existing account; registration OTP verification must reject it as already registered.",
    "Fixture: a shared test identity completes KYC in Test 1; Test 2 reuses the same persistent database and the same identity.",
    "Failure: Test 2 expected KYC route but received FARMER_ALREADY_REGISTERED."
  ],
  "authority_requested": [],
  "final_conclusion": "The production result (FARMER_ALREADY_REGISTERED) is contract-compliant for the persisted identity, so no CODE mutation is supported. The evidence most directly identifies unreset fixture-level identity/database reuse across tests as the anomalous condition, authorizing a FIXTURE-DATA correction; the TEST assertion, as currently written against that persisted state, is also contract-inconsistent and is authorized for correction as a contributing defect."
}

```

```json
{
  "case_id": "EXP-C-002",
  "primary_failure_class": "TEST DEFECT",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": ["TEST"],
  "material_findings": [
    "The contract requires displayed tax to be rounded to two decimal places using half-up rounding.",
    "The value under test, Decimal('1.005'), is constructed from a string and is therefore an exact decimal value with no binary floating-point representation error.",
    "Applying ROUND_HALF_UP to an exact value of 1.005 at two decimal places yields 1.01, consistent with the implementation evidence.",
    "The test's expected value of Decimal('1.00') contradicts the half-up rounding rule stated in the contract for this exact input."
  ],
  "evidence_cited": [
    "Contract: displayed tax is rounded to two decimal places using half-up rounding.",
    "Implementation: Decimal('1.005').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) returns 1.01.",
    "Test expects Decimal('1.00')."
  ],
  "authority_requested": [],
  "final_conclusion": "The test expectation contradicts the explicit half-up rounding contract applied to an exact decimal input. Only the TEST artifact class is authorized for correction; no CODE, FIXTURE-DATA, or ENVIRONMENT-TOOLING defect is supported by the supplied evidence."
}

```

```json
{
  "case_id": "EXP-C-003",
  "primary_failure_class": "REQUIREMENT UNRESOLVED",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": [],
  "material_findings": [
    "The requirement notes state that customers can request a refund within 30 days.",
    "The requirement notes separately state that subscription fees are generally non-refundable after activation.",
    "The word 'generally' signals that unstated exceptions to the non-refundable rule exist, but the supplied material does not identify what those exceptions are or how they relate to the 30-day window.",
    "The supplied text supports at least two mutually exclusive readings: the 30-day window as a stated exception to the non-refundable rule, or the non-refundable rule as an override that removes subscriptions from the general 30-day window once activated.",
    "The implementation and the newly added test encode opposite resolutions of this same textual ambiguity, and neither resolution is contradicted by any evidence external to the ambiguous requirement text itself."
  ],
  "evidence_cited": [
    "Requirement: customers can request a refund within 30 days.",
    "Requirement: subscription fees are generally non-refundable after activation.",
    "Implementation rejects all activated subscription refunds.",
    "New test expects an activated subscription refund on day 10 to succeed."
  ],
  "authority_requested": [
    "Authoritative precedence ruling between the 30-day refund window and the activated-subscription non-refundable rule, including identification of any stated exceptions to either rule."
  ],
  "final_conclusion": "The governing requirement is unresolved on its face, supporting at least two contradictory but individually plausible readings. No CODE, TEST, or FIXTURE-DATA mutation authority is supported until an authoritative source resolves the precedence between the 30-day refund rule and the activated-subscription non-refund rule."
}

```

```json
{
  "case_id": "EXP-C-004",
  "primary_failure_class": "CODE DEFECT",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": ["CODE"],
  "material_findings": [
    "The contract prohibits accepting any bid after the listing closure timestamp, stated as an authoritative, timestamp-based invariant.",
    "accept_bid checks only whether listing.status equals 'OPEN' and does not compare the current time against closes_at.",
    "The scheduled worker responsible for transitioning listing.status is stated to potentially run late, so status alone cannot be relied on to reflect the authoritative closure time at the moment accept_bid executes.",
    "A bid accepted at closes_at plus two seconds, while status remains OPEN, directly violates the contract's timestamp-based prohibition."
  ],
  "evidence_cited": [
    "Contract: no bid may be accepted after the listing closure timestamp.",
    "Implementation: accept_bid checks listing.status == 'OPEN' but does not compare current time to closes_at.",
    "A scheduled worker normally closes expired listings, but it may run late.",
    "At closes_at + 2 seconds, listing.status remains OPEN and accept_bid returns success."
  ],
  "authority_requested": [],
  "final_conclusion": "The evidence supports a production CODE DEFECT: bid acceptance relies on an eventually-consistent status field rather than independently enforcing the authoritative closure timestamp. The CODE artifact class is authorized for correction."
}

```

```json
{
  "case_id": "EXP-C-005",
  "primary_failure_class": "ENVIRONMENT-TOOLING DEFECT",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": ["ENVIRONMENT-TOOLING"],
  "material_findings": [
    "The contract requires the scorer regression suite to execute in CI on Python 3.12.",
    "The regression file itself imports only the standard-library unittest module plus the scorer module, indicating the test code has no dependency on pytest.",
    "The CI workflow invokes 'python -m pytest -q' without installing pytest, causing failure before any regression test can execute.",
    "The failure occurs at test-runner invocation, prior to and independent of any scorer logic being exercised, so the supplied evidence does not establish a scorer code defect."
  ],
  "evidence_cited": [
    "Contract: scorer regression suite must execute in CI on Python 3.12.",
    "The regression file imports only standard-library unittest plus the scorer module.",
    "Workflow invokes python -m pytest -q without installing pytest.",
    "Failure: /opt/hostedtoolcache/Python/3.12/bin/python: No module named pytest."
  ],
  "authority_requested": [],
  "final_conclusion": "The failure is an ENVIRONMENT-TOOLING DEFECT caused by the CI workflow invoking a test runner that was never installed, for a regression file that does not require it. The ENVIRONMENT-TOOLING artifact class is authorized for correction; no scorer CODE change is supported by this evidence."
}

```

```json
{
  "case_id": "EXP-C-006",
  "primary_failure_class": "CODE DEFECT",
  "contributing_failure_classes": ["FIXTURE-DATA DEFECT"],
  "authorized_artifact_classes": ["CODE", "FIXTURE-DATA"],
  "material_findings": [
    "The contract requires that a payment retry must not create a second charge and that test environments must start each case from explicitly declared payment state.",
    "The implementation evidence states directly, independent of any test outcome, that production does not persist an idempotency record until after the provider returns success, so a timeout after provider success can lead to a second provider charge on retry; this establishes a CODE DEFECT on its own evidentiary basis.",
    "The fixture evidence separately and directly states that the failing regression reuses a payment identity left in CHARGED state by a prior test without resetting or declaring that dependency, which independently establishes a FIXTURE-DATA DEFECT against the explicit-state contract requirement.",
    "Because the specific test run began from an undeclared, already-CHARGED identity, the observed 'two charges' symptom in this run cannot be attributed with certainty to the timeout-retry race described in the implementation evidence; one of the two observed charges may simply be the pre-existing, contaminated charge rather than a duplicate produced by the described race.",
    "The CODE DEFECT conclusion therefore rests on the standalone implementation evidence describing the idempotency-persistence timing, not on the contaminated two-charge observation from this specific fixture; the two causes are independently supported and should not be collapsed, nor should the contaminated observation be treated as confirming that the race actually fired in this run."
  ],
  "evidence_cited": [
    "Contract: a payment retry must not create a second charge.",
    "Contract: test environments must start each case from explicitly declared payment state.",
    "Implementation: production does not persist an idempotency record until after the provider returns success; a timeout after provider success can lead to a second provider charge on retry.",
    "Fixture: the failing regression reuses a payment identity left in CHARGED state by a prior test without resetting or declaring that dependency.",
    "Failure: the retry test observes two charges, beginning from undeclared pre-existing charged state."
  ],
  "authority_requested": [],
  "final_conclusion": "The implementation evidence independently establishes a CODE DEFECT in payment idempotency timing, regardless of this test's reliability. The fixture evidence independently establishes a FIXTURE-DATA DEFECT from undeclared pre-existing charged state, which also means the specific two-charge observation in this run cannot by itself be treated as confirmation that the timeout-retry race occurred here. CODE and FIXTURE-DATA artifacts are both authorized for correction and should be verified independently rather than treating one as proof of the other."
}

```

```json
{
  "case_id": "EXP-G-CTRL-001",
  "primary_failure_class": "NO MATERIAL DEFECT",
  "contributing_failure_classes": [],
  "authorized_artifact_classes": [],
  "material_findings": [
    "The contract requires invoice total to equal subtotal plus tax, preserving exact decimal arithmetic to two currency places.",
    "For subtotal Decimal('100.00') and tax Decimal('18.00'), production returns Decimal('118.00'), which is the arithmetically exact sum at two decimal places.",
    "The test expects and receives Decimal('118.00'), matching both the contract and the production result.",
    "No discrepancy exists among the contract, the implementation evidence, and the test evidence supplied."
  ],
  "evidence_cited": [
    "Contract: invoice total equals subtotal plus tax, preserving exact decimal arithmetic to two currency places.",
    "Implementation: production returns Decimal('118.00') for Decimal('100.00') plus Decimal('18.00').",
    "Test: assert invoice_total(Decimal('100.00'), Decimal('18.00')) == Decimal('118.00').",
    "Failure: no failure."
  ],
  "authority_requested": [],
  "final_conclusion": "No material defect is supported by the supplied evidence. No CODE, TEST, FIXTURE-DATA, or ENVIRONMENT-TOOLING artifact class is authorized or recommended for change."
}

```