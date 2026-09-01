#!/bin/bash
# ci-head-guard.sh
#
# PreToolUse hook (matcher: Bash). Blocks merges, force-pushes, and rebases
# unless the CI status for the *current* HEAD commit — not some earlier
# commit — has actually finished and passed.
#
# This implements the Codex Agent rules:
#   - never treat CI from an older commit as proof that the current head is healthy
#   - if the branch head changes, restart validation against the new head
#   - never merge a branch with unknown failing validation
#   - never perform unsafe rebases on frozen QA/release candidates
#
# Requires: jq, git, gh (GitHub CLI, authenticated: `gh auth login`)
# Install:  chmod +x ci-head-guard.sh
# Register: see settings.snippet.json in this folder

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only act on commands that actually change or rely on the merged/shipped state.
if ! echo "$COMMAND" | grep -Eq '(git[[:space:]]+merge|git[[:space:]]+push[[:space:]].*--force|git[[:space:]]+push[[:space:]].*-f([[:space:]]|$)|git[[:space:]]+rebase|gh[[:space:]]+pr[[:space:]]+merge)'; then
  exit 0
fi

# Must be inside a git repo with gh available; otherwise fail closed with a
# clear message rather than silently letting the action through.
if ! command -v gh >/dev/null 2>&1; then
  echo "BLOCKED: 'gh' CLI not found — cannot verify CI status for the current HEAD before merge/rebase/force-push. Install and authenticate gh, or verify CI status manually before retrying." >&2
  exit 2
fi

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "BLOCKED: not inside a git working tree — cannot resolve current HEAD SHA." >&2
  exit 2
fi

HEAD_SHA=$(git rev-parse HEAD)

# Pull check-run conclusions for the exact current HEAD SHA — not the branch
# name, not whatever CI run happens to be "latest" in the UI.
CHECKS_JSON=$(gh api "repos/{owner}/{repo}/commits/${HEAD_SHA}/check-runs" 2>/dev/null || echo "")

if [ -z "$CHECKS_JSON" ]; then
  echo "BLOCKED: could not fetch CI check-runs for current HEAD ($HEAD_SHA). Cannot confirm this exact commit is green — verify manually before merging/rebasing/force-pushing." >&2
  exit 2
fi

TOTAL=$(echo "$CHECKS_JSON" | jq '.total_count // 0')
if [ "$TOTAL" -eq 0 ]; then
  echo "BLOCKED: no CI check-runs recorded yet for current HEAD ($HEAD_SHA). CI may still be queued or hasn't started — wait for it before merging/rebasing/force-pushing." >&2
  exit 2
fi

INCOMPLETE=$(echo "$CHECKS_JSON" | jq '[.check_runs[] | select(.status != "completed")] | length')
if [ "$INCOMPLETE" -gt 0 ]; then
  echo "BLOCKED: CI is still running for current HEAD ($HEAD_SHA) — $INCOMPLETE check(s) incomplete. Do not race ahead of CI." >&2
  exit 2
fi

FAILED=$(echo "$CHECKS_JSON" | jq '[.check_runs[] | select(.conclusion != "success" and .conclusion != "neutral" and .conclusion != "skipped")] | length')
if [ "$FAILED" -gt 0 ]; then
  echo "BLOCKED: $FAILED check(s) did not pass for current HEAD ($HEAD_SHA). Do not merge/rebase/force-push over failing validation — diagnose via failure-triage first." >&2
  exit 2
fi

# All checks completed and passed for the exact current HEAD. Allow.
exit 0
