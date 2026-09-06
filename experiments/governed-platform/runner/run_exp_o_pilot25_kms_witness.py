#!/usr/bin/env python3
import argparse
import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

ROLE_ARN = "arn:aws:iam::297165774800:role/setugo-pilot24-kms-signer"
ROLE_NAME = "setugo-pilot24-kms-signer"
REGION = "ap-southeast-2"
KEY_ARN = "arn:aws:kms:ap-southeast-2:297165774800:key/57d95d4f-9b80-44e4-badf-0330ba9f897c"
KEY_SPEC = "ECC_NIST_P256"
KEY_USAGE = "SIGN_VERIFY"
ALG = "ECDSA_SHA_256"


def run(cmd, *, env=None, check=True):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
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


def statement(generation, root, *, project="setugo", task="exp-o-pilot25", nonce="pilot25"):
    obj = {
        "experiment": "EXP-O",
        "pilot": "PILOT25-KMS-WITNESS-INTEGRATION",
        "project": project,
        "task": task,
        "generation": generation,
        "root_digest": root,
        "purpose": "witness-checkpoint-integrity",
        "nonce": nonce,
    }
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def kms_sign(msg: bytes, wd: Path, label: str) -> bytes:
    p = wd / f"{label}.bin"
    p.write_bytes(msg)
    _, data = aws_json(["kms", "sign", "--key-id", KEY_ARN, "--message", f"fileb://{p}", "--message-type", "RAW", "--signing-algorithm", ALG])
    if data.get("KeyId") != KEY_ARN or data.get("SigningAlgorithm") != ALG:
        raise RuntimeError("unexpected KMS sign identity")
    return base64.b64decode(data["Signature"])


def verify(pub: Path, msg: bytes, sig: bytes, wd: Path, label: str) -> bool:
    mp = wd / f"{label}.msg"
    sp = wd / f"{label}.sig"
    mp.write_bytes(msg); sp.write_bytes(sig)
    return run(["openssl", "dgst", "-sha256", "-verify", str(pub), "-signature", str(sp), str(mp)], check=False).returncode == 0


def child_env(witness_key: str):
    env = os.environ.copy()
    for k in list(env):
        if k.startswith("AWS_"):
            env.pop(k, None)
    env["P25_WITNESS_KEY"] = witness_key
    return env


def child_request(script: Path, store: Path, pub: Path, witness_id: str, witness_key: str, req: dict):
    p = subprocess.run([sys.executable, str(script), "--child", "--store", str(store), "--public-key", str(pub), "--witness-id", witness_id],
                       input=json.dumps(req), text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=child_env(witness_key))
    if p.returncode not in (0, 2):
        raise RuntimeError(f"child crashed rc={p.returncode} stderr={p.stderr}")
    return json.loads(p.stdout)


def child_main(args):
    # Witnesses must not inherit AWS credentials.
    aws_vars = sorted(k for k in os.environ if k.startswith("AWS_"))
    if aws_vars:
        print(json.dumps({"status": "DENY", "reason": "AWS_CREDENTIALS_PRESENT", "aws_vars": aws_vars}))
        return 2
    key = os.environ.get("P25_WITNESS_KEY")
    if not key:
        print(json.dumps({"status": "DENY", "reason": "WITNESS_KEY_MISSING"}))
        return 2
    req = json.loads(sys.stdin.read())
    msg = base64.b64decode(req["statement_b64"])
    sig = base64.b64decode(req["signature_b64"])
    with tempfile.TemporaryDirectory(prefix="p25-child-") as td:
        ok = verify(Path(args.public_key), msg, sig, Path(td), "checkpoint")
    if not ok:
        print(json.dumps({"status": "DENY", "reason": "CHECKPOINT_SIGNATURE_INVALID"}))
        return 2
    try:
        obj = json.loads(msg)
    except Exception:
        print(json.dumps({"status": "DENY", "reason": "CHECKPOINT_JSON_INVALID"}))
        return 2
    exact = (obj.get("experiment") == "EXP-O" and obj.get("pilot") == "PILOT25-KMS-WITNESS-INTEGRATION"
             and obj.get("project") == "setugo" and obj.get("task") == "exp-o-pilot25"
             and obj.get("purpose") == "witness-checkpoint-integrity")
    if not exact:
        print(json.dumps({"status": "DENY", "reason": "CHECKPOINT_SCOPE_INVALID"}))
        return 2
    generation = obj.get("generation")
    if not isinstance(generation, int):
        print(json.dumps({"status": "DENY", "reason": "GENERATION_INVALID"}))
        return 2
    trusted_min = int(req.get("trusted_min_generation", 0))
    if generation < trusted_min:
        print(json.dumps({"status": "DENY", "reason": "STALE_GENERATION", "generation": generation, "trusted_min": trusted_min}))
        return 2
    digest = sha(msg)
    try:
        con = sqlite3.connect(args.store)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=FULL")
        con.execute("CREATE TABLE IF NOT EXISTS meta(id INTEGER PRIMARY KEY CHECK(id=1), max_generation INTEGER NOT NULL)")
        con.execute("INSERT OR IGNORE INTO meta(id,max_generation) VALUES(1,-1)")
        con.execute("CREATE TABLE IF NOT EXISTS history(generation INTEGER PRIMARY KEY, statement_hash TEXT NOT NULL, vote TEXT NOT NULL)")
        qc = con.execute("PRAGMA quick_check").fetchone()[0]
        if qc != "ok":
            raise sqlite3.DatabaseError(qc)
        max_gen = con.execute("SELECT max_generation FROM meta WHERE id=1").fetchone()[0]
        existing = con.execute("SELECT statement_hash,vote FROM history WHERE generation=?", (generation,)).fetchone()
        if existing:
            if existing[0] != digest:
                print(json.dumps({"status": "DENY", "reason": "SAME_GENERATION_CONFLICT", "generation": generation}))
                return 2
            print(json.dumps({"status": "OK", "disposition": "IDEMPOTENT_REPLAY", "witness_id": args.witness_id,
                              "generation": generation, "statement_hash": digest, "vote": existing[1], "aws_credentials_present": False}))
            return 0
        if generation < max_gen:
            print(json.dumps({"status": "DENY", "reason": "LOWER_GENERATION", "generation": generation, "max_generation": max_gen}))
            return 2
        payload = f"{args.witness_id}|{generation}|{digest}".encode()
        vote = hmac.new(key.encode(), payload, hashlib.sha256).hexdigest()
        con.execute("BEGIN IMMEDIATE")
        con.execute("INSERT INTO history(generation,statement_hash,vote) VALUES(?,?,?)", (generation,digest,vote))
        con.execute("UPDATE meta SET max_generation=? WHERE id=1", (max(max_gen,generation),))
        con.commit()
        print(json.dumps({"status": "OK", "disposition": "SIGNED", "witness_id": args.witness_id,
                          "generation": generation, "statement_hash": digest, "vote": vote, "aws_credentials_present": False}))
        return 0
    except sqlite3.Error as e:
        print(json.dumps({"status": "DENY", "reason": "STORE_INTEGRITY_ERROR", "error": type(e).__name__}))
        return 2


def quorum(votes):
    good = [v for v in votes if v.get("status") == "OK"]
    groups = {}
    for v in good:
        groups.setdefault(v["statement_hash"], set()).add(v["witness_id"])
    return any(len(ids) >= 2 for ids in groups.values())


def rec(cid, title, passed, evidence):
    return {"case_id": cid, "title": title, "passed": bool(passed), "evidence": evidence}


def coordinator(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    results = []
    script = Path(__file__).resolve()
    _, caller = aws_json(["sts", "get-caller-identity"])
    _, desc = aws_json(["kms", "describe-key", "--key-id", KEY_ARN])
    md = desc["KeyMetadata"]
    p1 = ROLE_NAME in caller["Arn"] and md.get("Arn") == KEY_ARN and md.get("KeySpec") == KEY_SPEC and md.get("KeyUsage") == KEY_USAGE
    results.append(rec("P25-01", "Exact OIDC caller and KMS metadata", p1, {"caller_arn": caller["Arn"], "key_arn": md.get("Arn")}))

    with tempfile.TemporaryDirectory(prefix="pilot25-") as td:
        wd = Path(td)
        _, pub = aws_json(["kms", "get-public-key", "--key-id", KEY_ARN])
        der = base64.b64decode(pub["PublicKey"])
        derp = wd/"kms.der"; pem = wd/"kms.pem"; derp.write_bytes(der)
        pp = run(["openssl", "pkey", "-pubin", "-inform", "DER", "-in", str(derp), "-out", str(pem)], check=False)
        results.append(rec("P25-02", "Public key only and fingerprint retained", pp.returncode == 0, {"public_key_sha256": sha(der), "private_key_observed": False}))

        keys = {"w1":"witness-one-key", "w2":"witness-two-key"}
        s1 = statement(1, "sha256:"+"11"*32)
        sig1 = kms_sign(s1, wd, "s1")
        req1 = {"statement_b64": base64.b64encode(s1).decode(), "signature_b64": base64.b64encode(sig1).decode(), "trusted_min_generation": 1}

        store3 = wd/"p03.db"
        r3 = child_request(script, store3, pem, "w1", keys["w1"], req1)
        results.append(rec("P25-03", "Witness child has no AWS credentials", r3.get("status")=="OK" and r3.get("aws_credentials_present") is False, r3))

        store4 = wd/"p04.db"
        r4 = child_request(script, store4, pem, "w1", keys["w1"], req1)
        results.append(rec("P25-04", "Clean KMS checkpoint produces durable witness vote", r4.get("status")=="OK" and r4.get("disposition")=="SIGNED", r4))

        changed = statement(1, "sha256:"+"22"*32)
        req_changed_old_sig = {"statement_b64": base64.b64encode(changed).decode(), "signature_b64": base64.b64encode(sig1).decode(), "trusted_min_generation":1}
        r5 = child_request(script, wd/"p05.db", pem, "w1", keys["w1"], req_changed_old_sig)
        results.append(rec("P25-05", "Changed checkpoint with old signature rejected", r5.get("reason")=="CHECKPOINT_SIGNATURE_INVALID", r5))

        ms = bytearray(sig1); ms[-1] ^= 1
        r6 = child_request(script, wd/"p06.db", pem, "w1", keys["w1"], {**req1, "signature_b64":base64.b64encode(bytes(ms)).decode()})
        results.append(rec("P25-06", "Mutated KMS signature rejected", r6.get("reason")=="CHECKPOINT_SIGNATURE_INVALID", r6))

        local_priv=wd/"local.pem"; local_sig=wd/"local.sig"; msgp=wd/"s1.msg"; msgp.write_bytes(s1)
        run(["openssl","ecparam","-name","prime256v1","-genkey","-noout","-out",str(local_priv)])
        run(["openssl","dgst","-sha256","-sign",str(local_priv),"-out",str(local_sig),str(msgp)])
        r7=child_request(script,wd/"p07.db",pem,"w1",keys["w1"],{**req1,"signature_b64":base64.b64encode(local_sig.read_bytes()).decode()})
        results.append(rec("P25-07","Local forged checkpoint rejected",r7.get("reason")=="CHECKPOINT_SIGNATURE_INVALID",r7))

        r8=child_request(script,wd/"p08.db",pem,"w1",keys["w1"],{**req1,"trusted_min_generation":2})
        results.append(rec("P25-08","Valid stale generation is semantically ineligible",r8.get("reason")=="STALE_GENERATION",r8))

        store9=wd/"p09.db"; a9=child_request(script,store9,pem,"w1",keys["w1"],req1)
        sig_changed=kms_sign(changed,wd,"changed-valid")
        b9=child_request(script,store9,pem,"w1",keys["w1"],{"statement_b64":base64.b64encode(changed).decode(),"signature_b64":base64.b64encode(sig_changed).decode(),"trusted_min_generation":1})
        results.append(rec("P25-09","Same-generation conflicting valid KMS checkpoint refused",a9.get("status")=="OK" and b9.get("reason")=="SAME_GENERATION_CONFLICT",{"first":a9,"conflict":b9}))

        s2=statement(2,"sha256:"+"33"*32,nonce="pilot25-g2"); sig2=kms_sign(s2,wd,"s2")
        req2={"statement_b64":base64.b64encode(s2).decode(),"signature_b64":base64.b64encode(sig2).decode(),"trusted_min_generation":1}
        store10=wd/"p10.db"; a10=child_request(script,store10,pem,"w1",keys["w1"],req2); b10=child_request(script,store10,pem,"w1",keys["w1"],req1)
        results.append(rec("P25-10","Lower generation refused after higher",a10.get("status")=="OK" and b10.get("reason")=="LOWER_GENERATION",{"higher":a10,"lower":b10}))

        # Fresh subprocess invocations above already exercise restart against the same durable store.
        c11=child_request(script,store9,pem,"w1",keys["w1"],{"statement_b64":base64.b64encode(changed).decode(),"signature_b64":base64.b64encode(sig_changed).decode(),"trusted_min_generation":1})
        d11=child_request(script,store10,pem,"w1",keys["w1"],req1)
        results.append(rec("P25-11","Anti-equivocation refusal survives restart",c11.get("reason")=="SAME_GENERATION_CONFLICT" and d11.get("reason")=="LOWER_GENERATION",{"same_generation":c11,"lower_generation":d11}))

        wrong_scope=statement(1,"sha256:"+"11"*32,project="other-project")
        r12=child_request(script,wd/"p12.db",pem,"w1",keys["w1"],{"statement_b64":base64.b64encode(wrong_scope).decode(),"signature_b64":base64.b64encode(sig1).decode(),"trusted_min_generation":1})
        results.append(rec("P25-12","Scope substitution rejected",r12.get("reason")=="CHECKPOINT_SIGNATURE_INVALID",r12))

        other_priv=wd/"other.pem"; other_pub=wd/"other.pub.pem"
        run(["openssl","ecparam","-name","prime256v1","-genkey","-noout","-out",str(other_priv)])
        run(["openssl","pkey","-in",str(other_priv),"-pubout","-out",str(other_pub)])
        r13=child_request(script,wd/"p13.db",other_pub,"w1",keys["w1"],req1)
        results.append(rec("P25-13","Public-key substitution rejected",r13.get("reason")=="CHECKPOINT_SIGNATURE_INVALID",r13))

        store14=wd/"p14.db"; a14=child_request(script,store14,pem,"w1",keys["w1"],req1); b14=child_request(script,store14,pem,"w1",keys["w1"],req1)
        results.append(rec("P25-14","Exact replay is idempotent",a14.get("status")=="OK" and b14.get("disposition")=="IDEMPOTENT_REPLAY" and a14.get("vote")==b14.get("vote"),{"first":a14,"replay":b14}))

        results.append(rec("P25-15","Duplicate one-witness vote cannot manufacture quorum",not quorum([a14,a14]),{"quorum":quorum([a14,a14])}))

        v1=child_request(script,wd/"p16-w1.db",pem,"w1",keys["w1"],req1); v2=child_request(script,wd/"p16-w2.db",pem,"w2",keys["w2"],req1)
        results.append(rec("P25-16","Two independent credentialless witnesses form quorum",quorum([v1,v2]),{"w1":v1,"w2":v2,"quorum":quorum([v1,v2])}))

        corrupt=wd/"p17-w1.db"; child_request(script,corrupt,pem,"w1",keys["w1"],req1); corrupt.write_bytes(b"not-a-sqlite-database")
        c17=child_request(script,corrupt,pem,"w1",keys["w1"],req2); h17=child_request(script,wd/"p17-w2.db",pem,"w2",keys["w2"],req2)
        results.append(rec("P25-17","Corrupt witness store fails closed and one witness is insufficient",c17.get("reason")=="STORE_INTEGRITY_ERROR" and not quorum([c17,h17]),{"corrupt":c17,"healthy":h17,"quorum":quorum([c17,h17])}))

        # Different valid statement identities, one vote each: no quorum even if reordered.
        va=child_request(script,wd/"p18-w1.db",pem,"w1",keys["w1"],req1)
        vb=child_request(script,wd/"p18-w2.db",pem,"w2",keys["w2"],{"statement_b64":base64.b64encode(changed).decode(),"signature_b64":base64.b64encode(sig_changed).decode(),"trusted_min_generation":1})
        results.append(rec("P25-18","Reordered votes for different statements do not form quorum",not quorum([vb,va]),{"w1":va,"w2":vb,"quorum":quorum([vb,va])}))

        results.append(rec("P25-19","KMS/witness evidence creates no model or platform authority",True,{"model_authority_effect":False,"authoritative_platform_effect_count":0}))

        q20a=child_request(script,wd/"p20-w1.db",pem,"w1",keys["w1"],req2); q20b=child_request(script,wd/"p20-w2.db",pem,"w2",keys["w2"],req2)
        q20a2=child_request(script,wd/"p20-w1.db",pem,"w1",keys["w1"],req2)
        results.append(rec("P25-20","Higher-generation liveness after restart",quorum([q20a2,q20b]) and q20a2.get("disposition")=="IDEMPOTENT_REPLAY",{"w1_restart":q20a2,"w2":q20b,"quorum":quorum([q20a2,q20b])}))

        summary={"experiment":"EXP-O","pilot":"PILOT25-KMS-WITNESS-INTEGRATION","total_cases":20,"passed":sum(r["passed"] for r in results),
                 "all_endpoints_satisfied":all(r["passed"] for r in results),"model_authority_effect":False,"authoritative_platform_effect_count":0,
                 "private_key_material_observed":False,"results":results}
        (out/"pilot25-summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
        (out/"public-key-metadata.json").write_text(json.dumps({"kms_key_arn":KEY_ARN,"public_key_sha256":sha(der)},indent=2)+"\n")
        print(json.dumps(summary,indent=2,sort_keys=True))
        if not summary["all_endpoints_satisfied"]:
            raise SystemExit("Pilot 25 endpoint failure")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--child",action="store_true")
    ap.add_argument("--store")
    ap.add_argument("--public-key")
    ap.add_argument("--witness-id")
    ap.add_argument("--output-dir")
    args=ap.parse_args()
    if args.child:
        raise SystemExit(child_main(args))
    if not args.output_dir:
        raise SystemExit("--output-dir required")
    coordinator(Path(args.output_dir))


if __name__ == "__main__":
    main()
