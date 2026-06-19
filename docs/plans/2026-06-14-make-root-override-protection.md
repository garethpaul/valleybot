# Protect the Selected Make Repository Root

## Status: Completed

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

## Work Completed

- Protected the selected Make working directory with `override` while
  preserving the Python command and recursive cleanup behavior.
- Added exact-line checker contracts and registered this completed plan.

## Verification

- Python compilation and the focused runtime/CI contract passed.
- Local, external-directory, and hostile-root `make check` runs passed under
  360-second timeouts with 48 dependency-free contracts and 27 runtime tests.
- Eight valid hostile root, checker, Python override, cleanup-routing, and
  plan-status mutations were rejected.
- `uv pip check` passed for all 18 installed packages. `pip-audit` reported no
  known vulnerabilities in the unchanged direct requirements and explicitly
  skipped the pinned non-PyPI WebOb distribution.
- Python syntax, workflow YAML, SVG XML, intended-path, generated-corpus,
  `git diff --check`, and changed-line secret audits passed.
