#!/usr/bin/env python3
"""Verify preregistration identities knowable before packet commit."""
import hashlib, json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md'
def main():
    text=PACKET.read_text(encoding='utf-8'); vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_parent_commit|packet_parent_tree|predecessor_commit|predecessor_tree|exact_source_diff_sha256|source_manifest_sha256|packet_content_identity_schema_version)=(.+)$',text,re.M))
    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_parent_commit','packet_parent_tree','predecessor_commit','predecessor_tree','exact_source_diff_sha256','source_manifest_sha256','packet_content_identity_schema_version'}
    assert subprocess.check_output(['git','rev-parse',vals['reviewed_source_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['reviewed_source_tree']
    assert subprocess.check_output(['git','rev-parse',vals['packet_parent_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['packet_parent_tree']
    assert subprocess.check_output(['git','rev-parse',vals['predecessor_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['predecessor_tree']
    diff=subprocess.run(['git','diff',vals['predecessor_commit'],vals['reviewed_source_commit'],'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md'],cwd=ROOT,text=True,capture_output=True,check=True).stdout
    assert hashlib.sha256(diff.encode()).hexdigest()==vals['exact_source_diff_sha256']
    assert vals['packet_content_identity_schema_version']=='1'
    assert 'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION' in text and 'packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION' in text
    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text()); assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
    assert 'NONE_EVIDENCE_ONLY' in text and 'RQ16_started=false' in text
    assert not re.search(r'^diff --git a/V24-I11-V6-RQ1-RQ16-(PRE|REMEDIATION-5-REVIEW)\.md',text,re.M)
    print(json.dumps({'packet_consistency':'PASS','identity_model':'PASS','RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
