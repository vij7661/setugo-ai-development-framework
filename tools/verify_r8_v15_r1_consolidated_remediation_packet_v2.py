from __future__ import annotations
import hashlib,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
PACKET=ROOT/"governance-r8/R8-V15-R1-CONSOLIDATED-REMEDIATION-52-REVIEW-PACKET-V2.txt"
BASE="7cd2787d85b189a4161f271ee131e42bd961140a"
HEADS={"42":"615e762f97753aa52fb4d4166c9cf3ad73baa91d","43":"c42f18f07b84197836d42ac72c1d22d09f8ac774","44":"424afbe9892aa8a9cc73fc530652662948d30dfc","46":"a8add41bf17efe5c5129607c26f5546963a6eebe","50":"6f6b063432fe5987600df2d508af8443e53d5e67"}
FILES={"42":[".github/workflows/r8-v15-r1-stage2-sg1-activation-gate.yml",".github/workflows/r8-v15-r1-stage2-sg1-review-packet.yml",".github/workflows/r8-v15-r1-stage2-sg1-review003-remediation-packet.yml",".github/workflows/r8-v15-r1-stage2-sg1-review004-remediation-packet.yml","tools/r8_v15_r1_review_contract_parser.py","tools/preflight_r8_v15_r1_stage2_sg1_review.py","tools/validate_r8_v15_r1_stage2_sg1_activation_gate_parser.py","tools/test_r8_v15_r1_review_contract_parser.py","tools/test_r8_v15_r1_stage2_sg1_review_preflight.py"],"43":["tools/r8_v15_r1_stage2_semantic_gap_inventory.py","tools/test_r8_v15_r1_stage2_semantic_gap_inventory.py","governance-r8/R8-V15-R1-STAGE2-SEMANTIC-GAP-INVENTORY.json"],"44":["governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/test_r8_v15_r1_runtime_toctou_hardening.py"],"46":["governance-r8/R8-V15-R1-STAGE1-CHANGED-PATHS-ACCOUNTING.json","tools/r8_evidence_bundle_integrity.py","tools/test_r8_evidence_bundle_integrity.py","governance-runtime/r8_v15_r1_frozen_schema_runtime.py","governance-runtime/test_r8_v15_r1_runtime_toctou_hardening.py"],"50":["governance-r8/CODEX-WORK-QUEUE-51.json","governance-r8/ISSUE-52-CONSOLIDATED-QUEUE-REPORT.md","tools/r8_work_queue.py","tools/test_r8_work_queue.py"]}
def run(*a): return subprocess.check_output(a,cwd=ROOT,text=True).strip()
def raw(rev,path): return subprocess.check_output(("git","show",f"{rev}:{path}"),cwd=ROOT)
def check():
    t=PACKET.read_text(encoding="utf-8")
    if BASE not in t or "REVIEWER OUTPUT CONTRACT" not in t: raise SystemExit("packet identity/reviewer contract missing")
    for n,h in HEADS.items():
        if h not in t: raise SystemExit(f"PR {n} head missing")
        for p in FILES[n]:
            marker=f"FILE_PATH={p}"; starts=[m.start() for m in re.finditer(re.escape(marker),t)]
            if not starts: raise SystemExit(f"missing embedded {p}")
            start=starts[0]; end=t.find("----- END EXACT FILE -----",start)
            block=t[start:end]
            m=re.search(r"FILE_BLOB_SHA1=([0-9a-f]{40})",block)
            if not m or run("git","rev-parse",f"{h}:{p}")!=m.group(1): raise SystemExit(f"blob mismatch {p}")
            rh=re.search(r"FILE_RAW_SHA256=([0-9a-f]{64})",block)
            if not rh or hashlib.sha256(raw(h,p)).hexdigest()!=rh.group(1): raise SystemExit(f"raw sha mismatch {p}")
    print("R8_CONSOLIDATED_REMEDIATION_PACKET_V2_PASS")
if __name__=="__main__": check()
