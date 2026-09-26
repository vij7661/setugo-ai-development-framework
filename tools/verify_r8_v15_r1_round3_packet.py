from __future__ import annotations
import hashlib, re, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='7cd2787d85b189a4161f271ee131e42bd961140a'
HEADS={'#42':'5428f001061f2bac4e6df6ea2debc09be6adfd50','#43':'8d1efb126a87adc4da101cf57d4d26025e9b9b16','#44':'36546975cf733becdbbec5b658a32716f7a1489a','#46':'41d2ed1718d0ad1faf1d8110d19a5ec819eafcad','#50':'12b3235ea2c1f67310f073708458b45b93ada9f5'}
PACKET=ROOT/'governance-r8/R8-V15-R1-CONSOLIDATED-REMEDIATION-53-ROUND3-REVIEW-PACKET.txt'
def run(*a): return subprocess.check_output(['git',*a],cwd=ROOT,stderr=subprocess.STDOUT).decode()
def blob(raw): return hashlib.sha1(f'blob {len(raw)}\\0'.encode()+raw).hexdigest()
def expected_files(h): return [x for x in run('diff','--name-only',BASE,h).splitlines() if x]
def raw(h,p): return subprocess.check_output(['git','show',f'{h}:{p}'],cwd=ROOT)
def main():
    text=PACKET.read_text(encoding='utf-8')
    assert 'SELF-CONTAINED OFFLINE INDEPENDENT-REVIEW PACKET' in text
    assert 'A. OVERALL_DISPOSITION' in text and 'J. FINAL_GATE_TABLE' in text
    assert '36237083781' in text and '36237054540' in text
    assert 'exact new heads is still manual/unavailable' in text
    for pr,h in HEADS.items():
        assert h in text, f'missing head {pr}'
        for p in expected_files(h):
            pat=re.compile(r'^FILE_BEGIN '+re.escape(pr)+r' '+re.escape(p)+r'\nFILE_BLOB_SHA1 ([0-9a-f]{40})\nFILE_RAW_SHA256 ([0-9a-f]{64})\nFILE_BYTES (\d+)\n(.*?)^FILE_END '+re.escape(pr)+r' '+re.escape(p)+r'\n',re.M|re.S)
            ms=list(pat.finditer(text)); assert len(ms)==1, f'missing/duplicate block {pr} {p}: {len(ms)}'
            m=ms[0]; actual=raw(h,p); embedded=m.group(4).encode('utf-8')
            assert int(m.group(3))==len(actual), f'byte count {pr} {p}'
            assert m.group(1)==blob(actual), f'blob embedded {pr} {p}'
            assert m.group(2)==hashlib.sha256(actual).hexdigest(), f'sha embedded {pr} {p}'
            assert embedded==actual, f'bytes mismatch {pr} {p}'
    assert 'H-1 -> #42' in text and 'H-2 -> #42' in text
    assert 'H-3 -> #43' in text and 'H-4 -> #43' in text
    assert 'H-5 -> #44' in text and 'H-6 -> #44' in text
    for x in ['H-7 -> #46','H-8 -> #46','H-9 -> #46','H-10 -> #46','H-14 -> #46','H-11 -> #50','H-12 -> #50','H-13 -> #50','M-2 -> #46','M-5 -> #43','M-6 -> #44','M-7 -> #43']:
        assert x in text, x
    assert 'a78add847f6d4ba8914a66ee00d89422fbaa47f2' in text
    assert 'final packet-bearing commit and packet hash are external identities after commit' in text
    assert 'No merge, activation' in text and 'Fallback-to-3 remains ACTIVE' in text
    print(f'ROUND3_PACKET_VERIFY_PASS files={sum(len(expected_files(h)) for h in HEADS.values())} heads={len(HEADS)}')
if __name__=='__main__': main()
