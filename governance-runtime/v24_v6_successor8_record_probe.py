from __future__ import annotations

import json
import sys

import v24_v6_decision_apply as decision_apply
import v24_v6_normative_clause_projection as normative_projection
from test_v24_v6_decision_apply import attach_proofs as attach_decision_proofs, bundle as decision_bundle
from test_v24_v6_normative_clause_projection import DISPOSITION_SET_ID, coverage_fixture
from test_v24_v6_proof_reference_closure import ROOT_CONTENT, proof_bundle
from v24_v6_trusted_service_client import request_service


def positive() -> dict:
    context, boundary, refs = proof_bundle()
    return request_service(
        "resolve-governed",
        context=context,
        boundary=boundary,
        reference=refs["root"],
        expected_id="ROOT-VERIFIER",
        expected_digest=ROOT_CONTENT,
    )


def da1() -> dict:
    payload = decision_bundle()
    context, boundary = attach_decision_proofs(payload)
    source = payload["snapshot_source"]
    payload["decision"]["authorized_effect_path_id"] = "PATH-ATTACK"
    payload["material_effect_path"]["path_id"] = "PATH-ATTACK"
    payload["decision"]["decision_digest"] = decision_apply.canonical_decision_content_digest(
        payload["decision"]
    )
    return request_service(
        "evaluate-decision-apply",
        context=context,
        boundary=boundary,
        payload=payload,
        reference=source["qualification_digest"],
        expected_id=source["mechanism_id"],
        expected_digest=source["mechanism_content_digest"],
    )


def ncp1() -> dict:
    payload, context, boundary, _ = coverage_fixture()
    descriptor = payload["catalog_descriptors"][0]
    descriptor["control_id"] = "CTRL-ATTACK"
    descriptor["control_binding_content_digest"] = (
        normative_projection.canonical_catalog_control_binding_digest(descriptor)
    )
    return request_service(
        "validate-normative-coverage",
        context=context,
        boundary=boundary,
        payload=payload,
        reference=payload["disposition_qualification_digest"],
        expected_id=DISPOSITION_SET_ID,
        expected_digest=payload["disposition_digest"],
    )


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"positive", "da1", "ncp1"}:
        raise SystemExit("usage: v24_v6_successor8_record_probe.py positive|da1|ncp1")
    result = {"positive": positive, "da1": da1, "ncp1": ncp1}[sys.argv[1]]()
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
