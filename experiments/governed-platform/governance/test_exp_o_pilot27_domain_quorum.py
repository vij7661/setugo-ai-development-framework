import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "runner" / "exp_o_pilot27_domain_quorum.py"
SPEC = importlib.util.spec_from_file_location("exp_o_pilot27_domain_quorum", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

RegisteredRoot = MODULE.RegisteredRoot
VerifiedContribution = MODULE.VerifiedContribution
canonical_statement = MODULE.canonical_statement
evaluate_verified_contributions = MODULE.evaluate_verified_contributions
validate_registry = MODULE.validate_registry


def roots():
    return [
        RegisteredRoot("aws-kms:key-a", "aws", "aws-account:297165774800", "github-oidc:aws-role-a"),
        RegisteredRoot("gcp-kms:key-b", "gcp", "gcp-project:setugo-pilot27-b", "github-wif:gcp-sa-b"),
        RegisteredRoot("azure-kv:key-c", "azure", "azure-subscription:setugo-pilot27-c", "github-oidc:azure-app-c"),
    ]


def c(root, domain, msg, sig=True, identity=True):
    return VerifiedContribution(root, domain, msg, sig, identity)


def test_registry_requires_three_distinct_admin_domains():
    validate_registry(roots())
    bad = roots()
    bad[1] = RegisteredRoot("aws-kms:key-b", "aws", "aws-account:297165774800", "github-oidc:aws-role-b")
    try:
        validate_registry(bad)
        assert False, "same administrative domain must be rejected"
    except ValueError as e:
        assert "administrative domains" in str(e)


def test_registry_rejects_shared_workload_identity():
    bad = roots()
    bad[1] = RegisteredRoot("gcp-kms:key-b", "gcp", "gcp-project:setugo-pilot27-b", "github-oidc:aws-role-a")
    try:
        validate_registry(bad)
        assert False, "shared workload identity must be rejected"
    except ValueError as e:
        assert "workload identity" in str(e)


def test_two_distinct_domains_form_quorum():
    reg = validate_registry(roots())
    msg = canonical_statement(generation=1, root_digest="sha256:" + "11" * 32, nonce="p27")
    q = evaluate_verified_contributions([
        c("aws-kms:key-a", "aws-account:297165774800", msg),
        c("gcp-kms:key-b", "gcp-project:setugo-pilot27-b", msg),
    ], reg, trusted_min_generation=1)
    assert q["quorum"] is True
    assert q["model_authority_effect"] is False
    assert q["authoritative_platform_effect_count"] == 0


def test_same_domain_cannot_double_count_even_if_presented_as_two_keys():
    bad = [
        RegisteredRoot("aws-kms:key-a", "aws", "aws-account:297165774800", "role-a"),
        RegisteredRoot("aws-kms:key-b", "aws", "aws-account:297165774800", "role-b"),
        RegisteredRoot("azure-kv:key-c", "azure", "azure-sub:c", "role-c"),
    ]
    try:
        validate_registry(bad)
        assert False
    except ValueError:
        pass


def test_domain_identity_substitution_is_rejected():
    reg = validate_registry(roots())
    msg = canonical_statement(generation=1, root_digest="sha256:" + "11" * 32, nonce="p27")
    q = evaluate_verified_contributions([
        c("aws-kms:key-a", "gcp-project:setugo-pilot27-b", msg),
        c("gcp-kms:key-b", "gcp-project:setugo-pilot27-b", msg),
    ], reg, trusted_min_generation=1)
    assert q["quorum"] is False
    assert any(x["reason"] == "DOMAIN_BINDING_MISMATCH" for x in q["rejected"])


def test_unverified_provider_identity_is_rejected():
    reg = validate_registry(roots())
    msg = canonical_statement(generation=1, root_digest="sha256:" + "11" * 32, nonce="p27")
    q = evaluate_verified_contributions([
        c("aws-kms:key-a", "aws-account:297165774800", msg),
        c("gcp-kms:key-b", "gcp-project:setugo-pilot27-b", msg, identity=False),
    ], reg, trusted_min_generation=1)
    assert q["quorum"] is False
    assert any(x["reason"] == "PROVIDER_IDENTITY_UNVERIFIED" for x in q["rejected"])


def test_invalid_signature_is_rejected():
    reg = validate_registry(roots())
    msg = canonical_statement(generation=1, root_digest="sha256:" + "11" * 32, nonce="p27")
    q = evaluate_verified_contributions([
        c("aws-kms:key-a", "aws-account:297165774800", msg),
        c("gcp-kms:key-b", "gcp-project:setugo-pilot27-b", msg, sig=False),
    ], reg, trusted_min_generation=1)
    assert q["quorum"] is False
    assert any(x["reason"] == "SIGNATURE_INVALID" for x in q["rejected"])


def test_mixed_statements_do_not_combine():
    reg = validate_registry(roots())
    a = canonical_statement(generation=1, root_digest="sha256:" + "11" * 32, nonce="p27-a")
    b = canonical_statement(generation=1, root_digest="sha256:" + "22" * 32, nonce="p27-b")
    q = evaluate_verified_contributions([
        c("aws-kms:key-a", "aws-account:297165774800", a),
        c("gcp-kms:key-b", "gcp-project:setugo-pilot27-b", b),
    ], reg, trusted_min_generation=1)
    assert q["quorum"] is False


def test_stale_quorum_is_rejected():
    reg = validate_registry(roots())
    msg = canonical_statement(generation=1, root_digest="sha256:" + "11" * 32, nonce="p27")
    q = evaluate_verified_contributions([
        c("aws-kms:key-a", "aws-account:297165774800", msg),
        c("gcp-kms:key-b", "gcp-project:setugo-pilot27-b", msg),
    ], reg, trusted_min_generation=2)
    assert q["quorum"] is False
    assert sum(1 for x in q["rejected"] if x["reason"] == "STALE_GENERATION") == 2


def test_one_domain_outage_retains_liveness_with_other_two():
    reg = validate_registry(roots())
    msg = canonical_statement(generation=2, root_digest="sha256:" + "33" * 32, nonce="p27-g2")
    q = evaluate_verified_contributions([
        c("gcp-kms:key-b", "gcp-project:setugo-pilot27-b", msg),
        c("azure-kv:key-c", "azure-subscription:setugo-pilot27-c", msg),
    ], reg, trusted_min_generation=2)
    assert q["quorum"] is True
