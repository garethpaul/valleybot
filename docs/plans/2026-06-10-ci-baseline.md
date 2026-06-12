# Valleybot CI Baseline

## Status: Completed

## Context

`valleybot` has dependency-free route and integration contract checks behind
`make check`. The repository needs a lightweight GitHub Actions gate so webhook,
token, timeout, logging, and template contracts run before review.

## Objectives

- Run the existing static and dependency-free route contracts in GitHub Actions.
- Keep legacy Python 2 runtime tests optional unless their dependencies are
  installed.
- Make the CI workflow presence part of the checked repository contract.

## Work Completed

- Added `.github/workflows/check.yml` to run `make check` on pushes, pull
  requests, and manual dispatches.
- Set up Python 3.12 in CI for the dependency-free contract checker.
- Extended `scripts/check_valleybot_contracts.py` to require the CI workflow
  and this completed plan.
- Updated README, VISION, SECURITY, and CHANGES with the CI baseline.

## Verification

- `make check`
- `python scripts/check_valleybot_contracts.py`
- `git diff --check`

## Follow-Up Candidates

- Add a pinned legacy Python 2/dependency test environment only after the
  runtime dependency set is documented.
