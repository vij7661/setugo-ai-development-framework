from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import unittest

from integrated_governed_mvp_external_side_effect import (
    ExternalSideEffectGateway,
    ReferenceExternalProvider,
    derive_external_idempotency_key,
)
from test_integrated_governed_mvp_slice10_external_side_effect import Slice10ExternalSideEffectTests


class _RevokeAfterIntentGateway(ExternalSideEffectGateway):
    def __init__(self, db_path, provider, authority_ref):
        self._authority_ref = authority_ref
        super().__init__(db_path, provider)

    def _store_intent(self, key, binding):
        created = super()._store_intent(key, binding)
        if created:
            self._authority_ref["authority_status"] = "REVOKED"
        return created


class _BarrierLookupProvider(ReferenceExternalProvider):
    def __init__(self, db_path, *, allowed_targets, barrier):
        self._barrier = barrier
        super().__init__(db_path, allowed_targets=allowed_targets)

    def lookup(self, external_idempotency_key):
        value = super().lookup(external_idempotency_key)
        self._barrier.wait(timeout=5)
        return value


class _SecretExceptionProvider(ReferenceExternalProvider):
    def __init__(self, db_path, *, allowed_targets, secret_value):
        self._secret_value = secret_value
        super().__init__(db_path, allowed_targets=allowed_targets)

    def dispatch(self, request):
        raise RuntimeError(f"provider exception token={self._secret_value}")


class Slice10ManualR3FalsificationTests(unittest.TestCase):
    def setUp(self):
        self.h = Slice10ExternalSideEffectTests(methodName="test_s10_01_exact_lineage_applies_one_bounded_reference_effect")
        self.h.setUp()

    def tearDown(self):
        self.h.tearDown()

    def test_r3_f001_revocation_after_initial_check_before_dispatch_denies(self):
        upstream = self.h._upstream()
        profile = self.h._profile()
        lease = self.h._lease(upstream=upstream, profile=profile)
        authority = self.h._authority()
        request = self.h._request(upstream=upstream, lease=lease)
        provider = ReferenceExternalProvider(self.h.provider_db, allowed_targets={("provider-a", "endpoint-a")})
        gateway = _RevokeAfterIntentGateway(self.h.gateway_db, provider, authority)

        result = gateway.execute(
            upstream_result=upstream,
            lease_result=lease,
            current_profile=profile,
            current_authority=authority,
            side_effect_request=request,
            now_epoch=101,
        )

        self.assertEqual("DENY_AUTHORITY_OR_LEASE", result["state"])
        self.assertEqual(0, provider.dispatch_count())
        self.assertEqual(0, provider.effect_count())

    def test_r3_f002_provider_same_key_concurrency_is_idempotent_without_exception(self):
        barrier = Barrier(2)
        provider = _BarrierLookupProvider(
            self.h.provider_db,
            allowed_targets={("provider-a", "endpoint-a")},
            barrier=barrier,
        )
        request = self.h._request()

        def invoke():
            try:
                return provider.dispatch(request)
            except Exception as exc:  # deliberate falsification capture
                return exc

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: invoke(), range(2)))

        unexpected = [value for value in results if isinstance(value, Exception)]
        self.assertEqual([], unexpected, f"provider same-key race escaped exception(s): {unexpected!r}")
        self.assertEqual(1, provider.effect_count())
        ids = {value["external_effect_id"] for value in results}
        self.assertEqual(1, len(ids))

    def test_r3_f003_external_idempotency_has_pinned_golden_vector(self):
        request = {
            "side_effect_request_id": "golden-request-1",
            "project_id": "golden-project",
            "task_id": "golden-task",
            "effect_id": "golden-effect",
            "terminal_execution_id": "golden-terminal",
            "remote_idempotency_key": "golden-remote-key",
            "credential_lease_id": "golden-lease",
            "credential_profile_id": "golden-profile",
            "provider_id": "golden-provider",
            "endpoint_id": "golden-endpoint",
            "action": "RELEASE",
            "resource_id": "repository:golden-artifact",
            "artifact_sha": "golden-artifact",
            "state_version": 42,
            "payload_digest": "golden-payload-digest",
            "authority_snapshot_hash": "golden-authority-hash",
            "lease_evidence_hash": "golden-lease-evidence-hash",
        }
        self.assertEqual(
            "e78d5bec190554e5042d1910791d261ae3f9d4b598b9c572a0aabe890b511560",
            derive_external_idempotency_key(request),
        )

    def test_r3_f004_secret_bearing_provider_exception_is_governed_and_redacted(self):
        secret = "CLAUDE-R3-SYNTHETIC-SECRET"
        upstream = self.h._upstream()
        profile = self.h._profile()
        lease = self.h._lease(upstream=upstream, profile=profile)
        authority = self.h._authority()
        request = self.h._request(upstream=upstream, lease=lease)
        provider = _SecretExceptionProvider(
            self.h.provider_db,
            allowed_targets={("provider-a", "endpoint-a")},
            secret_value=secret,
        )
        gateway = ExternalSideEffectGateway(self.h.gateway_db, provider)

        result = gateway.execute(
            upstream_result=upstream,
            lease_result=lease,
            current_profile=profile,
            current_authority=authority,
            side_effect_request=request,
            now_epoch=101,
        )

        self.assertEqual("REFERENCE_EFFECT_FAILED", result["state"])
        self.assertNotIn(secret, str(result))
        self.assertNotIn(secret, str(gateway.governed_records()))


if __name__ == "__main__":
    unittest.main()
