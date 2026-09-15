# V15 — Independent Evidence Package RED 001

Status: **PRESERVED PACKAGE-BUILDER RED / CANDIDATE UNCHANGED**

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`

## Bound run

- package workflow run: `34948998139`
- review metadata commit: `b45862cab905c9f74ac1fd00fda637ab8531a99e`
- frozen candidate commit: `380e1d9db083a6477691bf187d5cba7c61eee280`
- frozen candidate tree: `6bdd7bf8ec214e406383e084bd7c28b8c9738ee9`

## What passed before failure

The workflow successfully:

1. fetched and verified the exact frozen candidate commit/tree;
2. independently derived exactly 30 changed candidate files against baseline `87f6e3df73c0c70c5d8ff4da38365ff92721aff7`;
3. staged those exact candidate bytes plus neutral review instructions and the freeze record;
4. fetched and validated the expected SUCCESS/FAILURE conclusions for all ten construction runs.

## Failure endpoint

The workflow failed while retrieving raw GitHub Actions job logs using `gh api`.

The GitHub CLI refused to print the log response because it contained terminal escape sequences and required the explicit `--allow-escape-sequences` option. The candidate mechanism, tests, evidence bindings and package manifest/build steps were not implicated. The later package-build/upload steps did not execute and must not be inferred PASS.

## Classification

`PACKAGE_BUILDER_TRANSPORT_OUTPUT_GUARD_BEFORE_PACKAGE_COMPLETION`

## Narrow correction

Change only raw job-log retrieval to explicitly allow the already-authenticated log bytes to be emitted by `gh api`, then rerun the same package workflow. Do not alter the frozen candidate or its construction evidence.

- candidate implementation remains frozen;
- implementation qualification remains `NOT_CLAIMED`;
- runtime qualification remains `NOT_CLAIMED`;
- scientific execution remains `CLOSED_PENDING_INDEPENDENT_EVIDENCE_REVIEW`.

`AUTHORITY_EFFECT = NONE_EVIDENCE_ONLY`
