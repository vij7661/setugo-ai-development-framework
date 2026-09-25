#!/usr/bin/env python3
from __future__ import annotations
import ast, json, pathlib, subprocess

ROOT=pathlib.Path(__file__).resolve().parent.parent
CANDIDATE="4984f06a4420b76ad1ad475751aebda04a2d2c5c"
BASE="751162ee42c603cb6c84ee12021d16bab6fa626b"
ALLOW=ROOT/"governance-r8"/"R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json"
OUT=ROOT/"governance-r8"/"R8-V15-R1-STAGE2-SG1-DEPENDENCY-SEMANTIC-SURFACE.json"

def run(*args):
    return subprocess.check_output(args,cwd=ROOT,text=True)
def exists(rev,path):
    return subprocess.run(["git","cat-file","-e",f"{rev}:{path}"],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
def blob(rev,path):
    return run("git","rev-parse",f"{rev}:{path}").strip()
def module_path(mod):
    for p in (f"governance-runtime/{mod}.py",f"governance-runtime/{mod}/__init__.py"):
        if exists(CANDIDATE,p): return p
    return None

allow=json.loads(ALLOW.read_text())
selected_impl=sorted({
 e["path"] for rec in allow["per_candidate"].values() for e in rec["selected_entries"]
 if e["path"].startswith("governance-runtime/r8_v15_r1_") and e["path"].endswith(".py")
})
selected_set=set(selected_impl)
edges=[]
for path in selected_impl:
    src=run("git","show",f"{CANDIDATE}:{path}")
    tree=ast.parse(src,filename=path)
    aliases={}
    edge_meta=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            for a in node.names:
                if a.name.startswith("r8_v15_r1_"):
                    alias=a.asname or a.name
                    aliases[alias]=(a.name,"import",[],node.lineno)
                    edge_meta.append((alias,a.name,"import",[],node.lineno))
        elif isinstance(node,ast.ImportFrom):
            mod=node.module or ""
            if mod.startswith("r8_v15_r1_"):
                for a in node.names:
                    alias=a.asname or a.name
                    aliases[alias]=(mod,"from",[a.name],node.lineno)
                    edge_meta.append((alias,mod,"from",[a.name],node.lineno))
    attrs={alias:set() for alias in aliases}
    direct_names={alias:0 for alias in aliases}
    for node in ast.walk(tree):
        if isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id in aliases:
            attrs[node.value.id].add(node.attr)
        elif isinstance(node,ast.Name) and node.id in aliases:
            direct_names[node.id]+=1
    for alias,mod,kind,names,lineno in edge_meta:
        target=module_path(mod)
        edges.append({
          "from_path":path,
          "import_kind":kind,
          "import_module":mod,
          "alias":alias,
          "imported_names":names,
          "used_attributes":sorted(attrs.get(alias,set())),
          "direct_name_occurrences":direct_names.get(alias,0),
          "target_path":target,
          "target_blob_candidate":blob(CANDIDATE,target) if target else None,
          "target_changed_in_stage1":bool(target and target in selected_set),
          "target_inherited_from_base":bool(target and exists(BASE,target) and blob(BASE,target)==blob(CANDIDATE,target)),
          "lineno":lineno
        })
edges.sort(key=lambda x:(x["from_path"],x["lineno"],x["import_module"],x["alias"]))
targets={}
for e in edges:
    t=e["target_path"] or e["import_module"]
    item=targets.setdefault(t,{
      "blob":e["target_blob_candidate"],"inherited":e["target_inherited_from_base"],
      "changed":e["target_changed_in_stage1"],"edge_count":0,"attributes":set(),"sources":[]
    })
    item["edge_count"]+=1
    item["attributes"].update(e["used_attributes"])
    item["sources"].append(e["from_path"])
for t,v in targets.items():
    v["attributes"]=sorted(v["attributes"])
    v["sources"]=sorted(set(v["sources"]))
doc={
 "schema":"r8-v15-r1-stage2-sg1-dependency-semantic-surface/v1",
 "status":"PROPOSAL_EVIDENCE_ONLY_NOT_EXECUTION",
 "candidate":CANDIDATE,
 "candidate_tree":run("git","rev-parse",CANDIDATE+"^{tree}").strip(),
 "base":BASE,
 "selected_implementation_files":len(selected_impl),
 "direct_r8_dependency_edges":len(edges),
 "unique_dependency_targets":len(targets),
 "targets":targets,
 "edges":edges,
 "semantic_execution_performed":False,
 "authority_effect":"NONE",
 "stage2_authorized":False
}
OUT.write_text(json.dumps(doc,indent=2)+"\n")
print(json.dumps({
 "selected_implementation_files":len(selected_impl),
 "direct_edges":len(edges),
 "targets":targets
},indent=2))
