#!/usr/bin/env python3
"""Verify preregistration identities knowable before packet commit."""
import hashlib, json, re, subprocess
from pathlib import Path
from rq16_manifest import canonical_review_source_files, build_source_manifest, canonical_evidence_files, build_evidence_manifest, manifest_sha256
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'
SOURCE_FILES=canonical_review_source_files(ROOT)
def main():
    text=PACKET.read_text(encoding='utf-8'); vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_parent_commit|packet_parent_tree|predecessor_commit|predecessor_tree|exact_source_diff_sha256|source_manifest_sha256|packet_content_identity_schema_version)=(.+)$',text,re.M))
    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_parent_commit','packet_parent_tree','predecessor_commit','predecessor_tree','exact_source_diff_sha256','source_manifest_sha256','packet_content_identity_schema_version'}
    assert subprocess.check_output(['git','rev-parse',vals['reviewed_source_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['reviewed_source_tree']
    assert subprocess.check_output(['git','rev-parse',vals['packet_parent_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['packet_parent_tree']
    assert subprocess.check_output(['git','rev-parse',vals['predecessor_commit']+'^{tree}'],cwd=ROOT,text=True).strip()==vals['predecessor_tree']
    diff=subprocess.run(['git','diff',vals['predecessor_commit'],vals['reviewed_source_commit'],'--','.',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-5-REVIEW.md',':(exclude)V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md'],cwd=ROOT,text=True,capture_output=True,check=True).stdout
    assert hashlib.sha256(diff.encode()).hexdigest()==vals['exact_source_diff_sha256']
    assert vals['packet_content_identity_schema_version']=='2'
    manifest_match=re.search(r'## Source manifest\n(.*?)(?:\n### |\n## )',text,re.S)
    assert manifest_match, 'source_manifest_section_missing'
    declared=json.loads(manifest_match.group(1).strip())
    expected_manifest=json.loads(build_source_manifest(SOURCE_FILES,ROOT))
    assert declared==expected_manifest, 'source_manifest_entries_mismatch'
    manifest=build_source_manifest(SOURCE_FILES,ROOT)
    assert manifest_sha256(manifest)==vals['source_manifest_sha256'], 'source_manifest_hash_mismatch'
    evidence_match=re.search(r'## Generated evidence manifest\n(.*?)(?:\n### |\n## )',text,re.S); assert evidence_match, 'evidence_manifest_section_missing'
    assert json.loads(evidence_match.group(1).strip())==json.loads(build_evidence_manifest(ROOT)), 'evidence_manifest_entries_mismatch'
    tests=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json').read_text()); muts=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json').read_text())
    assert tests['tests_total']==tests['tests_passed']+tests['tests_failed'] and tests['exit_code']==0, 'test_result_binding_mismatch'
    assert muts['total_mutations']==len(muts['mutations']) and muts['rejected_mutations']+muts['surviving_mutations']==muts['total_mutations'] and muts['all_rejected']==(muts['surviving_mutations']==0), 'mutation_result_binding_mismatch'
    assert 'packet_commit=EXTERNALLY_BOUND_AFTER_GENERATION' in text and 'packet_tree=EXTERNALLY_BOUND_AFTER_GENERATION' in text
    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text()); assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
    assert 'NONE_EVIDENCE_ONLY' in text and 'RQ16_started=false' in text
    assert not re.search(r'^diff --git a/V24-I11-V6-RQ1-RQ16-(PRE|REMEDIATION-[56]-REVIEW)\.md',text,re.M)
    print(json.dumps({'packet_consistency':'PASS','identity_model':'PASS','RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
