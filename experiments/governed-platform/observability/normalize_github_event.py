#!/usr/bin/env python3
"""Normalize a GitHub Actions execution snapshot into dashboard state.

Input is deliberately provider-neutral JSON produced by the workflow. Protected truth
is never accepted by this adapter.
"""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

ALLOWED = {"CODE DEFECT", "FIXTURE-DATA DEFECT", "TEST DEFECT", "ENVIRONMENT-TOOLING DEFECT", "REQUIREMENT UNRESOLVED", "NONE"}

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument('--event', required=True); p.add_argument('--out', required=True)
    a=p.parse_args(); e=json.loads(Path(a.event).read_text(encoding='utf-8'))
    required=('campaign','experiment','case_id','branch','execution_sha','run_id','jobs')
    missing=[k for k in required if k not in e]
    if missing: raise SystemExit('missing authoritative fields: '+','.join(missing))
    conclusions=[j.get('conclusion') for j in e['jobs']]
    if any(x in {'failure','timed_out'} for x in conclusions): status='FAILED'
    elif any(x in {'queued','in_progress',None} for x in conclusions): status='EXECUTING'
    elif conclusions and all(x in {'success','skipped'} for x in conclusions): status='COMPLETE'
    else: status='BLOCKED'
    classification=e.get('failure_classification','NONE')
    if classification not in ALLOWED: raise SystemExit('invalid failure classification')
    state={
      'schema_version':'1.0','campaign':e['campaign'],'experiment':e['experiment'],'case_id':e['case_id'],
      'execution_status':status,'scientific_status':e.get('scientific_status','AWAITING_ADJUDICATION'),
      'branch':e['branch'],'execution_sha':e['execution_sha'],'run_id':e['run_id'],'jobs':e['jobs'],
      'failure_classification':classification,'controller_decision':e.get('controller_decision','UNKNOWN'),
      'repair_attempt':e.get('repair_attempt',0),'max_repair_attempts':e.get('max_repair_attempts',2),
      'next_case':e.get('next_case'),'human_required':bool(e.get('human_required',False)),
      'human_reason':e.get('human_reason'),'updated_at':datetime.now(timezone.utc).isoformat()
    }
    Path(a.out).write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8'); return 0
if __name__=='__main__': raise SystemExit(main())
