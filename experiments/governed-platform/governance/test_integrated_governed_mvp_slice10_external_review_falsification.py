from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import unittest

from test_integrated_governed_mvp_slice10_external_side_effect import Slice10ExternalSideEffectTests


class Slice10ExternalReviewFalsificationTests(unittest.TestCase):
    """Supplemental attacks derived from the external DeepSeek review.

    These tests strengthen already-frozen Slice10 invariants; they do not widen
    the production claim boundary.
    """

    def setUp(self) -> None:
        self.h = Slice10ExternalSideEffectTests(methodName="test_s10_01_exact_lineage_applies_one_bounded_reference_effect")
        self.h.setUp()

    def tearDown(self) -> None:
        self.h.tearDown()

    def test_concurrent_exact_duplicate_never_duplicates_provider_effect_or_throws(self):
        gateway, provider = self.h._new()
        upstream = self.h._upstream()
        profile = self.h._profile()
        lease = self.h._lease(upstream=upstream, profile=profile)
        authority = self.h._authority()
        request = self.h._request(upstream=upstream, lease=lease)
        barrier = Barrier(2)

        def invoke():
            barrier.wait()
            try:
                return gateway.execute(
                    upstream_result=upstream,
                    lease_result=lease,
                    current_profile=profile,
                    current_authority=authority,
                    side_effect_request=request,
                    now_epoch=101,
                )
            except Exception as exc:  # deliberate falsification capture
                return exc

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: invoke(), range(2)))

        unexpected = [value for value in results if isinstance(value, Exception)]
        self.assertEqual([], unexpected, f"concurrent duplicate escaped as exception(s): {unexpected!r}")
        self.assertEqual(1, provider.effect_count(), "same exact intent must never create duplicate provider effects")
        self.assertEqual(1, provider.dispatch_count(), "same exact intent must not issue two mutating dispatches")
        self.assertTrue(
            all(value["state"] in {"REFERENCE_EFFECT_APPLIED", "REFERENCE_EFFECT_REPLAYED", "OUTCOME_UNKNOWN_RECONCILE_REQUIRED"} for value in results),
            results,
        )

    def test_exact_lease_expiry_denies_at_external_invocation_boundary(self):
        gateway, provider = self.h._new()
        upstream = self.h._upstream()
        profile = self.h._profile()
        lease = self.h._lease(upstream=upstream, profile=profile)
        request = self.h._request(upstream=upstream, lease=lease)

        # The frozen reference lease expires at epoch 130. The boundary is
        # half-open: not_before <= now < expires, so equality must deny.
        result = gateway.execute(
            upstream_result=upstream,
            lease_result=lease,
            current_profile=profile,
            current_authority=self.h._authority(),
            side_effect_request=request,
            now_epoch=130,
        )
        self.assertEqual("DENY_AUTHORITY_OR_LEASE", result["state"])
        self.assertEqual(0, provider.dispatch_count())
        self.assertEqual(0, provider.effect_count())


if __name__ == "__main__":
    unittest.main()
