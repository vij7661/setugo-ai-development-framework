#!/usr/bin/env python3
"""Structured unittest child runner for IG-1 Successor3."""
from __future__ import annotations
import json
import pathlib
import sys
import unittest

SENTINEL="__IG1_S3_UNITTEST_RESULT__"

def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: child.py TARGET TEST_FILE...")
    root=pathlib.Path(sys.argv[1]).resolve()
    files=sys.argv[2:]
    sys.path.insert(0,str(root/"governance-runtime"))
    modules=[pathlib.Path(f).stem for f in files]
    suite=unittest.defaultTestLoader.loadTestsFromNames(modules)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    data={
      "testsRun":result.testsRun,
      "failures":len(result.failures),
      "errors":len(result.errors),
      "skipped":len(getattr(result,"skipped",[])),
      "expectedFailures":len(getattr(result,"expectedFailures",[])),
      "unexpectedSuccesses":len(getattr(result,"unexpectedSuccesses",[])),
      "successful":result.wasSuccessful(),
    }
    print(SENTINEL+json.dumps(data,sort_keys=True))
    ok=data["successful"] and all(data[k]==0 for k in ("failures","errors","skipped","expectedFailures","unexpectedSuccesses"))
    raise SystemExit(0 if ok else 1)

if __name__=="__main__":
    main()
