"""Slice 3 receipt compatibility repair for the Integrated Governed MVP.

This version preserves the accepted Slice 3 mutation mechanism and adds only the
verified lineage fields required by the accepted Slice 4 receipt contract.
It does not widen mutation scope or terminal/release authority.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from integrated_governed_mvp_repository_gateway import RepositoryMutationGateway as V1RepositoryMutationGateway


class RepositoryMutationGateway(V1RepositoryMutationGateway):
    """V1 mutation semantics plus deterministic Slice3→Slice4 receipt lineage."""

    _SUCCESS_STATES = {"COMMITTED", "REPLAYED", "RECOVERED_AND_COMMITTED", "RECOVERED_REPLAY"}

    def mutate(
        self,
        *,
        workspace: str,
        slice2_receipt: Mapping[str, Any],
        effect_contract: Mapping[str, Any],
        action_manifest: Mapping[str, Any],
        patch: Mapping[str, Any],
        crash_at: str | None = None,
    ) -> dict[str, Any]:
        result = super().mutate(
            workspace=workspace,
            slice2_receipt=slice2_receipt,
            effect_contract=effect_contract,
            action_manifest=action_manifest,
            patch=patch,
            crash_at=crash_at,
        )
        if result.get("state") not in self._SUCCESS_STATES:
            return result

        # V1 returns a success only after verifying the Slice 2 receipt and the
        # exact effect contract. Reconstruct the already-authoritative lineage
        # from those same verified inputs rather than accepting caller-supplied
        # replacement identities.
        receipt = deepcopy(dict(slice2_receipt))
        evidence = receipt.get("evidence") if isinstance(receipt, dict) else None
        lineage = evidence.get("capability_lineage") if isinstance(evidence, dict) else None
        slice2_result = receipt.get("result") if isinstance(receipt, dict) else None
        if not isinstance(lineage, Mapping) or not isinstance(slice2_result, Mapping):
            return {
                "state": "BLOCKED_AMBIGUOUS_DURABLE_STATE",
                "reason": "successful Slice 3 result cannot reconstruct verified Slice 2 lineage",
                "authorized": False,
                "terminal_authority": False,
                "release_completion_authority": False,
            }

        project_id = lineage.get("project_id")
        task_id = lineage.get("task_id")
        execution_id = slice2_result.get("effect_id")
        plan_step_id = effect_contract.get("plan_step_id") if isinstance(effect_contract, Mapping) else None
        if not all(isinstance(value, str) and value for value in (project_id, task_id, execution_id, plan_step_id)):
            return {
                "state": "BLOCKED_AMBIGUOUS_DURABLE_STATE",
                "reason": "successful Slice 3 result lacks reconstructable cross-slice lineage",
                "authorized": False,
                "terminal_authority": False,
                "release_completion_authority": False,
            }

        enriched = deepcopy(result)
        enriched.update(
            {
                "project_id": project_id,
                "task_id": task_id,
                "execution_id": execution_id,
                "plan_step_id": plan_step_id,
                "terminal_authority": False,
                "release_completion_authority": False,
            }
        )
        return enriched
