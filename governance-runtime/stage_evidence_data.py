"""Copy a fixed evidence allowlist without importing or executing evidence-ref content."""
from __future__ import annotations
import argparse,os,shutil
from pathlib import Path
ALLOWLIST=("receipt-spec.json","blob-map.json","artifact-locations.json","freeze-attestation.json","independent-review.txt","governed-receipt.json","expected-identity.json")
def stage(source:Path,destination:Path,names=ALLOWLIST):
 source=source.resolve();destination.mkdir(parents=True,exist_ok=True)
 for name in names:
  if name not in ALLOWLIST or Path(name).name!=name:raise ValueError("evidence path is not allowlisted")
  item=source/name
  if item.is_symlink() or not item.is_file() or item.resolve().parent!=source:raise ValueError(f"unsafe or missing evidence file: {name}")
  target=destination/name;shutil.copyfile(item,target)
  if os.name!="nt":os.chmod(target,0o444)
def main():
 p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--destination",required=True);p.add_argument("names",nargs="+");a=p.parse_args();stage(Path(a.source),Path(a.destination),tuple(a.names))
if __name__=="__main__":main()
