from __future__ import annotations

import unittest

from review_engine.judge_health import JudgeHealthMonitor, JudgeObservation
from review_engine.models import ReviewFinding, ReviewerConfig, ReviewerResponse, ReviewRequest
from review_engine.orchestrator import ReviewEngine
from review_engine.qualification import QualificationRecord, QualificationRegistry
from review_engine.truth_contract import TVC_VERSION, evaluate_truth_contract, neutral_epistemic_review


def cfg(role: str, lineage: str) -> ReviewerConfig:
    return ReviewerConfig(
        role=role,
        provider=f"p-{role.lower()}",
        model=f"m-{role.lower()}",
        sku="default",
        deployment_path="api",
        api_key_env=f"{role}_KEY",
        foundation_lineage=lineage,
        qualification_ref=f"q-{role.lower()}",
    )


def registry(*configs: ReviewerConfig) -> QualificationRegistry:
    return QualificationRegistry(tuple(
        QualificationRecord(
            qualification_ref=config.qualification_ref,
            provider=config.provider,
            model=config.model,
            sku=config.sku,
            deployment_path=config.deployment_path,
            role=config.role,
            status="QUALIFIED",
            qualification_epoch=1,
            foundation_lineage=config.foundation_lineage,
            max_risk="CRITICAL",
            task_types=("*",),
        )
        for config in configs
    ))


def unverified_material_review(text: str = "The deployment succeeded.") -> dict:
    return {
        "version": TVC_VERSION,
        "correspondence": "UNVERIFIED",
        "coherence": "CONSISTENT",
        "pragmatic": "VIABLE",
        "semantic": "PRECISE",
        "contradiction_refs": [],
        "claims": [{
            "claim_id": "c1",
            "text": text,
            "claim_type": "EMPIRICAL_FACT",
            "correspondence": "UNVERIFIED",
            "evidence_refs": [],
            "material": True,
        }],
    }


class ProductFalsificationTests(unittest.TestCase):
    def test_r2_cannot_hide_material_unverified_fact_by_omitting_free_form_finding(self):
        r1, r2, r3 = cfg("R1", "l1"), cfg("R2", "l2"), cfg("R3", "l3")
        calls = []

        def invoke(config, context):
            calls.append((config.role, context.get("mode"), context.get("phase")))
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse("R1", None, "v1: deployment succeeded")
            if config.role == "R2":
                # Free-form findings are deliberately empty. TVC must still
                # synthesize the material correspondence failure.
                return ReviewerResponse(
                    "R2",
                    context["artifact"]["artifact_hash"],
                    "looks fine",
                    findings=(),
                    epistemic_review=unverified_material_review(),
                )
            if config.role == "R1":
                self.assertEqual(context["verified_review_targets"][0]["violated_invariant"], "TVC-CORRESPONDENCE")
                return ReviewerResponse("R1", None, "v2: deployment status is unverified")
            return ReviewerResponse(
                "R3",
                context["artifact"]["artifact_hash"],
                "independently verified qualification of the claim",
                epistemic_review=neutral_epistemic_review(),
            )

        decision = ReviewEngine(invoke, qualification_registry=registry(r1, r2, r3)).run(
            ReviewRequest("pf-tvc-r2", "review deployment statement", risk="MEDIUM"),
            r1=r1,
            r2=r2,
            r3=r3,
        )
        self.assertEqual(decision.state, "CONVERGED_PASS")
        self.assertEqual([c[0] for c in calls], ["R1", "R2", "R1", "R3"])
        self.assertIn("unverified", decision.final_output)

    def test_r3_persistent_epistemic_contradiction_cannot_converge_by_majority(self):
        r1, r2, r3 = cfg("R1", "l1"), cfg("R2", "l2"), cfg("R3", "l3")

        contradicted = {
            "version": TVC_VERSION,
            "correspondence": "NOT_APPLICABLE",
            "coherence": "CONTRADICTED",
            "pragmatic": "VIABLE",
            "semantic": "PRECISE",
            "contradiction_refs": ["artifact:claim-a", "artifact:claim-b"],
            "claims": [],
        }

        def invoke(config, context):
            if config.role == "R1" and context.get("mode") != "SCOPED_CORRECTION":
                return ReviewerResponse("R1", None, "v1")
            if config.role == "R2":
                f = ReviewFinding("f1", "R2", "HIGH", True, "material defect")
                return ReviewerResponse("R2", context["artifact"]["artifact_hash"], "defect", (f,))
            if config.role == "R1":
                return ReviewerResponse("R1", None, "v2")
            return ReviewerResponse(
                "R3",
                context.get("artifact", {}).get("artifact_hash") or context["artifact_hash"],
                "contradiction remains",
                epistemic_review=contradicted,
            )

        decision = ReviewEngine(invoke, qualification_registry=registry(r1, r2, r3)).run(
            ReviewRequest("pf-tvc-r3", "material review", risk="HIGH", materiality="MATERIAL"),
            r1=r1,
            r2=r2,
            r3=r3,
        )
        self.assertEqual(decision.state, "HUMAN_REQUIRED")
        self.assertTrue(any("contradiction" in text.lower() for text in decision.dissent))

    def test_evidence_handle_presence_is_not_source_correspondence_validation(self):
        # Deliberate boundary test: TVC-1 checks structural evidence handles but
        # cannot know that an arbitrary handle actually supports the claim.
        review = {
            "version": TVC_VERSION,
            "correspondence": "SUPPORTED",
            "coherence": "CONSISTENT",
            "pragmatic": "VIABLE",
            "semantic": "PRECISE",
            "contradiction_refs": [],
            "claims": [{
                "claim_id": "c1",
                "text": "Revenue increased 40%.",
                "claim_type": "EMPIRICAL_FACT",
                "correspondence": "SUPPORTED",
                "evidence_refs": ["unverified-handle"],
                "material": True,
            }],
        }
        result = evaluate_truth_contract("R2", review)
        self.assertFalse(any(f.violated_invariant == "TVC-CORRESPONDENCE" for f in result.findings))

    def test_truth_bearer_misclassification_is_not_a_deterministic_semantic_oracle(self):
        # Deliberate boundary test: if a model labels an empirical assertion as
        # an INFERENCE, TVC-1 alone cannot prove the label is wrong. Independent
        # review/source validation remains necessary for stronger assurance.
        review = {
            "version": TVC_VERSION,
            "correspondence": "UNVERIFIED",
            "coherence": "CONSISTENT",
            "pragmatic": "VIABLE",
            "semantic": "PRECISE",
            "contradiction_refs": [],
            "claims": [{
                "claim_id": "c1",
                "text": "The deployment succeeded.",
                "claim_type": "INFERENCE",
                "correspondence": "UNVERIFIED",
                "evidence_refs": [],
                "material": True,
            }],
        }
        result = evaluate_truth_contract("R1", review)
        self.assertFalse(any(f.violated_invariant == "TVC-CORRESPONDENCE" for f in result.findings))

    def test_unanimous_judges_can_be_jointly_wrong_without_triggering_no_ground_truth_alarm(self):
        observations = []
        for i in range(20):
            # Both judges return the same label. With no answer key, the monitor
            # must not invent evidence that this shared label is correct.
            observations.append(JudgeObservation(f"t{i}", "judge-a", "WRONG-BUT-UNKNOWN"))
            observations.append(JudgeObservation(f"t{i}", "judge-b", "WRONG-BUT-UNKNOWN"))
        report = JudgeHealthMonitor(minimum_accuracy_target=0.9, minimum_shared_tasks=20).evaluate(observations)
        self.assertEqual(report.status, "NO_LOGICAL_ALARM")
        self.assertFalse(report.no_alarm_establishes_correctness)


if __name__ == "__main__":
    unittest.main()
