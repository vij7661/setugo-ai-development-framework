#!/usr/bin/env python3
from __future__ import annotations
import ast, json, pathlib, subprocess

ROOT=pathlib.Path(__file__).resolve().parent.parent
CANDIDATE="4984f06a4420b76ad1ad475751aebda04a2d2c5c"
BASE="751162ee42c603cb6c84ee12021d16bab6fa626b"
ALLOW=ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"
OUT=ROOT/"stage2-sg1-evidence"
OUT.mkdir(exist_ok=True)

def run(*args):
    return subprocess.check_output(args,cwd=ROOT,text=True)

def blob(rev,path):
    return run("git","rev-parse",f"{rev}:{path}").strip()

def exists(rev,path):
    return subprocess.run(["git","cat-file","-e",f"{rev}:{path}"],cwd=ROOT).returncode==0

def module_to_paths(module):
    return [
      f"governance-runtime/{module}.py",
      f"governance-runtime/{module}/__init__.py",
    ]

allow=json.loads(ALLOW.read_text())
selected_impl=sorted({
    e["path"]
    for rec in allow["per_candidate"].values()
    for e in rec["selected_entries"]
    if e["path"].startswith("governance-runtime/r8_v15_r1_") and e["path"].endswith(".py")
})
selected_set=set(selected_impl)
edges=[]
for path in selected_impl:
    src=run("git","show",f"{CANDIDATE}:{path}")
    tree=ast.parse(src,filename=path)
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            for alias in node.names:
                mod=alias.name
                if mod.startswith("r8_v15_r1_"):
                    target=None
                    for p in module_to_paths(mod):
                        if exists(CANDIDATE,p):
                            target=p; break
                    edges.append({
                      "from_path":path,
                      "import_kind":"import",
                      "import_module":mod,
                      "imported_names":[],
                      "target_path":target,
                      "target_blob_candidate":blob(CANDIDATE,target) if target else None,
                      "target_changed_in_stage1": bool(target and target in selected_set),
                      "target_inherited_from_base": bool(target and exists(BASE,target) and blob(BASE,target)==blob(CANDIDATE,target)),
                      "lineno":node.lineno
                    })
        elif isinstance(node,ast.ImportFrom):
            mod=node.module or ""
            if mod.startswith("r8_v15_r1_"):
                target=None
                for p in module_to_paths(mod):
                    if exists(CANDIDATE,p):
                        target=p; break
                edges.append({
                  "from_path":path,
                  "import_kind":"from",
                  "import_module":mod,
                  "imported_names":[a.name for a in node.names],
                  "target_path":target,
                  "target_blob_candidate":blob(CANDIDATE,target) if target else None,
                  "target_changed_in_stage1": bool(target and target in selected_set),
                  "target_inherited_from_base": bool(target and exists(BASE,target) and blob(BASE,target)==blob(CANDIDATE,target)),
                  "lineno":node.lineno
                })
edges=sorted(edges,key=lambda x:(x["from_path"],x["lineno"],x["import_module"]))
targets={}
for e in edges:
    t=e["target_path"] or e["import_module"]
    targets.setdefault(t,{"edge_count":0,"sources":[],"blob":e["target_blob_candidate"],"inherited":e["target_inherited_from_base"],"changed":e["target_changed_in_stage1"]})
    targets[t]["edge_count"]+=1
    targets[t]["sources"].append(e["from_path"])

summary={
 "schema":"r8-v15-r1-stage2-sg1-dependency-inventory/v1",
 "candidate":CANDIDATE,
 "candidate_tree":run("git","rev-parse",CANDIDATE+"^{tree}").strip(),
 "base":BASE,
 "selected_implementation_files":len(selected_impl),
 "direct_r8_dependency_edges":len(edges),
 "unique_targets":len(targets),
 "targets":targets,
 "edges":edges,
 "stage2_semantic_execution_performed":False,
 "authority_effect":"NONE"
}
(OUT/"R8-V15-R1-STAGE2-SG1-DEPENDENCY-INVENTORY.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps({
  "selected_implementation_files":len(selected_impl),
  "direct_edges":len(edges),
  "targets":targets
},indent=2))
