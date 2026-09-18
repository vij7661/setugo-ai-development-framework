#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, stat, subprocess
from pathlib import Path

SERVICE = Path("/opt/v24-v6-trusted-runtime/v24_v6_trusted_authority_service")
GATE = Path("/opt/v24-v6-trusted-runtime/.gate-build/v24_v6_external_authority_gate")
UNIT = Path("/etc/systemd/system/v24-v6-trusted-authority.service")
SOCKET = Path("/run/v24-v6-authority/service.sock")
PID = Path("/run/v24-v6-authority/service.pid")
RECORDS = Path("/run/v24-v6-authority/private/records")
CONSUMED = Path("/run/v24-v6-authority/private/consumed")

def sha256(path: Path):
    try:
        h=hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda:f.read(1024*1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None

def meta(path: Path):
    try:
        s=path.lstat()
        return {"exists":True,"uid":s.st_uid,"gid":s.st_gid,
                "mode":oct(stat.S_IMODE(s.st_mode)),"inode":s.st_ino,
                "device":s.st_dev,"sha256":sha256(path) if path.is_file() else None,
                "is_socket":stat.S_ISSOCK(s.st_mode),"is_symlink":stat.S_ISLNK(s.st_mode)}
    except OSError as exc:
        return {"exists":False,"error":repr(exc)}

def dir_hashes(path: Path):
    out=[]
    try:
        for p in sorted(path.iterdir(), key=lambda x:x.name):
            s=p.lstat()
            out.append({"name":p.name,"uid":s.st_uid,"gid":s.st_gid,
                        "mode":oct(stat.S_IMODE(s.st_mode)),
                        "sha256":sha256(p) if p.is_file() else None})
    except OSError as exc:
        return {"error":repr(exc),"entries":[]}
    return {"entries":out}

def cmd(*argv):
    p=subprocess.run(argv,text=True,capture_output=True,check=False)
    return {"rc":p.returncode,"stdout":p.stdout.strip(),"stderr":p.stderr.strip()}

pid=None
try: pid=int(PID.read_text().strip())
except Exception: pass
payload={"service":meta(SERVICE),"gate":meta(GATE),"unit":meta(UNIT),"socket":meta(SOCKET),
         "records":dir_hashes(RECORDS),"consumed":dir_hashes(CONSUMED),"service_pid":pid,
         "service_active":cmd("systemctl","is-active","v24-v6-trusted-authority.service"),
         "service_enabled":cmd("systemctl","is-enabled","v24-v6-trusted-authority.service"),
         "sysctls":{}}
for key in ["fs.suid_dumpable","kernel.unprivileged_userns_clone","kernel.yama.ptrace_scope",
            "kernel.dmesg_restrict","kernel.kptr_restrict"]:
    payload["sysctls"][key]=cmd("sysctl","-n",key)
if pid:
    try:
        lines=Path(f"/proc/{pid}/status").read_text().splitlines()
        payload["service_uid_line"]=next((x for x in lines if x.startswith("Uid:")),None)
    except OSError as exc:
        payload["service_uid_error"]=repr(exc)
print(json.dumps(payload,sort_keys=True,separators=(",",":")))
