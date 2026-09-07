from __future__ import annotations

import unittest

from review_engine.review_execution_classification import (
    AUTOMATIC_API,
    EXTERNAL_EVIDENCE_RELAY,
    PLATFORM_AUTO_API_REVIEW,
    PLATFORM_USER_INITIATED_API_REVIEW,
    USER_ATTESTED_EXTERNAL_LLM_REVIEW,
    USER_INITIATED_API,
    USER_PROVIDED_EXTERNAL_CONTENT,
    attest_external_llm_review,
    classify_platform_api_review,
    ingest_user_provided_external_content,
)


class ReviewExecutionClassificationTests(unittest.TestCase):
    def test_auto_mode_is_platform_authenticated_api_review(self):
        result = classify_platform_api_review(automatic=True)
        self.assertEqual(result.review_class, PLATFORM_AUTO_API_REVIEW)
        self.assertEqual(result.transport, AUTOMATIC_API)
        self.assertTrue(result.provider_api_authenticated)
        self.assertTrue(result.can_satisfy_platform_review)

    def test_manual_platform_mode_still_uses_authenticated_api(self):
        result = classify_platform_api_review(automatic=False)
        self.assertEqual(result.review_class, PLATFORM_USER_INITIATED_API_REVIEW)
        self.assertEqual(result.transport, USER_INITIATED_API)
        self.assertEqual(result.initiated_by, "USER_PLATFORM_CONTROL")
        self.assertTrue(result.provider_api_authenticated)
        self.assertTrue(result.can_satisfy_platform_review)

    def test_copy_paste_starts_as_external_content_not_a_review(self):
        result = ingest_user_provided_external_content()
        self.assertEqual(result.review_class, USER_PROVIDED_EXTERNAL_CONTENT)
        self.assertEqual(result.transport, EXTERNAL_EVIDENCE_RELAY)
        self.assertIsNone(result.reported_provider)
        self.assertFalse(result.provider_api_authenticated)
        self.assertFalse(result.can_satisfy_platform_review)

    def test_user_attestation_can_name_source_but_cannot_authenticate_it(self):
        result = attest_external_llm_review(
            ingest_user_provided_external_content(),
            reported_provider="deepseek",
            reported_model="deepseek-reasoner",
        )
        self.assertEqual(result.review_class, USER_ATTESTED_EXTERNAL_LLM_REVIEW)
        self.assertEqual(result.reported_provider, "deepseek")
        self.assertEqual(result.provenance_basis, "USER_ATTESTATION")
        self.assertFalse(result.provider_api_authenticated)
        self.assertFalse(result.can_satisfy_platform_review)

    def test_content_cannot_self_attest_by_reclassification(self):
        external = ingest_user_provided_external_content()
        with self.assertRaises(ValueError):
            attest_external_llm_review(
                attest_external_llm_review(external, reported_provider="kimi"),
                reported_provider="deepseek",
            )


if __name__ == "__main__":
    unittest.main()
