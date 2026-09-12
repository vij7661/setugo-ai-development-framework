# EXP-ECC-5 — Cross-Harness Tool/MCP Configuration Attestation and Drift

Status: **PREREGISTERED — NOT EXECUTED**

Authority effect: **NONE_EVIDENCE_ONLY**

Baseline: `290ac043959f30db12c9ae16826eda1dd5bcbdfb`

## Hypothesis

Tool/MCP configuration is part of the effective execution authority surface. A tool/server keeping the same human-readable name does not preserve qualification if transport, endpoint, permissions, arguments, environment, credentials, or harness binding changes.

## Required mechanism

A secret-safe `ToolConfigurationAttestation` canonically binds tool/server ID, harness, transport, endpoint identity, executable/argv where applicable, permission profile, credential-profile identity (never raw secret), environment-key allowlist, version/digest, configuration sequence, and dependent capability qualifications.

Configuration drift must stale affected qualifications and trigger policy-defined revalidation before consequential use.

## Falsification cases

- E5-01 same MCP display name points to a different endpoint.
- E5-02 transport changes from local stdio to remote network without requalification.
- E5-03 permission scope widens but configuration name/version label does not.
- E5-04 executable/argv changes while old attestation is replayed.
- E5-05 credential profile changes to a broader account without revalidation.
- E5-06 one harness has different effective MCP configuration but inherits another harness's qualification.
- E5-07 secret redaction changes the canonical identity so two materially different configs collide.
- E5-08 drift is detected but downstream role/capability remains current.
- E5-09 configuration read fails and missing evidence is interpreted as unchanged.

## Positive controls

- E5-P1 identical canonical configuration across restart preserves qualification where policy permits.
- E5-P2 benign metadata-only change that does not affect the governed canonical identity does not force unnecessary invalidation.
- E5-P3 changed config is re-attested/requalified and then valid use resumes.

## Pass condition

A consequential tool/MCP invocation cannot rely on stale or cross-harness configuration qualification, and unknown configuration state is never interpreted as unchanged/safe.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
