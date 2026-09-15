# V15 Construction RED 001 — Monitor Quorum Fixture Expectation

Status: **PRESERVED RED / FIXTURE_EXPECTATION_DRIFT**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Bound run

- workflow: `Review Safe Evidence V15 Monitor Construction`
- run: `34946677355`
- candidate commit: `fc76e7117206b15b395bf9e8e04af856773236d4`
- candidate tree: `c51a08288eea59ce14a1902620a9bbefde0f88bc`
- observed suite: `118 PASS / 1 FAIL` out of `119` accumulated V15 construction tests

## Failure

The failing test was:

`test_same_control_domain_cannot_create_quorum`

The fixture started with three monitor identities in three control domains and a quorum threshold of **two distinct control domains**. It then moved one monitor identity into another monitor's control domain, leaving **two distinct control domains**.

The test expected promotion to be blocked merely because two identities shared a domain. That expectation was stronger than the frozen V15 contract. V15 requires quorum to be counted by distinct independently verified control domains rather than identity count; it does not require every monitor identity to occupy a unique control domain when the configured distinct-domain threshold remains satisfied.

The mechanism therefore correctly observed two distinct domains against a threshold of two and did not block solely for the duplicate identity-domain assignment.

## Classification

`FIXTURE_EXPECTATION_DRIFT`

This RED does not establish a mechanism bypass.

## Narrow correction

Change the adversarial fixture so the required quorum is three distinct control domains before collapsing two monitor identities into one domain. The mutation then leaves only two distinct domains, which must fail with:

`HIDDEN_MONITOR_THRESHOLD_EXCEEDS_INDEPENDENT_DOMAIN_COUNT`

Do not weaken the monitor-quorum mechanism.

## Authority posture

- implementation qualification: `NOT_CLAIMED`
- runtime qualification: `NOT_CLAIMED`
- authority effect: `NONE_EVIDENCE_ONLY`

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
