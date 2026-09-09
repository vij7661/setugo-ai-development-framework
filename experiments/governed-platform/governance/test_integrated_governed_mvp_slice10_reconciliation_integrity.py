from __future__ import annotations

from copy import deepcopy
import unittest

from integrated_governed_mvp_external_side_effect import ExternalSideEffectGateway, SimulatedCrash
from test_integrated_governed_mvp_slice10_external_side_effect import Slice10ExternalSideEffectTests


class Slice10ReconciliationIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.h = Slice10ExternalSideEffectTests(methodName="test_s10_01_exact_lineage_applies_one_bounded_reference_effect")
        self.h.setUp()

    def tearDown(self) -> None:
        self.h.tearDown()

    def test_crash_before_dispatch_never_mutates_provider(self):
        gateway, provider = self.h._new()
        request = self.h._request()
        with self.assertRaises(SimulatedCrash):
            gateway.execute(
                upstream_result=self.h._upstream(),
                lease_result=self.h._lease(),
                current_profile=self.h._profile(),
                current_authority=self.h._authority(),
                side_effect_request=request,
                now_epoch=101,
                crash_point="before_dispatch",
            )
        self.assertEqual(0, provider.dispatch_count())
        self.assertEqual(0, provider.effect_count())

    def test_crash_after_provider_dispatch_leaves_durable_caller_attempt_evidence(self):
        gateway, provider = self.h._new()
        request = self.h._request()
        with self.assertRaises(SimulatedCrash):
            gateway.execute(
                upstream_result=self.h._upstream(),
                lease_result=self.h._lease(),
                current_profile=self.h._profile(),
                current_authority=self.h._authority(),
                side_effect_request=request,
                now_epoch=101,
                crash_point="after_provider_commit_before_local_completion",
            )
        records = gateway.governed_records()
        self.assertTrue(
            any(record.get("external_idempotency_key") == request["external_idempotency_key"] for record in records),
            "durable caller-side attempt evidence must exist even when the process dies after provider commit",
        )
        self.assertEqual(1, provider.effect_count())

    def test_crash_after_dispatch_before_response_recovers_same_effect(self):
        gateway, provider = self.h._new()
        request = self.h._request()
        with self.assertRaises(SimulatedCrash):
            gateway.execute(
                upstream_result=self.h._upstream(),
                lease_result=self.h._lease(),
                current_profile=self.h._profile(),
                current_authority=self.h._authority(),
                side_effect_request=request,
                now_epoch=101,
                crash_point="after_dispatch_before_response",
            )
        self.assertEqual(1, provider.effect_count())
        reopened = ExternalSideEffectGateway(self.h.gateway_db, provider)
        recovered = reopened.recover(
            upstream_result=self.h._upstream(),
            lease_result=self.h._lease(),
            current_profile=self.h._profile(),
            current_authority=self.h._authority(),
            side_effect_request=request,
            now_epoch=102,
        )
        self.assertEqual("RECONCILED_EXISTING_EFFECT", recovered["state"])
        self.assertEqual(1, provider.effect_count())

    def test_crash_after_local_completion_recovers_durable_completion_without_duplicate(self):
        gateway, provider = self.h._new()
        request = self.h._request()
        with self.assertRaises(SimulatedCrash):
            gateway.execute(
                upstream_result=self.h._upstream(),
                lease_result=self.h._lease(),
                current_profile=self.h._profile(),
                current_authority=self.h._authority(),
                side_effect_request=request,
                now_epoch=101,
                crash_point="after_local_completion",
            )
        self.assertEqual(1, provider.effect_count())
        reopened = ExternalSideEffectGateway(self.h.gateway_db, provider)
        recovered = reopened.recover(
            upstream_result=self.h._upstream(),
            lease_result=self.h._lease(),
            current_profile=self.h._profile(),
            current_authority=self.h._authority(),
            side_effect_request=request,
            now_epoch=102,
        )
        self.assertEqual("REFERENCE_EFFECT_REPLAYED", recovered["state"])
        self.assertEqual(1, provider.effect_count())

    def test_reconciliation_rejects_different_slice8_lineage_even_when_effect_exists(self):
        gateway, provider = self.h._new()
        upstream = self.h._upstream()
        lease = self.h._lease(upstream=upstream)
        request = self.h._request(upstream=upstream, lease=lease)
        provider.set_mode("timeout_after_commit")
        unknown = gateway.execute(
            upstream_result=upstream,
            lease_result=lease,
            current_profile=self.h._profile(),
            current_authority=self.h._authority(),
            side_effect_request=request,
            now_epoch=101,
        )
        self.assertEqual("OUTCOME_UNKNOWN_RECONCILE_REQUIRED", unknown["state"])
        tampered_lineage = self.h._upstream(artifact_sha="different-artifact")
        recovered = gateway.recover(
            upstream_result=tampered_lineage,
            lease_result=lease,
            current_profile=self.h._profile(),
            current_authority=self.h._authority(authority_status="REVOKED"),
            side_effect_request=request,
            now_epoch=102,
        )
        self.assertEqual("DENY_UPSTREAM_LINEAGE", recovered["state"])
        self.assertEqual(1, provider.effect_count())

    def test_reconciliation_rejects_different_slice9_lease_identity_even_when_effect_exists(self):
        gateway, provider = self.h._new()
        upstream = self.h._upstream()
        lease = self.h._lease(upstream=upstream)
        request = self.h._request(upstream=upstream, lease=lease)
        provider.set_mode("timeout_after_commit")
        gateway.execute(
            upstream_result=upstream,
            lease_result=lease,
            current_profile=self.h._profile(),
            current_authority=self.h._authority(),
            side_effect_request=request,
            now_epoch=101,
        )
        wrong_lease = deepcopy(lease)
        wrong_lease["bound_lease"]["credential_lease_id"] = "different-lease"
        recovered = gateway.recover(
            upstream_result=upstream,
            lease_result=wrong_lease,
            current_profile=self.h._profile(),
            current_authority=self.h._authority(authority_status="REVOKED"),
            side_effect_request=request,
            now_epoch=102,
        )
        self.assertEqual("DENY_AUTHORITY_OR_LEASE", recovered["state"])
        self.assertEqual(1, provider.effect_count())


if __name__ == "__main__":
    unittest.main()
