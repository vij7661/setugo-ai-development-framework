# Review Notes — ci-head-guard

This file records an independent review of the Claude-generated `ci-head-guard` artifacts without changing the original source files.

## What was validated

- `settings.snippet.json` parses as valid JSON.
- `ci-head-guard.sh` passes `bash -n` syntax validation.
- The hook is fail-closed when GitHub CLI access or repository context is unavailable.
- It checks GitHub check-runs against the exact local `HEAD` SHA rather than trusting an older CI result.

## Important limitations

1. **Pre-operation HEAD is not post-operation HEAD.** A rebase changes commit SHAs, and a merge can create a new commit. Passing CI for the current pre-operation HEAD does not prove that the resulting rebased or merged commit is healthy. CI must run again for the new HEAD after such an operation.
2. **`gh pr merge` context can differ from local HEAD.** The hook validates the local repository HEAD. That is not necessarily the head SHA of the pull request being merged. A production-grade guard should resolve and validate the actual PR head SHA.
3. **Check-run pagination is not handled.** The GitHub check-runs API is paginated. If a repository has more check-runs than the response page contains, evaluating only the returned page may miss a failing or incomplete check.
4. **Allowed conclusions are policy-specific.** Treating `neutral` and `skipped` as passing may be correct for some repositories but not others. Required-check policy should be explicit.
5. **GitHub Checks may not represent every required status.** Some repositories also use commit-status contexts or external CI systems. The supplied README already notes this and suggests combining those signals.
6. **This is a local agent safeguard, not branch protection.** It can reduce unsafe agent actions, but it should complement—not replace—server-side branch rules, required reviews, required CI, and protected-branch controls.

## Recommended use

Treat the current hook as an experimental safeguard and learning artifact. Before relying on it for release-critical repositories, add pagination, operation-specific SHA resolution, post-operation exact-HEAD validation, and repository-specific required-check policy.
