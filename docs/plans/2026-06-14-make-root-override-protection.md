# Protect the Selected Make Repository Root

## Status: Planned

## Context

Valleybot intentionally treats GNU Make's selected working directory as the
repository root so `make -C <checkout>` remains portable. A command-line
`ROOT=` assignment can still redirect compilation, tests, contracts, and
recursive cleanup outside that selected checkout.

## Requirements

- Protect `ROOT := $(CURDIR)` with GNU Make's `override` directive.
- Preserve `PYTHON ?= python3`, recursive cleanup, and the pinned package gate.
- Require the exact protected root and Python lines in the dependency-free
  checker.
- Pass local, external-directory, and hostile-root full gates.
- Reject weakened root, checker, Python override, cleanup, and plan mutations.
- Preserve Messenger behavior, dependencies, workflows, and test coverage.

## Verification Plan

- focused runtime/CI contract and Python compilation
- bounded local, external-directory, and hostile-root `make check`
- focused hostile mutations
- pinned dependency integrity/audit, workflow YAML, SVG XML, artifact,
  whitespace, and changed-line secret audits

## Scope Boundaries

- Do not change runtime behavior, packages, NLTK corpora, workflows, or
  Messenger security policy.
- Do not merge or close stacked pull requests without owner authorization.
