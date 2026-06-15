# Anchor Make Cleanup to the Makefile Location

## Status: In Progress

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
