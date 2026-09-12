"""V24 apply-time integration wrapper for the existing durable ExecutionGateway.

Legacy callers remain on ExecutionGateway unchanged.  V24 callers use this
wrapper, whose default delegate is the real durable gateway.  The V24 guard is
checked once before entering the delegate and again at the worker boundary,
which is the last unavoidable point before the external/deterministic effect.
The second receipt and AuthorityApplicationRecord are persisted inside the
existing gateway's durable result envelope.
"""
from __future__ import annotations

from copy import deepcopy
import threading
from typing import Any, Callable, Mapping

from integrated_governed_mvp_execution_gateway import ExecutionGateway, canonical_hash
from v24_apply_guard import evaluate_v24_apply


class V24ApplyBlocked(RuntimeError):
    pass


class V24ExecutionGateway:
    def __init__(
        self,
        db_path: str,
        worker: Callable[[Mapping[str, Any]], Mapping[str, Any]],
        *,
        gateway_factory: Callable[..., Any] = ExecutionGateway,
    ):
        self._business_worker = worker
        self._local = threading.local()
        self._delegate = gateway_factory(db_path, self._guarded_worker)

    @staticmethod
    def _deny(guard: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "state": "V24_APPLY_BLOCKED",
            "reason": "V24 apply-time prerequisites are not current and qualified",
            "v24_guard": deepcopy(dict(guard)),
            "terminal_authority": False,
            "release_completion_authority": False,
        }

    def _guarded_worker(self, effect_request: Mapping[str, Any]) -> Mapping[str, Any]:
        context = getattr(self._local, "v24_apply_context", None)
        if not isinstance(context, Mapping):
            raise V24ApplyBlocked("V24 apply context is missing at worker boundary")
        guard = evaluate_v24_apply(context)
        if not guard.get("allowed", False):
            raise V24ApplyBlocked("V24 apply context became unqualified before effect")

        business_result = deepcopy(dict(self._business_worker(effect_request)))
        application_material = {
            "application_id": "v24-app-" + canonical_hash({
                "effect_id": effect_request.get("effect_id"),
                "guard_receipt_digest": guard.get("guard_receipt_digest"),
            })[:32],
            "decision_digest": context.get("decision_digest"),
            "transition_digest": context.get("transition_digest"),
            "sink_set_digest": context.get("sink_set_digest"),
            "sink_id": context.get("sink_id"),
            "effect_id": effect_request.get("effect_id"),
            "pre_apply_state_digest": context.get("pre_apply_state_digest"),
            "post_apply_state_digest": context.get("expected_post_apply_state_digest"),
            "guarded_writer_id": context.get("guarded_writer_id"),
            "atomic_fencing_result": "DURABLE_GATEWAY_RESULT_COMMIT_REQUIRED",
            "admission_ledger_digest": context.get("current_admission_ledger_digest"),
            "completeness_ledger_digest": context.get("current_completeness_ledger_digest"),
            "governance_generation_id": context.get("governance_generation_id"),
            "v24_guard_receipt_digest": guard.get("guard_receipt_digest"),
        }
        application_material["application_record_digest"] = canonical_hash(application_material)
        return {
            "v24_result_envelope": True,
            "business_result": business_result,
            "v24_guard": deepcopy(dict(guard)),
            "authority_application_record": application_material,
        }

    def execute(self, *, v24_apply_context: Mapping[str, Any], **gateway_kwargs: Any) -> dict[str, Any]:
        precheck = evaluate_v24_apply(v24_apply_context)
        if not precheck.get("allowed", False):
            return self._deny(precheck)
        self._local.v24_apply_context = deepcopy(dict(v24_apply_context))
        try:
            result = self._delegate.execute(**gateway_kwargs)
        except V24ApplyBlocked:
            latest = evaluate_v24_apply(v24_apply_context)
            return self._deny(latest)
        finally:
            if hasattr(self._local, "v24_apply_context"):
                del self._local.v24_apply_context

        envelope = result.get("result") if isinstance(result, Mapping) else None
        if isinstance(envelope, Mapping) and envelope.get("v24_result_envelope") is True:
            out = deepcopy(dict(result))
            out["result"] = deepcopy(envelope.get("business_result"))
            out["v24_guard"] = deepcopy(envelope.get("v24_guard"))
            out["authority_application_record"] = deepcopy(envelope.get("authority_application_record"))
            return out
        return result

    def get_v24_evidence(self, idempotency_key: str) -> dict[str, Any]:
        evidence = self._delegate.get_evidence(idempotency_key)
        return deepcopy(dict(evidence))

    def effect_count(self) -> int:
        return self._delegate.effect_count()
