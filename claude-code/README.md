# ci-head-guard

A Claude Code `PreToolUse` hook that blocks `git merge`, `git rebase`,
`git push --force`/`-f`, and `gh pr merge` unless CI has actually **completed
and passed for the exact current HEAD commit** — not an older commit, not a
"probably still the same" assumption.

## Install

1. Copy `ci-head-guard.sh` into `.claude/hooks/` in your project.
2. `chmod +x .claude/hooks/ci-head-guard.sh`
3. Merge the contents of `settings.snippet.json` into `.claude/settings.json`
   (if you already have a `hooks.PreToolUse` array, add this entry to it
   rather than replacing the file).
4. Make sure `jq` and `gh` (GitHub CLI) are installed, and `gh auth login`
   has been run.

## What it does

- Lets every other Bash command through untouched (`exit 0` immediately if
  the command isn't a merge/rebase/force-push).
- For a matching command, resolves `git rev-parse HEAD` and asks GitHub for
  the check-runs on that **exact SHA**.
- Blocks (`exit 2`, with a reason Claude sees) if:
  - `gh` or git isn't available — fails closed rather than silently allowing.
  - No check-runs exist yet for this SHA (CI hasn't started).
  - Any check-run is still `in_progress`/`queued`.
  - Any check-run's conclusion isn't `success`/`neutral`/`skipped`.
- Only allows the action through when every check-run for the current HEAD
  has completed with a passing conclusion.

## Why fail closed

If `gh api` can't be reached, or the repo isn't a git worktree, the script
blocks rather than assumes things are fine. A guard that lets merges through
whenever it can't check anything isn't a guard — it degrades exactly when a
network hiccup or auth expiry makes verification unavailable, which is the
worst time to relax it.

## Adapting it

- If your org uses a different CI provider (GitLab, CircleCI, Buildkite),
  swap the `gh api .../check-runs` call for that provider's API/CLI — the
  block/allow logic (must be completed, must be passing, must match current
  HEAD) stays the same.
- To also cover branch-protection-style checks that live outside GitHub
  Checks (e.g. a required status from an external system), add another
  `gh api` call for `repos/{owner}/{repo}/commits/{sha}/status` and combine
  the two results before deciding.
