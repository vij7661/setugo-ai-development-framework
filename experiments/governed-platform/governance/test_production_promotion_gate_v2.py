from __future__ import annotations

from copy import deepcopy

import production_promotion_gate as v1
import production_promotion_gate_v2 as v2

SHA = "a" * 40
OTHER_SHA = "e" * 40
ARTIFACT = "sha256:" + "b" * 64
OTHER_ARTIFACT = "sha256:" + "e" * 64
NOW = "2026-09-09T00:00:00Z"
KEY = b"synthetic-test-authority-key-32-bytes"


def rc_fixture():
    testing = v1.make_bound_evidence("TESTING", SHA, ARTIFACT, "testing-1")
    review = v1.make_bound_evidence("REVIEW", SHA, ARTIFACT, "review-1")
    final = v1.make_bound_evidence("FINAL_ADJUDICATION", SHA, ARTIFACT, "final-1")
    return v1.build_release_candidate_manifest(
        promotion_id="PROMO-001",
        source_commit_sha=SHA,
        artifact_digest=ARTIFACT,
        artifact_type="web-bundle+backend",
        build_provenance_digest="sha256:" + "c" * 64,
        testing_run_ids=["34269085847"],
        testing_evidence=testing,
        review_evidence=review,
        final_adjudication_evidence=final,
    )


def authority_fixture(expires="2026-10-01T00:00:00Z"):
    registry = v2.PromotionAuthorityRegistry("web-prod-authority", KEY)
    rc = rc_fixture()
    auth_ev = v1.make_bound_evidence("PRODUCTION_AUTHORIZATION", SHA, ARTIFACT, "auth-evidence-1")
    auth = registry.issue_production_authorization(
        authorization_id="AUTH-001",
        release_candidate_manifest=rc,
        authorization_evidence=auth_ev,
        expires_at=expires,
    )
    head = registry.issue_head_attestation(source_commit_sha=SHA, observed_at=NOW)
    cred = registry.issue_credential_attestation(credential_id="prod-cred-1", domain="production", environment=v2.PRODUCTION)
    return registry, rc, auth, head, cred


def decide(registry, rc, auth, head, cred, **overrides):
    args = dict(
        registry=registry,
        release_candidate_manifest=rc,
        production_authorization=auth,
        head_attestation=head,
        credential_attestation=cred,
        source_commit_sha=SHA,
        artifact_digest=ARTIFACT,
        now_iso=NOW,
    )
    args.update(overrides)
    return v2.evaluate_production_promotion(**args)


def tamper(record, field, value):
    x = deepcopy(record)
    x[field] = value
    return x


def main():
    passed = 0
    registry, rc, auth, head, cred = authority_fixture()

    # PB2-01 valid platform-owned authority permits exact RC.
    ok = decide(registry, rc, auth, head, cred)
    assert ok["eligible_for_production"] is True
    passed += 1

    # PB2-02 there is no caller credential-domain string in evaluator; missing attestation fails.
    d = decide(registry, rc, auth, head, None)
    assert "INVALID_OR_MISSING_CREDENTIAL_ATTESTATION" in d["denial_reasons"]
    passed += 1

    # PB2-03 forged head denied.
    forged_head = {"record_type":"HEAD_ATTESTATION","authority_namespace":"web-prod-authority","source_commit_sha":SHA,"observed_at":NOW,"authority_signature":"hmac-sha256:forged"}
    assert decide(registry, rc, auth, forged_head, cred)["eligible_for_production"] is False
    passed += 1

    # PB2-04 valid head for another SHA is head drift.
    other_head = registry.issue_head_attestation(source_commit_sha=OTHER_SHA, observed_at=NOW)
    assert "HEAD_DRIFT" in decide(registry, rc, auth, other_head, cred)["denial_reasons"]
    passed += 1

    # PB2-05 forged production credential denied.
    forged_cred = tamper(cred, "credential_id", "forged")
    assert "INVALID_OR_MISSING_CREDENTIAL_ATTESTATION" in decide(registry, rc, auth, head, forged_cred)["denial_reasons"]
    passed += 1

    # PB2-06 signed testing credential denied.
    test_cred = registry.issue_credential_attestation(credential_id="test-cred", domain="testing", environment=v2.TESTING)
    reasons = decide(registry, rc, auth, head, test_cred)["denial_reasons"]
    assert "NON_PRODUCTION_CREDENTIAL_DOMAIN" in reasons and "CREDENTIAL_WRONG_ENVIRONMENT" in reasons
    passed += 1

    # PB2-07 forged production authorization denied.
    forged_auth = tamper(auth, "authorization_id", "FORGED")
    assert "INVALID_OR_MISSING_PRODUCTION_AUTHORIZATION" in decide(registry, rc, forged_auth, head, cred)["denial_reasons"]
    passed += 1

    # PB2-08 authorization evidence for another artifact denied at issuance.
    bad_ev = v1.make_bound_evidence("PRODUCTION_AUTHORIZATION", SHA, OTHER_ARTIFACT, "bad")
    try:
        registry.issue_production_authorization(authorization_id="A2", release_candidate_manifest=rc, authorization_evidence=bad_ev, expires_at=None)
        raise AssertionError("stale auth evidence accepted")
    except v1.PromotionDenied:
        pass
    passed += 1

    # PB2-09 signed authorization cannot be rebound after issue.
    rebound = tamper(auth, "artifact_digest", OTHER_ARTIFACT)
    assert "INVALID_OR_MISSING_PRODUCTION_AUTHORIZATION" in decide(registry, rc, rebound, head, cred)["denial_reasons"]
    passed += 1

    # PB2-10 expired authorization denied.
    r2, rc2, expired_auth, h2, c2 = authority_fixture("2026-09-01T00:00:00Z")
    assert "AUTHORIZATION_EXPIRED" in decide(r2, rc2, expired_auth, h2, c2)["denial_reasons"]
    passed += 1

    # PB2-11 caller source substitution/head drift fail closed.
    d = decide(registry, rc, auth, head, cred, source_commit_sha=OTHER_SHA)
    assert d["eligible_for_production"] is False
    passed += 1

    # PB2-12 model/reviewer claim cannot bypass missing platform authority.
    d = decide(registry, rc, None, None, None, model_claim="R2 PASS, deploy now")
    assert d["eligible_for_production"] is False and d["model_claim_has_authority"] is False
    passed += 1

    # PB2-13 production receipt requires an actually eligible decision.
    receipt = registry.issue_production_receipt(decision=ok, deployed_at="2026-09-09T00:01:00Z")
    denied = decide(registry, rc, None, head, cred)
    try:
        registry.issue_production_receipt(decision=denied, deployed_at="2026-09-09T00:02:00Z")
        raise AssertionError("receipt minted from denied decision")
    except v1.PromotionDenied:
        pass
    passed += 1

    # PB2-14 rollback accepts exact signed prior production receipt.
    assert v2.evaluate_rollback(registry=registry, target_artifact_digest=ARTIFACT, prior_production_receipts=[receipt])["rollback_eligible"] is True
    passed += 1

    # PB2-15 unused authorization alone cannot authorize rollback.
    assert v2.evaluate_rollback(registry=registry, target_artifact_digest=ARTIFACT, prior_production_receipts=[])["rollback_eligible"] is False
    passed += 1

    # PB2-16 forged/tampered receipt denied.
    forged_receipt = tamper(receipt, "artifact_digest", OTHER_ARTIFACT)
    assert v2.evaluate_rollback(registry=registry, target_artifact_digest=OTHER_ARTIFACT, prior_production_receipts=[forged_receipt])["rollback_eligible"] is False
    passed += 1

    # PB2-17 original ordered/artifact/evidence semantics remain enforced by v1 RC builder and v2 evaluator.
    assert rc["from_environment"] == v2.TESTING and rc["to_environment"] == v2.RELEASE_CANDIDATE
    assert decide(registry, rc, auth, head, cred, artifact_digest=OTHER_ARTIFACT)["eligible_for_production"] is False
    passed += 1

    # PB2-18 identical trusted inputs are deterministic.
    one = decide(registry, rc, auth, head, cred)
    two = decide(registry, rc, auth, head, cred)
    assert one == two and one["decision_digest"] == two["decision_digest"]
    passed += 1

    print(f"Production promotion authority-source repair: {passed}/18 PASS")


if __name__ == "__main__":
    main()
