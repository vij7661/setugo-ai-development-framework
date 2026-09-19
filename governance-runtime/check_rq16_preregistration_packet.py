#!/usr/bin/env python3
"""Verify preregistration identities knowable before packet commit."""
import hashlib, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'
SOURCE_FILES=[ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-CLEANUP-CONTRACT.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-PREREGISTRATION-ISSUES.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-AUTHORIZATION-TOKEN-SCHEMA.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-NONCE-LEDGER-DESIGN.md',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-READONLY-CAPABILITY-INSPECTION.md',ROOT/'governance-runtime/v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/test_v24_v6_rq1_rq16_harness.py',ROOT/'governance-runtime/run_v24_v6_rq1_rq16_mutations.py',ROOT/'governance-runtime/check_rq16_preregistration_packet.py',ROOT/'governance-runtime/collect_rq16_results.py',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json',ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json']
def main():
    text=PACKET.read_text(encoding='utf-8'); vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_parent_commit|packet_parent_tree|predecessor_commit|predecessor_tree|exact_source_diff_sha256|source_manifest_sha256|packet_content_identity_schema_version)=(.+)$',text,re.M))
    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_parent_commit','packet_parent_tree','predecessor_commit','predecessor_tree','exact_source_diff_sha256','source_manifest_sha256','packet_content_identity_schema_version'}
    assert subprocess.check_output(['git','rev-parse',vals['reviewed_source_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['reviewed_source_tree']
    assert subprocess.check_output(['git','rev-parse',vals['packet_parent_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['packet_parent_tree']
    assert subprocess.check_output(['git','rev-parse',vals['predecessor_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['predecessor_tree']
    diff=subprocess.run(['git','diff',vals['predecessor_commit'],vals['reviewed_source_commit'],'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'],cwd=ROOT,text=True,capture_output=True,check=True).stdout
    assert hashlib.sha256(diff.encode()).hexdigest()==vals['exact_source_diff_sha256']
    assert vals['packet_content_identity_schema_version']=='1'
    manifest_match=re.search(r'## Included file SHA-256\n(.*?)(?:\n### |\n## )',text,re.S)
    assert manifest_match, 'source_manifest_section_missing'
    declared=[]
    for line in manifest_match.group(1).strip().splitlines():
        hit=re.fullmatch(r'([0-9a-f]{64})  (.+)',line.strip()); assert hit, f'malformed_manifest_line:{line}'; declared.append((hit.group(2),hit.group(1)))
    expected_manifest=sorted((p.relative_to(ROOT).as_posix(),hashlib.sha256(p.read_bytes()).hexdigest()) for p in SOURCE_FILES)
    assert sorted(declared)==expected_manifest, 'source_manifest_entries_mismatch'
    manifest='\n'.join(f'{h}  {path}' for path,h in expected_manifest)
    assert hashlib.sha256(manifest.encode()).hexdigest()==vals['source_manifest_sha256'], 'source_manifest_hash_mismatch'
    assert 'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION' in text and 'packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION' in text
    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text()); assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
    assert 'NONE_EVIDENCE_ONLY' in text and 'RQ16_started=false' in text
    assert not re.search(r'^diff --git a/V24-I11-V6-RQ1-RQ16-(PRE|REMEDIATION-[56]-REVIEW)\.md',text,re.M)
    print(json.dumps({'packet_consistency':'PASS','identity_model':'PASS','RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
