from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

EXPECTED_BLOBS = {
    "governance-runtime/v24_v6_proof_reference_closure.py": "54c6d5a4ee5139837748fde06778224f2008b0d3",
    "governance-runtime/v24_v6_test_proof_context.py": "f5336d461dc0e83cf17cefb219f5b5f5c915bfbf",
    "governance-runtime/test_v24_v6_proof_reference_closure.py": "bf757f217cc50ca462a6ff3d71b8a885bf70f6f6",
    "governance-runtime/v24_v6_decision_apply.py": "19cd9e52cff3eba33fa2c7a8872b91e9f9a4f30e",
    "governance-runtime/test_v24_v6_decision_apply.py": "962dd05cb9222bf23e5e224f40d5d55e5f5e44e5",
    "governance-runtime/v24_v6_normative_clause_projection.py": "f51a472b7751b3a325224041bf66f746fda92580",
    "governance-runtime/test_v24_v6_normative_clause_projection.py": "4009dbdd60b2cc5a40b7839dd64dc623d3ee21e5",
    "governance-runtime/test_v24_v6_successor3_manual_review_red.py": "4eaeed63e31acbf3a7720a0be00e992757572c02",
}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("utf-8") + data).hexdigest()


def verify_sources() -> None:
    for rel, expected in EXPECTED_BLOBS.items():
        data = (ROOT / rel).read_bytes()
        actual = git_blob_sha(data)
        if actual != expected:
            raise RuntimeError(f"SOURCE_BLOB_MISMATCH:{rel}:{actual}:{expected}")


def replace_once(rel: str, old: str, new: str) -> None:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"REPLACEMENT_COUNT:{rel}:{count}:expected=1")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def repair_prc() -> None:
    rel = "governance-runtime/v24_v6_proof_reference_closure.py"
    replace_once(
        rel,
        "from __future__ import annotations\n\nfrom typing import Any, Mapping\n",
        "from __future__ import annotations\n\nimport os\nfrom typing import Any, Mapping\n",
    )
    replace_once(
        rel,
        'PROOF_REFERENCE_CYCLE_REJECTED = "PROOF_REFERENCE_CYCLE_REJECTED"\n\n_SUPPORTED_KINDS',
        'PROOF_REFERENCE_CYCLE_REJECTED = "PROOF_REFERENCE_CYCLE_REJECTED"\n\n'
        'TRUSTED_BOUNDARY_ANCHOR_ENV = "V24_V6_TRUSTED_BOUNDARY_ANCHOR_SHA256"\n\n'
        '_SUPPORTED_KINDS',
    )
    replace_once(
        rel,
        '''def trusted_boundary_for(context: Mapping[str, Any]) -> dict[str, Any]:
    """Construction helper for tests and frozen successor generation.

    Production authority must bind this boundary outside candidate decision data.
    """
    scope = context.get("genesis_trusted_scope")
    scope_digest = scope.get("scope_digest") if isinstance(scope, Mapping) else None
    return {
        "governance_generation_id": context.get("governance_generation_id"),
        "expected_proof_context_digest": context.get("context_digest"),
        "expected_genesis_scope_digest": scope_digest,
    }
''',
        '''def trusted_boundary_anchor_digest(boundary: Mapping[str, Any]) -> str:
    """Digest exact trusted-boundary material for out-of-band anchoring."""
    return digest(
        {
            "governance_generation_id": boundary.get("governance_generation_id"),
            "expected_proof_context_digest": boundary.get("expected_proof_context_digest"),
            "expected_genesis_scope_digest": boundary.get("expected_genesis_scope_digest"),
        }
    )
''',
    )
    replace_once(
        rel,
        '''    if not _is_sha256(expected_scope_digest):
        problems.append("TRUSTED_GENESIS_SCOPE_DIGEST_INVALID")

    if not isinstance(proof_context, Mapping):
''',
        '''    if not _is_sha256(expected_scope_digest):
        problems.append("TRUSTED_GENESIS_SCOPE_DIGEST_INVALID")
    external_anchor = os.environ.get(TRUSTED_BOUNDARY_ANCHOR_ENV)
    if not _is_sha256(external_anchor):
        problems.append("TRUSTED_PROOF_BOUNDARY_EXTERNAL_ANCHOR_REQUIRED")
    elif trusted_boundary_anchor_digest(trusted_boundary) != external_anchor:
        problems.append("TRUSTED_PROOF_BOUNDARY_EXTERNAL_ANCHOR_MISMATCH")

    if not isinstance(proof_context, Mapping):
''',
    )

    rel = "governance-runtime/v24_v6_test_proof_context.py"
    replace_once(
        rel,
        "from __future__ import annotations\n\nfrom typing import Any, Mapping\n",
        "from __future__ import annotations\n\nimport os\nfrom typing import Any, Mapping\n",
    )
    replace_once(
        rel,
        '''    INDEPENDENCE_QUALIFICATION,
    seal_proof_context,
    trusted_boundary_for,
)''',
        '''    INDEPENDENCE_QUALIFICATION,
    TRUSTED_BOUNDARY_ANCHOR_ENV,
    seal_proof_context,
    trusted_boundary_anchor_digest,
)''',
    )
    replace_once(
        rel,
        '''def build_test_proof_context(
    specs: Mapping[str, Mapping[str, Any]],
''',
        '''def _trusted_boundary_for_test(context: Mapping[str, Any]) -> dict[str, Any]:
    scope = context.get("genesis_trusted_scope")
    scope_digest = scope.get("scope_digest") if isinstance(scope, Mapping) else None
    boundary = {
        "governance_generation_id": context.get("governance_generation_id"),
        "expected_proof_context_digest": context.get("context_digest"),
        "expected_genesis_scope_digest": scope_digest,
    }
    os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = trusted_boundary_anchor_digest(boundary)
    return boundary


def build_test_proof_context(
    specs: Mapping[str, Mapping[str, Any]],
''',
    )
    replace_once(
        rel,
        "    return context, trusted_boundary_for(context), refs\n",
        "    return context, _trusted_boundary_for_test(context), refs\n",
    )

    rel = "governance-runtime/test_v24_v6_proof_reference_closure.py"
    replace_once(
        rel,
        "import copy\nimport unittest\n",
        "import copy\nimport os\nimport unittest\n",
    )
    replace_once(
        rel,
        '''    PROOF_REFERENCE_CLOSED,
    close_governance_dependencies,
''',
        '''    PROOF_REFERENCE_CLOSED,
    TRUSTED_BOUNDARY_ANCHOR_ENV,
    close_governance_dependencies,
''',
    )
    replace_once(
        rel,
        '''    seal_proof_context,
    trusted_boundary_for,
    validate_proof_context,
)''',
        '''    seal_proof_context,
    trusted_boundary_anchor_digest,
    validate_proof_context,
)''',
    )
    replace_once(
        rel,
        '''D9 = "9" * 64


def seal(record: dict, field: str) -> dict:
''',
        '''D9 = "9" * 64


def anchored_boundary_for(context: dict) -> dict:
    scope = context["genesis_trusted_scope"]
    boundary = {
        "governance_generation_id": context["governance_generation_id"],
        "expected_proof_context_digest": context["context_digest"],
        "expected_genesis_scope_digest": scope["scope_digest"],
    }
    os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = trusted_boundary_anchor_digest(boundary)
    return boundary


def seal(record: dict, field: str) -> dict:
''',
    )
    replace_once(
        rel,
        "    return context, trusted_boundary_for(context), {\n",
        "    return context, anchored_boundary_for(context), {\n",
    )
    replace_once(
        rel,
        "    return context, trusted_boundary_for(context)\n",
        "    return context, anchored_boundary_for(context)\n",
    )
    replace_once(
        rel,
        '''        fake_candidate = {
            "governance_proof_context": context,
            "trusted_boundary": trusted_boundary_for(context),
        }
''',
        '''        fake_candidate = {
            "governance_proof_context": context,
            "trusted_boundary": {
                "governance_generation_id": context["governance_generation_id"],
                "expected_proof_context_digest": context["context_digest"],
                "expected_genesis_scope_digest": context["genesis_trusted_scope"]["scope_digest"],
            },
        }
''',
    )


def repair_da1() -> None:
    rel = "governance-runtime/v24_v6_decision_apply.py"
    replace_once(
        rel,
        '''def decision_binding_material(decision: Mapping[str, Any]) -> dict[str, Any]:
    return {key: decision.get(key) for key in LOAD_BEARING_BINDINGS}


def _binding_drift''',
        '''def decision_binding_material(decision: Mapping[str, Any]) -> dict[str, Any]:
    return {key: decision.get(key) for key in LOAD_BEARING_BINDINGS}


DECISION_CONTENT_BINDINGS = tuple(
    key for key in LOAD_BEARING_BINDINGS if key != "predicate_coverage_qualification_digest"
)


def canonical_decision_content_digest(decision: Mapping[str, Any]) -> str:
    return digest(
        {
            "decision_id": decision.get("decision_id"),
            "decision_context_digest": decision.get("decision_context_digest"),
            "endpoint_projection_id": decision.get("endpoint_projection_id"),
            "endpoint_projection_digest": decision.get("endpoint_projection_digest"),
            "predicate_coverage_id": decision.get("predicate_coverage_id"),
            "predicate_coverage_content_digest": decision.get("predicate_coverage_content_digest"),
            "selected_endpoint_state": decision.get("selected_endpoint_state"),
            "authorized_effect_path_id": decision.get("authorized_effect_path_id"),
            "authorized_effect_path_content_digest": decision.get(
                "authorized_effect_path_content_digest"
            ),
            "authorized_effect_class_id": decision.get("authorized_effect_class_id"),
            "load_bearing_bindings": {
                key: decision.get(key) for key in DECISION_CONTENT_BINDINGS
            },
        }
    )


def _binding_drift''',
    )
    replace_once(
        rel,
        '''        "decision_id",
        "endpoint_projection_id",
        "predicate_coverage_id",
    ):
''',
        '''        "decision_id",
        "endpoint_projection_id",
        "predicate_coverage_id",
        "authorized_effect_path_id",
        "authorized_effect_class_id",
    ):
''',
    )
    replace_once(
        rel,
        '''        "decision_digest",
        "decision_qualification_digest",
''',
        '''        "decision_digest",
        "decision_context_digest",
        "authorized_effect_path_content_digest",
        "decision_qualification_digest",
''',
    )
    replace_once(
        rel,
        '''        if not _sha(decision.get(key)):
            p.append(f"DECISION_PROOF_DIGEST_INVALID:{key}")
    return sorted(set(p))
''',
        '''        if not _sha(decision.get(key)):
            p.append(f"DECISION_PROOF_DIGEST_INVALID:{key}")
    expected = canonical_decision_content_digest(decision)
    if _sha(decision.get("decision_digest")) and decision.get("decision_digest") != expected:
        p.append("DECISION_CONTENT_DIGEST_MISMATCH")
    return sorted(set(p))
''',
    )
    replace_once(
        rel,
        '''                "subject_id": decision.get("decision_id"),
                "subject_content_digest": decision.get("decision_digest"),
''',
        '''                "subject_id": decision.get("decision_id"),
                "subject_content_digest": canonical_decision_content_digest(decision),
''',
    )
    replace_once(
        rel,
        '''        if effect_path.get("material_surface_membership_digest") != snapshot.get("material_surface_digest"):
            p.append("MATERIAL_EFFECT_PATH_SURFACE_BINDING_MISMATCH")

    if active_decision.get("selected_endpoint_state") != "ALLOW":
''',
        '''        if effect_path.get("material_surface_membership_digest") != snapshot.get("material_surface_digest"):
            p.append("MATERIAL_EFFECT_PATH_SURFACE_BINDING_MISMATCH")
        if effect_path.get("path_id") != active_decision.get("authorized_effect_path_id"):
            p.append("DECISION_EFFECT_PATH_ID_BINDING_MISMATCH")
        if effect_path.get("path_content_digest") != active_decision.get(
            "authorized_effect_path_content_digest"
        ):
            p.append("DECISION_EFFECT_PATH_CONTENT_BINDING_MISMATCH")
        if effect_path.get("effect_class_id") != active_decision.get(
            "authorized_effect_class_id"
        ):
            p.append("DECISION_EFFECT_CLASS_BINDING_MISMATCH")

    if active_decision.get("selected_endpoint_state") != "ALLOW":
''',
    )
    replace_once(
        rel,
        '''        "decision_context_digest": active_decision.get("decision_context_digest"),
        "endpoint_projection_digest": active_decision.get("endpoint_projection_digest"),
''',
        '''        "decision_context_digest": active_decision.get("decision_context_digest"),
        "authorized_effect_path_id": active_decision.get("authorized_effect_path_id"),
        "authorized_effect_path_content_digest": active_decision.get(
            "authorized_effect_path_content_digest"
        ),
        "authorized_effect_class_id": active_decision.get("authorized_effect_class_id"),
        "endpoint_projection_digest": active_decision.get("endpoint_projection_digest"),
''',
    )

    rel = "governance-runtime/test_v24_v6_decision_apply.py"
    replace_once(
        rel,
        '''    REEVALUATION_REQUIRED,
    canonical_snapshot_digest,
''',
        '''    REEVALUATION_REQUIRED,
    canonical_decision_content_digest,
    canonical_snapshot_digest,
''',
    )
    replace_once(rel, '        "decision_digest":DB,\n', '        "decision_digest":"",\n')
    replace_once(
        rel,
        '''        "selected_endpoint_state":"ALLOW",
        **{k:s[k] for k in (
''',
        '''        "selected_endpoint_state":"ALLOW",
        "authorized_effect_path_id":"PATH-1",
        "authorized_effect_path_content_digest":PATHCONTENT,
        "authorized_effect_class_id":"WRITE",
        **{k:s[k] for k in (
''',
    )
    replace_once(
        rel,
        '''    d.update(overrides)
    return d
''',
        '''    d.update(overrides)
    d["decision_digest"]=canonical_decision_content_digest(d)
    return d
''',
    )
    replace_once(
        rel,
        '''    src=b["snapshot_source"];snap=b["current_snapshot"];dec=b["decision"];effect=b["material_effect_path"]
    old_snapshot_digest=snap.get("snapshot_digest")
    specs={
''',
        '''    src=b["snapshot_source"];snap=b["current_snapshot"];dec=b["decision"];effect=b["material_effect_path"]
    old_snapshot_digest=snap.get("snapshot_digest")
    dec["decision_digest"]=canonical_decision_content_digest(dec)
    rd=b.get("reevaluated_decision")
    if isinstance(rd,dict):
        rd["decision_digest"]=canonical_decision_content_digest(rd)
    specs={
''',
    )
    replace_once(rel, '    rd=b.get("reevaluated_decision")\n    if isinstance(rd,dict):\n', '    if isinstance(rd,dict):\n')
    replace_once(
        rel,
        '        rd=decision(s,decision_digest="d"*64,endpoint_projection_digest="c"*64,source_snapshot_digest=s["snapshot_digest"])\n',
        '        rd=decision(s,endpoint_projection_digest="c"*64,source_snapshot_digest=s["snapshot_digest"])\n',
    )
    replace_once(
        rel,
        '        r=evaluate(b);self.assertTrue(r["allowed"],r["problems"]);self.assertTrue(r["re_evaluated"]);self.assertEqual(r["active_decision_digest"],"d"*64)\n',
        '        r=evaluate(b);self.assertTrue(r["allowed"],r["problems"]);self.assertTrue(r["re_evaluated"]);self.assertEqual(r["active_decision_digest"],rd["decision_digest"])\n',
    )
    replace_once(
        rel,
        '        b["reevaluated_decision"]=decision(s,decision_digest="d"*64,endpoint_projection_digest="c"*64,source_snapshot_digest=D1)\n',
        '        b["reevaluated_decision"]=decision(s,endpoint_projection_digest="c"*64,source_snapshot_digest=D1)\n',
    )


def repair_ncp1() -> None:
    rel = "governance-runtime/v24_v6_normative_clause_projection.py"
    replace_once(
        rel,
        '''def validate_catalog_candidate_coverage(
    bundle: Mapping[str, Any],
''',
        '''def canonical_catalog_control_binding_digest(descriptor: Mapping[str, Any]) -> str:
    return digest(
        {
            "candidate_clause_id": descriptor.get("candidate_clause_id"),
            "control_id": descriptor.get("control_id"),
            "artifact_sha256": descriptor.get("artifact_sha256"),
            "normative_artifact_blob_sha": descriptor.get("normative_artifact_blob_sha"),
            "candidate_span_digest": descriptor.get("candidate_span_digest"),
        }
    )


def validate_catalog_candidate_coverage(
    bundle: Mapping[str, Any],
''',
    )
    replace_once(
        rel,
        '''        cid = descriptor.get("candidate_clause_id")
        if not _nonempty(cid):
''',
        '''        cid = descriptor.get("candidate_clause_id")
        control_id = descriptor.get("control_id")
        if not _nonempty(control_id):
            p.append("NORMATIVE_CATALOG_CONTROL_ID_REQUIRED")
        binding_id = descriptor.get("control_binding_id")
        if not _nonempty(binding_id):
            p.append(f"NORMATIVE_CATALOG_CONTROL_BINDING_ID_REQUIRED:{control_id}")
        if not _nonempty(cid):
''',
    )
    replace_once(
        rel,
        '''        by_candidate.setdefault(cid, []).append(descriptor)
        if descriptor.get("artifact_sha256") != artifact_sha:
''',
        '''        by_candidate.setdefault(cid, []).append(descriptor)
        binding_digest = canonical_catalog_control_binding_digest(descriptor)
        supplied_binding_digest = descriptor.get("control_binding_content_digest")
        if supplied_binding_digest != binding_digest:
            p.append(f"NORMATIVE_CATALOG_CONTROL_BINDING_DIGEST_MISMATCH:{control_id}")
        binding_q = descriptor.get("control_binding_qualification_digest")
        if not _sha(binding_q):
            p.append(f"NORMATIVE_CATALOG_CONTROL_BINDING_QUALIFICATION_REQUIRED:{control_id}")
        _close(
            [
                {
                    "kind": GOVERNED_QUALIFICATION,
                    "reference_digest": binding_q,
                    "subject_id": binding_id,
                    "subject_content_digest": binding_digest,
                }
            ],
            proof_context=proof_context,
            trusted_boundary=trusted_boundary,
            prefix=f"NORMATIVE_CATALOG_CONTROL_BINDING_PROOF:{control_id}",
            problems=p,
        )
        if descriptor.get("control_binding_qualification_state") not in (None, QUALIFIED):
            p.append(f"NORMATIVE_CATALOG_CONTROL_BINDING_NOT_QUALIFIED:{control_id}")
        if descriptor.get("artifact_sha256") != artifact_sha:
''',
    )

    rel = "governance-runtime/test_v24_v6_normative_clause_projection.py"
    replace_once(
        rel,
        '''    canonical_authority_set_content_digest,
    canonical_disposition_content_digest,
''',
        '''    canonical_authority_set_content_digest,
    canonical_catalog_control_binding_digest,
    canonical_disposition_content_digest,
''',
    )
    old = '''def coverage_fixture(descriptors=None):
    bundle,_,_,specs,result=disposition_result()
    assert result["qualified"],result["problems"]
    extended=dict(specs)
    extended["disposition_set_q"]={"kind":"QUALIFICATION","subject_id":DISPOSITION_SET_ID,"content_digest":result["disposition_digest"]}
    context,boundary,refs=build_test_proof_context(extended)
    # Earlier proof refs are stable when one final spec is appended.
    result=qualify_normative_dispositions(bundle,proof_context=context,trusted_boundary=boundary)
    assert result["qualified"],result["problems"]
    if descriptors is None:
        mid=result["material_candidate_ids"][0]
        span=next(x["candidate_span_digest"] for x in result["disposition_binding_material"]["candidate_span_digests"] if x["candidate_clause_id"]==mid)
        descriptors=[{
            "control_id":"CTRL-A",
            "candidate_clause_id":mid,
            "artifact_sha256":result["disposition_binding_material"]["artifact_sha256"],
            "normative_artifact_blob_sha":result["disposition_binding_material"]["artifact_git_blob_sha1"],
            "candidate_span_digest":span,
        }]
    coverage={
        "disposition_set_id":DISPOSITION_SET_ID,
        "disposition_digest":result["disposition_digest"],
        "disposition_qualification_digest":refs["disposition_set_q"],
        "disposition_qualification_state":QUALIFIED,
        "disposition_binding_material":result["disposition_binding_material"],
        "material_candidate_ids":result["material_candidate_ids"],
        "artifact_sha256":result["disposition_binding_material"]["artifact_sha256"],
        "artifact_git_blob_sha1":result["disposition_binding_material"]["artifact_git_blob_sha1"],
        "catalog_descriptors":descriptors,
    }
    return coverage,context,boundary,result
'''
    new = '''def coverage_fixture(descriptors=None):
    bundle,_,_,specs,result=disposition_result()
    assert result["qualified"],result["problems"]
    extended=dict(specs)
    extended["disposition_set_q"]={"kind":"QUALIFICATION","subject_id":DISPOSITION_SET_ID,"content_digest":result["disposition_digest"]}
    if descriptors is None:
        mid=result["material_candidate_ids"][0]
        span=next(x["candidate_span_digest"] for x in result["disposition_binding_material"]["candidate_span_digests"] if x["candidate_clause_id"]==mid)
        descriptors=[{
            "control_id":"CTRL-A",
            "candidate_clause_id":mid,
            "artifact_sha256":result["disposition_binding_material"]["artifact_sha256"],
            "normative_artifact_blob_sha":result["disposition_binding_material"]["artifact_git_blob_sha1"],
            "candidate_span_digest":span,
        }]
    descriptors=[dict(d) for d in descriptors]
    for index,descriptor in enumerate(descriptors,1):
        descriptor.setdefault("control_binding_id",f"CLAUSE-CONTROL-BINDING-{index}")
        descriptor["control_binding_content_digest"]=canonical_catalog_control_binding_digest(descriptor)
        extended[f"control_binding_{index}_q"]={"kind":"QUALIFICATION","subject_id":descriptor["control_binding_id"],"content_digest":descriptor["control_binding_content_digest"]}
    context,boundary,refs=build_test_proof_context(extended)
    # Earlier proof refs remain deterministic when binding proofs are appended.
    result=qualify_normative_dispositions(bundle,proof_context=context,trusted_boundary=boundary)
    assert result["qualified"],result["problems"]
    for index,descriptor in enumerate(descriptors,1):
        descriptor["control_binding_qualification_digest"]=refs[f"control_binding_{index}_q"]
        descriptor["control_binding_qualification_state"]=QUALIFIED
    coverage={
        "disposition_set_id":DISPOSITION_SET_ID,
        "disposition_digest":result["disposition_digest"],
        "disposition_qualification_digest":refs["disposition_set_q"],
        "disposition_qualification_state":QUALIFIED,
        "disposition_binding_material":result["disposition_binding_material"],
        "material_candidate_ids":result["material_candidate_ids"],
        "artifact_sha256":result["disposition_binding_material"]["artifact_sha256"],
        "artifact_git_blob_sha1":result["disposition_binding_material"]["artifact_git_blob_sha1"],
        "catalog_descriptors":descriptors,
    }
    return coverage,context,boundary,result
'''
    replace_once(rel, old, new)


def strengthen_successor3_regressions() -> None:
    rel = "governance-runtime/test_v24_v6_successor3_manual_review_red.py"
    replace_once(
        rel,
        "from __future__ import annotations\n\nimport unittest\n",
        "from __future__ import annotations\n\nimport copy\nimport os\nimport unittest\n",
    )
    replace_once(
        rel,
        "from v24_v6_proof_reference_closure import resolve_governed_qualification\n",
        '''from v24_v6_proof_reference_closure import (
    TRUSTED_BOUNDARY_ANCHOR_ENV,
    resolve_governed_qualification,
    seal_proof_context,
)
''',
    )
    old = '''    def test_prc1_self_constructed_trusted_boundary_is_rejected(self):
        context, _, refs = proof_bundle()
        scope = context["genesis_trusted_scope"]
        self_built_boundary = {
            "governance_generation_id": context["governance_generation_id"],
            "expected_proof_context_digest": context["context_digest"],
            "expected_genesis_scope_digest": scope["scope_digest"],
        }
        result = resolve_governed_qualification(
            refs["root"],
            context,
            self_built_boundary,
            expected_subject_id="ROOT-VERIFIER",
            expected_subject_content_digest=ROOT_CONTENT,
        )
        self.assertFalse(result["qualified"], result)
'''
    new = '''    def test_prc1_self_constructed_trusted_boundary_is_rejected(self):
        context, _, refs = proof_bundle()
        external_anchor = os.environ.get(TRUSTED_BOUNDARY_ANCHOR_ENV)
        self.assertIsNotNone(external_anchor)
        forged_context = copy.deepcopy(context)
        forged_context["proof_context_id"] = "ATTACKER-CONSTRUCTED-CONTEXT"
        seal_proof_context(forged_context)
        scope = forged_context["genesis_trusted_scope"]
        self_built_boundary = {
            "governance_generation_id": forged_context["governance_generation_id"],
            "expected_proof_context_digest": forged_context["context_digest"],
            "expected_genesis_scope_digest": scope["scope_digest"],
        }
        os.environ[TRUSTED_BOUNDARY_ANCHOR_ENV] = str(external_anchor)
        result = resolve_governed_qualification(
            refs["root"],
            forged_context,
            self_built_boundary,
            expected_subject_id="ROOT-VERIFIER",
            expected_subject_content_digest=ROOT_CONTENT,
        )
        self.assertFalse(result["qualified"], result)
        self.assertTrue(
            any("EXTERNAL_ANCHOR_MISMATCH" in x for x in result["problems"]),
            result,
        )
'''
    replace_once(rel, old, new)


def main() -> None:
    verify_sources()
    repair_prc()
    repair_da1()
    repair_ncp1()
    strengthen_successor3_regressions()
    print("successor-3 exact-source transformation complete")


if __name__ == "__main__":
    main()
