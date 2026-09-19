#!/usr/bin/env python3
"""Generate the single authoritative offline RQ-16 test and mutation results."""
import json, re, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TEST_OUT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-TEST-RESULTS.json'
MUT_OUT=ROOT/'implementation/v24/V24-I11-V6-RQ1-RQ16-MUTATION-RESULTS.json'
def main():
    t=subprocess.run(['python','governance-runtime/test_v24_v6_rq1_rq16_harness.py'],cwd=ROOT,text=True,capture_output=True)
    m=subprocess.run(['python','governance-runtime/run_v24_v6_rq1_rq16_mutations.py'],cwd=ROOT,text=True,capture_output=True)
    match=re.search(r'Ran (\d+) tests?',t.stderr+t.stdout); total=int(match.group(1)) if match else 0
    tests=[]
    for line in (t.stderr+t.stdout).splitlines():
        hit=re.match(r'test_\w+ \(__main__\.[^)]+\) \.\.\. (ok|FAIL)',line)
        if hit: tests.append({'name':line.split(' (',1)[0],'result':'PASS' if hit.group(1)=='ok' else 'FAIL'})
    test_result={'tests_total':total,'tests_passed':sum(x['result']=='PASS' for x in tests),'tests_failed':sum(x['result']=='FAIL' for x in tests),'exit_code':t.returncode,'tests':tests,'stdout':t.stdout,'stderr':t.stderr}
    mutation_result=json.loads(m.stdout)
    mutation_result['exit_code']=m.returncode
    TEST_OUT.write_text(json.dumps(test_result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    MUT_OUT.write_text(json.dumps(mutation_result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'tests_total':test_result['tests_total'],'tests_passed':test_result['tests_passed'],'tests_failed':test_result['tests_failed'],'mutation_total':mutation_result['total_mutations'],'mutation_rejected':mutation_result['rejected_mutations'],'mutation_surviving':mutation_result['surviving_mutations'],'all_rejected':mutation_result['all_rejected']},indent=2))
    return 0 if t.returncode==0 and m.returncode==0 else 1
if __name__=='__main__': raise SystemExit(main())
