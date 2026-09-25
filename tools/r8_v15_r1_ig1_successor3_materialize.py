#!/usr/bin/env python3
"""IG-1 Successor3 exact-base mechanical materializer and preflight."""
from __future__ import annotations
import argparse
import ast
import json
import pathlib
import posixpath
import subprocess
import sys

PROPOSAL_ROOT=pathlib.Path(__file__).resolve().parent.parent
ALLOW=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"
SUMMARY=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-PREFLIGHT-SUMMARY.json"
BASELINE=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR3-INHERITED-BASELINE-TEST-IDENTITY.json"
ORACLE=PROPOSAL_ROOT/"governance-runtime"/"test_r8_v15_r1_ig1_successor3_integration_oracle.py"
CHILD=PROPOSAL_ROOT/"tools"/"r8_v15_r1_ig1_successor3_unittest_child.py"
BASE="751162ee42c603cb6c84ee12021d16bab6fa626b"
FROZEN_SCHEMA="f93ca26975ecb64f0da13779889c75b36140cdfc"
MANIFEST_PATH="governance-r8/R8-V15-R1-IG1-SUCCESSOR3-INTEGRATED-CANDIDATE-MANIFEST.json"
ALLOWED_SCHEMA_ROOT="schemas/governance-r8/v15-r1"
GOV_ROOT="governance-r8"
FORBIDDEN_READ_ATTRS={"open","read_text","read_bytes","readlink","resolve","iterdir","glob","rglob","walk","listdir","scandir"}
FORBIDDEN_READ_NAMES={"open","listdir","scandir","walk","glob","rglob"}
FORBIDDEN_NAMES={"eval","exec","compile","__import__","globals","locals","vars"}
FORBIDDEN_MODULES={"importlib","pickle","marshal","ctypes","socket","urllib","requests","unittest.mock"}
ALLOWED_IMPORTS={
 "materializer":{"__future__","argparse","ast","json","pathlib","posixpath","subprocess","sys"},
 "oracle":{"__future__","argparse","json","pathlib","subprocess","sys"},
 "child":{"__future__","json","pathlib","sys","unittest"},
}
MACHINERY={
 "materializer":pathlib.Path(__file__).resolve(),
 "oracle":ORACLE,
 "child":CHILD,
}
REJECTED={"20":"053a5c0e70aee45e0e73653d68de3575a83d455c","21":"d3f184380f6cd15582cb3dd6e987895dd895d930","22":"8ecdd17ce80549f87dd15bbe1fc29414272b6253"}
REACCEPTED_IDENTICAL={
 "20":{"governance-runtime/test_r8_v15_r1_implementation_slice20.py"},
 "21":{"governance-runtime/test_r8_v15_r1_implementation_slice21.py"},
 "22":{"governance-runtime/test_r8_v15_r1_implementation_slice22.py"},
}
RESERVED={
 "tools/r8_v15_r1_ig1_successor3_materialize.py",
 "tools/r8_v15_r1_ig1_successor3_unittest_child.py",
 "governance-runtime/test_r8_v15_r1_ig1_successor3_integration_oracle.py",
 ".github/workflows/r8-v15-r1-ig1-successor3-core.yml",
 ".github/workflows/r8-v15-r1-ig1-successor3-activation-gate.yml",
 MANIFEST_PATH,
}

def run(root,*args,check=True):
    p=subprocess.run(args,cwd=root,text=True,capture_output=True)
    if check and p.returncode:
        raise SystemExit(f"FAIL cwd={root} command={args!r}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p

def load_json(path):
    return json.loads(path.read_text())

def ensure_commit(commit):
    if run(PROPOSAL_ROOT,"git","cat-file","-e",commit+"^{commit}",check=False).returncode:
        run(PROPOSAL_ROOT,"git","fetch","--no-tags","origin",commit)
    got=run(PROPOSAL_ROOT,"git","rev-parse",commit+"^{commit}").stdout.strip()
    if got!=commit:
        raise SystemExit(f"FAIL commit identity {commit} -> {got}")

def tree_entry(commit,path):
    out=run(PROPOSAL_ROOT,"git","ls-tree",commit,"--",path).stdout.rstrip("\n")
    if not out:
        return None
    meta,name=out.split("\t",1)
    mode,typ,blob=meta.split()
    return {"path":name,"mode":mode,"type":typ,"blob":blob}

def index_entry(target,path):
    out=run(target,"git","ls-files","-s","--",path).stdout.strip()
    if not out:
        return None
    meta,name=out.splitlines()[0].split("\t",1)
    mode,blob,stage=meta.split()
    return {"path":name,"mode":mode,"type":"blob","blob":blob,"stage":stage}

def dotted_name(node):
    parts=[]
    while isinstance(node,ast.Attribute):
        parts.append(node.attr)
        node=node.value
    if isinstance(node,ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return ""

def assert_machinery_declarative():
    for role,path in MACHINERY.items():
        tree=ast.parse(path.read_text(),filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                for alias in node.names:
                    root=alias.name
                    if root not in ALLOWED_IMPORTS[role]:
                        raise SystemExit(f"FAIL {role} import not allowlisted: {root}")
                    if any(root==m or root.startswith(m+".") for m in FORBIDDEN_MODULES):
                        raise SystemExit(f"FAIL {role} forbidden module import: {root}")
            elif isinstance(node,ast.ImportFrom):
                module=node.module or ""
                root=module
                if root not in ALLOWED_IMPORTS[role]:
                    raise SystemExit(f"FAIL {role} import-from not allowlisted: {root}")
                if any(root==m or root.startswith(m+".") for m in FORBIDDEN_MODULES):
                    raise SystemExit(f"FAIL {role} forbidden module import-from: {root}")
            elif isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in FORBIDDEN_NAMES:
                raise SystemExit(f"FAIL {role} forbidden dynamic call: {node.func.id}")
            elif isinstance(node,ast.Subscript):
                if dotted_name(node.value)=="sys.modules":
                    raise SystemExit(f"FAIL {role} sys.modules access")
            elif isinstance(node,(ast.Attribute,ast.Name)):
                name=dotted_name(node) if isinstance(node,ast.Attribute) else node.id
                if any(name==m or name.startswith(m+".") for m in FORBIDDEN_MODULES):
                    raise SystemExit(f"FAIL {role} forbidden module reference: {name}")
                if name=="monkeypatch" or name.startswith("unittest.mock") or name.startswith("mock.patch"):
                    raise SystemExit(f"FAIL {role} mock/monkeypatch reference: {name}")
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                names=[]
                if isinstance(node,ast.Import):
                    names=[a.name for a in node.names]
                else:
                    names=[node.module or ""]
                if any(name.startswith("r8_v15_r1_") for name in names):
                    raise SystemExit(f"FAIL {role} direct production-validator import")

def norm_path_literal(value):
    if not isinstance(value,str):
        return None
    value=value.replace("\\","/")
    return posixpath.normpath(value)

def classify_literal(value):
    n=norm_path_literal(value)
    if n is None:
        return None
    if n==ALLOWED_SCHEMA_ROOT or n.startswith(ALLOWED_SCHEMA_ROOT+"/"):
        return "SCHEMA"
    if n==GOV_ROOT or n.startswith(GOV_ROOT+"/") or "/governance-r8/" in ("/"+n+"/"):
        return "HISTORY"
    return None

def path_class(node,classes):
    literals=[x.value for x in ast.walk(node) if isinstance(x,ast.Constant) and isinstance(x.value,str)]
    inherited=[classes[x.id] for x in ast.walk(node) if isinstance(x,ast.Name) and x.id in classes]
    has_dotdot=any(".." in s.replace("\\","/").split("/") for s in literals)
    # Traversal is evaluated before any schema allowance.
    if has_dotdot and (any("governance-r8" in s or "schemas" in s for s in literals) or "SCHEMA" in inherited or "HISTORY" in inherited):
        return "HISTORY"
    if "HISTORY" in inherited:
        return "HISTORY"
    # A traversal-free expression that fully constructs the exact allowed schema root is schema access.
    segs=[s.replace("\\","/").strip("/") for s in literals]
    if not has_dotdot and {"schemas","governance-r8","v15-r1"}.issubset(set(segs)):
        return "SCHEMA"
    if "SCHEMA" in inherited and not has_dotdot:
        return "SCHEMA"
    if any(classify_literal(s)=="HISTORY" for s in literals):
        return "HISTORY"
    classes_found={classify_literal(s) for s in literals}
    classes_found.discard(None)
    if classes_found=={"SCHEMA"}:
        return "SCHEMA"
    return None

def forbidden_history_reason(text,path):
    tree=ast.parse(text,filename=path)
    classes={}
    changed=True
    while changed:
        changed=False
        for node in ast.walk(tree):
            if not isinstance(node,(ast.Assign,ast.AnnAssign)) or node.value is None:
                continue
            cls=path_class(node.value,classes)
            if cls is None:
                continue
            targets=node.targets if isinstance(node,ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target,ast.Name) and classes.get(target.id)!=cls:
                    classes[target.id]=cls
                    changed=True
    for node in ast.walk(tree):
        if isinstance(node,ast.Call):
            if isinstance(node.func,ast.Name) and node.func.id in FORBIDDEN_READ_NAMES:
                if any(path_class(arg,classes)=="HISTORY" for arg in node.args):
                    return f"{node.func.id} history read"
            elif isinstance(node.func,ast.Attribute) and node.func.attr in FORBIDDEN_READ_ATTRS:
                if path_class(node.func.value,classes)=="HISTORY":
                    return f"{node.func.attr} history receiver read"
                if any(path_class(arg,classes)=="HISTORY" for arg in node.args):
                    return f"{node.func.attr} history argument read"
        if isinstance(node,ast.BinOp) and isinstance(node.op,ast.Div):
            literals=[x.value for x in ast.walk(node) if isinstance(x,ast.Constant) and isinstance(x.value,str)]
            if any(".." in s.replace("\\","/").split("/") for s in literals) and path_class(node,classes)=="HISTORY":
                return "history traversal path expression"
    return None

def assert_detector_self_tests():
    bad=[
      'from pathlib import Path\np=Path("schemas/governance-r8/v15-r1")/"../../governance-r8/foo"\np.read_text()',
      'from pathlib import Path\nPath("schemas/governance-r8/v15-r1/../../governance-r8/foo").read_text()',
      'import os\nos.listdir("governance-r8")',
      'from pathlib import Path\nPath("governance-r8").glob("*")',
      'from pathlib import Path\nbase=Path("schemas/governance-r8/v15-r1")\n(base/"../../../governance-r8/x").read_bytes()',
    ]
    good=[
      'from pathlib import Path\nPath("schemas/governance-r8/v15-r1/foo.json").read_text()',
      'from pathlib import Path\nbase=Path("schemas")/"governance-r8"/"v15-r1"\n(base/"foo.json").read_text()',
    ]
    for i,src in enumerate(bad,1):
        if forbidden_history_reason(src,f"<bad-{i}>") is None:
            raise SystemExit(f"FAIL detector false-negative self-test {i}")
    for i,src in enumerate(good,1):
        reason=forbidden_history_reason(src,f"<good-{i}>")
        if reason is not None:
            raise SystemExit(f"FAIL detector false-positive self-test {i}: {reason}")

def static_governance_runtime_read_check(blob,path):
    if not path.startswith("governance-runtime/r8_v15_r1_") or path.startswith("governance-runtime/test_"):
        return
    text=run(PROPOSAL_ROOT,"git","cat-file","blob",blob).stdout
    reason=forbidden_history_reason(text,path)
    if reason is not None:
        raise SystemExit(f"FAIL runtime governance-history dependency {path}: {reason}")

def assert_exact_clean_base(target):
    head=run(target,"git","rev-parse","HEAD").stdout.strip()
    if head!=BASE:
        raise SystemExit(f"FAIL target HEAD {head} != exact Slice7 base {BASE}")
    if run(target,"git","status","--porcelain=v1").stdout.strip():
        raise SystemExit("FAIL target worktree not clean before materialization")
    if run(target,"git","diff","--quiet",BASE,"HEAD",check=False).returncode!=0:
        raise SystemExit("FAIL target commit tree differs from exact base")
    if run(PROPOSAL_ROOT,"git","diff","--quiet",FROZEN_SCHEMA,BASE,"--","schemas/governance-r8/v15-r1",check=False).returncode!=0:
        raise SystemExit("FAIL Slice7 schema subtree differs from frozen schema candidate")

def preflight(target):
    assert_machinery_declarative()
    assert_detector_self_tests()
    allow=load_json(ALLOW)
    summary=load_json(SUMMARY)
    baseline=load_json(BASELINE)
    assert_exact_clean_base(target)
    if allow["implementation_tree_base"]!=BASE or baseline["exact_slice7_base"]!=BASE:
        raise SystemExit("FAIL base binding mismatch")
    if summary["collisions_total"]!=0 or summary["conflicting_collisions_total"]!=0:
        raise SystemExit("FAIL collisions exist before materialization")
    claims={}
    for n,rec in allow["per_candidate"].items():
        source=rec["source_commit"]
        if source!=allow["reviewed_candidates"][n]:
            raise SystemExit(f"FAIL source commit mismatch slice {n}")
        ensure_commit(source)
        for e in rec["selected_entries"]:
            if e["source_commit"]!=source:
                raise SystemExit(f"FAIL entry source mismatch {e['path']}")
            if e["path"] in RESERVED:
                raise SystemExit(f"FAIL reserved-path collision {e['path']}")
            got=tree_entry(source,e["path"])
            exp={k:e[k] for k in ("path","mode","type","blob")}
            if got!=exp:
                raise SystemExit(f"FAIL source tree-entry mismatch {n} {e['path']}: {got} != {exp}")
            if e["type"]!="blob":
                raise SystemExit(f"FAIL selected non-blob {e['path']}")
            static_governance_runtime_read_check(e["blob"],e["path"])
            claims.setdefault(e["path"],[]).append((n,e["mode"],e["blob"]))
    if any(len(v)>1 for v in claims.values()):
        raise SystemExit("FAIL duplicate/colliding selected path before materialization")
    for n,pred in REJECTED.items():
        ensure_commit(pred)
        source=allow["per_candidate"][n]["source_commit"]
        if run(PROPOSAL_ROOT,"git","merge-base","--is-ancestor",pred,source,check=False).returncode!=0:
            raise SystemExit(f"FAIL repaired successor ancestry changed slice {n}")
        identical=set()
        for e in allow["per_candidate"][n]["selected_entries"]:
            pe=tree_entry(pred,e["path"])
            if pe and pe["mode"]==e["mode"] and pe["blob"]==e["blob"]:
                identical.add(e["path"])
        if identical!=REACCEPTED_IDENTICAL[n]:
            raise SystemExit(f"FAIL rejected-predecessor identical set changed slice {n}: {sorted(identical)}")
    manifest_paths=[e["path"] for e in baseline["test_entries"]]
    grouped=[p for g in baseline["groups"] for p in g["files"]]
    if sorted(grouped)!=sorted(manifest_paths) or len(grouped)!=len(set(grouped)):
        raise SystemExit("FAIL baseline groups do not exactly partition baseline identities")
    if sum(g["expected_tests"] for g in baseline["groups"])!=baseline["expected_total_tests"] or baseline["expected_total_tests"]!=140:
        raise SystemExit("FAIL baseline expected counts inconsistent")
    for e in baseline["test_entries"]:
        got=index_entry(target,e["path"])
        exp={"path":e["path"],"mode":e["mode"],"type":e["type"],"blob":e["blob"],"stage":"0"}
        if got!=exp:
            raise SystemExit(f"FAIL baseline test identity {e['path']}: {got} != {exp}")
    return allow

def materialize(target,allow):
    for n in sorted(allow["per_candidate"],key=int):
        source=allow["per_candidate"][n]["source_commit"]
        for e in allow["per_candidate"][n]["selected_entries"]:
            run(target,"git","checkout",source,"--",e["path"])
    for rec in allow["per_candidate"].values():
        for e in rec["selected_entries"]:
            got=index_entry(target,e["path"])
            exp={"path":e["path"],"mode":e["mode"],"type":"blob","blob":e["blob"],"stage":"0"}
            if got!=exp:
                raise SystemExit(f"FAIL post-materialization identity {e['path']}: {got} != {exp}")

def write_manifest(target,allow):
    p=target/MANIFEST_PATH
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps({
      "schema":"r8-v15-r1-ig1-successor3-integrated-candidate-manifest/v1",
      "status":"INTEGRATED_IMPLEMENTATION_CANDIDATE_NON_AUTHORITATIVE_PENDING_FRESH_INDEPENDENT_REVIEW",
      "authority_effect":"NONE",
      "base_commit":BASE,
      "frozen_schema_candidate":FROZEN_SCHEMA,
      "selected_reviewed_entry_count":sum(len(v["selected_entries"]) for v in allow["per_candidate"].values()),
      "selected_reviewed_candidate_count":len(allow["per_candidate"]),
      "composition_rule":"Exact Slice7 base plus exactly 120 reviewed allowlisted entries plus this manifest.",
      "semantic_execution_performed":False,
      "currentness_decision_performed":False,
      "qualification_performed":False,
      "evidence_promotion_performed":False,
      "cross_slice_dependency_authority_granted":False,
      "runtime_qualification":False,
      "release":False,
      "deployment":False,
      "production":False,
      "policy_authority":False,
      "constitutional_authority":False,
      "root_authority":False,
      "terminal_authority":False
    },indent=2)+"\n")
    run(target,"git","add","--",MANIFEST_PATH)

def verify_exact_final_diff(target,allow):
    expected={e["path"] for rec in allow["per_candidate"].values() for e in rec["selected_entries"]}
    expected.add(MANIFEST_PATH)
    staged=set(filter(None,run(target,"git","diff","--cached","--name-only",BASE).stdout.splitlines()))
    if staged!=expected:
        raise SystemExit(f"FAIL staged path set mismatch missing={sorted(expected-staged)} extra={sorted(staged-expected)}")
    if run(target,"git","diff","--quiet",check=False).returncode!=0:
        raise SystemExit("FAIL unstaged tracked changes exist")
    untracked=run(target,"git","ls-files","--others","--exclude-standard").stdout.splitlines()
    if untracked:
        raise SystemExit(f"FAIL untracked paths exist: {untracked}")
    for rec in allow["per_candidate"].values():
        for e in rec["selected_entries"]:
            got=index_entry(target,e["path"])
            exp={"path":e["path"],"mode":e["mode"],"type":"blob","blob":e["blob"],"stage":"0"}
            if got!=exp:
                raise SystemExit(f"FAIL final selected identity {e['path']}: {got} != {exp}")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--target",required=True)
    ap.add_argument("--preflight-only",action="store_true")
    ap.add_argument("--verify-final-only",action="store_true")
    args=ap.parse_args()
    target=pathlib.Path(args.target).resolve()
    if args.verify_final_only:
        verify_exact_final_diff(target,load_json(ALLOW))
        print("IG1_SUCCESSOR3_FINAL_DIFF_VERIFY_PASS")
        return
    allow=preflight(target)
    if args.preflight_only:
        print("IG1_SUCCESSOR3_PREFLIGHT_PASS")
        return
    materialize(target,allow)
    write_manifest(target,allow)
    verify_exact_final_diff(target,allow)
    run(PROPOSAL_ROOT,sys.executable,str(ORACLE),"--target",str(target))
    verify_exact_final_diff(target,allow)
    print("IG1_SUCCESSOR3_MATERIALIZATION_AND_ORACLE_PASS")

if __name__=="__main__":
    main()
