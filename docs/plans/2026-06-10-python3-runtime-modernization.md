# Python 3 Runtime Modernization

Status: Completed

## Context

Valleybot still declared Python 2.7.11 and dependency versions from 2015-2016.
The real WebTest suite was therefore optional and skipped on modern developer
machines, leaving runtime compatibility and dependency regressions unverified.

## Objectives

- Move deployment metadata to the supported Python 3.14 line.
- Replace obsolete dependencies with current stable releases from PyPI.
- Run the real unittest/WebTest suite as part of `make check`.
- Prepare current TextBlob corpora during local verification and deployment.
- Keep Bottle debug mode disabled unless explicitly enabled for local work.
- Require Messenger POST signatures before parsing webhook JSON.
- Verify the supported runtime range in hosted CI.

## Verification

- `python3 -m pip install -r requirements.txt`
- `make check`
- `python3 -m unittest bot_tests`
- `git diff --check`
