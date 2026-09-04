#!/usr/bin/env python3
"""Provider-independent bounded failover router for governed reasoning tasks."""
from __future__ import annotations
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
from adapters import normalize_adapter_result
from openai_compatible import OpenAICompatibleAdapter,RemoteProviderConfig
from prepare_run import prepare

def load(path:Path): return json.loads(path.read_text(encoding='utf-8'))
def now(): return datetime.now(timezone.utc).isoformat()

def main()->int:
 p=argparse.ArgumentParser();p.add_argument('--case',required=True,type=Path);p.add_argument('--mechanisms',required=True,type=Path);p.add_argument('--order',required=True);p.add_argument('--instruction-version',required=True);p.add_argument('--out',required=True,type=Path);p.add_argument('--evidence-out',required=True,type=Path);a=p.parse_args()
 case=load(a.case);registry={m['mechanism_id']:m for m in load(a.mechanisms)['mechanisms']};order=[x.strip() for x in a.order.split(',') if x.strip()];attempts=[];selected=None;normalized=None
 for index,mechanism_id in enumerate(order):
  m=registry.get(mechanism_id)
  if not m or not m.get('enabled'):
   attempts.append({'mechanism_id':mechanism_id,'provider':m.get('provider') if m else None,'status':'NOT_CALLED','reason':'missing-or-disabled','updated_at':now()});continue
  envelope=prepare(case,m,a.instruction_version);started=now()
  try:
   adapter=OpenAICompatibleAdapter(RemoteProviderConfig(provider_id=m['provider'],base_url=m['base_url'],model=m['model'],api_key_env=m['api_key_env']))
   result=adapter.invoke(envelope);normalized=normalize_adapter_result(envelope,result);selected=mechanism_id
   attempts.append({'mechanism_id':mechanism_id,'provider':m['provider'],'status':'SUCCESS','model':m['model'],'run_id':normalized['run_id'],'attempts':getattr(result,'attempts',None) or 1,'started_at':started,'updated_at':now()})
   for later in order[index+1:]:
    lm=registry.get(later);attempts.append({'mechanism_id':later,'provider':lm.get('provider') if lm else None,'status':'NOT_CALLED','model':lm.get('model') if lm else None,'attempts':0,'reason':'first qualified success already obtained','updated_at':now()})
   break
  except Exception as exc:
   text=str(exc);count=3 if 'attempt 3/3' in text else None
   attempts.append({'mechanism_id':mechanism_id,'provider':m['provider'],'status':'FAILED','model':m['model'],'run_id':envelope['run_id'],'attempts':count,'started_at':started,'updated_at':now(),'reason':text[:1000]})
 evidence={'event_type':'PROVIDER_ROUTING_COMPLETED','updated_at':now(),'case_id':case.get('case_id'),'instruction_version':a.instruction_version,'selected_mechanism':selected,'attempts':attempts,'portfolio_exhausted':selected is None,'routing_rule':'QUALIFIED_FIRST_SUCCESS'}
 a.evidence_out.parent.mkdir(parents=True,exist_ok=True);a.evidence_out.write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
 if normalized is None: raise RuntimeError('eligible provider portfolio exhausted without usable completion')
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(normalized,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print(a.out);return 0
if __name__=='__main__': raise SystemExit(main())
