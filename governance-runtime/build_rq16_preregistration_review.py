from __future__ import annotations
import hashlib, os, subprocess
from pathlib import Path
from rq16_manifest import canonical_review_source_files, canonical_evidence_files, build_source_manifest, build_evidence_manifest, manifest_sha256
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-7-FINAL-REVIEW.md'
PACKET_CHECK_CURRENT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PACKET-CHECK-CURRENT.json'
FILES=canonical_review_source_files(ROOT)
EVIDENCE_FILES=canonical_evidence_files(ROOT)
def run(cmd): return subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def fence(name,body,lang='text'): return f'\n### {name}\n\n```{lang}\n{body.rstrip()}\n```\n'
def main():
    if not PACKET_CHECK_CURRENT.exists(): PACKET_CHECK_CURRENT.write_text('{"status":"PENDING"}\n',encoding='utf-8')
    current=run(['git','rev-parse','HEAD']).stdout.strip(); current_tree=run(['git','rev-parse','HEAD^{tree}']).stdout.strip(); reviewed=os.environ.get('REVIEWED_SOURCE_COMMIT',current); reviewed_tree=os.environ.get('REVIEWED_SOURCE_TREE',run(['git','rev-parse',f'{reviewed}^{{tree}}']).stdout.strip()); predecessor='8477830f5f35a35a8c9b19fdca9c5b6c39e2916d'; packet_parent=current; packet_parent_tree=current_tree
    diff=run(['git','diff',predecessor,reviewed,'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md']).stdout
    tests=run(['python','governance-runtime/collect_rq16_results.py']); mutations=run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py']); selftest=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--self-test']); plan=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--plan']); refuse=run(['python','governance-runtime/v24_v6_rq1_rq16_harness.py','--execute-rq16']); consistency=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
    def render(packet_check_json):
        source_manifest=build_source_manifest(FILES,ROOT); evidence_manifest=build_evidence_manifest(ROOT); ids=[f'reviewed_source_commit={reviewed}',f'reviewed_source_tree={reviewed_tree}',f'packet_parent_commit={packet_parent}',f'packet_parent_tree={packet_parent_tree}',f'predecessor_commit={predecessor}','predecessor_tree=82457b9307f133db281055dbbdae26b618f8c3cf',f'exact_source_diff_sha256={hashlib.sha256(diff.encode()).hexdigest()}',f'source_manifest_sha256={manifest_sha256(source_manifest)}',f'generated_evidence_manifest_sha256={manifest_sha256(evidence_manifest)}','packet_content_identity_schema_version=3']
        parts=['# V24-I11-V6 RQ-16 preregistration remediation-7 final review','','Planning-only artifact. No RQ-16 execution occurred.','','## Identity',*ids,f"branch={run(['git','branch','--show-current']).stdout.strip()}",'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION','packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION','packet_file_sha256=EXTERNALLY_BOUND_AFTER_GENERATION','RQ16_EXECUTED=false','RQ16_AUTHORIZED=false','RQ16_started=false','scientific_rerun=false','qualification=NOT_QUALIFIED','scientific_execution_state=CLOSED_PENDING_SUCCESSOR_REVIEW','authority_effect=NONE_EVIDENCE_ONLY','', '## Frozen contract', fence('execution contract',FILES[2].read_text(),'json'), '## Source-path analysis', fence('preregistration',FILES[5].read_text(),'markdown'), '## Cleanup contract', fence('cleanup',FILES[1].read_text(),'markdown'), '## Issues', fence('issue ledger',FILES[4].read_text(),'json'), '## Source manifest',source_manifest,'## Generated evidence manifest',evidence_manifest]
        for p in FILES: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'python'))
        for p in EVIDENCE_FILES: parts.append(fence(p.relative_to(ROOT).as_posix()+f' sha256={sha(p)}',p.read_text(),'json'))
        parts += ['## Static and behavioral results',fence('plan',plan.stdout+plan.stderr),fence('self-test',selftest.stdout+selftest.stderr),fence('tests',tests.stdout+tests.stderr),fence('mutations',mutations.stdout+mutations.stderr,'json'),fence('packet-check-current',packet_check_json,'json'),fence('execution-refusal',refuse.stdout+refuse.stderr), '## Exact predecessor-to-reviewed-source diff', fence('diff',diff), '## Manual-review questions','Historical packet consistency failure source_manifest_entries_mismatch was fixed and superseded; no failed traceback is current evidence. Determine independently whether any arm has safe literal Linux bound-runtime capability. No arm is authorized; do not execute RQ-16.']
        OUT.write_text('\n'.join(parts)+'\n',encoding='utf-8')
    render('{"status":"PENDING"}\n')
    current_check=run(['python','governance-runtime/check_rq16_preregistration_packet.py','--allow-pending'])
    if current_check.returncode != 0: raise SystemExit(current_check.stderr or current_check.stdout)
    packet_check_json=current_check.stdout.strip()+'\n'
    PACKET_CHECK_CURRENT.write_text(packet_check_json,encoding='utf-8')
    render(packet_check_json)
    final_check=run(['python','governance-runtime/check_rq16_preregistration_packet.py'])
    if final_check.returncode != 0: raise SystemExit(final_check.stderr or final_check.stdout)
    print(OUT)
if __name__=='__main__': main()
