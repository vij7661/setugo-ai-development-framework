#!/usr/bin/env python3
"""Offline packet consistency checks; no runtime interaction."""
from __future__ import annotations
import json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    contract=json.loads((ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-EXECUTION-CONTRACT.json').read_text())
    assert contract['RQ16_EXECUTED'] is False and contract['RQ16_AUTHORIZED'] is False
    assert contract['governance']=='NOT_QUALIFIED,CLOSED_PENDING_SUCCESSOR_REVIEW,NONE_EVIDENCE_ONLY'
    assert set(contract['arms'])=={'ENOSPC','EROFS','EIO','EACCES'}
    for arm, spec in contract['arms'].items(): assert spec['classification'] in {'INSUFFICIENT_EVIDENCE','UNSAFE','PROXY_NOT_ACCEPTABLE','AUTHORIZATION_CANDIDATE'}
    packet=ROOT/'V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REVIEW.md'; text=packet.read_text(encoding='utf-8')
    import re, subprocess
    vals=dict(re.findall(r'^(reviewed_source_commit|reviewed_source_tree|packet_commit|packet_tree|predecessor_commit|predecessor_tree|exact_diff_sha256)=(.+)$',text,re.M))
    assert set(vals)=={'reviewed_source_commit','reviewed_source_tree','packet_commit','packet_tree','predecessor_commit','predecessor_tree','exact_diff_sha256'}
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert subprocess.run(['git','merge-base','--is-ancestor',vals['packet_commit'],head],cwd=ROOT).returncode==0
    assert vals['predecessor_commit']=='8477830f5f35a35a8c9b19fdca9c5b6c39e2916d' and vals['predecessor_tree']=='82457b9307f133db281055dbbdae26b618f8c3cf'
    assert 'RQ16_EXECUTED=false' in text and 'RQ16_AUTHORIZED=false' in text and 'NONE_EVIDENCE_ONLY' in text
    print(json.dumps({'packet_consistency':'PASS','arm_count':4,'RQ16_EXECUTED':False,'RQ16_AUTHORIZED':False},indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
