# EXP-O Pilot 27 — Second Pre-execution Harness Failure Record

## Run

GitHub Actions run `34034783378` at commit `1e0b69b96c9ae88f6964a0a404ba5e20ddb7d936`.

## Classification

TEST HARNESS / DYNAMIC-IMPORT BOOTSTRAP DEFECT. NOT A PILOT 27 SCIENTIFIC EXECUTION AND NOT A DOMAIN-QUORUM MECHANISM FAILURE.

The prior dotted-package import defect was removed, and the Pilot 27 module again compiled successfully. The governance suite still failed before executing any Pilot 27 assertion because the test's `importlib.util.spec_from_file_location` bootstrap executed a module containing `@dataclass` before registering that module object in `sys.modules`.

Observed failure:

`AttributeError: 'NoneType' object has no attribute '__dict__'`

from Python `dataclasses._is_type`, which evaluates `sys.modules.get(cls.__module__)` during class processing.

## Allowed repair

Only register the dynamically loaded test module in `sys.modules` before `SPEC.loader.exec_module(MODULE)`. No Pilot 27 preregistered endpoint, canonical statement, administrative-domain distinctness rule, threshold rule, workload-identity separation rule, or provider requirement may change.

## Scientific status

Pilot 27 remains PRE-EXECUTION / EXTERNALLY BLOCKED. No external signing provider was called and this run produced no scientific endpoint evidence.
