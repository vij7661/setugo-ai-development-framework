from __future__ import annotations
import hashlib, re, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
PACKET=ROOT/"governance-r8/R8-V15-R1-CONSOLIDATED-REMEDIATION-52-ROUND2-REVIEW-PACKET.txt"
BASE="7cd2787d85b189a4161f271ee131e42bd961140a"
HEADS={"42":"82da8dce64a8f96c938f687f8ef31dee34c7938e","43":"8954bd34e98c96e035f8f6e27eb55765ddf76bae","44":"72814c11b60cb9a7385d860777878727d4a4f52c","46":"1d916fc0314c4d4f66f69bf039887f4212847943","50":"ce8be8c5ca551ce0b831e39789a7ed8819348644"}
PREVIOUS={"42":"615e762f97753aa52fb4d4166c9cf3ad73baa91d","43":"c42f18f07b84197836d42ac72c1d22d09f8ac774","44":"424afbe9892aa8a9cc73fc530652662948d30dfc","46":"a8add41bf17efe5c5129607c26f5546963a6eebe","50":"6f6b063432fe5987600df2d508af8443e53d5e67"}
def run(*a): return subprocess.check_output(a,cwd=ROOT,text=True,encoding="utf-8").strip()
def raw(rev,path): return subprocess.check_output(("git","show",f"{rev}:{path}"),cwd=ROOT)
def check():
    text=PACKET.read_text(encoding="utf-8")
    for needle in ["R8 V15-R1 CONSOLIDATED REMEDIATION ROUND 2 REVIEW PACKET",BASE,"REVIEWER OUTPUT CONTRACT","Fallback-to-3 ACTIVE","six-slice cadence NOT RESTORED","grant no authority"]:
        if needle not in text: raise SystemExit(f"missing packet identity/boundary: {needle}")
    for n,h in {**PREVIOUS,**HEADS}.items():
        if h not in text: raise SystemExit(f"missing PR identity {n}:{h}")
    if "Linux capability evidence was not available" not in text: raise SystemExit("Linux evidence boundary missing")
    for n,h in HEADS.items():
        section_start=text.find(f"===== PR #{n} EXACT CHANGED FILES AND BLOBS =====")
        if section_start<0: raise SystemExit(f"missing PR section {n}")
        section_end=text.find("===== PR #",section_start+10)
        section=text[section_start:] if section_end<0 else text[section_start:section_end]
        if f"reviewed_head={h}" not in section: raise SystemExit(f"head mismatch {n}")
        for m in re.finditer(r"FILE_PATH=(.+?)\nFILE_BLOB_SHA1=([0-9a-f]{40})\nFILE_RAW_SHA256=([0-9a-f]{64})",section):
            path,blob,sha=m.groups()
            if run("git","rev-parse",f"{h}:{path}") != blob: raise SystemExit(f"blob mismatch {n}:{path}")
            if hashlib.sha256(raw(h,path)).hexdigest()!=sha: raise SystemExit(f"raw hash mismatch {n}:{path}")
    if "C-1 #43" not in text or "C-2 #46" not in text or "D-5 #50" not in text or "E-1 #44" not in text or "E-2 #46" not in text or "F-1 #42" not in text: raise SystemExit("round-2 finding matrix mismatch")
    print("R8_CONSOLIDATED_REMEDIATION_ROUND2_PACKET_PASS")
if __name__=="__main__": check()
