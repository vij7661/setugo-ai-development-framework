# Claude Code Safeguards

This directory is reserved for the native Claude Code artifacts from the Setugo multi-LLM development experiment.

Expected source files:

- `hooks/ci-head-guard.sh`
- `settings.snippet.json`
- supporting `README.md`

The `ci-head-guard.sh` experiment is designed as a `PreToolUse` safeguard around selected risky Git operations. Its key idea is to verify CI for the **exact current HEAD** rather than relying on an older green run.

These files are developer examples, not a universal security policy. Before adopting them, review the CI provider, authentication model, allowed check conclusions, hook matcher, fail-closed behavior, and the Git operations that should actually be guarded in your repository.

The original native artifacts will be added only from the verified source files. Reconstructed copies will not be labeled as originals.
