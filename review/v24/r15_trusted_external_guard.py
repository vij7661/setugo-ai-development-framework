from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path, PurePosixPath

AUTHORITY_EFFECT="NONE_EVIDENCE_ONLY"
FORBIDDEN={"unittest.py","sitecustomize.py","usercustomize.py"}
SUPPORT=(
    "implementation/v24/V24-I11-V6-INTEGRATED-SUCCESSOR-MANIFEST.json",
    *tuple(f"implementation/v24/V24-I11-V6-R{i}-CONSTRUCTION-EVIDENCE.md" for i in range(1,9)),
    "implementation/v24/V24-I11-V6-R11-EXECUTION-CONTRACT.json",
    "implementation/v24/V24-I11-V6-R12-EXECUTION-CONTRACT.json",
    "implementation/v24/V24-I11-V6-R13-EXECUTION-CONTRACT.json",
    "implementation/v24/V24-I11-V6-R14-EXECUTION-CONTRACT.json",
    "implementation/v24/V24-I11-V6-R15-EXECUTION-CONTRACT.json",
    "implementation/v24/V24-I11-V6-R14-LINEAGE.json",
    "implementation/v24/V24-I11-V6-R14-LINEAGE.md",
    "implementation/v24/V24-I11-V6-R12-CONSTRUCTION-EVIDENCE.md",
)


def canonical(obj: object)->bytes:
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def sha256(data:bytes)->str:return hashlib.sha256(data).hexdigest()
def blob(data:bytes)->str:return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def runtime_contract()->dict:
    flags={"isolated":bool(sys.flags.isolated),"no_site":bool(sys.flags.no_site),"ignore_environment":bool(sys.flags.ignore_environment),"safe_path":bool(sys.flags.safe_path)}
    if any(v is not True for v in flags.values()):raise SystemExit(f"R15_GUARD_INTERPRETER_FLAGS_INVALID:{flags}")
    exe=Path(sys.executable).resolve()
    if not exe.is_file():raise SystemExit("R15_GUARD_INTERPRETER_MISSING")
    r={"flags":flags,"implementation":sys.implementation.name,"cache_tag":sys.implementation.cache_tag,"version":list(sys.version_info),"hexversion":sys.hexversion,"executable_sha256":sha256(exe.read_bytes()),"stdlib_names_digest":sha256(canonical(sorted(sys.stdlib_module_names)))}
    r["contract_digest"]=sha256(canonical(r));return r

def safe(rel:str)->str:
    p=PurePosixPath(rel)
    if not rel or p.is_absolute() or ".." in p.parts or any(x in {"","."} for x in p.parts):raise SystemExit(f"R15_GUARD_UNSAFE_PATH:{rel}")
    return p.as_posix()

def checked(root:Path,rel:str,role:str)->dict:
    rel=safe(rel);p=root/rel
    if p.is_symlink():raise SystemExit(f"R15_GUARD_SYMLINK:{rel}")
    if not p.is_file():raise SystemExit(f"R15_GUARD_FILE_MISSING:{rel}")
    if p.suffix==".py":
        if p.name in FORBIDDEN:raise SystemExit(f"R15_GUARD_BOOTSTRAP_SHADOW:{rel}")
        if p.stem in sys.stdlib_module_names:raise SystemExit(f"R15_GUARD_STDLIB_SHADOW:{rel}")
    data=p.read_bytes();return {"path":rel,"git_blob_sha1":blob(data),"raw_sha256":sha256(data),"bytes":len(data),"role":role}

def source_rows(root:Path)->list[dict]:
    scope=root/"governance-runtime"
    if not scope.is_dir():raise SystemExit("R15_GUARD_RUNTIME_SCOPE_MISSING")
    rows=[]
    for p in sorted(scope.rglob("*")):
        if p.is_symlink():raise SystemExit(f"R15_GUARD_SYMLINK:{p.relative_to(root).as_posix()}")
        if p.is_file():
            rel=p.relative_to(root).as_posix();role="test" if p.name.startswith("test_") and p.suffix==".py" else "runtime"
            rows.append(checked(root,rel,role))
    for rel in SUPPORT:rows.append(checked(root,rel,"support"))
    rows.sort(key=lambda x:x["path"])
    if len({x["path"] for x in rows})!=len(rows):raise SystemExit("R15_GUARD_DUPLICATE_ADMISSION")
    return rows

def load(path:Path)->dict:
    obj=json.loads(path.read_text())
    if obj.get("schema_version")!=4:raise SystemExit("R15_GUARD_PINSET_SCHEMA_INVALID")
    if obj.get("authority_origin")!="EXTERNAL_REVIEW_BRANCH" or obj.get("candidate_self_grant") is not False:raise SystemExit("R15_GUARD_AUTHORITY_INVALID")
    if obj.get("guard_runtime_contract")!=runtime_contract():raise SystemExit("R15_GUARD_RUNTIME_CONTRACT_MISMATCH")
    return obj

def identity(obj:dict,commit:str,tree:str)->None:
    if obj.get("candidate_commit")!=commit:raise SystemExit("R15_GUARD_COMMIT_MISMATCH")
    if obj.get("candidate_tree")!=tree:raise SystemExit("R15_GUARD_TREE_MISMATCH")
    if tuple(obj.get("required_support_files",()))!=SUPPORT:raise SystemExit("R15_GUARD_SUPPORT_SET_MISMATCH")

def build(args):
    root=Path(args.root).resolve();rows=source_rows(root);rt=runtime_contract()
    obj={"schema_version":4,"authority_origin":"EXTERNAL_REVIEW_BRANCH","candidate_self_grant":False,"candidate_commit":args.commit,"candidate_tree":args.tree,"review_commit":args.review_commit,"guard_runtime_contract":rt,"admitted_files":rows,"required_support_files":list(SUPPORT),"scientific_execution_state":"CLOSED_PENDING_SUCCESSOR_REVIEW","authority_effect":AUTHORITY_EFFECT}
    out=Path(args.output);out.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
    print(f"R15_PINSET_FILES={len(rows)}");print(f"R15_PINSET_SHA256={sha256(out.read_bytes())}");print(f"R15_GUARD_RUNTIME_DIGEST={rt['contract_digest']}")
def verify_source(args):
    root=Path(args.root).resolve();obj=load(Path(args.pinset));identity(obj,args.commit,args.tree);actual=source_rows(root)
    if actual!=obj.get("admitted_files"):raise SystemExit("R15_GUARD_SOURCE_BINDING_MISMATCH")
    print(f"R15_SOURCE_BINDING_PASS={len(actual)}")
def stage(args):
    source=Path(args.root).resolve();target=Path(args.target).resolve();obj=load(Path(args.pinset));identity(obj,args.commit,args.tree)
    if target.exists():raise SystemExit("R15_GUARD_STAGE_TARGET_EXISTS")
    target.mkdir(parents=True)
    for row in obj["admitted_files"]:
        now=checked(source,row["path"],row["role"])
        if now!=row:raise SystemExit(f"R15_GUARD_SOURCE_CHANGED:{row['path']}")
        dst=target/row["path"];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/row["path"],dst)
    print("R15_STAGE_PASS")
def sandbox_rows(root:Path)->list[dict]:
    rows=[]
    for p in sorted(root.rglob("*")):
        if p.is_symlink():raise SystemExit(f"R15_GUARD_SANDBOX_SYMLINK:{p.relative_to(root).as_posix()}")
        if p.is_file():
            rel=p.relative_to(root).as_posix();data=p.read_bytes();rows.append({"path":rel,"git_blob_sha1":blob(data),"raw_sha256":sha256(data),"bytes":len(data)})
    return rows
def verify_sandbox(args):
    root=Path(args.root).resolve();obj=load(Path(args.pinset));identity(obj,args.commit,args.tree)
    exp={r["path"]:{k:r[k] for k in ("path","git_blob_sha1","raw_sha256","bytes")} for r in obj["admitted_files"]};act={r["path"]:r for r in sandbox_rows(root)}
    if set(exp)!=set(act):raise SystemExit(f"R15_GUARD_SANDBOX_FILESET_MISMATCH:missing={sorted(set(exp)-set(act))}:extra={sorted(set(act)-set(exp))}")
    for path in sorted(exp):
        if exp[path]!=act[path]:raise SystemExit(f"R15_GUARD_SANDBOX_BINDING_MISMATCH:{path}")
    print(f"R15_SANDBOX_BINDING_PASS={len(act)}")

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("build-pinset");p.add_argument("--root",required=True);p.add_argument("--commit",required=True);p.add_argument("--tree",required=True);p.add_argument("--review-commit",required=True);p.add_argument("--output",required=True);p.set_defaults(fn=build)
    for name,fn in (("verify-source",verify_source),("stage",stage),("verify-sandbox",verify_sandbox)):
        p=sp.add_parser(name);p.add_argument("--root",required=True);p.add_argument("--pinset",required=True);p.add_argument("--commit",required=True);p.add_argument("--tree",required=True)
        if name=="stage":p.add_argument("--target",required=True)
        p.set_defaults(fn=fn)
    a=ap.parse_args();a.fn(a)
if __name__=="__main__":main()
