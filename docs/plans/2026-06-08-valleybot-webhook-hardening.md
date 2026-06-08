# Valleybot Webhook Hardening Plan

Date: 2026-06-08

status: completed

## Goal

Make the legacy Bottle bot safer to exercise by requiring webhook verification
tokens, avoiding tokenized Messenger URLs, setting outbound request timeouts,
and capturing those route contracts in repeatable local checks.

## Scope

- Preserve the existing Messenger hardening already present in the worktree:
  - `hub.verify_token` must match `MESSENGER_VERIFY_TOKEN`.
  - Invalid Messenger JSON returns a deterministic 400.
  - Non-message webhook events are acknowledged without sending replies.
  - Messenger replies use a bearer header and explicit timeout.
- Add Slack slash-command token validation before any bot response is generated.
- Add dependency-free verification targets for this legacy Python project.

## TDD Notes

- Red: `python scripts/check_valleybot_contracts.py` failed with
  `AssertionError: invalid Slack token response` after adding the Slack
  invalid-token contract.
- Green: `python scripts/check_valleybot_contracts.py` passed with 8 route
  contract checks after rejecting invalid Slack tokens in `app.py`.

## Verification

- `make lint`
- `make test`
- `make build`
- `make verify`
- `make check`
- `git diff --check`
- Legacy Python 2 `bot_tests` are skipped by `make test` in this environment
  because the Python 2 dependencies are not installed.
