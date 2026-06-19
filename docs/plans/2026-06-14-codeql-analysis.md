# CodeQL Analysis

## Status: Completed

## Context

The hosted Python matrix and local security contracts are green, but GitHub
reports no code-scanning analysis for the repository. Python source and
workflow changes therefore lack a first-party static security signal.

## Priority

Add pinned, least-privilege CodeQL analysis to the existing hosted workflow
without weakening runtime coverage or creating a second workflow surface.

## Requirements

- Analyze GitHub Actions and Python on every push, pull request, and manual
  workflow dispatch.
- Keep global workflow permissions read-only and grant
  `security-events: write` only to the CodeQL job.
- Pin CodeQL initialization and analysis to an immutable action SHA.
- Preserve the complete Python matrix, dependency installation,
  credential-free checkout, and repository plus external-directory checks.
- Extend the action allowlist and documentation contracts so language,
  permission, checkout, and analysis drift fails closed.
- Reject hostile mutations for the language matrix, upload permission,
  immutable action pin, and analysis step.

## Verification

- Python checker compilation, workflow YAML parsing, and focused runtime/CI
  contracts passed.
- The repository and external-directory `make check` passed.
- Four hostile CodeQL workflow mutations were rejected across the language
  matrix, upload permission, immutable action pin, and analysis step.
- Final artifact, corpus-integrity, credential, exact-diff, and hosted checks
  remain the shipping gate.

## Scope Boundary

This change does not alter bot behavior, content moderation, live Messenger or
Slack integrations, repository-level secret scanning, or dependency versions.
