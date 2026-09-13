"""Fail-closed governed Git identity verification for authority-bearing commit bindings."""
from __future__ import annotations

from pathlib import Path
import re
import subprocess

SHA40=re.compile(r"^[0-9a-f]{40}$")

def _git(repo_root:Path,*args:str)->str:
    proc=subprocess.run(["git","-C",str(repo_root),*args],capture_output=True,text=True,check=False)
    if proc.returncode!=0:
        raise ValueError(f"git {' '.join(args)} failed")
    return proc.stdout.strip()

def _remote_matches(remote:str,expected_repository:str)->bool:
    cleaned=remote.strip().removesuffix(".git").replace("\\","/")
    expected=expected_repository.strip("/")
    return cleaned.endswith("/"+expected) or cleaned.endswith(":"+expected)

def verify_governed_commit(*,repo_root:str|Path,expected_repository:str,commit:str,expected_head:str|None=None)->tuple[bool,str]:
    try:
        root=Path(repo_root).resolve(strict=True)
        if not SHA40.fullmatch(str(commit)):return False,"commit is not an exact lowercase 40-character Git SHA"
        if not (root/".git").exists():return False,"governed repository root is not a Git worktree"
        remote=_git(root,"config","--get","remote.origin.url")
        if not _remote_matches(remote,expected_repository):return False,"governed repository origin mismatch"
        resolved=_git(root,"rev-parse","--verify",f"{commit}^{{commit}}")
        if resolved!=commit:return False,"commit does not resolve to the exact governed Git commit"
        if expected_head is not None:
            if not SHA40.fullmatch(str(expected_head)):return False,"expected head is not an exact Git SHA"
            head=_git(root,"rev-parse","HEAD")
            if head!=expected_head:return False,"governed repository HEAD differs from authoritative head"
            if commit!=expected_head:return False,"reviewed commit differs from authoritative head"
        return True,"governed Git commit verified"
    except (OSError,ValueError):
        return False,"governed Git commit verification failed"

def read_governed_file_at_commit(*,repo_root:str|Path,expected_repository:str,commit:str,path:str)->tuple[bool,bytes|None,str]:
    ok,reason=verify_governed_commit(repo_root=repo_root,expected_repository=expected_repository,commit=commit)
    if not ok:return False,None,reason
    if not isinstance(path,str) or not path or path.startswith("/") or ".." in Path(path).parts:
        return False,None,"governed Git path is invalid"
    try:
        root=Path(repo_root).resolve(strict=True)
        proc=subprocess.run(["git","-C",str(root),"show",f"{commit}:{path}"],capture_output=True,check=False)
        if proc.returncode!=0:return False,None,"governed Git path does not exist at commit"
        return True,proc.stdout,"governed Git path verified"
    except OSError:
        return False,None,"governed Git path verification failed"

def verify_governed_ref_commit(*,repo_root:str|Path,expected_repository:str,ref_name:str,commit:str)->tuple[bool,str]:
    ok,reason=verify_governed_commit(repo_root=repo_root,expected_repository=expected_repository,commit=commit)
    if not ok:return False,reason
    if not isinstance(ref_name,str) or not ref_name or ref_name.startswith("-"):
        return False,"governed Git ref name is invalid"
    try:
        root=Path(repo_root).resolve(strict=True)
        candidates=(f"refs/heads/{ref_name}",f"refs/remotes/origin/{ref_name}")
        resolved=[]
        for candidate in candidates:
            proc=subprocess.run(["git","-C",str(root),"rev-parse","--verify",candidate],capture_output=True,text=True,check=False)
            if proc.returncode==0:resolved.append(proc.stdout.strip())
        if not resolved:return False,"governed Git branch ref is unavailable"
        if commit not in resolved:return False,"governed Git branch ref differs from bound commit"
        return True,"governed Git branch binding verified"
    except OSError:
        return False,"governed Git branch verification failed"
