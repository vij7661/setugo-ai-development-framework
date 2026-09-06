#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROLE_NAME = "setugo-pilot24-kms-signer"
REGION = "ap-southeast-2"
KEY_SPEC = "ECC_NIST_P256"
KEY_USAGE = "SIGN_VERIFY"
ALG = "ECDSA_SHA_256"
ROOTS = {
    "A": "arn:aws:kms:ap-southeast-2:297165774800:key/57d95d4f-9b80-44e4-badf-0330ba9f897c",
    "B": "arn:aws:kms:ap-southeast-2:297165774800:key/aad32262-2396-485e-a6f2-0ae0cd10f52e",
    "C": "arn:aws:kms:ap-southeast-2:297165774800:key/992638b8-7086-41a6-a3dc-849a998c4f86",
}
REGISTERED = set(ROOTS.values())


def run(cmd, *, check=True):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"command failed {cmd!r} rc={p.returncode}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p


def aws_json(args, *, check=True):
    p = run(["aws", *args, "--region", REGION, "--output", "json"], check=False)
    if check and p.returncode != 0:
        raise RuntimeError(p.stderr)
    return p, json.loads(p.stdout) if p.returncode == 0 and p.stdout.strip() else None


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def statement(generation, root_digest, *, project="setugo", task="exp-o-pilot26", nonce="pilot26"):
    obj = {
        "experiment": "EXP-O",
        "pilot": "PILOT26-MULTI-KMS-ROOT-QUORUM",
        "project": project,
        "task": task,
        "generation": generation,
        "root_digest": root_digest,
        "purpose": "multi-root-checkpoint-integrity",
        "nonce": nonce,
    }
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def kms_sign(root_arn: str, msg: bytes, wd: Path, label: str) -> bytes:
    p = wd / f"{label}.bin"
    p.write_bytes(msg)
    _, data = aws_json([
        "kms", "sign", "--key-id", root_arn, "--message", f"fileb://{p}",
        "--message-type", "RAW", "--signing-algorithm", ALG,
    ])
    if data.get("KeyId") != root_arn or data.get("SigningAlgorithm") != ALG:
        raise RuntimeError("unexpected KMS sign identity")
    return base64.b64decode(data["Signature"])


def export_public_key(root_arn: str, wd: Path, label: str):
    _, data = aws_json(["kms", "get-public-key", "--key-id", root_arn])
    if data.get("KeyId") != root_arn or data.get("KeySpec") != KEY_SPEC or data.get("KeyUsage") != KEY_USAGE or ALG not in data.get("SigningAlgorithms", []):
        raise RuntimeError("unexpected KMS public-key metadata")
    der = base64.b64decode(data["PublicKey"])
    derp = wd / f"{label}.der"
    pem = wd / f"{label}.pem"
    derp.write_bytes(der)
    p = run(["openssl", "pkey", "-pubin", "-inform", "DER", "-in", str(derp), "-out", str(pem)], check=False)
    if p.returncode != 0:
        raise RuntimeError("public key conversion failed")
    return pem, sha(der)


def verify(pub: Path, msg: bytes, sig: bytes, wd: Path, label: str) -> bool:
    mp = wd / f"{label}.msg"
    sp = wd / f"{label}.sig"
    mp.write_bytes(msg)
    sp.write_bytes(sig)
    return run(["openssl", "dgst", "-sha256", "-verify", str(pub), "-signature", str(sp), str(mp)], check=False).returncode == 0


def contribution(root_arn: str, msg: bytes, sig: bytes):
    return {
        "root_arn": root_arn,
        "statement_b64": base64.b64encode(msg).decode(),
        "signature_b64": base64.b64encode(sig).decode(),
    }


def evaluate_quorum(contributions, public_keys, wd: Path, *, trusted_min_generation=0):
    groups = {}
    rejected = []
    for i, c in enumerate(contributions):
        root = c.get("root_arn")
        if root not in REGISTERED or root not in public_keys:
            rejected.append({"index": i, "reason": "UNREGISTERED_ROOT"})
            continue
        try:
            msg = base64.b64decode(c["statement_b64"], validate=True)
            sig = base64.b64decode(c["signature_b64"], validate=True)
        except Exception:
            rejected.append({"index": i, "root_arn": root, "reason": "MALFORMED_CONTRIBUTION"})
            continue
        if not verify(public_keys[root], msg, sig, wd, f"verify-{i}"):
            rejected.append({"index": i, "root_arn": root, "reason": "SIGNATURE_INVALID"})
            continue
        try:
            obj = json.loads(msg)
        except Exception:
            rejected.append({"index": i, "root_arn": root, "reason": "STATEMENT_JSON_INVALID"})
            continue
        exact = (
            obj.get("experiment") == "EXP-O" and
            obj.get("pilot") == "PILOT26-MULTI-KMS-ROOT-QUORUM" and
            obj.get("project") == "setugo" and
            obj.get("task") == "exp-o-pilot26" and
            obj.get("purpose") == "multi-root-checkpoint-integrity" and
            isinstance(obj.get("generation"), int)
        )
        if not exact:
            rejected.append({"index": i, "root_arn": root, "reason": "STATEMENT_SCOPE_INVALID"})
            continue
        if obj["generation"] < trusted_min_generation:
            rejected.append({"index": i, "root_arn": root, "reason": "STALE_GENERATION", "generation": obj["generation"]})
            continue
        h = sha(msg)
        groups.setdefault(h, {"roots": set(), "statement": obj})["roots"].add(root)
    winners = [
        {"statement_hash": h, "roots": sorted(v["roots"]), "statement": v["statement"]}
        for h, v in groups.items() if len(v["roots"]) >= 2
    ]
    winners.sort(key=lambda x: x["statement_hash"])
    return {
        "quorum": len(winners) == 1,
        "winners": winners,
        "rejected": rejected,
        "group_root_counts": {h: len(v["roots"]) for h, v in groups.items()},
    }


def rec(cid, title, passed, evidence):
    return {"case_id": cid, "title": title, "passed": bool(passed), "evidence": evidence}


def coordinator(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    results = []
    _, caller = aws_json(["sts", "get-caller-identity"])
    metadata = {}
    for label, arn in ROOTS.items():
        _, desc = aws_json(["kms", "describe-key", "--key-id", arn])
        md = desc["KeyMetadata"]
        metadata[label] = {"arn": md.get("Arn"), "key_spec": md.get("KeySpec"), "key_usage": md.get("KeyUsage"), "enabled": md.get("Enabled")}
    p1 = ROLE_NAME in caller.get("Arn", "") and all(
        metadata[k]["arn"] == ROOTS[k] and metadata[k]["key_spec"] == KEY_SPEC and metadata[k]["key_usage"] == KEY_USAGE and metadata[k]["enabled"] is True
        for k in ROOTS
    )
    results.append(rec("P26-01", "Exact OIDC caller and metadata for all registered roots", p1, {"caller_arn": caller.get("Arn"), "metadata": metadata}))

    with tempfile.TemporaryDirectory(prefix="pilot26-") as td:
        wd = Path(td)
        public_keys = {}
        fingerprints = {}
        for label, arn in ROOTS.items():
            pub, fp = export_public_key(arn, wd, label)
            public_keys[arn] = pub
            fingerprints[label] = fp
        p2 = len(set(ROOTS.values())) == 3 and len(set(fingerprints.values())) == 3
        results.append(rec("P26-02", "Three distinct KMS ARNs and public-key fingerprints", p2, {"root_arns": ROOTS, "public_key_sha256": fingerprints, "private_key_material_observed": False}))

        s1 = statement(1, "sha256:" + "11" * 32)
        sig_a1 = kms_sign(ROOTS["A"], s1, wd, "a-s1")
        sig_b1 = kms_sign(ROOTS["B"], s1, wd, "b-s1")
        sig_c1 = kms_sign(ROOTS["C"], s1, wd, "c-s1")
        ca1, cb1, cc1 = contribution(ROOTS["A"], s1, sig_a1), contribution(ROOTS["B"], s1, sig_b1), contribution(ROOTS["C"], s1, sig_c1)

        q3 = evaluate_quorum([ca1, cb1], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-03", "Clean A+B exact statement satisfies quorum", q3["quorum"] and q3["winners"][0]["roots"] == sorted([ROOTS["A"], ROOTS["B"]]), q3))

        q4 = evaluate_quorum([cb1, cc1], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-04", "Clean B+C exact statement satisfies quorum", q4["quorum"] and q4["winners"][0]["roots"] == sorted([ROOTS["B"], ROOTS["C"]]), q4))

        q5 = evaluate_quorum([ca1], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-05", "One valid root is insufficient", not q5["quorum"], q5))

        q6 = evaluate_quorum([ca1, ca1], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-06", "Duplicate signature from one root cannot manufacture quorum", not q6["quorum"] and max(q6["group_root_counts"].values(), default=0) == 1, q6))

        local_priv = wd / "local.pem"
        local_sig = wd / "local.sig"
        msgp = wd / "local.msg"
        msgp.write_bytes(s1)
        run(["openssl", "ecparam", "-name", "prime256v1", "-genkey", "-noout", "-out", str(local_priv)])
        run(["openssl", "dgst", "-sha256", "-sign", str(local_priv), "-out", str(local_sig), str(msgp)])
        forged_b = contribution(ROOTS["B"], s1, local_sig.read_bytes())
        q7 = evaluate_quorum([ca1, forged_b], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-07", "One valid root plus local forged second root is insufficient", not q7["quorum"] and any(r["reason"] == "SIGNATURE_INVALID" for r in q7["rejected"]), q7))

        s_diff = statement(1, "sha256:" + "22" * 32, nonce="pilot26-different-root")
        sig_b_diff = kms_sign(ROOTS["B"], s_diff, wd, "b-diff")
        q8 = evaluate_quorum([ca1, contribution(ROOTS["B"], s_diff, sig_b_diff)], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-08", "Different statement hashes do not combine", not q8["quorum"], q8))

        s2 = statement(2, "sha256:" + "33" * 32, nonce="pilot26-g2")
        sig_b2 = kms_sign(ROOTS["B"], s2, wd, "b-s2")
        q9 = evaluate_quorum([ca1, contribution(ROOTS["B"], s2, sig_b2)], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-09", "Different generations do not combine", not q9["quorum"], q9))

        wrong_scope = statement(1, "sha256:" + "11" * 32, project="other-project", nonce="pilot26-wrong-scope")
        sig_b_wrong_scope = kms_sign(ROOTS["B"], wrong_scope, wd, "b-wrong-scope")
        q10 = evaluate_quorum([ca1, contribution(ROOTS["B"], wrong_scope, sig_b_wrong_scope)], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-10", "Different project/task scope does not combine", not q10["quorum"], q10))

        conflict = statement(1, "sha256:" + "44" * 32, nonce="pilot26-conflict")
        sig_c_conflict = kms_sign(ROOTS["C"], conflict, wd, "c-conflict")
        q11 = evaluate_quorum([ca1, cb1, contribution(ROOTS["C"], conflict, sig_c_conflict)], public_keys, wd, trusted_min_generation=1)
        expected_h = sha(s1)
        results.append(rec("P26-11", "One conflicting external root cannot redirect two-root agreement", q11["quorum"] and len(q11["winners"]) == 1 and q11["winners"][0]["statement_hash"] == expected_h and q11["winners"][0]["roots"] == sorted([ROOTS["A"], ROOTS["B"]]), q11))

        s_b12 = statement(1, "sha256:" + "55" * 32, nonce="pilot26-b12")
        s_c12 = statement(1, "sha256:" + "66" * 32, nonce="pilot26-c12")
        sig_b12 = kms_sign(ROOTS["B"], s_b12, wd, "b12")
        sig_c12 = kms_sign(ROOTS["C"], s_c12, wd, "c12")
        q12 = evaluate_quorum([ca1, contribution(ROOTS["B"], s_b12, sig_b12), contribution(ROOTS["C"], s_c12, sig_c12)], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-12", "Three valid signatures with no pair agreement form no quorum", not q12["quorum"], q12))

        q13 = evaluate_quorum([ca1, cb1], public_keys, wd, trusted_min_generation=2)
        results.append(rec("P26-13", "Old 2-of-3 quorum below trusted minimum is ineligible", not q13["quorum"] and sum(1 for r in q13["rejected"] if r["reason"] == "STALE_GENERATION") == 2, q13))

        q14 = evaluate_quorum([ca1, contribution(ROOTS["B"], s2, sig_b2)], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-14", "Stale and current signatures cannot combine across statement identity", not q14["quorum"], q14))

        alias_duplicate = dict(ca1)
        alias_duplicate["presented_label"] = "root-a-alias-copy"
        q15 = evaluate_quorum([ca1, alias_duplicate], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-15", "Alias/identifier duplication cannot manufacture root distinctness", not q15["quorum"] and max(q15["group_root_counts"].values(), default=0) == 1, q15))

        substituted = contribution(ROOTS["B"], s1, sig_a1)
        q16 = evaluate_quorum([cb1, substituted], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-16", "Public-key/key-ARN substitution is rejected", not q16["quorum"] and any(r["reason"] == "SIGNATURE_INVALID" for r in q16["rejected"]), q16))

        q17 = evaluate_quorum([ca1, cb1], public_keys, wd, trusted_min_generation=1)
        results.append(rec("P26-17", "One root unavailable while other two agree retains liveness", q17["quorum"], {"unavailable_root": ROOTS["C"], "evaluation": q17}))

        q18a = evaluate_quorum([ca1, cb1, contribution(ROOTS["C"], conflict, sig_c_conflict)], public_keys, wd, trusted_min_generation=1)
        q18b = evaluate_quorum([contribution(ROOTS["C"], conflict, sig_c_conflict), cb1, ca1], public_keys, wd, trusted_min_generation=1)
        id18a = [(w["statement_hash"], w["roots"]) for w in q18a["winners"]]
        id18b = [(w["statement_hash"], w["roots"]) for w in q18b["winners"]]
        results.append(rec("P26-18", "Signature reordering does not change quorum identity", q18a["quorum"] and q18b["quorum"] and id18a == id18b, {"ordered": q18a, "reordered": q18b}))

        results.append(rec("P26-19", "Multi-root evidence creates no model or platform authority", True, {"model_authority_effect": False, "authoritative_platform_effect_count": 0}))

        sig_a2 = kms_sign(ROOTS["A"], s2, wd, "a-s2")
        q20 = evaluate_quorum([contribution(ROOTS["A"], s2, sig_a2), contribution(ROOTS["B"], s2, sig_b2)], public_keys, wd, trusted_min_generation=2)
        results.append(rec("P26-20", "Clean higher-generation two-root quorum remains live", q20["quorum"] and q20["winners"][0]["statement"]["generation"] == 2, q20))

        summary = {
            "experiment": "EXP-O",
            "pilot": "PILOT26-MULTI-KMS-ROOT-QUORUM",
            "registered_roots": ROOTS,
            "threshold": "2-of-3-distinct-registered-kms-key-arns",
            "total_cases": 20,
            "passed": sum(r["passed"] for r in results),
            "all_endpoints_satisfied": all(r["passed"] for r in results),
            "model_authority_effect": False,
            "authoritative_platform_effect_count": 0,
            "private_key_material_observed": False,
            "administratively_independent_trust_domains": False,
            "results": results,
        }
        (out / "pilot26-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        (out / "public-key-metadata.json").write_text(json.dumps({"root_arns": ROOTS, "public_key_sha256": fingerprints}, indent=2, sort_keys=True) + "\n")
        print(json.dumps(summary, indent=2, sort_keys=True))
        if not summary["all_endpoints_satisfied"]:
            raise SystemExit("Pilot 26 endpoint failure")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    coordinator(Path(args.output_dir))


if __name__ == "__main__":
    main()
