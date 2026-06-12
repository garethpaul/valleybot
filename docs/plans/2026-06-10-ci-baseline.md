# Valleybot CI Baseline

## Status: Completed

## Context

`valleybot` has dependency-free route contracts and a Bottle/WebTest runtime
suite behind `make check`. The repository needs a reproducible GitHub Actions
gate so webhook, token, timeout, logging, moderation, and template behavior runs
before review.

## Objectives

- Install pinned runtime dependencies and run the complete gate in GitHub Actions.
- Cover the supported Python 3.10, 3.12, and 3.14 lines.
- Make the CI workflow presence part of the checked repository contract.

## Work Completed

- Added `.github/workflows/check.yml` to run `make check` on pushes, pull
  requests, and manual dispatches.
- Set up a fixed Ubuntu 24.04 matrix for Python 3.10, 3.12, and 3.14.
- Pinned actions to immutable commits, disabled checkout credential persistence,
  and constrained workflow permissions to read-only repository contents.
- Installed the pinned requirements and made the dependency-backed runtime suite
  mandatory alongside the dependency-free contracts.
- Extended `scripts/check_valleybot_contracts.py` to require the CI workflow
  and this completed plan.
- Made recursive cleanup use the repository Makefile so `make check` works when
  invoked from another directory.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `python scripts/check_valleybot_contracts.py`
- `make -f /path/to/valleybot/Makefile check` from outside the repository
- `git diff --check`

## Follow-Up Candidates

- Revisit the oldest Python matrix entry when upstream dependency support moves.
