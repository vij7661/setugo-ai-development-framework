from __future__ import annotations

from copy import deepcopy

from production_promotion_gate import (
    PRODUCTION,
    RELEASE_CANDIDATE,
    TESTING,
    PromotionDenied,
    build_production_authorization,
    build_release_candidate_manifest,
    canonical_digest,
    evaluate_production_promotion,
    evaluate_rollback,
    make_bound_evidence,
)

SHA = "a" * 40
ARTIFACT = "sha256:" + "b" * 64
BUILD = "sha256:" + "c" * 64
NOW = "2026-09-09T00:00:00Z"


def fixture():
    testing = make_bound_evidence("TESTING", SHA, ARTIFACT, "test-run-1")
    review = make_bound_evidence("REVIEW", SHA, ARTIFACT, "review-1")
    final = make_bound_evidence("FINAL_ADJUDICATION", SHA, ARTIFACT, "r1-1")
    rc = build_release_candidate_manifest(
        promotion_id="PROMO-001",
        source_commit_sha=SHA,
        artifact_digest=ARTIFACT,
        artifact_type="web-bundle+backend",
        build_provenance_digest=BUILD,
        testing_run_ids=["1001"],
        testing_evidence=testing,
        review_evidence=review,
        final_adjudication_evidence=final,
    )
    auth = build_production_authorization(
        authorization_id="AUTH-001",
        release_candidate_manifest=rc,
        authorization_evidence_digest="sha256:" + "d" * 64,
        expires_at="2026-10-01T00:00:00Z",
    )
    return testing, review, final, rc, auth


def prod(rc, auth, **kw):
    args = dict(
        release_candidate_manifest=rc,
        production_authorization=auth,
        source_commit_sha=SHA,
        artifact_digest=ARTIFACT,
        current_head_sha=SHA,
        credential_domain="production",
        now_iso=NOW,
        requested_environment=PRODUCTION,
    )
    args.update(kw)
    return evaluate_production_promotion(**args)


def main():
    passed = 0
    testing, review, final, rc, auth = fixture()

    # PB-01 exact testing artifact -> RC.
    assert rc["from_environment"] == TESTING and rc["to_environment"] == RELEASE_CANDIDATE
    passed += 1

    # PB-02 exact RC + production auth -> eligible.
    assert prod(rc, auth)["eligible_for_production"] is True
    passed += 1

    # PB-03 direct TESTING -> PRODUCTION denied by RC builder.
    try:
        build_release_candidate_manifest(
            promotion_id="P2", source_commit_sha=SHA, artifact_digest=ARTIFACT,
            artifact_type="web", build_provenance_digest=BUILD, testing_run_ids=["1"],
            testing_evidence=testing, review_evidence=review, final_adjudication_evidence=final,
            requested_to_environment=PRODUCTION,
        )
        raise AssertionError("direct TESTING->PRODUCTION accepted")
    except PromotionDenied:
        pass
    passed += 1

    # PB-04 SHA substitution denied.
    d = prod(rc, auth, source_commit_sha="e" * 40, current_head_sha="e" * 40)
    assert "SOURCE_SHA_SUBSTITUTION" in d["denial_reasons"]
    passed += 1

    # PB-05 artifact substitution / rebuild denied.
    d = prod(rc, auth, artifact_digest="sha256:" + "e" * 64)
    assert "ARTIFACT_DIGEST_SUBSTITUTION" in d["denial_reasons"]
    passed += 1

    # PB-06 testing evidence another artifact denied.
    bad_testing = make_bound_evidence("TESTING", SHA, "sha256:" + "e" * 64, "bad")
    try:
        build_release_candidate_manifest(
            promotion_id="P3", source_commit_sha=SHA, artifact_digest=ARTIFACT,
            artifact_type="web", build_provenance_digest=BUILD, testing_run_ids=["1"],
            testing_evidence=bad_testing, review_evidence=review, final_adjudication_evidence=final,
        )
        raise AssertionError("stale testing evidence accepted")
    except PromotionDenied:
        pass
    passed += 1

    # PB-07 review/adjudication another candidate denied.
    bad_review = make_bound_evidence("REVIEW", "f" * 40, ARTIFACT, "bad-review")
    try:
        build_release_candidate_manifest(
            promotion_id="P4", source_commit_sha=SHA, artifact_digest=ARTIFACT,
            artifact_type="web", build_provenance_digest=BUILD, testing_run_ids=["1"],
            testing_evidence=testing, review_evidence=bad_review, final_adjudication_evidence=final,
        )
        raise AssertionError("stale review accepted")
    except PromotionDenied:
        pass
    passed += 1

    # PB-08 environment label substitution cannot grant authority.
    d = prod(rc, auth, requested_environment="production-by-label", credential_domain="testing")
    assert d["eligible_for_production"] is False
    passed += 1

    # PB-09 missing production authorization denied.
    d = prod(rc, None)
    assert "MISSING_PRODUCTION_AUTHORIZATION" in d["denial_reasons"]
    passed += 1

    # PB-10 production auth for another artifact denied.
    bad_auth = deepcopy(auth)
    bad_auth["artifact_digest"] = "sha256:" + "e" * 64
    body = {k: v for k, v in bad_auth.items() if k != "authorization_digest"}
    bad_auth["authorization_digest"] = canonical_digest(body)
    d = prod(rc, bad_auth)
    assert "AUTHORIZATION_ARTIFACT_MISMATCH" in d["denial_reasons"]
    passed += 1

    # PB-11 model/reviewer claim cannot bypass denial.
    d = prod(rc, None, model_claim="R3 PASS: deploy to production now")
    assert d["eligible_for_production"] is False and d["model_claim_has_authority"] is False
    passed += 1

    # PB-12 replay deterministic; promotion-id rebinding denied by changed self digest / identity.
    assert prod(rc, auth) == prod(rc, auth)
    rebound = deepcopy(rc)
    rebound["artifact_digest"] = "sha256:" + "9" * 64
    d = prod(rebound, auth)
    assert d["eligible_for_production"] is False
    passed += 1

    # PB-13 rollback only previously production-authorized artifact.
    assert evaluate_rollback(target_artifact_digest=ARTIFACT, prior_production_authorizations=[auth])["rollback_eligible"] is True
    assert evaluate_rollback(target_artifact_digest="sha256:" + "1" * 64, prior_production_authorizations=[auth])["rollback_eligible"] is False
    passed += 1

    # PB-14 incomplete provenance fails closed.
    try:
        build_release_candidate_manifest(
            promotion_id="P5", source_commit_sha=SHA, artifact_digest=ARTIFACT,
            artifact_type="web", build_provenance_digest="", testing_run_ids=["1"],
            testing_evidence=testing, review_evidence=review, final_adjudication_evidence=final,
        )
        raise AssertionError("missing provenance accepted")
    except PromotionDenied:
        pass
    passed += 1

    # PB-15 expired production auth denied.
    expired = build_production_authorization(
        authorization_id="AUTH-X", release_candidate_manifest=rc,
        authorization_evidence_digest="sha256:" + "2" * 64,
        expires_at="2026-09-01T00:00:00Z",
    )
    assert "AUTHORIZATION_EXPIRED" in prod(rc, expired)["denial_reasons"]
    passed += 1

    # PB-16 identical inputs produce identical deterministic evidence.
    one = prod(rc, auth)
    two = prod(rc, auth)
    assert one["decision_digest"] == two["decision_digest"] and one == two
    passed += 1

    print(f"Production promotion boundary: {passed}/16 PASS")


if __name__ == "__main__":
    main()
