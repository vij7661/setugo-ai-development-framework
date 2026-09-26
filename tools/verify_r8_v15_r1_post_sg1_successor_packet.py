import hashlib,re,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1]; BASE='7cd2787d85b189a4161f271ee131e42bd961140a'; HEAD='b73f2eb2fd44f97a53f3b39307fd92175330325d'; P=R/'governance-r8/R8-V15-R1-POST-SG1-SUCCESSOR1-REVIEW-PACKET.txt'
def run(*a): return subprocess.check_output(['git',*a],cwd=R).decode()
def files(): return [p for p in run('diff','--name-only',BASE,HEAD).splitlines() if p]
def raw(p): return subprocess.check_output(['git','show',f'{HEAD}:{p}'],cwd=R)
def main():
 t=P.read_text(encoding='utf8'); assert 'DO NOT STOP AFTER FIRST FINDING' in t and 'Return ONLY sections A-J.' in t
 assert HEAD in t and '99fad2453dc849598e95497c1f0d6edf8cf34b36' in t and 'HISTORICAL_STAGE1_BOUND_EVIDENCE' in t
 assert 'Linux-bound evidence for exact successor unavailable' in t
 for p in files():
  pat=re.compile(r'^FILE_BEGIN '+re.escape(p)+r'\nFILE_BLOB_SHA1 ([0-9a-f]{40})\nFILE_RAW_SHA256 ([0-9a-f]{64})\nFILE_BYTES (\d+)\n(.*?)^FILE_END '+re.escape(p)+r'\n',re.M|re.S); m=pat.search(t); assert m, p
  b=raw(p); expected=subprocess.check_output(['git','hash-object','--stdin'],input=b,cwd=R).decode().strip(); assert m.group(1)==expected and m.group(2)==hashlib.sha256(b).hexdigest() and int(m.group(3))==len(b) and m.group(4).encode()==b, p
 print(f'POST_SG1_SUCCESSOR_PACKET_VERIFY_PASS files={len(files())}')
if __name__=='__main__': main()
