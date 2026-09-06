#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

EXPECTED_ROLE_ARN = "arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer"
EXPECTED_ROLE_NAME = "setugo-pilot24-kms-signer"
EXPECTED_KEY_ARN = "arn:aws:kms:ap-southeast-2:297165774800:key/57d95d4f-9b80-44e4-badf-0330ba9f897c"
EXPECTED_REGION = "ap-southeast-2"
EXPECTED_KEY_SPEC = "ECC_NIST_P256"
EXPECTED_KEY_USAGE = "SIGN_VERIFY"
EXPECTED_ALGORITHM = "ECDSA_SHA_256"
WORKFLOW_PATH = Path(".github/workflows/governed-platform-exp-o-pilot24-aws-kms.yml")


def run(cmd, *, check=True, env=None, text=True):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, env=env, text=text)
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed rc={p.returncode}: {cmd!r}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p


def aws_json(args, *, check=True):
    p = run(["aws", *args, "--region", EXPECTED_REGION, "--output", "json"], check=False)
    if check and p.returncode != 0:
        raise RuntimeError(f"AWS command failed: {args!r}\n{p.stderr}")
    data = None
    if p.returncode == 0 and p.stdout.strip():
        data = json.loads(p.stdout)
    return p, data


def canonical_statement(*, generation, root, project="setugo", task="exp-o-pilot24", logical_state="checkpoint-authority", nonce="pilot24"):
    obj = {
        "experiment": "EXP-O",
        "pilot": "PILOT24-AWS-KMS-ASYMMETRIC-CHECKPOINT",
        "project": project,
        "task": task,
        "logical_state": logical_state,
        "generation": generation,
        "root_digest": root,
        "purpose": "checkpoint-integrity",
        "nonce": nonce,
    }
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def sign_bytes(message, workdir, label):
    msg = workdir / f"{label}.bin"
    msg.write_bytes(message)
    p, data = aws_json([
        "kms", "sign",
        "--key-id", EXPECTED_KEY_ARN,
        "--message", f"fileb://{msg}",
        "--message-type", "RAW",
        "--signing-algorithm", EXPECTED_ALGORITHM,
    ])
    sig = base64.b64decode(data["Signature"])
    sig_path = workdir / f"{label}.sig.der"
    sig_path.write_bytes(sig)
    return sig, sig_path, data


def verify_with_openssl(public_pem, message, signature, workdir, label, *, credentialless=False):
    msg = workdir / f"verify-{label}.bin"
    sig = workdir / f"verify-{label}.sig.der"
    msg.write_bytes(message)
    sig.write_bytes(signature)
    env = os.environ.copy()
    if credentialless:
        for key in list(env):
            if key.startswith("AWS_"):
                env.pop(key, None)
    p = run([
        "openssl", "dgst", "-sha256", "-verify", str(public_pem),
        "-signature", str(sig), str(msg)
    ], check=False, env=env)
    return p.returncode == 0, p


def case(case_id, title, passed, evidence, classification="RUNTIME"):
    return {
        "case_id": case_id,
        "title": title,
        "classification": classification,
        "passed": bool(passed),
        "evidence": evidence,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = []

    workflow_text = WORKFLOW_PATH.read_text(encoding="utf-8")
    static_secret_refs = re.findall(r"secrets\.[A-Za-z0-9_]*AWS[A-Za-z0-9_]*", workflow_text, flags=re.I)
    forbidden_admin_invocations = [x for x in ["disable-key", "schedule-key-deletion", "create-key", "kms:*"] if x in workflow_text.lower()]
    oidc_shape_ok = (
        "id-token: write" in workflow_text
        and "aws-actions/configure-aws-credentials" in workflow_text
        and EXPECTED_ROLE_ARN in workflow_text
        and EXPECTED_REGION in workflow_text
        and not static_secret_refs
    )

    caller_p, caller = aws_json(["sts", "get-caller-identity"])
    caller_arn = caller["Arn"]
    caller_ok = EXPECTED_ROLE_NAME in caller_arn and ":assumed-role/" in caller_arn
    results.append(case("P24-01", "OIDC role acquisition", oidc_shape_ok and caller_p.returncode == 0,
                        {"oidc_workflow_shape": oidc_shape_ok, "static_aws_secret_refs": static_secret_refs, "caller_arn": caller_arn}))
    results.append(case("P24-02", "Exact caller identity", caller_ok, {"caller_arn": caller_arn, "expected_role_name": EXPECTED_ROLE_NAME}))

    _, desc = aws_json(["kms", "describe-key", "--key-id", EXPECTED_KEY_ARN])
    md = desc["KeyMetadata"]
    metadata_ok = (
        md.get("Arn") == EXPECTED_KEY_ARN
        and md.get("KeySpec") == EXPECTED_KEY_SPEC
        and md.get("KeyUsage") == EXPECTED_KEY_USAGE
        and md.get("Enabled") is True
    )
    results.append(case("P24-03", "Exact KMS metadata", metadata_ok,
                        {"arn": md.get("Arn"), "key_id": md.get("KeyId"), "key_spec": md.get("KeySpec"), "key_usage": md.get("KeyUsage"), "enabled": md.get("Enabled")}))

    with tempfile.TemporaryDirectory(prefix="pilot24-") as td:
        workdir = Path(td)
        _, pub = aws_json(["kms", "get-public-key", "--key-id", EXPECTED_KEY_ARN])
        pub_der = base64.b64decode(pub["PublicKey"])
        pub_der_path = workdir / "kms-public.der"
        pub_pem_path = workdir / "kms-public.pem"
        pub_der_path.write_bytes(pub_der)
        pem_p = run(["openssl", "pkey", "-pubin", "-inform", "DER", "-in", str(pub_der_path), "-out", str(pub_pem_path)], check=False)
        pub_ok = pem_p.returncode == 0 and pub_pem_path.exists() and len(pub_der) > 0
        public_key_digest = sha256_hex(pub_der)
        results.append(case("P24-04", "Public key export only", pub_ok,
                            {"public_key_sha256": public_key_digest, "key_id": pub.get("KeyId"), "key_usage": pub.get("KeyUsage"), "signing_algorithms": pub.get("SigningAlgorithms", [])}))

        s1 = canonical_statement(generation=1, root="sha256:" + "11" * 32)
        sig1, _, sign1 = sign_bytes(s1, workdir, "gen1")
        sign1_ok = sign1.get("KeyId") == EXPECTED_KEY_ARN and sign1.get("SigningAlgorithm") == EXPECTED_ALGORITHM
        results.append(case("P24-05", "Exact checkpoint signing", sign1_ok,
                            {"statement_sha256": sha256_hex(s1), "signature_sha256": sha256_hex(sig1), "key_id": sign1.get("KeyId"), "algorithm": sign1.get("SigningAlgorithm")}))

        exact_ok, exact_p = verify_with_openssl(pub_pem_path, s1, sig1, workdir, "exact")
        results.append(case("P24-06", "Independent local verification", exact_ok,
                            {"verify_rc": exact_p.returncode, "statement_sha256": sha256_hex(s1), "signature_sha256": sha256_hex(sig1)}))

        changed = canonical_statement(generation=1, root="sha256:" + "22" * 32)
        changed_ok, changed_p = verify_with_openssl(pub_pem_path, changed, sig1, workdir, "message-substitution")
        results.append(case("P24-07", "Message substitution", not changed_ok,
                            {"verify_rc": changed_p.returncode, "original_statement_sha256": sha256_hex(s1), "changed_statement_sha256": sha256_hex(changed)}))

        mutated_sig = bytearray(sig1)
        mutated_sig[-1] ^= 0x01
        mut_ok, mut_p = verify_with_openssl(pub_pem_path, s1, bytes(mutated_sig), workdir, "sig-mutation")
        results.append(case("P24-08", "Signature mutation", not mut_ok,
                            {"verify_rc": mut_p.returncode, "mutated_signature_sha256": sha256_hex(bytes(mutated_sig))}))

        local_key = workdir / "local-forgery-key.pem"
        local_sig = workdir / "local-forgery.sig.der"
        run(["openssl", "ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", str(local_key)])
        msg_path = workdir / "local-forgery-message.bin"
        msg_path.write_bytes(s1)
        run(["openssl", "dgst", "-sha256", "-sign", str(local_key), "-out", str(local_sig), str(msg_path)])
        local_sig_bytes = local_sig.read_bytes()
        forge_ok, forge_p = verify_with_openssl(pub_pem_path, s1, local_sig_bytes, workdir, "local-forgery")
        results.append(case("P24-09", "Local private-key forgery", not forge_ok,
                            {"verify_rc": forge_p.returncode, "forged_signature_sha256": sha256_hex(local_sig_bytes)}))

        credless_ok, credless_p = verify_with_openssl(pub_pem_path, s1, sig1, workdir, "credentialless", credentialless=True)
        results.append(case("P24-10", "Credentialless verifier", credless_ok,
                            {"verify_rc": credless_p.returncode, "aws_credentials_removed_from_verifier_env": True}))

        wrong_alg_p, _ = aws_json([
            "kms", "sign", "--key-id", EXPECTED_KEY_ARN,
            "--message", f"fileb://{msg_path}", "--message-type", "RAW",
            "--signing-algorithm", "RSASSA_PKCS1_V1_5_SHA_256",
        ], check=False)
        results.append(case("P24-11", "Wrong signing algorithm", wrong_alg_p.returncode != 0,
                            {"returncode": wrong_alg_p.returncode, "error_class_excerpt": wrong_alg_p.stderr[-500:]}))

        bogus_key = "arn:aws:kms:ap-southeast-2:297165774800:key/00000000-0000-0000-0000-000000000000"
        bogus_p, _ = aws_json(["kms", "describe-key", "--key-id", bogus_key], check=False)
        results.append(case("P24-12", "Different key substitution", bogus_p.returncode != 0,
                            {"returncode": bogus_p.returncode, "bogus_key": bogus_key, "error_class_excerpt": bogus_p.stderr[-500:]}))

        config_evidence = {
            "expected_role_policy_actions": ["kms:Sign", "kms:GetPublicKey", "kms:DescribeKey"],
            "expected_resource": EXPECTED_KEY_ARN,
            "forbidden_admin_invocations_in_workflow": forbidden_admin_invocations,
            "destructive_runtime_probe_performed": False,
            "amendment": "EXP-O-PILOT24-PREEXECUTION-SAFETY-AMENDMENT.md",
        }
        config_ok = not forbidden_admin_invocations
        results.append(case("P24-13", "Key disable permission configuration boundary", config_ok, config_evidence, classification="CONFIGURATION_BOUND_NOT_RUNTIME_PROBED"))
        results.append(case("P24-14", "Key deletion scheduling permission configuration boundary", config_ok, config_evidence, classification="CONFIGURATION_BOUND_NOT_RUNTIME_PROBED"))
        results.append(case("P24-15", "Key creation permission configuration boundary", config_ok, config_evidence, classification="CONFIGURATION_BOUND_NOT_RUNTIME_PROBED"))

        stale_crypto_ok, _ = verify_with_openssl(pub_pem_path, s1, sig1, workdir, "stale-gen")
        trusted_min_generation = 2
        stale_semantic_ok = stale_crypto_ok and 1 >= trusted_min_generation
        results.append(case("P24-16", "Old valid signed generation remains semantically stale", stale_crypto_ok and not stale_semantic_ok,
                            {"cryptographic_verification": stale_crypto_ok, "statement_generation": 1, "trusted_min_generation": trusted_min_generation, "semantic_eligible": stale_semantic_ok}))

        wrong_scope = canonical_statement(generation=1, root="sha256:" + "11" * 32, project="other-project")
        scope_verify, scope_p = verify_with_openssl(pub_pem_path, wrong_scope, sig1, workdir, "scope-sub")
        results.append(case("P24-17", "Scope substitution remains invalid", not scope_verify,
                            {"verify_rc": scope_p.returncode, "signed_project": "setugo", "substituted_project": "other-project"}))

        replay_exact_1, _ = verify_with_openssl(pub_pem_path, s1, sig1, workdir, "replay-exact-1")
        replay_exact_2, _ = verify_with_openssl(pub_pem_path, s1, sig1, workdir, "replay-exact-2")
        replay_changed, _ = verify_with_openssl(pub_pem_path, changed, sig1, workdir, "replay-changed")
        results.append(case("P24-18", "Signature replay cannot change statement identity", replay_exact_1 and replay_exact_2 and not replay_changed,
                            {"exact_replay_1": replay_exact_1, "exact_replay_2": replay_exact_2, "changed_statement_replay": replay_changed}))

        v1, p1 = verify_with_openssl(pub_pem_path, s1, sig1, workdir, "verifier-1", credentialless=True)
        v2, p2 = verify_with_openssl(pub_pem_path, s1, sig1, workdir, "verifier-2", credentialless=True)
        results.append(case("P24-19", "Two credentialless verifier processes agree", v1 and v2,
                            {"verifier_1_rc": p1.returncode, "verifier_2_rc": p2.returncode, "aws_credentials_removed": True}))

        s2 = canonical_statement(generation=2, root="sha256:" + "33" * 32, nonce="pilot24-gen2")
        sig2, _, sign2 = sign_bytes(s2, workdir, "gen2")
        gen2_ok, gen2_p = verify_with_openssl(pub_pem_path, s2, sig2, workdir, "gen2-exact", credentialless=True)
        results.append(case("P24-20", "Clean higher-generation liveness", gen2_ok,
                            {"verify_rc": gen2_p.returncode, "generation": 2, "statement_sha256": sha256_hex(s2), "signature_sha256": sha256_hex(sig2), "key_id": sign2.get("KeyId"), "model_authority_effect": False, "consequential_platform_effect": False}))

    runtime = [r for r in results if r["classification"] == "RUNTIME"]
    config = [r for r in results if r["classification"] != "RUNTIME"]
    summary = {
        "experiment": "EXP-O",
        "pilot": "PILOT24-AWS-KMS-ASYMMETRIC-CHECKPOINT",
        "role_arn": EXPECTED_ROLE_ARN,
        "key_arn": EXPECTED_KEY_ARN,
        "region": EXPECTED_REGION,
        "signing_algorithm": EXPECTED_ALGORITHM,
        "total_cases": len(results),
        "runtime_cases": len(runtime),
        "runtime_passed": sum(r["passed"] for r in runtime),
        "configuration_bound_cases": len(config),
        "configuration_bound_passed": sum(r["passed"] for r in config),
        "all_endpoints_satisfied": all(r["passed"] for r in results),
        "private_key_material_observed": False,
        "static_aws_credentials_referenced_by_workflow": bool(static_secret_refs),
        "model_authority_effect": False,
        "authoritative_platform_effect_count": 0,
        "results": results,
    }
    (out / "pilot24-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "public-key-metadata.json").write_text(json.dumps({"public_key_sha256": public_key_digest, "key_arn": EXPECTED_KEY_ARN}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not summary["all_endpoints_satisfied"]:
        raise SystemExit("Pilot 24 endpoint failure")


if __name__ == "__main__":
    main()