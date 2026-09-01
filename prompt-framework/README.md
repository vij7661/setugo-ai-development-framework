# Setugo AI Development Prompt Framework v1.6

This directory is the public home of the Setugo prompt framework.

## Canonical public document

The current public release is **Version 1.6**. The PDF is the publication/LinkedIn attachment version. A Markdown source version should only be added when it has been verified against the v1.6 master so formatting or PDF extraction artifacts do not silently change the framework.

## Lifecycle covered

1. Research the Idea
2. High-Level Architecture
3. Technical Requirements
4. Develop the Architecture
5. Test What Was Developed
6. Create the Codex Execution Agent

The framework also defines shared Core Standards A–E, including the Universal Rule, source-of-truth/variable ownership, failure root-cause taxonomy, transaction/reliability integrity, and audit/replay integrity.

## Dependency rule

When using a prompt independently, automatically include every Core Standard referenced by that prompt. A prompt with an unresolved Core Standard reference must not be executed. Do not guess or reconstruct missing standards from memory.

## Publication note

The PDF is intentionally kept separate from the Setugo product repository. This repository is for reusable development methodology, not product source code.
