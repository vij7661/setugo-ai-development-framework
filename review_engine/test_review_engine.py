from __future__ import annotations

import unittest

from review_engine import (
    MemoryRecord,
    ReviewEngine,
    ReviewFinding,
    ReviewerConfig,
    ReviewerResponse,
    ReviewRequest,
    VersionedMemoryStore,
)


def cfg(role: str, *, lineage: str | None = None) -> ReviewerConfig:
    return ReviewerConfig(
        role=role,
        provider=f"provider-{role.lower()}",
        model=f"model-{role.lower()}",
        sku="default",
        deployment_path="api",
        api_key_env=f"{role}_API_KEY",
        foundation_lineage=lineage or f"lineage-{role.lower()}",
        qualification_ref=f"qual-{role.lower()}",
    )


class ReviewEngineTests(unittest.TestCase):
    def test_low_risk_request_finishes_with_r1_only(self):
        calls = []
        def invoke(config, context):
            calls.append((config.role, context.get("mode"), context.get("phase")))
            return ReviewerResponse(role="R1", artifact_hash=None, output="simple answer")
        result = ReviewEngine(invoke).run(ReviewRequest(request_id="q1", user_input="brainstorm names"), r1=cfg("R1"), r2=cfg("R2"), r3=cfg("R3"))
        self.assertEqual(result.state, "CONVERGED_PASS")
        self.assertEqual(result.final_output, "simple answer")
        self.assertEqual([c[0] for c in calls], ["R1"])

    def test_platform_high_risk_floor_cannot_be_downgraded_by_r1(self):
        calls = []
        def invoke(config, context):
            calls.append(config.role)
            if config.role == "R1":
                return ReviewerResponse(role="R1", artifact_hash=None, output="candidate", proposed_signals={"risk": "LOW"})
            return ReviewerResponse(role="R2", artifact_hash=context["artifact"]["artifact_hash"], output="clean")
        result = ReviewEngine(invoke).run(ReviewRequest(request_id="q2", user_input="security change", risk="HIGH"), r1=cfg("R1"), r2=cfg("R2"), r3=cfg("R3"))
        self.assertEqual(result.state, "CONVERGED_PASS")
        self.assertEqual(calls, ["R1", "R2"])

    def test_r1_can_escalate_review_but_not_self_authorize_direct_finalization(self):
        calls = []
        def invoke(config, context):
            calls.append(config.role)
            if config.role == "R1":
                return ReviewerResponse(role="R1", artifact_hash=None, output="candidate", proposed_signals={"risk": "MEDIUM"})
            return ReviewerResponse(role="R2", artifact_hash=context["artifact"]["artifact_hash"], output="clean")
        result = ReviewEngine(invoke).run(ReviewRequest(request_id="q3", user_input="looks simple", risk="LOW"), r1=cfg("R1"), r2=cfg("R2"), r3=cfg("R3"))
        self.assertEqual(result.state, "CONVERGED_PASS")
        self.assertEqual(calls, ["R1", "R2"])

    def test_material_r2_finding_causes_scoped_revision_and_blinded_r3_verification(self):
        calls = []
        def invoke(config, context):
            calls.append((config.role, context.get("mode"), context.get("phase")))
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse(role="R1", artifact_hash=None, output="v1 wrong")
            if config.role == "R2":
                finding = ReviewFinding("f1", "R2", "HIGH", True, "claim 2 violates invariant AUTH-1", "AUTH-1", (), ("claim:2",), "claim:2")
                return ReviewerResponse(role="R2", artifact_hash=context["artifact"]["artifact_hash"], output="localized finding", findings=(finding,))
            if config.role == "R1":
                self.assertEqual(context["mode"], "SCOPED_CORRECTION")
                self.assertEqual(context["verified_review_targets"][0]["affected_scope"], ["claim:2"])
                return ReviewerResponse(role="R1", artifact_hash=None, output="v2 corrected")
            self.assertEqual(context["phase"], "INDEPENDENT")
            self.assertNotIn("prior_reviews", context)
            return ReviewerResponse(role="R3", artifact_hash=context["artifact"]["artifact_hash"], output="independently verified")
        result = ReviewEngine(invoke).run(ReviewRequest(request_id="q4", user_input="change architecture", risk="HIGH", materiality="MATERIAL"), r1=cfg("R1"), r2=cfg("R2", lineage="lineage-a"), r3=cfg("R3", lineage="lineage-b"))
        self.assertEqual(result.state, "CONVERGED_PASS")
        self.assertEqual(result.final_output, "v2 corrected")
        self.assertEqual(calls, [("R1", None, None), ("R2", None, None), ("R1", "SCOPED_CORRECTION", None), ("R3", None, "INDEPENDENT")])

    def test_high_risk_r3_must_be_lineage_independent_from_r2(self):
        def invoke(config, context):
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse(role="R1", artifact_hash=None, output="v1")
            if config.role == "R2":
                f = ReviewFinding("f", "R2", "HIGH", True, "material defect")
                return ReviewerResponse("R2", context["artifact"]["artifact_hash"], "bad", (f,))
            if config.role == "R1":
                return ReviewerResponse(role="R1", artifact_hash=None, output="v2")
            self.fail("R3 must not be called")
        result = ReviewEngine(invoke).run(ReviewRequest(request_id="q5", user_input="critical change", risk="HIGH", materiality="MATERIAL"), r1=cfg("R1"), r2=cfg("R2", lineage="same"), r3=cfg("R3", lineage="same"))
        self.assertEqual(result.state, "HUMAN_REQUIRED")
        self.assertIn("foundation-lineage", result.reasons[0])

    def test_r3_prior_reviews_are_disclosed_only_after_independent_view_is_frozen(self):
        phases = []
        def invoke(config, context):
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse(role="R1", artifact_hash=None, output="v1")
            if config.role == "R2":
                f = ReviewFinding("f1", "R2", "HIGH", True, "material issue")
                return ReviewerResponse("R2", context["artifact"]["artifact_hash"], "R2 says issue", (f,))
            if config.role == "R1":
                return ReviewerResponse(role="R1", artifact_hash=None, output="v2")
            phases.append(context["phase"])
            if context["phase"] == "INDEPENDENT":
                self.assertNotIn("prior_reviews", context)
                f = ReviewFinding("f2", "R3", "MEDIUM", True, "still uncertain")
                return ReviewerResponse("R3", context["artifact"]["artifact_hash"], "independent concern", (f,))
            self.assertEqual(context["frozen_independent_view"], "independent concern")
            self.assertEqual(context["prior_reviews"]["R2"], "R2 says issue")
            return ReviewerResponse("R3", context["artifact_hash"], "resolved after evidence comparison")
        result = ReviewEngine(invoke).run(ReviewRequest(request_id="q6", user_input="material change", risk="HIGH", materiality="MATERIAL"), r1=cfg("R1"), r2=cfg("R2", lineage="a"), r3=cfg("R3", lineage="b"))
        self.assertEqual(result.state, "CONVERGED_PASS")
        self.assertEqual(phases, ["INDEPENDENT", "ADJUDICATION"])

    def test_authoritative_memory_is_versioned_and_external_authority_only(self):
        store = VersionedMemoryStore()
        v1 = MemoryRecord("req:1", "AUTHORITATIVE", "ACTIVE", 1, "user-approved", "must verify")
        with self.assertRaises(PermissionError): store.append(v1)
        store.append(v1, external_authority=True)
        with self.assertRaises(ValueError): store.append(v1, external_authority=True)
        v2 = MemoryRecord("req:1", "AUTHORITATIVE", "ACTIVE", 2, "user-approved", "must independently verify", supersedes_version=1)
        store.append(v2, external_authority=True)
        self.assertEqual(store.current(), (v2,))

    def test_incomplete_consequential_evidence_fails_to_human_before_r2(self):
        calls = []
        def invoke(config, context):
            calls.append(config.role)
            return ReviewerResponse(role="R1", artifact_hash=None, output="candidate")
        result = ReviewEngine(invoke).run(ReviewRequest(request_id="q7", user_input="deploy change", risk="HIGH", external_action=True, evidence_complete=False), r1=cfg("R1"), r2=cfg("R2"), r3=cfg("R3"))
        self.assertEqual(result.state, "HUMAN_REQUIRED")
        self.assertEqual(calls, ["R1"])


if __name__ == "__main__": unittest.main()
