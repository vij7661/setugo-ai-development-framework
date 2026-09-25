#!/usr/bin/env python3
"""Compare forward/reverse Stage2 SG-1 harness results."""
from __future__ import annotations
import json, pathlib, sys

def load(path):
    return json.loads(pathlib.Path(path).read_text())

if len(sys.argv)!=3:
    raise SystemExit("usage: compare.py FORWARD.json REVERSE.json")
a=load(sys.argv[1]); b=load(sys.argv[2])
for x in (a,b):
    if x.get("status")!="PASS" or x.get("case_count")!=18:
        raise SystemExit("SG1 result not exact PASS/18")
    if set(x.get("cases",{}).values())!={True}:
        raise SystemExit("SG1 case failure")
    if x.get("authority_effect")!="NONE" or x.get("external_effects_performed") is not False or x.get("candidate_modified") is not False:
        raise SystemExit("SG1 authority/effect boundary violated")
if a["candidate"]!=b["candidate"] or a["candidate_tree"]!=b["candidate_tree"]:
    raise SystemExit("candidate identity differs across import orders")
if a["semantic_fingerprint"]!=b["semantic_fingerprint"]:
    raise SystemExit("semantic fingerprint differs across import orders")
if a["cases"]!=b["cases"]:
    raise SystemExit("case results differ across import orders")
print(json.dumps({
 "status":"R8V15R1_STAGE2_SG1_FORWARD_REVERSE_EQUIVALENCE_PASS",
 "candidate":a["candidate"],
 "case_count_each":18,
 "orders":["forward","reverse"],
 "authority_effect":"NONE"
},sort_keys=True))
