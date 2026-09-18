# RQ1 Remediation-2 workspace-hygiene root cause

Historical failure: workflow `35405012362` failed in `actions/checkout@v4` while
`git clean -ffdx` attempted to remove root-owned files under
`governance-runtime/__pycache__`; checkout then failed with `EACCES` unlink
errors. No RQ case executed. This remains immutable infrastructure evidence.

## Root cause

The root trusted-consume path in
`governance-runtime/v24_v6_rq1_remediation2_harness.py` invoked
`sudo -u root -- env PYTHONPATH=<checkout>/governance-runtime python3 ...`.
That process imported repository Python modules while its current module search
path was inside the checkout, so Python bytecode was written as root-owned
`__pycache__/*.pyc` files. The next self-hosted checkout cleanup could not
remove those files as the runner user.

Classification: `INFRASTRUCTURE_DEFECT / WORKSPACE_HYGIENE_DEFECT`.
This is not a trusted-service mechanism result and no RQ outcome is inferred.

## Narrow repair

Root-context subprocesses now receive `PYTHONDONTWRITEBYTECODE=1`; the trusted
consumer additionally invokes `python3 -B`. The workflow uses
`actions/checkout` with `clean: false`, then performs a bounded cleanup only
within `$GITHUB_WORKSPACE/governance-runtime` for stale `*.pyc` files and empty
`__pycache__` directories, verifies none remain, and records the result.
Runner installation/state and all paths outside the checked-out tree are out of
scope. Evidence staging/upload is gated on successful checkout/preparation so a
checkout failure cannot be obscured by unset `EVIDENCE_DIR` follow-on errors.

The 9-case exact-safe evidence and all prior failures remain append-only.
Governance remains `NOT_QUALIFIED`, `CLOSED_PENDING_SUCCESSOR_REVIEW`, and
`NONE_EVIDENCE_ONLY`.
