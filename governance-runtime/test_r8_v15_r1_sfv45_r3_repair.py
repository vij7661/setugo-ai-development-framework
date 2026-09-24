import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "schemas/governance-r8/v15-r1"
RUNTIME = SCHEMA_ROOT / "runtime-contracts.schema.json"
GCP = SCHEMA_ROOT / "gcp-rvm-2.json"
TRACE = SCHEMA_ROOT / "schema-freeze-traceability.json"
SOURCE_MAP = SCHEMA_ROOT / "schema-provenance-source-map.json"
VALIDATOR = SCHEMA_ROOT / "schema-freeze-validator-contract.json"
SPM = SCHEMA_ROOT / "schema-provenance-manifest-candidate.json"

INT64_MAX = 9223372036854775807
P05_BYTES = '{"max":9223372036854775807,"min":-9223372036854775808}'
P05_SHA = "161a1dcda7bae00f28f0ba32675f218fd4977065d2aa0439cf451c6d066dbbfb"
SEMANTIC_SUCCESSOR = "1fa49fa4adfa6aa47fae68c0f1938083eeb1497f"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_no_stale_materialized_spm_transfers():
    assert not SPM.exists()


def test_p05_uses_semantic_successor_canonical_bytes():
    gcp = load(GCP)
    p05 = next(x for x in gcp["canonical_vectors"] if x["vector_id"] == "GCP-RVM2-P05")
    assert p05["expected_canonical_utf8"] == P05_BYTES
    assert p05["expected_sha256"] == P05_SHA
    assert hashlib.sha256(P05_BYTES.encode("utf-8")).hexdigest() == P05_SHA
    assert "R8-V15-R1-GCP-P05-SEMANTIC-CORRECTION" in p05["source_rules"]


def test_runtime_schema_preserves_exact_int64_maxima():
    raw = RUNTIME.read_text(encoding="utf-8")
    assert "9223372036854776000" not in raw
    assert str(INT64_MAX) in raw


def test_las_authority_root_is_exact_flat_v14_preimage():
    r = load(RUNTIME)["$defs"]["LASAuthorityStateRoot"]
    expected = [
        "semantic_state_sequence",
        "committed_log_prefix_digest",
        "stream_head_map_root",
        "idempotency_ledger_root",
        "authority_state_machine_root",
        "revocation_stream_head",
        "nonce_ledger_head",
        "effect_stream_head",
        "csm5_registry_head",
        "aim4_descriptor_head",
        "any_scope_permission_head",
        "aim_scope_policy_head",
        "resolver_policy_head",
        "resolver_implementation_registry_head",
        "guard_registry_head",
        "configuration_generation",
        "prior_certificate_chain_digest",
    ]
    assert r["x-gcp1-preimage-members"] == expected
    assert r["required"] == expected + ["state_root_digest"]
    assert "semantic_heads" not in r["properties"]


def test_stc_binds_rotation_prepare_and_conditional_semantic_state():
    defs = load(RUNTIME)["$defs"]
    stc = defs["StateTransferCertificate"]
    assert "rotation_prepare_certificate_digest" in stc["required"]
    assert "semantic_state_binding_required" in stc["required"]
    assert "ggs_genesis_state_root" in stc["required"]
    assert "GGSGenesisStateRoot" in defs
    ggs = defs["GGSGenesisStateRoot"]
    assert ggs["x-gcp1-preimage-members"] == [
        "barrier_index",
        "committed_log_prefix_digest",
        "constitution_namespace_root",
        "bootstrap_authorization_root",
        "idempotency_ledger_root",
        "configuration_generation",
        "prior_certificate_chain_digest",
    ]


def test_csm5_uses_resolver_policy_ref_not_embedded_policy():
    csm = load(RUNTIME)["$defs"]["CurrentSemanticModelBundle"]
    assert "resolver_policy_ref" in csm["properties"]
    assert "resolver_policy_ref" in csm["required"]
    assert "resolver_policy" not in csm["properties"]
    assert "resolver_policy" not in csm["required"]


def test_rcs1_suite_identity_is_machine_readable_and_bound():
    defs = load(RUNTIME)["$defs"]
    suite = defs["ResolverConformanceSuite1"]
    expected = {
        "suite_id",
        "suite_version",
        "vector_manifest_digest",
        "vector_generator_implementation_digest",
        "generator_runtime_manifest_digest",
        "input_corpus_digest",
        "expected_result_manifest_digest",
        "execution_harness_digest",
        "required_resolver_runtime_identity_digest",
        "required_resolver_workload_identity_digest",
        "result_schema_digest",
        "suite_digest",
    }
    assert set(suite["required"]) == expected
    evidence = defs["ResolverConformanceEvidence"]
    assert "rcs_suite" in evidence["required"]
    assert evidence["properties"]["rcs_suite"]["$ref"] == "#/$defs/ResolverConformanceSuite1"


def test_dps_effect_class_has_explicit_null_sentinel_semantics():
    dps = load(RUNTIME)["$defs"]["DecisionPresealContext"]
    assert "effect_class" in dps["required"]
    joined = " ".join(dps["x-validator-invariants"])
    assert "null if and only if" in joined
    assert "omission is invalid" in joined


def test_t0_manifest_does_not_invent_bootstrap_authorization_member():
    t0 = load(RUNTIME)["$defs"]["T0SuccessorManifest"]
    assert "bootstrap_authorization_digest" not in t0["properties"]
    assert "bootstrap_authorization_digest" not in t0["required"]
    assert any("reservation certificate" in x for x in t0["x-validator-invariants"])


def test_semantic_successor_and_qualification_reset_are_bound():
    trace = load(TRACE)
    sm = load(SOURCE_MAP)
    assert trace["semantic_candidate_commit"] == SEMANTIC_SUCCESSOR
    assert sm["semantic_candidate_commit"] == SEMANTIC_SUCCESSOR
    assert sm["named_source_refs"]["SRC-GCP-P05-CORRECTION"]["commit"] == SEMANTIC_SUCCESSOR
    assert "SRC-SPG-V2R1-EXTENSION" not in sm["named_source_refs"]
    assert "SRC-SPG-V2R1-VERIFY" not in sm["named_source_refs"]
    assert {"SFV-35", "SFV-36", "SFV-44", "SFV-45"}.issubset(set(trace["final_freeze_blockers"]))


def test_validator_contract_covers_repaired_rules():
    vc = load(VALIDATOR)
    by = {x["id"]: x for x in vc["rules"]}
    assert "RCS-1" in by["SFV-17"]["requirement"]
    assert "effect_class=null" in by["SFV-20"]["requirement"]
    assert "reservation request/certificate" in by["SFV-27"]["requirement"]
    assert "GGSGenesisStateRoot" in by["SFV-29"]["requirement"]
    assert "ROTATION_PREPARE certificate digest" in by["SFV-30"]["requirement"]
    assert "flat v14 member set" in by["SFV-33"]["requirement"]
    assert "R8-V15-R1-GCP-P05-SEMANTIC-CORRECTION" in by["SFV-37"]["source"]
