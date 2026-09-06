"""EXP-O Pilot 14 post-first-run transport hardening.

This versioned test transport adds one preregistered fault schedule:
DELAY_RESPONSE_UNTIL_RELEASE. The request still crosses the original Pilot 14
peer HTTP/authentication/durable-ledger path immediately. Only the already-
generated, already-validated response is withheld from the current quorum
collector. Releasing it later cannot resume a completed authority operation.

The original Pilot 14 implementation remains unchanged so first-run evidence is
not rewritten.
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Mapping

import process_network_quorum_exp_o as base


class HardenedProcessQuorumNode(base.ProcessQuorumNode):
    """Original Pilot 14 node plus delayed-after-generation response scheduling."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.delayed_responses: list[dict[str, Any]] = []

    def _send_peer(
        self,
        peer_id: str,
        message_type: str,
        term: int,
        payload: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        if self._fault(peer_id, message_type) != "DELAY_RESPONSE_UNTIL_RELEASE":
            return super()._send_peer(peer_id, message_type, term, payload)

        # Use the same envelope construction, authenticated HTTP transport,
        # response verification, and response-history path as normal traffic.
        # The peer therefore durably processes the request before the leader's
        # active quorum collector is deprived of the response.
        env = self._make_peer_envelope(peer_id, message_type, term, payload)
        message_id = str(env["core"]["message_id"])
        with self._history_lock:
            self.outbound_history[message_id] = (peer_id, copy.deepcopy(env))

        response = self._post_peer_envelope(peer_id, env)
        if response is not None:
            with self._history_lock:
                self.delayed_responses.append(
                    {
                        "peer_id": peer_id,
                        "message_id": message_id,
                        "response_envelope": copy.deepcopy(response),
                    }
                )
        # The already-generated response is intentionally invisible to the
        # in-progress production quorum collector.
        return []

    def release_delayed(self) -> dict[str, Any]:
        # Preserve the original queued-request behavior used by P14-07/P14-11.
        original = super().release_delayed()
        with self._history_lock:
            response_outcomes = copy.deepcopy(self.delayed_responses)
            self.delayed_responses.clear()
        return {
            **original,
            "released": int(original.get("released", 0)) + len(response_outcomes),
            "response_outcomes": response_outcomes,
        }


class HardenedProcessQuorumClusterHarness(base.ProcessQuorumClusterHarness):
    """Starts the hardening process image; authority still lives in each node."""

    @property
    def script_path(self) -> Path:
        return Path(__file__).resolve()


def main() -> int:
    # base.serve_replica resolves ProcessQuorumNode from its module globals.
    # Swap only inside this hardening process image; importing the original
    # module elsewhere remains unchanged.
    original = base.ProcessQuorumNode
    base.ProcessQuorumNode = HardenedProcessQuorumNode
    try:
        return base.main()
    finally:
        base.ProcessQuorumNode = original


if __name__ == "__main__":
    raise SystemExit(main())
