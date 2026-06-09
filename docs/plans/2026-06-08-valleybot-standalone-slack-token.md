# Valleybot Standalone Slack Token Plan

Date: 2026-06-08

Status: Completed

## Goal

Make the standalone Slack handler enforce the configured Slack verification
token before invoking the bot, matching the Bottle `/slack` route contract.

## Scope

- Reject standalone Slack events with missing or mismatched `token` values.
- Reject blank Slack command text without calling `bot.respond`.
- Keep accepted event behavior unchanged for matching tokens and non-empty text.
- Cover the standalone handler in the dependency-free contract checker.

## TDD Notes

- Red: `python3 scripts/check_valleybot_contracts.py` failed because this plan
  was not yet present under `docs/plans`.
- Green: `python3 scripts/check_valleybot_contracts.py` passed with standalone
  Slack token and blank-text coverage after updating `slack.py`.

## Verification

- `python3 scripts/check_valleybot_contracts.py`
- `make check`
- `git diff --check`
