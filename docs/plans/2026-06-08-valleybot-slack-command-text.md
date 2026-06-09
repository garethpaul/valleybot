# Valleybot Slack Command Text

## Status: Completed

## Context

The Bottle Slack slash-command route verified the request token, but still sent
missing or whitespace-only command text into the bot. The standalone Slack
adapter already rejected blank text, so the web route needed the same contract.

## Objectives

- Preserve the existing Slack token check.
- Reject missing or blank Slack command text before calling the bot.
- Trim accepted Slack command text before response generation.
- Cover the route in dependency-free checks that run under `make check`.

## Work Completed

- Added `400` responses for missing and blank Slack command text.
- Trimmed valid Slack command text before calling `bot.respond`.
- Extended `scripts/check_valleybot_contracts.py` with blank-text and trim
  coverage for the Bottle route.
- Updated README, VISION, and CHANGES with the command-text guardrail.

## Verification

- `python3 scripts/check_valleybot_contracts.py`
- `make check`
- `make verify`
- `git diff --check`

## Follow-Up Candidates

- Add similar missing-query handling to the web `/bot` route.
- Add content-review guidance for new response templates.
