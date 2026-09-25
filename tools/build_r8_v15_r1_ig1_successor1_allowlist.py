#!/usr/bin/env python3
import json, os, pathlib, re, subprocess, hashlib
REPO=os.environ["GITHUB_REPOSITORY"]
BASE="751162ee42c603cb6c84ee12021d16bab6fa626b"
ROSTER={"8":"fa94f8dd96bc54515baabf3f34ed37d25f41f6db","9":"9d82c3f095fa08e81808d7e0d4c4b0a0a26556ea","10":"33d112b5e2d3d6bc75fb07f14f6cf55c4d6b19f4","11":"4b49613a56c53048cf9531783b09ba71b64539ef","12":"294c8b0112e1715402325836f1c8f0b58a042e70","13":"4f9c5f6a1a22d61a038ada48bb8ce5ce28af41f0","14":"5c0e6e47d7b4e23f0be0b9137e1d67f3ab73b88b","15":"1dcccf04e8c05f8acae145fa63c140d44e68d882","16":"d9a935a0e418e70a0f63904c98547ff4590d8f72","17":"2717f6127a4d2a76a7d7efafe5e79fe83cc32c53","18":"9a7d60691fa80b1b5da52dbd5120e899eeefbfe6","19":"6d591e8ce8a881411929a887d7152603a4af0e49","20":"eee3dee24243fe79c86f0d587fcbf42df932fb39","21":"799921c4e31df9b1140a21c3a1f182dceaaa3f6d","22":"7adab4471a17612d50eaf3fae48feb50884f5fcd","23":"e80783edea482605eb15ddaded6c8ef8aa79303c","24":"49ad02ca8ccc4f9d6f1b5c78c7ba392184eb2ab4","25":"aa61ee5637daa10f1de9f39d164c610145fe47be","26":"83e0366251e22d9768554e44340e2b81dbf5424a","27":"d5c01df8c03b808ca0382793433e6e910485f09f","28":"bc17d15d4f0939945576d364dec6ee761c96d8d5","29":"4c720a215e8d3e99ea236f7a951263a168929813","30":"113a67da6b11936a48a919410e88469ece20f84b","31":"66595ac25a600daa9c71e63f473d815859945136","32":"5fa171b732e58e2eb1a75d755ae25b18f4ac3fff","33":"bbf310642e6e106fc2de4375da38bbb6d355c6ad","34":"6b313f9d1a0c7a2712e5773e7844aa19355091e3","35":"fd8f410be0cf6e0a45cd5b67942e462278d360e2","36":"07a62458e36adb02b621ecf0fb6761c6cbb6c376","37":"3b16bd2ea3c00eb1f1d2acedf1c3375d2f0eeb2e","38":"9d5e9af3a643297b5b4074d8be42904a6fa6098d","39":"43d43aa48571c905cb4d43e202f891ab853e8d5a","40":"46e373bc50aee6d1d05aeba01a8d42037a743128","41":"cea8e0925e715d5735d33b6522521c3abca8c87b","42":"0a4ada53a74dc09f064b4a753fc0629fe64a9a07","43":"308a06c55de52ec2e59c350aa119733ff7cc6b3b","44":"c1d95441292d2051fbb50b03af8d79093818d0ff","45":"e04913f7973d135f00ecafe6c5b6ea580305e55c","46":"237b2e3216378ad75e8c54b1a44cb1b0b245002f"}
REJECTED={"20":"053a5c0e70aee45e0e73653d68de3575a83d455c","21":"d3f184380f6cd15582cb3dd6e987895dd895d930","22":"8ecdd17ce80549f87dd15bbe1fc29414272b6253"}
OUT=pathlib.Path("ig1-successor1-evidence"); OUT.mkdir(exist_ok=True)

def sh(*args,check=True):
    p=subprocess.run(args,text=True,capture_output=True)
    if check and p.returncode: raise SystemExit(f"command failed {args}: {p.stderr}")
    return p

def ensure(commit):
    if sh("git","cat-file","-e",commit+"^{commit}",check=False).returncode:
        sh("git","fetch","--no-tags","origin",commit)
    assert sh("git","rev-parse",commit+"^{commit}").stdout.strip()==commit

def tree_entry(commit,path):
    p=sh("git","ls-tree",commit,"--",path).stdout.rstrip("\n")
    if not p: return None
    meta,name=p.split("\t",1); mode,typ,blob=meta.split()
    return {"path":name,"mode":mode,"type":typ,"blob":blob}

def changed_paths(base,cand):
    z=subprocess.check_output(["git","diff","--name-status","-z",base,cand]).decode("utf-8","surrogateescape").split("\0")
    out=[]; i=0
    while i<len(z)-1:
        status=z[i]; i+=1
        if status.startswith(("R","C")):
            old=z[i]; new=z[i+1]; i+=2; out.append({"status":status,"old_path":old,"path":new})
        else:
            path=z[i]; i+=1; out.append({"status":status,"path":path})
    return out

def selected_for_slice(n,path):
    if re.fullmatch(r"governance-runtime/r8_v15_r1_[^/]+\.py",path):
        return True
    if re.fullmatch(rf"governance-runtime/test_r8_v15_r1_implementation_slice{n}[^/]*\.py",path):
        return True
    if re.fullmatch(rf"\.github/workflows/r8-v15-r1-implementation-slice{n}[^/]*\.yml",path):
        return True
    return False

for c in [BASE,*ROSTER.values(),*REJECTED.values()]: ensure(c)

per={}
path_claims={}
all_inventory=[]
for n,cand in ROSTER.items():
    inv=changed_paths(BASE,cand)
    selected=[]
    for item in inv:
        path=item["path"]; ent=tree_entry(cand,path)
        rec={"slice":int(n),"candidate":cand,**item,"candidate_tree_entry":ent,"selected":False}
        if selected_for_slice(n,path):
            if ent is None or ent["type"]!="blob":
                raise SystemExit(f"selected non-blob or missing: slice {n} {path}")
            rec["selected"]=True
            selected.append({"slice":int(n),"source_commit":cand,**ent})
            path_claims.setdefault(path,[]).append({"slice":int(n),"source_commit":cand,"mode":ent["mode"],"blob":ent["blob"]})
        all_inventory.append(rec)
    if not selected:
        raise SystemExit(f"slice {n} has no selected entries")
    per[n]={"source_commit":cand,"selected_entries":selected,"changed_path_count":len(inv),"selected_count":len(selected)}

collisions=[]
for path,claims in sorted(path_claims.items()):
    if len(claims)>1:
        identities={(x["mode"],x["blob"]) for x in claims}
        collisions.append({"path":path,"claims":claims,"identity_count":len(identities),"conflicting":len(identities)>1})

rejected_analysis={}
for n,pred in REJECTED.items():
    cand=ROSTER[n]
    anc=(sh("git","merge-base","--is-ancestor",pred,cand,check=False).returncode==0)
    selected=[]
    for e in per[n]["selected_entries"]:
        pe=tree_entry(pred,e["path"])
        selected.append({
          "path":e["path"],"successor_mode":e["mode"],"successor_blob":e["blob"],
          "predecessor_entry":pe,
          "identical_to_rejected_predecessor": bool(pe and pe["mode"]==e["mode"] and pe["blob"]==e["blob"]),
          "eligibility_basis":"EXACT_SUCCESSOR_CANDIDATE_REVIEW_GATE_YES_AND_SUCCESSOR1_CLOSURE; entry still requires explicit allowlist review"
        })
    rejected_analysis[n]={
      "rejected_predecessor":pred,"reviewed_successor":cand,
      "rejected_is_ancestor_of_reviewed_successor":anc,
      "strict_ancestry_ban_compatible_with_repair_lineage":not anc,
      "selected_entry_comparison":selected
    }

manifest={
 "schema":"r8-v15-r1-ig1-successor1-exact-tree-entry-allowlist/v1",
 "status":"PROPOSAL_EVIDENCE_NOT_ACTIVE_NOT_MATERIALIZED",
 "authority_effect":"NONE",
 "implementation_tree_base":BASE,
 "reviewed_candidates":ROSTER,
 "selection_rule":{
   "implementation":"direct governance-runtime/r8_v15_r1_*.py blobs changed by exact candidate relative to Slice7 base",
   "tests":"governance-runtime/test_r8_v15_r1_implementation_sliceN*.py changed by exact candidate relative to Slice7 base",
   "workflows":".github/workflows/r8-v15-r1-implementation-sliceN*.yml changed by exact candidate relative to Slice7 base",
   "important":"This generated list itself must receive independent review before it can become an executable allowlist. No unlisted path may be materialized."
 },
 "per_candidate":per,
 "collisions":collisions,
 "hard_fail_if_any_conflicting_collision":True,
 "hard_fail_if_source_commit_not_exact_roster_candidate":True,
 "hard_fail_if_materialized_path_not_listed":True,
 "hard_fail_if_materialized_mode_or_blob_differs":True,
 "rejected_predecessor_analysis":rejected_analysis,
 "grants":{"integration":False,"semantic_execution":False,"runtime_qualification":False,"evidence_promotion":False,"terminal_authority":False}
}
(OUT/"R8-V15-R1-IG1-SUCCESSOR1-EXACT-TREE-ENTRY-ALLOWLIST.json").write_text(json.dumps(manifest,indent=2)+"\n")
(OUT/"R8-V15-R1-IG1-SUCCESSOR1-FULL-CHANGE-INVENTORY.json").write_text(json.dumps({
 "schema":"r8-v15-r1-ig1-successor1-full-change-inventory/v1",
 "base":BASE,"inventory":all_inventory
},indent=2)+"\n")
summary={
 "selected_entries_total":sum(v["selected_count"] for v in per.values()),
 "changed_paths_total":sum(v["changed_path_count"] for v in per.values()),
 "collisions_total":len(collisions),
 "conflicting_collisions_total":sum(1 for c in collisions if c["conflicting"]),
 "s20_22_rejected_ancestor_flags":{n:v["rejected_is_ancestor_of_reviewed_successor"] for n,v in rejected_analysis.items()},
 "s20_22_identical_selected_entries_to_rejected":{n:sum(1 for x in v["selected_entry_comparison"] if x["identical_to_rejected_predecessor"]) for n,v in rejected_analysis.items()}
}
(OUT/"R8-V15-R1-IG1-SUCCESSOR1-PREFLIGHT-SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
for p in sorted(OUT.iterdir()):
    b=p.read_bytes(); print(p.name,len(b),hashlib.sha256(b).hexdigest())
