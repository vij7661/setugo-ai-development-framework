#!/usr/bin/env python3
"""IG-1 Successor2: exact-base mechanical integration materializer.

Proposal/execution machinery only. It never imports or calls production validators.
All source/collision/base/machinery checks complete before the first materialization.
"""
from __future__ import annotations
import argparse, ast, json, pathlib, subprocess, sys

PROPOSAL_ROOT=pathlib.Path(__file__).resolve().parent.parent
ALLOW=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"
SUMMARY=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-PREFLIGHT-SUMMARY.json"
BASELINE=PROPOSAL_ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR2-INHERITED-BASELINE-TEST-IDENTITY.json"
ORACLE=PROPOSAL_ROOT/"governance-runtime"/"test_r8_v15_r1_ig1_successor2_integration_oracle.py"
BASE="751162ee42c603cb6c84ee12021d16bab6fa626b"
FROZEN_SCHEMA="f93ca26975ecb64f0da13779889c75b36140cdfc"
MANIFEST_PATH="governance-r8/R8-V15-R1-IG1-SUCCESSOR2-INTEGRATED-CANDIDATE-MANIFEST.json"
REJECTED={"20":"053a5c0e70aee45e0e73653d68de3575a83d455c","21":"d3f184380f6cd15582cb3dd6e987895dd895d930","22":"8ecdd17ce80549f87dd15bbe1fc29414272b6253"}
REACCEPTED_IDENTICAL={
 "20":{"governance-runtime/test_r8_v15_r1_implementation_slice20.py"},
 "21":{"governance-runtime/test_r8_v15_r1_implementation_slice21.py"},
 "22":{"governance-runtime/test_r8_v15_r1_implementation_slice22.py"},
}
RESERVED={
 "tools/r8_v15_r1_ig1_successor2_materialize.py",
 "governance-runtime/test_r8_v15_r1_ig1_successor2_integration_oracle.py",
 ".github/workflows/r8-v15-r1-ig1-successor2-materialize.yml",
 MANIFEST_PATH,
}

def run(root,*args,check=True):
    p=subprocess.run(args,cwd=root,text=True,capture_output=True)
    if check and p.returncode:
        raise SystemExit(f"FAIL cwd={root} command={args!r}\nstdout={p.stdout}\nstderr={p.stderr}")
    return p

def load_json(path):
    return json.loads(path.read_text())

def ensure_commit(c):
    p=run(PROPOSAL_ROOT,"git","cat-file","-e",c+"^{commit}",check=False)
    if p.returncode:
        run(PROPOSAL_ROOT,"git","fetch","--no-tags","origin",c)
    got=run(PROPOSAL_ROOT,"git","rev-parse",c+"^{commit}").stdout.strip()
    if got!=c: raise SystemExit(f"FAIL source commit identity {c} -> {got}")

def tree_entry(commit,path):
    out=run(PROPOSAL_ROOT,"git","ls-tree",commit,"--",path).stdout.rstrip("\n")
    if not out: return None
    meta,name=out.split("\t",1); mode,typ,blob=meta.split()
    return {"path":name,"mode":mode,"type":typ,"blob":blob}

def index_entry(target,path):
    out=run(target,"git","ls-files","-s","--",path).stdout.strip()
    if not out: return None
    first=out.splitlines()[0]
    meta,name=first.split("\t",1); mode,blob,stage=meta.split()
    return {"path":name,"mode":mode,"type":"blob","blob":blob,"stage":stage}

def path_class(node,classes):
    literals=[x.value for x in ast.walk(node) if isinstance(x,ast.Constant) and isinstance(x.value,str)]
    inherited=[classes[x.id] for x in ast.walk(node) if isinstance(x,ast.Name) and x.id in classes]
    joined="/".join(literals)
    if "SCHEMA" in inherited:
        return "SCHEMA"
    if "HISTORY" in inherited:
        return "HISTORY"
    if ("schemas" in literals and "governance-r8" in literals) or "schemas/governance-r8" in joined:
        return "SCHEMA"
    for s in literals:
        norm=s.replace("\\","/")
        if norm=="governance-r8" or norm.startswith("governance-r8/") or ("/governance-r8/" in norm and "/schemas/governance-r8/" not in norm):
            return "HISTORY"
    return None

def static_governance_runtime_read_check(blob,path):
    if not path.startswith("governance-runtime/r8_v15_r1_") or path.startswith("governance-runtime/test_"):
        return
    text=run(PROPOSAL_ROOT,"git","cat-file","blob",blob).stdout
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
                    classes[target.id]=cls; changed=True
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call):
            continue
        if isinstance(node.func,ast.Name) and node.func.id=="open":
            if any(path_class(a,classes)=="HISTORY" for a in node.args):
                raise SystemExit(f"FAIL runtime governance-history open(): {path}")
        elif isinstance(node.func,ast.Attribute) and node.func.attr in {"open","read_text","read_bytes"}:
            receiver_class=path_class(node.func.value,classes)
            arg_classes=[path_class(a,classes) for a in node.args]
            if receiver_class=="HISTORY" or "HISTORY" in arg_classes:
                raise SystemExit(f"FAIL runtime governance-history file read: {path}")

def assert_integration_machinery_declarative():
    for p in (
        pathlib.Path(__file__).resolve(),
        ORACLE,
    ):
        text=p.read_text()
        tree=ast.parse(text,filename=str(p))
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                for alias in node.names:
                    if alias.name.startswith("r8_v15_r1_") or alias.name.startswith("unittest.mock"):
                        raise SystemExit(f"FAIL forbidden integration import {alias.name} in {p}")
            elif isinstance(node,ast.ImportFrom):
                name=node.module or ""
                if name.startswith("r8_v15_r1_") or name.startswith("unittest.mock"):
                    raise SystemExit(f"FAIL forbidden integration import-from {name} in {p}")
            elif isinstance(node,ast.Name) and node.id=="monkeypatch":
                raise SystemExit(f"FAIL monkeypatch name in {p}")
            elif isinstance(node,ast.Subscript):
                target=node.value
                if isinstance(target,ast.Attribute) and isinstance(target.value,ast.Name) and target.value.id=="sys" and target.attr=="modules":
                    raise SystemExit(f"FAIL sys.modules access in {p}")
    wf=(PROPOSAL_ROOT/".github/workflows/r8-v15-r1-ig1-successor2-materialize.yml").read_text().lower()
    for token in ("unittest.mock","mock.patch","monkeypatch","sys.modules"):
        if token in wf:
            raise SystemExit(f"FAIL forbidden workflow token {token}")

def assert_exact_clean_base(target):
    head=run(target,"git","rev-parse","HEAD").stdout.strip()
    if head!=BASE: raise SystemExit(f"FAIL target HEAD {head} != exact Slice7 base {BASE}")
    if run(target,"git","status","--porcelain=v1").stdout.strip():
        raise SystemExit("FAIL target worktree is not clean before materialization")
    if run(target,"git","diff","--quiet",BASE,"HEAD",check=False).returncode!=0:
        raise SystemExit("FAIL target commit tree differs from exact base")
    if run(PROPOSAL_ROOT,"git","diff","--quiet",FROZEN_SCHEMA,BASE,"--","schemas/governance-r8/v15-r1",check=False).returncode!=0:
        raise SystemExit("FAIL Slice7 base schema tree differs from frozen schema candidate")

def preflight(target):
    assert_integration_machinery_declarative()
    allow=load_json(ALLOW); summary=load_json(SUMMARY); baseline=load_json(BASELINE)
    assert_exact_clean_base(target)
    if allow["implementation_tree_base"]!=BASE or baseline["exact_slice7_base"]!=BASE:
        raise SystemExit("FAIL base binding mismatch")
    if summary["collisions_total"]!=0 or summary["conflicting_collisions_total"]!=0:
        raise SystemExit("FAIL collisions exist before materialization")
    claims={}
    for n,rec in allow["per_candidate"].items():
        source=rec["source_commit"]
        if source!=allow["reviewed_candidates"][n]:
            raise SystemExit(f"FAIL source commit not exact reviewed candidate slice {n}")
        ensure_commit(source)
        for e in rec["selected_entries"]:
            if e["source_commit"]!=source: raise SystemExit(f"FAIL entry source mismatch {e}")
            if e["path"] in RESERVED: raise SystemExit(f"FAIL reserved-path collision {e['path']}")
            current=tree_entry(source,e["path"])
            expected={k:e[k] for k in ("path","mode","type","blob")}
            if current!=expected: raise SystemExit(f"FAIL source tree-entry mismatch {n} {e['path']}")
            if e["type"]!="blob": raise SystemExit(f"FAIL selected non-blob {e['path']}")
            static_governance_runtime_read_check(e["blob"],e["path"])
            claims.setdefault(e["path"],[]).append((n,e["mode"],e["blob"]))
    if any(len(v)>1 for v in claims.values()):
        raise SystemExit("FAIL duplicate/colliding selected path before materialization")
    for n,pred in REJECTED.items():
        ensure_commit(pred)
        source=allow["per_candidate"][n]["source_commit"]
        if run(PROPOSAL_ROOT,"git","merge-base","--is-ancestor",pred,source,check=False).returncode!=0:
            raise SystemExit(f"FAIL repaired successor lineage changed slice {n}")
        identical=set()
        for e in allow["per_candidate"][n]["selected_entries"]:
            pe=tree_entry(pred,e["path"])
            if pe and pe["mode"]==e["mode"] and pe["blob"]==e["blob"]:
                identical.add(e["path"])
        if identical!=REACCEPTED_IDENTICAL[n]:
            raise SystemExit(f"FAIL rejected-predecessor identical-entry set changed slice {n}: {sorted(identical)}")
    # Baseline test identities must be exact in the untouched base before any test execution.
    for e in baseline["test_entries"]:
        got=index_entry(target,e["path"])
        expected={"path":e["path"],"mode":e["mode"],"type":e["type"],"blob":e["blob"],"stage":"0"}
        if got!=expected: raise SystemExit(f"FAIL baseline test identity mismatch {e['path']}: {got} != {expected}")
    return allow,baseline

def materialize(target,allow):
    # No byte is selected before preflight returns successfully.
    for n in sorted(allow["per_candidate"],key=int):
        source=allow["per_candidate"][n]["source_commit"]
        for e in allow["per_candidate"][n]["selected_entries"]:
            run(target,"git","checkout",source,"--",e["path"])
    for rec in allow["per_candidate"].values():
        for e in rec["selected_entries"]:
            got=index_entry(target,e["path"])
            expected={"path":e["path"],"mode":e["mode"],"type":"blob","blob":e["blob"],"stage":"0"}
            if got!=expected: raise SystemExit(f"FAIL post-materialization identity {e['path']}: {got} != {expected}")

def write_manifest(target,allow):
    manifest={
      "schema":"r8-v15-r1-ig1-successor2-integrated-candidate-manifest/v1",
      "status":"INTEGRATED_IMPLEMENTATION_CANDIDATE_NON_AUTHORITATIVE_PENDING_FRESH_INDEPENDENT_REVIEW",
      "authority_effect":"NONE",
      "base_commit":BASE,
      "frozen_schema_candidate":FROZEN_SCHEMA,
      "selected_reviewed_entry_count":sum(len(v["selected_entries"]) for v in allow["per_candidate"].values()),
      "selected_reviewed_candidate_count":len(allow["per_candidate"]),
      "composition_rule":"Exact Slice7 base plus exactly the 120 independently reviewed allowlisted tree entries plus this manifest.",
      "semantic_execution_performed":False,
      "currentness_decision_performed":False,
      "qualification_performed":False,
      "evidence_promotion_performed":False,
      "cross_slice_dependency_authority_granted":False,
      "runtime_qualification":False,"release":False,"deployment":False,"production":False,
      "policy_authority":False,"constitutional_authority":False,"root_authority":False,"terminal_authority":False
    }
    p=target/MANIFEST_PATH
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(manifest,indent=2)+"\n")
    run(target,"git","add","--",MANIFEST_PATH)

def verify_exact_final_diff(target,allow):
    expected={e["path"] for rec in allow["per_candidate"].values() for e in rec["selected_entries"]}
    expected.add(MANIFEST_PATH)
    staged=set(filter(None,run(target,"git","diff","--cached","--name-only",BASE).stdout.splitlines()))
    if staged!=expected:
        raise SystemExit(f"FAIL final staged diff path set mismatch missing={sorted(expected-staged)} extra={sorted(staged-expected)}")
    if run(target,"git","diff","--quiet",check=False).returncode!=0:
        raise SystemExit("FAIL unstaged tracked changes exist")
    untracked=run(target,"git","ls-files","--others","--exclude-standard").stdout.splitlines()
    if untracked: raise SystemExit(f"FAIL untracked paths exist: {untracked}")
    for rec in allow["per_candidate"].values():
        for e in rec["selected_entries"]:
            got=index_entry(target,e["path"])
            if got!={"path":e["path"],"mode":e["mode"],"type":"blob","blob":e["blob"],"stage":"0"}:
                raise SystemExit(f"FAIL final selected entry identity {e['path']}")
    return expected

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--target",required=True)
    ap.add_argument("--preflight-only",action="store_true")
    args=ap.parse_args()
    target=pathlib.Path(args.target).resolve()
    allow,baseline=preflight(target)
    if args.preflight_only:
        print("IG1_SUCCESSOR2_PREFLIGHT_PASS"); return
    materialize(target,allow)
    write_manifest(target,allow)
    verify_exact_final_diff(target,allow)
    run(PROPOSAL_ROOT,sys.executable,str(ORACLE),"--target",str(target))
    verify_exact_final_diff(target,allow)
    print("IG1_SUCCESSOR2_MATERIALIZATION_AND_STRICT_ORACLE_PASS")

if __name__=="__main__": main()
