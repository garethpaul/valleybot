# Valleybot Slack Non-Text Command Guard

## Status: Completed

## Context

Slack command text validation rejected missing and blank values, but both the
Bottle route and standalone adapter still called `.strip()` directly. A
malformed event with a non-text `text` value could raise before returning the
existing `missing text` response.

## Objectives

- Preserve Slack token validation before any bot response generation.
- Reject missing, blank, or non-text Slack command text.
- Trim accepted Slack command text before calling the bot.
- Cover both Slack entry points with dependency-free contracts.

## Work Completed

- Added a small text normalizer to the Bottle Slack route.
- Added the same non-text guard to the standalone Slack adapter.
- Extended the contract checker with non-text command coverage for both entry
  points.
- Updated README, SECURITY, VISION, and CHANGES with the Slack command guard.

## Verification

- `python3 scripts/check_valleybot_contracts.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
