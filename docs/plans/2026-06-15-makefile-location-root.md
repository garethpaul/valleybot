# Anchor Make Cleanup to the Makefile Location

## Status: Completed

## Context

The current protected `ROOT := $(CURDIR)` cannot be overridden, but it still
trusts the caller's working directory. Running `make -f /path/to/Makefile check`
outside the checkout therefore sends recursive cleanup into the caller's tree.

## Requirements

- Derive the protected repository root from the loaded Makefile location.
- Keep cleanup, source checks, corpora preparation, tests, and recursion inside
  the checkout for repository and external-directory invocations.
- Preserve explicit `PYTHON` overrides and existing runtime behavior.
- Add fail-closed static contracts for the exact rooted declaration and reject
  the caller-directory form.

## Verification Plan

- focused contract checker and hostile root-declaration mutations
- repository and external-directory `make check` with bounded execution
- diff, generated-artifact, tracked-corpus, and credential-pattern audits

## Scope Boundaries

- Do not change bot behavior, dependencies, workflows, or tracked NLTK data.
- Do not merge or close stacked pull requests without owner authorization.

## Work Completed

- Replaced the protected caller-directory root with the absolute directory of
  the last loaded Makefile.
- Added fail-closed contracts for the exact rooted declaration and rejection
  of `CURDIR`.
- Updated local verification documentation without changing runtime behavior.

## Verification

- The focused checker passed 50 dependency-free contracts.
- Caller-directory and missing-`override` mutations were rejected, and a
  hostile command-line `ROOT` assignment could not redirect any dry-run path.
- Repository and external-directory `make check` passed with a pinned Python
  environment: 50 contracts and 28 runtime tests in each run.
- `pip check` passed and `pip-audit` found no known vulnerabilities in auditable
  dependencies; the pinned private WebOb build was explicitly unauditable.
- Tracked NLTK corpus hashes remained unchanged. Four downloader outputs were
  removed by exact path after validation.
