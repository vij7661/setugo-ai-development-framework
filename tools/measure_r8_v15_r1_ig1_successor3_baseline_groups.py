#!/usr/bin/env python3
import json, pathlib, re, subprocess, sys
ROOT=pathlib.Path(sys.argv[1]).resolve()
groups=[
 {"name":"slice7","files":["governance-runtime/test_r8_v15_r1_implementation_slice7.py"]},
 {"name":"slice6","files":["governance-runtime/test_r8_v15_r1_implementation_slice6.py"]},
 {"name":"slice5","files":["governance-runtime/test_r8_v15_r1_implementation_slice5.py"]},
 {"name":"slice4","files":["governance-runtime/test_r8_v15_r1_implementation_slice4.py"]},
 {"name":"slice3","files":["governance-runtime/test_r8_v15_r1_implementation_slice3.py"]},
 {"name":"slice2","files":["governance-runtime/test_r8_v15_r1_implementation_slice2.py"]},
 {"name":"slice1-family","files":[
   "governance-runtime/test_r8_v15_r1_implementation_slice1.py",
   "governance-runtime/test_r8_v15_r1_implementation_slice1_successor1.py",
   "governance-runtime/test_r8_v15_r1_implementation_slice1_successor2.py",
   "governance-runtime/test_r8_v15_r1_sfv45_r2_repair.py",
   "governance-runtime/test_r8_v15_r1_post_freeze_regression.py"
 ]}
]
out=[]
for g in groups:
    p=subprocess.run([sys.executable,"-m","unittest","-v",*g["files"]],cwd=ROOT,text=True,capture_output=True)
    txt=p.stdout+"\n"+p.stderr
    ms=re.findall(r"Ran\s+(\d+)\s+tests?",txt,re.I)
    if p.returncode!=0 or not ms:
        raise SystemExit(f"group {g['name']} failed\n{txt}")
    count=int(ms[-1])
    out.append({**g,"expected_tests":count})
total=sum(x["expected_tests"] for x in out)
if total!=140: raise SystemExit(f"baseline total {total} != 140")
print(json.dumps({"exact_base":"751162ee42c603cb6c84ee12021d16bab6fa626b","groups":out,"expected_total_tests":total},indent=2))
